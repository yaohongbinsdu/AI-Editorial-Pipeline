import math
import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import DBSession, Pagination
from app.models.article import Article
from app.models.gravity_score import GravityScore
from app.models.summary import Summary

router = APIRouter()


def _article_brief(a: Article) -> dict:
    summary = a.summary
    gravity = a.gravity_score
    return {
        "id": str(a.id),
        "final_title": a.final_title,
        "rewritten_title": summary.rewritten_title if summary else None,
        "human_tldr": summary.human_tldr if summary else None,
        "category": summary.category if summary else None,
        "tags": summary.tags if summary else [],
        "composite_score": gravity.composite_score if gravity else None,
        "editorial_vote": gravity.editorial_vote if gravity else None,
        "viral_potential": gravity.viral_potential if gravity else None,
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "source_name": a.source.name if a.source else "",
        "final_image_url": a.final_image_url,
    }


@router.get("/articles")
async def list_articles(
    db: DBSession,
    pagination: Pagination,
    category: str | None = None,
    status: str | None = None,
    novelty_gate: bool | None = None,
    editorial_vote: str | None = None,
    min_score: float | None = None,
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
):
    stmt = select(Article).options(
        selectinload(Article.source),
        selectinload(Article.summary),
        selectinload(Article.gravity_score),
    )

    if category:
        stmt = stmt.join(Summary, Article.id == Summary.article_id).where(
            Summary.category == category
        )
    if status:
        stmt = stmt.where(Article.status == status)
    if novelty_gate is not None:
        stmt = stmt.join(GravityScore, Article.id == GravityScore.article_id).where(
            GravityScore.novelty_gate == novelty_gate
        )
    if editorial_vote:
        stmt = stmt.join(
            GravityScore, Article.id == GravityScore.article_id, isouter=True
        ).where(GravityScore.editorial_vote == editorial_vote)
    if min_score is not None:
        stmt = stmt.join(
            GravityScore, Article.id == GravityScore.article_id, isouter=True
        ).where(GravityScore.composite_score >= min_score)

    sort_col = getattr(Article, sort_by, Article.created_at)
    if sort_by == "composite_score":
        stmt = stmt.join(
            GravityScore, Article.id == GravityScore.article_id, isouter=True
        )
        sort_col = GravityScore.composite_score
    stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(stmt)
    articles = result.scalars().unique().all()

    return {
        "items": [_article_brief(a) for a in articles],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": math.ceil(total / pagination.page_size) if pagination.page_size else 0,
    }


@router.get("/articles/{article_id}")
async def get_article(article_id: str, db: DBSession):
    stmt = (
        select(Article)
        .options(
            selectinload(Article.source),
            selectinload(Article.summary),
            selectinload(Article.gravity_score),
            selectinload(Article.cluster),
        )
        .where(Article.id == uuid.UUID(article_id))
    )
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    summary = article.summary
    gravity = article.gravity_score

    return {
        "id": str(article.id),
        "original_url": article.original_url,
        "final_title": article.final_title,
        "final_content": article.final_content,
        "final_image_url": article.final_image_url,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "author": article.author,
        "status": article.status,
        "source": {
            "id": str(article.source.id),
            "name": article.source.name,
            "category": article.source.category,
        } if article.source else None,
        "summary": {
            "human_tldr": summary.human_tldr,
            "vector_tldr": summary.vector_tldr,
            "key_points": summary.key_points,
            "rewritten_title": summary.rewritten_title,
            "category": summary.category,
            "tags": summary.tags,
        } if summary else None,
        "gravity_score": {
            "industry_impact": gravity.industry_impact,
            "consumer_impact": gravity.consumer_impact,
            "actionability": gravity.actionability,
            "risk_urgency": gravity.risk_urgency,
            "novelty": gravity.novelty,
            "technical_depth": gravity.technical_depth,
            "second_order_potential": gravity.second_order_potential,
            "builder_relevance": gravity.builder_relevance,
            "entertainment_value": gravity.entertainment_value,
            "signal_to_noise": gravity.signal_to_noise,
            "viral_potential": gravity.viral_potential,
            "early_trend_signal": gravity.early_trend_signal,
            "pr_fluff": gravity.pr_fluff,
            "speculation": gravity.speculation,
            "concreteness": gravity.concreteness,
            "paid_sponsorship": gravity.paid_sponsorship,
            "editorial_vote": gravity.editorial_vote,
            "novelty_gate": gravity.novelty_gate,
            "composite_score": gravity.composite_score,
            "reasoning": gravity.reasoning,
        } if gravity else None,
        "cluster": {
            "id": str(article.cluster.id),
            "title": article.cluster.title,
            "category": article.cluster.category,
            "article_count": article.cluster.article_count,
        } if article.cluster else None,
    }


@router.get("/articles/{article_id}/similar")
async def get_similar_articles(
    article_id: str,
    db: DBSession,
    limit: int = 5,
    threshold: float = 0.75,
):
    return []
