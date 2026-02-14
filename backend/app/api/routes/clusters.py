import math
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import DBSession, Pagination
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.summary import Summary

router = APIRouter()


@router.get("/clusters")
async def list_clusters(
    db: DBSession,
    pagination: Pagination,
    category: str | None = None,
    min_articles: int = 2,
    sort_by: str = "last_updated_at",
):
    stmt = select(Cluster).where(Cluster.article_count >= min_articles)

    if category:
        stmt = stmt.where(Cluster.category == category)

    sort_col = getattr(Cluster, sort_by, Cluster.last_updated_at)
    stmt = stmt.order_by(sort_col.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(stmt)
    clusters = result.scalars().all()

    return {
        "items": [
            {
                "id": str(c.id),
                "title": c.title,
                "category": c.category,
                "article_count": c.article_count,
                "expansion_triggered": c.expansion_triggered,
                "first_seen_at": c.first_seen_at.isoformat() if c.first_seen_at else None,
                "last_updated_at": c.last_updated_at.isoformat() if c.last_updated_at else None,
            }
            for c in clusters
        ],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": math.ceil(total / pagination.page_size) if pagination.page_size else 0,
    }


@router.get("/clusters/{cluster_id}")
async def get_cluster(cluster_id: str, db: DBSession):
    cluster = await db.get(Cluster, uuid.UUID(cluster_id))
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    articles_stmt = (
        select(Article)
        .options(selectinload(Article.source), selectinload(Article.summary), selectinload(Article.gravity_score))
        .where(Article.cluster_id == cluster.id)
        .order_by(Article.published_at.desc())
    )
    result = await db.execute(articles_stmt)
    articles = result.scalars().all()

    def _brief(a: Article) -> dict:
        s = a.summary
        g = a.gravity_score
        return {
            "id": str(a.id),
            "final_title": a.final_title,
            "rewritten_title": s.rewritten_title if s else None,
            "human_tldr": s.human_tldr if s else None,
            "category": s.category if s else None,
            "tags": s.tags if s else [],
            "composite_score": g.composite_score if g else None,
            "editorial_vote": g.editorial_vote if g else None,
            "viral_potential": g.viral_potential if g else None,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "source_name": a.source.name if a.source else "",
            "final_image_url": a.final_image_url,
        }

    return {
        "id": str(cluster.id),
        "title": cluster.title,
        "category": cluster.category,
        "article_count": cluster.article_count,
        "expansion_triggered": cluster.expansion_triggered,
        "first_seen_at": cluster.first_seen_at.isoformat() if cluster.first_seen_at else None,
        "last_updated_at": cluster.last_updated_at.isoformat() if cluster.last_updated_at else None,
        "articles": [_brief(a) for a in articles],
    }
