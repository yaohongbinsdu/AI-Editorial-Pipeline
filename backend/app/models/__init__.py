import enum

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=20, max_overflow=10)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class CategoryEnum(str, enum.Enum):
    FINANCE = "finance"
    TECHNOLOGY = "technology"
    COMMERCIAL_SPACE = "commercial_space"
    NEW_ENERGY = "new_energy"
    HEALTHCARE = "healthcare"
    AGRICULTURE = "agriculture"
    CONSUMER = "consumer"
    REAL_ESTATE = "real_estate"
    MANUFACTURING = "manufacturing"
    CRYPTO = "crypto"
    MACRO_ECONOMY = "macro_economy"
    REGULATION = "regulation"
    OTHER = "other"


class ArticleStatusEnum(str, enum.Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    FETCHED = "fetched"
    SUMMARIZING = "summarizing"
    SUMMARIZED = "summarized"
    VECTORIZING = "vectorizing"
    VECTORIZED = "vectorized"
    SCORING = "scoring"
    COMPLETED = "completed"
    FETCH_FAILED = "fetch_failed"
    SUMMARY_FAILED = "summary_failed"
    SCORE_FAILED = "score_failed"
