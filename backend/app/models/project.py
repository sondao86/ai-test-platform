import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="created")
    current_phase: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_name: Mapped[str | None] = mapped_column(String(255))
    raw_text: Mapped[str | None] = mapped_column(Text)
    brd_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", default=1)
    brd_source: Mapped[str | None] = mapped_column(String(30), default="upload")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    chunks: Mapped[list["BrdChunk"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    clarifications: Mapped[list["Clarification"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    test_category_maps: Mapped[list["TestCategoryMap"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    agent_reviews: Mapped[list["AgentReview"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    phase_history: Mapped[list["PhaseHistory"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    executions: Mapped[list["TestExecution"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
    config: Mapped["ProjectConfig | None"] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")  # type: ignore[name-defined] # noqa: F821
