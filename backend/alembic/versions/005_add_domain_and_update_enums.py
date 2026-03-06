"""Add domain column and migrate layer/category values.

Revision ID: 005_add_domain_and_update_enums
Revises: 004_add_wiki_sync_columns
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_add_domain_and_update_enums"
down_revision: Union[str, None] = "004_add_wiki_sync_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Category mapping: old DQ dimensions → new operational categories ---
CATEGORY_MAP = {
    "completeness": "data_quality",
    "consistency": "data_quality",
    "uniqueness": "data_quality",
    "accuracy": "business_logic",
    "timeliness": "freshness",
    "validity": "schema_contract",
}

# --- Layer mapping: generic ETL → medallion ---
LAYER_MAP = {
    "staging": "bronze",
    "intermediate": "silver",
    "mart": "gold",
}


def upgrade() -> None:
    # --- Add domain columns ---
    op.add_column(
        "test_cases",
        sa.Column("domain", sa.String(50), nullable=True),
    )
    op.add_column(
        "test_category_mappings",
        sa.Column("domain", sa.String(50), nullable=True),
    )

    # --- Migrate category values in test_cases ---
    test_cases = sa.table(
        "test_cases",
        sa.column("test_category", sa.String),
        sa.column("pipeline_layer", sa.String),
    )
    for old_cat, new_cat in CATEGORY_MAP.items():
        op.execute(
            test_cases.update()
            .where(test_cases.c.test_category == op.inline_literal(old_cat))
            .values(test_category=op.inline_literal(new_cat))
        )

    # --- Migrate layer values in test_cases ---
    for old_layer, new_layer in LAYER_MAP.items():
        op.execute(
            test_cases.update()
            .where(test_cases.c.pipeline_layer == op.inline_literal(old_layer))
            .values(pipeline_layer=op.inline_literal(new_layer))
        )

    # --- Migrate category values in test_category_mappings ---
    tcm = sa.table(
        "test_category_mappings",
        sa.column("test_category", sa.String),
        sa.column("pipeline_layer", sa.String),
    )
    for old_cat, new_cat in CATEGORY_MAP.items():
        op.execute(
            tcm.update()
            .where(tcm.c.test_category == op.inline_literal(old_cat))
            .values(test_category=op.inline_literal(new_cat))
        )

    # --- Migrate layer values in test_category_mappings ---
    for old_layer, new_layer in LAYER_MAP.items():
        op.execute(
            tcm.update()
            .where(tcm.c.pipeline_layer == op.inline_literal(old_layer))
            .values(pipeline_layer=op.inline_literal(new_layer))
        )


def downgrade() -> None:
    # --- Reverse layer mapping ---
    REVERSE_LAYER = {v: k for k, v in LAYER_MAP.items()}
    # --- Reverse category mapping (note: data_quality maps back to completeness) ---
    REVERSE_CATEGORY = {
        "schema_contract": "validity",
        "data_quality": "completeness",
        "business_logic": "accuracy",
        "freshness": "timeliness",
    }

    test_cases = sa.table(
        "test_cases",
        sa.column("test_category", sa.String),
        sa.column("pipeline_layer", sa.String),
    )
    for new_layer, old_layer in REVERSE_LAYER.items():
        op.execute(
            test_cases.update()
            .where(test_cases.c.pipeline_layer == op.inline_literal(new_layer))
            .values(pipeline_layer=op.inline_literal(old_layer))
        )
    for new_cat, old_cat in REVERSE_CATEGORY.items():
        op.execute(
            test_cases.update()
            .where(test_cases.c.test_category == op.inline_literal(new_cat))
            .values(test_category=op.inline_literal(old_cat))
        )

    tcm = sa.table(
        "test_category_mappings",
        sa.column("test_category", sa.String),
        sa.column("pipeline_layer", sa.String),
    )
    for new_layer, old_layer in REVERSE_LAYER.items():
        op.execute(
            tcm.update()
            .where(tcm.c.pipeline_layer == op.inline_literal(new_layer))
            .values(pipeline_layer=op.inline_literal(old_layer))
        )
    for new_cat, old_cat in REVERSE_CATEGORY.items():
        op.execute(
            tcm.update()
            .where(tcm.c.test_category == op.inline_literal(new_cat))
            .values(test_category=op.inline_literal(old_cat))
        )

    op.drop_column("test_category_mappings", "domain")
    op.drop_column("test_cases", "domain")
