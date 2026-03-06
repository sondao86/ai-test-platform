"""Outer pipeline graph — orchestrates 4 phases sequentially.

Each phase is a compiled review sub-graph (primary → review → consolidate → human gate).
After user approves a phase, its output is promoted to the pipeline state
and the next phase begins.
"""

from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from app.graph.phase_config import PHASE_CONFIGS, get_phase_config
from app.graph.review_subgraph import compile_review_subgraph
from app.graph.state import PhaseResultState, PipelineState, ReviewSubgraphState

logger = logging.getLogger(__name__)


def _make_phase_entry_node(phase_id: int):
    """Create a node that initializes subgraph state for a phase."""

    async def phase_entry(state: PipelineState) -> dict:
        logger.info("Entering Phase %d: %s", phase_id, get_phase_config(phase_id).phase_name)
        return {
            "current_phase": phase_id,
            "current_step": "primary_generate",
            "current_primary_output": None,
            "current_reviews": [],
            "current_consolidated_output": None,
            "current_consolidation_summary": None,
            "user_decision": None,
            "user_feedback": None,
            "revision_round": 1,
        }

    phase_entry.__name__ = f"phase_{phase_id}_entry"
    return phase_entry


def _make_phase_subgraph_node(phase_id: int):
    """Create a node that runs the review subgraph for a phase."""
    config = get_phase_config(phase_id)
    subgraph = compile_review_subgraph(config)

    async def phase_subgraph(state: PipelineState) -> dict:
        # Map pipeline state → subgraph state
        subgraph_input: ReviewSubgraphState = {
            "project_id": state["project_id"],
            "phase_id": phase_id,
            "raw_document": state.get("raw_document", ""),
            "brd_chunks": state.get("brd_chunks"),
            "clarified_requirements": state.get("clarified_requirements"),
            "test_category_map": state.get("test_category_map"),
            "current_step": "primary_generate",
            "current_primary_output": None,
            "current_reviews": [],
            "current_consolidated_output": None,
            "current_consolidation_summary": None,
            "user_decision": state.get("user_decision"),
            "user_feedback": state.get("user_feedback"),
            "revision_round": state.get("revision_round", 1),
        }

        # Run the subgraph
        result = await subgraph.ainvoke(subgraph_input)

        # Map subgraph result back to pipeline state
        return {
            "current_step": result.get("current_step", "completed"),
            "current_primary_output": result.get("current_primary_output"),
            "current_reviews": result.get("current_reviews", []),
            "current_consolidated_output": result.get("current_consolidated_output"),
            "current_consolidation_summary": result.get("current_consolidation_summary"),
            "user_decision": result.get("user_decision"),
            "user_feedback": result.get("user_feedback"),
        }

    phase_subgraph.__name__ = f"phase_{phase_id}_subgraph"
    return phase_subgraph


def _make_phase_commit_node(phase_id: int):
    """Create a node that commits phase results to pipeline state."""

    async def phase_commit(state: PipelineState) -> dict:
        config = get_phase_config(phase_id)
        consolidated = state.get("current_consolidated_output")

        # Store phase result
        result = PhaseResultState(
            phase_id=phase_id,
            phase_name=config.phase_name,
            primary_output=state.get("current_primary_output"),
            consolidated_output=consolidated,
            reviews=state.get("current_reviews", []),
            changelog=state.get("current_consolidation_summary"),
            revision_round=state.get("revision_round", 1),
            user_decision=state.get("user_decision"),
        )

        phase_results = list(state.get("phase_results", []))
        phase_results.append(result)

        # Promote consolidated output to the appropriate artifact slot
        updates: dict = {"phase_results": phase_results}

        if phase_id == 1:
            # Ingest → brd_chunks
            if isinstance(consolidated, list):
                updates["brd_chunks"] = consolidated
            elif isinstance(consolidated, dict):
                updates["brd_chunks"] = consolidated.get("chunks", consolidated.get("output", [consolidated]))
            else:
                updates["brd_chunks"] = []

        elif phase_id == 2:
            # Clarify → clarified_requirements
            if isinstance(consolidated, dict):
                updates["clarified_requirements"] = consolidated.get(
                    "requirements", consolidated.get("output", [consolidated])
                )
            elif isinstance(consolidated, list):
                updates["clarified_requirements"] = consolidated
            else:
                updates["clarified_requirements"] = []

        elif phase_id == 3:
            # Classify → test_category_map
            if isinstance(consolidated, list):
                updates["test_category_map"] = consolidated
            elif isinstance(consolidated, dict):
                updates["test_category_map"] = consolidated.get("mappings", consolidated.get("output", [consolidated]))
            else:
                updates["test_category_map"] = []

        elif phase_id == 4:
            # Generate → test_case_specs
            if isinstance(consolidated, list):
                updates["test_case_specs"] = consolidated
            elif isinstance(consolidated, dict):
                updates["test_case_specs"] = consolidated.get("test_cases", consolidated.get("output", [consolidated]))
            else:
                updates["test_case_specs"] = []

        logger.info("Phase %d committed", phase_id)
        return updates

    phase_commit.__name__ = f"phase_{phase_id}_commit"
    return phase_commit


def build_pipeline_graph() -> StateGraph:
    """Build the full 4-phase pipeline graph."""
    builder = StateGraph(PipelineState)

    # Add nodes for each phase: entry → subgraph → commit
    for phase_id in range(1, 5):
        builder.add_node(f"phase_{phase_id}_entry", _make_phase_entry_node(phase_id))
        builder.add_node(f"phase_{phase_id}_subgraph", _make_phase_subgraph_node(phase_id))
        builder.add_node(f"phase_{phase_id}_commit", _make_phase_commit_node(phase_id))

        # entry → subgraph → commit
        builder.add_edge(f"phase_{phase_id}_entry", f"phase_{phase_id}_subgraph")
        builder.add_edge(f"phase_{phase_id}_subgraph", f"phase_{phase_id}_commit")

    # Chain phases: commit_1 → entry_2 → ... → commit_4 → END
    builder.set_entry_point("phase_1_entry")
    for phase_id in range(1, 4):
        builder.add_edge(f"phase_{phase_id}_commit", f"phase_{phase_id + 1}_entry")
    builder.add_edge("phase_4_commit", END)

    return builder


def compile_pipeline_graph():
    """Build and compile the full pipeline graph."""
    builder = build_pipeline_graph()
    return builder.compile()
