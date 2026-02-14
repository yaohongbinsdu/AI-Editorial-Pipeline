import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    articles_discovered: Mapped[int] = mapped_column(Integer, default=0)
    articles_processed: Mapped[int] = mapped_column(Integer, default=0)
    articles_failed: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    step_logs = relationship("PipelineStepLog", back_populates="pipeline_run", lazy="selectin")

    __table_args__ = (
        Index("idx_pipeline_run_started", started_at.desc()),
        Index("idx_pipeline_run_status", "status"),
    )
