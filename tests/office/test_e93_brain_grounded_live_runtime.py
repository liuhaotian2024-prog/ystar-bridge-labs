"""Tests for E93 brain-grounded live runtime."""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pytest

# Ensure paths
_BRIDGE_ROOT = Path(__file__).resolve().parents[2]
_Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT",
    "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
_GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT",
    "/Users/haotianliu/.openclaw/workspace/gov-mcp"))

for p in [str(_BRIDGE_ROOT), str(_BRIDGE_ROOT / "scripts"),
          str(_Y_GOV_ROOT), str(_GOV_MCP_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)


def _has_brain_db() -> bool:
    return (_BRIDGE_ROOT / "aiden_brain.db").exists()


pytestmark = pytest.mark.skipif(
    not _has_brain_db(),
    reason="aiden_brain.db not present; E93 requires the brain DB",
)


def test_brain_query_returns_activations():
    from office.mission_command.e93_brain_grounded_live_runtime import (
        query_brain_for_stage,
    )
    activations = query_brain_for_stage(
        "speed_to_cash_evaluation",
        "find first cash path quickly",
        top_n=5,
    )
    assert isinstance(activations, list)
    assert len(activations) >= 1
    for n in activations:
        assert "node_id" in n and n["node_id"]
        assert "activation_level" in n


def test_brain_grounded_packet_contract_satisfied():
    from office.mission_command.e93_brain_grounded_live_runtime import (
        build_brain_grounded_packet,
    )
    from ystar.governance import validate_ceo_brain_grounded_intelligence_packet
    packet = build_brain_grounded_packet(
        owner_intent="test owner intent for E93",
        session_id="e93_test_session",
    )
    decision = validate_ceo_brain_grounded_intelligence_packet(packet)
    assert decision.decision.value == "ALLOW", \
        f"contract failed: {decision.reason}"


def test_e93_session_writes_persistent_cieu(tmp_path):
    from office.mission_command.e93_brain_grounded_live_runtime import (
        run_e93_brain_grounded_runtime_session,
    )
    db = tmp_path / "e93_test.db"
    result = run_e93_brain_grounded_runtime_session(
        cieu_db=str(db),
        owner_intent="E93 end-to-end test owner intent",
        session_id="e93_e2e_test",
        seal_session=True,
    )
    assert result["brain_grounded_decision"] == "ALLOW"
    assert result["pre_action_decision"] == "ALLOW"
    assert result["post_action_decision"] == "ALLOW"
    assert result["end_to_end_brain_grounded_chain_proven"] is True

    # Verify CIEU events wrote
    c = sqlite3.connect(str(db))
    rows = c.execute(
        "SELECT event_type, decision FROM cieu_events WHERE session_id='e93_e2e_test'"
    ).fetchall()
    event_types = [r[0] for r in rows]
    assert "CEO_BRAIN_GROUNDED_INTELLIGENCE_DECISION" in event_types
    assert "CEO_COGNITIVE_OS_RUNTIME_DECISION" in event_types
    assert all(r[1] == "allow" for r in rows)

    # Verify Merkle seal
    sealed = c.execute(
        "SELECT merkle_root, event_count FROM sealed_sessions WHERE session_id='e93_e2e_test'"
    ).fetchone()
    assert sealed is not None
    assert sealed[1] >= 3


def test_e93_no_external_action_executed(tmp_path):
    from office.mission_command.e93_brain_grounded_live_runtime import (
        run_e93_brain_grounded_runtime_session,
    )
    db = tmp_path / "e93_boundary.db"
    result = run_e93_brain_grounded_runtime_session(
        cieu_db=str(db),
        owner_intent="boundary test",
        session_id="e93_boundary_test",
    )
    assert result["no_external_action_executed"] is True
    assert result["no_customer_revenue_payment_claim"] is True
    assert result["K9Audit_integration_claim"] is False
    receipt = result["gov_mcp_receipt"]
    assert receipt["no_send_invariant"] is True
    assert receipt["external_provider_called"] is False
    assert receipt["provider_action_executed"] is False


def test_e93_different_intents_produce_different_brain_activations():
    from office.mission_command.e93_brain_grounded_live_runtime import (
        build_brain_grounded_packet,
    )
    p1 = build_brain_grounded_packet(
        owner_intent="how do I find first paying customer",
        session_id="e93_p1",
    )
    p2 = build_brain_grounded_packet(
        owner_intent="absolute honesty board governance",
        session_id="e93_p2",
    )
    nodes_1 = {n["node_id"] for s in p1["stages"] for n in s["brain_activations"]}
    nodes_2 = {n["node_id"] for s in p2["stages"] for n in s["brain_activations"]}
    # Different intents must yield at least some different activated nodes
    assert nodes_1 != nodes_2
    # And both must have produced real activations
    assert len(nodes_1) >= 3
    assert len(nodes_2) >= 3


def test_e93_l5_truth_table_after():
    from office.mission_command.e93_brain_grounded_live_runtime import _l5_truth_table
    table = _l5_truth_table()
    assert table["L5-A Runtime Foundation"] == "complete_with_persistent_cieu_store"
    assert "brain_grounded" in table["L5-B CEO Intelligence Loop"]
    assert table["L5-C Controlled External Action"] == "partial_dry_run_only"
    assert table["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
    assert "active" in table["L5-E Brain Learning Loop"]


def test_e93_reports_written_to_disk(tmp_path):
    from office.mission_command.e93_brain_grounded_live_runtime import (
        run_e93_brain_grounded_runtime_session,
        write_e93_session_reports,
    )
    db = tmp_path / "e93_reports.db"
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    result = run_e93_brain_grounded_runtime_session(
        cieu_db=str(db),
        owner_intent="report test",
        session_id="e93_report_test",
    )
    paths = write_e93_session_reports(result, repo_root=repo)
    assert Path(paths["report_path"]).exists()
    assert Path(paths["readback_path"]).exists()
    assert Path(paths["status_json"]).exists()
    assert Path(paths["status_md"]).exists()
    readback_text = Path(paths["readback_path"]).read_text()
    assert "E93" in readback_text
    assert "brain_grounded_decision" in readback_text
