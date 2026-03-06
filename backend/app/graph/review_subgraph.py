"""Reusable collaborative review sub-graph.

Pattern per phase:
  primary_generate → fan_out_reviews (parallel Send) → collect → consolidate → human_gate
  If user revises → loop back to primary_generate
"""

from __future__ import annotations

import logging

from langgraph.constants import Send
from langgraph.graph import END, StateGraph

from app.graph.nodes.consolidator import consolidate
from app.graph.nodes.human_gate import human_gate, should_continue_or_revise
from app.graph.nodes.primary import primary_generate
from app.graph.nodes.reviewer import make_reviewer_node
from app.graph.phase_config import PhaseConfig
from app.graph.state import ReviewSubgraphState

logger = logging.getLogger(__name__)


def build_review_subgraph(config: PhaseConfig) -> StateGraph:
    """Build a reusable collaborative review sub-graph for a given phase.

    The graph structure:
        primary_generate
            ↓
        fan_out → [reviewer_agent_1, reviewer_agent_2, ...] (parallel)
            ↓
        consolidate
            ↓
        human_gate
            ↓
        (approve → END) | (revise → primary_generate)
    """
    builder = StateGraph(ReviewSubgraphState)

    # 1. Primary generation node
    builder.add_node("primary_generate", primary_generate)

    # 2. Reviewer nodes (one per reviewer agent)
    reviewer_nodes = []
    for agent_id in config.reviewer_agent_ids:
        node_name = f"reviewer_{agent_id}"
        builder.add_node(node_name, make_reviewer_node(agent_id))
        reviewer_nodes.append(node_name)

    # 3. Consolidation node
    builder.add_node("consolidate", consolidate)

    # 4. Human gate node
    builder.add_node("human_gate", human_gate)

    # --- Edges ---

    # Entry point
    builder.set_entry_point("primary_generate")

    # Primary → fan out to all reviewers (using conditional Send)
    if reviewer_nodes:

        def fan_out_to_reviewers(state: ReviewSubgraphState) -> list[Send]:
            """Send to all reviewer nodes in parallel."""
            sends = []
            for node_name in reviewer_nodes:
                sends.append(Send(node_name, state))
            return sends

        builder.add_conditional_edges("primary_generate", fan_out_to_reviewers, reviewer_nodes)

        # Each reviewer → consolidate
        for node_name in reviewer_nodes:
            builder.add_edge(node_name, "consolidate")
    else:
        # No reviewers — skip directly to consolidate
        builder.add_edge("primary_generate", "consolidate")

    # Consolidate → human gate
    builder.add_edge("consolidate", "human_gate")

    # Human gate → approve (END) or revise (loop back)
    builder.add_conditional_edges(
        "human_gate",
        should_continue_or_revise,
        {
            "complete": END,
            "revise": "primary_generate",
        },
    )

    return builder


def compile_review_subgraph(config: PhaseConfig):
    """Build and compile the review sub-graph for a phase."""
    builder = build_review_subgraph(config)
    return builder.compile()
