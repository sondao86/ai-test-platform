from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    current_phase: int
    file_name: str | None
    brd_version: int = 1
    brd_source: str | None = "upload"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int


class BrdChunkResponse(BaseModel):
    id: UUID
    section_title: str
    section_type: str
    content: str
    order_index: int
    metadata_: dict | None = Field(None, alias="metadata_")
    cross_references: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BrdChunkUpdate(BaseModel):
    section_title: str | None = None
    content: str | None = None
    section_type: str | None = None


class ClarificationResponse(BaseModel):
    id: UUID
    chunk_id: UUID | None
    question: str
    category: str
    severity: str
    answer: str | None
    context: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RequirementResponse(BaseModel):
    id: UUID
    chunk_id: UUID | None
    requirement_id: str
    title: str
    description: str
    priority: str
    business_rules: list | None
    kpis: list | None
    data_elements: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RequirementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    business_rules: list | None = None
    kpis: list | None = None


class TestCategoryMapResponse(BaseModel):
    id: UUID
    requirement_id: UUID | None
    test_category: str
    sub_category: str | None
    rationale: str
    confidence: float
    pipeline_layer: str | None
    tool_suggestion: str | None
    domain: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TestCategoryMapUpdate(BaseModel):
    test_category: str | None = None
    sub_category: str | None = None
    rationale: str | None = None
    pipeline_layer: str | None = None
    tool_suggestion: str | None = None
    domain: str | None = None


class TestCaseResponse(BaseModel):
    id: UUID
    category_map_id: UUID | None
    test_id: str
    title: str
    description: str
    test_category: str
    pipeline_layer: str
    tool: str
    sql_logic: str | None
    dbt_test_yaml: str | None
    great_expectations_config: dict | None
    input_data: dict | None
    expected_result: dict | None
    severity: str
    priority: int
    sla_seconds: int | None
    tags: list | None
    is_active: bool = True
    source: str = "pipeline"
    domain: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TestCaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    test_category: str | None = None
    pipeline_layer: str | None = None
    tool: str | None = None
    sql_logic: str | None = None
    dbt_test_yaml: str | None = None
    great_expectations_config: dict | None = None
    input_data: dict | None = None
    expected_result: dict | None = None
    severity: str | None = None
    priority: int | None = None
    sla_seconds: int | None = None
    tags: list | None = None
    is_active: bool | None = None
    domain: str | None = None


class TestCaseCreate(BaseModel):
    test_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    test_category: str = Field(..., min_length=1, max_length=50)
    pipeline_layer: str = Field(..., min_length=1, max_length=50)
    tool: str = Field(..., min_length=1, max_length=100)
    sql_logic: str | None = None
    dbt_test_yaml: str | None = None
    great_expectations_config: dict | None = None
    input_data: dict | None = None
    expected_result: dict | None = None
    severity: str = "medium"
    priority: int = 3
    sla_seconds: int | None = None
    tags: list | None = None
    domain: str | None = None


class BrdReuploadResponse(BaseModel):
    project_id: UUID
    brd_version: int
    file_name: str | None
    artifacts_discarded: bool
    message: str


class ExportRequest(BaseModel):
    output_dir: str | None = None


class ExportResponse(BaseModel):
    project_id: UUID
    total_tests: int
    domains: list[str]
    export_path: str
    message: str


class WikiSyncRequest(BaseModel):
    page_path: str | None = None
    discard_artifacts: bool = True


class WikiSyncResponse(BaseModel):
    project_id: UUID
    brd_version: int
    brd_source: str
    page_path: str | None
    content_length: int
    artifacts_discarded: bool
    message: str
