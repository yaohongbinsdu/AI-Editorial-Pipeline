import math
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import DBSession, Pagination
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.gravity_score import GravityScore
from app.models.summary import Summary

router = APIRouter()

VALID_CATEGORIES = [
    "finance", "technology", "commercial_space", "new_energy",
    "healthcare", "agriculture", "consumer", "real_estate",
    "manufacturing", "crypto", "macro_economy", "regulation", "other",
]


@router.get("/categories")
async def list_categories(db: DBSession):
    results = []
    for cat in VALID_CATEGORIES:
        article_count_stmt = (
            select(func.count())
            .select_from(Summary)
            .where(Summary.category == cat)
        )
        article_count = (await db.execute(article_count_stmt)).scalar() or 0

        cluster_count_stmt = (
            select(func.count())
            .select_from(Cluster)
            .where(Cluster.category == cat)
        )
        cluster_count = (await db.execute(cluster_count_stmt)).scalar() or 0

        results.append({
            "slug": cat,
            "article_count": article_count,
            "cluster_count": cluster_count,
        })
    return results


@router.get("/categories/{slug}")
async def get_category_page(
    slug: str,
    db: DBSession,
    pagination: Pagination,
    hours: int = 24,
):
    article_stmt = (
        select(Article)
        .join(Summary, Article.id == Summary.article_id)
        .where(Summary.category == slug)
        .order_by(Article.created_at.desc())
    )

    count_stmt = select(func.count()).select_from(article_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    article_stmt = article_stmt.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(article_stmt)
    articles = result.scalars().all()

    return {
        "slug": slug,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": math.ceil(total / pagination.page_size) if pagination.page_size else 0,
        "items": [
            {
                "id": str(a.id),
                "final_title": a.final_title,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "final_image_url": a.final_image_url,
            }
            for a in articles
        ],
    }
