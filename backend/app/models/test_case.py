import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    category_map_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_category_mappings.id", ondelete="SET NULL")
    )
    test_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    test_category: Mapped[str] = mapped_column(String(50), nullable=False)
    pipeline_layer: Mapped[str] = mapped_column(String(50), nullable=False)
    tool: Mapped[str] = mapped_column(String(100), nullable=False)
    sql_logic: Mapped[str | None] = mapped_column(Text)
    dbt_test_yaml: Mapped[str | None] = mapped_column(Text)
    great_expectations_config: Mapped[dict | None] = mapped_column(JSONB)
    input_data: Mapped[dict | None] = mapped_column(JSONB)
    expected_result: Mapped[dict | None] = mapped_column(JSONB)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="medium")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    sla_seconds: Mapped[int | None] = mapped_column(Integer)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true", default=True)
    domain: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(30), nullable=False, server_default="pipeline", default="pipeline")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="test_cases")  # type: ignore[name-defined] # noqa: F821
