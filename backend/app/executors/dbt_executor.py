"""dbt test executor — runs dbt test commands via CLI."""

from __future__ import annotations

import asyncio
import json
import logging
import os

from app.executors.base import BaseExecutor, ExecutionContext, ExecutionResult, TestCaseSpec

logger = logging.getLogger(__name__)


class DbtExecutor(BaseExecutor):
    executor_type = "dbt_test"

    async def validate(self, spec: TestCaseSpec) -> list[str]:
        errors = []
        if not spec.dbt_test_yaml and not spec.sql_logic:
            errors.append(
                f"Test {spec.test_id}: dbt_test_yaml or sql_logic required for dbt executor"
            )
        return errors

    async def execute(
        self, spec: TestCaseSpec, ctx: ExecutionContext
    ) -> ExecutionResult:
        if ctx.dry_run:
            return ExecutionResult(
                result="pass",
                sql_executed=spec.sql_logic,
                logs=[
                    "DRY RUN: dbt test validated",
                    f"YAML: {spec.dbt_test_yaml[:200] if spec.dbt_test_yaml else 'N/A'}",
                ],
            )

        if not ctx.dbt_project_dir:
            # Fallback: if we have sql_logic, run as raw SQL via dbt run-operation
            if spec.sql_logic:
                return await self._run_as_sql(spec, ctx)
            return ExecutionResult(
                result="skip",
                error_message="No dbt project directory configured",
                logs=["SKIP: dbt_project_dir not set. Configure to run dbt tests."],
            )

        logs = []
        with self._timed() as timer:
            try:
                # Run dbt test with select
                cmd = [
                    "dbt", "test",
                    "--project-dir", ctx.dbt_project_dir,
                    "--select", spec.test_id,
                    "--output", "json",
                    "--no-use-colors",
                ]

                logs.append(f"Running: {' '.join(cmd)}")

                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env={**os.environ},
                )

                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=spec.sla_seconds or 120
                )

                stdout_str = stdout.decode()
                stderr_str = stderr.decode()
                logs.append(f"Exit code: {proc.returncode}")

                if proc.returncode == 0:
                    result = "pass"
                    logs.append("dbt test PASSED")
                elif proc.returncode == 1:
                    result = "fail"
                    logs.append("dbt test FAILED")
                else:
                    result = "error"
                    logs.append(f"dbt error: {stderr_str[:500]}")

                # Parse dbt JSON output if possible
                actual_output = {"stdout": stdout_str[:2000], "returncode": proc.returncode}
                try:
                    for line in stdout_str.strip().split("\n"):
                        if line.strip().startswith("{"):
                            parsed = json.loads(line)
                            if "data" in parsed:
                                actual_output = parsed["data"]
                                break
                except (json.JSONDecodeError, KeyError):
                    pass

                return ExecutionResult(
                    result=result,
                    actual_output=actual_output,
                    expected_output=spec.expected_result,
                    duration_ms=timer.elapsed_ms,
                    sql_executed=spec.sql_logic,
                    logs=logs,
                )

            except asyncio.TimeoutError:
                logs.append(f"TIMEOUT after {spec.sla_seconds or 120}s")
                return ExecutionResult(
                    result="error",
                    error_message=f"dbt test timed out after {spec.sla_seconds or 120}s",
                    duration_ms=timer.elapsed_ms,
                    logs=logs,
                )
            except FileNotFoundError:
                logs.append("ERROR: dbt CLI not found")
                return ExecutionResult(
                    result="error",
                    error_message="dbt CLI not found. Install with: pip install dbt-core",
                    duration_ms=timer.elapsed_ms,
                    logs=logs,
                )
            except Exception as e:
                logger.exception("dbt execution error for %s", spec.test_id)
                logs.append(f"ERROR: {e}")
                return ExecutionResult(
                    result="error",
                    error_message=str(e),
                    duration_ms=timer.elapsed_ms,
                    logs=logs,
                )

    async def _run_as_sql(self, spec: TestCaseSpec, ctx: ExecutionContext) -> ExecutionResult:
        """Fallback: run the SQL logic directly if no dbt project is configured."""
        from app.executors.sql_executor import SqlExecutor

        sql_exec = SqlExecutor()
        result = await sql_exec.execute(spec, ctx)
        result.logs.insert(0, "Fallback: ran as raw SQL (no dbt project configured)")
        return result
