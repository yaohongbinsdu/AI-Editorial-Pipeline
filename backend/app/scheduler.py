"""Asyncio-based background scheduler for periodic pipeline execution.

Replaces Celery beat when running without Celery infrastructure.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.config import settings
from app.models import async_session
from app.services.pipeline import run_pipeline
from app.utils.logging import get_logger

logger = get_logger("scheduler")

_task: asyncio.Task | None = None


async def _run_loop() -> None:
    interval = settings.PIPELINE_INTERVAL_MINUTES * 60
    logger.info(
        "scheduler_started",
        interval_minutes=settings.PIPELINE_INTERVAL_MINUTES,
    )

    while True:
        try:
            logger.info("scheduler_tick", time=datetime.now(timezone.utc).isoformat())
            async with async_session() as db:
                run = await run_pipeline(db)
                await db.commit()
                logger.info(
                    "scheduler_pipeline_done",
                    run_id=str(run.id),
                    discovered=run.articles_discovered,
                    duration_s=run.duration_seconds,
                )
        except asyncio.CancelledError:
            logger.info("scheduler_cancelled")
            return
        except Exception as exc:
            logger.error("scheduler_pipeline_error", error=str(exc)[:500])

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("scheduler_cancelled_during_sleep")
            return


def start() -> None:
    """Start the background scheduler task."""
    global _task
    if _task is not None and not _task.done():
        logger.warning("scheduler_already_running")
        return
    _task = asyncio.create_task(_run_loop())
    logger.info("scheduler_task_created")


def stop() -> None:
    """Cancel the background scheduler task."""
    global _task
    if _task is not None and not _task.done():
        _task.cancel()
        logger.info("scheduler_task_cancelled")
    _task = None
