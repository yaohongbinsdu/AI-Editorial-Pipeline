from celery.schedules import crontab

from app.config import settings
from app.tasks.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "run-full-pipeline": {
        "task": "run_full_pipeline",
        "schedule": settings.PIPELINE_INTERVAL_MINUTES * 60,
        "options": {"queue": "pipeline"},
    },
    "retry-failed-articles": {
        "task": "retry_failed_articles",
        "schedule": crontab(minute=0, hour="*/6"),
        "options": {"queue": "pipeline"},
    },
    "cleanup-old-step-logs": {
        "task": "cleanup_old_step_logs",
        "schedule": crontab(minute=0, hour=3),
        "options": {"queue": "maintenance"},
    },
}


@celery_app.task(name="cleanup_old_step_logs")
def cleanup_old_step_logs():
    import asyncio
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import delete

    from app.models import async_session
    from app.models.pipeline_step_log import PipelineStepLog
    from app.utils.logging import get_logger

    logger = get_logger("cleanup")

    async def _execute():
        async with async_session() as db:
            async with db.begin():
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                stmt = delete(PipelineStepLog).where(
                    PipelineStepLog.created_at < cutoff
                )
                result = await db.execute(stmt)
                return result.rowcount

    loop = asyncio.new_event_loop()
    try:
        deleted = loop.run_until_complete(_execute())
        logger.info("old_step_logs_cleaned", deleted=deleted)
        return deleted
    finally:
        loop.close()
