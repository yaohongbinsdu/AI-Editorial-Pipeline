"""T072: Unit tests for ORM models, enums, and relationships."""
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArticleStatusEnum, CategoryEnum, Base
from app.models.rss_source import RSSSource
from app.models.article import Article
from app.models.summary import Summary
from app.models.gravity_score import GravityScore
from app.models.pipeline_run import PipelineRun
from app.models.pipeline_step_log import PipelineStepLog
from app.models.cluster import Cluster

from tests.conftest import make_source, make_article, make_summary, make_gravity_score, make_cluster, make_pipeline_run


# ── Enum tests ───────────────────────────────────────────────────────────────

class TestCategoryEnum:
    def test_has_13_members(self):
        assert len(CategoryEnum) == 13

    def test_known_categories(self):
        expected = {
            "finance", "technology", "commercial_space", "new_energy",
            "healthcare", "agriculture", "consumer", "real_estate",
            "manufacturing", "crypto", "macro_economy", "regulation", "other",
        }
        actual = {e.value for e in CategoryEnum}
        assert actual == expected


class TestArticleStatusEnum:
    def test_has_all_statuses(self):
        expected = {
            "pending", "fetching", "fetched", "summarizing", "summarized",
            "vectorizing", "vectorized", "scoring", "completed",
            "fetch_failed", "summary_failed", "score_failed",
        }
        actual = {e.value for e in ArticleStatusEnum}
        assert actual == expected


# ── Model instantiation tests ────────────────────────────────────────────────

class TestRSSSourceModel:
    @pytest.mark.asyncio
    async def test_create_and_read(self, db_session: AsyncSession):
        data = make_source()
        src = RSSSource(**data)
        db_session.add(src)
        await db_session.flush()

        result = await db_session.get(RSSSource, data["id"])
        assert result is not None
        assert result.url == data["url"]
        assert result.name == "Test Source"
        assert result.enabled is True
        assert result.consecutive_failures == 0


class TestArticleModel:
    @pytest.mark.asyncio
    async def test_create_with_source(self, db_session: AsyncSession):
        src_data = make_source()
        src = RSSSource(**src_data)
        db_session.add(src)
        await db_session.flush()

        art_data = make_article(src_data["id"])
        art = Article(**art_data)
        db_session.add(art)
        await db_session.flush()

        result = await db_session.get(Article, art_data["id"])
        assert result is not None
        assert result.source_id == src_data["id"]
        assert result.status == "completed"
        assert result.final_title == "Test Article Title"

    @pytest.mark.asyncio
    async def test_default_status_is_pending(self, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"], status="pending")
        art = Article(**art_data)
        db_session.add(art)
        await db_session.flush()
        assert art.status == "pending"


class TestSummaryModel:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()

        sum_data = make_summary(art_data["id"])
        db_session.add(Summary(**sum_data))
        await db_session.flush()

        result = await db_session.get(Summary, sum_data["id"])
        assert result is not None
        assert result.category == "technology"
        assert len(result.key_points) == 5


class TestGravityScoreModel:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        src_data = make_source()
        db_session.add(RSSSource(**src_data))
        await db_session.flush()

        art_data = make_article(src_data["id"])
        db_session.add(Article(**art_data))
        await db_session.flush()

        gs_data = make_gravity_score(art_data["id"])
        db_session.add(GravityScore(**gs_data))
        await db_session.flush()

        result = await db_session.get(GravityScore, gs_data["id"])
        assert result is not None
        assert result.composite_score == 7.5
        assert result.editorial_vote == "interesting"
        assert result.novelty_gate is True
        assert 0 <= result.industry_impact <= 10


class TestClusterModel:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        cl_data = make_cluster()
        db_session.add(Cluster(**cl_data))
        await db_session.flush()

        result = await db_session.get(Cluster, cl_data["id"])
        assert result is not None
        assert result.article_count == 3
        assert result.expansion_triggered is False


class TestPipelineRunModel:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        run_data = make_pipeline_run()
        db_session.add(PipelineRun(**run_data))
        await db_session.flush()

        result = await db_session.get(PipelineRun, run_data["id"])
        assert result is not None
        assert result.status == "completed"
        assert result.articles_discovered == 10
        assert result.duration_seconds == 120.5


class TestPipelineStepLogModel:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        run_data = make_pipeline_run()
        db_session.add(PipelineRun(**run_data))
        await db_session.flush()

        log = PipelineStepLog(
            id=uuid.uuid4(),
            pipeline_run_id=run_data["id"],
            step_name="rss_fetch",
            status="success",
            duration_ms=450,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
        await db_session.flush()

        result = await db_session.get(PipelineStepLog, log.id)
        assert result is not None
        assert result.step_name == "rss_fetch"
        assert result.duration_ms == 450
