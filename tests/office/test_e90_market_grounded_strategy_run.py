from __future__ import annotations

import json

from office.mission_command.e90_market_grounded_strategy_run import (
    build_market_grounded_strategy_artifact,
    run_e90_market_grounded_strategy_session,
    write_e90_strategy_reports,
)


def test_market_grounded_strategy_outputs_required_routes_and_selected_strategy():
    strategy = build_market_grounded_strategy_artifact()

    assert len(strategy["route_candidates"]) >= 5
    assert len(strategy["route_scoring"]) >= 5
    selected = strategy["selected_strategy"]
    assert selected["current_best_first_cash_path"]
    assert selected["second_best_path"]
    assert selected["do_not_pursue_path"]
    assert selected["next_48h_action"]
    assert selected["next_7d_action"]
    assert strategy["benchmark_result"]["pass"] is True


def test_next_l4_feedback_packet_is_no_send_and_owner_decision_gated():
    packet = build_market_grounded_strategy_artifact()["next_L4_feedback_owner_decision_packet"]

    assert packet["owner_decision_required"] is True
    assert packet["owner_approval_state"] == "pending_owner_decision"
    assert packet["no_send_default"] is True
    assert packet["external_action_executed"] is False
    assert packet["provider_action_executed"] is False
    assert packet["ai_transparency"] is True
    assert packet["opt_out_language"]


def test_strategy_makes_no_customer_revenue_or_payment_claims():
    strategy = build_market_grounded_strategy_artifact()
    overclaim = strategy["overclaim_boundary"]

    for field in [
        "customer_validation_claim",
        "revenue_claim",
        "payment_claim",
        "paid_signal_claim",
        "pricing_validation_claim",
        "L4_feedback_executed",
        "L5_revenue_loop_complete",
    ]:
        assert overclaim[field] is False


def test_cieu_predictions_are_future_testable():
    predictions = build_market_grounded_strategy_artifact()["CIEU_predictions"]

    assert predictions
    for prediction in predictions:
        for field in [
            "X_t",
            "U_t",
            "Y_star_t",
            "expected_Y_t_plus_1",
            "predicted_R_t_plus_1",
            "residual_severity",
            "falsification_condition",
        ]:
            assert prediction[field]


def test_full_e90_chain_reuses_e89_e88_writes_cieustore_and_keeps_gov_mcp_no_send(tmp_path):
    result = run_e90_market_grounded_strategy_session(cieu_db=str(tmp_path / "e90_strategy.db"))
    receipt = result["provider_route"]["gov_mcp_receipt"]

    assert result["intelligence_governance_decision"] == "ALLOW"
    assert result["strategic_benchmark_governance_decision"] == "ALLOW"
    assert result["pre_action_runtime_decision"] == "ALLOW"
    assert result["post_action_runtime_decision"] == "ALLOW"
    assert result["intelligence_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["strategic_benchmark_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["pre_action_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["post_action_CIEU_write"]["formal_CIEU_log_written"] is True
    assert result["CIEUStore_record_summary"]["event_count"] >= 4
    assert result["CIEUStore_record_summary"]["sealed_session_valid"] is True
    assert result["end_to_end_chain_proven"] is True
    assert result["provider_route"]["gov_mcp_dry_run_invoked"] is True
    assert receipt["provider_action_executed"] is False
    assert receipt["external_side_effect"] is False
    assert receipt["no_send_invariant"] is True


def test_l5_status_remains_honest_after_strategy_run(tmp_path):
    result = run_e90_market_grounded_strategy_session(cieu_db=str(tmp_path / "e90_l5.db"))
    l5 = result["L5_truth_table_after"]

    assert l5["L5-A"] == "complete_internal_runtime_foundation"
    assert l5["L5-B"] == "complete_for_structured_governed_intelligence_loop_with_strategy_benchmark"
    assert l5["L5-C"] == "partial_dry_run_only"
    assert l5["L5-D"] == "absent_or_not_executed"
    assert result["safety_statement"]["no_L4_feedback_executed"] is True
    assert result["safety_statement"]["no_revenue_payment_pricing_claim"] is True


def test_reports_are_written_with_required_sections(tmp_path):
    report = write_e90_strategy_reports(cieu_db=str(tmp_path / "e90_report.db"), root=tmp_path)

    benchmark_path = tmp_path / "office/mission_command/e90_ceo_strategic_intelligence_benchmark_report.json"
    strategy_path = tmp_path / "office/mission_command/e90_market_grounded_strategy_run_report.json"
    status_path = tmp_path / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e90_ceo_strategic_intelligence_benchmark.json"
    readback_path = tmp_path / "office/mission_command/e90_market_grounded_strategy_run_readback.md"

    assert benchmark_path.exists()
    assert strategy_path.exists()
    assert status_path.exists()
    assert readback_path.exists()
    strategy_report = json.loads(strategy_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert report["end_to_end_chain_proven"] is True
    assert len(strategy_report["external_evidence_sources"]) >= 8
    assert strategy_report["next_L4_owner_decision_packet"]["no_send_default"] is True
    assert strategy_report["gov_mcp_status"]["provider_action_executed"] is False
    assert strategy_report["gov_mcp_status"]["external_side_effect"] is False
    assert status["L5-D"] == "absent_or_not_executed"
