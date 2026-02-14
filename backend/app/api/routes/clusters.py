from fastapi import APIRouter

from app.api.deps import DBSession, Pagination

router = APIRouter()


@router.get("/clusters")
async def list_clusters(
    db: DBSession,
    pagination: Pagination,
    category: str | None = None,
    min_articles: int = 2,
    sort_by: str = "last_updated_at",
):
    return {"items": [], "total": 0, "page": pagination.page, "page_size": pagination.page_size, "total_pages": 0}


@router.get("/clusters/{cluster_id}")
async def get_cluster(cluster_id: str, db: DBSession):
    return {}
