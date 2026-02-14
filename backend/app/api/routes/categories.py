import math
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from sqlalchemy import func, select

from sqlalchemy import case, or_
from sqlalchemy.orm import aliased

from app.api.deps import DBSession, Pagination
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.gravity_score import GravityScore
from app.models.rss_source import RSSSource
from app.models.summary import Summary

router = APIRouter()

VALID_CATEGORIES = [
    "finance", "technology", "commercial_space", "new_energy",
    "healthcare", "agriculture", "consumer", "real_estate",
    "manufacturing", "crypto", "macro_economy", "regulation", "other",
]


def _effective_category():
    """COALESCE(summary.category, rss_source.category) — use AI category if available, else source category."""
    return func.coalesce(Summary.category, RSSSource.category)


@router.get("/categories")
async def list_categories(db: DBSession):
    # Count articles per effective category (summary category or source category fallback)
    article_counts_stmt = (
        select(
            func.coalesce(Summary.category, RSSSource.category).label("cat"),
            func.count(Article.id).label("cnt"),
        )
        .select_from(Article)
        .join(RSSSource, Article.source_id == RSSSource.id)
        .outerjoin(Summary, Article.id == Summary.article_id)
        .group_by("cat")
    )
    article_counts = {
        row.cat: row.cnt
        for row in (await db.execute(article_counts_stmt)).all()
    }

    cluster_counts_stmt = (
        select(Cluster.category, func.count(Cluster.id).label("cnt"))
        .group_by(Cluster.category)
    )
    cluster_counts = {
        row.category: row.cnt
        for row in (await db.execute(cluster_counts_stmt)).all()
    }

    results = []
    for cat in VALID_CATEGORIES:
        results.append({
            "slug": cat,
            "article_count": article_counts.get(cat, 0),
            "cluster_count": cluster_counts.get(cat, 0),
        })
    return results


@router.get("/categories/{slug}")
async def get_category_page(
    slug: str,
    db: DBSession,
    pagination: Pagination,
    hours: int = 24,
):
    # Match articles by summary category OR source category fallback
    article_stmt = (
        select(Article)
        .join(RSSSource, Article.source_id == RSSSource.id)
        .outerjoin(Summary, Article.id == Summary.article_id)
        .where(func.coalesce(Summary.category, RSSSource.category) == slug)
        .order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
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
                "source_name": a.source.name if a.source else None,
            }
            for a in articles
        ],
    }
