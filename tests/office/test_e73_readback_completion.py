import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e73_ecosystem_boundary_lock import build_completion_report
from office.mission_command.e73_readback import get_owner_readable_closure_report, run_e73_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def test_e73_owner_closure_report_answers_real_work_question():
    report = get_owner_readable_closure_report()

    assert "can start real internal work now at L2" in report["direct_answer"]
    assert report["highest_ready_CEO_work_level"] == "L2_internal_autonomous_work_ready"
    assert report["exact_next_milestone"] == "E74_CEO_L2_Internal_Autonomous_Work_Pilot"
    assert report["next_milestone_type"] == "real_internal_work"
    assert report["external_action_allowed"] is False
    assert report["read_only_repos_mutated"] is False


def test_e73_ceo_brain_adapter_exposes_boundary_lock_state():
    assert run_e73_readback_smoke()["passes"] is True
    context = load_ceo_brain_context({"task_title": "e73 readback", "task_description": "real work readiness"})

    assert context["current_ceo_real_work_highest_ready_level"] == "L2_internal_autonomous_work_ready"
    assert context["current_ceo_L2_readiness_decision"] == "ready"
    assert context["current_ceo_L3_readiness_decision"] == "conditionally_ready"
    assert context["current_ceo_L4_readiness_decision"] == "not_ready"
    assert context["current_ceo_L5_readiness_decision"] == "not_ready"
    assert context["current_ceo_real_work_next_recommended_milestone"] == "E74_CEO_L2_Internal_Autonomous_Work_Pilot"
    assert context["current_ceo_real_work_external_action_allowed"] is False


def test_e73_completion_report_and_no_overclaim_flags_pass():
    completion = build_completion_report()
    no_overclaim = json.loads((ROOT / "operations/external_validation/e73_no_overclaim_validation_result.json").read_text())

    assert completion["gate_passed"] is True
    assert completion["read_only_repo_status_unchanged"] is True
    assert completion["external_action_allowed"] is False
    assert completion["customer_validation_claimed"] is False
    assert completion["paid_signal_claimed"] is False
    assert completion["compliance_legal_claimed"] is False
    assert completion["production_deployment_claimed"] is False
    assert no_overclaim["passed"] is True
    assert no_overclaim["live_external_action_claimed"] is False
    assert no_overclaim["live_ledger_claimed"] is False
