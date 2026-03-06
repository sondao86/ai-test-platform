"""Initial migration — create all tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-03-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Projects
    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="created"),
        sa.Column("current_phase", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # BRD Chunks
    op.create_table(
        "brd_chunks",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("section_title", sa.String(500), nullable=False),
        sa.Column("section_type", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("cross_references", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Clarifications
    op.create_table(
        "clarifications",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("chunk_id", sa.UUID(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(30), nullable=False, server_default="medium"),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("context", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chunk_id"], ["brd_chunks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Requirements
    op.create_table(
        "requirements",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("chunk_id", sa.UUID(), nullable=True),
        sa.Column("requirement_id", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(30), nullable=False, server_default="medium"),
        sa.Column("business_rules", postgresql.JSONB(), server_default="[]"),
        sa.Column("kpis", postgresql.JSONB(), server_default="[]"),
        sa.Column("data_elements", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chunk_id"], ["brd_chunks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Test Category Mappings
    op.create_table(
        "test_category_mappings",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("requirement_id", sa.UUID(), nullable=True),
        sa.Column("test_category", sa.String(50), nullable=False),
        sa.Column("sub_category", sa.String(100), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("pipeline_layer", sa.String(50), nullable=True),
        sa.Column("tool_suggestion", sa.String(100), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Test Cases
    op.create_table(
        "test_cases",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("category_map_id", sa.UUID(), nullable=True),
        sa.Column("test_id", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("test_category", sa.String(50), nullable=False),
        sa.Column("pipeline_layer", sa.String(50), nullable=False),
        sa.Column("tool", sa.String(100), nullable=False),
        sa.Column("sql_logic", sa.Text(), nullable=True),
        sa.Column("dbt_test_yaml", sa.Text(), nullable=True),
        sa.Column("great_expectations_config", postgresql.JSONB(), nullable=True),
        sa.Column("input_data", postgresql.JSONB(), nullable=True),
        sa.Column("expected_result", postgresql.JSONB(), nullable=True),
        sa.Column("severity", sa.String(30), nullable=False, server_default="medium"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("sla_seconds", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["category_map_id"], ["test_category_mappings.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Agent Reviews
    op.create_table(
        "agent_reviews",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(50), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("comments", postgresql.JSONB(), server_default="[]"),
        sa.Column("additions", postgresql.JSONB(), server_default="[]"),
        sa.Column("consolidation_summary", postgresql.JSONB(), nullable=True),
        sa.Column("revision_round", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Phase History
    op.create_table(
        "phase_history",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=False),
        sa.Column("phase_name", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("user_decision", sa.String(30), nullable=True),
        sa.Column("user_feedback", sa.String(2000), nullable=True),
        sa.Column("revision_round", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("snapshot", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("phase_history")
    op.drop_table("agent_reviews")
    op.drop_table("test_cases")
    op.drop_table("test_category_mappings")
    op.drop_table("requirements")
    op.drop_table("clarifications")
    op.drop_table("brd_chunks")
    op.drop_table("projects")
