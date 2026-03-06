# Data Model Reference

> BRD Pipeline — PostgreSQL Schema Documentation
>
> **Engine:** Async SQLAlchemy 2.x + asyncpg
> **Database:** PostgreSQL 15+
> **Primary Keys:** UUID v4
> **Flexible Fields:** JSONB for metadata, configs, lists
> **Migrations:** Alembic (5 revisions)

---

## Overview

The BRD Pipeline database contains **12 tables** organized into four logical groups:

| Group | Tables | Purpose |
|-------|--------|---------|
| **Core** | `projects`, `project_configs` | Project root and per-project configuration |
| **Document Processing** | `brd_chunks`, `clarifications`, `requirements` | Pipeline phases 1–2 outputs |
| **Test Pipeline** | `test_category_mappings`, `test_cases` | Pipeline phases 3–4 outputs |
| **Execution** | `test_executions`, `test_results` | Test run tracking |
| **Audit** | `agent_reviews`, `phase_history` | Multi-agent review and phase transitions |
| **Internal** | `alembic_version` | Migration tracking |

---

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          BRD Pipeline Schema                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐ 1:1  ┌─────────────────┐                               │
│  │  projects    │─────▶│ project_configs  │                               │
│  └──────┬──────┘      └─────────────────┘                               │
│         │                                                                │
│    1:N  │  ┌──────────────────────────────────────────────┐              │
│         │  │                                              │              │
│         ▼  ▼                                              │              │
│  ┌─────────────┐ 1:N  ┌────────────────┐                 │              │
│  │ brd_chunks   │◀─ ─ ┤ clarifications  │                 │              │
│  └──────┬──────┘      └────────────────┘                 │              │
│         │                                                 │              │
│         │ N:1 (optional)                                  │              │
│         ▼                                                 │              │
│  ┌──────────────┐                                         │              │
│  │ requirements  │                                        │              │
│  └──────┬───────┘                                         │              │
│         │                                                 │              │
│         │ N:1 (optional)                                  │              │
│         ▼                                                 │              │
│  ┌────────────────────────┐                               │              │
│  │ test_category_mappings  │                              │              │
│  └──────────┬─────────────┘                               │              │
│             │                                             │              │
│             │ N:1 (optional)                              │              │
│             ▼                                             │              │
│  ┌─────────────┐                                          │              │
│  │ test_cases   │◀────────────────────────┐               │              │
│  └─────────────┘                          │               │              │
│                                           │               │              │
│  ┌──────────────────┐ 1:N ┌──────────────┤               │              │
│  │ test_executions   │───▶│ test_results  │               │              │
│  └──────────────────┘     └──────────────┘               │              │
│                                                           │              │
│  ┌────────────────┐   ┌────────────────┐                  │              │
│  │ agent_reviews   │   │ phase_history   │◀───────────────┘              │
│  └────────────────┘   └────────────────┘                                │
│                                                                          │
│  Legend: ──▶ FK (CASCADE)   ─ ─▶ FK (SET NULL)   1:N / 1:1 cardinality  │
└──────────────────────────────────────────────────────────────────────────┘
```

All child tables reference `projects.id` with `ON DELETE CASCADE`.
Optional FK references (chunk_id, requirement_id, category_map_id) use `ON DELETE SET NULL`.

---

## Table Reference

### 1. `projects`

> Root entity. One project = one BRD analysis pipeline run.

**Model:** `app/models/project.py` → `Project`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `name` | VARCHAR(255) | NO | — | |
| `description` | TEXT | YES | — | |
| `status` | VARCHAR(30) | NO | `"created"` | |
| `current_phase` | INTEGER | NO | `0` | |
| `file_path` | VARCHAR(500) | YES | — | |
| `file_name` | VARCHAR(255) | YES | — | |
| `raw_text` | TEXT | YES | — | |
| `brd_version` | INTEGER | NO | `1` | server_default |
| `brd_source` | VARCHAR(30) | YES | `"upload"` | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |
| `updated_at` | TIMESTAMPTZ | NO | `now()` | server_default, onupdate |

**Foreign Keys:** None (root table)
**Indexes:** None
**Relationships:** 1:N to all child tables, 1:1 to `project_configs`

---

### 2. `project_configs`

> Per-project configuration: DB connection, dbt paths, Azure Wiki integration.

**Model:** `app/models/project_config.py` → `ProjectConfig`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK**, UNIQUE |
| `db_url` | VARCHAR(1000) | YES | — | |
| `dbt_project_dir` | VARCHAR(500) | YES | — | |
| `gx_context_dir` | VARCHAR(500) | YES | — | |
| `extra` | JSONB | YES | `{}` | |
| `azure_wiki_org` | VARCHAR(255) | YES | — | |
| `azure_wiki_project` | VARCHAR(255) | YES | — | |
| `azure_wiki_name` | VARCHAR(255) | YES | — | |
| `azure_wiki_pat` | VARCHAR(500) | YES | — | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |
| `updated_at` | TIMESTAMPTZ | NO | `now()` | server_default, onupdate |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE, UNIQUE (enforces 1:1)

**Indexes:** Implicit unique index on `project_id`

---

### 3. `brd_chunks`

> Phase 1 output. Chunked sections of the uploaded BRD document.

**Model:** `app/models/brd_chunk.py` → `BrdChunk`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `section_title` | VARCHAR(500) | NO | — | |
| `section_type` | VARCHAR(100) | NO | — | |
| `content` | TEXT | NO | — | |
| `order_index` | INTEGER | NO | — | |
| `metadata` | JSONB | YES | `{}` | column name mapped from `metadata_` |
| `cross_references` | JSONB | YES | `[]` | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE

**Indexes:** None

---

### 4. `clarifications`

> Phase 2 output. AI-generated clarification questions for ambiguous BRD sections.

**Model:** `app/models/clarification.py` → `Clarification`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `chunk_id` | UUID | YES | — | **FK** (optional) |
| `question` | TEXT | NO | — | |
| `category` | VARCHAR(100) | NO | — | |
| `severity` | VARCHAR(30) | NO | `"medium"` | |
| `answer` | TEXT | YES | — | |
| `context` | JSONB | YES | `{}` | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE
- `chunk_id` → `brd_chunks.id` ON DELETE SET NULL

**Indexes:** None

---

### 5. `requirements`

> Phase 2 output. Structured requirements extracted from BRD analysis.

**Model:** `app/models/requirement.py` → `Requirement`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `chunk_id` | UUID | YES | — | **FK** (optional) |
| `requirement_id` | VARCHAR(50) | NO | — | |
| `title` | VARCHAR(500) | NO | — | |
| `description` | TEXT | NO | — | |
| `priority` | VARCHAR(30) | NO | `"medium"` | |
| `business_rules` | JSONB | YES | `[]` | |
| `kpis` | JSONB | YES | `[]` | |
| `data_elements` | JSONB | YES | `[]` | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE
- `chunk_id` → `brd_chunks.id` ON DELETE SET NULL

**Indexes:** None

---

### 6. `test_category_mappings`

> Phase 3 output. Maps each requirement to test categories, layers, and domains.

**Model:** `app/models/test_category_map.py` → `TestCategoryMap`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `requirement_id` | UUID | YES | — | **FK** (optional) |
| `test_category` | VARCHAR(50) | NO | — | |
| `sub_category` | VARCHAR(100) | YES | — | |
| `rationale` | TEXT | NO | — | |
| `confidence` | FLOAT | NO | `0.0` | |
| `pipeline_layer` | VARCHAR(50) | YES | — | |
| `tool_suggestion` | VARCHAR(100) | YES | — | |
| `domain` | VARCHAR(50) | YES | — | |
| `metadata` | JSONB | YES | `{}` | column name mapped from `metadata_` |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE
- `requirement_id` → `requirements.id` ON DELETE SET NULL

**Indexes:** None

---

### 7. `test_cases`

> Phase 4 output. Generated test cases with SQL logic, dbt YAML, GX configs.

**Model:** `app/models/test_case.py` → `TestCase`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `category_map_id` | UUID | YES | — | **FK** (optional) |
| `test_id` | VARCHAR(50) | NO | — | |
| `title` | VARCHAR(500) | NO | — | |
| `description` | TEXT | NO | — | |
| `test_category` | VARCHAR(50) | NO | — | |
| `pipeline_layer` | VARCHAR(50) | NO | — | |
| `tool` | VARCHAR(100) | NO | — | |
| `sql_logic` | TEXT | YES | — | |
| `dbt_test_yaml` | TEXT | YES | — | |
| `great_expectations_config` | JSONB | YES | — | |
| `input_data` | JSONB | YES | — | |
| `expected_result` | JSONB | YES | — | |
| `severity` | VARCHAR(30) | NO | `"medium"` | |
| `priority` | INTEGER | NO | `3` | |
| `sla_seconds` | INTEGER | YES | — | |
| `tags` | JSONB | YES | `[]` | |
| `is_active` | BOOLEAN | NO | `true` | server_default |
| `domain` | VARCHAR(50) | YES | — | |
| `source` | VARCHAR(30) | NO | `"pipeline"` | server_default |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |
| `updated_at` | TIMESTAMPTZ | NO | `now()` | server_default, onupdate |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE
- `category_map_id` → `test_category_mappings.id` ON DELETE SET NULL

**Indexes:**
- `ix_test_cases_project_active` on (`project_id`, `is_active`)

---

### 8. `test_executions`

> Test run container. Groups test results for a single execution.

**Model:** `app/models/test_execution.py` → `TestExecution`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `status` | VARCHAR(30) | NO | `"pending"` | |
| `triggered_by` | VARCHAR(50) | NO | `"user"` | |
| `total_tests` | INTEGER | NO | `0` | |
| `passed` | INTEGER | NO | `0` | |
| `failed` | INTEGER | NO | `0` | |
| `errors` | INTEGER | NO | `0` | |
| `skipped` | INTEGER | NO | `0` | |
| `duration_ms` | INTEGER | YES | — | |
| `config` | JSONB | YES | `{}` | |
| `started_at` | TIMESTAMPTZ | YES | — | |
| `finished_at` | TIMESTAMPTZ | YES | — | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE

**Indexes:** None

---

### 9. `test_results`

> Individual test result within an execution. Links back to both execution and test case.

**Model:** `app/models/test_execution.py` → `TestResult`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `execution_id` | UUID | NO | — | **FK** |
| `test_case_id` | UUID | NO | — | **FK** |
| `status` | VARCHAR(20) | NO | `"pending"` | |
| `result` | VARCHAR(20) | YES | — | pass/fail/error/skip |
| `executor_type` | VARCHAR(30) | NO | — | |
| `actual_output` | JSONB | YES | — | |
| `expected_output` | JSONB | YES | — | |
| `error_message` | VARCHAR(2000) | YES | — | |
| `error_detail` | JSONB | YES | — | |
| `rows_scanned` | INTEGER | YES | — | |
| `rows_failed` | INTEGER | YES | — | |
| `duration_ms` | INTEGER | YES | — | |
| `sql_executed` | VARCHAR(5000) | YES | — | |
| `logs` | JSONB | YES | `[]` | |
| `started_at` | TIMESTAMPTZ | YES | — | |
| `finished_at` | TIMESTAMPTZ | YES | — | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `execution_id` → `test_executions.id` ON DELETE CASCADE
- `test_case_id` → `test_cases.id` ON DELETE CASCADE

**Indexes:** None

---

### 10. `agent_reviews`

> Multi-agent review records. Each phase can have primary + reviewer agents.

**Model:** `app/models/agent_review.py` → `AgentReview`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `phase_id` | INTEGER | NO | — | |
| `agent_id` | VARCHAR(50) | NO | — | |
| `agent_name` | VARCHAR(100) | NO | — | |
| `role` | VARCHAR(20) | NO | — | primary/reviewer |
| `status` | VARCHAR(30) | NO | — | |
| `confidence` | FLOAT | YES | — | |
| `comments` | JSONB | YES | `[]` | |
| `additions` | JSONB | YES | `[]` | |
| `consolidation_summary` | JSONB | YES | — | |
| `revision_round` | INTEGER | NO | `1` | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE

**Indexes:** None

---

### 11. `phase_history`

> Audit trail of every phase transition, user decision, and feedback.

**Model:** `app/models/phase_history.py` → `PhaseHistory`

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | `uuid4()` | **PK** |
| `project_id` | UUID | NO | — | **FK** |
| `phase_id` | INTEGER | NO | — | |
| `phase_name` | VARCHAR(50) | NO | — | |
| `action` | VARCHAR(50) | NO | — | |
| `user_decision` | VARCHAR(30) | YES | — | |
| `user_feedback` | VARCHAR(2000) | YES | — | |
| `revision_round` | INTEGER | NO | `1` | |
| `snapshot` | JSONB | YES | — | |
| `created_at` | TIMESTAMPTZ | NO | `now()` | server_default |

**Foreign Keys:**
- `project_id` → `projects.id` ON DELETE CASCADE

**Indexes:** None

---

### 12. `alembic_version`

> Internal Alembic migration tracking table (auto-managed).

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `version_num` | VARCHAR(32) | NO | — | **PK** |

---

## Enumerations

All enums are defined in `app/core/enums.py` as Python `StrEnum` / `IntEnum` classes.
Values are stored as plain strings/integers in the database (not PostgreSQL ENUM types).

### PhaseEnum (StrEnum)

| Value | Description |
|-------|-------------|
| `ingest` | Phase 1 — BRD upload and chunking |
| `clarify` | Phase 2 — Clarification + requirement extraction |
| `classify` | Phase 3 — Test category mapping |
| `generate` | Phase 4 — Test case generation |

### PhaseNumber (IntEnum)

| Value | Maps to |
|-------|---------|
| `1` | `ingest` |
| `2` | `clarify` |
| `3` | `classify` |
| `4` | `generate` |

### TestCategoryEnum (StrEnum)

| Value | Description |
|-------|-------------|
| `schema_contract` | Schema validation, column types, not-null |
| `data_quality` | Completeness, uniqueness, consistency |
| `business_logic` | Business rule validation, calculations |
| `metrics` | KPI and metric accuracy checks |
| `regulatory` | Compliance and regulatory requirements |
| `freshness` | Data timeliness and SLA checks |
| `consistency` | Cross-source data consistency |

### PipelineLayerEnum (StrEnum) — Medallion Architecture

| Value | Description |
|-------|-------------|
| `bronze` | Raw/staging layer |
| `silver` | Cleaned/intermediate layer |
| `gold` | Business/mart layer |

### DomainEnum (StrEnum)

| Value | Description |
|-------|-------------|
| `customer` | Customer data domain |
| `risk` | Risk management domain |
| `finance` | Financial data domain |
| `hr` | Human resources domain |
| `wholesale_sme` | Wholesale/SME banking domain |
| `cross_domain` | Spans multiple domains |

### AgentIdEnum (StrEnum)

| Value | Agent Name |
|-------|------------|
| `business_agent` | Business Analyst |
| `data_translator_agent` | Data Translator |
| `data_engineer_agent` | Data Engineer |
| `data_governance_agent` | Data Governance |
| `data_ops_agent` | Data Ops |
| `data_architect_agent` | Data Architect |
| `bi_analytics_agent` | BI & Analytics |

### AgentRoleEnum (StrEnum)

| Value | Description |
|-------|-------------|
| `primary` | Lead agent for the phase |
| `reviewer` | Reviewing agent |

### ReviewStatusEnum (StrEnum)

| Value |
|-------|
| `approved` |
| `changes_requested` |
| `additions_suggested` |

### UserDecisionEnum (StrEnum)

| Value |
|-------|
| `approved` |
| `revision_requested` |

### ProjectStatusEnum (StrEnum)

| Value |
|-------|
| `created` |
| `in_progress` |
| `completed` |
| `archived` |

### CommentSeverityEnum (StrEnum)

| Value |
|-------|
| `critical` |
| `suggestion` |
| `info` |

### ExecutionStatusEnum (StrEnum)

| Value |
|-------|
| `pending` |
| `running` |
| `completed` |
| `failed` |
| `cancelled` |

### TestResultEnum (StrEnum)

| Value |
|-------|
| `pass` |
| `fail` |
| `error` |
| `skip` |

### ExecutorTypeEnum (StrEnum)

| Value |
|-------|
| `dbt_test` |
| `great_expectations` |
| `custom_sql` |
| `dbt_macro` |

---

## Key Design Patterns

### Delete-Before-Insert

Phases 1–4 use a **delete-before-insert** strategy: when a phase re-runs (e.g., after revision), all existing rows for that project+phase are deleted, then fresh rows are inserted. This avoids stale data and simplifies conflict resolution.

### Source Tracking

`test_cases.source` distinguishes pipeline-generated tests (`"pipeline"`) from manually added tests (`"manual"`). The delete-before-insert pattern only removes `source = "pipeline"` rows, preserving manual additions.

### Active Filtering

`test_cases.is_active` allows soft-deactivation of test cases without deletion. The composite index `ix_test_cases_project_active` supports efficient queries for active tests within a project.

### Tag Conventions

Test case `tags` use a `key:value` format for structured traceability:
- `domain:customer` — Business domain
- `layer:bronze` — Pipeline layer
- `requirement:REQ-001` — Source requirement
- `category:data_quality` — Test category

### JSONB Usage

JSONB columns store variable-structure data:
- `metadata` — Arbitrary key-value pairs for extensibility
- `business_rules`, `kpis`, `data_elements` — Structured lists from requirements
- `comments`, `additions` — Agent review content
- `snapshot` — Phase state at time of transition
- `config`, `actual_output`, `expected_output` — Execution data

### Cascade Behavior

- **CASCADE** on all `project_id` FKs — deleting a project removes all children
- **SET NULL** on optional references (`chunk_id`, `requirement_id`, `category_map_id`) — parent deletion doesn't break referencing rows
- **CASCADE** on `test_results.execution_id` and `test_results.test_case_id` — results are removed with their execution or test case

---

## Schema Changelog

Human-readable history of all Alembic migrations.

### `001_initial` — Initial Schema

**Revision:** `001_initial` | **Parent:** None

Created the 8 core tables:

| Table | Description |
|-------|-------------|
| `projects` | Root project entity with status, phase tracking |
| `brd_chunks` | Chunked BRD sections with metadata and cross-references |
| `clarifications` | Clarification questions linked to chunks |
| `requirements` | Extracted requirements with business rules, KPIs |
| `test_category_mappings` | Category/layer mappings for requirements |
| `test_cases` | Generated test cases with SQL, dbt, GX configs |
| `agent_reviews` | Multi-agent review records per phase |
| `phase_history` | Phase transition audit trail |

---

### `002_test_execution` — Test Execution Tables

**Revision:** `002_test_execution` | **Parent:** `001_initial`

Added 2 tables for test execution tracking:

| Table | Description |
|-------|-------------|
| `test_executions` | Execution run container with pass/fail/error/skip counts |
| `test_results` | Individual test results with actual output, SQL, logs |

---

### `003_project_update_features` — Project Update & Config

**Revision:** `003_project_update_features` | **Parent:** `002_test_execution`

| Change | Detail |
|--------|--------|
| Added `test_cases.is_active` | Boolean, default `true` — soft-delete support |
| Added `test_cases.source` | VARCHAR(30), default `"pipeline"` — distinguishes generated vs manual |
| Added `test_cases.updated_at` | TIMESTAMPTZ — tracks last modification |
| Added index `ix_test_cases_project_active` | Composite on (`project_id`, `is_active`) |
| Added `projects.brd_version` | INTEGER, default `1` — BRD revision tracking |
| Created `project_configs` table | Per-project config: DB URL, dbt/GX paths |

---

### `004_add_wiki_sync_columns` — Azure Wiki Integration

**Revision:** `004_add_wiki_sync_columns` | **Parent:** `003_project_update_features`

| Change | Detail |
|--------|--------|
| Added `project_configs.azure_wiki_org` | VARCHAR(255) — Azure DevOps organization |
| Added `project_configs.azure_wiki_project` | VARCHAR(255) — Azure DevOps project name |
| Added `project_configs.azure_wiki_name` | VARCHAR(255) — Wiki name |
| Added `project_configs.azure_wiki_pat` | VARCHAR(500) — Personal access token |
| Added `projects.brd_source` | VARCHAR(30), default `"upload"` — upload vs wiki source |

---

### `005_add_domain_and_update_enums` — Domain & Enum Migration

**Revision:** `005_add_domain_and_update_enums` | **Parent:** `004_add_wiki_sync_columns`

| Change | Detail |
|--------|--------|
| Added `test_cases.domain` | VARCHAR(50) — AI-inferred business domain |
| Added `test_category_mappings.domain` | VARCHAR(50) — AI-inferred business domain |
| Migrated `test_category` values | `completeness`→`data_quality`, `consistency`→`data_quality`, `uniqueness`→`data_quality`, `accuracy`→`business_logic`, `timeliness`→`freshness`, `validity`→`schema_contract` |
| Migrated `pipeline_layer` values | `staging`→`bronze`, `intermediate`→`silver`, `mart`→`gold` |

Applied to both `test_cases` and `test_category_mappings` tables.
