from pathlib import Path

from office.mission_command.evidence_gated_money_plan import build_evidence_gated_money_plan
from office.mission_command.internal_world_scan import build_internal_world_scan
from office.mission_command.mission_summary import build_mission_summary
from office.mission_command.research_capability import audit_research_capability


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_internal_research_capability_detected():
    audit = audit_research_capability(REPO_ROOT)
    assert audit.internal_research_verdict == "INTERNAL_RESEARCH_READY"
    assert audit.internal_capability["directive_retriage_loaded"] is True
    assert audit.internal_capability["scannable_dirs"]["sales"] is True


def test_external_research_architecture_only_is_not_treated_as_live_evidence():
    audit = audit_research_capability(REPO_ROOT)
    assert audit.external_research_verdict in {"ARCHITECTURE_ONLY", "FIXTURE_ONLY", "NOT_READY"}
    assert audit.plan_confidence_allowed != "evidence_backed_live_read_only"
    assert audit.external_capability["live_research_executed"] is False


def test_money_plan_marks_internal_only_confidence_when_live_research_disabled():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert plan["evidence_status"]["confidence_level"] == "internal_only_preliminary"
    summary = build_mission_summary("Aiden，带团队制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert "Evidence mode: internal-evidence preliminary plan" in summary


def test_money_plan_compares_multiple_paths_not_only_founder_audit():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    paths = {item["path"] for item in plan["top_money_paths"]}
    assert "Founder AI Workflow Audit / CEO Command Brief" in paths
    assert "AI Company Cockpit Setup" in paths
    assert "Coding-Agent Governance Audit" in paths
    assert len(paths) >= 6


def test_money_plan_has_default_recommendation():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert plan["default_recommendation"]["path"]
    assert "internal-only" in plan["default_recommendation"]["reason"]


def test_money_plan_lists_approval_needed_actions():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    actions = " ".join(plan["approval_needed_actions"])
    assert "contact" in actions
    assert "email" in actions
    assert "publish" in actions
    assert "payment" in actions
    assert "core DB" in actions


def test_internal_world_scan_maps_assets_to_money_paths():
    scan = build_internal_world_scan(REPO_ROOT)
    assert scan["internal_assets"]
    assert scan["money_paths"]
    assert scan["old_commercial_assets"]


def test_no_external_side_effects():
    audit = audit_research_capability(REPO_ROOT)
    assert audit.external_capability["live_research_executed"] is False


def test_no_customer_contact():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert "contact a customer" in plan["approval_needed_actions"]


def test_no_email():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert "send email/message" in plan["approval_needed_actions"]


def test_no_publication():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert "publish content" in plan["approval_needed_actions"]


def test_no_payment():
    plan = build_evidence_gated_money_plan(REPO_ROOT)
    assert "create payment link or process payment" in plan["approval_needed_actions"]

