"""Add project update features: test_case is_active/source/updated_at, project brd_version, project_configs table.

Revision ID: 003_project_update_features
Revises: 002_test_execution
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_project_update_features"
down_revision: Union[str, None] = "002_test_execution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- test_cases: add is_active, source, updated_at ---
    op.add_column(
        "test_cases",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "test_cases",
        sa.Column("source", sa.String(30), nullable=False, server_default="pipeline"),
    )
    op.add_column(
        "test_cases",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Composite index for filtering active test cases by project
    op.create_index(
        "ix_test_cases_project_active",
        "test_cases",
        ["project_id", "is_active"],
    )

    # --- projects: add brd_version ---
    op.add_column(
        "projects",
        sa.Column("brd_version", sa.Integer(), nullable=False, server_default="1"),
    )

    # --- project_configs: new table ---
    op.create_table(
        "project_configs",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("db_url", sa.String(1000), nullable=True),
        sa.Column("dbt_project_dir", sa.String(500), nullable=True),
        sa.Column("gx_context_dir", sa.String(500), nullable=True),
        sa.Column("extra", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )


def downgrade() -> None:
    op.drop_table("project_configs")
    op.drop_column("projects", "brd_version")
    op.drop_index("ix_test_cases_project_active", table_name="test_cases")
    op.drop_column("test_cases", "updated_at")
    op.drop_column("test_cases", "source")
    op.drop_column("test_cases", "is_active")
