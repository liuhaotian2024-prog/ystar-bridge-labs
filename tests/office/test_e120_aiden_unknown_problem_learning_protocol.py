from __future__ import annotations

import os
from pathlib import Path

from office.mission_command.e120_aiden_unknown_problem_learning_protocol import (
    build_aiden_unknown_problem_learning_protocol,
    build_e120_operating_pattern_proof,
    run_e120_unknown_problem_learning_protocol_session,
)


YSTAR_ROOT = Path(os.environ.get("E120_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def test_unknown_problem_protocol_contains_human_grade_learning_stack():
    protocol = build_aiden_unknown_problem_learning_protocol()

    objective_domains = {item["domain_id"] for item in protocol["learning_objectives"]}
    assert "classical_theory_canon" in objective_domains
    assert "peer_experience_corpus" in objective_domains
    assert "historical_case_corpus" in objective_domains
    assert "current_market_evidence" in objective_domains
    assert "internal_capability_recall" in objective_domains
    assert "customer_contact_residuals" in objective_domains
    assert "first_principles" in protocol["thinking_modes"]
    assert "customer_empathy" in protocol["thinking_modes"]
    assert protocol["truth_constraints"]["recent_memory_only"] is False


def test_e120_operating_pattern_proof_requires_unknown_and_durable_learning_patterns():
    proof = build_e120_operating_pattern_proof()
    pattern_ids = {item["pattern_id"] for item in proof["pattern_invocations"]}

    assert "unknown_problem_learning_protocol" in pattern_ids
    assert "knowledge_graph_methodology_selection" in pattern_ids
    assert "source_discovery_tool_selection" in pattern_ids
    assert "content_type_freshness_policy" in pattern_ids
    assert "downstream_impact_scan" in pattern_ids


def test_e120_session_writes_operating_pattern_and_learning_protocol_cieu(tmp_path):
    result = run_e120_unknown_problem_learning_protocol_session(
        cieu_db=tmp_path / "e120.db",
        ystar_gov_root=YSTAR_ROOT,
        seal_session=False,
    )

    assert result["proven"] is True
    assert result["operating_pattern_result"]["governance_decision"]["decision"] == "ALLOW"
    assert result["unknown_problem_learning_result"]["governance_decision"]["decision"] == "ALLOW"
    assert result["truth_constraints"]["external_action_executed"] is False
