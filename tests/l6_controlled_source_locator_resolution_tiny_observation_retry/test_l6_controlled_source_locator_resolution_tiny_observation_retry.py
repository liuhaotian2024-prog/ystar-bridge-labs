from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_controlled_source_locator_resolution_tiny_observation_retry",
    "locator_retry_work_order_selector",
    "controlled_locator_discovery_plan",
    "controlled_locator_resolution_trace",
    "locator_eligibility_and_risk_gate",
    "tiny_observation_retry_execution_packet",
    "tiny_observation_retry_runtime_guard",
    "tiny_observation_retry_trace",
    "tiny_retry_evidence_capture_packet",
    "tiny_retry_evidence_validation",
    "tiny_retry_claim_boundary_freshness_assessment",
    "tiny_retry_post_observation_review",
    "tiny_retry_refinement_candidate",
    "tiny_retry_abort_quarantine",
    "tiny_retry_no_action_receipts",
    "l6_10r_strategic_residual_loop",
    "l6_10r_readiness_report",
]

REQUIRED_JSON = [
    "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_milestone_contract.json",
    "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_scope.json",
    "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_safety_flags.json",
    "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_runtime_limits.json",
    "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.json",
    "locator_retry_work_order_selector/l6_8_l6_9_l6_10_work_order_inventory.json",
    "locator_retry_work_order_selector/locator_retry_selection_matrix.json",
    "locator_retry_work_order_selector/selected_locator_retry_work_order.json",
    "locator_retry_work_order_selector/deferred_locator_retry_work_orders.json",
    "controlled_locator_discovery_plan/locator_discovery_plan_schema.json",
    "controlled_locator_discovery_plan/locator_discovery_plan.json",
    "controlled_locator_discovery_plan/locator_discovery_query_budget.json",
    "controlled_locator_discovery_plan/locator_discovery_abort_conditions.json",
    "controlled_locator_resolution_trace/locator_resolution_trace_schema.json",
    "controlled_locator_resolution_trace/locator_resolution_trace.json",
    "controlled_locator_resolution_trace/resolved_source_locator.json",
    "locator_eligibility_and_risk_gate/locator_eligibility_gate_contract.json",
    "locator_eligibility_and_risk_gate/locator_eligibility_result.json",
    "locator_eligibility_and_risk_gate/locator_risk_assessment.json",
    "locator_eligibility_and_risk_gate/locator_rejection_decision.json",
    "tiny_observation_retry_execution_packet/retry_execution_packet_schema.json",
    "tiny_observation_retry_execution_packet/retry_execution_packet.json",
    "tiny_observation_retry_execution_packet/retry_pre_run_checklist.json",
    "tiny_observation_retry_runtime_guard/retry_runtime_guard_contract.json",
    "tiny_observation_retry_runtime_guard/retry_runtime_guard_limits.json",
    "tiny_observation_retry_runtime_guard/retry_prohibited_runtime_actions.json",
    "tiny_observation_retry_runtime_guard/retry_runtime_abort_conditions.json",
    "tiny_observation_retry_trace/retry_observation_trace_schema.json",
    "tiny_observation_retry_trace/retry_observation_trace.json",
    "tiny_retry_evidence_capture_packet/retry_evidence_capture_schema.json",
    "tiny_retry_evidence_capture_packet/retry_evidence_packet.json",
    "tiny_retry_evidence_capture_packet/retry_citation_trace.json",
    "tiny_retry_evidence_validation/retry_evidence_validation_contract.json",
    "tiny_retry_evidence_validation/retry_evidence_validation_matrix.json",
    "tiny_retry_evidence_validation/retry_evidence_validation_result.json",
    "tiny_retry_claim_boundary_freshness_assessment/retry_claim_boundary_schema.json",
    "tiny_retry_claim_boundary_freshness_assessment/retry_bounded_claim_registry.json",
    "tiny_retry_claim_boundary_freshness_assessment/retry_freshness_assessment.json",
    "tiny_retry_claim_boundary_freshness_assessment/retry_unsupported_inference_registry.json",
    "tiny_retry_post_observation_review/retry_post_observation_review_schema.json",
    "tiny_retry_post_observation_review/retry_post_observation_review_packet.json",
    "tiny_retry_refinement_candidate/retry_refinement_candidate_schema.json",
    "tiny_retry_refinement_candidate/retry_artifact_refinement_candidate.json",
    "tiny_retry_abort_quarantine/retry_abort_policy.json",
    "tiny_retry_abort_quarantine/retry_quarantine_policy.json",
    "tiny_retry_abort_quarantine/retry_abort_or_quarantine_decision.json",
    "l6_10r_strategic_residual_loop/l6_10r_cieu_like_fixture.json",
    "l6_10r_strategic_residual_loop/l6_10r_strategic_residual_delta.json",
    "l6_10r_strategic_residual_loop/l6_10r_meta_learning_update_candidate.json",
    "l6_10r_readiness_report/l6_10r_readiness_assessment.json",
    "l6_10r_readiness_report/l6_10r_next_milestone_recommendation.json",
    "l6_10r_readiness_report/l6_10r_blockers.json",
    "console_read_model/generated/l6_10r_locator_retry_summary.json",
]

RECEIPTS = [
    "no_broad_search_receipt.json",
    "no_repeated_search_loop_receipt.json",
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


def test_l6_10r_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10r_and_runtime_limits() -> None:
    contract = load("l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_milestone_contract.json")
    assert contract["milestone_id"] == "L6.10R"
    assert contract["milestone_name"] == "Controlled Source Locator Resolution & Tiny Observation Retry v0"
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
        "L6.10",
    ]
    assert contract["mode"] == "controlled_locator_resolution_and_tiny_observation_retry"
    assert contract["max_selected_work_orders"] == 1
    assert contract["max_locator_discovery_queries"] == 1
    assert contract["max_concrete_locators_resolved"] == 1
    assert contract["max_source_locators_observed"] == 1
    assert contract["max_pages_read"] == 1
    assert contract["max_external_reads_total"] == 2
    assert contract["controlled_locator_discovery_authorized"] is True
    assert contract["tiny_real_read_only_observation_retry_authorized"] is True


def test_forbidden_actions_are_not_authorized() -> None:
    contract = load("l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_milestone_contract.json")
    for field in [
        "broad_web_search_authorized",
        "repeated_search_loop_authorized",
        "crawling_authorized",
        "scraping_authorized",
        "browser_automation_authorized",
        "login_authorized",
        "account_creation_authorized",
        "contact_authorized",
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


def test_work_order_selector_selects_at_most_one() -> None:
    selected = load("locator_retry_work_order_selector/selected_locator_retry_work_order.json")
    matrix = load("locator_retry_work_order_selector/locator_retry_selection_matrix.json")
    assert matrix["max_selected_work_orders"] == 1
    assert matrix["selected_count"] == 1
    assert selected["selected_retry_work_order_id"] == "l6_10r_selected_locator_retry_work_order_001"
    assert selected["real_observation_authorized_now"] is False
    assert selected["linked_l6_8_work_order_id"]
    assert "L6.10 selected it" in selected["selection_criteria"]


def test_locator_discovery_plan_respects_single_query_budget() -> None:
    plan = load("controlled_locator_discovery_plan/locator_discovery_plan.json")
    budget = load("controlled_locator_discovery_plan/locator_discovery_query_budget.json")
    assert plan["query_purpose"] == "locator_resolution_only"
    assert plan["max_queries"] == 1
    assert plan["max_results_to_consider"] == 1
    assert plan["no_snippet_fact_use"] is True
    assert plan["no_claim_inference_from_search_result"] is True
    assert budget["queries_used"] <= budget["max_queries"]
    assert budget["results_considered"] <= budget["max_results_to_consider"]


def test_locator_resolution_trace_and_eligibility_gate_block_safely() -> None:
    trace = load("controlled_locator_resolution_trace/locator_resolution_trace.json")
    assert trace["locator_resolution_attempted"] is True
    assert trace["locator_discovery_queries_count"] <= 1
    assert trace["external_reads_count_for_resolution"] <= 2
    assert trace["facts_inferred_from_locator_discovery"] is False
    if trace["concrete_locator_resolved"] is False:
        assert trace["resolved_locator"] is None
        assert trace["abort_triggered"] is True
    eligibility = load("locator_eligibility_and_risk_gate/locator_eligibility_result.json")
    assert eligibility["locator_eligible_for_observation"] is False
    assert eligibility["observation_blocked"] is True
    rejection = load("locator_eligibility_and_risk_gate/locator_rejection_decision.json")
    assert rejection["observation_authorized"] is False


def test_retry_execution_packet_and_runtime_guard_keep_boundaries() -> None:
    packet = load("tiny_observation_retry_execution_packet/retry_execution_packet.json")
    assert packet["retry_observation_authorized"] is False
    assert packet["publication_authorized"] is False
    assert packet["canonical_update_authorized"] is False
    assert packet["direct_y_star_mutation_authorized"] is False
    guard = load("tiny_observation_retry_runtime_guard/retry_runtime_guard_limits.json")
    assert guard["max_selected_work_orders"] == 1
    assert guard["max_locator_discovery_queries"] == 1
    assert guard["max_external_reads_total"] == 2
    assert guard["max_pages_read"] == 1
    prohibited = load("tiny_observation_retry_runtime_guard/retry_prohibited_runtime_actions.json")
    assert "no broad search" in prohibited["prohibited_actions"]
    assert "no contact" in prohibited["prohibited_actions"]


def test_retry_observation_trace_exists_and_never_exceeds_budget() -> None:
    trace = load("tiny_observation_retry_trace/retry_observation_trace.json")
    limits = trace["runtime_limits"]
    assert trace["external_reads_total"] <= limits["max_external_reads_total"]
    assert trace["pages_read_count"] <= limits["max_pages_read"]
    assert trace["locator_discovery_queries_count"] <= limits["max_locator_discovery_queries"]
    if not trace["observation_executed"]:
        assert trace["network_used"] is False
        assert trace["source_locator"] is None
        assert trace["abort_triggered"] is True
    assert trace["login_encountered"] is False
    assert trace["payment_encountered"] is False
    assert trace["form_encountered"] is False
    assert trace["private_data_encountered"] is False


def test_evidence_packet_and_validation_do_not_fake_live_evidence() -> None:
    evidence = load("tiny_retry_evidence_capture_packet/retry_evidence_packet.json")
    assert evidence["review_status"] == "pending_review"
    assert evidence["live_source_evidence_captured"] is False
    assert evidence["captured_claims"] == []
    assert "no live observation executed" in evidence["missing_context"]
    assert evidence["publication_taken"] is False
    assert evidence["outreach_taken"] is False
    assert evidence["payment_taken"] is False
    assert evidence["mcp_execution_taken"] is False
    validation = load("tiny_retry_evidence_validation/retry_evidence_validation_matrix.json")
    assert validation["semantic_truth_score"] is None
    assert validation["llm_confidence_as_authority"] is False
    assert all(item["passed"] for item in validation["validation_checks"])


def test_claim_boundary_review_and_refinement_are_review_only() -> None:
    bounded = load("tiny_retry_claim_boundary_freshness_assessment/retry_bounded_claim_registry.json")
    assert bounded["claim_count"] == 0
    assert bounded["external_use_authorized"] is False
    unsupported = load("tiny_retry_claim_boundary_freshness_assessment/retry_unsupported_inference_registry.json")
    assert unsupported["unsupported_inferences"][0]["unsupported_inference_marker"] is True
    review = load("tiny_retry_post_observation_review/retry_post_observation_review_packet.json")
    assert review["approval_status"] == "pending_review"
    assert review["approve_for_externalization"] is False
    assert review["approve_for_artifact_update"] is False
    assert review["applied"] is False
    candidate = load("tiny_retry_refinement_candidate/retry_artifact_refinement_candidate.json")
    assert candidate["review_required"] is True
    assert candidate["approved"] is False
    assert candidate["applied"] is False
    assert candidate["artifact_update_authorized"] is False
    assert candidate["canonical_update_authorized"] is False
    assert candidate["brain_writeback_authorized"] is False
    assert candidate["memory_ingestion_authorized"] is False
    assert candidate["direct_y_star_mutation_authorized"] is False


def test_abort_quarantine_and_no_action_receipts() -> None:
    abort = load("tiny_retry_abort_quarantine/retry_abort_or_quarantine_decision.json")
    assert abort["abort_triggered"] is True
    assert abort["decision"] == "blocked_before_observation_no_evidence_to_quarantine"
    for receipt in RECEIPTS:
        data = load(f"tiny_retry_no_action_receipts/{receipt}")
        assert data["authorized_in_l6_10r"] is False
        assert data["executed_in_l6_10r"] is False


def test_strategic_residual_and_meta_learning_are_review_only() -> None:
    cieu = load("l6_10r_strategic_residual_loop/l6_10r_cieu_like_fixture.json")
    assert cieu["event_mode"] == "l6_10r_controlled_source_locator_resolution_tiny_observation_retry_fixture"
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in cieu
    meta = load("l6_10r_strategic_residual_loop/l6_10r_meta_learning_update_candidate.json")
    assert meta["eligible_for_review_queue"] is True
    assert meta["eligible_for_direct_brain_writeback"] is False
    assert meta["eligible_for_direct_memory_ingestion"] is False
    assert meta["eligible_for_candidate_auto_approval"] is False
    assert meta["eligible_for_direct_strategy_mutation"] is False
    assert meta["approved"] is False
    assert meta["applied"] is False


def test_readiness_report_and_console_command() -> None:
    readiness = load("l6_10r_readiness_report/l6_10r_readiness_assessment.json")
    assert readiness["l6_10r_design_and_guardrails_complete"] is True
    assert readiness["concrete_locator_resolved"] is False
    assert readiness["tiny_read_only_observation_executed"] is False
    assert readiness["ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot"] is False
    assert readiness["ready_for_publication"] is False
    assert readiness["ready_for_outreach"] is False
    assert readiness["ready_for_payment"] is False
    assert readiness["ready_for_revenue_execution"] is False
    assert readiness["ready_for_mcp_execution"] is False
    assert readiness["ready_for_canonical_update"] is False
    assert readiness["ready_for_brain_memory_writeback"] is False
    assert readiness["ready_for_direct_y_star_mutation"] is False
    summary = load("console_read_model/generated/l6_10r_locator_retry_summary.json")
    assert summary["remaining_blocker"] == readiness["remaining_blocker"]
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "controlled-source-locator-resolution-tiny-observation-retry",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.10R Controlled Source Locator Resolution" in result.stdout
