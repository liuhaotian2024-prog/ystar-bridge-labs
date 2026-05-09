from __future__ import annotations

import os
from pathlib import Path

from office.mission_command.e121_aiden_host_autonomous_web_observer import (
    build_aiden_autonomous_query_frontier,
    build_aiden_host_autonomous_web_observer_packet,
    collect_autonomous_public_read_evidence,
    probe_local_gemma_runtime,
    run_e121_aiden_host_autonomous_web_observer_session,
)


def test_query_frontier_is_open_world_and_multi_round() -> None:
    frontier = build_aiden_autonomous_query_frontier()
    assert frontier["recent_memory_anchor_removed"] is True
    assert frontier["round_count"] >= 3
    assert len(frontier["domain_hypotheses"]) >= 8
    assert any(domain["domain_id"] == "manufacturing_quality" for domain in frontier["domain_hypotheses"])


def test_snapshot_observation_collects_source_dated_quality_gated_evidence() -> None:
    evidence = collect_autonomous_public_read_evidence(use_host_live_network=False)
    assert len(evidence["accepted"]) >= 12
    assert len({row["domain_id"] for row in evidence["accepted"]}) >= 6
    assert evidence["learning_quality_summary"]["learning_quality_gate_applied"] is True
    assert evidence["learning_quality_summary"]["average_quality_score"] >= 0.65
    assert all(row.get("source_date") for row in evidence["accepted"])


def test_packet_declares_public_read_no_side_effect_boundary() -> None:
    packet = build_aiden_host_autonomous_web_observer_packet()
    policy = packet["public_read_policy"]
    truth = packet["truth_constraints"]
    assert policy["public_read_only"] is True
    assert set(policy["allowed_http_methods"]) == {"GET", "HEAD"}
    assert truth["external_action_executed"] is False
    assert truth["customer_validation_claim"] is False


def test_local_gemma_probe_detects_gemma4_from_ollama_output() -> None:
    probe = probe_local_gemma_runtime(
        ollama_list_output="NAME                 ID        SIZE\ngemma4:latest       abc123    4.7 GB\nllama3:latest       def456    4.1 GB\n"
    )
    assert probe["available"] is True
    assert probe["model_name"] == "gemma4:latest"
    assert probe["external_provider_api_used"] is False
    assert probe["can_embed_aiden"] is True


def test_local_gemma_probe_returns_correct_path_when_missing() -> None:
    probe = probe_local_gemma_runtime(ollama_list_output="NAME ID SIZE\nllama3:latest def456 4.1 GB\n")
    assert probe["available"] is False
    assert probe["can_embed_aiden"] is False
    assert any("Ollama" in step for step in probe["correct_path_if_missing"])


def test_end_to_end_observer_session_writes_cieu_records(tmp_path: Path) -> None:
    result = run_e121_aiden_host_autonomous_web_observer_session(
        cieu_db=tmp_path / "e121_bridge.db",
        ystar_gov_root=Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov")),
        local_gemma_probe={
            "requested": False,
            "available": False,
            "status": "not_available",
            "runtime_host": "host-local",
            "model_name": "gemma4",
            "external_provider_api_used": False,
            "private_data_exfiltration_allowed": False,
        },
    )
    assert result["host_autonomous_web_observer_proven"] is True
    counts = result["CIEUStore_summary"]["event_type_counts"]
    assert counts["AIDEN_HOST_AUTONOMOUS_WEB_OBSERVER_DECISION"] == 1
    assert counts["AIDEN_OPERATING_PATTERN_DOCTRINE_DECISION"] == 1
    assert counts["AIDEN_UNKNOWN_PROBLEM_LEARNING_PROTOCOL_DECISION"] == 1
    assert result["packet"]["truth_constraints"]["external_action_executed"] is False
