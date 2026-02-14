from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import DBSession
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.gravity_score import GravityScore
from app.models.pipeline_run import PipelineRun
from app.models.summary import Summary

router = APIRouter()


@router.get("/dashboard/overview")
async def get_overview(db: DBSession, hours: int = 24):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    total_stmt = select(func.count()).select_from(Article).where(Article.created_at >= cutoff)
    total_articles = (await db.execute(total_stmt)).scalar() or 0

    cat_stmt = (
        select(Summary.category, func.count().label("count"))
        .join(Article, Summary.article_id == Article.id)
        .where(Article.created_at >= cutoff)
        .group_by(Summary.category)
        .order_by(func.count().desc())
    )
    cat_result = await db.execute(cat_stmt)
    category_breakdown = [
        {"slug": row.category, "article_count": row.count}
        for row in cat_result.all()
    ]

    top_clusters_stmt = (
        select(Cluster)
        .where(Cluster.last_updated_at >= cutoff)
        .order_by(Cluster.article_count.desc())
        .limit(5)
    )
    top_clusters_result = await db.execute(top_clusters_stmt)
    top_clusters = [
        {
            "id": str(c.id),
            "title": c.title,
            "category": c.category,
            "article_count": c.article_count,
        }
        for c in top_clusters_result.scalars().all()
    ]

    must_read_stmt = (
        select(Article)
        .join(GravityScore, Article.id == GravityScore.article_id)
        .options(selectinload(Article.source), selectinload(Article.summary))
        .where(GravityScore.editorial_vote == "must_read")
        .where(Article.created_at >= cutoff)
        .order_by(GravityScore.composite_score.desc())
        .limit(10)
    )
    must_read_result = await db.execute(must_read_stmt)
    must_read_articles = [
        {
            "id": str(a.id),
            "final_title": a.final_title,
            "rewritten_title": a.summary.rewritten_title if a.summary else None,
            "human_tldr": a.summary.human_tldr if a.summary else None,
            "source_name": a.source.name if a.source else "",
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "final_image_url": a.final_image_url,
        }
        for a in must_read_result.scalars().all()
    ]

    last_run_stmt = select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(1)
    last_run_result = await db.execute(last_run_stmt)
    last_run = last_run_result.scalar_one_or_none()

    return {
        "time_window_hours": hours,
        "total_articles": total_articles,
        "category_breakdown": category_breakdown,
        "top_clusters": top_clusters,
        "must_read_articles": must_read_articles,
        "market_focus": category_breakdown[:5],
        "pipeline_health": {
            "last_run_at": last_run.completed_at.isoformat() if last_run and last_run.completed_at else None,
            "last_run_status": last_run.status if last_run else None,
            "articles_processed_24h": total_articles,
        },
    }


@router.get("/dashboard/trending")
async def get_trending(db: DBSession, limit: int = 10):
    trending_clusters_stmt = (
        select(Cluster)
        .order_by(Cluster.article_count.desc(), Cluster.last_updated_at.desc())
        .limit(limit)
    )
    clusters_result = await db.execute(trending_clusters_stmt)
    trending_clusters = [
        {
            "id": str(c.id),
            "title": c.title,
            "category": c.category,
            "article_count": c.article_count,
            "last_updated_at": c.last_updated_at.isoformat() if c.last_updated_at else None,
        }
        for c in clusters_result.scalars().all()
    ]

    trending_articles_stmt = (
        select(Article)
        .join(GravityScore, Article.id == GravityScore.article_id)
        .options(selectinload(Article.source), selectinload(Article.summary))
        .where(GravityScore.novelty_gate.is_(True))
        .order_by(GravityScore.composite_score.desc())
        .limit(limit)
    )
    articles_result = await db.execute(trending_articles_stmt)
    trending_articles = [
        {
            "id": str(a.id),
            "final_title": a.final_title,
            "rewritten_title": a.summary.rewritten_title if a.summary else None,
            "human_tldr": a.summary.human_tldr if a.summary else None,
            "source_name": a.source.name if a.source else "",
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "final_image_url": a.final_image_url,
        }
        for a in articles_result.scalars().all()
    ]

    return {
        "trending_clusters": trending_clusters,
        "trending_articles": trending_articles,
    }
