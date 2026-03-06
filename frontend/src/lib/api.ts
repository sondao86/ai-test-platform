import axios from "axios";
import type {
  AgentReview,
  BrdChunk,
  ExecutionListResponse,
  ExecutionSummary,
  PhaseHistory,
  PhaseResult,
  PipelineStatus,
  Project,
  ProjectListResponse,
  Requirement,
  TestCase,
  TestCategoryMap,
  TestExecution,
  TestExecutionDetail,
  TestResult,
  UserDecisionRequest,
} from "@/types/api";

const api = axios.create({
  baseURL: "/api/v1",
});

// === Projects ===

export async function createProject(formData: FormData): Promise<Project> {
  const { data } = await api.post("/projects", formData);
  return data;
}

export async function listProjects(): Promise<ProjectListResponse> {
  const { data } = await api.get("/projects");
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await api.get(`/projects/${id}`);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}`);
}

// === Phase Artifacts ===

export async function getProjectArtifacts(projectId: string) {
  const [chunks, requirements, classifications, test_cases] = await Promise.all([
    getChunks(projectId),
    getRequirements(projectId),
    getClassifications(projectId),
    getTestCases(projectId),
  ]);

  return {
    chunks,
    requirements,
    classifications,
    test_cases
  };
}

export async function getChunks(projectId: string): Promise<BrdChunk[]> {
  const { data } = await api.get(`/projects/${projectId}/chunks`);
  return data;
}

export async function updateChunk(projectId: string, chunkId: string, updates: Partial<BrdChunk>): Promise<BrdChunk> {
  const { data } = await api.put(`/projects/${projectId}/chunks/${chunkId}`, updates);
  return data;
}

export async function getRequirements(projectId: string): Promise<Requirement[]> {
  const { data } = await api.get(`/projects/${projectId}/requirements`);
  return data;
}

export async function updateRequirement(projectId: string, reqId: string, updates: Partial<Requirement>): Promise<Requirement> {
  const { data } = await api.put(`/projects/${projectId}/requirements/${reqId}`, updates);
  return data;
}

export async function getClassifications(projectId: string): Promise<TestCategoryMap[]> {
  const { data } = await api.get(`/projects/${projectId}/classifications`);
  return data;
}

export async function updateClassification(projectId: string, mapId: string, updates: Partial<TestCategoryMap>): Promise<TestCategoryMap> {
  const { data } = await api.put(`/projects/${projectId}/classifications/${mapId}`, updates);
  return data;
}

export async function getTestCases(projectId: string): Promise<TestCase[]> {
  const { data } = await api.get(`/projects/${projectId}/test-cases`);
  return data;
}

export async function updateTestCase(projectId: string, tcId: string, updates: Partial<TestCase>): Promise<TestCase> {
  const { data } = await api.put(`/projects/${projectId}/test-cases/${tcId}`, updates);
  return data;
}

// === Phase Results & Reviews ===

export async function getPhaseResult(projectId: string, phaseId: number): Promise<PhaseResult> {
  const { data } = await api.get(`/projects/${projectId}/phases/${phaseId}`);
  return data;
}

export async function getPhaseReviews(projectId: string, phaseId: number): Promise<AgentReview[]> {
  const { data } = await api.get(`/projects/${projectId}/phases/${phaseId}/reviews`);
  return data;
}

// === Pipeline Workflow ===

export async function startPipeline(projectId: string): Promise<Record<string, unknown>> {
  const { data } = await api.post(`/projects/${projectId}/pipeline/start`);
  return data;
}

export async function submitDecision(
  projectId: string,
  body: UserDecisionRequest
): Promise<Record<string, unknown>> {
  const { data } = await api.post(`/projects/${projectId}/pipeline/decide`, body);
  return data;
}

export async function getPipelineStatus(projectId: string): Promise<PipelineStatus> {
  const { data } = await api.get(`/projects/${projectId}/pipeline/status`);
  return data;
}

// === Workflow History ===

export async function getWorkflowHistory(projectId: string): Promise<PhaseHistory[]> {
  const { data } = await api.get(`/projects/${projectId}/workflow/history`);
  return data;
}

export async function getProjectHistory(projectId: string): Promise<PhaseHistory[]> {
  return getWorkflowHistory(projectId);
}

export async function rollbackWorkflow(
  projectId: string,
  targetPhase: number
): Promise<Record<string, unknown>> {
  const { data } = await api.post(`/projects/${projectId}/workflow/rollback`, {
    target_phase: targetPhase,
  });
  return data;
}

// === Test Execution ===

export async function startExecution(
  projectId: string,
  testCaseIds?: string[],
  config?: Record<string, unknown>
): Promise<TestExecution> {
  const { data } = await api.post(`/projects/${projectId}/executions`, {
    test_case_ids: testCaseIds || null,
    config: config || null,
  });
  return data;
}

export async function listExecutions(projectId: string): Promise<ExecutionListResponse> {
  const { data } = await api.get(`/projects/${projectId}/executions`);
  return data;
}

export async function getExecution(
  projectId: string,
  executionId: string
): Promise<TestExecutionDetail> {
  const { data } = await api.get(`/projects/${projectId}/executions/${executionId}`);
  return data;
}

export async function getExecutionResults(
  projectId: string,
  executionId: string
): Promise<TestResult[]> {
  const { data } = await api.get(`/projects/${projectId}/executions/${executionId}/results`);
  return data;
}

export async function getExecutionSummary(
  projectId: string,
  executionId: string
): Promise<ExecutionSummary> {
  const { data } = await api.get(`/projects/${projectId}/executions/${executionId}/summary`);
  return data;
}

export async function cancelExecution(
  projectId: string,
  executionId: string
): Promise<TestExecution> {
  const { data } = await api.post(`/projects/${projectId}/executions/${executionId}/cancel`);
  return data;
}
