from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from l9_meta_development_opportunity_runtime import opportunity_model as model
from l9_meta_development_opportunity_runtime.evidence_basis_builder import build_evidence_basis
from l9_meta_development_opportunity_runtime.execution_plan_generator import build_execution_plan, list_execution_plans
from l9_meta_development_opportunity_runtime.internal_asset_inventory import build_internal_asset_inventory
from l9_meta_development_opportunity_runtime.l8_action_loop_bridge import build_l8_bridge_packet
from l9_meta_development_opportunity_runtime.l9_manifest_builder import build_manifest
from l9_meta_development_opportunity_runtime.meta_development_cockpit import build_meta_cockpit
from l9_meta_development_opportunity_runtime.money_path_generator import generate_money_paths
from l9_meta_development_opportunity_runtime.money_path_model import list_money_paths
from l9_meta_development_opportunity_runtime.opportunity_discovery_engine import discover_opportunities
from l9_meta_development_opportunity_runtime.opportunity_review_center import decide_opportunity
from l9_meta_development_opportunity_runtime.owner_decision_packet import build_owner_decision_packets, list_owner_decision_packets
from l9_meta_development_opportunity_runtime.portfolio_feedback_ingestor import record_portfolio_feedback
from l9_meta_development_opportunity_runtime.portfolio_learning_candidate import build_portfolio_learning_candidate
from l9_meta_development_opportunity_runtime.portfolio_residual import build_portfolio_residual
from l9_meta_development_opportunity_runtime.ranking_engine import build_rankings

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def isolated_l9(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    import l9_meta_development_opportunity_runtime.l9_manifest_builder as manifest_builder

    out = tmp_path / "l9_meta_development_opportunity_runtime"
    packet_root = out / "runtime_packets"
    dirs = {name: packet_root / name for name in model.PACKET_DIRS}
    monkeypatch.setattr(model, "OUT", out)
    monkeypatch.setattr(model, "PACKET_ROOT", packet_root)
    monkeypatch.setattr(model, "PACKET_DIRS", dirs)
    monkeypatch.setattr(manifest_builder, "OUT", out)
    model.ensure_dirs()
    return out


def test_internal_asset_inventory_builds_from_existing_runtime(isolated_l9: Path) -> None:
    inventory = build_internal_asset_inventory()
    titles = {asset["title"] for asset in inventory["assets"]}
    assert "L7.5 Labs Office UI" in titles
    assert "L7.6 Self-Work Scheduler" in titles
    assert "L8 First Cash Path Operating Loop" in titles
    assert inventory["asset_count"] >= 8


def test_opportunity_discovery_generates_multiple_candidates(isolated_l9: Path) -> None:
    result = discover_opportunities(force=True)
    assert len(result["opportunities"]) >= 8
    assert all("Aiden" in opp["generated_by"] for opp in result["opportunities"])


def test_l8_first_cash_path_is_seed_not_only_route(isolated_l9: Path) -> None:
    opportunities = discover_opportunities(force=True)["opportunities"]
    titles = [opp["title"] for opp in opportunities]
    assert any("Founder AI Workflow Audit" in title for title in titles)
    assert len(set(titles)) > 1


def test_no_grant_or_rfp_path_created_by_default(isolated_l9: Path) -> None:
    discover_opportunities(force=True)
    paths = generate_money_paths(force=True)["money_paths"]
    combined = json.dumps(paths, ensure_ascii=False).lower()
    assert "grant/rfp" not in combined
    assert "grant rfp" not in combined


def test_opportunity_categories_are_not_closed_enum(isolated_l9: Path) -> None:
    opportunities = discover_opportunities(force=True)["opportunities"]
    assert all(opp["closed_category_enum"] is False for opp in opportunities)


def test_money_path_generator_creates_paths_for_multiple_opportunities(isolated_l9: Path) -> None:
    paths = generate_money_paths(force=True)["money_paths"]
    assert len(paths) >= 8
    assert len({path["opportunity_id"] for path in paths}) >= 8


def test_money_paths_include_shortest_cash_and_strategic_lenses(isolated_l9: Path) -> None:
    rankings = build_rankings(force=True)["rankings"]
    lenses = {ranking["lens"] for ranking in rankings}
    assert {"shortest_cash", "strategic_long_term", "balanced"}.issubset(lenses)


def test_ranking_engine_builds_multi_lens_rankings(isolated_l9: Path) -> None:
    rankings = build_rankings(force=True)["rankings"]
    assert len(rankings) >= 8
    assert all(ranking["ranked_items"] for ranking in rankings)


def test_ranking_explanations_include_risk_penalties(isolated_l9: Path) -> None:
    rankings = build_rankings(force=True)["rankings"]
    assert all("risk penalties" in ranking["explanation"] for ranking in rankings)
    assert all("risk_penalty" in ranking["ranked_items"][0] for ranking in rankings)


def test_evidence_basis_marks_external_observation_as_optional_controlled(isolated_l9: Path) -> None:
    basis = build_evidence_basis("opp_test", ["local"], "safe local evidence")
    assert basis["external_observation_needed"] == "optional_controlled_read_only_planning_only"
    assert basis["uncontrolled_external_search_run"] is False


def test_owner_decision_packets_are_created_for_top_paths(isolated_l9: Path) -> None:
    packets = build_owner_decision_packets(force=True)["decision_packets"]
    assert packets
    assert {"select_for_execution", "reject", "hold", "request_revision", "request_more_evidence"}.issubset(packets[0]["options"])


def test_review_center_select_for_execution_creates_selected_status(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    decision = decide_opportunity(packet["decision_packet_id"], "select_for_execution")
    assert decision["money_path"]["status"] == "selected_for_execution"


def test_review_center_reject_does_not_create_execution_plan(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    decide_opportunity(packet["decision_packet_id"], "reject")
    assert list_execution_plans() == []
    with pytest.raises(ValueError):
        build_execution_plan(packet["money_path_id"])


def test_review_center_hold_keeps_opportunity_in_portfolio(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    decision = decide_opportunity(packet["decision_packet_id"], "hold")
    assert decision["opportunity"]["current_status"] == "held"


def test_request_revision_creates_revision_needed_status(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    decision = decide_opportunity(packet["decision_packet_id"], "request_revision")
    assert decision["money_path"]["status"] == "revision_needed"


def test_request_more_evidence_does_not_run_uncontrolled_external_search(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    decision = decide_opportunity(packet["decision_packet_id"], "request_more_evidence")
    review = decision["review_decision"]
    assert review["controlled_observation_planning_only"] is True
    assert review["uncontrolled_external_search_run"] is False


def test_execution_plan_generator_builds_manual_send_only_plan(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    selected = decide_opportunity(packet["decision_packet_id"], "select_for_execution")
    plan = build_execution_plan(selected["money_path"]["money_path_id"])
    assert plan["manual_execution_mode"] == "manual_send_only"
    assert plan["required_owner_approval"]


def test_execution_plan_does_not_send_email(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    selected = decide_opportunity(packet["decision_packet_id"], "select_for_execution")
    plan = build_execution_plan(selected["money_path"]["money_path_id"])
    assert plan["tool_send_email_enabled"] is False
    assert plan["email_sent"] is False


def test_l8_bridge_builds_approval_required_manual_send_payload(isolated_l9: Path) -> None:
    packet = build_owner_decision_packets(force=True)["decision_packets"][0]
    selected = decide_opportunity(packet["decision_packet_id"], "select_for_execution")
    plan = build_execution_plan(selected["money_path"]["money_path_id"])
    bridge = build_l8_bridge_packet(plan["execution_plan_id"])
    assert bridge["approval_required"] is True
    assert bridge["manual_send_only"] is True
    assert bridge["commercial_action_payload"]["approval_required"] is True


def test_l8_bridge_supports_non_first_cash_path_opportunity(isolated_l9: Path) -> None:
    packets = build_owner_decision_packets(force=True)["decision_packets"]
    packet = next(item for item in packets if "founder_ai_workflow_audit" not in item["money_path_id"])
    selected = decide_opportunity(packet["decision_packet_id"], "select_for_execution")
    plan = build_execution_plan(selected["money_path"]["money_path_id"])
    bridge = build_l8_bridge_packet(plan["execution_plan_id"])
    assert "founder_ai_workflow_audit" not in bridge["money_path_id"]


def test_portfolio_residual_builds_from_signal_gap(isolated_l9: Path) -> None:
    path = generate_money_paths(force=True)["money_paths"][0]
    feedback = record_portfolio_feedback(path["money_path_id"], "no_signal", "No response in local demo.")
    residual = build_portfolio_residual(feedback["feedback_id"])
    assert residual["residual_type"] == "no_signal"


def test_portfolio_learning_candidate_is_review_gated(isolated_l9: Path) -> None:
    path = generate_money_paths(force=True)["money_paths"][0]
    feedback = record_portfolio_feedback(path["money_path_id"], "positive_signal", "Promising local demo signal.")
    residual = build_portfolio_residual(feedback["feedback_id"])
    candidate = build_portfolio_learning_candidate(residual["residual_id"])
    assert candidate["review_required"] is True
    assert candidate["owner_review_status"] == "pending_review"


def test_learning_candidate_does_not_write_core_memory(isolated_l9: Path) -> None:
    path = generate_money_paths(force=True)["money_paths"][0]
    feedback = record_portfolio_feedback(path["money_path_id"], "capability_gap", "Needs a tool.")
    residual = build_portfolio_residual(feedback["feedback_id"])
    candidate = build_portfolio_learning_candidate(residual["residual_id"])
    assert candidate["writeback_allowed"] is False
    assert candidate["core_writeback"] is False


def test_meta_cockpit_snapshot_contains_portfolio_and_rankings(isolated_l9: Path) -> None:
    build_manifest(force=True)
    cockpit = build_meta_cockpit()
    assert len(cockpit["opportunity_candidates"]) >= 8
    assert len(cockpit["rankings_by_lens"]) >= 8
    assert cockpit["grant_rfp_default_path_status"] == "no"


def test_l9_api_assets_build() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l9/assets/build" in source


def test_l9_api_opportunities_discover() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l9/opportunities/discover" in source


def test_l9_api_money_paths_generate() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l9/money_paths/generate" in source


def test_l9_api_rankings_build() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l9/rankings/build" in source


def test_l9_api_review_decision_select() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l9/opportunity_reviews/decide" in source
    assert "decide_opportunity" in source


def test_l9_api_execution_plan_and_l8_bridge() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l9/execution_plans/build" in source
    assert "/api/l9/l8_bridge/build" in source


def test_runner_build_status_demo_smoke() -> None:
    runner = ROOT / "scripts/run_l7_labs_office_web.sh"
    result = subprocess.run(["bash", "-n", str(runner)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    source = runner.read_text(encoding="utf-8")
    assert "l9_manifest_opportunities" in source
    assert "--mode build|serve|status|smoke|demo" in source


def test_no_external_side_effects(isolated_l9: Path) -> None:
    receipt = model.no_action_receipt()
    assert receipt["automatic_customer_contact"] is False
    assert receipt["uncontrolled_web_search_crawl_occurred"] is False


def test_no_customer_contact(isolated_l9: Path) -> None:
    assert build_manifest(force=True)["customer_contact"] is False


def test_no_email_sent(isolated_l9: Path) -> None:
    assert build_manifest(force=True)["email_sent"] is False


def test_no_payment_created(isolated_l9: Path) -> None:
    assert build_manifest(force=True)["payment_processed"] is False


def test_no_publication(isolated_l9: Path) -> None:
    assert build_manifest(force=True)["publication"] is False


def test_no_coo_invented(isolated_l9: Path) -> None:
    manifest = build_manifest(force=True)
    assert manifest["coo_invented"] is False
    assert "operator/coo" not in json.dumps(manifest, ensure_ascii=False).lower()


def test_existing_l8_loop_still_works() -> None:
    assert (ROOT / "l8_first_cash_path_operating_loop/l8_summary.json").exists()
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l8/cockpit" in source


def test_existing_l7_scheduler_still_works() -> None:
    assert (ROOT / "l7_labs_team_self_work_scheduler/l7_6_summary.json").exists()
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/scheduler/run_bounded" in source


def test_existing_l7_office_apis_still_work() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/whiteboard/message" in source
    assert "/api/team_work_cycle" in source
