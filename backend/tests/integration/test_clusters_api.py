"""T083: Integration tests for Clusters API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cluster import Cluster
from app.models.rss_source import RSSSource
from app.models.article import Article
from tests.conftest import make_cluster, make_source, make_article


class TestClustersAPI:
    @pytest.mark.asyncio
    async def test_list_clusters_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/clusters")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_clusters_with_data(self, client: AsyncClient, db_session: AsyncSession):
        cl_data = make_cluster(article_count=3)  # min_articles=2 by default
        db_session.add(Cluster(**cl_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/clusters")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_get_cluster_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/clusters/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_cluster_detail(self, client: AsyncClient, db_session: AsyncSession):
        cl_data = make_cluster()
        db_session.add(Cluster(**cl_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get(f"/api/v1/clusters/{cl_data['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(cl_data["id"])

    @pytest.mark.asyncio
    async def test_filter_clusters_by_category(self, client: AsyncClient, db_session: AsyncSession):
        db_session.add(Cluster(**make_cluster(category="finance", article_count=3)))
        db_session.add(Cluster(**make_cluster(category="technology", article_count=3)))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/clusters?category=finance")
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["category"] == "finance"
