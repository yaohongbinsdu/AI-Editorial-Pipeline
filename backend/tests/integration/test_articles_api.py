"""T078: Integration tests for Articles API."""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rss_source import RSSSource
from app.models.article import Article
from tests.conftest import make_source, make_article


class TestArticlesAPI:
    @pytest.mark.asyncio
    async def test_list_articles_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/articles")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_articles_with_data(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/articles")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_get_article_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/articles/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_article_detail(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get(f"/api/v1/articles/{art_data['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(art_data["id"])

    @pytest.mark.asyncio
    async def test_list_articles_pagination(self, client: AsyncClient, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        for i in range(5):
            art_data = make_article(src_data["id"])
            db_session.add(Article(**art_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/articles?page=1&page_size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
