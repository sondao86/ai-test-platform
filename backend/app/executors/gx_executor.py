"""Great Expectations executor — runs GX expectations against data."""

from __future__ import annotations

import json
import logging

from app.executors.base import BaseExecutor, ExecutionContext, ExecutionResult, TestCaseSpec

logger = logging.getLogger(__name__)


class GxExecutor(BaseExecutor):
    executor_type = "great_expectations"

    async def validate(self, spec: TestCaseSpec) -> list[str]:
        errors = []
        if not spec.great_expectations_config and not spec.sql_logic:
            errors.append(
                f"Test {spec.test_id}: great_expectations_config or sql_logic required"
            )
        return errors

    async def execute(
        self, spec: TestCaseSpec, ctx: ExecutionContext
    ) -> ExecutionResult:
        gx_config = spec.great_expectations_config or {}

        if ctx.dry_run:
            return ExecutionResult(
                result="pass",
                logs=[
                    "DRY RUN: GX expectation validated",
                    f"Config: {json.dumps(gx_config)[:300]}",
                ],
            )

        if not ctx.gx_context_dir:
            # Fallback to SQL if available
            if spec.sql_logic:
                from app.executors.sql_executor import SqlExecutor

                sql_exec = SqlExecutor()
                result = await sql_exec.execute(spec, ctx)
                result.logs.insert(0, "Fallback: ran as raw SQL (no GX context configured)")
                return result

            return ExecutionResult(
                result="skip",
                error_message="No Great Expectations context configured",
                logs=["SKIP: gx_context_dir not set. Configure to run GX expectations."],
            )

        logs = []
        with self._timed() as timer:
            try:
                import great_expectations as gx

                context = gx.get_context(context_root_dir=ctx.gx_context_dir)

                expectation_type = gx_config.get("expectation_type", "")
                kwargs = gx_config.get("kwargs", {})

                logs.append(f"Running GX expectation: {expectation_type}")
                logs.append(f"Kwargs: {json.dumps(kwargs)[:300]}")

                # Get datasource + batch
                datasource_name = gx_config.get("datasource", "default")
                asset_name = gx_config.get("asset", "default")

                datasource = context.get_datasource(datasource_name)
                data_asset = datasource.get_asset(asset_name)
                batch_request = data_asset.build_batch_request()

                # Create expectation suite
                suite_name = f"test_{spec.test_id}"
                suite = context.add_or_update_expectation_suite(suite_name)

                expectation = gx.expectations.ExpectationConfiguration(
                    type=expectation_type,
                    kwargs=kwargs,
                )
                suite.add_expectation(expectation)

                # Run validation
                validator = context.get_validator(
                    batch_request=batch_request,
                    expectation_suite=suite,
                )
                validation_result = validator.validate()

                success = validation_result.success
                stats = validation_result.statistics

                actual_output = {
                    "success": success,
                    "evaluated_expectations": stats.get("evaluated_expectations", 0),
                    "successful_expectations": stats.get("successful_expectations", 0),
                    "unsuccessful_expectations": stats.get("unsuccessful_expectations", 0),
                }

                logs.append(f"GX validation {'PASSED' if success else 'FAILED'}")
                logs.append(f"Stats: {json.dumps(stats)}")

                return ExecutionResult(
                    result="pass" if success else "fail",
                    actual_output=actual_output,
                    expected_output=spec.expected_result,
                    duration_ms=timer.elapsed_ms,
                    logs=logs,
                )

            except ImportError:
                logs.append("ERROR: great_expectations not installed")
                return ExecutionResult(
                    result="error",
                    error_message="great_expectations not installed. pip install great_expectations",
                    duration_ms=timer.elapsed_ms,
                    logs=logs,
                )
            except Exception as e:
                logger.exception("GX execution error for %s", spec.test_id)
                logs.append(f"ERROR: {e}")
                return ExecutionResult(
                    result="error",
                    error_message=str(e),
                    error_detail={"exception_type": type(e).__name__},
                    duration_ms=timer.elapsed_ms,
                    logs=logs,
                )
