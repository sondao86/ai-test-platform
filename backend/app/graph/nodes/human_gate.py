"""Human gate node — interrupts for user approval/revision."""

from __future__ import annotations

import logging

from langgraph.types import interrupt

from app.graph.state import ReviewSubgraphState

logger = logging.getLogger(__name__)


async def human_gate(state: ReviewSubgraphState) -> dict:
    """Interrupt execution and wait for user decision.

    The user sees:
    - Consolidated output
    - All reviews
    - Changelog

    They can approve or request revision.
    """
    phase_id = state["phase_id"]
    consolidated_output = state.get("current_consolidated_output")
    reviews = state.get("current_reviews", [])
    changelog = state.get("current_consolidation_summary")

    logger.info("Phase %d: Awaiting user decision", phase_id)

    # Prepare summary for user
    review_summary = []
    for r in reviews:
        review_summary.append({
            "agent": r.agent_name,
            "status": r.status,
            "confidence": r.confidence,
            "comment_count": len(r.comments),
            "addition_count": len(r.additions),
        })

    # Interrupt and wait for user input
    user_input = interrupt({
        "phase_id": phase_id,
        "consolidated_output": consolidated_output,
        "review_summary": review_summary,
        "changelog": changelog,
        "revision_round": state.get("revision_round", 1),
        "prompt": "Review the consolidated output and agent reviews. Approve or request revision.",
    })

    decision = user_input.get("decision", "approved")
    feedback = user_input.get("feedback")

    logger.info("Phase %d: User decision = %s", phase_id, decision)

    return {
        "user_decision": decision,
        "user_feedback": feedback,
    }


def should_continue_or_revise(state: ReviewSubgraphState) -> str:
    """Routing function: after human gate, decide next step."""
    decision = state.get("user_decision")
    if decision == "revision_requested":
        return "revise"
    return "complete"
