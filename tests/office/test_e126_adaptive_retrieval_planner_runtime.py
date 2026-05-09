from __future__ import annotations

import sqlite3
from pathlib import Path

from office.mission_command.e124_agent_native_company_messenger import generate_aiden_reply_text
from office.mission_command.e126_adaptive_retrieval_planner_runtime import (
    build_adaptive_action_context,
    build_adaptive_retrieval_planner_packet,
    run_adaptive_retrieval_planner_and_retrieval,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_planner_builds_adaptive_plan_not_fixed_list(tmp_path):
    packet = build_adaptive_retrieval_planner_packet(
        "Aiden, this is a new autonomous retrieval problem; plan intelligently.",
        repo_root=_repo_root(),
        force_unknown_problem=True,
    )
    assert packet["task_context"]["planning_mode"] == "adaptive_evidence_need_and_capability_invocation"
    assert packet["dynamic_retrieval_plan"]["plan_mode"] == "adaptive_dynamic_source_selection"
    assert packet["truth_constraints"]["fixed_retrieval_list_only"] is False
    assert "unknown_problem_learning_protocol" in packet["operating_pattern_selection"]["selected_pattern_ids"]


def test_strategy_plan_includes_public_read_or_open_world_route(tmp_path):
    packet = build_adaptive_retrieval_planner_packet(
        "Aiden, do a global market strategy analysis for fastest cash.",
        repo_root=_repo_root(),
        force_unknown_problem=True,
    )
    sources = set(packet["dynamic_retrieval_plan"]["planned_source_ids"])
    assert "external_public_read_runtime" in sources
    assert "open_world_strategy_runtime" in sources
    families = set(packet["evidence_need_analysis"]["required_evidence_families"])
    assert "competitor_and_substitute_evidence" in families
    assert "classical_theory_or_case_corpus" in families


def test_capability_invocation_plan_binds_old_mechanisms(tmp_path):
    packet = build_adaptive_retrieval_planner_packet(
        "Aiden, retrieve relevant memory before answering.",
        repo_root=_repo_root(),
        force_unknown_problem=True,
    )
    mechanisms = {
        item["mechanism_id"]
        for item in packet["capability_invocation_plan"]["invocations"]
    }
    assert {
        "E101_adaptive_governance_correct_path",
        "E113_no_new_wheel_runtime_law",
        "E119_operating_pattern_doctrine_registry",
        "E120_unknown_problem_learning_protocol",
        "E125_retrieval_orchestration_runtime",
    }.issubset(mechanisms)


def test_runtime_writes_planner_and_retrieval_cieu_records(tmp_path):
    db = tmp_path / "e126_runtime.db"
    result = run_adaptive_retrieval_planner_and_retrieval(
        "Aiden, plan adaptive retrieval and then retrieve local evidence.",
        cieu_db=db,
        repo_root=_repo_root(),
        allow_vector_query=False,
        force_unknown_problem=True,
    )
    assert result["adaptive_planner_decision"] == "ALLOW"
    assert result["retrieval_result"]["retrieval_decision"] == "ALLOW"
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT event_type, passed FROM cieu_events ORDER BY rowid").fetchall()
    assert ("AIDEN_ADAPTIVE_RETRIEVAL_PLANNER_DECISION", 1) in rows
    assert ("AIDEN_RETRIEVAL_ORCHESTRATION_DECISION", 1) in rows


def test_messenger_reply_uses_adaptive_planner_before_retrieval(tmp_path):
    result = generate_aiden_reply_text(
        "Can you use your retrieval intelligence before answering me?",
        cieu_db=tmp_path / "e126_messenger.db",
        repo_root=_repo_root(),
        allow_live_network=False,
    )
    assert result["adaptive_planner_decision"] == "ALLOW"
    assert result["retrieval_decision"] == "ALLOW"
    assert result["adaptive_retrieval_result"]["runtime_may_answer"] is True
    assert result["reply_text"]


def test_unknown_detection_for_new_need():
    context = build_adaptive_action_context(
        "Aiden, here is a new capability need you have not seen before.",
        task_type="runtime",
    )
    assert context["unknown_problem_related"] is True
    assert context["self_governance_related"] is True
