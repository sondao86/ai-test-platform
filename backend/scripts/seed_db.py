"""
Seed the database with demo data from db-init.yaml.

Usage:
    docker compose exec app python scripts/seed_db.py

Reads backend/docs/db-init.yaml and inserts seed data in FK-safe order.
Idempotent: skips if the demo project already exists.
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

import yaml
from sqlalchemy import select

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_factory, engine
from app.models import (
    AgentReview,
    BrdChunk,
    Clarification,
    PhaseHistory,
    Project,
    ProjectConfig,
    Requirement,
    TestCase,
    TestCategoryMap,
    TestExecution,
    TestResult,
)

# Insertion order respects FK dependencies
TABLE_MODEL_MAP = [
    ("projects", Project),
    ("project_configs", ProjectConfig),
    ("brd_chunks", BrdChunk),
    ("clarifications", Clarification),
    ("requirements", Requirement),
    ("test_category_mappings", TestCategoryMap),
    ("test_cases", TestCase),
    ("test_executions", TestExecution),
    ("test_results", TestResult),
    ("agent_reviews", AgentReview),
    ("phase_history", PhaseHistory),
]

YAML_PATH = Path(__file__).resolve().parent.parent / "docs" / "db-init.yaml"

DEMO_PROJECT_ID = UUID("550e8400-e29b-41d4-a716-446655440001")


def _coerce_uuids(data: dict, model_cls) -> dict:
    """Convert string UUID fields to uuid.UUID objects based on column types."""
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(model_cls)
    result = {}
    for key, value in data.items():
        if value is None:
            result[key] = value
            continue
        col = mapper.columns.get(key)
        if col is not None and hasattr(col.type, "impl") and "UUID" in str(col.type):
            result[key] = UUID(value) if isinstance(value, str) else value
        elif col is not None and "UUID" in str(col.type):
            result[key] = UUID(value) if isinstance(value, str) else value
        else:
            result[key] = value
    return result


async def seed():
    """Load seed data from YAML and insert into the database."""
    if not YAML_PATH.exists():
        print(f"ERROR: Seed file not found at {YAML_PATH}")
        sys.exit(1)

    with open(YAML_PATH) as f:
        config = yaml.safe_load(f)

    seed_data = config.get("seed", {})
    if not seed_data:
        print("No seed data found in YAML.")
        return

    async with async_session_factory() as session:
        # Idempotency check: skip if demo project exists
        result = await session.execute(
            select(Project).where(Project.id == DEMO_PROJECT_ID)
        )
        if result.scalar_one_or_none() is not None:
            print(f"Demo project {DEMO_PROJECT_ID} already exists. Skipping seed.")
            return

        total_rows = 0

        for table_key, model_cls in TABLE_MODEL_MAP:
            rows = seed_data.get(table_key, [])
            if not rows:
                continue

            for row_data in rows:
                coerced = _coerce_uuids(row_data, model_cls)
                obj = model_cls(**coerced)
                session.add(obj)

            total_rows += len(rows)
            print(f"  {table_key}: {len(rows)} row(s) staged")

        await session.commit()
        print(f"\nSeed complete: {total_rows} rows inserted across {len(TABLE_MODEL_MAP)} tables.")


async def main():
    print(f"Loading seed data from {YAML_PATH}\n")
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
