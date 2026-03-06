"""Phase configuration registry — maps each phase to its agents and prompts."""

from dataclasses import dataclass, field

from app.core.enums import AgentIdEnum, PhaseEnum


@dataclass(frozen=True)
class PhaseConfig:
    """Configuration for a single pipeline phase."""

    phase_id: int
    phase_name: str
    phase_enum: PhaseEnum
    primary_agent_id: str
    reviewer_agent_ids: list[str]
    # Keys in prompt modules: e.g., "PHASE1_INGEST_PROMPT"
    primary_prompt_key: str
    reviewer_prompt_keys: dict[str, str] = field(default_factory=dict)


PHASE_CONFIGS: dict[int, PhaseConfig] = {
    1: PhaseConfig(
        phase_id=1,
        phase_name="Ingest & Chunk",
        phase_enum=PhaseEnum.INGEST,
        primary_agent_id=AgentIdEnum.BUSINESS,
        reviewer_agent_ids=[AgentIdEnum.DATA_ARCHITECT],
        primary_prompt_key="PHASE1_INGEST_PROMPT",
        reviewer_prompt_keys={
            AgentIdEnum.DATA_ARCHITECT: "PHASE1_REVIEW_PROMPT",
        },
    ),
    2: PhaseConfig(
        phase_id=2,
        phase_name="Requirement Clarification",
        phase_enum=PhaseEnum.CLARIFY,
        primary_agent_id=AgentIdEnum.BUSINESS,
        reviewer_agent_ids=[AgentIdEnum.DATA_TRANSLATOR, AgentIdEnum.DATA_GOVERNANCE],
        primary_prompt_key="PHASE2_CLARIFY_PROMPT",
        reviewer_prompt_keys={
            AgentIdEnum.DATA_TRANSLATOR: "PHASE2_REVIEW_PROMPT",
            AgentIdEnum.DATA_GOVERNANCE: "PHASE2_REVIEW_PROMPT",
        },
    ),
    3: PhaseConfig(
        phase_id=3,
        phase_name="Test Category Classification",
        phase_enum=PhaseEnum.CLASSIFY,
        primary_agent_id=AgentIdEnum.DATA_TRANSLATOR,
        reviewer_agent_ids=[
            AgentIdEnum.DATA_ENGINEER,
            AgentIdEnum.DATA_GOVERNANCE,
            AgentIdEnum.BI_ANALYTICS,
        ],
        primary_prompt_key="PHASE3_CLASSIFY_PROMPT",
        reviewer_prompt_keys={
            AgentIdEnum.DATA_ENGINEER: "PHASE3_REVIEW_PROMPT",
            AgentIdEnum.DATA_GOVERNANCE: "PHASE3_REVIEW_PROMPT",
            AgentIdEnum.BI_ANALYTICS: "PHASE3_REVIEW_PROMPT",
        },
    ),
    4: PhaseConfig(
        phase_id=4,
        phase_name="Test Case Generation",
        phase_enum=PhaseEnum.GENERATE,
        primary_agent_id=AgentIdEnum.DATA_ENGINEER,
        reviewer_agent_ids=[
            AgentIdEnum.DATA_GOVERNANCE,
            AgentIdEnum.DATA_OPS,
            AgentIdEnum.BI_ANALYTICS,
            AgentIdEnum.DATA_ARCHITECT,
        ],
        primary_prompt_key="PHASE4_GENERATE_PROMPT",
        reviewer_prompt_keys={
            AgentIdEnum.DATA_GOVERNANCE: "PHASE4_REVIEW_PROMPT",
            AgentIdEnum.DATA_OPS: "PHASE4_REVIEW_PROMPT",
            AgentIdEnum.BI_ANALYTICS: "PHASE4_REVIEW_PROMPT",
            AgentIdEnum.DATA_ARCHITECT: "PHASE4_REVIEW_PROMPT",
        },
    ),
}


def get_phase_config(phase_id: int) -> PhaseConfig:
    if phase_id not in PHASE_CONFIGS:
        raise ValueError(f"Invalid phase_id: {phase_id}. Must be 1-4.")
    return PHASE_CONFIGS[phase_id]
