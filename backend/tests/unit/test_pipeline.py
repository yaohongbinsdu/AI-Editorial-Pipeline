"""T085: Unit tests for pipeline orchestration service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.pipeline import run_pipeline, STEPS


class TestPipeline:
    def test_module_has_run_pipeline(self):
        from app.services import pipeline
        assert hasattr(pipeline, "run_pipeline")

    def test_steps_defined(self):
        assert len(STEPS) == 7
        assert "rss_fetch" in STEPS
        assert "gravity_score" in STEPS

    @pytest.mark.asyncio
    async def test_run_pipeline_creates_pipeline_run(self):
        """run_pipeline should add a PipelineRun to the session."""
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        # Mock execute to return empty results for queries
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.services.pipeline.RSSFetcher") as MockFetcher, \
             patch("app.services.pipeline._log_step", new_callable=AsyncMock):
            mock_fetcher_instance = AsyncMock()
            mock_fetcher_instance.fetch_all_sources = AsyncMock(return_value=[])
            MockFetcher.return_value = mock_fetcher_instance

            result = await run_pipeline(mock_db)
            # Verify add was called (PipelineRun creation)
            assert mock_db.add.called
            assert result is not None
