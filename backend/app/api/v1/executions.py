"""Test execution endpoints — run tests, view results."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.execution import (
    CancelExecutionRequest,
    ExecutionListResponse,
    ExecutionSummary,
    StartExecutionRequest,
    TestExecutionDetailResponse,
    TestExecutionResponse,
    TestResultResponse,
)
from app.services.execution_service import ExecutionService

router = APIRouter()


@router.post("/{project_id}/executions", response_model=TestExecutionResponse, status_code=201)
async def start_execution(
    project_id: UUID,
    body: StartExecutionRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Start a new test execution run."""
    svc = ExecutionService(db)
    body = body or StartExecutionRequest()
    execution = await svc.start_execution(
        project_id,
        test_case_ids=body.test_case_ids,
        config=body.config,
        rerun_execution_id=body.rerun_execution_id,
        rerun_statuses=body.rerun_statuses,
    )
    return execution


@router.get("/{project_id}/executions", response_model=ExecutionListResponse)
async def list_executions(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all execution runs for a project."""
    svc = ExecutionService(db)
    executions, total = await svc.list_executions(project_id)
    return ExecutionListResponse(items=executions, total=total)


@router.get(
    "/{project_id}/executions/{execution_id}",
    response_model=TestExecutionDetailResponse,
)
async def get_execution(
    project_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get execution details with all results."""
    svc = ExecutionService(db)
    execution = await svc.get_execution(execution_id)
    results = await svc.get_execution_results(execution_id)
    summary = await svc.get_execution_summary(execution_id)

    return TestExecutionDetailResponse(
        **{
            "id": execution.id,
            "project_id": execution.project_id,
            "status": execution.status,
            "triggered_by": execution.triggered_by,
            "total_tests": execution.total_tests,
            "passed": execution.passed,
            "failed": execution.failed,
            "errors": execution.errors,
            "skipped": execution.skipped,
            "duration_ms": execution.duration_ms,
            "config": execution.config,
            "started_at": execution.started_at,
            "finished_at": execution.finished_at,
            "created_at": execution.created_at,
        },
        results=[TestResultResponse(**r) for r in results],
        summary=ExecutionSummary(**summary),
    )


@router.get(
    "/{project_id}/executions/{execution_id}/results",
    response_model=list[TestResultResponse],
)
async def get_execution_results(
    project_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all individual test results for an execution."""
    svc = ExecutionService(db)
    results = await svc.get_execution_results(execution_id)
    return [TestResultResponse(**r) for r in results]


@router.get(
    "/{project_id}/executions/{execution_id}/summary",
    response_model=ExecutionSummary,
)
async def get_execution_summary(
    project_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get execution summary with category/severity breakdowns."""
    svc = ExecutionService(db)
    summary = await svc.get_execution_summary(execution_id)
    return ExecutionSummary(**summary)


@router.post(
    "/{project_id}/executions/{execution_id}/cancel",
    response_model=TestExecutionResponse,
)
async def cancel_execution(
    project_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running execution."""
    svc = ExecutionService(db)
    execution = await svc.cancel_execution(execution_id)
    return execution


@router.post(
    "/{project_id}/executions/{execution_id}/rerun-failed",
    response_model=TestExecutionResponse,
    status_code=201,
)
async def rerun_failed(
    project_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Convenience endpoint: re-run failed/error tests from a previous execution."""
    svc = ExecutionService(db)
    execution = await svc.start_execution(
        project_id,
        rerun_execution_id=execution_id,
        rerun_statuses=["fail", "error"],
    )
    return execution
