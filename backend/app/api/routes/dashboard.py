from fastapi import APIRouter

from app.api.deps import DBSession

router = APIRouter()


@router.get("/dashboard/overview")
async def get_overview(db: DBSession, hours: int = 24):
    return {
        "time_window_hours": hours,
        "total_articles": 0,
        "category_breakdown": [],
        "top_clusters": [],
        "must_read_articles": [],
        "market_focus": [],
        "pipeline_health": {
            "last_run_at": None,
            "last_run_status": None,
            "success_rate_24h": 0,
            "articles_processed_24h": 0,
        },
    }


@router.get("/dashboard/trending")
async def get_trending(db: DBSession, limit: int = 10):
    return {"trending_clusters": [], "trending_articles": []}
