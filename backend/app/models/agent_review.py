import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AgentReview(Base):
    __tablename__ = "agent_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    phase_id: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    comments: Mapped[list | None] = mapped_column(JSONB, default=list)
    additions: Mapped[list | None] = mapped_column(JSONB, default=list)
    consolidation_summary: Mapped[dict | None] = mapped_column(JSONB)
    revision_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="agent_reviews")  # type: ignore[name-defined] # noqa: F821
