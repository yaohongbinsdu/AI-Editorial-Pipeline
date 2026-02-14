import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

try:
    from pgvector.sqlalchemy import Vector as PGVector
except ImportError:
    PGVector = None


class Vector(Base):
    __tablename__ = "vectors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), unique=True, nullable=False
    )
    embedding = mapped_column(PGVector(3072) if PGVector else String, nullable=True)
    model_used: Mapped[str] = mapped_column(String(50), nullable=False, default="text-embedding-3-large")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    article = relationship("Article", back_populates="vector")
