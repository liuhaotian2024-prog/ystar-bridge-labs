from __future__ import annotations

import json

from office.mission_command.e98_global_money_map_unanchored_strategy import (
    build_global_money_map_strategy_artifact,
    run_e98_global_money_map_strategy,
    write_e98_reports,
)


def test_global_money_map_does_not_privilege_old_agent_governance_route():
    strategy = build_global_money_map_strategy_artifact()
    receipt_route = strategy["global_money_map_scores"]["selected_route_id"]

    assert strategy["anti_recent_memory_anchor"]["capability_blind_first_pass"] is True
    assert strategy["anti_recent_memory_anchor"]["old_agent_governance_route_status"] == "ordinary_candidate_no_privilege"
    assert receipt_route == "tariff_shock_margin_rescue_desk"
    assert strategy["global_money_map_scores"]["old_agent_governance_route_rank"] > 2
    assert strategy["selected_strategy"]["current_best_first_cash_path"] != (
        "Agent Autonomy Flight Recorder readiness sprint for teams moving AI agents from pilot to production"
    )


def test_global_money_map_scores_unrelated_cash_opportunities_before_capability_fit():
    strategy = build_global_money_map_strategy_artifact()
    ranked = strategy["global_money_map_scores"]["ranked_routes"]
    route_ids = [row["route_id"] for row in ranked]

    assert len(route_ids) >= 8
    assert route_ids[0] == "tariff_shock_margin_rescue_desk"
    assert "caregiver_admin_relief_packet" in route_ids
    assert "cpa_review_bottleneck_rescue" in route_ids
    assert "climate_insurance_premium_rescue" in route_ids
    assert "prior_auth_admin_relief" in route_ids
    assert strategy["global_money_map_scores"]["capability_fit_applied_after_market_selection"] is True
    assert strategy["benchmark_result"]["benchmark_decision"] == "ALLOW"
    assert strategy["benchmark_result"]["pass"] is True


def test_e98_writes_formal_cieustore_record_without_external_action(tmp_path):
    result = run_e98_global_money_map_strategy(cieu_db=tmp_path / "e98.db")
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_strategy_record_proven"] is True
    assert receipt["mode"] == "CEO_RUNTIME_CERTIFIED_GLOBAL_MONEY_MAP"
    assert receipt["Y_star_gov_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["selected_route_id"] == "tariff_shock_margin_rescue_desk"
    assert receipt["truth_boundary"]["no_L4_feedback_executed"] is True
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True


def test_e98_reports_state_honest_boundaries(tmp_path):
    result = run_e98_global_money_map_strategy(cieu_db=tmp_path / "e98_report.db")
    paths = write_e98_reports(result, repo_root=tmp_path)

    assert set(paths) == {"report_json", "readback_md", "status_json", "status_md"}
    report = json.loads((tmp_path / "office/mission_command/e98_global_money_map_unanchored_strategy_report.json").read_text())
    status = json.loads(
        (
            tmp_path
            / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e98_global_money_map_unanchored_strategy.json"
        ).read_text()
    )

    assert report["CEO_runtime_receipt"]["selected_route_id"] == "tariff_shock_margin_rescue_desk"
    assert report["anti_recent_memory_anchor"]["capability_blind_first_pass"] is True
    assert "No customer validation" in " ".join(report["what_was_not_claimed"])
    assert status["L5-D"] == "absent_or_not_executed"
    assert status["CEO_runtime_receipt"]["CIEUStore_written"] is True
