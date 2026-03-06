# Architecture

> This file is maintained by Claude (Backend Agent). It documents the system design as features are built.

---

## System Overview

Multi-Agent BRD-to-Test Pipeline: 7 AI agents collaborate to analyze Business Requirement Documents (BRD) and generate executable data quality test cases, with human-in-the-loop at every decision point.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Next.js 15)                           │
│  React 19 · TailwindCSS 4 · React Query 5 · Axios                          │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │ REST API (JSON + multipart)
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Backend (FastAPI + async)                          │
│                                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │  API Layer   │  │ Service Layer│  │  Graph Layer   │  │ Executor Layer  │  │
│  │  (v1 routes) │→ │  (business   │→ │  (LangGraph    │  │  (dbt, GX, SQL) │  │
│  │              │  │   logic)     │  │   pipeline)    │  │                 │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  └─────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                    Model + Schema Layer (SQLAlchemy + Pydantic)       │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │ asyncpg
                                 ▼
                    ┌────────────────────────┐
                    │   PostgreSQL (JSONB)    │
                    │   12 tables + indexes   │
                    └────────────────────────┘
```

---

## Backend Layer Architecture

### 1. API Layer (`app/api/v1/`)

FastAPI routers — thin HTTP handlers that delegate to service layer.

| Router | Prefix | Responsibilities |
|--------|--------|-----------------|
| `projects.py` | `/projects` | CRUD, BRD upload/re-upload, artifact CRUD, test case management, config |
| `executions.py` | `/projects` | Start/cancel/list executions, results, summaries, re-run failed |
| `phases.py` | `/projects` | Phase results, agent reviews |
| `workflow.py` | `/projects` | Pipeline start/decide/status, rollback |

All routes are registered through `router.py` and mounted at `/api/v1`.

### 2. Service Layer (`app/services/`)

Business logic — no HTTP concerns, fully testable.

| Service | Responsibilities |
|---------|-----------------|
| `ProjectService` | Project CRUD, artifact queries/updates, test case management (create/activate/deactivate), BRD re-upload with artifact discard, project config upsert, file uploads, phase history |
| `ExecutionService` | Create executions, run tests, config merge (saved + request), re-run from previous execution, results/summary aggregation |
| `PipelineService` | LangGraph pipeline orchestration, phase transitions, user decisions, artifact persistence (delete-before-insert), rollback |
| `DocumentParser` | PDF/DOCX/Markdown parsing via dedicated parsers |
| `WikiSyncService` | Azure DevOps Wiki git clone + markdown extraction |

### 3. Graph Layer (`app/graph/`)

LangGraph-based multi-agent pipeline with 4 phases.

```
┌─────────────────────────────────────────────────────────┐
│                    Outer Graph (Pipeline)                 │
│                                                          │
│  Phase 1        Phase 2        Phase 3        Phase 4    │
│  Ingest &  ──►  Requirement ──► Test Cat. ──► Test Case  │
│  Chunk          Clarify         Classify      Generate   │
│                                                          │
│  Each phase follows:                                     │
│  ┌────────┐    ┌──────────┐    ┌────────────┐            │
│  │Primary │ ──►│Reviewers │ ──►│Consolidator│──► Human   │
│  │Generate│    │(parallel)│    │            │    Gate     │
│  └────────┘    └──────────┘    └────────────┘    │       │
│       ▲                                          │       │
│       └──────── revision_requested ──────────────┘       │
└─────────────────────────────────────────────────────────┘
```

**Nodes**: `primary.py`, `reviewer.py`, `consolidator.py`, `human_gate.py`
**Config**: `phase_config.py` maps phase_id → (primary agent, reviewer agents, phase name)
**State**: `PipelineState` TypedDict flows through the graph

### 4. Executor Layer (`app/executors/`)

Pluggable test execution engine with fallback chain.

```
TestCase.tool ──► Registry ──► Executor
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼             ▼
                SQL Executor  dbt Executor  GX Executor
                (always avail) (fallback→SQL) (fallback→SQL)
```

| Executor | Handles | Fallback |
|----------|---------|----------|
| `sql_executor.py` | `custom_sql` | — |
| `dbt_executor.py` | `dbt_test`, `dbt_macro` | SQL |
| `gx_executor.py` | `great_expectations` | SQL |

### 5. Agent Layer (`app/agents/`)

7 specialized AI agent personas, each with role-specific prompts.

| Agent | Role | Primary in | Reviews in |
|-------|------|-----------|------------|
| Business Agent | Domain expert | Phase 1, 2 | — |
| Data Translator Agent | Requirements→data | Phase 3 | Phase 2 |
| Data Engineer Agent | Test generation | Phase 4 | Phase 3 |
| Data Governance Agent | Quality standards | — | Phase 2, 3, 4 |
| Data Ops Agent | Operations | — | Phase 4 |
| Data Architect Agent | Architecture | — | Phase 1, 4 |
| BI & Analytics Agent | Analytics | — | Phase 3, 4 |

### 6. Core Layer (`app/core/`)

| Module | Purpose |
|--------|---------|
| `database.py` | Async SQLAlchemy engine + session factory |
| `enums.py` | All domain enumerations (phases, categories, statuses, etc.) |
| `exceptions.py` | HTTP exception classes (ProjectNotFound, PipelineAlreadyRunning, etc.) |
| `claude_client.py` | Claude CLI integration |

---

## Database Schema

### Entity Relationship Diagram

```
projects ─────────┬──► brd_chunks
   │               ├──► clarifications
   │               ├──► requirements ◄──── test_category_mappings
   │               ├──► test_category_mappings
   │               ├──► test_cases ────────► test_results
   │               ├──► agent_reviews
   │               ├──► phase_history
   │               ├──► test_executions ──► test_results
   │               └──► project_configs (1:1)
   │
   └─ brd_version (tracks re-uploads)
```

### Tables (12)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `projects` | id, name, status, current_phase, raw_text, file_path, **brd_version**, **brd_source** | Root entity |
| `brd_chunks` | project_id, section_title, section_type, content, order_index | Phase 1 output |
| `clarifications` | project_id, chunk_id, question, answer, category | Phase 2 Q&A |
| `requirements` | project_id, requirement_id, title, description, priority | Phase 2 output |
| `test_category_mappings` | project_id, requirement_id, test_category, confidence | Phase 3 output |
| `test_cases` | project_id, test_id, tool, sql_logic, **is_active**, **source**, **updated_at** | Phase 4 output |
| `agent_reviews` | project_id, phase_id, agent_id, role, status, comments | Agent feedback |
| `phase_history` | project_id, phase_id, action, user_decision, snapshot | Audit log |
| `test_executions` | project_id, status, triggered_by, passed/failed/errors/skipped | Execution runs |
| `test_results` | execution_id, test_case_id, result, actual_output, duration_ms | Per-test results |
| `project_configs` | project_id (unique), db_url, dbt_project_dir, gx_context_dir, extra, **azure_wiki_org/project/name/pat** | Saved env config + wiki settings |

### Migrations

| Migration | Changes |
|-----------|---------|
| `001_initial` | Core tables: projects, brd_chunks, clarifications, requirements, test_category_mappings, test_cases, agent_reviews, phase_history |
| `002_test_execution` | test_executions, test_results |
| `003_project_update_features` | +is_active/source/updated_at on test_cases, +brd_version on projects, +project_configs table, +composite index |
| `004_add_wiki_sync_columns` | +azure_wiki_org/project/name/pat on project_configs, +brd_source on projects |

---

## Key Data Flows

### Flow 1: Create Project + Pipeline (Happy Path)

```
Upload BRD ──► Parse doc ──► Create project (phase=0)
                                    │
                              Start Pipeline
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                      ▼
         Phase 1               Phase 2                Phase 3,4
         Ingest & Chunk        Clarify Req            Classify + Generate
              │                     │                      │
         persist artifacts     persist artifacts      persist artifacts
         (delete-before-insert) (delete-before-insert) (delete-before-insert)
              │                     │                      │
         Human Gate            Human Gate              Human Gate
         (approve/revise)      (approve/revise)       (approve/revise)
              │                     │                      │
              └─────────────────────┴──────────────────────┘
                                    │
                              Pipeline Complete
                              (phase=4, status=completed)
```

### Flow 2: Update Project (Re-upload BRD)

```
POST /projects/{id}/brd
    │
    ├── Guard: reject if pipeline running (409)
    ├── Parse new document
    ├── Update project: raw_text, file_path, file_name
    ├── Increment brd_version
    │
    └── if discard_artifacts=true:
          ├── Delete: BrdChunks, Clarifications, Requirements, TestCategoryMaps
          ├── Delete: TestCases WHERE source='pipeline'  (keep source='manual')
          ├── Reset: current_phase=0, status='created'
          └── Record phase_history: action='brd_reuploaded'
```

### Flow 2b: Wiki Sync (Azure DevOps Wiki → BRD)

```
PUT /projects/{id}/config  (save azure_wiki_org/project/pat)
    │
POST /projects/{id}/brd/sync-wiki
    │
    ├── Guard: reject if pipeline running (409)
    ├── Validate wiki config (org, project, pat) → 400 if missing
    ├── WikiSyncService.sync_page(page_path)
    │     ├── git clone --depth 1 (120s timeout)
    │     ├── If page_path: find specific .md file
    │     └── If page_path=None: concatenate all .md files
    ├── Update project: raw_text, brd_version++, brd_source='wiki_sync'
    │
    └── if discard_artifacts=true:
          ├── Delete pipeline artifacts (same as re-upload)
          ├── Reset: current_phase=0, status='created'
          └── Record phase_history: action='wiki_synced'
```

### Flow 3: Test Execution with Config Merge + Re-run

```
POST /projects/{id}/executions
    │
    ├── Resolve test_case_ids:
    │     if rerun_execution_id:
    │       → query previous results WHERE result IN rerun_statuses
    │       → intersect with explicit test_case_ids (if any)
    │
    ├── Filter: is_active=true ALWAYS
    │
    ├── Config merge:
    │     saved project_config (base)
    │       └── request config (override, wins)
    │
    ├── Create TestExecution (triggered_by='user' | 'rerun')
    ├── Create TestResult per test case
    ├── Execute via Executor layer
    └── Aggregate: passed/failed/errors/skipped
```

### Flow 4: Manual Test Case Lifecycle

```
Create:     POST /projects/{id}/test-cases        → source='manual', is_active=true
Edit:       PUT  /projects/{id}/test-cases/{tc_id} → updated_at auto-set
Deactivate: POST .../deactivate                    → is_active=false (excluded from executions)
Activate:   POST .../activate                      → is_active=true (re-included)
Pipeline:   Re-run pipeline                        → source='pipeline' deleted, source='manual' preserved
```

---

## Pipeline Artifact Persistence Strategy

**Problem**: Pipeline re-runs caused append-only artifact accumulation.

**Solution**: Delete-before-insert per artifact type.

| Phase | Artifacts | Delete Strategy |
|-------|-----------|-----------------|
| Phase 1 | BrdChunks | Delete all for project → insert new |
| Phase 2 | Requirements | Delete all for project → insert new |
| Phase 3 | TestCategoryMaps | Delete all for project → insert new |
| Phase 4 | TestCases | Delete WHERE `source='pipeline'` → insert new. **Manual test cases preserved.** |

---

## Project Config & Execution Config Merge

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  project_configs │ ──► │   Merge Logic     │ ──► │ ExecutionContext │
│  (saved in DB)   │     │                  │     │  db_url          │
│  db_url          │     │  saved = base    │     │  dbt_project_dir │
│  dbt_project_dir │     │  request = over- │     │  gx_context_dir  │
│  gx_context_dir  │     │  ride (wins)     │     │  dry_run         │
│  extra {}        │     │                  │     │                  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              ▲
                              │
                    ┌─────────────────┐
                    │ Request config   │
                    │ (from POST body) │
                    └─────────────────┘
```

User chỉ cần `PUT /projects/{id}/config` một lần. Mỗi lần `POST /executions` không cần truyền lại config — tự động merge từ saved config.

---

## Directory Structure

```
backend/
├── alembic/
│   └── versions/
│       ├── 001_initial.py
│       ├── 002_test_execution.py
│       ├── 003_project_update_features.py
│       └── 004_add_wiki_sync_columns.py
├── app/
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Settings (env vars + .env)
│   ├── dependencies.py             # Dependency injection
│   ├── api/v1/
│   │   ├── router.py              # Route aggregator
│   │   ├── projects.py            # 15 endpoints (CRUD + artifacts + update features + wiki sync)
│   │   ├── executions.py          # 7 endpoints (run + results + rerun-failed)
│   │   ├── phases.py              # Phase results + reviews
│   │   └── workflow.py            # Pipeline start/decide/rollback
│   ├── models/                     # SQLAlchemy ORM (11 models)
│   │   ├── project.py
│   │   ├── project_config.py      # NEW: saved env config
│   │   ├── brd_chunk.py
│   │   ├── clarification.py
│   │   ├── requirement.py
│   │   ├── test_category_map.py
│   │   ├── test_case.py           # +is_active, source, updated_at
│   │   ├── agent_review.py
│   │   ├── phase_history.py
│   │   └── test_execution.py      # TestExecution + TestResult
│   ├── schemas/                    # Pydantic validation
│   │   ├── project.py             # +TestCaseCreate, BrdReuploadResponse
│   │   ├── project_config.py      # NEW: config CRUD schemas
│   │   ├── execution.py           # +rerun_execution_id, rerun_statuses
│   │   ├── phase.py
│   │   └── common.py
│   ├── services/                   # Business logic
│   │   ├── project_service.py     # +reupload_brd, config, test case mgmt, wiki sync
│   │   ├── execution_service.py   # +rerun, config merge, active filter
│   │   ├── pipeline_service.py    # Fixed: delete-before-insert
│   │   ├── wiki_sync_service.py   # NEW: Azure DevOps Wiki git clone + read
│   │   └── document_parser.py
│   ├── executors/                  # Test execution engine
│   │   ├── base.py                # ExecutionContext, TestCaseSpec, BaseExecutor
│   │   ├── registry.py            # tool → executor mapping
│   │   ├── sql_executor.py
│   │   ├── dbt_executor.py
│   │   └── gx_executor.py
│   ├── graph/                      # LangGraph pipeline
│   │   ├── outer_graph.py         # 4-phase pipeline graph
│   │   ├── review_subgraph.py     # Review subgraph pattern
│   │   ├── phase_config.py        # Phase → agent mapping
│   │   ├── state.py               # PipelineState TypedDict
│   │   └── nodes/
│   │       ├── primary.py
│   │       ├── reviewer.py
│   │       ├── consolidator.py
│   │       └── human_gate.py
│   ├── agents/                     # AI agent prompts
│   │   ├── personas.py
│   │   └── prompts/               # 7 agent prompt files
│   ├── parsers/                    # Document parsing
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── md_parser.py           # NEW: Markdown (read as-is)
│   └── core/
│       ├── database.py
│       ├── enums.py
│       ├── exceptions.py          # +TestCaseNotFoundError, NoTestCasesForRerunError
│       └── claude_client.py
└── tests/
    ├── conftest.py
    ├── test_projects.py
    ├── test_graph_structure.py
    ├── test_personas.py
    └── test_phase_config.py
```

---

## API Endpoint Summary

### Projects (`/api/v1/projects`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/projects` | Create project + optional BRD upload |
| GET | `/projects` | List projects |
| GET | `/projects/{id}` | Get project detail |
| DELETE | `/projects/{id}` | Archive project |
| POST | `/projects/{id}/brd` | **Re-upload BRD** |
| POST | `/projects/{id}/brd/sync-wiki` | **Sync BRD from Azure Wiki** |
| GET | `/projects/{id}/chunks` | Get BRD chunks |
| PUT | `/projects/{id}/chunks/{cid}` | Edit chunk |
| GET | `/projects/{id}/requirements` | Get requirements |
| PUT | `/projects/{id}/requirements/{rid}` | Edit requirement |
| GET | `/projects/{id}/classifications` | Get classifications |
| PUT | `/projects/{id}/classifications/{mid}` | Edit classification |
| GET | `/projects/{id}/test-cases` | Get test cases (?active_only) |
| POST | `/projects/{id}/test-cases` | **Create manual test case** |
| PUT | `/projects/{id}/test-cases/{tid}` | Edit test case |
| POST | `/projects/{id}/test-cases/{tid}/deactivate` | **Deactivate test case** |
| POST | `/projects/{id}/test-cases/{tid}/activate` | **Activate test case** |
| GET | `/projects/{id}/config` | **Get saved config** |
| PUT | `/projects/{id}/config` | **Upsert config** |

### Executions (`/api/v1/projects`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/projects/{id}/executions` | Start execution (+ rerun + config merge) |
| GET | `/projects/{id}/executions` | List executions |
| GET | `/projects/{id}/executions/{eid}` | Execution detail + results |
| GET | `/projects/{id}/executions/{eid}/results` | Results only |
| GET | `/projects/{id}/executions/{eid}/summary` | Summary with breakdowns |
| POST | `/projects/{id}/executions/{eid}/cancel` | Cancel execution |
| POST | `/projects/{id}/executions/{eid}/rerun-failed` | **Re-run failed tests** |

### Phases & Workflow (`/api/v1/projects`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/phases/{pid}` | Phase result + reviews |
| GET | `/projects/{id}/phases/{pid}/reviews` | Agent reviews for phase |
| GET | `/projects/{id}/workflow/history` | Full audit log |
| POST | `/projects/{id}/pipeline/start` | Start pipeline |
| POST | `/projects/{id}/pipeline/decide` | Submit user decision |
| GET | `/projects/{id}/pipeline/status` | Pipeline status |
| POST | `/projects/{id}/workflow/rollback` | Rollback to phase |

**Total: 33 endpoints** (8 new from Project Update + Wiki Sync features, bold above)

---

## Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| API Framework | FastAPI (async) | Auto OpenAPI docs at /docs |
| ORM | SQLAlchemy 2.0 (async) | Mapped columns, asyncpg driver |
| Database | PostgreSQL | JSONB for flexible fields |
| Migrations | Alembic | 4 migration files |
| Validation | Pydantic v2 | Request/response schemas |
| Agent Orchestration | LangGraph | Stateful graph with interrupts |
| LLM | Claude (via CLI) | Prompt per agent persona |
| Document Parsing | Custom (pdf + docx + md) | pymupdf / python-docx / raw read |
| Frontend | Next.js 15 + React 19 | TailwindCSS 4, React Query 5 |

---

## Error Handling

All errors inherit from `fastapi.HTTPException`:

| Exception | Status | When |
|-----------|--------|------|
| `ProjectNotFoundError` | 404 | Project/artifact ID not found |
| `TestCaseNotFoundError` | 404 | Test case ID not found |
| `PhaseNotCompletedError` | 400 | Accessing phase not yet completed |
| `InvalidPhaseTransitionError` | 400 | Invalid phase rollback target |
| `PipelineAlreadyRunningError` | 409 | Start pipeline / re-upload BRD while running |
| `NoTestCasesForRerunError` | 400 | Re-run with no matching failed tests |
| `DocumentParseError` | 422 | PDF/DOCX/MD parsing failure |
| `FileTooLargeError` | 413 | Upload exceeds max_upload_size_mb |
| `WikiConfigMissingError` | 400 | Wiki config incomplete (missing org/project/pat) |
| `WikiSyncFailedError` | 502 | Wiki sync failed (clone error, page not found, empty) |
