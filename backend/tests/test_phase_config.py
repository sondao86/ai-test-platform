"""Tests for phase configuration."""

import pytest

from app.core.enums import AgentIdEnum
from app.graph.phase_config import PHASE_CONFIGS, get_phase_config


def test_all_four_phases_configured():
    assert set(PHASE_CONFIGS.keys()) == {1, 2, 3, 4}


def test_phase1_config():
    config = get_phase_config(1)
    assert config.primary_agent_id == AgentIdEnum.BUSINESS
    assert AgentIdEnum.DATA_ARCHITECT in config.reviewer_agent_ids


def test_phase2_config():
    config = get_phase_config(2)
    assert config.primary_agent_id == AgentIdEnum.BUSINESS
    assert AgentIdEnum.DATA_TRANSLATOR in config.reviewer_agent_ids
    assert AgentIdEnum.DATA_GOVERNANCE in config.reviewer_agent_ids


def test_phase3_config():
    config = get_phase_config(3)
    assert config.primary_agent_id == AgentIdEnum.DATA_TRANSLATOR
    assert len(config.reviewer_agent_ids) == 3


def test_phase4_config():
    config = get_phase_config(4)
    assert config.primary_agent_id == AgentIdEnum.DATA_ENGINEER
    assert len(config.reviewer_agent_ids) == 4


def test_invalid_phase_raises():
    with pytest.raises(ValueError):
        get_phase_config(5)
