from __future__ import annotations

import json

from office.mission_command.e85_ceo_cognitive_os_runtime_bridge import (
    route_provider_tool_action_through_runtime_nervous_system,
)
from office.mission_command.e87_ceo_runtime_session import (
    build_e87_runtime_session_envelope,
    run_e87_ceo_runtime_session,
    write_e87_session_reports,
)


def test_e87_session_reuses_behavior_center_and_writes_pre_and_post_cieustore_records(tmp_path):
    cieu_db = tmp_path / "e87_session.db"

    result = run_e87_ceo_runtime_session(cieu_db=str(cieu_db))

    assert result["behavior_center_used"] is True
    assert result["pre_action_runtime_decision"] == "ALLOW"
    assert result["post_action_runtime_decision"] == "ALLOW"
    assert result["pre_action_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["post_action_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["CIEUStore_record_summary"]["event_count"] >= 2
    assert result["CIEUStore_record_summary"]["sealed_session_valid"] is True
    assert result["end_to_end_chain_proven"] is True


def test_e87_session_routes_allowed_provider_action_to_gov_mcp_dry_run_only(tmp_path):
    result = run_e87_ceo_runtime_session(cieu_db=str(tmp_path / "e87_session.db"))
    route = result["provider_route"]
    receipt = route["gov_mcp_receipt"]

    assert route["YstarGov_route"]["YstarGov_runtime_decision"] == "ALLOW"
    assert route["gov_mcp_dry_run_invoked"] is True
    assert receipt["execution_mode_boundary"] == "dry_run_only"
    assert receipt["provider_action_executed"] is False
    assert receipt["external_side_effect"] is False
    assert receipt["external_provider_called"] is False
    assert receipt["no_send_invariant"] is True


def test_e87_session_keeps_e85_runtime_bridge_compatibility_for_provider_route():
    envelope = build_e87_runtime_session_envelope()
    result = route_provider_tool_action_through_runtime_nervous_system(envelope)

    assert result["YstarGov_route"]["YstarGov_runtime_decision"] == "ALLOW"
    assert result["gov_mcp_dry_run_invoked"] is True
    assert result["provider_action_executed"] is False
    assert result["external_side_effect"] is False


def test_e87_session_l5_truth_table_is_honest(tmp_path):
    result = run_e87_ceo_runtime_session(cieu_db=str(tmp_path / "e87_session.db"))
    l5 = result["L5_truth_table_after"]

    assert l5["L5-A Runtime Foundation"] == "complete"
    assert l5["L5-B CEO Intelligence Loop"] == "partial"
    assert l5["L5-C Controlled External Action"] == "partial_dry_run_only"
    assert l5["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
    assert result["K9Audit_status"] == "not_integrated_no_write"
    assert result["safety_statement"]["no_L4_feedback_executed"] is True


def test_e87_session_reports_are_written_without_l5d_or_live_execution_claims(tmp_path):
    cieu_db = tmp_path / "e87_report_session.db"
    report = write_e87_session_reports(cieu_db=str(cieu_db), root=tmp_path)

    report_path = tmp_path / "office/mission_command/e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop_report.json"
    status_path = tmp_path / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop.json"
    readback_path = tmp_path / "office/mission_command/e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop_readback.md"

    assert report_path.exists()
    assert status_path.exists()
    assert readback_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))

    assert report["end_to_end_chain_proven"] is True
    assert payload["CIEUStore_write_status"]["formal_CIEU_log_written"] is True
    assert payload["gov_mcp_status"]["provider_action_executed"] is False
    assert payload["gov_mcp_status"]["external_side_effect"] is False
    assert payload["L5_truth_table_after"]["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
    assert status["end_to_end_chain"]["K9Audit"] == "not_integrated"
    assert status["L5-C"] == "partial_dry_run_only"
