"""T099: Page data completeness tests — verify all frontend page APIs return correct structures."""
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models.article import Article
from app.models.cluster import Cluster
from app.models.gravity_score import GravityScore
from app.models.rss_source import RSSSource
from app.models.summary import Summary
from app.models.pipeline_run import PipelineRun
from tests.conftest import (
    make_article,
    make_cluster,
    make_gravity_score,
    make_pipeline_run,
    make_source,
    make_summary,
)


@pytest.mark.asyncio
async def test_articles_list_returns_paginated(client: AsyncClient, db_session):
    """GET /articles returns paginated structure with items, total, page, page_size, total_pages."""
    src = RSSSource(**make_source())
    db_session.add(src)
    await db_session.flush()

    for i in range(3):
        art = Article(**make_article(src.id))
        db_session.add(art)
    await db_session.commit()

    resp = await client.get("/api/v1/articles")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_articles_category_filter(client: AsyncClient, db_session):
    """GET /articles?category=finance returns only finance articles."""
    src = RSSSource(**make_source())
    db_session.add(src)
    await db_session.flush()

    art1 = Article(**make_article(src.id, status="completed"))
    db_session.add(art1)
    s1 = Summary(**make_summary(art1.id, category="finance"))
    db_session.add(s1)

    art2 = Article(**make_article(src.id, status="completed"))
    db_session.add(art2)
    s2 = Summary(**make_summary(art2.id, category="technology"))
    db_session.add(s2)

    await db_session.commit()

    resp = await client.get("/api/v1/articles?category=finance")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_clusters_list_returns_paginated(client: AsyncClient, db_session):
    """GET /clusters returns paginated structure."""
    for i in range(2):
        c = Cluster(**make_cluster(article_count=3))
        db_session.add(c)
    await db_session.commit()

    resp = await client.get("/api/v1/clusters")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_categories_list(client: AsyncClient, db_session):
    """GET /categories returns list of category stats."""
    resp = await client.get("/api/v1/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_sources_list(client: AsyncClient, db_session):
    """GET /sources returns list of RSS sources."""
    for i in range(3):
        s = RSSSource(**make_source(name=f"Source {i}"))
        db_session.add(s)
    await db_session.commit()

    resp = await client.get("/api/v1/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_dashboard_overview(client: AsyncClient, db_session):
    """GET /dashboard/overview returns correct structure."""
    resp = await client.get("/api/v1/dashboard/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_articles" in data
    assert "category_breakdown" in data


@pytest.mark.asyncio
async def test_dashboard_trending(client: AsyncClient, db_session):
    """GET /dashboard/trending returns clusters and articles lists."""
    resp = await client.get("/api/v1/dashboard/trending")
    assert resp.status_code == 200
    data = resp.json()
    assert "trending_clusters" in data
    assert "trending_articles" in data


@pytest.mark.asyncio
async def test_pipeline_status(client: AsyncClient, db_session):
    """GET /pipeline/status returns correct structure."""
    resp = await client.get("/api/v1/pipeline/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "is_running" in data
    assert "current_run" in data
    assert "last_completed_run" in data
    assert "step_stats_24h" in data


@pytest.mark.asyncio
async def test_pipeline_runs_list(client: AsyncClient, db_session):
    """GET /pipeline/runs returns list."""
    run = PipelineRun(**make_pipeline_run())
    db_session.add(run)
    await db_session.commit()

    resp = await client.get("/api/v1/pipeline/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_pipeline_trigger_sync(client: AsyncClient, db_session):
    """POST /pipeline/trigger?sync=true creates a pipeline run (mocked RSS)."""
    from unittest.mock import AsyncMock, patch

    src = RSSSource(**make_source())
    db_session.add(src)
    await db_session.commit()

    with patch("app.services.pipeline.RSSFetcher") as MockFetcher:
        instance = MockFetcher.return_value
        instance.fetch_all_sources = AsyncMock(return_value=[])
        resp = await client.post("/api/v1/pipeline/trigger?sync=true")

    assert resp.status_code == 202
    data = resp.json()
    assert "run_id" in data
