import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PhaseHistory(Base):
    __tablename__ = "phase_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    phase_id: Mapped[int] = mapped_column(Integer, nullable=False)
    phase_name: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    user_decision: Mapped[str | None] = mapped_column(String(30))
    user_feedback: Mapped[str | None] = mapped_column(String(2000))
    revision_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    snapshot: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="phase_history")  # type: ignore[name-defined] # noqa: F821
