from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.cluster import Cluster
from app.utils.logging import get_logger

logger = get_logger("clusterer")

SIMILARITY_THRESHOLD = 0.82
MAX_CLUSTER_SIZE = 50


class Clusterer:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_nearest_cluster(
        self, embedding: list[float], threshold: float = SIMILARITY_THRESHOLD
    ) -> tuple[Cluster | None, float]:
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

        stmt = text("""
            SELECT id, title, category, article_count,
                   1 - (centroid <=> :embedding::vector) AS similarity
            FROM clusters
            WHERE centroid IS NOT NULL
            ORDER BY centroid <=> :embedding::vector
            LIMIT 1
        """).bindparams(embedding=embedding_str)

        result = await self.db.execute(stmt)
        row = result.first()

        if row is None or row.similarity < threshold:
            return None, 0.0

        cluster = await self.db.get(Cluster, row.id)
        return cluster, float(row.similarity)

    async def assign_to_cluster(
        self, article: Article, embedding: list[float]
    ) -> Cluster:
        cluster, similarity = await self.find_nearest_cluster(embedding)

        if cluster and cluster.article_count < MAX_CLUSTER_SIZE:
            article.cluster_id = cluster.id
            cluster.article_count += 1
            cluster.last_updated_at = datetime.now(timezone.utc)
            logger.info(
                "article_assigned_to_cluster",
                article_id=str(article.id),
                cluster_id=str(cluster.id),
                similarity=similarity,
            )

            await self.check_expansion(cluster)
            return cluster

        summary = article.summary
        new_cluster = Cluster(
            title=summary.rewritten_title if summary else article.final_title,
            category=summary.category if summary else "other",
            article_count=1,
        )
        self.db.add(new_cluster)
        await self.db.flush()

        article.cluster_id = new_cluster.id
        logger.info(
            "new_cluster_created",
            article_id=str(article.id),
            cluster_id=str(new_cluster.id),
            title=new_cluster.title,
        )
        return new_cluster

    async def check_expansion(self, cluster: Cluster) -> None:
        if cluster.article_count >= 3 and not cluster.expansion_triggered:
            logger.info(
                "expansion_triggered",
                cluster_id=str(cluster.id),
                article_count=cluster.article_count,
            )
            cluster.expansion_triggered = True

    async def split_large_cluster(self, cluster_id: uuid.UUID) -> list[Cluster]:
        cluster = await self.db.get(Cluster, cluster_id)
        if not cluster or cluster.article_count <= MAX_CLUSTER_SIZE:
            return []

        logger.info(
            "split_large_cluster",
            cluster_id=str(cluster_id),
            article_count=cluster.article_count,
        )
        return []
