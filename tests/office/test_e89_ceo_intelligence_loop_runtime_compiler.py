from __future__ import annotations

import json

from office.mission_command.e89_ceo_intelligence_loop_runtime_compiler import (
    INTELLIGENCE_STAGE_IDS,
    build_pre_action_packet_from_intelligence_packet,
    compile_ceo_intelligence_loop_packet,
    run_ceo_intelligence_runtime_session,
    write_e89_intelligence_runtime_reports,
)


def test_compiler_produces_all_required_structured_stages():
    packet = compile_ceo_intelligence_loop_packet()
    stage_ids = {stage["stage_id"] for stage in packet["stages"]}

    assert stage_ids == set(INTELLIGENCE_STAGE_IDS)
    for stage in packet["stages"]:
        assert stage["evidence_refs"]
        assert stage["output_summary"]
        assert stage["runtime_governance_required"] is True
        assert stage["CIEU_recording_required"] is True
    assert packet["truth_constraints"]["private_chain_of_thought_stored"] is False


def test_compiler_generates_candidates_counterfactual_and_commercial_gate():
    packet = compile_ceo_intelligence_loop_packet()

    assert len(packet["candidate_actions"]) >= 3
    assert packet["selected_candidate_id"] == "candidate_provider_dry_run"
    assert len(packet["counterfactual_comparison"]) >= 3
    assert any(row.get("selected") for row in packet["counterfactual_comparison"])
    for dimension in {
        "buyer_pain_clarity",
        "urgency",
        "willingness_to_pay_proxy",
        "shortest_cash_path_fit",
        "differentiation",
        "proof_needed",
        "owner_execution_burden",
        "risk_of_wasting_time",
    }:
        assert dimension in packet["commercial_sharpness_gate"]


def test_no_new_wheel_gate_references_existing_runtime_systems():
    packet = compile_ceo_intelligence_loop_packet()
    reused = " ".join(packet["no_new_wheel_gate"]["reused_systems"])

    for expected in [
        "bridge-labs behavior center",
        "E88 runtime session",
        "Y-star-gov runtime hook",
        "E86 CIEU writer",
        "gov-mcp dry-run",
        "E87R baseline",
    ]:
        assert expected in reused


def test_intelligence_loop_validates_and_writes_formal_cieustore_record(tmp_path):
    from ystar.governance import validate_and_write_ceo_intelligence_loop_packet

    db_path = tmp_path / "e89_intelligence.db"
    packet = compile_ceo_intelligence_loop_packet()

    result = validate_and_write_ceo_intelligence_loop_packet(packet, cieu_db=str(db_path), seal_session=True)

    assert result["governance_decision"]["decision"] == "ALLOW"
    assert result["formal_CIEU_log_written"] is True
    assert result["CIEU_write_result"]["verify_result"]["valid"] is True


def test_pre_action_packet_from_intelligence_preserves_selected_action():
    packet = compile_ceo_intelligence_loop_packet()
    pre_action = build_pre_action_packet_from_intelligence_packet(packet)

    assert pre_action["selected_action"] == packet["selected_action"]["description"]
    assert pre_action["action_class"] == "provider_tool_execution"
    assert any(
        capability["capability_id"] == "YstarGov_ceo_intelligence_loop_contract"
        for capability in pre_action["discovered_capabilities_consulted"]
    )


def test_full_intelligence_chain_reaches_e88_runtime_and_gov_mcp_dry_run(tmp_path):
    db_path = tmp_path / "e89_full_chain.db"

    result = run_ceo_intelligence_runtime_session(cieu_db=str(db_path))
    receipt = result["provider_route"]["gov_mcp_receipt"]

    assert result["intelligence_governance_decision"] == "ALLOW"
    assert result["intelligence_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["pre_action_runtime_decision"] == "ALLOW"
    assert result["post_action_runtime_decision"] == "ALLOW"
    assert result["pre_action_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["post_action_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["CIEUStore_record_summary"]["event_count"] >= 3
    assert result["CIEUStore_record_summary"]["sealed_session_valid"] is True
    assert result["end_to_end_intelligence_chain_proven"] is True
    assert result["selected_action_proof"]["flowed_into_E88_runtime_session"] is True
    assert receipt["intelligence_loop_id"] == "e89_ceo_intelligence_loop"
    assert receipt["selected_candidate_id"] == "candidate_provider_dry_run"
    assert receipt["YstarGov_intelligence_decision"] == "ALLOW"
    assert receipt["provider_action_executed"] is False
    assert receipt["external_side_effect"] is False
    assert receipt["no_send_invariant"] is True


def test_l5_status_updates_honestly_without_l4_or_revenue_claims(tmp_path):
    result = run_ceo_intelligence_runtime_session(cieu_db=str(tmp_path / "e89_l5.db"))
    l5 = result["L5_truth_table_after"]

    assert l5["L5-A Runtime Foundation"] == "complete_internal_runtime_foundation"
    assert l5["L5-B CEO Intelligence Loop"] == "complete_for_structured_governed_intelligence_loop"
    assert l5["L5-C Controlled External Action"] == "partial_dry_run_only"
    assert l5["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
    assert result["safety_statement"]["no_L4_feedback_executed"] is True
    assert result["safety_statement"]["no_revenue_payment_pricing_loop_claim"] is True


def test_reports_are_written_with_required_status(tmp_path):
    report = write_e89_intelligence_runtime_reports(cieu_db=str(tmp_path / "e89_report.db"), root=tmp_path)

    report_path = tmp_path / "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler_report.json"
    status_path = tmp_path / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e89_ceo_intelligence_loop_runtime_compiler.json"
    readback_path = tmp_path / "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler_readback.md"

    assert report_path.exists()
    assert status_path.exists()
    assert readback_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert report["end_to_end_intelligence_chain_proven"] is True
    assert payload["gov_mcp_receipt_summary"]["provider_action_executed"] is False
    assert payload["gov_mcp_receipt_summary"]["external_side_effect"] is False
    assert status["L5-B"] == "complete_for_structured_governed_intelligence_loop"
    assert status["L5-D"] == "absent_or_not_executed"
