import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectConfig(Base):
    __tablename__ = "project_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    db_url: Mapped[str | None] = mapped_column(String(1000))
    dbt_project_dir: Mapped[str | None] = mapped_column(String(500))
    gx_context_dir: Mapped[str | None] = mapped_column(String(500))
    extra: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    azure_wiki_org: Mapped[str | None] = mapped_column(String(255))
    azure_wiki_project: Mapped[str | None] = mapped_column(String(255))
    azure_wiki_name: Mapped[str | None] = mapped_column(String(255))
    azure_wiki_pat: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="config")  # type: ignore[name-defined] # noqa: F821
