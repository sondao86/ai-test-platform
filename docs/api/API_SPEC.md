# API Specification — BRD Test Pipeline

**Base URL**: `http://localhost:8000/api/v1`
**Content-Type**: `application/json` (trừ upload dùng `multipart/form-data`)

---

## 1. Projects

### POST /projects
Tạo project mới, có thể upload BRD file.

**Content-Type**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Tên project (1-255 chars) |
| `description` | string | No | Mô tả |
| `file` | file | No | BRD file (PDF/DOCX/MD, max 50MB) |

**Response** `201`:
```json
{
  "id": "uuid",
  "name": "My BRD Project",
  "description": "...",
  "status": "created",
  "current_phase": 0,
  "file_name": "brd.pdf",
  "brd_version": 1,
  "brd_source": "upload",
  "created_at": "2026-03-06T10:00:00Z",
  "updated_at": "2026-03-06T10:00:00Z"
}
```

**brd_source values**: `upload` (file upload, default), `wiki_sync` (synced from Azure DevOps Wiki)

### GET /projects
List tất cả projects.

**Response** `200`:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "...",
      "description": "...",
      "status": "created | in_progress | completed | archived",
      "current_phase": 0,
      "file_name": "brd.pdf",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 1
}
```

### GET /projects/{project_id}
Chi tiết 1 project.

**Response** `200`: Same as project object above.
**Response** `404`: `{"detail": "Project {id} not found"}`

### DELETE /projects/{project_id}
Archive project (soft delete — set status = "archived").

**Response** `204`: No content.

---

## 2. Phase Artifacts

### GET /projects/{project_id}/chunks
Phase 1 output — BRD chunks.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "section_title": "Executive Summary",
    "section_type": "executive_summary",
    "content": "Full text...",
    "order_index": 0,
    "metadata_": {},
    "cross_references": ["Data Requirements"],
    "created_at": "..."
  }
]
```

**section_type values**: `executive_summary`, `business_context`, `functional_requirement`, `non_functional_requirement`, `data_requirement`, `kpi_definition`, `business_rule`, `acceptance_criteria`, `dependency`, `glossary`, `appendix`, `other`

### PUT /projects/{project_id}/chunks/{chunk_id}
Edit BRD chunk.

**Body**:
```json
{
  "section_title": "Updated Title",
  "content": "Updated content...",
  "section_type": "functional_requirement"
}
```
Tất cả fields optional — chỉ gửi fields cần update.

### GET /projects/{project_id}/requirements
Phase 2 output — clarified requirements.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "chunk_id": "uuid | null",
    "requirement_id": "REQ-001",
    "title": "Customer Data Completeness",
    "description": "All customer records must have...",
    "priority": "high",
    "business_rules": ["Rule 1", "Rule 2"],
    "kpis": ["KPI-001"],
    "data_elements": ["customer_id", "customer_name"],
    "created_at": "..."
  }
]
```

### PUT /projects/{project_id}/requirements/{req_id}
Edit requirement.

**Body**:
```json
{
  "title": "...",
  "description": "...",
  "priority": "high | medium | low",
  "business_rules": ["..."],
  "kpis": ["..."]
}
```

### GET /projects/{project_id}/classifications
Phase 3 output — test category mappings.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "requirement_id": "uuid | null",
    "test_category": "schema_contract",
    "sub_category": "required_columns",
    "rationale": "Business rule requires all fields...",
    "confidence": 0.85,
    "pipeline_layer": "bronze",
    "tool_suggestion": "dbt_test",
    "domain": "customer",
    "created_at": "..."
  }
]
```

**test_category values**: `schema_contract`, `data_quality`, `business_logic`, `metrics`, `regulatory`, `freshness`, `consistency`
**pipeline_layer values**: `bronze`, `silver`, `gold`
**tool_suggestion values**: `dbt_test`, `great_expectations`, `custom_sql`, `dbt_macro`
**domain values** (suggested, AI-inferred): `customer`, `risk`, `finance`, `hr`, `wholesale_sme`, `cross_domain`

### PUT /projects/{project_id}/classifications/{map_id}
Override test category mapping.

**Body**:
```json
{
  "test_category": "business_logic",
  "sub_category": "range_check",
  "rationale": "...",
  "pipeline_layer": "gold",
  "tool_suggestion": "great_expectations",
  "domain": "risk"
}
```

### GET /projects/{project_id}/test-cases
Phase 4 output — test cases.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "category_map_id": "uuid | null",
    "test_id": "TC-SC-001",
    "title": "Verify required customer fields",
    "description": "Checks that all mandatory fields...",
    "test_category": "schema_contract",
    "pipeline_layer": "bronze",
    "tool": "dbt_test",
    "sql_logic": "SELECT count(*) FROM customers WHERE name IS NULL",
    "dbt_test_yaml": "version: 2\nmodels:\n  - name: bronze_customers\n    columns:\n      - name: customer_id\n        tests:\n          - not_null",
    "great_expectations_config": null,
    "input_data": {"table": "customers", "sample_size": 100},
    "expected_result": {"null_count": 0},
    "severity": "critical",
    "priority": 1,
    "sla_seconds": 30,
    "tags": ["domain:customer", "layer:bronze", "category:schema_contract", "priority:P1", "req:REQ-001"],
    "is_active": true,
    "source": "pipeline",
    "domain": "customer",
    "created_at": "...",
    "updated_at": "..."
  }
]
```

### PUT /projects/{project_id}/test-cases/{tc_id}
Edit test case.

**Body**:
```json
{
  "title": "...",
  "description": "...",
  "test_category": "...",
  "pipeline_layer": "...",
  "tool": "...",
  "sql_logic": "...",
  "dbt_test_yaml": "...",
  "great_expectations_config": {},
  "input_data": {},
  "expected_result": {},
  "severity": "critical | high | medium | low",
  "priority": 1,
  "sla_seconds": 30,
  "tags": ["..."],
  "is_active": true
}
```

---

## 3. Phase Results & Agent Reviews

### GET /projects/{project_id}/phases/{phase_id}
Kết quả phase: consolidated output + reviews + changelog.

**phase_id**: `1` | `2` | `3` | `4`

**Response** `200`:
```json
{
  "phase_id": 1,
  "phase_name": "Ingest & Chunk",
  "status": "completed | pending | in_progress | awaiting_user",
  "primary_agent": "business_agent",
  "reviewer_agents": ["data_architect_agent"],
  "consolidated_output": { "...phase-specific output..." },
  "reviews": [
    {
      "id": "uuid",
      "phase_id": 1,
      "agent_id": "data_architect_agent",
      "agent_name": "Data Architect Agent",
      "role": "reviewer",
      "status": "approved | changes_requested | additions_suggested",
      "confidence": 0.85,
      "comments": [
        {
          "target_id": "section-ref or null",
          "severity": "critical | suggestion | info",
          "comment": "Missing cross-reference to...",
          "proposed_change": "Add reference to..."
        }
      ],
      "additions": [],
      "consolidation_summary": null,
      "revision_round": 1,
      "created_at": "..."
    }
  ],
  "changelog": {
    "accepted": [
      {"from_agent": "data_architect_agent", "comment_summary": "...", "action_taken": "..."}
    ],
    "rejected_with_reason": [
      {"from_agent": "...", "comment_summary": "...", "rejection_reason": "..."}
    ],
    "additions_merged": [
      {"from_agent": "...", "description": "..."}
    ],
    "conflicts_for_user": [
      {"agents": ["agent_1", "agent_2"], "description": "...", "options": ["A", "B"], "conflict_flag": true}
    ]
  },
  "revision_round": 1
}
```

### GET /projects/{project_id}/phases/{phase_id}/reviews
Tất cả agent reviews cho 1 phase.

**Response** `200`: Array of `AgentReview` objects (same format as trong `reviews` array ở trên).

---

## 4. Pipeline Workflow

### POST /projects/{project_id}/pipeline/start
Bắt đầu pipeline. Project phải có file đã upload.

**Body**: `{}` (empty hoặc null)

**Response** `200`:
```json
{
  "project_id": "uuid",
  "status": "awaiting_user",
  "current_phase": 1,
  "message": "Pipeline started. Review phase output and approve or revise."
}
```

**Error** `409`: `{"detail": "Pipeline already running for project {id}"}`

### POST /projects/{project_id}/pipeline/decide
User approve hoặc request revision cho phase hiện tại.

**Body**:
```json
{
  "decision": "approved | revision_requested",
  "feedback": "Optional feedback text khi revision_requested"
}
```

**Response** `200`:
```json
{
  "project_id": "uuid",
  "status": "awaiting_user | completed",
  "current_phase": 2,
  "message": "Decision processed."
}
```

### GET /projects/{project_id}/pipeline/status
Trạng thái pipeline hiện tại.

**Response** `200`:
```json
{
  "project_id": "uuid",
  "current_phase": 1,
  "current_step": "primary_generate | reviewing | consolidating | awaiting_user | idle",
  "phase_name": "Ingest & Chunk",
  "status": "running | awaiting_user | completed | error | created"
}
```

---

## 5. Workflow History & Rollback

### GET /projects/{project_id}/workflow/history
Full audit log.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "phase_id": 1,
    "phase_name": "Ingest & Chunk",
    "action": "pipeline_started | user_approved | user_revision_requested | rollback_to_phase_1",
    "user_decision": "approved | revision_requested | null",
    "user_feedback": "text | null",
    "revision_round": 1,
    "snapshot": null,
    "created_at": "..."
  }
]
```

### POST /projects/{project_id}/workflow/rollback
Rollback về phase trước.

**Body**:
```json
{
  "target_phase": 2
}
```

**Response** `200`:
```json
{
  "project_id": "uuid",
  "rolled_back_to": 2,
  "message": "Rolled back to phase 2. Restart the pipeline to continue."
}
```

---

## 6. Test Execution

### POST /projects/{project_id}/executions
Tạo và chạy test execution run. Chạy tất cả test cases hoặc chỉ subset.

**Body** (optional):
```json
{
  "test_case_ids": ["uuid", "uuid"],
  "config": {
    "dry_run": true,
    "db_url": "postgresql://...",
    "dbt_project_dir": "/path/to/dbt",
    "gx_context_dir": "/path/to/gx"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_case_ids` | uuid[] | No | Chỉ run các test case này. `null` = run tất cả |
| `config` | object | No | Executor config overrides |
| `config.dry_run` | boolean | No | `true` = validate only, không thực sự execute SQL |
| `config.db_url` | string | No | Target DB connection string cho SQL tests |
| `config.dbt_project_dir` | string | No | Path to dbt project (cho dbt executor) |
| `config.gx_context_dir` | string | No | Path to Great Expectations context (cho GX executor) |

**Response** `201`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "running",
  "triggered_by": "user",
  "total_tests": 15,
  "passed": 0,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "duration_ms": null,
  "config": {"dry_run": true},
  "started_at": "2026-03-06T12:00:00Z",
  "finished_at": null,
  "created_at": "2026-03-06T12:00:00Z"
}
```

**Error** `400`: `{"detail": "No test cases found to execute"}`

---

### GET /projects/{project_id}/executions
List tất cả execution runs cho project, mới nhất trước.

**Response** `200`:
```json
{
  "items": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "status": "completed | running | pending | failed | cancelled",
      "triggered_by": "user",
      "total_tests": 15,
      "passed": 12,
      "failed": 2,
      "errors": 0,
      "skipped": 1,
      "duration_ms": 4523,
      "config": {},
      "started_at": "2026-03-06T12:00:00Z",
      "finished_at": "2026-03-06T12:00:04Z",
      "created_at": "2026-03-06T12:00:00Z"
    }
  ],
  "total": 5
}
```

---

### GET /projects/{project_id}/executions/{execution_id}
Chi tiết execution kèm tất cả test results + summary.

**Response** `200`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "completed",
  "triggered_by": "user",
  "total_tests": 15,
  "passed": 12,
  "failed": 2,
  "errors": 0,
  "skipped": 1,
  "duration_ms": 4523,
  "config": {},
  "started_at": "2026-03-06T12:00:00Z",
  "finished_at": "2026-03-06T12:00:04Z",
  "created_at": "2026-03-06T12:00:00Z",
  "results": [
    {
      "id": "uuid",
      "execution_id": "uuid",
      "test_case_id": "uuid",
      "status": "completed",
      "result": "pass | fail | error | skip",
      "executor_type": "custom_sql | dbt_test | great_expectations | dbt_macro",
      "actual_output": {"row_count": 0},
      "expected_output": {"row_count": 0},
      "error_message": null,
      "error_detail": null,
      "rows_scanned": 10000,
      "rows_failed": 0,
      "duration_ms": 320,
      "sql_executed": "SELECT count(*) FROM customers WHERE name IS NULL",
      "logs": ["EXECUTE: Running SQL...", "RESULT: 0 rows returned → PASS"],
      "started_at": "2026-03-06T12:00:01Z",
      "finished_at": "2026-03-06T12:00:01Z",
      "created_at": "2026-03-06T12:00:00Z",
      "test_id": "TC-SC-001",
      "test_title": "Verify required customer fields",
      "test_category": "schema_contract",
      "pipeline_layer": "bronze",
      "severity": "critical"
    }
  ],
  "summary": {
    "total_tests": 15,
    "passed": 12,
    "failed": 2,
    "errors": 0,
    "skipped": 1,
    "pass_rate": 80.0,
    "duration_ms": 4523,
    "by_category": {
      "schema_contract": {"total": 3, "pass": 3, "fail": 0, "error": 0, "skip": 0},
      "data_quality": {"total": 4, "pass": 3, "fail": 1, "error": 0, "skip": 0},
      "business_logic": {"total": 3, "pass": 2, "fail": 1, "error": 0, "skip": 0},
      "metrics": {"total": 2, "pass": 2, "fail": 0, "error": 0, "skip": 0},
      "freshness": {"total": 2, "pass": 1, "fail": 0, "error": 0, "skip": 1},
      "consistency": {"total": 1, "pass": 1, "fail": 0, "error": 0, "skip": 0}
    },
    "by_severity": {
      "critical": {"total": 6, "pass": 5, "fail": 1, "error": 0, "skip": 0},
      "high": {"total": 5, "pass": 4, "fail": 1, "error": 0, "skip": 0},
      "medium": {"total": 3, "pass": 2, "fail": 0, "error": 0, "skip": 1},
      "low": {"total": 1, "pass": 1, "fail": 0, "error": 0, "skip": 0}
    }
  }
}
```

**Error** `404`: `{"detail": "Execution {id} not found"}`

---

### GET /projects/{project_id}/executions/{execution_id}/results
Chỉ lấy array test results (không kèm summary). Format giống `results` array trong detail endpoint.

**Response** `200`: Array of `TestResult` objects (same format as above).

---

### GET /projects/{project_id}/executions/{execution_id}/summary
Chỉ lấy summary statistics + breakdowns.

**Response** `200`:
```json
{
  "total_tests": 15,
  "passed": 12,
  "failed": 2,
  "errors": 0,
  "skipped": 1,
  "pass_rate": 80.0,
  "duration_ms": 4523,
  "by_category": { "...same as above..." },
  "by_severity": { "...same as above..." }
}
```

---

### POST /projects/{project_id}/executions/{execution_id}/cancel
Huỷ execution đang chạy.

**Body**: `{}` (empty hoặc không cần body)

**Response** `200`: `TestExecution` object with `status: "cancelled"`.

**Error** `400`: `{"detail": "Cannot cancel execution in status: completed"}`

---

## 7. Project Update APIs

### POST /projects/{project_id}/brd
Re-upload BRD file cho project đã tồn tại. Tăng `brd_version`, tuỳ chọn xoá artifacts cũ.

**Content-Type**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | BRD file mới (PDF/DOCX/MD, max 50MB) |
| `discard_artifacts` | boolean | No | `true` (default) = xoá tất cả pipeline artifacts, giữ manual test cases |

**Response** `200`:
```json
{
  "project_id": "uuid",
  "brd_version": 2,
  "file_name": "brd_v2.pdf",
  "artifacts_discarded": true,
  "message": "BRD re-uploaded (version 2). Pipeline artifacts discarded."
}
```

**Error** `409`: `{"detail": "Pipeline already running for project {id}"}`

---

### POST /projects/{project_id}/brd/sync-wiki
Sync BRD content from Azure DevOps Wiki. Requires wiki config (azure_wiki_org, azure_wiki_project, azure_wiki_pat) in project config.

**Content-Type**: `application/json`

**Body**:
```json
{
  "page_path": "Requirements/My-BRD-Page",
  "discard_artifacts": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `page_path` | string | No | Path to specific wiki page. `null` = sync all pages |
| `discard_artifacts` | boolean | No | `true` (default) = xoá pipeline artifacts, giữ manual test cases |

**Response** `200`:
```json
{
  "project_id": "uuid",
  "brd_version": 3,
  "brd_source": "wiki_sync",
  "page_path": "Requirements/My-BRD-Page",
  "content_length": 12345,
  "artifacts_discarded": true,
  "message": "Wiki synced (version 3). Pipeline artifacts discarded."
}
```

**Error** `400`: `{"detail": "Wiki configuration incomplete for project {id}. Required: azure_wiki_org, azure_wiki_project, azure_wiki_pat in PUT /projects/{id}/config."}`
**Error** `409`: `{"detail": "Pipeline already running for project {id}"}`
**Error** `502`: `{"detail": "Wiki sync failed for project {id}: Git clone failed: ..."}`

**Notes**:
- Wiki content >10MB sẽ bị truncate
- Git clone timeout: 120s
- Azure Wiki dùng hyphen cho spaces trong filename (e.g. "My Page" → "My-Page.md")
- PAT scrubbed from all error messages

---

### POST /projects/{project_id}/test-cases
Tạo test case thủ công (source = "manual").

**Body**:
```json
{
  "test_id": "TC-MANUAL-001",
  "title": "Custom validation check",
  "description": "Manually defined test case...",
  "test_category": "business_logic",
  "pipeline_layer": "gold",
  "tool": "custom_sql",
  "sql_logic": "SELECT count(*) FROM orders WHERE amount < 0",
  "severity": "high",
  "priority": 2,
  "tags": ["domain:finance", "layer:gold", "category:business_logic", "priority:P2"],
  "domain": "finance"
}
```

**Response** `201`: `TestCase` object with `source: "manual"`.

---

### POST /projects/{project_id}/test-cases/{tc_id}/deactivate
Tắt test case — excluded from future executions. Historical results giữ nguyên.

**Response** `200`: `TestCase` object with `is_active: false`.

### POST /projects/{project_id}/test-cases/{tc_id}/activate
Bật lại test case đã deactivate.

**Response** `200`: `TestCase` object with `is_active: true`.

---

### GET /projects/{project_id}/test-cases?active_only=true
Modified: thêm query param `active_only` (boolean, default `false`).

Khi `active_only=true`, chỉ trả về test cases có `is_active = true`.

---

### POST /projects/{project_id}/test-cases/export
Export test cases as a hybrid domain-first folder structure ZIP file.

**Body** (optional):
```json
{
  "output_dir": "/path/to/output"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `output_dir` | string | No | Custom output directory. Default: system temp dir |

**Response** `200`: ZIP file download (`application/zip`)

Response headers:
| Header | Description |
|--------|-------------|
| `X-Export-Project-Id` | Project UUID |
| `X-Export-Total-Tests` | Number of test cases exported |
| `X-Export-Domains` | Comma-separated list of domains |

**ZIP Structure**:
```
export_{project_name}_{timestamp}/
├── _shared/
│   └── README.md
├── customer/
│   ├── bronze/schema_contract/TC-SC-001.yml
│   ├── silver/data_quality/TC-DQ-001.yml
│   ├── gold/metrics/TC-MET-001.yml
│   └── _test_meta.yml
├── risk/
│   ├── gold/business_logic/TC-BL-001.yml
│   ├── gold/regulatory/TC-REG-001.yml
│   └── _test_meta.yml
└── _unassigned/
    └── _test_meta.yml
```

**Test YAML format** (per file):
```yaml
# Auto-generated by BRD Test Pipeline
# Requirement: REQ-023 — NPL Ratio Calculation
# Domain: risk | Layer: gold | Category: metrics

models:
  - name: gold_risk_metrics
    tests:
      - custom_npl_ratio_check:
          config:
            severity: critical
            tags:
              - domain:risk
              - layer:gold
              - category:metrics
              - priority:P1
              - req:REQ-023
          meta:
            description: "NPL Ratio check"
            sql_logic: "SELECT ..."
```

**_test_meta.yml format** (per domain):
```yaml
domain: risk
tests:
  - test_file: gold/metrics/TC-MET-002.yml
    test_id: TC-MET-002
    req_id: REQ-023
    category: metrics
    priority: 1
    severity: critical
    description: "NPL Ratio check"
```

**Edge cases**:
- No domain → grouped under `_unassigned/`
- No active test cases → ZIP contains only README
- `dbt_test_yaml` present → used as-is with injected tags
- Only `sql_logic` → wrapped in dbt-compatible YAML
- Only `great_expectations_config` → exported as GX suite YAML

---

### PUT /projects/{project_id}/test-cases/{tc_id}
Modified: thêm editable fields.

**Body** (tất cả optional):
```json
{
  "title": "...",
  "description": "...",
  "test_category": "...",
  "pipeline_layer": "...",
  "tool": "...",
  "sql_logic": "...",
  "dbt_test_yaml": "...",
  "great_expectations_config": {},
  "input_data": {},
  "expected_result": {},
  "severity": "...",
  "priority": 1,
  "sla_seconds": 30,
  "tags": ["..."],
  "is_active": true
}
```

---

### GET /projects/{project_id}/config
Lấy saved environment config cho project.

**Response** `200`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "db_url": "postgresql://...",
  "dbt_project_dir": "/path/to/dbt",
  "gx_context_dir": "/path/to/gx",
  "extra": {"custom_key": "value"},
  "azure_wiki_org": "my-org",
  "azure_wiki_project": "my-project",
  "azure_wiki_name": "my-project.wiki",
  "has_azure_wiki_pat": true,
  "created_at": "...",
  "updated_at": "..."
}
```

**Note**: `azure_wiki_pat` is **never returned** in responses. Use `has_azure_wiki_pat` (bool) to check if PAT is configured.

**Response** `200`: `null` nếu chưa có config.

### PUT /projects/{project_id}/config
Lưu hoặc update environment config. Upsert — tự tạo mới nếu chưa có.

**Body**:
```json
{
  "db_url": "postgresql://...",
  "dbt_project_dir": "/path/to/dbt",
  "gx_context_dir": "/path/to/gx",
  "extra": {"custom_key": "value"},
  "azure_wiki_org": "my-org",
  "azure_wiki_project": "my-project",
  "azure_wiki_name": "my-project.wiki",
  "azure_wiki_pat": "your-personal-access-token"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `db_url` | string | No | Target DB connection string |
| `dbt_project_dir` | string | No | Path to dbt project |
| `gx_context_dir` | string | No | Path to Great Expectations context |
| `extra` | object | No | Custom key-value pairs |
| `azure_wiki_org` | string | No | Azure DevOps organization name |
| `azure_wiki_project` | string | No | Azure DevOps project name |
| `azure_wiki_name` | string | No | Wiki name (default: `{project}.wiki`) |
| `azure_wiki_pat` | string | No | Personal Access Token (write-only, never returned) |

**Response** `200`: `ProjectConfig` object (PAT excluded).

---

### POST /projects/{project_id}/executions (Modified)
Thêm fields cho re-run support.

**Body** (optional):
```json
{
  "test_case_ids": ["uuid"],
  "config": {"db_url": "..."},
  "rerun_execution_id": "uuid",
  "rerun_statuses": ["fail", "error"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rerun_execution_id` | uuid | No | Previous execution ID để lấy failed test cases |
| `rerun_statuses` | string[] | No | Filter results theo status. Default: `["fail", "error"]` |

**Config merge logic**: Saved project config (base) → request config (override). Request wins.

**Active filter**: Luôn filter `is_active = true`, kể cả khi rerun.

---

### POST /projects/{project_id}/executions/{execution_id}/rerun-failed
Convenience endpoint: re-run tất cả failed/error tests từ execution trước.

**Body**: None required.

**Response** `201`: New `TestExecution` object with `triggered_by: "rerun"`.

**Error** `400`: `{"detail": "No active test cases to re-run from execution {id}"}`

---

## 8. Enum Reference

### Test Category (Operational)
| Value | Description |
|-------|-------------|
| `schema_contract` | Schema validation: data types, required columns, enum checks |
| `data_quality` | General DQ: NOT NULL, uniqueness, row counts, referential integrity |
| `business_logic` | Business rule validation: range checks, calculation correctness |
| `metrics` | KPI/aggregation validation: metric calculations, thresholds |
| `regulatory` | Compliance: BCBS 239, Basel III, audit trail completeness |
| `freshness` | Timeliness: SLA compliance, data arrival latency |
| `consistency` | Cross-domain consistency: data agrees across domain boundaries |

### Pipeline Layer (Medallion)
| Value | Description |
|-------|-------------|
| `bronze` | Raw/ingested data (was: staging) |
| `silver` | Cleaned/transformed data (was: intermediate) |
| `gold` | Business-ready/aggregated data (was: mart) |

### Domain
| Value | Description |
|-------|-------------|
| `customer` | Customer data domain |
| `risk` | Risk management domain |
| `finance` | Finance domain |
| `hr` | Human resources domain |
| `wholesale_sme` | Wholesale/SME domain |
| `cross_domain` | Cross-domain tests |

### Structured Tag Convention
Tags follow the format `key:value`. Standard keys:
- `domain:<domain>` — Business domain
- `layer:<layer>` — Pipeline layer
- `category:<category>` — Test category
- `priority:P<n>` — Priority (P1 = highest)
- `req:<requirement_id>` — Linked requirement ID

Example: `["domain:risk", "layer:gold", "category:metrics", "priority:P1", "req:REQ-023"]`

### Execution Status
| Value | Description |
|-------|-------------|
| `pending` | Execution created, chưa bắt đầu |
| `running` | Đang chạy tests |
| `completed` | Hoàn thành (có thể có failed tests) |
| `failed` | Execution gặp lỗi hệ thống |
| `cancelled` | User huỷ |

### Test Result
| Value | Description |
|-------|-------------|
| `pass` | Test passed (violation query trả 0 rows, hoặc expected_result match) |
| `fail` | Test failed (violation query trả >0 rows) |
| `error` | Executor crash hoặc SQL error |
| `skip` | Validation failed, không có SQL logic, hoặc executor không available |

### Executor Type
| Value | Description |
|-------|-------------|
| `custom_sql` | Chạy SQL trực tiếp qua SQLAlchemy |
| `dbt_test` | Chạy dbt test (fallback → SQL nếu ko có dbt project) |
| `great_expectations` | Chạy GX validation (fallback → SQL) |
| `dbt_macro` | Chạy dbt macro (fallback → SQL) |

### Execution Logic
- **Dry run**: `config.dry_run = true` → validate test specs only, trả `skip` cho tất cả tests
- **SQL executor**: Chạy `sql_logic`, convention: 0 rows = pass (violation queries), có thể override via `expected_result`
- **dbt executor**: Chạy `dbt test --select`, nếu ko config `dbt_project_dir` → fallback sang SQL
- **GX executor**: Chạy Great Expectations, nếu ko config → fallback sang SQL
- **Fallback chain**: dbt → SQL, GX → SQL. Luôn có SQL fallback

---

## 8. Agent Reference

| Agent ID | Name | Primary In | Reviews In |
|----------|------|-----------|------------|
| `business_agent` | Business Agent | Phase 1, 2 | — |
| `data_translator_agent` | Data Translator Agent | Phase 3 | Phase 2 |
| `data_engineer_agent` | Data Engineer Agent | Phase 4 | Phase 3 |
| `data_governance_agent` | Data Governance Agent | — | Phase 2, 3, 4 |
| `data_ops_agent` | Data Ops Agent | — | Phase 4 |
| `data_architect_agent` | Data Architect Agent | — | Phase 1, 4 |
| `bi_analytics_agent` | BI & Analytics Agent | — | Phase 3, 4 |

## 9. Phase Reference

| Phase | Name | Primary Agent | Reviewers |
|-------|------|--------------|-----------|
| 1 | Ingest & Chunk | business_agent | data_architect_agent |
| 2 | Requirement Clarification | business_agent | data_translator_agent, data_governance_agent |
| 3 | Test Category Classification | data_translator_agent | data_engineer_agent, data_governance_agent, bi_analytics_agent |
| 4 | Test Case Generation | data_engineer_agent | data_governance_agent, data_ops_agent, bi_analytics_agent, data_architect_agent |

## 10. Collaborative Review Flow

Mỗi phase follow pattern:
```
Primary Agent generates → Reviewers review (parallel) → Primary consolidates → User approves/revises
```

1. `current_step = "primary_generate"` — Primary agent tạo output
2. `current_step = "reviewing"` — Reviewer agents review song song
3. `current_step = "consolidating"` — Primary agent consolidate feedback
4. `current_step = "awaiting_user"` — User review và quyết định
5. Nếu `revision_requested` → quay lại step 1 với feedback

## 11. Error Responses

| Status | Meaning |
|--------|---------|
| `400` | Bad request / Invalid phase transition / Wiki config missing |
| `404` | Project / Test case not found |
| `409` | Pipeline already running |
| `413` | File too large (>50MB) |
| `422` | Document parse error / Validation error |
| `502` | Wiki sync failed (clone error, page not found, empty wiki) |
