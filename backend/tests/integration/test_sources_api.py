"""T077: Integration tests for Sources API."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rss_source import RSSSource
from tests.conftest import make_source


class TestSourcesAPI:
    @pytest.mark.asyncio
    async def test_list_sources_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/sources")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_create_source(self, client: AsyncClient):
        payload = {
            "url": "https://example.com/rss/new",
            "name": "New Source",
            "category": "technology",
        }
        resp = await client.post("/api/v1/sources", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == payload["url"]
        assert data["name"] == payload["name"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_sources_after_create(self, client: AsyncClient):
        payload = {"url": "https://example.com/rss/list", "name": "List Source", "category": "finance"}
        await client.post("/api/v1/sources", json=payload)  # 201

        resp = await client.get("/api/v1/sources")
        assert resp.status_code == 200
        sources = resp.json()
        assert len(sources) >= 1

    @pytest.mark.asyncio
    async def test_update_source(self, client: AsyncClient):
        create_resp = await client.post("/api/v1/sources", json={
            "url": "https://example.com/rss/update",
            "name": "Update Me",
            "category": "technology",
        })
        assert create_resp.status_code == 201
        source_id = create_resp.json()["id"]

        resp = await client.patch(f"/api/v1/sources/{source_id}", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_source(self, client: AsyncClient):
        create_resp = await client.post("/api/v1/sources", json={
            "url": "https://example.com/rss/delete",
            "name": "Delete Me",
            "category": "technology",
        })
        assert create_resp.status_code == 201
        source_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/sources/{source_id}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_source(self, client: AsyncClient):
        resp = await client.delete("/api/v1/sources/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
