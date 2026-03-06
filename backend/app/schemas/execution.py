from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --- Requests ---


class StartExecutionRequest(BaseModel):
    test_case_ids: list[UUID] | None = None  # None = run all
    config: dict | None = None  # executor-specific config overrides
    rerun_execution_id: UUID | None = None  # re-run from a previous execution
    rerun_statuses: list[str] | None = None  # e.g. ["fail", "error"] — filter previous results


class CancelExecutionRequest(BaseModel):
    reason: str | None = None


# --- Responses ---


class TestResultResponse(BaseModel):
    id: UUID
    execution_id: UUID
    test_case_id: UUID
    status: str
    result: str | None  # pass | fail | error | skip
    executor_type: str
    actual_output: dict | None
    expected_output: dict | None
    error_message: str | None
    error_detail: dict | None
    rows_scanned: int | None
    rows_failed: int | None
    duration_ms: int | None
    sql_executed: str | None
    logs: list | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    # Joined from test_case
    test_id: str | None = None
    test_title: str | None = None
    test_category: str | None = None
    pipeline_layer: str | None = None
    severity: str | None = None

    model_config = {"from_attributes": True}


class ExecutionSummary(BaseModel):
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    pass_rate: float = 0.0
    duration_ms: int | None = None

    # Breakdown by category
    by_category: dict[str, dict] = Field(default_factory=dict)
    # Breakdown by severity
    by_severity: dict[str, dict] = Field(default_factory=dict)


class TestExecutionResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str  # pending | running | completed | failed | cancelled
    triggered_by: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    duration_ms: int | None
    config: dict | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TestExecutionDetailResponse(TestExecutionResponse):
    results: list[TestResultResponse] = Field(default_factory=list)
    summary: ExecutionSummary | None = None


class ExecutionListResponse(BaseModel):
    items: list[TestExecutionResponse]
    total: int
