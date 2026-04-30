from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from l10_delegated_live_meta_development_runtime import mission_model as model
from l10_delegated_live_meta_development_runtime.action_plan_builder import build_action_plan
from l10_delegated_live_meta_development_runtime.conflict_detector import build_conflict_report
from l10_delegated_live_meta_development_runtime.controlled_research_executor import run_configured_live_read_only, run_fixture_research_demo
from l10_delegated_live_meta_development_runtime.controlled_research_planner import build_research_plan
from l10_delegated_live_meta_development_runtime.escalation_packet_builder import build_escalation_packets
from l10_delegated_live_meta_development_runtime.escalation_review_center import decide_escalation
from l10_delegated_live_meta_development_runtime.l8_action_loop_escalation_bridge import build_l8_action_loop_escalation_packet
from l10_delegated_live_meta_development_runtime.l9_portfolio_update_bridge import build_l9_portfolio_update_packet
from l10_delegated_live_meta_development_runtime.l10_manifest_builder import build_manifest
from l10_delegated_live_meta_development_runtime.meta_strategy_brief_builder import build_meta_strategy_brief
from l10_delegated_live_meta_development_runtime.mission_cockpit_model import build_mission_cockpit
from l10_delegated_live_meta_development_runtime.mission_completion_report import build_mission_completion_report
from l10_delegated_live_meta_development_runtime.mission_delegation_center import create_default_mission, create_mission
from l10_delegated_live_meta_development_runtime.mission_plan_builder import build_mission_plan
from l10_delegated_live_meta_development_runtime.mission_runner import run_bounded_mission, run_mission_cycle
from l10_delegated_live_meta_development_runtime.opportunity_signal_extractor import extract_opportunity_signals
from l10_delegated_live_meta_development_runtime.permission_tiers import is_action_allowed, permission_tier_registry
from l10_delegated_live_meta_development_runtime.source_summary_builder import build_source_summary

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def isolated_l10(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    import l10_delegated_live_meta_development_runtime.l10_manifest_builder as manifest_builder

    out = tmp_path / "l10_delegated_live_meta_development_runtime"
    packet_root = out / "runtime_packets"
    dirs = {name: packet_root / name for name in model.PACKET_DIRS}
    monkeypatch.setattr(model, "OUT", out)
    monkeypatch.setattr(model, "PACKET_ROOT", packet_root)
    monkeypatch.setattr(model, "PACKET_DIRS", dirs)
    monkeypatch.setattr(manifest_builder, "OUT", out)
    model.ensure_dirs()
    return out


def test_permission_tier_registry_contains_tier0_to_tier4(isolated_l10: Path) -> None:
    registry = permission_tier_registry()
    assert {tier["tier_id"] for tier in registry["tiers"]} == {"tier_0", "tier_1", "tier_2", "tier_3", "tier_4"}


def test_tier1_allows_read_only_research_with_budget(isolated_l10: Path) -> None:
    decision = is_action_allowed("tier_1", "budgeted_read_only_research", budget_attached=True)
    assert decision["allowed"] is True


def test_tier1_blocks_contact_submit_payment_publication(isolated_l10: Path) -> None:
    for action in ["customer_contact", "form_submission", "payment", "publication"]:
        decision = is_action_allowed("tier_1", action, budget_attached=True)
        assert decision["allowed"] is False
        assert decision["requires_escalation"] is True


def test_mission_delegation_center_creates_default_meta_mission(isolated_l10: Path) -> None:
    mission = create_default_mission()
    assert mission["mission_type"] == "meta_development_strategy"
    assert mission["allowed_permission_tier"] == "tier_1"


def test_custom_mission_can_set_permission_tier_and_budget(isolated_l10: Path) -> None:
    mission = create_mission("Custom Labs plan", "Analyze money paths", allowed_permission_tier="tier_0")
    assert mission["allowed_permission_tier"] == "tier_0"
    assert mission["research_budget_id"].startswith("research_budget_")


def test_research_budget_defaults_are_bounded(isolated_l10: Path) -> None:
    mission = create_default_mission()
    budget = model.get_packet("research_budget_receipts", mission["research_budget_id"])
    assert budget["max_search_queries"] == 20
    assert budget["max_pages_read"] == 40
    assert budget["max_domains"] == 15
    assert budget["no_contact"] is True


def test_mission_plan_builder_assigns_existing_legacy_agents_only(isolated_l10: Path) -> None:
    mission = create_default_mission()
    plan = build_mission_plan(mission["mission_id"])
    assert set(plan["assigned_agents"]).issubset(model.LEGACY_AGENT_IDS)


def test_no_coo_invented(isolated_l10: Path) -> None:
    manifest = build_manifest(force=True)
    assert manifest["coo_invented"] is False
    assert "operator/coo" not in json.dumps(manifest, ensure_ascii=False).lower()


def test_mission_runner_builds_team_tasks(isolated_l10: Path) -> None:
    mission = create_default_mission()
    build_mission_plan(mission["mission_id"])
    tasks = model.load_packets("mission_team_tasks")
    assert len(tasks) >= 8


def test_mission_runner_respects_cycle_limit(isolated_l10: Path) -> None:
    mission = create_default_mission()
    result = run_mission_cycle(mission["mission_id"], max_cycles=0)
    assert result["stopped_reason"] == "cycle_limit_reached"


def test_mission_runner_stops_on_forbidden_action(isolated_l10: Path) -> None:
    mission = create_mission("Bad mission", "Please email send a customer", allowed_permission_tier="tier_1")
    result = run_bounded_mission(mission["mission_id"])
    assert result["ok"] is False
    assert result["stopped_reason"] == "forbidden_action_requested"


def test_research_plan_builder_creates_bounded_queries(isolated_l10: Path) -> None:
    mission = create_default_mission()
    plan = build_research_plan(mission["mission_id"])
    assert 1 <= len(plan["search_queries"]) <= 20
    assert "budget_id" in plan


def test_fixture_research_demo_writes_evidence_packets(isolated_l10: Path) -> None:
    mission = create_default_mission()
    result = run_fixture_research_demo(mission["mission_id"])
    assert result["mode"] == "fixture_demo"
    assert len(result["evidence_packets"]) >= 3


def test_configured_live_read_only_is_disabled_unless_explicitly_enabled(isolated_l10: Path) -> None:
    mission = create_default_mission()
    result = run_configured_live_read_only(mission["mission_id"], explicitly_enabled=False)
    assert result["configured_live_read_only_executed"] is False
    assert result["budget_receipt"]["external_observation_executed"] is False


def test_research_budget_receipt_tracks_queries_pages_domains(isolated_l10: Path) -> None:
    mission = create_default_mission()
    receipt = run_fixture_research_demo(mission["mission_id"])["budget_receipt"]
    assert {"queries_used", "pages_read", "domains_used"}.issubset(receipt)


def test_evidence_packet_does_not_include_secret_or_private_content(isolated_l10: Path) -> None:
    mission = create_default_mission()
    evidence = run_fixture_research_demo(mission["mission_id"])["evidence_packets"]
    text = json.dumps(evidence, ensure_ascii=False).lower()
    assert "api_key" not in text
    assert "password" not in text


def test_source_summary_builder_creates_opportunity_implications(isolated_l10: Path) -> None:
    mission = create_default_mission()
    run_fixture_research_demo(mission["mission_id"])
    summary = build_source_summary(mission["mission_id"])
    assert summary["opportunity_implications"]


def test_conflict_detector_builds_conflict_report(isolated_l10: Path) -> None:
    mission = create_default_mission()
    run_fixture_research_demo(mission["mission_id"])
    conflict = build_conflict_report(mission["mission_id"])
    assert conflict["severity"] == "medium"


def test_opportunity_signal_extractor_builds_signals(isolated_l10: Path) -> None:
    mission = create_default_mission()
    run_fixture_research_demo(mission["mission_id"])
    signals = extract_opportunity_signals(mission["mission_id"])
    assert len(signals) >= 3


def test_meta_strategy_brief_contains_top_opportunities(isolated_l10: Path) -> None:
    mission = create_default_mission()
    run_fixture_research_demo(mission["mission_id"])
    extract_opportunity_signals(mission["mission_id"])
    brief = build_meta_strategy_brief(mission["mission_id"])
    assert brief["top_opportunities"]


def test_meta_strategy_brief_contains_shortest_cash_and_strategic_recommendations(isolated_l10: Path) -> None:
    mission = create_default_mission()
    brief = build_meta_strategy_brief(mission["mission_id"])
    assert brief["shortest_cash_recommendation"]
    assert brief["strategic_recommendation"]


def test_action_plan_separates_autonomous_and_approval_required_actions(isolated_l10: Path) -> None:
    mission = create_default_mission()
    plan = build_action_plan(mission["mission_id"])
    assert plan["autonomous_actions"]
    assert "contact customer" in plan["approval_required_actions"]


def test_escalation_packet_created_for_external_side_effect_action(isolated_l10: Path) -> None:
    mission = create_default_mission()
    packets = build_escalation_packets(mission["mission_id"])
    assert any(packet["action_class"] == "customer_contact" for packet in packets)


def test_escalation_review_center_approve_reject_revision_hold(isolated_l10: Path) -> None:
    mission = create_default_mission()
    escalation = build_escalation_packets(mission["mission_id"])[0]
    for decision in ["approve", "reject", "request_revision", "hold"]:
        packet = decide_escalation(escalation["escalation_id"], decision)
        assert packet["decision"] == decision


def test_escalation_approval_does_not_execute_action_in_l10(isolated_l10: Path) -> None:
    mission = create_default_mission()
    escalation = build_escalation_packets(mission["mission_id"])[0]
    decision = decide_escalation(escalation["escalation_id"], "approve")
    assert decision["external_action_executed"] is False


def test_l9_portfolio_update_packet_created_from_mission_outputs(isolated_l10: Path) -> None:
    mission = create_default_mission()
    run_fixture_research_demo(mission["mission_id"])
    extract_opportunity_signals(mission["mission_id"])
    packet = build_l9_portfolio_update_packet(mission["mission_id"])
    assert packet["review_required"] is True


def test_l8_action_loop_escalation_packet_is_manual_send_only(isolated_l10: Path) -> None:
    mission = create_default_mission()
    build_escalation_packets(mission["mission_id"])
    packet = build_l8_action_loop_escalation_packet(mission["mission_id"])
    assert packet["manual_send_only"] is True
    assert packet["tool_send_email_enabled"] is False


def test_mission_completion_report_contains_deliverables_and_next_mission(isolated_l10: Path) -> None:
    mission = create_default_mission()
    report = build_mission_completion_report(mission["mission_id"])
    assert report["deliverables"]
    assert report["next_recommended_mission"]


def test_cockpit_snapshot_contains_mission_progress_and_escalations(isolated_l10: Path) -> None:
    mission = create_default_mission()
    run_bounded_mission(mission["mission_id"])
    cockpit = build_mission_cockpit()
    assert cockpit["mission_progress"]
    assert cockpit["escalation_packets"]


def test_l10_api_create_default_mission() -> None:
    assert "/api/l10/missions/create_default" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_l10_api_build_mission_plan() -> None:
    assert "/api/l10/mission_plan/build" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_l10_api_run_fixture_research_demo() -> None:
    assert "/api/l10/research/run_fixture_demo" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_l10_api_build_strategy_brief_and_escalations() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l10/meta_strategy_brief/build" in source
    assert "/api/l10/escalations/build" in source


def test_l10_api_escalation_decision() -> None:
    assert "/api/l10/escalations/decide" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_runner_build_status_demo_smoke() -> None:
    runner = ROOT / "scripts/run_l7_labs_office_web.sh"
    result = subprocess.run(["bash", "-n", str(runner)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    source = runner.read_text(encoding="utf-8")
    assert "l10_manifest_missions" in source
    assert "L10 Delegated Mission Cockpit" in (ROOT / "l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")


def test_no_external_side_effects_in_demo(isolated_l10: Path) -> None:
    result = run_bounded_mission(create_default_mission()["mission_id"])
    assert result["ok"] is True
    assert result["mission_completion_report"]["external_side_effects"] is False


def test_no_customer_contact(isolated_l10: Path) -> None:
    assert build_manifest(force=True)["customer_contact"] is False


def test_no_email_sent(isolated_l10: Path) -> None:
    assert build_manifest(force=True)["email_sent"] is False


def test_no_payment_processed(isolated_l10: Path) -> None:
    assert build_manifest(force=True)["payment_processed"] is False


def test_no_publication(isolated_l10: Path) -> None:
    assert build_manifest(force=True)["publication"] is False


def test_no_core_writeback(isolated_l10: Path) -> None:
    assert build_manifest(force=True)["core_writeback"] is False


def test_existing_l9_meta_runtime_still_works() -> None:
    assert (ROOT / "l9_meta_development_opportunity_runtime/l9_summary.json").exists()
    assert "/api/l9/meta/cockpit" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_existing_l8_loop_still_works() -> None:
    assert (ROOT / "l8_first_cash_path_operating_loop/l8_summary.json").exists()
    assert "/api/l8/cockpit" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_existing_l7_scheduler_still_works() -> None:
    assert (ROOT / "l7_labs_team_self_work_scheduler/l7_6_summary.json").exists()
    assert "/api/scheduler/run_bounded" in (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")


def test_existing_l7_office_apis_still_work() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/whiteboard/message" in source
    assert "/api/team_work_cycle" in source
