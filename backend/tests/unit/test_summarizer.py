"""T079: Unit tests for summarizer service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.summarizer import Summarizer, SummarySchema


class TestSummarySchema:
    def test_valid_schema(self):
        data = {
            "human_tldr": "测试摘要",
            "vector_tldr": "test vector tldr",
            "key_points": ["a", "b", "c", "d", "e"],
            "rewritten_title": "Rewritten",
            "category": "technology",
            "tags": ["tag1", "tag2", "tag3"],
        }
        schema = SummarySchema(**data)
        assert len(schema.key_points) == 5
        assert schema.category == "technology"

    def test_invalid_category_falls_back_to_other(self):
        data = {
            "human_tldr": "测试",
            "vector_tldr": "test",
            "key_points": ["a", "b", "c", "d", "e"],
            "rewritten_title": "Title",
            "category": "invalid_cat",
            "tags": ["a", "b", "c"],
        }
        schema = SummarySchema(**data)
        assert schema.category == "other"


class TestSummarizer:
    def test_class_exists(self):
        with patch("app.services.summarizer.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            s = Summarizer()
            assert hasattr(s, "generate_summary")
            assert hasattr(s, "summarize_article")

    @pytest.mark.asyncio
    async def test_short_content_skipped(self):
        """Articles with content < 50 chars should return None."""
        with patch("app.services.summarizer.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            summarizer = Summarizer()

        mock_article = MagicMock()
        mock_article.final_content = "Too short"
        mock_article.id = "test-id"

        mock_db = AsyncMock()
        result = await summarizer.generate_summary(mock_article, mock_db)
        assert result is None
