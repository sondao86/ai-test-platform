from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentComment(BaseModel):
    target_id: str | None = None
    severity: str  # critical | suggestion | info
    comment: str
    proposed_change: str | None = None


class AgentReviewResponse(BaseModel):
    id: UUID
    phase_id: int
    agent_id: str
    agent_name: str
    role: str
    status: str
    confidence: float | None
    comments: list[AgentComment] | None
    additions: list[dict] | None
    consolidation_summary: dict | None
    revision_round: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsolidationChangelog(BaseModel):
    accepted: list[dict] = Field(default_factory=list)
    rejected_with_reason: list[dict] = Field(default_factory=list)
    additions_merged: list[dict] = Field(default_factory=list)
    conflicts_for_user: list[dict] = Field(default_factory=list)


class PhaseResultResponse(BaseModel):
    phase_id: int
    phase_name: str
    status: str  # pending | in_progress | completed | awaiting_user
    primary_agent: str
    reviewer_agents: list[str]
    consolidated_output: dict | None = None
    reviews: list[AgentReviewResponse] = Field(default_factory=list)
    changelog: ConsolidationChangelog | None = None
    revision_round: int = 1


class PipelineStatusResponse(BaseModel):
    project_id: UUID
    current_phase: int
    current_step: str  # primary_generate | reviewing | consolidating | awaiting_user
    phase_name: str
    status: str


class StartPipelineRequest(BaseModel):
    pass  # future: options like skip_phases, etc.


class UserDecisionRequest(BaseModel):
    decision: str  # approved | revision_requested
    feedback: str | None = None


class PhaseHistoryResponse(BaseModel):
    id: UUID
    phase_id: int
    phase_name: str
    action: str
    user_decision: str | None
    user_feedback: str | None
    revision_round: int
    snapshot: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RollbackRequest(BaseModel):
    target_phase: int = Field(..., ge=1, le=4)
