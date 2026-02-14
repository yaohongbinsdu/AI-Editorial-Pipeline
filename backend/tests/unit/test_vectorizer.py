"""T081: Unit tests for vectorizer service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.vectorizer import Vectorizer


class TestVectorizer:
    def test_class_exists(self):
        with patch("app.services.vectorizer.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            v = Vectorizer()
            assert hasattr(v, "generate_embedding")
            assert hasattr(v, "vectorize_article")
            assert hasattr(v, "vectorize_batch")

    @pytest.mark.asyncio
    async def test_generate_embedding_returns_3072_dims(self):
        """generate_embedding should return a 3072-dim vector."""
        with patch("app.services.vectorizer.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            vectorizer = Vectorizer()

        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.1] * 3072

        vectorizer.client = MagicMock()
        vectorizer.client.embeddings.create = AsyncMock(return_value=mock_response)

        result = await vectorizer.generate_embedding("test text")
        assert result is not None
        assert len(result) == 3072
