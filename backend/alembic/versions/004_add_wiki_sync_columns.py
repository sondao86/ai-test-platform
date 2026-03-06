"""Add wiki sync columns to project_configs and brd_source to projects.

Revision ID: 004_add_wiki_sync_columns
Revises: 003_project_update_features
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_add_wiki_sync_columns"
down_revision: Union[str, None] = "003_project_update_features"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- project_configs: add Azure Wiki fields ---
    op.add_column(
        "project_configs",
        sa.Column("azure_wiki_org", sa.String(255), nullable=True),
    )
    op.add_column(
        "project_configs",
        sa.Column("azure_wiki_project", sa.String(255), nullable=True),
    )
    op.add_column(
        "project_configs",
        sa.Column("azure_wiki_name", sa.String(255), nullable=True),
    )
    op.add_column(
        "project_configs",
        sa.Column("azure_wiki_pat", sa.String(500), nullable=True),
    )

    # --- projects: add brd_source ---
    op.add_column(
        "projects",
        sa.Column("brd_source", sa.String(30), nullable=True, server_default="upload"),
    )


def downgrade() -> None:
    op.drop_column("projects", "brd_source")
    op.drop_column("project_configs", "azure_wiki_pat")
    op.drop_column("project_configs", "azure_wiki_name")
    op.drop_column("project_configs", "azure_wiki_project")
    op.drop_column("project_configs", "azure_wiki_org")
