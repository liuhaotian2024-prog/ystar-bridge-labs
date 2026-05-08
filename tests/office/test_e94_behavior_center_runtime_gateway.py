from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/tmp/e94_ystar_work"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))

for path in (BRIDGE_ROOT, BRIDGE_ROOT / "scripts", Y_GOV_ROOT, GOV_MCP_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _has_brain_db() -> bool:
    return (BRIDGE_ROOT / "aiden_brain.db").exists()


pytestmark = pytest.mark.skipif(not _has_brain_db(), reason="E94 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRIDGE_ROOT / "aiden_brain.db", copied)
    return copied


def test_behavior_center_packet_calls_answer_owner_and_brain(tmp_path):
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        build_behavior_center_runtime_packet,
    )

    packet = build_behavior_center_runtime_packet(
        "Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？",
        repo_root=BRIDGE_ROOT,
        brain_db=_brain_copy(tmp_path),
    )

    assert packet["behavior_center_source"].endswith("answer_owner")
    assert "Founder AI Workflow Audit" in packet["behavior_center_response"]
    assert packet["brain_provenance"]["total_activations"] >= 1
    assert packet["brain_provenance"]["unique_nodes"] >= 1
    assert packet["brain_activations"]
    assert packet["autonomous_execution_policy"]["can_autonomously_execute"] is True


def test_low_risk_external_validation_routes_to_gov_mcp_dry_run(tmp_path):
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        run_behavior_center_runtime_gateway_session,
    )

    result = run_behavior_center_runtime_gateway_session(
        owner_message="Prepare a transparent low-risk customer validation message draft",
        cieu_db=str(tmp_path / "e94_low_risk.db"),
        repo_root=BRIDGE_ROOT,
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=Y_GOV_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
        session_id="e94_low_risk_session",
    )

    assert result["behavior_center_decision"] == "ALLOW"
    assert result["route_result"]["route_type"] == "low_risk_external_validation_dry_run"
    receipt = result["route_result"]["gov_mcp_receipt"]
    assert receipt["no_send_invariant"] is True
    assert receipt["external_provider_called"] is False
    assert receipt["provider_action_executed"] is False
    assert result["no_external_action_executed"] is True


def test_high_risk_payment_generates_owner_packet_not_autonomous_execution(tmp_path):
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        run_behavior_center_runtime_gateway_session,
    )

    result = run_behavior_center_runtime_gateway_session(
        owner_message="Send payment and sign the legal contract now",
        cieu_db=str(tmp_path / "e94_high_risk.db"),
        repo_root=BRIDGE_ROOT,
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=Y_GOV_ROOT,
        session_id="e94_high_risk_session",
    )

    assert result["behavior_center_decision"] == "ESCALATE"
    assert result["route_result"]["route_type"] == "owner_decision_packet"
    assert result["route_result"]["owner_decision_packet"]["execution_allowed_before_owner_decision"] is False
    assert result["no_external_action_executed"] is True


def test_engineering_route_builds_ceo_implementation_order(tmp_path):
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        run_behavior_center_runtime_gateway_session,
    )

    result = run_behavior_center_runtime_gateway_session(
        owner_message="Codex should implement the next runtime test patch",
        cieu_db=str(tmp_path / "e94_codex.db"),
        repo_root=BRIDGE_ROOT,
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=Y_GOV_ROOT,
        session_id="e94_codex_session",
    )

    assert result["behavior_center_decision"] == "ALLOW"
    assert result["route_result"]["route_type"] == "ceo_implementation_order_required"
    order = result["route_result"]["CEOImplementationOrder"]
    assert order["artifact_id"] == "CEOImplementationOrder"
    assert order["executor_actor"] == "Codex"
    assert order["CEO_decision_actor"] == "bridge_labs_ceo"


def test_behavior_gateway_writes_cieu_records_and_seals(tmp_path):
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        run_behavior_center_runtime_gateway_session,
    )

    db = tmp_path / "e94_records.db"
    result = run_behavior_center_runtime_gateway_session(
        owner_message="Aiden, what should we do next internally?",
        cieu_db=str(db),
        repo_root=BRIDGE_ROOT,
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=Y_GOV_ROOT,
        session_id="e94_records_session",
    )

    assert result["end_to_end_behavior_gateway_proven"] is True
    con = sqlite3.connect(str(db))
    events = con.execute("select event_type, decision from cieu_events order by seq_global").fetchall()
    assert len(events) >= 2
    assert all(event[0] == "CEO_BEHAVIOR_CENTER_RUNTIME_DECISION" for event in events)
    seal = con.execute("select event_count, merkle_root from sealed_sessions").fetchone()
    assert seal[0] == len(events)
    assert seal[1]


def test_write_e94_reports(tmp_path):
    from office.mission_command.e94_behavior_center_runtime_gateway import (
        run_behavior_center_runtime_gateway_session,
        write_e94_reports,
    )

    result = run_behavior_center_runtime_gateway_session(
        owner_message="Aiden, summarize current internal runtime status",
        cieu_db=str(tmp_path / "e94_reports.db"),
        repo_root=BRIDGE_ROOT,
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=Y_GOV_ROOT,
        session_id="e94_report_session",
    )
    paths = write_e94_reports(result, repo_root=tmp_path)
    for value in paths.values():
        assert Path(value).exists()
    readback = Path(paths["readback_path"]).read_text(encoding="utf-8")
    assert "Low-risk work is not pushed back to the owner" in readback
    assert "high-risk external side effects remain owner-bound" in readback
