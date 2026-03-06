"""Primary agent generation node."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.agents.personas import get_persona
from app.core.claude_client import call_claude, parse_json_from_text
from app.graph.phase_config import get_phase_config
from app.graph.state import ReviewSubgraphState

logger = logging.getLogger(__name__)

# Prompt module registry — maps agent_id to its prompt module
_PROMPT_MODULES: dict[str, Any] = {}


def _get_prompt_module(agent_id: str) -> Any:
    """Lazily load and cache prompt modules."""
    if agent_id not in _PROMPT_MODULES:
        module_map = {
            "business_agent": "app.agents.prompts.business_agent",
            "data_translator_agent": "app.agents.prompts.data_translator",
            "data_engineer_agent": "app.agents.prompts.data_engineer",
            "data_governance_agent": "app.agents.prompts.data_governance",
            "data_ops_agent": "app.agents.prompts.data_ops",
            "data_architect_agent": "app.agents.prompts.data_architect",
            "bi_analytics_agent": "app.agents.prompts.bi_analytics",
        }
        import importlib

        _PROMPT_MODULES[agent_id] = importlib.import_module(module_map[agent_id])
    return _PROMPT_MODULES[agent_id]


def _build_prompt_context(state: ReviewSubgraphState, phase_id: int) -> dict[str, str]:
    """Build template context variables from state for prompt formatting."""
    return {
        "raw_document": state.get("raw_document", "") or "",
        "brd_chunks": json.dumps(state.get("brd_chunks") or [], indent=2),
        "requirements": json.dumps(state.get("clarified_requirements") or [], indent=2),
        "test_category_map": json.dumps(state.get("test_category_map") or [], indent=2),
        "previous_clarifications": "[]",
        "user_feedback": state.get("user_feedback") or "None",
    }


async def primary_generate(state: ReviewSubgraphState) -> dict:
    """Primary agent generates initial output for the phase."""
    phase_id = state["phase_id"]
    config = get_phase_config(phase_id)
    persona = get_persona(config.primary_agent_id)

    prompt_module = _get_prompt_module(config.primary_agent_id)
    prompt_template = getattr(prompt_module, config.primary_prompt_key)

    context = _build_prompt_context(state, phase_id)
    user_prompt = prompt_template.format(**context)

    logger.info(
        "Phase %d: %s generating with %s",
        phase_id,
        config.phase_name,
        persona.name,
    )

    response = await call_claude(
        prompt=user_prompt,
        system_prompt=persona.system_prompt,
    )

    # Parse JSON from response
    output = parse_json_from_text(response.text)
    if output is None:
        output = {"raw_response": response.text}

    return {
        "current_step": "reviewing",
        "current_primary_output": {
            "agent_id": config.primary_agent_id,
            "agent_name": persona.name,
            "phase_id": phase_id,
            "output": output,
        },
        "current_reviews": [],
        "current_consolidated_output": None,
        "current_consolidation_summary": None,
        "user_decision": None,
        "user_feedback": None if state.get("user_decision") != "revision_requested" else state.get("user_feedback"),
    }
