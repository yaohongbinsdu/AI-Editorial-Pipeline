"""T080: Integration tests for Categories API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rss_source import RSSSource
from app.models.article import Article
from app.models.summary import Summary
from tests.conftest import make_source, make_article, make_summary


class TestCategoriesAPI:
    @pytest.mark.asyncio
    async def test_list_categories(self, client: AsyncClient):
        resp = await client.get("/api/v1/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_categories_with_data(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()

        sum_data = make_summary(art_data["id"], category="technology")
        db_session.add(Summary(**sum_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        cats = [c["slug"] for c in data]
        assert "technology" in cats

    @pytest.mark.asyncio
    async def test_get_category_page(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()

        sum_data = make_summary(art_data["id"], category="finance")
        db_session.add(Summary(**sum_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/categories/finance")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_nonexistent_category_returns_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/categories/nonexistent_slug_xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []
