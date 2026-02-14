"""T082: Unit tests for clusterer service."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.clusterer import Clusterer, SIMILARITY_THRESHOLD, MAX_CLUSTER_SIZE


class TestClusterer:
    def test_class_exists(self):
        mock_db = AsyncMock()
        c = Clusterer(mock_db)
        assert hasattr(c, "assign_to_cluster")
        assert hasattr(c, "find_nearest_cluster")
        assert hasattr(c, "check_expansion")

    def test_similarity_threshold(self):
        assert SIMILARITY_THRESHOLD == 0.82

    def test_max_cluster_size(self):
        assert MAX_CLUSTER_SIZE == 50

    @pytest.mark.asyncio
    async def test_check_expansion_triggers_at_3(self):
        """Expansion should trigger when article_count >= 3."""
        mock_db = AsyncMock()
        c = Clusterer(mock_db)

        cluster = MagicMock()
        cluster.article_count = 3
        cluster.expansion_triggered = False
        cluster.id = "test-cluster-id"

        await c.check_expansion(cluster)
        assert cluster.expansion_triggered is True

    @pytest.mark.asyncio
    async def test_check_expansion_no_trigger_below_3(self):
        """Expansion should NOT trigger when article_count < 3."""
        mock_db = AsyncMock()
        c = Clusterer(mock_db)

        cluster = MagicMock()
        cluster.article_count = 2
        cluster.expansion_triggered = False

        await c.check_expansion(cluster)
        assert cluster.expansion_triggered is False
