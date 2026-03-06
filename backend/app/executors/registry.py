"""Executor registry — maps tool type to executor class."""

from __future__ import annotations

from app.executors.base import BaseExecutor
from app.executors.dbt_executor import DbtExecutor
from app.executors.gx_executor import GxExecutor
from app.executors.sql_executor import SqlExecutor

_EXECUTORS: dict[str, BaseExecutor] = {
    "custom_sql": SqlExecutor(),
    "dbt_test": DbtExecutor(),
    "dbt_macro": DbtExecutor(),  # dbt macros use same executor
    "great_expectations": GxExecutor(),
}


def get_executor(tool: str) -> BaseExecutor:
    """Get executor for a given tool type.

    Falls back to SqlExecutor if tool type is unknown.
    """
    return _EXECUTORS.get(tool, _EXECUTORS["custom_sql"])


def list_executor_types() -> list[str]:
    return list(_EXECUTORS.keys())
