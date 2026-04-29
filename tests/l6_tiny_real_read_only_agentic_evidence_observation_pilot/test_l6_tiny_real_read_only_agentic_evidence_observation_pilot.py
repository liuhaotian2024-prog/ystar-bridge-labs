from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot",
    "tiny_observation_work_order_selector",
    "tiny_observation_execution_packet",
    "tiny_observation_runtime_guard",
    "tiny_source_locator_resolution",
    "tiny_real_read_only_observation_trace",
    "tiny_evidence_capture_packet",
    "tiny_evidence_structural_validation",
    "tiny_claim_boundary_and_freshness_assessment",
    "tiny_post_observation_review_packet",
    "tiny_artifact_refinement_candidate",
    "tiny_observation_abort_and_quarantine",
    "tiny_observation_no_action_receipts",
    "l6_tiny_observation_strategic_residual_loop",
    "l6_tiny_observation_readiness_report",
]

REQUIRED_JSON = [
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_milestone_contract.json",
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_scope.json",
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_safety_flags.json",
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_runtime_limits.json",
    "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_summary.json",
    "tiny_observation_work_order_selector/l6_9_work_order_inventory.json",
    "tiny_observation_work_order_selector/tiny_observation_selection_matrix.json",
    "tiny_observation_work_order_selector/selected_tiny_observation_work_order.json",
    "tiny_observation_work_order_selector/deferred_tiny_observation_work_orders.json",
    "tiny_observation_execution_packet/tiny_observation_execution_packet_schema.json",
    "tiny_observation_execution_packet/tiny_observation_execution_packet.json",
    "tiny_observation_execution_packet/tiny_observation_pre_run_checklist.json",
    "tiny_observation_runtime_guard/runtime_guard_contract.json",
    "tiny_observation_runtime_guard/runtime_guard_limits.json",
    "tiny_observation_runtime_guard/prohibited_runtime_actions.json",
    "tiny_observation_runtime_guard/runtime_abort_conditions.json",
    "tiny_source_locator_resolution/source_locator_resolution_contract.json",
    "tiny_source_locator_resolution/source_locator_resolution_result.json",
    "tiny_source_locator_resolution/source_locator_resolution_trace.json",
    "tiny_real_read_only_observation_trace/observation_trace_schema.json",
    "tiny_real_read_only_observation_trace/tiny_observation_trace.json",
    "tiny_evidence_capture_packet/evidence_capture_schema.json",
    "tiny_evidence_capture_packet/tiny_evidence_packet.json",
    "tiny_evidence_capture_packet/citation_trace.json",
    "tiny_evidence_structural_validation/evidence_validation_contract.json",
    "tiny_evidence_structural_validation/evidence_validation_matrix.json",
    "tiny_evidence_structural_validation/evidence_validation_result.json",
    "tiny_claim_boundary_and_freshness_assessment/claim_boundary_assessment_schema.json",
    "tiny_claim_boundary_and_freshness_assessment/bounded_claim_registry.json",
    "tiny_claim_boundary_and_freshness_assessment/freshness_assessment.json",
    "tiny_claim_boundary_and_freshness_assessment/unsupported_inference_registry.json",
    "tiny_post_observation_review_packet/post_observation_review_packet_schema.json",
    "tiny_post_observation_review_packet/tiny_post_observation_review_packet.json",
    "tiny_artifact_refinement_candidate/artifact_refinement_candidate_schema.json",
    "tiny_artifact_refinement_candidate/tiny_artifact_refinement_candidate.json",
    "tiny_observation_abort_and_quarantine/abort_policy.json",
    "tiny_observation_abort_and_quarantine/quarantine_policy.json",
    "tiny_observation_abort_and_quarantine/abort_or_quarantine_decision.json",
    "l6_tiny_observation_strategic_residual_loop/l6_10_cieu_like_fixture.json",
    "l6_tiny_observation_strategic_residual_loop/l6_10_strategic_residual_delta.json",
    "l6_tiny_observation_strategic_residual_loop/l6_10_meta_learning_update_candidate.json",
    "l6_tiny_observation_readiness_report/l6_10_readiness_assessment.json",
    "l6_tiny_observation_readiness_report/l6_10_next_milestone_recommendation.json",
    "l6_tiny_observation_readiness_report/l6_10_blockers.json",
    "console_read_model/generated/l6_tiny_observation_pilot_summary.json",
]

RECEIPTS = [
    "no_crawling_receipt.json",
    "no_scraping_receipt.json",
    "no_browser_automation_receipt.json",
    "no_login_receipt.json",
    "no_account_creation_receipt.json",
    "no_payment_receipt.json",
    "no_form_submission_receipt.json",
    "no_posting_commenting_messaging_receipt.json",
    "no_publication_receipt.json",
    "no_outreach_receipt.json",
    "no_revenue_execution_receipt.json",
    "no_mcp_execution_receipt.json",
    "no_live_behavior_receipt.json",
    "no_cieu_db_write_receipt.json",
    "no_canonical_mutation_receipt.json",
    "no_brain_memory_writeback_receipt.json",
    "no_direct_y_star_mutation_receipt.json",
]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_l6_10_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10_and_runtime_limits() -> None:
    contract = load("l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_milestone_contract.json")
    assert contract["milestone_id"] == "L6.10"
    assert contract["milestone_name"] == "Tiny Real Read-Only Agentic Evidence Observation Pilot v0"
    assert contract["input_milestones"] == [
        "L6.0",
        "L6.1",
        "L6.2",
        "L6.3",
        "L6.4",
        "L6.5",
        "L6.6",
        "L6.7",
        "L6.8",
        "L6.9",
    ]
    assert contract["mode"] == "tiny_real_read_only_observation_pilot"
    assert contract["max_selected_work_orders"] == 1
    assert contract["max_source_locators_observed"] == 1
    assert contract["max_search_queries_if_locator_missing"] == 1
    assert contract["max_pages_read"] == 1
    assert contract["real_read_only_observation_pilot_authorized"] is True


def test_forbidden_actions_are_not_authorized() -> None:
    contract = load("l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_milestone_contract.json")
    for field in [
        "broad_web_search_authorized",
        "crawling_authorized",
        "scraping_authorized",
        "browser_automation_authorized",
        "login_authorized",
        "account_creation_authorized",
        "payment_authorized",
        "form_submission_authorized",
        "posting_commenting_messaging_authorized",
        "publication_authorized",
        "outreach_authorized",
        "revenue_execution_authorized",
        "mcp_execution_authorized",
        "live_behavior_authorized",
        "cieu_db_write_authorized",
        "canonical_update_authorized",
        "direct_y_star_mutation_authorized",
        "brain_writeback_authorized",
        "memory_ingestion_authorized",
        "artifact_refinement_application_authorized",
    ]:
        assert contract[field] is False, field


def test_work_order_selection_and_execution_packet() -> None:
    selected = load("tiny_observation_work_order_selector/selected_tiny_observation_work_order.json")
    assert selected["selected_work_order_id"] == "l6_10_selected_tiny_observation_work_order_001"
    assert selected["max_selected_work_orders"] == 1
    matrix = load("tiny_observation_work_order_selector/tiny_observation_selection_matrix.json")
    assert matrix["max_selected_work_orders"] == 1
    packet = load("tiny_observation_execution_packet/tiny_observation_execution_packet.json")
    assert packet["selected_work_order_id"] == selected["selected_work_order_id"]
    assert packet["operator_or_agent_mode"] == "controlled_agentic_read_only"
    assert packet["publication_authorized"] is False
    assert packet["canonical_update_authorized"] is False


def test_runtime_guard_and_locator_resolution_respect_limits() -> None:
    guard = load("tiny_observation_runtime_guard/runtime_guard_limits.json")
    assert guard["max_selected_work_orders"] == 1
    assert guard["max_pages_read"] == 1
    assert guard["crawling_allowed"] is False
    prohibited = load("tiny_observation_runtime_guard/prohibited_runtime_actions.json")
    assert "broad web search" in prohibited["prohibited_actions"]
    resolution = load("tiny_source_locator_resolution/source_locator_resolution_result.json")
    assert resolution["source_locator_resolved"] is False
    assert resolution["search_queries_used"] <= guard["max_search_queries_if_locator_missing"]
    assert resolution["external_requests_used"] <= guard["max_external_requests"]
    assert resolution["pages_read"] <= guard["max_pages_read"]


def test_observation_trace_exists_and_never_exceeds_budget() -> None:
    trace = load("tiny_real_read_only_observation_trace/tiny_observation_trace.json")
    limits = trace["runtime_limits"]
    assert trace["external_requests_count"] <= limits["max_external_requests"]
    assert trace["pages_read_count"] <= limits["max_pages_read"]
    assert trace["search_queries_count"] <= limits["max_search_queries_if_locator_missing"]
    if not trace["observation_executed"]:
        assert trace["network_used"] is False
        assert trace["source_locator"] is None
        assert trace["abort_triggered"] is True
    assert trace["login_encountered"] is False
    assert trace["payment_encountered"] is False
    assert trace["form_encountered"] is False
    assert trace["private_data_encountered"] is False


def test_evidence_packet_and_structural_validation_are_honest() -> None:
    evidence = load("tiny_evidence_capture_packet/tiny_evidence_packet.json")
    assert evidence["review_status"] == "pending_review"
    assert evidence["external_action_taken"] is False
    assert evidence["publication_taken"] is False
    assert evidence["outreach_taken"] is False
    assert evidence["payment_taken"] is False
    assert evidence["mcp_execution_taken"] is False
    if evidence["live_source_evidence_captured"] is False:
        assert evidence["captured_claims"] == []
        assert "no live observation executed" in evidence["missing_context"]
    validation = load("tiny_evidence_structural_validation/evidence_validation_matrix.json")
    assert validation["semantic_truth_score"] is None
    assert validation["llm_confidence_as_authority"] is False
    assert all(item["passed"] for item in validation["validation_checks"])


def test_claim_boundary_review_and_refinement_are_review_only() -> None:
    bounded = load("tiny_claim_boundary_and_freshness_assessment/bounded_claim_registry.json")
    assert bounded["claim_count"] == 0
    unsupported = load("tiny_claim_boundary_and_freshness_assessment/unsupported_inference_registry.json")
    assert unsupported["unsupported_inferences"][0]["unsupported_inference_marker"] is True
    review = load("tiny_post_observation_review_packet/tiny_post_observation_review_packet.json")
    assert review["approve_for_external_use"] is False
    assert review["applied"] is False
    candidate = load("tiny_artifact_refinement_candidate/tiny_artifact_refinement_candidate.json")
    assert candidate["review_required"] is True
    assert candidate["approved"] is False
    assert candidate["applied"] is False
    assert candidate["artifact_update_authorized"] is False
    assert candidate["canonical_update_authorized"] is False
    assert candidate["brain_writeback_authorized"] is False
    assert candidate["memory_ingestion_authorized"] is False
    assert candidate["direct_y_star_mutation_authorized"] is False


def test_abort_quarantine_and_no_action_receipts() -> None:
    abort = load("tiny_observation_abort_and_quarantine/abort_or_quarantine_decision.json")
    assert abort["abort_triggered"] is True
    assert abort["decision"] == "blocked_before_observation_no_evidence_to_quarantine"
    for receipt in RECEIPTS:
        data = load(f"tiny_observation_no_action_receipts/{receipt}")
        assert data["authorized_in_l6_10"] is False
        assert data["executed_in_l6_10"] is False


def test_strategic_residual_and_meta_learning_are_review_only() -> None:
    cieu = load("l6_tiny_observation_strategic_residual_loop/l6_10_cieu_like_fixture.json")
    assert cieu["event_mode"] == "l6_10_tiny_real_read_only_agentic_evidence_observation_pilot_fixture"
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in cieu
    meta = load("l6_tiny_observation_strategic_residual_loop/l6_10_meta_learning_update_candidate.json")
    assert meta["eligible_for_review_queue"] is True
    assert meta["eligible_for_direct_brain_writeback"] is False
    assert meta["eligible_for_direct_memory_ingestion"] is False
    assert meta["eligible_for_candidate_auto_approval"] is False
    assert meta["eligible_for_direct_strategy_mutation"] is False
    assert meta["approved"] is False
    assert meta["applied"] is False


def test_readiness_blocks_downstream_actions() -> None:
    readiness = load("l6_tiny_observation_readiness_report/l6_10_readiness_assessment.json")
    assert readiness["l6_10_design_and_guardrails_complete"] is True
    assert readiness["real_observation_blocked_by_environment_or_locator"] is True
    assert readiness["ready_for_retry_after_condition_resolved"] is True
    assert readiness["ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot"] is False
    for field in [
        "ready_for_publication",
        "ready_for_outreach",
        "ready_for_payment",
        "ready_for_revenue_execution",
        "ready_for_mcp_execution",
        "ready_for_canonical_update",
        "ready_for_brain_memory_writeback",
        "ready_for_direct_y_star_mutation",
    ]:
        assert readiness[field] is False, field


def test_console_read_model_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "tiny-real-read-only-agentic-evidence-observation-pilot",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.10 Tiny Real Read-Only Agentic Evidence Observation Pilot" in result.stdout
    assert "observation executed: False" in result.stdout
