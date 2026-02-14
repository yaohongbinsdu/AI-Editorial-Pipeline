from fastapi import APIRouter

from app.api.deps import DBSession, Pagination

router = APIRouter()


@router.get("/categories")
async def list_categories(db: DBSession):
    return []


@router.get("/categories/{slug}")
async def get_category_page(
    slug: str,
    db: DBSession,
    pagination: Pagination,
    hours: int = 24,
):
    return {}
