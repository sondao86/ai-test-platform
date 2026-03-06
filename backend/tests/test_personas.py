"""Tests for agent personas."""

from app.agents.personas import AGENT_PERSONAS, get_persona
from app.core.enums import AgentIdEnum


def test_all_seven_agents_defined():
    assert len(AGENT_PERSONAS) == 7
    expected_ids = {
        AgentIdEnum.BUSINESS,
        AgentIdEnum.DATA_TRANSLATOR,
        AgentIdEnum.DATA_ENGINEER,
        AgentIdEnum.DATA_GOVERNANCE,
        AgentIdEnum.DATA_OPS,
        AgentIdEnum.DATA_ARCHITECT,
        AgentIdEnum.BI_ANALYTICS,
    }
    assert set(AGENT_PERSONAS.keys()) == expected_ids


def test_persona_has_required_fields():
    for agent_id, persona in AGENT_PERSONAS.items():
        assert persona.agent_id == agent_id
        assert persona.name
        assert persona.system_prompt
        assert persona.expertise_areas


def test_get_persona():
    persona = get_persona(AgentIdEnum.BUSINESS)
    assert persona.name == "Business Agent"
