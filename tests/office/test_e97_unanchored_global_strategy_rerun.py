from __future__ import annotations

import json

from office.mission_command.e97_unanchored_global_strategy_rerun import (
    build_unanchored_global_strategy_artifact,
    run_e97_unanchored_global_strategy_rerun,
    write_e97_reports,
)


def test_unanchored_strategy_has_no_initial_seed_and_old_route_only_competes():
    strategy = build_unanchored_global_strategy_artifact()

    assert strategy["anti_recent_memory_anchor"]["initial_seed_thesis"] == "none"
    assert strategy["anti_recent_memory_anchor"]["old_thesis_forced_to_compete"] is True
    assert strategy["anti_recent_memory_anchor"]["old_E90_route_status"] == "competitor_only_not_default"
    assert strategy["selected_strategy"]["current_best_first_cash_path"] != (
        "Governed Business Operations Blueprint + CIEU Audit Module for small AI-agent teams"
    )


def test_unanchored_strategy_uses_public_evidence_and_distinct_global_routes():
    strategy = build_unanchored_global_strategy_artifact()
    route_ids = {route["route_id"] for route in strategy["route_candidates"]}

    assert len(strategy["external_market_evidence_map"]["evidence_items"]) >= 8
    assert len(route_ids) >= 8
    assert "agent_autonomy_flight_recorder" in route_ids
    assert "agent_skill_supply_chain_scanner" in route_ids
    assert "eu_ai_act_agent_readiness_pack" in route_ids
    assert "legacy_cieu_audit_module" in route_ids
    assert strategy["benchmark_result"]["benchmark_decision"] == "ALLOW"
    assert strategy["benchmark_result"]["pass"] is True


def test_ceo_runtime_receipt_writes_formal_cieustore_record(tmp_path):
    result = run_e97_unanchored_global_strategy_rerun(cieu_db=tmp_path / "e97.db")
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_strategy_record_proven"] is True
    assert receipt["mode"] == "CEO_RUNTIME_CERTIFIED_STRATEGY_RECORD"
    assert receipt["Y_star_gov_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["CIEU_event_count"] >= 1
    assert "CEO_STRATEGIC_INTELLIGENCE_BENCHMARK_DECISION" in receipt["CIEU_event_types"]
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True


def test_reports_include_receipt_status_and_honest_l5_boundary(tmp_path):
    result = run_e97_unanchored_global_strategy_rerun(cieu_db=tmp_path / "e97_report.db")
    paths = write_e97_reports(result, repo_root=tmp_path)

    for path in paths.values():
        assert path
    report = json.loads((tmp_path / "office/mission_command/e97_unanchored_global_strategy_rerun_report.json").read_text())
    status = json.loads(
        (
            tmp_path
            / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e97_unanchored_global_strategy_rerun.json"
        ).read_text()
    )

    assert report["CEO_runtime_receipt"]["mode"] == "CEO_RUNTIME_CERTIFIED_STRATEGY_RECORD"
    assert report["anti_recent_memory_anchor"]["initial_seed_thesis"] == "none"
    assert status["L5-D"] == "absent_or_not_executed"
    assert status["CEO_runtime_receipt"]["CIEUStore_written"] is True
