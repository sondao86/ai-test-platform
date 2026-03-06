# Multi-Agent BRD → Data Pipeline Test Architecture

## Overview

Hệ thống Multi-Agent hỗ trợ end-to-end test data pipeline, tập trung vào **Business Logic / Metrics Testing**, với vòng lặp Human-in-the-Loop tại các điểm quyết định quan trọng.

---

## Flow Diagram (Swimlane)

```
👤 USER   │ ① Upload │         │ ③ Confirm  │         │ ⑤ Confirm  │ ⑦ Confirm  │         │ ⑨ Confirm  │         │         │ ⑫ Review  │
          │ BRD/BRS  │         │ + Edit Req │         │ + Edit     │ + Edit     │         │ + Edit     │         │         │ Results   │
          │ (chunk)  │         │ (per sect) │         │ Test Types │ TC Specs   │         │ Mapping    │         │         │ Scorecard │
──────────┼──────────┼─────────┼────────────┼─────────┼────────────┼────────────┼─────────┼────────────┼─────────┼─────────┼───────────┤
🤖 AGENT  │         │ ② Clarify│            │ ④ Recommend│         │ ⑥ Recommend│ ⑧ Generate│         │ ⑩ Execute│ ⑪ Root  │           │
          │         │ Req batch│            │ Categories │         │ TC Details │ Req→TC   │         │ Tests    │ Cause   │           │
          │         │ per sect │            │ + Classify │         │ best prac. │ Mapping  │         │ dbt/GX   │ Suggest │           │
──────────┼──────────┼─────────┼────────────┼─────────┼────────────┼────────────┼─────────┼────────────┼─────────┼─────────┼───────────┤
📄 STATE  │BRD Chunks│         │Clarified   │         │Test Cat.   │Test Case   │         │Req-Test    │         │Failure+ │Evidence / │
          │          │         │Req List    │         │Map         │Specs       │         │Mapping     │         │RootCause│Scorecard  │
```

---

## Phases & Steps

### Phase 1 — Ingest & Chunk
**Step ①** `USER` — Upload BRD / BRS

- Chunk document **theo cấu trúc section**, không chunk theo token
- Thứ tự chunk ưu tiên:
  1. Objective / Background
  2. Functional Requirements
  3. Business Rules & Formulas
  4. Constraints & Assumptions
- **Output artifact:** `BRD Chunks[]`

---

### Phase 2 — Requirement Clarification
**Step ②** `AGENT` — Clarify Requirements (Batch per section)

- Với mỗi BRD chunk, agent tạo **danh sách câu hỏi clarification theo nhóm** (không hỏi all-at-once)
- Tập trung vào: ambiguous metrics formula, missing threshold, undefined edge cases
- **Output:** Clarification Q&A list per section

**Step ③** `USER` — Confirm + Edit Requirements (per section)

- Review Q&A, trả lời clarification questions
- Có thể edit / bổ sung requirement trực tiếp
- **Feedback loop:** Nếu cần làm rõ thêm → quay lại ②
- **Output artifact:** `Clarified Requirement List`

---

### Phase 3 — Test Category Classification
**Step ④** `AGENT` — Recommend Testing Categories

Agent phân loại requirements vào các testing category:

| Category | Mô tả | Ví dụ |
|---|---|---|
| ⚙️ Business Logic | Metrics formula, KPI calculation | NPL Ratio, LTV, P&L |
| ✅ Data Quality | Null, unique, type, referential integrity | PK unique, not null |
| 📊 Statistical Anomaly | Drift, outlier, threshold deviation | Revenue spike > 3σ |
| 🏦 Regulatory / Compliance | Decision 2439, Basel III, BCBS 239 | Exposure limit check |
| 🔗 Cross-domain Consistency | FK, dedup, MDM alignment | Customer dedup across domains |
| 🕐 Temporal / Freshness | Date logic, SLA, period completeness | T+1 data SLA, no gap dates |

**Step ⑤** `USER` — Confirm + Edit Test Case Types

- Approve / remove / add category mapping
- **Feedback loop:** Nếu classification sai → quay lại ④ để re-classify
- **Output artifact:** `Test Category Map`

---

### Phase 4 — Test Case Generation
**Step ⑥** `AGENT` — Recommend Test Case Details (best practice)

Với mỗi confirmed category, agent generate test case specs bao gồm:

```yaml
test_case:
  id: TC-BL-001
  category: Business Logic
  priority: P0
  requirement_ref: REQ-023
  test_name: "NPL Ratio Calculation Accuracy"
  logic: "NPL_ratio = SUM(npl_balance) / SUM(gross_loan) per period"
  tool: dbt
  layer: Gold
  edge_cases:
    - Zero gross loan portfolio
    - Partial period calculation
    - Multi-currency scenario
  expected_result: "ratio between 0.0 and 1.0, non-null"
```

**Step ⑦** `USER` — Confirm + Edit Test Case Specs

- Review từng test case spec trước khi generate mapping
- Có thể thêm edge case, chỉnh expected result, đổi priority
- **Feedback loop:** Nếu specs chưa đúng → quay lại ⑥ để re-generate
- **Output artifact:** `Test Case Specs[]`

---

### Phase 5 — Requirement → Test Case Mapping
**Step ⑧** `AGENT` — Generate Requirement → Test Case Mapping

Agent tạo traceability matrix:

| Req ID | Requirement Summary | Test Case ID(s) | Category | Priority | Layer |
|---|---|---|---|---|---|
| REQ-001 | NPL Ratio formula | TC-BL-001 | Business Logic | P0 | Gold |
| REQ-002 | Customer dedup rule | TC-DQ-003, TC-XD-001 | Data Quality, Cross-domain | P1 | Silver |
| REQ-015 | T+1 data freshness | TC-TF-002 | Temporal | P1 | Bronze→Silver |

**Step ⑨** `USER` — Confirm + Edit Mapping

- Verify coverage (mỗi requirement có ít nhất 1 test case)
- Phát hiện orphan requirements (chưa có test case)
- **Feedback loop:** Nếu mapping sai → quay lại ⑧ để re-generate
- **Output artifact:** `Req-Test Mapping (Traceability Matrix)`

---

### Phase 6 — Execution
**Step ⑩** `AGENT` — Execute Tests

Execution theo tool phù hợp với category:

| Category | Tool | Trigger |
|---|---|---|
| Business Logic | dbt unit tests + dbt-expectations | dbt test |
| Data Quality | Great Expectations / Soda | GX checkpoint |
| Statistical Anomaly | dbt-expectations (moving stdev) | dbt test |
| Regulatory | Custom SQL + dbt singular tests | dbt test |
| Cross-domain | Spark / Delta Live Tables | DLT pipeline |
| Temporal | dbt source freshness | dbt source freshness |

---

### Phase 7 — Root Cause & Evidence
**Step ⑪** `AGENT` — Root Cause Suggestion (on failures)

- Với mỗi failed test case, agent phân tích và suggest:
  - Upstream source nghi vấn
  - Transformation logic lỗi tại layer nào (Bronze/Silver/Gold)
  - Loại lỗi (data issue vs logic issue vs pipeline issue)
- **Output artifact:** `Failure + Root Cause Report`

**Step ⑫** `USER` — Review Results + Evidence / Scorecard

- Review pass/fail summary theo category và domain
- Có thể trigger **re-execute** sau khi fix
- **Feedback loop:** Fix → re-execute → quay lại ⑩
- **Output artifact:** `Evidence / Scorecard`

---

## Feedback Loops Summary

| From | To | Trigger | Type |
|---|---|---|---|
| ③ Confirm Req | ② Clarify | Requirement vẫn còn unclear | 🔴 Refine |
| ⑤ Confirm Types | ④ Classify | Category classification sai | 🔴 Refine |
| ⑦ Confirm Specs | ⑥ Recommend TC | Test case spec chưa đúng | 🔴 Refine |
| ⑨ Confirm Mapping | ⑧ Generate Mapping | Mapping thiếu / sai | 🔴 Refine |
| ⑫ Review Results | ⑩ Execute | Fix xong, cần re-test | 🟢 Re-execute |

---

## Artifact State Machine

```
BRD Chunks
  └─► Clarified Requirement List
        └─► Test Category Map
              └─► Test Case Specs[]
                    └─► Req-Test Mapping (Traceability Matrix)
                          └─► Test Execution Results
                                ├─► Failure + Root Cause Report
                                └─► Evidence / Scorecard
```

---

## Tech Stack (VIB context)

| Component | Tool | Notes |
|---|---|---|
| Agent Orchestration | LangGraph | Stateful graph, audit trail cho banking |
| BRD Parsing | LLM (Claude) + chunking | Section-aware chunking |
| Business Logic Tests | dbt + dbt-expectations | YAML-based, CI/CD ready |
| Complex Validation | Great Expectations (GX Core) | Python-based, multi-source |
| Statistical Anomaly | dbt-expectations moving stdev | Seasonality-aware |
| Compliance Tests | Custom dbt singular tests (SQL) | Decision 2439 rules |
| Execution Layer | Databricks / Delta Live Tables | Bronze → Silver → Gold |
| Observability | Elementary Data / Soda | Continuous monitoring |
| CI/CD Gate | Azure DevOps | Auto-block promotion on failure |

---

## Medallion Layer → Test Mapping

```
Bronze → Silver:   ② Schema Contract  +  ✅ Data Quality  +  🕐 Freshness
Silver → Gold:     ⚙️ Business Logic  +  🏦 Regulatory   +  🔗 Cross-domain
Gold → Serving:    📊 Statistical Anomaly  +  final Evidence sign-off
```