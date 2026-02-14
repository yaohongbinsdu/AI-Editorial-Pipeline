from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from app.config import settings
from app.models.article import Article
from app.utils.logging import get_logger
from app.utils.retry import async_retry

logger = get_logger("content_scraper")


@dataclass
class ScrapedContent:
    title: str | None = None
    content: str | None = None
    image_url: str | None = None
    source: str = ""


class ContentScraper:
    @async_retry(max_retries=2, retry_on=(httpx.HTTPError,))
    async def scrape_with_firecrawl(self, url: str) -> ScrapedContent:
        if not settings.FIRECRAWL_API_KEY:
            return ScrapedContent(source="firecrawl")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}"},
                json={"url": url, "formats": ["markdown"]},
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            metadata = data.get("metadata", {})
            return ScrapedContent(
                title=metadata.get("title") or metadata.get("ogTitle"),
                content=data.get("markdown", ""),
                image_url=metadata.get("ogImage"),
                source="firecrawl",
            )

    @async_retry(max_retries=2, retry_on=(httpx.HTTPError,))
    async def scrape_with_iframely(self, url: str) -> ScrapedContent:
        if not settings.IFRAMELY_API_KEY:
            return ScrapedContent(source="iframely")

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                "https://iframe.ly/api/iframely",
                params={"url": url, "api_key": settings.IFRAMELY_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()
            meta = data.get("meta", {})
            links = data.get("links", {})

            image_url = None
            for thumb in links.get("thumbnail", []):
                if thumb.get("href"):
                    image_url = thumb["href"]
                    break

            return ScrapedContent(
                title=meta.get("title"),
                content=meta.get("description", ""),
                image_url=image_url,
                source="iframely",
            )

    @async_retry(max_retries=2, retry_on=(Exception,))
    async def scrape_with_gemini(self, url: str) -> ScrapedContent:
        if not settings.GOOGLE_AI_API_KEY:
            return ScrapedContent(source="gemini")

        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = (
                f"Visit this URL and extract the article content: {url}\n\n"
                "Return a JSON object with exactly these fields:\n"
                '- "title": the article title\n'
                '- "content": the full article body text in markdown format\n'
                "Return only valid JSON, no other text."
            )

            response = await asyncio.to_thread(model.generate_content, prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            import json
            data = json.loads(text)
            return ScrapedContent(
                title=data.get("title"),
                content=data.get("content", ""),
                source="gemini",
            )
        except Exception as exc:
            logger.warning("gemini_scrape_failed", url=url, error=str(exc))
            return ScrapedContent(source="gemini")

    async def scrape_article(self, url: str) -> dict[str, str | None]:
        results = await asyncio.gather(
            self.scrape_with_firecrawl(url),
            self.scrape_with_iframely(url),
            self.scrape_with_gemini(url),
            return_exceptions=True,
        )

        firecrawl = results[0] if not isinstance(results[0], BaseException) else ScrapedContent(source="firecrawl")
        iframely = results[1] if not isinstance(results[1], BaseException) else ScrapedContent(source="iframely")
        gemini = results[2] if not isinstance(results[2], BaseException) else ScrapedContent(source="gemini")

        for i, r in enumerate(results):
            if isinstance(r, BaseException):
                logger.warning("scraper_exception", scraper_index=i, error=str(r))

        best_title = self._select_best_title(iframely, gemini, firecrawl)
        best_content = self._select_best_content(gemini, firecrawl)
        best_image = self._select_best_image(iframely, firecrawl)

        return {
            "firecrawl_title": firecrawl.title,
            "firecrawl_content": firecrawl.content,
            "iframely_title": iframely.title,
            "iframely_content": iframely.content,
            "iframely_image_url": iframely.image_url,
            "gemini_title": gemini.title,
            "gemini_content": gemini.content,
            "final_title": best_title,
            "final_content": best_content,
            "final_image_url": best_image,
        }

    @staticmethod
    def _select_best_title(
        iframely: ScrapedContent, gemini: ScrapedContent, firecrawl: ScrapedContent
    ) -> str | None:
        for src in [iframely, gemini, firecrawl]:
            if src.title and len(src.title.strip()) > 5:
                return src.title.strip()
        return None

    @staticmethod
    def _select_best_content(gemini: ScrapedContent, firecrawl: ScrapedContent) -> str | None:
        candidates = [
            (gemini.content, "gemini"),
            (firecrawl.content, "firecrawl"),
        ]
        best = ""
        for content, _source in candidates:
            if content and len(content) > len(best):
                best = content
        return best or None

    @staticmethod
    def _select_best_image(
        iframely: ScrapedContent, firecrawl: ScrapedContent
    ) -> str | None:
        for src in [iframely, firecrawl]:
            if src.image_url:
                return src.image_url
        return None

    async def scrape_and_update_article(self, article: Article) -> None:
        logger.info("scrape_article_start", article_id=str(article.id), url=article.original_url)
        article.status = "fetching"

        try:
            scraped = await self.scrape_article(article.original_url)
            article.firecrawl_title = scraped.get("firecrawl_title")
            article.firecrawl_content = scraped.get("firecrawl_content")
            article.iframely_title = scraped.get("iframely_title")
            article.iframely_content = scraped.get("iframely_content")
            article.iframely_image_url = scraped.get("iframely_image_url")
            article.gemini_title = scraped.get("gemini_title")
            article.gemini_content = scraped.get("gemini_content")

            if scraped.get("final_title"):
                article.final_title = scraped["final_title"]
            if scraped.get("final_content"):
                article.final_content = scraped["final_content"]
            if scraped.get("final_image_url"):
                article.final_image_url = scraped["final_image_url"]

            article.status = "fetched"
            logger.info("scrape_article_done", article_id=str(article.id))
        except Exception as exc:
            article.status = "fetch_failed"
            logger.error("scrape_article_failed", article_id=str(article.id), error=str(exc))
            raise
