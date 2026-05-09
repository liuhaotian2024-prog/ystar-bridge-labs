from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e116_aiden_idle_continuous_learning_runtime import (
    BRAIN_DB,
    build_aiden_idle_learning_packet,
    build_ceo_idle_learning_curriculum,
    run_aiden_idle_continuous_learning_cycle,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
YSTAR_ROOT = Path(os.environ.get("E116_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E116 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_e116_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e116_curriculum_covers_ceo_learning_breadth():
    domains = build_ceo_idle_learning_curriculum()
    domain_ids = {domain["domain_id"] for domain in domains}

    assert "ceo_judgment" in domain_ids
    assert "market_intelligence" in domain_ids
    assert "competitive_strategy" in domain_ids
    assert "technology_architecture" in domain_ids
    assert "failure_residual_learning" in domain_ids
    assert len(domains) >= 10


def test_e116_packet_builds_source_dated_knowledge_graph_delta(tmp_path):
    packet = build_aiden_idle_learning_packet(
        cieu_db=tmp_path / "idle.db",
        brain_db=_brain_copy(tmp_path),
        allow_brain_write=True,
    )

    assert packet["trigger_context"]["idle_state_verified"] is True
    assert len(packet["evidence_items"]) >= 8
    assert all(item["source_date"] for item in packet["evidence_items"])
    assert len(packet["knowledge_graph_delta"]["nodes"]) >= 8
    assert len(packet["knowledge_graph_delta"]["edges"]) >= 8
    assert packet["CZL_closure"]["R_t_plus_1"] == 0.0
    assert packet["truth_constraints"]["external_action_executed"] is False


def test_e116_idle_cycle_writes_cieu_then_test_brain_graph(tmp_path):
    brain = _brain_copy(tmp_path)
    result = run_aiden_idle_continuous_learning_cycle(
        cieu_db=tmp_path / "e116_cieu.db",
        brain_db=brain,
        ystar_gov_root=YSTAR_ROOT,
        allow_brain_write=True,
        seal_session=False,
    )

    assert result["idle_learning_cycle_proven"] is True
    assert result["YstarGov_idle_learning_write_result"]["governance_decision"]["decision"] == "ALLOW"
    assert "AIDEN_IDLE_CONTINUOUS_LEARNING_DECISION" in result["CIEUStore_summary"]["event_types"]
    assert result["brain_write_result"]["brain_write_performed"] is True
    assert result["brain_write_result"]["node_delta"] >= 1
    assert result["brain_write_result"]["edge_delta"] >= 1


def test_e116_active_session_preempts_idle_learning(tmp_path):
    result = run_aiden_idle_continuous_learning_cycle(
        cieu_db=tmp_path / "e116_active.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        allow_brain_write=True,
        explicit_session_task_active=True,
        seal_session=False,
    )

    decision = result["YstarGov_idle_learning_write_result"]["governance_decision"]
    assert decision["decision"] == "REQUIRE_REVISION"
    assert result["brain_write_result"]["brain_write_performed"] is False
    assert "finish the active session task first" in " ".join(decision["correct_path"])


def test_e116_report_mode_does_not_claim_revenue_or_external_action(tmp_path):
    result = run_aiden_idle_continuous_learning_cycle(
        cieu_db=tmp_path / "e116_report.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        allow_brain_write=False,
        seal_session=False,
    )

    assert result["truth_constraints"]["customer_validation_claim"] is False
    assert result["truth_constraints"]["revenue_claim"] is False
    assert result["truth_constraints"]["payment_claim"] is False
    assert result["truth_constraints"]["external_action_executed"] is False
    assert result["continuous_runtime_capability"]["supports_24h_idle_loop"] is True

