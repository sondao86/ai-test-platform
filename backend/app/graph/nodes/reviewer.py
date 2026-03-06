"""Reviewer agent node — parameterized by agent persona."""

from __future__ import annotations

import json
import logging

from app.agents.personas import get_persona
from app.core.claude_client import call_claude, parse_json_from_text
from app.graph.nodes.primary import _build_prompt_context, _get_prompt_module
from app.graph.phase_config import get_phase_config
from app.graph.state import AgentReviewState, ReviewSubgraphState

logger = logging.getLogger(__name__)


async def reviewer_node(state: ReviewSubgraphState, agent_id: str) -> dict:
    """A reviewer agent evaluates the primary agent's output.

    This function is called via Send() with the agent_id bound.
    """
    phase_id = state["phase_id"]
    config = get_phase_config(phase_id)
    persona = get_persona(agent_id)

    prompt_module = _get_prompt_module(agent_id)
    prompt_key = config.reviewer_prompt_keys[agent_id]
    prompt_template = getattr(prompt_module, prompt_key)

    primary_output = state.get("current_primary_output", {})

    context = _build_prompt_context(state, phase_id)
    context["primary_output"] = json.dumps(primary_output.get("output", {}), indent=2)

    user_prompt = prompt_template.format(**context)

    logger.info(
        "Phase %d: %s reviewing output from %s",
        phase_id,
        persona.name,
        primary_output.get("agent_name", "unknown"),
    )

    response = await call_claude(
        prompt=user_prompt,
        system_prompt=persona.system_prompt,
    )

    # Parse review response
    review_data = parse_json_from_text(response.text)
    if review_data is None or not isinstance(review_data, dict):
        review_data = {
            "status": "approved",
            "confidence": 0.5,
            "comments": [{"severity": "info", "comment": response.text}],
            "additions": [],
        }

    review = AgentReviewState(
        agent_id=agent_id,
        agent_name=persona.name,
        role="reviewer",
        status=review_data.get("status", "approved"),
        confidence=review_data.get("confidence", 0.5),
        comments=review_data.get("comments", []),
        additions=review_data.get("additions", []),
    )

    return {
        "current_reviews": [review],
    }


def make_reviewer_node(agent_id: str):
    """Create a parameterized reviewer node for a specific agent."""

    async def _node(state: ReviewSubgraphState) -> dict:
        return await reviewer_node(state, agent_id)

    _node.__name__ = f"reviewer_{agent_id}"
    return _node
