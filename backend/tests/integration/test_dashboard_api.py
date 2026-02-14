"""T087: Integration tests for Dashboard API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rss_source import RSSSource
from app.models.article import Article
from app.models.summary import Summary
from app.models.gravity_score import GravityScore
from tests.conftest import make_source, make_article, make_summary, make_gravity_score


class TestDashboardAPI:
    @pytest.mark.asyncio
    async def test_overview_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_articles" in data
        assert "category_breakdown" in data
        assert "top_clusters" in data
        assert "must_read_articles" in data
        assert "pipeline_health" in data
        assert data["total_articles"] == 0

    @pytest.mark.asyncio
    async def test_overview_with_data(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()

        sum_data = make_summary(art_data["id"])
        db_session.add(Summary(**sum_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/dashboard/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_articles"] >= 1

    @pytest.mark.asyncio
    async def test_trending_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/trending")
        assert resp.status_code == 200
        data = resp.json()
        assert "trending_clusters" in data
        assert "trending_articles" in data

    @pytest.mark.asyncio
    async def test_trending_with_data(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()

        gs_data = make_gravity_score(art_data["id"], novelty_gate=True)
        db_session.add(GravityScore(**gs_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/dashboard/trending")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["trending_articles"]) >= 1
