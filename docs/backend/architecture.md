# Architecture — BRD Test Pipeline

**Tech Stack**: FastAPI · PostgreSQL · LangGraph · Claude API

---

## System Overview

The BRD Test Pipeline converts Business Requirements Documents into executable data quality test cases through a 4-phase, multi-agent pipeline with human-in-the-loop review gates.

```
BRD Upload → Phase 1 (Ingest) → Phase 2 (Clarify) → Phase 3 (Classify) → Phase 4 (Generate) → Export
```

---

## Directory Structure (Backend)

```
backend/
├── alembic/
│   └── versions/
│       ├── 001_initial.py
│       ├── 002_test_execution.py
│       ├── 003_project_update_features.py
│       ├── 004_add_wiki_sync_columns.py
│       └── 005_add_domain_and_update_enums.py
├── app/
│   ├── agents/
│   │   ├── personas.py              # 7 agent personas
│   │   └── prompts/
│   │       ├── business_agent.py     # Phase 1, 2 primary
│   │       ├── data_translator.py    # Phase 3 primary
│   │       ├── data_engineer.py      # Phase 4 primary
│   │       ├── data_architect.py     # Phase 1, 4 reviewer
│   │       ├── data_governance.py    # Phase 2, 3, 4 reviewer
│   │       ├── data_ops.py           # Phase 4 reviewer
│   │       ├── bi_analytics.py       # Phase 3, 4 reviewer
│   │       └── consolidation.py      # Consolidation prompt
│   ├── api/v1/
│   │   ├── projects.py               # Project CRUD + export endpoint
│   │   ├── phases.py                 # Phase artifact endpoints
│   │   ├── executions.py             # Test execution endpoints
│   │   └── workflow.py               # Pipeline control endpoints
│   ├── core/
│   │   ├── enums.py                  # TestCategoryEnum, PipelineLayerEnum, DomainEnum
│   │   ├── database.py               # Async SQLAlchemy setup
│   │   └── exceptions.py             # Custom exceptions
│   ├── graph/
│   │   ├── outer_graph.py            # LangGraph pipeline orchestration
│   │   ├── phase_config.py           # Phase definitions
│   │   ├── review_subgraph.py        # Multi-agent review pattern
│   │   └── state.py                  # Pipeline state TypedDict
│   ├── models/
│   │   ├── project.py
│   │   ├── brd_chunk.py
│   │   ├── requirement.py
│   │   ├── test_category_map.py      # +domain column
│   │   ├── test_case.py              # +domain column
│   │   ├── test_execution.py
│   │   └── agent_review.py
│   ├── services/
│   │   ├── project_service.py        # Project CRUD + artifact queries
│   │   ├── pipeline_service.py       # Graph execution + persistence
│   │   ├── export_service.py         # Export test cases as ZIP
│   │   ├── execution_service.py      # Test execution engine
│   │   └── wiki_sync_service.py      # Azure DevOps Wiki sync
│   └── executors/
│       ├── base.py
│       ├── dbt_executor.py
│       ├── gx_executor.py
│       └── sql_executor.py
└── docs/
```

---

## Enum Reference

### Test Categories (Operational)

| Enum Value | Description | Replaces |
|---|---|---|
| `schema_contract` | Schema validation: types, columns, enums | validity |
| `data_quality` | General DQ: NULL, unique, FK, row counts | completeness, consistency, uniqueness |
| `business_logic` | Business rule validation: ranges, calculations | accuracy |
| `metrics` | KPI/aggregation validation | *(new)* |
| `regulatory` | BCBS 239, Basel III compliance | *(new)* |
| `freshness` | SLA, latency, staleness detection | timeliness |
| `consistency` | Cross-domain consistency, MDM alignment | *(renamed)* |

### Pipeline Layers (Medallion)

| Enum Value | Description | Replaces |
|---|---|---|
| `bronze` | Raw / ingested data | staging |
| `silver` | Cleaned / transformed data | intermediate |
| `gold` | Business-ready / aggregated data | mart |

### Domains (AI-inferred)

| Enum Value | Description |
|---|---|
| `customer` | Customer data domain |
| `risk` | Risk management domain |
| `finance` | Finance domain |
| `hr` | Human resources domain |
| `wholesale_sme` | Wholesale/SME domain |
| `cross_domain` | Cross-domain tests |

---

## Structured Tag Convention

Tags follow `key:value` format for traceability:

```
["domain:risk", "layer:gold", "category:metrics", "priority:P1", "req:REQ-023"]
```

Standard keys: `domain`, `layer`, `category`, `priority`, `req`

---

## Multi-Agent Pipeline

### Phase Flow
```
Phase 1: Ingest & Chunk      → BRD → structured sections
Phase 2: Requirement Clarify  → sections → clarified requirements
Phase 3: Test Classification   → requirements → category mappings + domain
Phase 4: Test Generation       → mappings → test case specs + structured tags
```

### Review Pattern (per phase)
```
Primary Agent generates → Reviewer Agents review (parallel) → Primary consolidates → User approves/revises
```

### Agent Assignment

| Phase | Primary | Reviewers |
|-------|---------|-----------|
| 1 — Ingest | Business Agent | Data Architect |
| 2 — Clarify | Business Agent | Data Translator, Data Governance |
| 3 — Classify | Data Translator | Data Engineer, Data Governance, BI & Analytics |
| 4 — Generate | Data Engineer | Data Governance, Data Ops, BI & Analytics, Data Architect |

---

## Export Flow

```
POST /projects/{id}/test-cases/export
  │
  ├─ Query active test cases
  ├─ Group by domain
  ├─ For each test case:
  │   ├─ Resolve requirement via TestCategoryMap
  │   ├─ Build structured tags
  │   └─ Generate YAML (dbt_test_yaml | sql_logic | GX config)
  ├─ Generate _test_meta.yml per domain
  ├─ Create ZIP archive
  └─ Return FileResponse (application/zip)
```

### Export Output Structure

```
export_{project_name}_{timestamp}/
├── _shared/
│   └── README.md
├── {domain}/
│   ├── {layer}/
│   │   └── {category}/
│   │       └── {test_id}.yml
│   └── _test_meta.yml
└── _unassigned/
    └── _test_meta.yml
```

### Test YAML Format

```yaml
# Auto-generated by BRD Test Pipeline
# Requirement: REQ-023 — NPL Ratio Calculation
# Domain: risk | Layer: gold | Category: metrics

models:
  - name: gold_risk_metrics
    tests:
      - npl_ratio_check:
          config:
            severity: critical
            tags:
              - domain:risk
              - layer:gold
              - category:metrics
              - priority:P1
              - req:REQ-023
          meta:
            description: "NPL Ratio = Non-performing Loans / Total Gross Loans"
            sql_logic: "SELECT ..."
```

### _test_meta.yml Format

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

---

## Data Model (Key Tables)

```
projects
  └── brd_chunks           (Phase 1 output)
  └── requirements         (Phase 2 output)
  └── test_category_mappings  (Phase 3 output, +domain)
  └── test_cases           (Phase 4 output, +domain)
  └── test_executions
       └── test_results
  └── agent_reviews
  └── phase_history
  └── project_configs
```

### Domain Column

Added to `test_cases` and `test_category_mappings` (VARCHAR 50, nullable). AI-inferred from BRD context during Phase 3 classification. Used by export service for domain-first folder grouping.
