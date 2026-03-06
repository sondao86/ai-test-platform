"""Consolidation node — primary agent addresses all reviewer feedback."""

from __future__ import annotations

import json
import logging

from app.agents.personas import get_persona
from app.agents.prompts.consolidation import CONSOLIDATION_PROMPT
from app.core.claude_client import call_claude, parse_json_from_text
from app.graph.phase_config import get_phase_config
from app.graph.state import ReviewSubgraphState

logger = logging.getLogger(__name__)


def _format_reviews(reviews) -> str:
    """Format all reviews into a readable string for the consolidation prompt."""
    formatted = []
    for r in reviews:
        review_dict = {
            "agent_id": r.agent_id,
            "agent_name": r.agent_name,
            "status": r.status,
            "confidence": r.confidence,
            "comments": r.comments,
            "additions": r.additions,
        }
        formatted.append(review_dict)
    return json.dumps(formatted, indent=2)


async def consolidate(state: ReviewSubgraphState) -> dict:
    """Primary agent consolidates all reviewer feedback into final output."""
    phase_id = state["phase_id"]
    config = get_phase_config(phase_id)
    persona = get_persona(config.primary_agent_id)

    primary_output = state.get("current_primary_output", {})
    reviews = state.get("current_reviews", [])

    if not reviews:
        # No reviews to consolidate — pass through
        return {
            "current_step": "awaiting_user",
            "current_consolidated_output": primary_output.get("output"),
            "current_consolidation_summary": {"note": "No reviewers for this phase"},
        }

    user_prompt = CONSOLIDATION_PROMPT.format(
        primary_output=json.dumps(primary_output.get("output", {}), indent=2),
        reviews=_format_reviews(reviews),
    )

    logger.info(
        "Phase %d: %s consolidating %d reviews",
        phase_id,
        persona.name,
        len(reviews),
    )

    response = await call_claude(
        prompt=user_prompt,
        system_prompt=persona.system_prompt,
    )

    # Parse consolidation response
    result = parse_json_from_text(response.text)
    if result is None or not isinstance(result, dict):
        result = {
            "consolidated_output": primary_output.get("output"),
            "changelog": {
                "accepted": [],
                "rejected_with_reason": [],
                "additions_merged": [],
                "conflicts_for_user": [],
            },
        }

    return {
        "current_step": "awaiting_user",
        "current_consolidated_output": result.get(
            "consolidated_output", primary_output.get("output")
        ),
        "current_consolidation_summary": result.get("changelog", {}),
    }
