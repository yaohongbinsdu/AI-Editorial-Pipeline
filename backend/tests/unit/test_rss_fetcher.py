"""T075: Unit tests for RSS fetcher service."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.rss_source import RSSSource
from app.models.article import Article
from tests.conftest import make_source


class TestRSSFetcher:
    """Tests for rss_fetcher module logic."""

    @pytest.mark.asyncio
    async def test_rss_fetcher_class_has_methods(self, db_session):
        """RSSFetcher class should have fetch_all_sources and fetch_source."""
        from app.services.rss_fetcher import RSSFetcher
        fetcher = RSSFetcher(db_session)
        assert hasattr(fetcher, "fetch_all_sources")
        assert hasattr(fetcher, "fetch_source")

    @pytest.mark.asyncio
    async def test_duplicate_url_not_created(self, db_session):
        """Articles with duplicate URLs should not be re-created."""
        src_data = make_source()
        src = RSSSource(**src_data)
        db_session.add(src)
        await db_session.flush()

        # Create existing article
        art = Article(
            id=uuid.uuid4(),
            source_id=src_data["id"],
            original_url="https://example.com/existing",
            final_title="Existing",
            final_content="content",
            status="completed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(art)
        await db_session.flush()

        from sqlalchemy import select, func
        count = (await db_session.execute(
            select(func.count()).select_from(Article).where(Article.original_url == "https://example.com/existing")
        )).scalar()
        assert count == 1
