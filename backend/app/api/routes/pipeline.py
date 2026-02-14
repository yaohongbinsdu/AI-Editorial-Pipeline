from fastapi import APIRouter

from app.api.deps import DBSession

router = APIRouter()


@router.get("/pipeline/status")
async def get_pipeline_status(db: DBSession):
    return {
        "is_running": False,
        "current_run": None,
        "last_completed_run": None,
        "step_stats_24h": [],
    }


@router.get("/pipeline/runs")
async def list_pipeline_runs(db: DBSession, limit: int = 24):
    return []


@router.get("/pipeline/runs/{run_id}")
async def get_pipeline_run_detail(run_id: str, db: DBSession):
    return {}


@router.post("/pipeline/trigger", status_code=202)
async def trigger_pipeline(db: DBSession):
    return {"run_id": "", "message": "Pipeline triggered"}
