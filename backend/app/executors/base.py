"""Base executor interface for all test types."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ExecutionContext:
    """Context passed to executors — contains DB connection info + config."""

    db_url: str | None = None  # Target DB connection string for SQL tests
    dbt_project_dir: str | None = None
    gx_context_dir: str | None = None
    dry_run: bool = False  # If True, validate but don't execute


@dataclass
class TestCaseSpec:
    """Flat test case spec passed to executors."""

    id: str
    test_id: str
    title: str
    test_category: str
    pipeline_layer: str
    tool: str
    sql_logic: str | None = None
    dbt_test_yaml: str | None = None
    great_expectations_config: dict | None = None
    input_data: dict | None = None
    expected_result: dict | None = None
    severity: str = "medium"
    sla_seconds: int | None = None


@dataclass
class ExecutionResult:
    """Result returned by an executor."""

    result: str  # pass | fail | error | skip
    actual_output: dict | None = None
    expected_output: dict | None = None
    error_message: str | None = None
    error_detail: dict | None = None
    rows_scanned: int | None = None
    rows_failed: int | None = None
    duration_ms: int = 0
    sql_executed: str | None = None
    logs: list[str] = field(default_factory=list)


class BaseExecutor(ABC):
    """Abstract base for test executors."""

    executor_type: str = "base"

    @abstractmethod
    async def execute(
        self, spec: TestCaseSpec, ctx: ExecutionContext
    ) -> ExecutionResult:
        """Execute a single test case and return the result."""
        ...

    @abstractmethod
    async def validate(self, spec: TestCaseSpec) -> list[str]:
        """Validate a test case spec before execution. Returns list of errors."""
        ...

    def _timed(self):
        """Helper to time execution."""
        return _Timer()


class _Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = int((time.perf_counter() - self._start) * 1000)
