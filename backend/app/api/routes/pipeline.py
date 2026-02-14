import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.api.deps import DBSession
from app.models.pipeline_run import PipelineRun
from app.models.pipeline_step_log import PipelineStepLog

router = APIRouter()


@router.get("/pipeline/status")
async def get_pipeline_status(db: DBSession):
    running_stmt = select(PipelineRun).where(PipelineRun.status == "running").order_by(PipelineRun.started_at.desc())
    running_result = await db.execute(running_stmt)
    current_run = running_result.scalar_one_or_none()

    last_stmt = select(PipelineRun).where(PipelineRun.status == "completed").order_by(PipelineRun.completed_at.desc())
    last_result = await db.execute(last_stmt)
    last_completed = last_result.scalar_one_or_none()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    step_stats_stmt = (
        select(
            PipelineStepLog.step_name,
            PipelineStepLog.status,
            func.count().label("count"),
            func.avg(PipelineStepLog.duration_ms).label("avg_duration_ms"),
        )
        .where(PipelineStepLog.created_at >= cutoff)
        .group_by(PipelineStepLog.step_name, PipelineStepLog.status)
    )
    step_stats_result = await db.execute(step_stats_stmt)
    step_stats = [
        {
            "step_name": row.step_name,
            "status": row.status,
            "count": row.count,
            "avg_duration_ms": int(row.avg_duration_ms) if row.avg_duration_ms else 0,
        }
        for row in step_stats_result.all()
    ]

    def _run_dict(r: PipelineRun | None) -> dict | None:
        if not r:
            return None
        return {
            "id": str(r.id),
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "status": r.status,
            "articles_discovered": r.articles_discovered,
            "articles_processed": r.articles_processed,
            "articles_failed": r.articles_failed,
            "duration_seconds": r.duration_seconds,
        }

    return {
        "is_running": current_run is not None,
        "current_run": _run_dict(current_run),
        "last_completed_run": _run_dict(last_completed),
        "step_stats_24h": step_stats,
    }


@router.get("/pipeline/runs")
async def list_pipeline_runs(db: DBSession, limit: int = 24):
    stmt = select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(limit)
    result = await db.execute(stmt)
    runs = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "status": r.status,
            "articles_discovered": r.articles_discovered,
            "articles_processed": r.articles_processed,
            "articles_failed": r.articles_failed,
            "duration_seconds": r.duration_seconds,
        }
        for r in runs
    ]


@router.get("/pipeline/runs/{run_id}")
async def get_pipeline_run_detail(run_id: str, db: DBSession):
    run = await db.get(PipelineRun, uuid.UUID(run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")

    logs_stmt = (
        select(PipelineStepLog)
        .where(PipelineStepLog.pipeline_run_id == run.id)
        .order_by(PipelineStepLog.created_at)
    )
    logs_result = await db.execute(logs_stmt)
    logs = logs_result.scalars().all()

    return {
        "id": str(run.id),
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "status": run.status,
        "articles_discovered": run.articles_discovered,
        "articles_processed": run.articles_processed,
        "articles_failed": run.articles_failed,
        "duration_seconds": run.duration_seconds,
        "step_logs": [
            {
                "id": str(log.id),
                "step_name": log.step_name,
                "status": log.status,
                "article_id": str(log.article_id) if log.article_id else None,
                "duration_ms": log.duration_ms,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.post("/pipeline/trigger", status_code=202)
async def trigger_pipeline(db: DBSession):
    from app.tasks.workers import run_full_pipeline

    task = run_full_pipeline.delay()
    return {"task_id": task.id, "message": "Pipeline triggered"}
