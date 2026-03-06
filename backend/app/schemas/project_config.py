from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectConfigCreate(BaseModel):
    db_url: str | None = None
    dbt_project_dir: str | None = None
    gx_context_dir: str | None = None
    extra: dict | None = None
    azure_wiki_org: str | None = None
    azure_wiki_project: str | None = None
    azure_wiki_name: str | None = None
    azure_wiki_pat: str | None = None


class ProjectConfigUpdate(BaseModel):
    db_url: str | None = None
    dbt_project_dir: str | None = None
    gx_context_dir: str | None = None
    extra: dict | None = None
    azure_wiki_org: str | None = None
    azure_wiki_project: str | None = None
    azure_wiki_name: str | None = None
    azure_wiki_pat: str | None = None


class ProjectConfigResponse(BaseModel):
    id: UUID
    project_id: UUID
    db_url: str | None
    dbt_project_dir: str | None
    gx_context_dir: str | None
    extra: dict | None
    azure_wiki_org: str | None = None
    azure_wiki_project: str | None = None
    azure_wiki_name: str | None = None
    has_azure_wiki_pat: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, config) -> "ProjectConfigResponse":
        """Build response from ORM model, computing has_azure_wiki_pat."""
        return cls(
            id=config.id,
            project_id=config.project_id,
            db_url=config.db_url,
            dbt_project_dir=config.dbt_project_dir,
            gx_context_dir=config.gx_context_dir,
            extra=config.extra,
            azure_wiki_org=config.azure_wiki_org,
            azure_wiki_project=config.azure_wiki_project,
            azure_wiki_name=config.azure_wiki_name,
            has_azure_wiki_pat=bool(config.azure_wiki_pat),
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
