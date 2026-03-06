"""LangGraph state definitions for the pipeline."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, TypedDict


@dataclass
class AgentReviewState:
    """A single agent's review of phase output."""

    agent_id: str
    agent_name: str
    role: str  # primary | reviewer
    status: str  # approved | changes_requested | additions_suggested
    confidence: float = 0.0
    comments: list[dict] = field(default_factory=list)
    additions: list[dict] = field(default_factory=list)


@dataclass
class PhaseResultState:
    """Result of a completed phase."""

    phase_id: int
    phase_name: str
    primary_output: dict | None = None
    consolidated_output: dict | None = None
    reviews: list[AgentReviewState] = field(default_factory=list)
    changelog: dict | None = None
    revision_round: int = 1
    user_decision: str | None = None
    user_feedback: str | None = None


class PipelineState(TypedDict):
    """Top-level LangGraph state for the entire pipeline."""

    # Session
    project_id: str
    current_phase: int  # 1-4

    # Input
    raw_document: str
    document_metadata: dict

    # Phase artifacts (accumulated across phases)
    brd_chunks: list[dict] | None
    clarified_requirements: list[dict] | None
    test_category_map: list[dict] | None
    test_case_specs: list[dict] | None

    # Active phase working state
    current_step: str  # primary_generate | reviewing | consolidating | awaiting_user
    current_primary_output: dict | None
    current_reviews: Annotated[list[AgentReviewState], operator.add]  # reducer: parallel append
    current_consolidated_output: dict | None
    current_consolidation_summary: dict | None

    # Human-in-the-loop
    user_decision: str | None  # approved | revision_requested
    user_feedback: str | None

    # History
    phase_results: list[PhaseResultState]
    revision_round: int


class ReviewSubgraphState(TypedDict):
    """State for the reusable review sub-graph."""

    # Inherited from parent
    project_id: str
    phase_id: int
    raw_document: str

    # Phase context (read-only within subgraph)
    brd_chunks: list[dict] | None
    clarified_requirements: list[dict] | None
    test_category_map: list[dict] | None

    # Working state
    current_step: str
    current_primary_output: dict | None
    current_reviews: Annotated[list[AgentReviewState], operator.add]
    current_consolidated_output: dict | None
    current_consolidation_summary: dict | None

    # Human-in-the-loop
    user_decision: str | None
    user_feedback: str | None
    revision_round: int
