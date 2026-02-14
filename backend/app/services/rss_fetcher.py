from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.rss_source import RSSSource
from app.utils.logging import get_logger
from app.utils.retry import async_retry

logger = get_logger("rss_fetcher")


class RSSFetcher:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_all_sources(self) -> list[Article]:
        stmt = select(RSSSource).where(RSSSource.enabled.is_(True))
        result = await self.db.execute(stmt)
        sources = result.scalars().all()

        logger.info("fetch_all_sources_start", source_count=len(sources))

        self._seen_urls: set[str] = set()
        all_new_articles: list[Article] = []
        for source in sources:
            try:
                new_articles = await self.fetch_source(source)
                all_new_articles.extend(new_articles)
                source.last_fetched_at = datetime.now(timezone.utc)
                source.consecutive_failures = 0
                source.last_error = None
            except Exception as exc:
                source.consecutive_failures += 1
                source.last_error = str(exc)[:500]
                logger.error(
                    "fetch_source_failed",
                    source_id=str(source.id),
                    source_name=source.name,
                    error=str(exc),
                    consecutive_failures=source.consecutive_failures,
                )

        await self.db.flush()
        logger.info("fetch_all_sources_done", new_articles=len(all_new_articles))
        return all_new_articles

    @async_retry(max_retries=2, backoff_base=2.0, retry_on=(httpx.HTTPError, Exception))
    async def fetch_source(self, source: RSSSource) -> list[Article]:
        logger.info("fetch_source_start", source_id=str(source.id), source_name=source.name)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(source.url)
            response.raise_for_status()

        feed = feedparser.parse(response.text)

        if feed.bozo and not feed.entries:
            raise ValueError(f"Failed to parse RSS feed: {feed.bozo_exception}")

        urls = [entry.get("link", "") for entry in feed.entries if entry.get("link")]
        existing_stmt = select(Article.original_url).where(Article.original_url.in_(urls))
        existing_result = await self.db.execute(existing_stmt)
        existing_urls = set(existing_result.scalars().all())

        new_articles: list[Article] = []
        for entry in feed.entries:
            url = entry.get("link", "").strip()
            if not url or url in existing_urls or url in self._seen_urls:
                continue

            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    pass

            image_url = None
            if hasattr(entry, "media_content") and entry.media_content:
                image_url = entry.media_content[0].get("url")
            elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get("url")
            elif hasattr(entry, "enclosures") and entry.enclosures:
                for enc in entry.enclosures:
                    if enc.get("type", "").startswith("image/"):
                        image_url = enc.get("href")
                        break

            article = Article(
                source_id=source.id,
                original_url=url,
                original_title=entry.get("title", "")[:500] or None,
                original_content=entry.get("summary", "") or None,
                original_image_url=image_url,
                final_title=entry.get("title", "")[:500] or url,
                final_content=entry.get("summary", "") or "",
                final_image_url=image_url,
                published_at=published_at,
                author=entry.get("author", "")[:255] or None,
            )
            self.db.add(article)
            new_articles.append(article)
            self._seen_urls.add(url)

        logger.info(
            "fetch_source_done",
            source_id=str(source.id),
            entries_total=len(feed.entries),
            new_articles=len(new_articles),
            skipped_existing=len(feed.entries) - len(new_articles),
        )
        return new_articles
