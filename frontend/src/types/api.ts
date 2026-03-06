// === Project ===

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  current_phase: number;
  file_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
}

// === BRD Chunks (Phase 1) ===

export interface BrdChunk {
  id: string;
  section_title: string;
  section_type: string;
  content: string;
  order_index: number;
  metadata_: Record<string, unknown> | null;
  cross_references: string[] | null;
  created_at: string;
}

// === Requirements (Phase 2) ===

export interface Requirement {
  id: string;
  chunk_id: string | null;
  requirement_id: string;
  title: string;
  description: string;
  priority: string;
  business_rules: string[] | null;
  kpis: string[] | null;
  data_elements: string[] | null;
  created_at: string;
}

// === Test Category Mappings (Phase 3) ===

export interface TestCategoryMap {
  id: string;
  requirement_id: string | null;
  test_category: string;
  sub_category: string | null;
  rationale: string;
  confidence: number;
  pipeline_layer: string | null;
  tool_suggestion: string | null;
  created_at: string;
}

// === Test Cases (Phase 4) ===

export interface TestCase {
  id: string;
  category_map_id: string | null;
  test_id: string;
  title: string;
  description: string;
  test_category: string;
  pipeline_layer: string;
  tool: string;
  sql_logic: string | null;
  dbt_test_yaml: string | null;
  great_expectations_config: Record<string, unknown> | null;
  input_data: Record<string, unknown> | null;
  expected_result: Record<string, unknown> | null;
  severity: string;
  priority: number;
  sla_seconds: number | null;
  tags: string[] | null;
  created_at: string;
}

// === Agent Reviews ===

export interface AgentComment {
  target_id: string | null;
  severity: "critical" | "suggestion" | "info";
  comment: string;
  proposed_change: string | null;
}

export interface AgentReview {
  id: string;
  phase_id: number;
  agent_id: string;
  agent_name: string;
  role: "primary" | "reviewer";
  status: string;
  confidence: number | null;
  comments: AgentComment[] | null;
  additions: Record<string, unknown>[] | null;
  consolidation_summary: Record<string, unknown> | null;
  revision_round: number;
  created_at: string;
}

// === Phase Results ===

export interface ConsolidationChangelog {
  accepted: Record<string, unknown>[];
  rejected_with_reason: Record<string, unknown>[];
  additions_merged: Record<string, unknown>[];
  conflicts_for_user: Record<string, unknown>[];
}

export interface PhaseResult {
  phase_id: number;
  phase_name: string;
  status: string;
  primary_agent: string;
  reviewer_agents: string[];
  consolidated_output: Record<string, unknown> | null;
  reviews: AgentReview[];
  changelog: ConsolidationChangelog | null;
  revision_round: number;
}

// === Pipeline ===

export interface PipelineStatus {
  project_id: string;
  current_phase: number;
  current_step: string;
  phase_name: string;
  status: string;
}

export interface UserDecisionRequest {
  decision: "approved" | "revision_requested";
  feedback?: string;
}

// === Test Execution ===

export interface TestExecution {
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

export interface TestResult {
  id: string;
  execution_id: string;
  test_case_id: string;
  status: string;
  result: "pass" | "fail" | "error" | "skip" | null;
  executor_type: string;
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
  test_category?: string;
  pipeline_layer?: string;
  severity?: string;
}

export interface ExecutionSummary {
  total_tests: number;
  passed: number;
  failed: number;
  errors: number;
  skipped: number;
  pass_rate: number;
  duration_ms: number | null;
  by_category: Record<string, { total: number; pass: number; fail: number; error: number; skip: number }>;
  by_severity: Record<string, { total: number; pass: number; fail: number; error: number; skip: number }>;
}

export interface TestExecutionDetail extends TestExecution {
  results: TestResult[];
  summary: ExecutionSummary | null;
}

export interface ExecutionListResponse {
  items: TestExecution[];
  total: number;
}

// === Phase History ===

export interface PhaseHistory {
  id: string;
  phase_id: number;
  phase_name: string;
  status: string;
  action: string;
  user_decision: string | null;
  user_feedback: string | null;
  revision_round: number;
  snapshot: Record<string, unknown> | null;
  error_message?: string;
  completed_at?: string;
  created_at: string;
}
