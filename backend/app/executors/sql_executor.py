"""Custom SQL executor — runs SQL validation queries against a database."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.executors.base import BaseExecutor, ExecutionContext, ExecutionResult, TestCaseSpec

logger = logging.getLogger(__name__)


class SqlExecutor(BaseExecutor):
    executor_type = "custom_sql"

    async def validate(self, spec: TestCaseSpec) -> list[str]:
        errors = []
        if not spec.sql_logic:
            errors.append(f"Test {spec.test_id}: sql_logic is required for custom_sql executor")
        return errors

    async def execute(
        self, spec: TestCaseSpec, ctx: ExecutionContext
    ) -> ExecutionResult:
        if not spec.sql_logic:
            return ExecutionResult(
                result="error",
                error_message="No SQL logic provided",
                logs=["SKIP: No sql_logic defined"],
            )

        if ctx.dry_run:
            return ExecutionResult(
                result="pass",
                sql_executed=spec.sql_logic,
                logs=["DRY RUN: SQL validated, not executed"],
            )

        if not ctx.db_url:
            return ExecutionResult(
                result="error",
                error_message="No database URL configured for SQL execution",
                logs=["ERROR: db_url not set in execution context"],
            )

        logs = []
        with self._timed() as timer:
            try:
                engine = create_async_engine(ctx.db_url, echo=False)
                async with engine.connect() as conn:
                    logs.append(f"Executing SQL: {spec.sql_logic[:200]}...")

                    result = await conn.execute(text(spec.sql_logic))
                    rows = result.fetchall()
                    columns = list(result.keys()) if result.keys() else []

                    rows_scanned = len(rows)
                    actual_output = {
                        "columns": columns,
                        "rows": [dict(zip(columns, row)) for row in rows[:100]],  # cap at 100
                        "total_rows": rows_scanned,
                    }

                    # Determine pass/fail
                    test_result = self._evaluate_result(
                        spec, actual_output, rows_scanned
                    )

                    logs.append(f"Query returned {rows_scanned} rows")
                    logs.append(f"Result: {test_result}")

                await engine.dispose()

                return ExecutionResult(
                    result=test_result,
                    actual_output=actual_output,
                    expected_output=spec.expected_result,
                    rows_scanned=rows_scanned,
                    rows_failed=rows_scanned if test_result == "fail" else 0,
                    duration_ms=timer.elapsed_ms,
                    sql_executed=spec.sql_logic,
                    logs=logs,
                )
            except Exception as e:
                logger.exception("SQL execution error for %s", spec.test_id)
                logs.append(f"ERROR: {e}")
                return ExecutionResult(
                    result="error",
                    error_message=str(e),
                    error_detail={"exception_type": type(e).__name__},
                    duration_ms=timer.elapsed_ms,
                    sql_executed=spec.sql_logic,
                    logs=logs,
                )

    def _evaluate_result(
        self, spec: TestCaseSpec, actual: dict, row_count: int
    ) -> str:
        """Evaluate whether the SQL result constitutes pass or fail.

        Convention:
        - For validation queries (find bad rows): 0 rows = pass, >0 rows = fail
        - If expected_result has explicit criteria, use those
        """
        expected = spec.expected_result or {}

        # Explicit expected row count
        if "row_count" in expected:
            return "pass" if row_count == expected["row_count"] else "fail"

        # Explicit expected null_count, fail_count, etc.
        if "null_count" in expected:
            return "pass" if row_count <= expected["null_count"] else "fail"

        # Explicit max_rows (threshold)
        if "max_rows" in expected:
            return "pass" if row_count <= expected["max_rows"] else "fail"

        # Default: 0 bad rows = pass (most DQ tests find violations)
        return "pass" if row_count == 0 else "fail"
