from celery import Celery

from app.config import settings

celery_app = Celery(
    "editorial",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_routes={
        "app.tasks.workers.run_full_pipeline": {"queue": "pipeline"},
        "app.tasks.workers.process_single_article": {"queue": "articles"},
        "app.tasks.workers.retry_failed_articles": {"queue": "retry"},
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
