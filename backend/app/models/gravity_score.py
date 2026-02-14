import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class GravityScore(Base):
    __tablename__ = "gravity_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), unique=True, nullable=False
    )

    industry_impact: Mapped[float] = mapped_column(Float, nullable=False)
    consumer_impact: Mapped[float] = mapped_column(Float, nullable=False)
    actionability: Mapped[float] = mapped_column(Float, nullable=False)
    risk_urgency: Mapped[float] = mapped_column(Float, nullable=False)

    novelty: Mapped[float] = mapped_column(Float, nullable=False)
    technical_depth: Mapped[float] = mapped_column(Float, nullable=False)
    second_order_potential: Mapped[float] = mapped_column(Float, nullable=False)
    builder_relevance: Mapped[float] = mapped_column(Float, nullable=False)
    entertainment_value: Mapped[float] = mapped_column(Float, nullable=False)

    signal_to_noise: Mapped[float] = mapped_column(Float, nullable=False)
    viral_potential: Mapped[float] = mapped_column(Float, nullable=False)
    early_trend_signal: Mapped[float] = mapped_column(Float, nullable=False)

    pr_fluff: Mapped[float] = mapped_column(Float, nullable=False)
    speculation: Mapped[float] = mapped_column(Float, nullable=False)
    concreteness: Mapped[float] = mapped_column(Float, nullable=False)
    paid_sponsorship: Mapped[float] = mapped_column(Float, nullable=False)

    editorial_vote: Mapped[str] = mapped_column(String(20), nullable=False)
    novelty_gate: Mapped[bool] = mapped_column(Boolean, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text)
    model_used: Mapped[str] = mapped_column(String(50), nullable=False)
    scoring_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    article = relationship("Article", back_populates="gravity_score")

    __table_args__ = (
        Index("idx_gravity_composite", composite_score.desc()),
        Index("idx_gravity_novelty_gate", "novelty_gate"),
        Index("idx_gravity_editorial_vote", "editorial_vote"),
    )
