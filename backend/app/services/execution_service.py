"""Execution service — orchestrates test execution runs."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NoTestCasesForRerunError
from app.executors.base import ExecutionContext, TestCaseSpec
from app.executors.registry import get_executor
from app.models.project_config import ProjectConfig
from app.models.test_case import TestCase
from app.models.test_execution import TestExecution, TestResult
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)

    async def start_execution(
        self,
        project_id: uuid.UUID,
        test_case_ids: list[uuid.UUID] | None = None,
        config: dict | None = None,
        rerun_execution_id: uuid.UUID | None = None,
        rerun_statuses: list[str] | None = None,
    ) -> TestExecution:
        """Create and run an execution for the given test cases."""
        project = await self.project_service.get_project(project_id)

        triggered_by = "user"

        # --- Resolve test_case_ids from previous execution (re-run) ---
        if rerun_execution_id:
            triggered_by = "rerun"
            statuses = rerun_statuses or ["fail", "error"]
            prev_results = await self.db.execute(
                select(TestResult.test_case_id)
                .where(
                    TestResult.execution_id == rerun_execution_id,
                    TestResult.result.in_(statuses),
                )
            )
            rerun_ids = set(row[0] for row in prev_results.all())
            # Merge with explicit test_case_ids if provided
            if test_case_ids:
                rerun_ids = rerun_ids.intersection(set(test_case_ids))
            test_case_ids = list(rerun_ids) if rerun_ids else None
            if not test_case_ids:
                raise NoTestCasesForRerunError(str(rerun_execution_id))

        # --- Get test cases (always filter active) ---
        query = select(TestCase).where(
            TestCase.project_id == project_id,
            TestCase.is_active == True,  # noqa: E712
        )
        if test_case_ids:
            query = query.where(TestCase.id.in_(test_case_ids))
        result = await self.db.execute(query)
        test_cases = list(result.scalars().all())

        if not test_cases:
            raise ValueError("No test cases found to execute")

        # --- Merge config: saved project config (base) + request config (override) ---
        merged_config: dict = {}
        saved_config_result = await self.db.execute(
            select(ProjectConfig).where(ProjectConfig.project_id == project_id)
        )
        saved_config = saved_config_result.scalar_one_or_none()
        if saved_config:
            if saved_config.db_url:
                merged_config["db_url"] = saved_config.db_url
            if saved_config.dbt_project_dir:
                merged_config["dbt_project_dir"] = saved_config.dbt_project_dir
            if saved_config.gx_context_dir:
                merged_config["gx_context_dir"] = saved_config.gx_context_dir
            if saved_config.extra:
                merged_config.update(saved_config.extra)
        # Request config overrides saved config
        if config:
            merged_config.update(config)

        # Create execution record
        execution = TestExecution(
            project_id=project_id,
            status="running",
            triggered_by=triggered_by,
            total_tests=len(test_cases),
            config=merged_config,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(execution)
        await self.db.flush()

        # Create test result records
        test_results = []
        for tc in test_cases:
            tr = TestResult(
                execution_id=execution.id,
                test_case_id=tc.id,
                status="pending",
                executor_type=tc.tool,
            )
            self.db.add(tr)
            test_results.append((tr, tc))
        await self.db.commit()

        # Build execution context
        ctx = ExecutionContext(
            db_url=merged_config.get("db_url"),
            dbt_project_dir=merged_config.get("dbt_project_dir"),
            gx_context_dir=merged_config.get("gx_context_dir"),
            dry_run=merged_config.get("dry_run", False),
        )

        # Run all tests
        await self._run_tests(execution, test_results, ctx)

        return execution

    async def _run_tests(
        self,
        execution: TestExecution,
        test_results: list[tuple[TestResult, TestCase]],
        ctx: ExecutionContext,
    ) -> None:
        """Execute all test cases and update results."""
        passed = 0
        failed = 0
        errors = 0
        skipped = 0
        total_duration = 0

        for tr, tc in test_results:
            spec = TestCaseSpec(
                id=str(tc.id),
                test_id=tc.test_id,
                title=tc.title,
                test_category=tc.test_category,
                pipeline_layer=tc.pipeline_layer,
                tool=tc.tool,
                sql_logic=tc.sql_logic,
                dbt_test_yaml=tc.dbt_test_yaml,
                great_expectations_config=tc.great_expectations_config,
                input_data=tc.input_data,
                expected_result=tc.expected_result,
                severity=tc.severity,
                sla_seconds=tc.sla_seconds,
            )

            executor = get_executor(tc.tool)

            # Validate first
            validation_errors = await executor.validate(spec)
            if validation_errors:
                tr.status = "completed"
                tr.result = "skip"
                tr.error_message = "; ".join(validation_errors)
                tr.logs = [f"VALIDATION: {e}" for e in validation_errors]
                tr.finished_at = datetime.now(timezone.utc)
                skipped += 1
                continue

            # Execute
            tr.status = "running"
            tr.started_at = datetime.now(timezone.utc)
            await self.db.commit()

            try:
                exec_result = await executor.execute(spec, ctx)
            except Exception as e:
                logger.exception("Executor crashed for %s", tc.test_id)
                exec_result = None
                tr.status = "completed"
                tr.result = "error"
                tr.error_message = f"Executor crash: {e}"
                tr.finished_at = datetime.now(timezone.utc)
                errors += 1
                await self.db.commit()
                continue

            # Update result
            tr.status = "completed"
            tr.result = exec_result.result
            tr.actual_output = exec_result.actual_output
            tr.expected_output = exec_result.expected_output
            tr.error_message = exec_result.error_message
            tr.error_detail = exec_result.error_detail
            tr.rows_scanned = exec_result.rows_scanned
            tr.rows_failed = exec_result.rows_failed
            tr.duration_ms = exec_result.duration_ms
            tr.sql_executed = exec_result.sql_executed
            tr.logs = exec_result.logs
            tr.finished_at = datetime.now(timezone.utc)
            total_duration += exec_result.duration_ms

            if exec_result.result == "pass":
                passed += 1
            elif exec_result.result == "fail":
                failed += 1
            elif exec_result.result == "error":
                errors += 1
            else:
                skipped += 1

            await self.db.commit()

        # Update execution summary
        execution.status = "completed" if errors == 0 else "failed"
        execution.passed = passed
        execution.failed = failed
        execution.errors = errors
        execution.skipped = skipped
        execution.duration_ms = total_duration
        execution.finished_at = datetime.now(timezone.utc)
        await self.db.commit()

        logger.info(
            "Execution %s: %d passed, %d failed, %d errors, %d skipped (total %dms)",
            execution.id, passed, failed, errors, skipped, total_duration,
        )

    async def get_execution(self, execution_id: uuid.UUID) -> TestExecution:
        result = await self.db.execute(
            select(TestExecution)
            .where(TestExecution.id == execution_id)
            .options(selectinload(TestExecution.results))
        )
        execution = result.scalar_one_or_none()
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        return execution

    async def list_executions(self, project_id: uuid.UUID) -> tuple[list[TestExecution], int]:
        result = await self.db.execute(
            select(TestExecution)
            .where(TestExecution.project_id == project_id)
            .order_by(TestExecution.created_at.desc())
        )
        executions = list(result.scalars().all())
        count_result = await self.db.execute(
            select(func.count(TestExecution.id))
            .where(TestExecution.project_id == project_id)
        )
        total = count_result.scalar() or 0
        return executions, total

    async def get_execution_results(
        self, execution_id: uuid.UUID
    ) -> list[dict]:
        """Get all results with joined test case info."""
        result = await self.db.execute(
            select(TestResult, TestCase)
            .join(TestCase, TestResult.test_case_id == TestCase.id)
            .where(TestResult.execution_id == execution_id)
            .order_by(TestResult.created_at)
        )
        rows = result.all()
        output = []
        for tr, tc in rows:
            d = {
                "id": tr.id,
                "execution_id": tr.execution_id,
                "test_case_id": tr.test_case_id,
                "status": tr.status,
                "result": tr.result,
                "executor_type": tr.executor_type,
                "actual_output": tr.actual_output,
                "expected_output": tr.expected_output,
                "error_message": tr.error_message,
                "error_detail": tr.error_detail,
                "rows_scanned": tr.rows_scanned,
                "rows_failed": tr.rows_failed,
                "duration_ms": tr.duration_ms,
                "sql_executed": tr.sql_executed,
                "logs": tr.logs,
                "started_at": tr.started_at,
                "finished_at": tr.finished_at,
                "created_at": tr.created_at,
                # Joined test case info
                "test_id": tc.test_id,
                "test_title": tc.title,
                "test_category": tc.test_category,
                "pipeline_layer": tc.pipeline_layer,
                "severity": tc.severity,
            }
            output.append(d)
        return output

    async def get_execution_summary(self, execution_id: uuid.UUID) -> dict:
        """Build summary with breakdowns by category and severity."""
        results = await self.get_execution_results(execution_id)

        by_category: dict[str, dict] = {}
        by_severity: dict[str, dict] = {}

        for r in results:
            cat = r.get("test_category", "unknown")
            sev = r.get("severity", "medium")
            res = r.get("result", "skip")

            for group, key in [(by_category, cat), (by_severity, sev)]:
                if key not in group:
                    group[key] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "skip": 0}
                group[key]["total"] += 1
                group[key][res] = group[key].get(res, 0) + 1

        execution = await self.get_execution(execution_id)
        total = execution.total_tests
        pass_rate = (execution.passed / total * 100) if total > 0 else 0

        return {
            "total_tests": total,
            "passed": execution.passed,
            "failed": execution.failed,
            "errors": execution.errors,
            "skipped": execution.skipped,
            "pass_rate": round(pass_rate, 1),
            "duration_ms": execution.duration_ms,
            "by_category": by_category,
            "by_severity": by_severity,
        }

    async def cancel_execution(self, execution_id: uuid.UUID) -> TestExecution:
        execution = await self.get_execution(execution_id)
        if execution.status in ("completed", "failed", "cancelled"):
            raise ValueError(f"Cannot cancel execution in status: {execution.status}")
        execution.status = "cancelled"
        execution.finished_at = datetime.now(timezone.utc)
        await self.db.commit()
        return execution
