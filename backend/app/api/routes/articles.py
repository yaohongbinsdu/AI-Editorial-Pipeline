from fastapi import APIRouter, Query

from app.api.deps import DBSession, Pagination

router = APIRouter()


@router.get("/articles")
async def list_articles(
    db: DBSession,
    pagination: Pagination,
    category: str | None = None,
    status: str | None = None,
    novelty_gate: bool | None = None,
    editorial_vote: str | None = None,
    min_score: float | None = None,
    sort_by: str = Query(default="composite_score"),
    order: str = Query(default="desc"),
):
    return {"items": [], "total": 0, "page": pagination.page, "page_size": pagination.page_size, "total_pages": 0}


@router.get("/articles/{article_id}")
async def get_article(article_id: str, db: DBSession):
    return {}


@router.get("/articles/{article_id}/similar")
async def get_similar_articles(
    article_id: str,
    db: DBSession,
    limit: int = 5,
    threshold: float = 0.75,
):
    return []
