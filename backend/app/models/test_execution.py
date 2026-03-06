import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestExecution(Base):
    """A single execution run — runs all (or selected) test cases for a project."""

    __tablename__ = "test_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    triggered_by: Mapped[str] = mapped_column(String(50), nullable=False, default="user")

    total_tests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    duration_ms: Mapped[int | None] = mapped_column(Integer)
    config: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    results: Mapped[list["TestResult"]] = relationship(
        back_populates="execution", cascade="all, delete-orphan"
    )
    project: Mapped["Project"] = relationship(back_populates="executions")  # type: ignore[name-defined] # noqa: F821


class TestResult(Base):
    """Result of a single test case within an execution run."""

    __tablename__ = "test_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_executions.id", ondelete="CASCADE"), nullable=False
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    result: Mapped[str | None] = mapped_column(String(20))  # pass | fail | error | skip
    executor_type: Mapped[str] = mapped_column(String(30), nullable=False)

    # Execution details
    actual_output: Mapped[dict | None] = mapped_column(JSONB)
    expected_output: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(String(2000))
    error_detail: Mapped[dict | None] = mapped_column(JSONB)
    rows_scanned: Mapped[int | None] = mapped_column(Integer)
    rows_failed: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    sql_executed: Mapped[str | None] = mapped_column(String(5000))
    logs: Mapped[list | None] = mapped_column(JSONB, default=list)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    execution: Mapped["TestExecution"] = relationship(back_populates="results")
    test_case: Mapped["TestCase"] = relationship()  # type: ignore[name-defined] # noqa: F821
