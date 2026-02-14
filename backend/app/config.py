from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/editorial"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/editorial"
    REDIS_URL: str = "redis://localhost:6379/0"

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""

    FIRECRAWL_API_KEY: str = ""
    IFRAMELY_API_KEY: str = ""

    PIPELINE_INTERVAL_MINUTES: int = 60
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
