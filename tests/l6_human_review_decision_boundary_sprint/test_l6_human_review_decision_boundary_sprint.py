from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_human_review_decision_boundary_sprint",
    "human_review_packet",
    "evidence_usability_assessment",
    "bounded_conflict_interpretation",
    "planning_eligibility_matrix",
    "governed_planning_candidates",
    "decision_boundary_packet",
    "human_approval_gate",
    "residual_risk_register",
    "l6_15_no_action_receipts",
    "l6_15_read_model",
]

REQUIRED_JSON = [
    "l6_human_review_decision_boundary_sprint/l6_15_milestone_contract.json",
    "l6_human_review_decision_boundary_sprint/l6_15_summary.json",
    "human_review_packet/l6_15_human_review_packet.json",
    "evidence_usability_assessment/evidence_usability_assessment.json",
    "bounded_conflict_interpretation/bounded_conflict_interpretation_packet.json",
    "planning_eligibility_matrix/planning_eligibility_matrix.json",
    "governed_planning_candidates/governed_planning_candidates.json",
    "decision_boundary_packet/decision_boundary_packet.json",
    "human_approval_gate/human_approval_gate_spec.json",
    "residual_risk_register/residual_risk_register.json",
    "l6_15_no_action_receipts/no_side_effect_receipt.json",
    "l6_15_read_model/l6_15_read_model_summary.json",
    "console_read_model/generated/l6_15_human_review_decision_boundary_sprint_summary.json",
]

FORBIDDEN_FLAGS = [
    "ask_user_for_url_authorized",
    "login_authorized",
    "account_creation_authorized",
    "payment_authorized",
    "checkout_authorized",
    "form_submission_authorized",
    "posting_authorized",
    "commenting_authorized",
    "messaging_authorized",
    "publication_authorized",
    "outreach_authorized",
    "grant_rfp_bounty_submission_authorized",
    "revenue_execution_authorized",
    "mcp_execution_authorized",
    "live_behavior_authorized",
    "cieu_db_write_authorized",
    "canonical_update_authorized",
    "brain_writeback_authorized",
    "memory_ingestion_authorized",
    "direct_y_star_mutation_authorized",
    "artifact_refinement_application_authorized",
]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_l6_15_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_15_and_forbids_external_side_effects() -> None:
    contract = load("l6_human_review_decision_boundary_sprint/l6_15_milestone_contract.json")
    assert contract["milestone_id"] == "L6.15"
    assert contract["input_milestones"][-1] == "L6.14"
    assert contract["mode"] == "human_review_decision_boundary_sprint"
    assert contract["selected_work_order_id"] == "l6_10x_selected_work_order_001"
    assert contract["human_review_packet_authorized"] is True
    assert contract["decision_boundary_packet_authorized"] is True
    assert contract["new_external_observation_authorized_by_default"] is False
    assert contract["external_action_authorized"] is False
    assert contract["core_writeback_authorized"] is False
    for field in FORBIDDEN_FLAGS:
        assert contract[field] is False, field


def test_builder_ingests_l6_14_fixture_report_and_statuses_are_deterministic() -> None:
    builder = load_module(
        "l6_15_builder",
        "l6_human_review_decision_boundary_sprint/tools/build_l6_human_review_decision_boundary_sprint.py",
    )
    inputs = builder.load_inputs()
    assert not inputs["missing"]
    assert inputs["l6_14_summary"]["post_second_pass_classification"] == "conflict_bounded"
    summary = load("l6_15_read_model/l6_15_read_model_summary.json")
    assert summary["prior_classification"] == "real_evidence_collected_with_unresolved_conflicts"
    assert summary["l6_14_conflict_status"] == "bounded_conflict"
    assert summary["l6_15_review_status"] == "human_review_ready_with_bounded_conflict"


def test_human_review_packet_is_generated_for_non_engineering_review() -> None:
    packet = load("human_review_packet/l6_15_human_review_packet.json")
    markdown = (ROOT / "human_review_packet/l6_15_human_review_packet.md").read_text()
    assert packet["review_status"] == "human_review_ready_with_bounded_conflict"
    assert packet["executive_summary"]
    assert packet["what_was_observed"]
    assert packet["why_conflict_is_bounded"]
    assert packet["responsible_planning_use"]
    assert packet["must_not_use_as_settled_truth"]
    assert packet["recommended_decision_options"]
    assert "Executive Summary" in markdown
    assert "Must Not Be Used As Settled Truth" in markdown


def test_evidence_usability_assessment_buckets_claims() -> None:
    assessment = load("evidence_usability_assessment/evidence_usability_assessment.json")
    summary = load("l6_15_read_model/l6_15_read_model_summary.json")
    allowed = set(assessment["allowed_planning_eligibility"])
    assert assessment["assessments"]
    assert {item["planning_eligibility"] for item in assessment["assessments"]} <= allowed
    assert summary["caveated_claims"] >= 1
    assert summary["human_review_required_claims"] >= 1


def test_bounded_conflict_interpretation_explains_permitted_and_blocked_decisions() -> None:
    packet = load("bounded_conflict_interpretation/bounded_conflict_interpretation_packet.json")
    assert packet["bounded_conflict_count"] >= 1
    conflict = packet["bounded_conflicts"][0]
    assert conflict["what_is_bounded"]
    assert conflict["what_is_not_resolved"]
    assert "external publication" in conflict["what_decision_types_it_blocks"]
    assert "internal analysis only" in conflict["what_decision_types_it_permits"]
    assert conflict["recommended_human_question"]


def test_planning_eligibility_matrix_blocks_external_action_and_core_writeback() -> None:
    matrix = load("planning_eligibility_matrix/planning_eligibility_matrix.json")["matrix"]
    categories = {item["category"]: item for item in matrix}
    assert categories["internal_analysis_only"]["allowed_or_blocked"] == "allowed"
    assert categories["blocked_external_side_effect"]["allowed_or_blocked"] == "blocked"
    assert categories["blocked_core_writeback"]["allowed_or_blocked"] == "blocked"
    forbidden = set(categories["blocked_external_side_effect"]["forbidden_actions"])
    for action in [
        "outreach",
        "publication",
        "payment",
        "account_creation",
        "grant_rfp_bounty_submission",
        "customer_contact",
        "external_posting",
    ]:
        assert action in forbidden
    core_forbidden = set(categories["blocked_core_writeback"]["forbidden_actions"])
    for action in ["cieu_db_write", "brain_memory_writeback", "canonical_strategy_mutation", "direct_y_star_mutation"]:
        assert action in core_forbidden


def test_governed_planning_candidates_are_internal_or_review_gated() -> None:
    candidates = load("governed_planning_candidates/governed_planning_candidates.json")["candidates"]
    assert len(candidates) >= 3
    assert any(candidate["next_safe_step"] == "draft internal strategy memo" for candidate in candidates)
    assert any(candidate["next_safe_step"] == "run third-pass read-only observation" for candidate in candidates)
    for candidate in candidates:
        assert "external sending" in candidate["forbidden_scope"]
        assert candidate["required_human_approval"]


def test_decision_boundary_packet_answers_core_questions_and_no_writeback() -> None:
    packet = load("decision_boundary_packet/decision_boundary_packet.json")
    assert packet["what_system_can_conclude"]
    assert packet["what_system_cannot_conclude"]
    assert packet["usable_for_internal_planning"]
    assert packet["needs_human_review"]
    assert "outreach" in packet["actions_remain_forbidden"]
    assert packet["required_to_unlock_external_action"]
    assert packet["required_to_unlock_core_writeback"]
    assert packet["writeback_performed_in_l6_15"] is False


def test_human_approval_gate_spec_defaults_to_blocked_until_approved() -> None:
    gates = load("human_approval_gate/human_approval_gate_spec.json")["gates"]
    action_types = {gate["action_type"] for gate in gates}
    for action in [
        "third_pass_observation",
        "internal_strategy_draft",
        "external_publication",
        "customer_outreach",
        "funding_grant_application",
        "core_memory_brain_writeback",
        "canonical_strategy_update",
        "mcp_live_behavior",
    ]:
        assert action in action_types
    assert all(gate["default_decision"] == "blocked_until_approved" for gate in gates)


def test_residual_risk_register_marks_external_and_core_blocks() -> None:
    risks = load("residual_risk_register/residual_risk_register.json")["risks"]
    assert risks
    assert any(risk["risk_id"] == "l6_15_risk_bounded_conflict_not_settled_truth" for risk in risks)
    assert all("blocks_external_action" in risk for risk in risks)
    assert all("blocks_core_writeback" in risk for risk in risks)


def test_no_action_receipt_covers_forbidden_actions_and_no_url_path() -> None:
    receipt = load("l6_15_no_action_receipts/no_side_effect_receipt.json")
    assert receipt["new_external_search_performed"] is False
    assert receipt["ask_user_for_url_occurred"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False
    assert receipt["secret_values_serialized"] is False
    for action in [
        "login",
        "account_creation",
        "payment",
        "checkout",
        "form_submission",
        "posting",
        "commenting",
        "messaging",
        "email_customer_outreach",
        "publication",
        "grant_rfp_bounty_submission",
        "revenue_execution",
        "mcp_execution",
        "live_behavior",
        "cieu_db_write",
        "brain_memory_writeback",
        "canonical_strategy_mutation",
        "direct_y_star_mutation",
        "ask_user_url",
    ]:
        assert receipt[f"{action}_occurred"] is False


def test_read_model_summary_and_console_command_work() -> None:
    summary = load("console_read_model/generated/l6_15_human_review_decision_boundary_sprint_summary.json")
    assert summary["l6_15_review_status"] == "human_review_ready_with_bounded_conflict"
    assert summary["external_side_effects_occurred"] is False
    assert summary["core_writeback_occurred"] is False
    result = subprocess.run(
        [sys.executable, "console_read_model/cli/team_console.py", "human-review-decision-boundary-sprint"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.15 Human Review Decision Boundary Sprint" in result.stdout
    assert "ask-user-URL occurred: False" in result.stdout

