# Frontend Improvements — Implementation Guide for Gemini

## Context

Đây là project multi-agent AI system gồm **7 AI agents** cộng tác xử lý BRD documents và sinh test cases cho data pipelines. Backend đã hoàn thiện (FastAPI + PostgreSQL + LangGraph + Claude CLI). Frontend scaffold đã có (Next.js 15 + React 19 + TailwindCSS 4 + React Query 5).

**Backend API**: Xem `docs/API_SPEC.md` cho chi tiết tất cả endpoints.
**Frontend hiện tại**: Xem `frontend/src/` — đã có basic scaffolding.

---

## Current Frontend Stack

```
frontend/
├── package.json          # Next.js 15, React 19, TailwindCSS 4, React Query 5, Axios, Lucide
├── next.config.ts        # API proxy → localhost:8000
├── tsconfig.json
├── postcss.config.mjs
├── src/
│   ├── types/api.ts      # TypeScript types cho tất cả API responses
│   ├── lib/api.ts        # Axios API client (tất cả endpoints đã có)
│   ├── lib/utils.ts      # cn(), constants (colors, phase names)
│   ├── app/
│   │   ├── layout.tsx    # Root layout + nav
│   │   ├── page.tsx      # Landing page
│   │   ├── providers.tsx # React Query provider
│   │   ├── projects/
│   │   │   ├── page.tsx                       # Project list
│   │   │   └── [id]/
│   │   │       ├── page.tsx                   # Project detail + pipeline controls
│   │   │       └── executions/                # ← NEW (IMP-11)
│   │   │           ├── page.tsx               # Execution list
│   │   │           └── [executionId]/page.tsx # Execution detail
│   │   └── globals.css
│   └── components/
│       ├── project/
│       │   ├── project-card.tsx
│       │   └── create-project-dialog.tsx
│       ├── phase/
│       │   ├── phase-timeline.tsx
│       │   ├── pipeline-controls.tsx
│       │   ├── phase-detail.tsx
│       │   └── changelog-view.tsx
│       └── agent/
│           └── agent-review-card.tsx
```

---

## Improvements cần implement

### IMP-01: Design System + UI Component Library

**Mức độ**: High Priority
**Files**: `src/components/ui/`

Tạo reusable UI components thay vì inline Tailwind classes everywhere:

```
src/components/ui/
├── button.tsx          # Primary, Secondary, Danger, Ghost variants + sizes
├── badge.tsx           # Status badges với color mapping
├── card.tsx            # Card container + CardHeader + CardContent + CardFooter
├── dialog.tsx          # Modal dialog wrapper (thay CreateProjectDialog inline)
├── input.tsx           # Text input + textarea
├── select.tsx          # Dropdown select
├── tabs.tsx            # Tab navigation (cho phase artifacts)
├── skeleton.tsx        # Loading skeleton
├── toast.tsx           # Toast notifications cho success/error
├── progress.tsx        # Progress bar (cho pipeline progress)
├── collapsible.tsx     # Expandable sections (cho agent reviews)
├── code-block.tsx      # Syntax highlighted code (cho SQL, YAML, JSON)
└── empty-state.tsx     # Empty state illustration
```

Reference style: Giữ minimal clean style hiện tại, nhưng consistent. Dùng CSS variables cho theming.

---

### IMP-02: Phase Artifact Viewers

**Mức độ**: High Priority
**Files**: `src/components/phase/artifacts/`

Mỗi phase output cần dedicated viewer thay vì chỉ `JSON.stringify`:

```
src/components/phase/artifacts/
├── chunk-viewer.tsx            # Phase 1: BRD chunks as expandable cards
├── chunk-editor.tsx            # Inline edit chunk (PUT /chunks/{id})
├── requirement-table.tsx       # Phase 2: Requirements as sortable table
├── requirement-editor.tsx      # Inline edit requirement
├── classification-matrix.tsx   # Phase 3: Matrix view (requirement × category)
├── classification-editor.tsx   # Override category mapping
├── test-case-list.tsx          # Phase 4: Test cases grouped by category
├── test-case-detail.tsx        # Single test case detail view
├── test-case-editor.tsx        # Edit test case
└── sql-preview.tsx             # SQL logic preview with syntax highlighting
```

**Chi tiết từng viewer**:

#### chunk-viewer.tsx (Phase 1)
- Hiện từng BRD section dạng accordion/expandable card
- Badge cho `section_type` (e.g., "functional_requirement" → blue, "kpi_definition" → green)
- Hiện `cross_references` dạng linked tags
- Click để expand/collapse content
- Edit button → inline editor
- API: `GET /projects/{id}/chunks`, `PUT /projects/{id}/chunks/{cid}`

#### requirement-table.tsx (Phase 2)
- Table với columns: ID, Title, Priority, Business Rules count, KPIs count
- Sort by priority, filter by search
- Click row → expand detail panel
- Priority badges: high=red, medium=yellow, low=green
- Inline edit support
- API: `GET /projects/{id}/requirements`, `PUT /projects/{id}/requirements/{rid}`

#### classification-matrix.tsx (Phase 3)
- **Matrix/heatmap view**: rows = requirements, columns = 6 test categories
- Cell = confidence score (color intensity)
- Click cell → detail panel với rationale, pipeline_layer, tool_suggestion
- Bar chart: count per category (completeness: 5, consistency: 3, ...)
- Dropdown override: user có thể đổi category
- API: `GET /projects/{id}/classifications`, `PUT /projects/{id}/classifications/{mid}`

#### test-case-list.tsx (Phase 4)
- Group by `test_category` tabs
- Mỗi test case card: test_id, title, severity badge, tool badge, pipeline_layer
- Expand → full detail với SQL logic (syntax highlighted), dbt YAML, GX config
- Filter by: severity, tool, pipeline_layer
- Export to JSON button
- API: `GET /projects/{id}/test-cases`, `PUT /projects/{id}/test-cases/{tid}`

---

### IMP-03: Agent Review Panel (Enhanced)

**Mức độ**: High Priority
**Files**: `src/components/agent/`

Nâng cấp agent review display:

```
src/components/agent/
├── agent-review-card.tsx       # ĐÃ CÓ — cần enhance
├── agent-avatar.tsx            # Agent icon/avatar theo agent_id
├── review-summary-bar.tsx      # Summary bar: "3 approved, 1 changes requested"
├── review-diff-view.tsx        # Side-by-side: original vs proposed change
├── conflict-resolver.tsx       # UI cho user resolve conflicts giữa agents
└── agent-legend.tsx            # Legend showing all 7 agents + their colors
```

**Enhancements cho agent-review-card.tsx**:
- Thêm agent avatar/icon
- Collapsible comments (mặc định show first 2, expand để xem hết)
- Severity filter: show only critical / show all
- "Accept" / "Reject" buttons cho từng comment (khi user reviewing)
- Highlight proposed_change vs original text

**review-summary-bar.tsx**:
- Horizontal bar hiện: `[✓ Data Architect: approved] [! Data Governance: changes requested] [+ BI Agent: additions suggested]`
- Click agent → scroll to their review card

**conflict-resolver.tsx**:
- Khi changelog có `conflicts_for_user`, hiện UI:
  - Mô tả conflict
  - Option A (from agent X) vs Option B (from agent Y)
  - User chọn option hoặc write custom resolution
  - Submit resolution → thêm vào feedback khi approve/revise

---

### IMP-04: Real-time Pipeline Progress

**Mức độ**: Medium Priority
**Files**: `src/components/pipeline/`

```
src/components/pipeline/
├── pipeline-progress.tsx       # Overall progress bar (Phase 1/4)
├── agent-activity-feed.tsx     # Real-time: "Business Agent is generating..."
├── step-indicator.tsx          # Current step within phase
└── execution-log.tsx           # Expandable log of all agent activities
```

**pipeline-progress.tsx**:
- Progress bar 0-100% (25% per phase)
- Animated transition khi phase changes
- Show current step: "Primary generating..." → "Reviewers reviewing..." → "Consolidating..."

**agent-activity-feed.tsx**:
- Live feed (poll mỗi 3s via `GET /pipeline/status`):
  ```
  🔵 Business Agent generating BRD chunks...
  ✅ Business Agent completed
  🔵 Data Architect reviewing...
  ✅ Data Architect: approved (confidence: 92%)
  🔵 Business Agent consolidating feedback...
  ⏳ Awaiting your review
  ```
- Mỗi entry: timestamp + agent badge + message + status icon

**step-indicator.tsx**:
- 4 steps trong mỗi phase: Generate → Review → Consolidate → User Decision
- Animated dot moving through steps

---

### IMP-05: Workflow History Timeline

**Mức độ**: Medium Priority
**Files**: `src/app/projects/[id]/history/page.tsx`, `src/components/workflow/`

```
src/components/workflow/
├── history-timeline.tsx        # Vertical timeline of all actions
├── history-entry.tsx           # Single history entry card
└── rollback-dialog.tsx         # Confirm rollback dialog
```

**Page**: `/projects/[id]/history`
**API**: `GET /projects/{id}/workflow/history`

- Vertical timeline showing mọi event:
  - Pipeline started
  - Phase 1 completed (approved)
  - Phase 2: revision requested — "Need more detail on KPI thresholds"
  - Phase 2: revision completed (approved)
  - Phase 3 completed
  - ...
- Mỗi entry: icon + timestamp + phase badge + action + user feedback (nếu có)
- Rollback button: "Rollback to Phase X" → confirm dialog → `POST /workflow/rollback`

---

### IMP-06: Dashboard / Project Overview

**Mức độ**: Medium Priority
**Files**: `src/app/projects/[id]/dashboard/`

Thêm dashboard tab cho project detail page:

```
src/components/dashboard/
├── stats-grid.tsx              # 4 stat cards (chunks, requirements, classifications, test cases count)
├── category-chart.tsx          # Pie/bar chart: test cases by category
├── severity-chart.tsx          # Test cases by severity
├── agent-participation.tsx     # Which agents reviewed which phases
├── coverage-matrix.tsx         # Requirements → test case coverage
└── export-panel.tsx            # Export test cases (JSON, CSV, dbt YAML)
```

**stats-grid.tsx**: 4 cards:
- Phase 1: X chunks parsed
- Phase 2: X requirements extracted
- Phase 3: X classifications mapped
- Phase 4: X test cases generated

**category-chart.tsx**: (dùng simple SVG hoặc recharts)
- Bar/pie chart: completeness: 12, consistency: 8, timeliness: 5, accuracy: 10, uniqueness: 3, validity: 7

**coverage-matrix.tsx**:
- Table: requirement vs test_category
- Cell: count of test cases
- Highlight gaps (requirements without test cases)

**export-panel.tsx**:
- Export all test cases as JSON
- Export dbt test YAML (concat all `dbt_test_yaml` fields)
- Export SQL test scripts
- Download as ZIP

---

### IMP-07: Responsive Layout + Navigation

**Mức độ**: Medium Priority
**Files**: `src/app/layout.tsx`, `src/components/layout/`

```
src/components/layout/
├── sidebar.tsx                 # Left sidebar navigation
├── header.tsx                  # Top header with breadcrumbs
├── breadcrumbs.tsx             # Breadcrumb navigation
└── mobile-nav.tsx              # Mobile hamburger menu
```

**Layout cần thay đổi**:
- Thêm sidebar cho project detail page:
  - Overview
  - Phase 1: Chunks
  - Phase 2: Requirements
  - Phase 3: Classifications
  - Phase 4: Test Cases
  - Agent Reviews
  - History
  - Dashboard
  - Export
- Breadcrumbs: Home > Projects > My Project > Phase 2
- Responsive: collapse sidebar on mobile

---

### IMP-08: Error Handling + Loading States

**Mức độ**: High Priority
**Files**: update existing components

Cần thêm across toàn bộ frontend:

1. **Error boundaries**: `src/components/error-boundary.tsx`
2. **Loading skeletons** cho mỗi page/component (thay vì "Loading..." text)
3. **Toast notifications**:
   - Success: "Project created", "Pipeline started", "Phase approved"
   - Error: "Failed to start pipeline", "Document parse error"
   - Info: "Pipeline is running..."
4. **Optimistic updates**: khi approve/revise, update UI ngay trước khi API respond
5. **Retry logic**: React Query retry đã config, nhưng hiện retry message cho user
6. **Empty states**: illustration + helpful message khi no data

---

### IMP-09: Search + Filter

**Mức độ**: Low Priority
**Files**: `src/components/filters/`

```
src/components/filters/
├── search-bar.tsx              # Global search across project artifacts
├── filter-panel.tsx            # Filter panel for tables
└── sort-controls.tsx           # Sort controls
```

Cần cho:
- Requirements table: search by title, filter by priority
- Classifications table: filter by category, pipeline_layer
- Test cases: filter by category, severity, tool, pipeline_layer
- Agent reviews: filter by agent, status, severity

---

### IMP-10: Dark Mode

**Mức độ**: Low Priority
**Files**: `src/lib/theme.ts`, update `globals.css`

- Toggle dark/light mode
- Store preference in localStorage
- Use CSS variables + Tailwind dark: variant

---

### IMP-11: Test Execution UI

**Mức độ**: High Priority
**Files**: `src/app/projects/[id]/executions/`, `src/components/execution/`
**API Spec**: Xem `API_SPEC.md` Section 6 — tất cả 6 endpoints đã implement phía backend.

Backend đã implement đầy đủ test execution feature gồm:
- 3 executor types (SQL, dbt, Great Expectations) với fallback chains
- Dry-run mode (validate only)
- Summary với breakdown by category & severity
- Cancel running execution

#### Cần tạo files:

```
src/components/execution/
├── execution-list.tsx             # Danh sách execution runs
├── execution-summary-card.tsx     # Summary card cho 1 execution
├── category-breakdown.tsx         # Breakdown by category/severity (stacked bars)
├── test-result-row.tsx            # Single test result (expandable)
└── execution-actions.tsx          # Run / Cancel buttons + config

src/app/projects/[id]/executions/
├── page.tsx                       # Execution list page
└── [executionId]/
    └── page.tsx                   # Execution detail page
```

#### API calls cần thêm vào `lib/api.ts`:

```typescript
// Start execution
export async function startExecution(
  projectId: string,
  testCaseIds?: string[],
  config?: Record<string, unknown>
): Promise<TestExecution>
// POST /projects/{projectId}/executions
// Body: { test_case_ids?: uuid[], config?: { dry_run?: boolean, db_url?: string } }

// List executions
export async function listExecutions(projectId: string): Promise<ExecutionListResponse>
// GET /projects/{projectId}/executions

// Get execution detail (includes results + summary)
export async function getExecution(
  projectId: string, executionId: string
): Promise<TestExecutionDetail>
// GET /projects/{projectId}/executions/{executionId}

// Get only results
export async function getExecutionResults(
  projectId: string, executionId: string
): Promise<TestResult[]>
// GET /projects/{projectId}/executions/{executionId}/results

// Get only summary
export async function getExecutionSummary(
  projectId: string, executionId: string
): Promise<ExecutionSummary>
// GET /projects/{projectId}/executions/{executionId}/summary

// Cancel execution
export async function cancelExecution(
  projectId: string, executionId: string
): Promise<TestExecution>
// POST /projects/{projectId}/executions/{executionId}/cancel
```

#### Types cần thêm vào `types/api.ts`:

```typescript
interface TestExecution {
  id: string;
  project_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  triggered_by: string;
  total_tests: number;
  passed: number;
  failed: number;
  errors: number;
  skipped: number;
  duration_ms: number | null;
  config: Record<string, unknown> | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
}

interface TestResult {
  id: string;
  execution_id: string;
  test_case_id: string;
  status: string;              // "pending" | "running" | "completed"
  result: "pass" | "fail" | "error" | "skip" | null;
  executor_type: string;       // "custom_sql" | "dbt_test" | "great_expectations" | "dbt_macro"
  actual_output: Record<string, unknown> | null;
  expected_output: Record<string, unknown> | null;
  error_message: string | null;
  error_detail: Record<string, unknown> | null;
  rows_scanned: number | null;
  rows_failed: number | null;
  duration_ms: number | null;
  sql_executed: string | null;
  logs: string[] | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  // Joined from test case
  test_id?: string;
  test_title?: string;
  test_category?: string;      // "completeness" | "consistency" | "timeliness" | "accuracy" | "uniqueness" | "validity"
  pipeline_layer?: string;     // "staging" | "intermediate" | "mart"
  severity?: string;           // "critical" | "high" | "medium" | "low"
}

interface ExecutionSummary {
  total_tests: number;
  passed: number;
  failed: number;
  errors: number;
  skipped: number;
  pass_rate: number;           // 0-100
  duration_ms: number | null;
  by_category: Record<string, { total: number; pass: number; fail: number; error: number; skip: number }>;
  by_severity: Record<string, { total: number; pass: number; fail: number; error: number; skip: number }>;
}

interface TestExecutionDetail extends TestExecution {
  results: TestResult[];
  summary: ExecutionSummary | null;
}

interface ExecutionListResponse {
  items: TestExecution[];
  total: number;
}
```

---

#### Chi tiết từng component:

##### execution-list.tsx
- Card list cho mỗi execution run
- Hiện: status icon + badge, pass rate (e.g. "12/15 passed — 80%"), mini progress bar (green/red segments), duration, triggered_by, timestamp
- Status colors: pending=gray, running=blue (pulse animation), completed=green, failed=red, cancelled=yellow
- Click row → navigate to `/projects/[id]/executions/[executionId]`
- API: `GET /projects/{id}/executions`

##### execution-summary-card.tsx
- Hiện overview cho 1 execution:
  - Pass rate lớn (e.g. "80%") với circular or horizontal progress bar
  - Color: >=90% green, >=70% yellow, <70% red
  - Stats grid: Total | Passed | Failed | Errors | Skipped (mỗi cái 1 number card)
  - Duration: "4.5s"
- Input: `ExecutionSummary` object

##### category-breakdown.tsx
- Breakdown kết quả theo `by_category` hoặc `by_severity`
- Hiện mỗi category/severity 1 row:
  - Label (e.g. "Completeness")
  - Stacked horizontal bar: green=pass, red=fail, orange=error, gray=skip
  - Count text: "4/5 passed"
- Toggle giữa "By Category" và "By Severity" tabs
- Category labels mapping: completeness→"Completeness", consistency→"Consistency", timeliness→"Timeliness", accuracy→"Accuracy", uniqueness→"Uniqueness", validity→"Validity"
- Input: `ExecutionSummary` object + `groupBy: "by_category" | "by_severity"`

##### test-result-row.tsx
- Expandable row cho 1 test result
- Collapsed: status icon (✓ green, ✗ red, ! orange, — gray), test_id, test_title, category badge, severity badge, executor_type badge, duration
- Expanded (click to toggle):
  - Error message (nếu có, hiện trong red box)
  - SQL executed (syntax highlighted trong code block)
  - Actual vs Expected output (side-by-side JSON, highlight differences)
  - Rows scanned / Rows failed metrics
  - Execution logs (mỗi log line 1 row, monospace)
- Input: `TestResult` object

##### execution-actions.tsx
- "Run All Tests" button → `POST /executions` (no body)
- "Run Selected" button → `POST /executions` with `test_case_ids` (nếu user selected specific tests)
- Dry Run checkbox toggle → set `config.dry_run = true`
- Disabled khi: no test cases exist, hoặc execution đang running
- Cancel button (khi execution đang running) → `POST /executions/{id}/cancel`
- Show spinner + "Running..." khi mutation pending

---

#### Page: Execution List (`/projects/[id]/executions/page.tsx`)

```
┌──────────────────────────────────────────────┐
│ Test Executions              [⚙ Run All Tests]│
│                              [☐ Dry Run]      │
├──────────────────────────────────────────────┤
│ 🟢 Run #5  |  12/15 passed (80%)  |  4.5s   │
│    Mar 6, 2026 12:04 · by user               │
│    [████████████░░░]                          │
├──────────────────────────────────────────────┤
│ 🔵 Run #4  |  Running... 8/15     |  --      │
│    Mar 6, 2026 11:30 · by user               │
│    [██████░░░░░░░░░] ⏳                       │
├──────────────────────────────────────────────┤
│ 🔴 Run #3  |  5/15 passed (33%)   |  2.1s   │
│    Mar 5, 2026 09:15 · by user               │
│    [████░░░░░░░░░░░]                          │
└──────────────────────────────────────────────┘
```

- React Query: `queryKey: ["executions", projectId]`
- Auto-refetch every 5s nếu có execution đang running
- Show empty state khi chưa có executions
- Warn khi project chưa có test cases (disable Run button)

---

#### Page: Execution Detail (`/projects/[id]/executions/[executionId]/page.tsx`)

```
┌──────────────────────────────────────────────┐
│ Executions / abc123de                        │
│ Execution Detail          🟢 Completed       │
│ Triggered by user · Started Mar 6, 12:00     │
│                                   [Cancel]   │
├──────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────┐ │
│ │        80%          12 passed            │ │
│ │  [██████████████░░░] 2 failed  0 errors  │ │
│ │        4.5s          1 skipped           │ │
│ └──────────────────────────────────────────┘ │
├──────────────────────────────────────────────┤
│ [By Category] [By Severity]                  │
│                                              │
│ Completeness  [████░]  4/5                   │
│ Consistency   [█████]  3/3                   │
│ Accuracy      [███░░]  3/4                   │
│ Timeliness    [██░░░]  1/2                   │
│ Uniqueness    [█████]  1/1                   │
├──────────────────────────────────────────────┤
│ Test Results (14 of 15)                      │
│ [All Results ▾] [All Categories ▾]           │
│                                              │
│ ✓ TC-COMP-001 Verify required fields  CRIT  │
│ ✓ TC-COMP-002 Check email format      HIGH  │
│ ✗ TC-COMP-003 Validate phone number   HIGH  │
│   └─ Error: 42 rows have null phone_number  │
│      SQL: SELECT * FROM customers WHERE...   │
│ ✓ TC-CONS-001 Cross-table reference   MED   │
│ — TC-TIME-002 SLA check (skipped)     LOW   │
└──────────────────────────────────────────────┘
```

- React Query: `queryKey: ["execution", projectId, executionId]`
- **Auto-refetch every 3s** khi status = `running` hoặc `pending`
- Stop auto-refetch khi completed/failed/cancelled
- Breadcrumb: Executions → {executionId.slice(0,8)}
- Filters: result (all/pass/fail/error/skip), category (all/completeness/...)
- Cancel button chỉ hiện khi status = running/pending

---

#### Navigation
Thêm link "Executions" vào sidebar/navigation của project detail page, route: `/projects/[id]/executions`

---

## Implementation Order (Suggested)

| Priority | Task | Dependencies |
|----------|------|-------------|
| 1 | IMP-01: UI Component Library | None |
| 2 | IMP-08: Error Handling + Loading | IMP-01 |
| 3 | IMP-02: Phase Artifact Viewers | IMP-01 |
| 4 | IMP-03: Agent Review Panel | IMP-01 |
| 5 | IMP-11: Test Execution UI | IMP-01 |
| 6 | IMP-07: Responsive Layout + Nav | IMP-01 |
| 7 | IMP-04: Real-time Pipeline Progress | IMP-01 |
| 8 | IMP-05: Workflow History | IMP-01, IMP-07 |
| 9 | IMP-06: Dashboard | IMP-02 |
| 10 | IMP-09: Search + Filter | IMP-02 |
| 11 | IMP-10: Dark Mode | IMP-01 |

---

## Technical Notes

### API Proxy
`next.config.ts` đã config proxy `/api/*` → `http://localhost:8000/api/*`. Không cần CORS.

### API Client
`src/lib/api.ts` đã implement tất cả API calls. Chỉ cần import và dùng.

### Types
`src/types/api.ts` đã define tất cả TypeScript interfaces matching backend schemas.

### State Management
Dùng React Query (TanStack Query v5) cho server state. Không cần Redux/Zustand.
- `queryKey` conventions: `["projects"]`, `["project", id]`, `["phase-result", id, phaseId]`
- Mutations invalidate related queries automatically

### Styling
TailwindCSS v4 — import via `@import "tailwindcss"` trong `globals.css`.
Utility: `cn()` helper từ `src/lib/utils.ts` cho conditional classes.

### Color Mapping Constants
Đã define trong `src/lib/utils.ts`:
- `STATUS_COLORS` — project/phase status
- `SEVERITY_COLORS` — comment severity (critical/suggestion/info)
- `AGENT_COLORS` — 7 agent color schemes
- `PHASE_NAMES` — phase number → name
- `PHASE_DESCRIPTIONS` — phase number → description

### Existing Pages (đã scaffold, cần enhance)
| Route | File | Current State |
|-------|------|--------------|
| `/` | `app/page.tsx` | Basic landing page |
| `/projects` | `app/projects/page.tsx` | List + create (functional) |
| `/projects/[id]` | `app/projects/[id]/page.tsx` | Detail + pipeline controls (functional) |

### New Pages to Add
| Route | Purpose |
|-------|---------|
| `/projects/[id]/phases/[phaseId]` | Dedicated phase detail page |
| `/projects/[id]/executions` | Execution list + run tests (IMP-11) |
| `/projects/[id]/executions/[executionId]` | Execution detail + results (IMP-11) |
| `/projects/[id]/history` | Workflow history timeline |
| `/projects/[id]/dashboard` | Project dashboard with charts |
| `/projects/[id]/export` | Export test cases |
| `/projects/[id]/settings` | Project config + BRD re-upload (IMP-12) |

---

## IMP-12: Project Update UI

**Priority**: High
**Depends on**: Backend Project Update APIs (Section 7 in API_SPEC.md)

### Overview
Cho phép user update project đã tạo: re-upload BRD, quản lý test cases (tạo/sửa/deactivate), re-run failed tests, và lưu environment config.

### Components cần tạo

#### 1. BRD Re-upload Panel (`components/project/brd-reupload.tsx`)
- File dropzone cho BRD mới (PDF/DOCX)
- Checkbox "Discard pipeline artifacts" (default: checked)
- Warning dialog khi discard = true: "This will delete all pipeline-generated artifacts. Manual test cases will be preserved."
- Show current `brd_version`
- API: `POST /projects/{id}/brd` (multipart)

#### 2. Test Case Manager (`components/project/test-case-manager.tsx`)
- Table hiển thị tất cả test cases với columns: test_id, title, category, tool, source, is_active, actions
- Filter bar: `active_only` toggle, search by title/test_id, filter by source (pipeline/manual)
- Row actions: Edit, Deactivate/Activate toggle
- "Add Manual Test Case" button → opens create form
- Bulk deactivate selection
- API: `GET /projects/{id}/test-cases?active_only=true`, `POST .../deactivate`, `POST .../activate`

#### 3. Manual Test Case Form (`components/project/create-test-case-dialog.tsx`)
- Form fields: test_id, title, description, test_category (dropdown), pipeline_layer (dropdown), tool (dropdown), sql_logic (code editor), severity, priority, tags
- Validation: required fields per `TestCaseCreate` schema
- API: `POST /projects/{id}/test-cases`

#### 4. Environment Config Panel (`components/project/project-config.tsx`)
- Form: db_url, dbt_project_dir, gx_context_dir, extra (JSON editor)
- "Test Connection" button (optional, client-side only)
- Auto-save on blur hoặc explicit Save button
- Show "Config saved" feedback
- API: `GET /projects/{id}/config`, `PUT /projects/{id}/config`

#### 5. Re-run Failed Button (`components/execution/rerun-failed-button.tsx`)
- Button trên execution detail page: "Re-run Failed Tests"
- Chỉ show khi execution có failed/error tests
- Confirmation dialog: "Re-run X failed tests?"
- Navigate to new execution detail sau khi tạo
- API: `POST /projects/{id}/executions/{eid}/rerun-failed`

### Pages to modify

#### `/projects/[id]/page.tsx`
- Add tab "Settings" → chứa BRD Re-upload Panel + Environment Config Panel
- Add tab "Test Cases" → chứa Test Case Manager
- Update project header hiển thị `brd_version`

#### `/projects/[id]/executions/[executionId]/page.tsx`
- Add "Re-run Failed" button
- Show `triggered_by: "rerun"` badge

### API client additions (`lib/api.ts`)
```typescript
// BRD re-upload
reuploadBrd(projectId: string, file: File, discardArtifacts?: boolean): Promise<BrdReuploadResponse>

// Test case management
createTestCase(projectId: string, data: TestCaseCreate): Promise<TestCase>
deactivateTestCase(projectId: string, tcId: string): Promise<TestCase>
activateTestCase(projectId: string, tcId: string): Promise<TestCase>

// Project config
getProjectConfig(projectId: string): Promise<ProjectConfig | null>
updateProjectConfig(projectId: string, data: ProjectConfigUpdate): Promise<ProjectConfig>

// Re-run failed
rerunFailed(projectId: string, executionId: string): Promise<TestExecution>
```

### TypeScript types additions (`types/api.ts`)
```typescript
interface TestCase {
  // ...existing fields...
  is_active: boolean
  source: 'pipeline' | 'manual'
  updated_at: string | null
}

interface ProjectConfig {
  id: string
  project_id: string
  db_url: string | null
  dbt_project_dir: string | null
  gx_context_dir: string | null
  extra: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

interface BrdReuploadResponse {
  project_id: string
  brd_version: number
  file_name: string | null
  artifacts_discarded: boolean
  message: string
}

interface Project {
  // ...existing fields...
  brd_version: number
}
```
