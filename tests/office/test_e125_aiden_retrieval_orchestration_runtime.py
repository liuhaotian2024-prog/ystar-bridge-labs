from __future__ import annotations

import sqlite3
from pathlib import Path

from office.mission_command.e124_agent_native_company_messenger import generate_aiden_reply_text
from office.mission_command.e125_aiden_retrieval_orchestration_runtime import (
    MANDATORY_SOURCE_IDS,
    build_aiden_retrieval_orchestration_packet,
    format_retrieval_context_for_aiden,
    run_aiden_retrieval_orchestration,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_retrieval_packet_queries_all_mandatory_sources(tmp_path):
    packet = build_aiden_retrieval_orchestration_packet(
        "Aiden, do you have RAG-like retrieval?",
        cieu_db=tmp_path / "e125_retrieval.db",
        repo_root=_repo_root(),
        allow_vector_query=False,
    )
    queried = {source["source_id"] for source in packet["retrieval_sources"]}
    assert set(MANDATORY_SOURCE_IDS).issubset(queried)
    assert packet["retrieval_plan"]["retrieval_required_before_answer"] is True
    assert packet["truth_constraints"]["recent_memory_only"] is False


def test_retrieval_runtime_writes_cieustore_record(tmp_path):
    db = tmp_path / "e125_retrieval_write.db"
    result = run_aiden_retrieval_orchestration(
        "Aiden, explain retrieval orchestration and use your repo memory.",
        cieu_db=db,
        repo_root=_repo_root(),
        allow_vector_query=False,
    )
    assert result["retrieval_decision"] == "ALLOW"
    assert "Governed retrieval context" in result["retrieval_context_summary"]
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT event_type, passed FROM cieu_events ORDER BY rowid").fetchall()
    assert ("AIDEN_RETRIEVAL_ORCHESTRATION_DECISION", 1) in rows


def test_vector_rag_missing_is_declared_not_faked(tmp_path):
    packet = build_aiden_retrieval_orchestration_packet(
        "Aiden, retrieve local knowledge.",
        cieu_db=tmp_path / "e125_vector.db",
        repo_root=_repo_root(),
        allow_vector_query=False,
    )
    vector = next(source for source in packet["retrieval_sources"] if source["source_id"] == "local_vector_rag")
    assert vector["retrieval_status"] in {"blocked_by_policy", "not_configured", "dependency_unavailable", "queried", "empty"}
    if vector["retrieval_status"] != "queried":
        assert vector["unavailable_reason"]
        assert vector["correct_path"]


def test_retrieval_context_includes_multiple_source_families(tmp_path):
    packet = build_aiden_retrieval_orchestration_packet(
        "Aiden, use the brain, repo, and runtime evidence.",
        cieu_db=tmp_path / "e125_context.db",
        repo_root=_repo_root(),
        allow_vector_query=False,
    )
    summary = format_retrieval_context_for_aiden(packet)
    assert "repo_evidence_index" in summary
    assert "aiden_6d_brain" in summary
    assert packet["source_coverage"]["satisfied_source_family_count"] >= 4


def test_messenger_aiden_reply_is_retrieval_governed(tmp_path):
    result = generate_aiden_reply_text(
        "Can you explain whether you have RAG-like retrieval?",
        cieu_db=tmp_path / "e125_messenger.db",
        repo_root=_repo_root(),
        allow_live_network=False,
    )
    assert result["retrieval_decision"] == "ALLOW"
    assert result["retrieval_result"]["YstarGov_retrieval_result"]["formal_CIEU_log_written"] is True
    assert result["reply_text"]
