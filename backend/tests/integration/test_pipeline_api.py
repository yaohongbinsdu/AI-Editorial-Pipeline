"""T086: Integration tests for Pipeline API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pipeline_run import PipelineRun
from tests.conftest import make_pipeline_run


class TestPipelineAPI:
    @pytest.mark.asyncio
    async def test_get_pipeline_status(self, client: AsyncClient):
        resp = await client.get("/api/v1/pipeline/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "is_running" in data
        assert "current_run" in data
        assert "last_completed_run" in data
        assert "step_stats_24h" in data

    @pytest.mark.asyncio
    async def test_get_pipeline_runs_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/pipeline/runs")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert data == []

    @pytest.mark.asyncio
    async def test_get_pipeline_runs_with_data(self, client: AsyncClient, db_session: AsyncSession):
        run_data = make_pipeline_run()
        db_session.add(PipelineRun(**run_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get("/api/v1/pipeline/runs")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_pipeline_run_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/pipeline/runs/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_pipeline_run_detail(self, client: AsyncClient, db_session: AsyncSession):
        run_data = make_pipeline_run()
        db_session.add(PipelineRun(**run_data))
        await db_session.flush()
        await db_session.commit()

        resp = await client.get(f"/api/v1/pipeline/runs/{run_data['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(run_data["id"])
        assert "step_logs" in data
