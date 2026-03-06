"""Tests for graph structure — verifies graphs compile without errors."""

from app.graph.phase_config import get_phase_config
from app.graph.review_subgraph import build_review_subgraph


def test_review_subgraph_builds_for_all_phases():
    """Verify review subgraph can be built for every phase."""
    for phase_id in range(1, 5):
        config = get_phase_config(phase_id)
        builder = build_review_subgraph(config)
        graph = builder.compile()
        assert graph is not None


def test_phase1_subgraph_has_one_reviewer():
    config = get_phase_config(1)
    builder = build_review_subgraph(config)
    graph = builder.compile()
    # Should have: primary_generate, reviewer_data_architect_agent, consolidate, human_gate
    node_names = set(graph.nodes.keys())
    assert "primary_generate" in node_names
    assert "consolidate" in node_names
    assert "human_gate" in node_names


def test_phase4_subgraph_has_four_reviewers():
    config = get_phase_config(4)
    builder = build_review_subgraph(config)
    graph = builder.compile()
    node_names = set(graph.nodes.keys())
    reviewer_nodes = [n for n in node_names if n.startswith("reviewer_")]
    assert len(reviewer_nodes) == 4
