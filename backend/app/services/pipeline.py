from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.pipeline_run import PipelineRun
from app.models.pipeline_step_log import PipelineStepLog
from app.services.clusterer import Clusterer
from app.services.content_scraper import ContentScraper
from app.services.gravity_engine import GravityEngine
from app.services.rss_fetcher import RSSFetcher
from app.services.summarizer import Summarizer
from app.services.vectorizer import Vectorizer
from app.utils.logging import get_logger

logger = get_logger("pipeline")

STEPS = [
    "rss_fetch",
    "content_scrape",
    "summarize",
    "vectorize",
    "cluster",
    "expansion_check",
    "gravity_score",
]


async def _log_step(
    db: AsyncSession,
    run_id,
    article_id,
    step: str,
    status: str,
    duration_ms: int = 0,
    error: str | None = None,
) -> None:
    log = PipelineStepLog(
        pipeline_run_id=run_id,
        article_id=article_id,
        step_name=step,
        status=status,
        duration_ms=duration_ms,
        error_message=error[:500] if error else None,
    )
    db.add(log)


async def run_pipeline(db: AsyncSession) -> PipelineRun:
    pipeline_run = PipelineRun(
        started_at=datetime.now(timezone.utc),
        status="running",
    )
    db.add(pipeline_run)
    await db.flush()

    logger.info("pipeline_started", run_id=str(pipeline_run.id))
    run_start = time.monotonic()

    total_discovered = 0
    total_processed = 0
    total_failed = 0

    # Step 1: RSS Fetch
    fetcher = RSSFetcher(db)
    new_articles: list[Article] = []
    try:
        step_start = time.monotonic()
        new_articles = await fetcher.fetch_all_sources()
        total_discovered = len(new_articles)
        await _log_step(
            db, pipeline_run.id, None, "rss_fetch", "success",
            duration_ms=int((time.monotonic() - step_start) * 1000),
        )
        await db.flush()
    except Exception as exc:
        logger.error("rss_fetch_failed", error=str(exc))
        await _log_step(db, pipeline_run.id, None, "rss_fetch", "failed", error=str(exc))

    # Step 2: Content Scrape
    scraper = ContentScraper()
    for article in new_articles:
        try:
            step_start = time.monotonic()
            await scraper.scrape_and_update_article(article)
            await _log_step(
                db, pipeline_run.id, article.id, "content_scrape", "success",
                duration_ms=int((time.monotonic() - step_start) * 1000),
            )
        except Exception as exc:
            total_failed += 1
            await _log_step(
                db, pipeline_run.id, article.id, "content_scrape", "failed",
                error=str(exc),
            )

    await db.flush()

    # Step 3: Summarize
    summarizer = Summarizer()
    fetched_stmt = select(Article).where(Article.status == "fetched")
    fetched_result = await db.execute(fetched_stmt)
    fetched_articles = fetched_result.scalars().all()

    for article in fetched_articles:
        try:
            step_start = time.monotonic()
            await summarizer.summarize_article(article, db)
            await _log_step(
                db, pipeline_run.id, article.id, "summarize", "success",
                duration_ms=int((time.monotonic() - step_start) * 1000),
            )
            total_processed += 1
        except Exception as exc:
            total_failed += 1
            await _log_step(
                db, pipeline_run.id, article.id, "summarize", "failed",
                error=str(exc),
            )

    await db.flush()

    # Step 4: Vectorize
    vectorizer = Vectorizer()
    summarized_stmt = select(Article).where(Article.status == "summarized")
    summarized_result = await db.execute(summarized_stmt)
    summarized_articles = summarized_result.scalars().all()

    embeddings: dict[str, list[float]] = {}
    for article in summarized_articles:
        try:
            step_start = time.monotonic()
            emb = await vectorizer.vectorize_article(str(article.id), db)
            if emb:
                embeddings[str(article.id)] = emb
            await _log_step(
                db, pipeline_run.id, article.id, "vectorize", "success",
                duration_ms=int((time.monotonic() - step_start) * 1000),
            )
        except Exception as exc:
            total_failed += 1
            await _log_step(
                db, pipeline_run.id, article.id, "vectorize", "failed",
                error=str(exc),
            )

    await db.flush()

    # Step 5: Cluster
    clusterer = Clusterer(db)
    vectorized_stmt = select(Article).where(Article.status == "vectorized")
    vectorized_result = await db.execute(vectorized_stmt)
    vectorized_articles = vectorized_result.scalars().all()

    for article in vectorized_articles:
        emb = embeddings.get(str(article.id))
        if not emb:
            continue
        try:
            step_start = time.monotonic()
            await clusterer.assign_to_cluster(article, emb)
            article.status = "clustered"
            await _log_step(
                db, pipeline_run.id, article.id, "cluster", "success",
                duration_ms=int((time.monotonic() - step_start) * 1000),
            )
        except Exception as exc:
            total_failed += 1
            await _log_step(
                db, pipeline_run.id, article.id, "cluster", "failed",
                error=str(exc),
            )

    await db.flush()

    # Step 6: Gravity Score
    gravity = GravityEngine()
    clustered_stmt = select(Article).where(Article.status == "clustered")
    clustered_result = await db.execute(clustered_stmt)
    clustered_articles = clustered_result.scalars().all()

    for article in clustered_articles:
        try:
            step_start = time.monotonic()
            await gravity.score_and_update(article, db)
            await _log_step(
                db, pipeline_run.id, article.id, "gravity_score", "success",
                duration_ms=int((time.monotonic() - step_start) * 1000),
            )
        except Exception as exc:
            total_failed += 1
            await _log_step(
                db, pipeline_run.id, article.id, "gravity_score", "failed",
                error=str(exc),
            )

    # Finalize
    elapsed_ms = int((time.monotonic() - run_start) * 1000)
    pipeline_run.completed_at = datetime.now(timezone.utc)
    pipeline_run.status = "completed"
    pipeline_run.articles_discovered = total_discovered
    pipeline_run.articles_processed = total_processed
    pipeline_run.articles_failed = total_failed
    pipeline_run.duration_seconds = elapsed_ms / 1000.0

    await db.flush()

    logger.info(
        "pipeline_completed",
        run_id=str(pipeline_run.id),
        discovered=total_discovered,
        processed=total_processed,
        failed=total_failed,
        duration_ms=elapsed_ms,
    )
    return pipeline_run
