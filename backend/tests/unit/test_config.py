"""T073: Unit tests for app configuration."""
import pytest

from app.config import Settings


class TestSettings:
    def test_default_database_url(self):
        s = Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://localhost/test",
            DATABASE_URL_SYNC="postgresql://localhost/test",
        )
        assert "postgresql" in s.DATABASE_URL

    def test_default_redis_url(self):
        s = Settings(_env_file=None)
        assert s.REDIS_URL.startswith("redis://")

    def test_api_key_fields_exist(self):
        s = Settings(_env_file=None)
        assert hasattr(s, "OPENAI_API_KEY")
        assert hasattr(s, "ANTHROPIC_API_KEY")
        assert hasattr(s, "GOOGLE_AI_API_KEY")
        assert hasattr(s, "FIRECRAWL_API_KEY")
        assert hasattr(s, "IFRAMELY_API_KEY")

    def test_pipeline_interval_default(self):
        s = Settings(_env_file=None)
        assert s.PIPELINE_INTERVAL_MINUTES == 60

    def test_log_level_default(self):
        s = Settings(_env_file=None)
        assert s.LOG_LEVEL == "INFO"
