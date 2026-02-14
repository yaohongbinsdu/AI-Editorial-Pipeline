import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    article_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    centroid = mapped_column(Vector(3072) if Vector else Text, nullable=True)
    expansion_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expansion_query: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    articles = relationship("Article", back_populates="cluster", lazy="selectin")

    __table_args__ = (
        Index("idx_cluster_category", "category"),
        Index("idx_cluster_article_count", article_count.desc()),
        Index("idx_cluster_updated", last_updated_at.desc()),
    )
