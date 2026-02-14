from __future__ import annotations

import asyncio

from app.models import async_session
from app.tasks.celery_app import celery_app
from app.utils.logging import get_logger

logger = get_logger("workers")


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="run_full_pipeline", bind=True, max_retries=1)
def run_full_pipeline(self):
    from app.services.pipeline import run_pipeline

    async def _execute():
        async with async_session() as db:
            async with db.begin():
                result = await run_pipeline(db)
                return str(result.id)

    try:
        run_id = _run_async(_execute())
        logger.info("pipeline_task_completed", run_id=run_id)
        return run_id
    except Exception as exc:
        logger.error("pipeline_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="process_single_article", bind=True, max_retries=2)
def process_single_article(self, article_id: str):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.article import Article
    from app.services.content_scraper import ContentScraper
    from app.services.gravity_engine import GravityEngine
    from app.services.summarizer import Summarizer

    async def _execute():
        async with async_session() as db:
            async with db.begin():
                stmt = (
                    select(Article)
                    .options(selectinload(Article.summary))
                    .where(Article.id == article_id)
                )
                result = await db.execute(stmt)
                article = result.scalar_one_or_none()
                if not article:
                    logger.warning("article_not_found", article_id=article_id)
                    return

                scraper = ContentScraper()
                await scraper.scrape_and_update_article(article)

                summarizer = Summarizer()
                await summarizer.summarize_article(article, db)

                gravity = GravityEngine()
                await gravity.score_and_update(article, db)

    try:
        _run_async(_execute())
        logger.info("single_article_processed", article_id=article_id)
    except Exception as exc:
        logger.error("single_article_failed", article_id=article_id, error=str(exc))
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="retry_failed_articles")
def retry_failed_articles():
    from sqlalchemy import select

    from app.models.article import Article

    async def _execute():
        async with async_session() as db:
            stmt = select(Article.id).where(
                Article.status.in_(["fetch_failed", "summary_failed", "score_failed"])
            )
            result = await db.execute(stmt)
            failed_ids = [str(row[0]) for row in result.all()]

            for aid in failed_ids:
                process_single_article.delay(aid)

            return len(failed_ids)

    count = _run_async(_execute())
    logger.info("retry_failed_dispatched", count=count)
    return count
