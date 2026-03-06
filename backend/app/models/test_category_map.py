import uuid
from datetime import datetime

from sqlalchemy import String, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestCategoryMap(Base):
    __tablename__ = "test_category_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("requirements.id", ondelete="SET NULL")
    )
    test_category: Mapped[str] = mapped_column(String(50), nullable=False)
    sub_category: Mapped[str | None] = mapped_column(String(100))
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pipeline_layer: Mapped[str | None] = mapped_column(String(50))
    tool_suggestion: Mapped[str | None] = mapped_column(String(100))
    domain: Mapped[str | None] = mapped_column(String(50))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="test_category_maps")  # type: ignore[name-defined] # noqa: F821
