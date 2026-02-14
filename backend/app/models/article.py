import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import ArticleStatusEnum, Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rss_sources.id"), nullable=False
    )
    original_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    original_title: Mapped[str | None] = mapped_column(String(500))
    original_content: Mapped[str | None] = mapped_column(Text)
    original_image_url: Mapped[str | None] = mapped_column(Text)

    firecrawl_title: Mapped[str | None] = mapped_column(String(500))
    firecrawl_content: Mapped[str | None] = mapped_column(Text)

    iframely_title: Mapped[str | None] = mapped_column(String(500))
    iframely_content: Mapped[str | None] = mapped_column(Text)
    iframely_image_url: Mapped[str | None] = mapped_column(Text)

    gemini_title: Mapped[str | None] = mapped_column(String(500))
    gemini_content: Mapped[str | None] = mapped_column(Text)

    final_title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    final_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    final_image_url: Mapped[str | None] = mapped_column(Text)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    author: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ArticleStatusEnum.PENDING.value
    )
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clusters.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    source = relationship("RSSSource", back_populates="articles", lazy="selectin")
    summary = relationship("Summary", back_populates="article", uselist=False, lazy="selectin")
    vector = relationship("Vector", back_populates="article", uselist=False, lazy="selectin")
    gravity_score = relationship(
        "GravityScore", back_populates="article", uselist=False, lazy="selectin"
    )
    cluster = relationship("Cluster", back_populates="articles", lazy="selectin")

    __table_args__ = (
        Index("idx_article_status", "status"),
        Index("idx_article_source", "source_id"),
        Index("idx_article_cluster", "cluster_id"),
        Index("idx_article_published", published_at.desc()),
        Index("idx_article_created", created_at.desc()),
    )
