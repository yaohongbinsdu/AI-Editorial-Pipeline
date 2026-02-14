from __future__ import annotations

import asyncio

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.article import Article
from app.models.summary import Summary
from app.utils.logging import get_logger
from app.utils.retry import async_retry

logger = get_logger("vectorizer")

EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072


class Vectorizer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @async_retry(max_retries=3, backoff_base=2.0)
    async def generate_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding

    async def vectorize_article(self, article_id: str, db: AsyncSession) -> list[float] | None:
        stmt = select(Summary).where(Summary.article_id == article_id)
        result = await db.execute(stmt)
        summary = result.scalar_one_or_none()

        if not summary or not summary.vector_tldr:
            logger.warning("no_vector_tldr", article_id=article_id)
            return None

        embedding = await self.generate_embedding(summary.vector_tldr)

        article = await db.get(Article, article_id)
        if article:
            article.status = "vectorized"

        logger.info("article_vectorized", article_id=article_id)
        return embedding

    async def vectorize_batch(
        self, article_ids: list[str], db: AsyncSession
    ) -> dict[str, list[float]]:
        semaphore = asyncio.Semaphore(20)
        results: dict[str, list[float]] = {}

        async def _process(aid: str) -> None:
            async with semaphore:
                try:
                    emb = await self.vectorize_article(aid, db)
                    if emb:
                        results[aid] = emb
                except Exception as exc:
                    logger.error("vectorize_failed", article_id=aid, error=str(exc))

        await asyncio.gather(*[_process(aid) for aid in article_ids])
        logger.info("batch_vectorized", total=len(article_ids), success=len(results))
        return results
