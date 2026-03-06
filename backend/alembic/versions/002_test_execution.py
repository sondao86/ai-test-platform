"""Add test execution tables.

Revision ID: 002_test_execution
Revises: 001_initial
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_test_execution"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_executions",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("triggered_by", sa.String(50), nullable=False, server_default="user"),
        sa.Column("total_tests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("config", postgresql.JSONB(), server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "test_results",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("execution_id", sa.UUID(), nullable=False),
        sa.Column("test_case_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("result", sa.String(20), nullable=True),
        sa.Column("executor_type", sa.String(30), nullable=False),
        sa.Column("actual_output", postgresql.JSONB(), nullable=True),
        sa.Column("expected_output", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.String(2000), nullable=True),
        sa.Column("error_detail", postgresql.JSONB(), nullable=True),
        sa.Column("rows_scanned", sa.Integer(), nullable=True),
        sa.Column("rows_failed", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("sql_executed", sa.String(5000), nullable=True),
        sa.Column("logs", postgresql.JSONB(), server_default="[]"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["execution_id"], ["test_executions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("test_results")
    op.drop_table("test_executions")
