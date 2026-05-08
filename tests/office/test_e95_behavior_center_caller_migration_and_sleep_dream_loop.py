from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")


def _has_brain_db() -> bool:
    return (BRIDGE_ROOT / "aiden_brain.db").exists()


pytestmark = pytest.mark.skipif(not _has_brain_db(), reason="E95 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRIDGE_ROOT / "aiden_brain.db", copied)
    return copied


def test_owner_facing_meeting_cli_uses_governed_gateway():
    source = (BRIDGE_ROOT / "office/aiden_meeting_room/meeting_cli.py").read_text(encoding="utf-8")

    assert "answer_owner_governed_text" in source
    assert "aiden_response_engine import answer_owner" not in source


def test_discovery_has_no_unmigrated_owner_facing_raw_callers():
    from office.mission_command.e95_behavior_center_caller_migration_and_sleep_dream_loop import (
        assert_no_owner_facing_raw_behavior_callers,
        discover_behavior_center_callers,
    )

    inventory = discover_behavior_center_callers(BRIDGE_ROOT)

    assert assert_no_owner_facing_raw_behavior_callers(inventory) is True
    assert inventory["unmigrated_owner_facing_callers"] == []
    statuses = {item["path"]: item["migration_status"] for item in inventory["callers"]}
    assert statuses["office/aiden_meeting_room/meeting_cli.py"] == "migrated_to_governed_gateway"
    assert statuses["office/mission_command/e94_behavior_center_runtime_gateway.py"] == "allowed_internal_kernel_or_compatibility_test"


def test_governed_entrypoint_writes_cieu_and_returns_behavior_response(tmp_path):
    from office.aiden_meeting_room.governed_gateway import answer_owner_governed_text

    text = answer_owner_governed_text(
        "Aiden, summarize current internal runtime status",
        repo_root=BRIDGE_ROOT,
        cieu_db=tmp_path / "e95_entrypoint.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=Y_GOV_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )

    assert "Runtime governance:" in text
    assert "decision: ALLOW" in text
    assert "external_action_executed: False" in text
    con = sqlite3.connect(str(tmp_path / "e95_entrypoint.db"))
    count = con.execute("select count(*) from cieu_events").fetchone()[0]
    assert count >= 2


def test_e95_session_builds_sleep_dream_candidate_and_applies_to_isolated_brain_copy(tmp_path):
    from office.mission_command.e95_behavior_center_caller_migration_and_sleep_dream_loop import (
        run_e95_behavior_center_migration_session,
        summarize_brain_node_exists,
    )

    brain_db = _brain_copy(tmp_path)
    result = run_e95_behavior_center_migration_session(
        owner_message="Aiden, summarize current internal runtime status",
        cieu_db=str(tmp_path / "e95_session.db"),
        brain_db=brain_db,
        repo_root=BRIDGE_ROOT,
        ystar_gov_root=Y_GOV_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )
    candidate = result["sleep_dream_learning_candidate"]

    assert result["owner_facing_raw_callers_closed"] is True
    assert result["governed_behavior_session"]["behavior_center_decision"] == "ALLOW"
    assert result["sleep_dream_apply_result"]["status"] == "ALLOW"
    assert summarize_brain_node_exists(brain_db, candidate["proposed_brain_node"]["node_id"]) is True
    assert result["no_external_action_executed"] is True


def test_production_brain_write_is_denied_without_explicit_authority(tmp_path):
    from office.mission_command.e95_behavior_center_caller_migration_and_sleep_dream_loop import (
        apply_sleep_dream_learning_candidate,
        build_sleep_dream_learning_candidate,
        run_governed_behavior_center_entrypoint,
    )

    result = run_governed_behavior_center_entrypoint(
        "Aiden, summarize current internal runtime status",
        cieu_db=str(tmp_path / "e95_candidate.db"),
        brain_db=_brain_copy(tmp_path),
        repo_root=BRIDGE_ROOT,
        ystar_gov_root=Y_GOV_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )
    candidate = build_sleep_dream_learning_candidate(result)
    denied = apply_sleep_dream_learning_candidate(
        candidate,
        brain_db=BRIDGE_ROOT / "aiden_brain.db",
        repo_root=BRIDGE_ROOT,
        allow_production_brain_write=False,
    )

    assert denied["status"] == "DENY"
    assert denied["brain_node_written"] is False


def test_reports_are_written_with_honest_l5_status(tmp_path):
    from office.mission_command.e95_behavior_center_caller_migration_and_sleep_dream_loop import (
        run_e95_behavior_center_migration_session,
        write_e95_reports,
    )

    result = run_e95_behavior_center_migration_session(
        owner_message="Aiden, summarize current internal runtime status",
        cieu_db=str(tmp_path / "e95_report_session.db"),
        brain_db=_brain_copy(tmp_path),
        repo_root=BRIDGE_ROOT,
        ystar_gov_root=Y_GOV_ROOT,
        gov_mcp_root=GOV_MCP_ROOT,
    )
    paths = write_e95_reports(result, repo_root=tmp_path)

    report = json.loads(Path(paths["report_path"]).read_text(encoding="utf-8"))
    assert report["owner_facing_raw_callers_closed"] is True
    assert report["L5_truth_table_after"]["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
    assert "No L4 feedback was executed." in report["what_was_not_claimed"]
    assert Path(paths["readback_path"]).exists()
