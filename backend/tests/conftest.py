"""Shared test fixtures for the AI Editorial Pipeline backend."""
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool, Text, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Register SQLite type compilers for PostgreSQL-specific types BEFORE importing models
# ---------------------------------------------------------------------------
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

# Teach SQLite how to render JSONB → TEXT
_orig_process = getattr(SQLiteTypeCompiler, "visit_JSONB", None)
if _orig_process is None:
    SQLiteTypeCompiler.visit_JSONB = lambda self, type_, **kw: "TEXT"

# Teach SQLite how to render pgvector Vector → TEXT
try:
    from pgvector.sqlalchemy import Vector as PGVector
    SQLiteTypeCompiler.visit_VECTOR = lambda self, type_, **kw: "TEXT"
except ImportError:
    pass

from app.models import Base

# ---------------------------------------------------------------------------
# In-memory SQLite async engine for tests (no pgvector)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite doesn't support UUID natively – register adapter
@event.listens_for(test_engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=OFF")
    cursor.close()


TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# ---------------------------------------------------------------------------
# DB session fixture with table creation / teardown
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# FastAPI test client with DB dependency override
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from app.api.deps import get_db
    from app.main import app

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------
def make_source(**overrides) -> dict:
    defaults = {
        "id": uuid.uuid4(),
        "url": f"https://example.com/rss/{uuid.uuid4().hex[:8]}",
        "name": "Test Source",
        "category": "technology",
        "enabled": True,
        "fetch_interval_minutes": 60,
        "consecutive_failures": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return defaults


def make_article(source_id: uuid.UUID, **overrides) -> dict:
    defaults = {
        "id": uuid.uuid4(),
        "source_id": source_id,
        "original_url": f"https://example.com/article/{uuid.uuid4().hex[:8]}",
        "original_title": "Test Article Title",
        "final_title": "Test Article Title",
        "final_content": "This is test content that is long enough for summarization. " * 5,
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return defaults


def make_summary(article_id: uuid.UUID, **overrides) -> dict:
    defaults = {
        "id": uuid.uuid4(),
        "article_id": article_id,
        "human_tldr": "Test TLDR summary",
        "vector_tldr": "test vector tldr with keywords entities numbers",
        "key_points": ["point1", "point2", "point3", "point4", "point5"],
        "rewritten_title": "Rewritten Test Title",
        "category": "technology",
        "tags": ["test", "technology"],
        "model_used": "gpt-4o-mini",
        "generation_time_ms": 500,
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return defaults


def make_gravity_score(article_id: uuid.UUID, **overrides) -> dict:
    defaults = {
        "id": uuid.uuid4(),
        "article_id": article_id,
        "industry_impact": 7.0,
        "consumer_impact": 5.0,
        "actionability": 6.0,
        "risk_urgency": 4.0,
        "novelty": 8.0,
        "technical_depth": 7.0,
        "second_order_potential": 5.0,
        "builder_relevance": 6.0,
        "entertainment_value": 4.0,
        "signal_to_noise": 8.0,
        "viral_potential": 6.0,
        "early_trend_signal": 7.0,
        "pr_fluff": 2.0,
        "speculation": 3.0,
        "concreteness": 7.0,
        "paid_sponsorship": 1.0,
        "editorial_vote": "interesting",
        "novelty_gate": True,
        "composite_score": 7.5,
        "reasoning": "Test reasoning",
        "model_used": "claude-3-5-sonnet",
        "scoring_time_ms": 1200,
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return defaults


def make_cluster(**overrides) -> dict:
    defaults = {
        "id": uuid.uuid4(),
        "title": "Test Cluster",
        "category": "technology",
        "article_count": 3,
        "expansion_triggered": False,
        "first_seen_at": datetime.now(timezone.utc),
        "last_updated_at": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return defaults


def make_pipeline_run(**overrides) -> dict:
    defaults = {
        "id": uuid.uuid4(),
        "started_at": datetime.now(timezone.utc),
        "status": "completed",
        "articles_discovered": 10,
        "articles_processed": 8,
        "articles_failed": 2,
        "duration_seconds": 120.5,
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return defaults
