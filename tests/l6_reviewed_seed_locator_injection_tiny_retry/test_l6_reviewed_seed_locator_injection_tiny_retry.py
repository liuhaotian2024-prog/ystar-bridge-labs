from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_reviewed_seed_locator_injection_tiny_retry",
    "reviewed_seed_locator_injection",
    "seed_locator_user_action_request",
    "seed_locator_retry_attempt",
    "seed_locator_retry_result",
    "l6_10w_read_model",
]

REQUIRED_JSON = [
    "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_milestone_contract.json",
    "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_scope.json",
    "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_runtime_limits.json",
    "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_safety_flags.json",
    "l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_summary.json",
    "reviewed_seed_locator_injection/selected_work_order_for_seed_injection.json",
    "reviewed_seed_locator_injection/seed_locator_injection_schema.json",
    "reviewed_seed_locator_injection/existing_seed_registry_scan.json",
    "reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json",
    "reviewed_seed_locator_injection/reviewed_seed_locator_injection_decision.json",
    "seed_locator_user_action_request/user_action_required.json",
    "seed_locator_user_action_request/seed_locator_request_packet.json",
    "seed_locator_user_action_request/seed_locator_submission_template.json",
    "seed_locator_retry_attempt/seed_locator_retry_request.json",
    "seed_locator_retry_attempt/seed_locator_retry_trace.json",
    "seed_locator_retry_attempt/seed_locator_eligibility_result.json",
    "seed_locator_retry_result/tiny_seed_observation_trace.json",
    "seed_locator_retry_result/tiny_seed_evidence_packet.json",
    "seed_locator_retry_result/tiny_seed_claim_boundary_assessment.json",
    "seed_locator_retry_result/tiny_seed_post_observation_review_packet.json",
    "seed_locator_retry_result/tiny_seed_refinement_candidate.json",
    "seed_locator_retry_result/tiny_seed_no_action_receipts.json",
    "l6_10w_read_model/l6_10w_cieu_like_fixture.json",
    "l6_10w_read_model/l6_10w_strategic_residual_delta.json",
    "l6_10w_read_model/l6_10w_meta_learning_update_candidate.json",
    "l6_10w_read_model/l6_10w_readiness_assessment.json",
    "l6_10w_read_model/l6_10w_blockers.json",
    "l6_10w_read_model/l6_10w_next_milestone_recommendation.json",
    "l6_10w_read_model/l6_10w_read_model_summary.json",
    "console_read_model/generated/l6_10w_reviewed_seed_locator_injection_summary.json",
]

FORBIDDEN_FLAGS = [
    "url_invention_authorized",
    "fake_locator_authorized",
    "broad_search_authorized",
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
]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_l6_10w_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10w_and_boundaries() -> None:
    contract = load("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_milestone_contract.json")
    assert contract["milestone_id"] == "L6.10W"
    assert contract["milestone_name"] == "Reviewed Seed Locator Injection & Tiny Observation Retry v0"
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
        "L6.10R",
        "L6.10T",
        "L6.10U",
        "L6.10V",
    ]
    assert contract["mode"] == "reviewed_seed_locator_injection_and_tiny_retry"
    assert contract["reviewed_seed_locator_injection_authorized"] is True
    assert contract["user_action_request_authorized"] is True
    assert contract["seed_locator_from_existing_repo_artifacts_authorized"] is True
    assert contract["max_selected_work_orders"] == 1
    assert contract["max_seed_locators_injected"] == 1
    assert contract["max_pages_read"] == 1
    assert contract["max_total_external_reads"] == 1
    for field in FORBIDDEN_FLAGS:
        assert contract[field] is False, field


def test_selected_work_order_count_at_most_one_and_scan_exists() -> None:
    selected = load("reviewed_seed_locator_injection/selected_work_order_for_seed_injection.json")
    scan = load("reviewed_seed_locator_injection/existing_seed_registry_scan.json")
    assert selected["selected_count"] <= 1
    assert selected["selected_work_order_id"] == "l6_10w_selected_work_order_001"
    assert scan["scan_scope"] == "existing_local_seed_registry_files_only"
    assert scan["url_invented"] is False
    assert scan["facts_inferred_from_seed"] is False


def test_no_reviewed_locator_generates_exact_one_url_user_action_request() -> None:
    candidate = load("reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json")
    request = load("seed_locator_user_action_request/user_action_required.json")
    markdown = (ROOT / "seed_locator_user_action_request/USER_ACTION_REQUIRED.md").read_text(
        encoding="utf-8"
    )
    assert candidate["status"] == "user_action_required"
    assert candidate["concrete_locator"] is None
    assert candidate["facts_inferred_from_seed"] is False
    assert candidate["observation_authorized_by_seed_alone"] is False
    assert request["request_count"] == 1
    assert request["requested_item"] == "one_concrete_public_url"
    assert request["prompt"] == "Please provide one concrete public URL for the selected work order."
    assert request["selected_work_order_id"] == "l6_10w_selected_work_order_001"
    assert request["source_type_needed"]
    assert request["source_function_needed"]
    assert request["observation_question"]
    assert "search results page" in request["unacceptable_source_criteria"]
    assert "public page" in request["acceptable_source_criteria"]
    assert "Please provide one concrete public URL" in markdown
    assert "Paste exactly one URL" in markdown


def test_retry_does_not_execute_without_locator_and_evidence_exists() -> None:
    retry = load("seed_locator_retry_attempt/seed_locator_retry_trace.json")
    observation = load("seed_locator_retry_result/tiny_seed_observation_trace.json")
    evidence = load("seed_locator_retry_result/tiny_seed_evidence_packet.json")
    review = load("seed_locator_retry_result/tiny_seed_post_observation_review_packet.json")
    refinement = load("seed_locator_retry_result/tiny_seed_refinement_candidate.json")
    assert retry["retry_attempted"] is False
    assert retry["reason"] == "user_action_required_no_seed_locator"
    assert observation["observation_executed"] is False
    assert observation["network_used"] is False
    assert observation["external_reads_count"] == 0
    assert observation["pages_read_count"] == 0
    assert evidence["live_source_evidence_captured"] is False
    assert evidence["captured_claims"] == []
    assert evidence["publication_taken"] is False
    assert evidence["outreach_taken"] is False
    assert evidence["payment_taken"] is False
    assert evidence["revenue_action_taken"] is False
    assert evidence["mcp_execution_taken"] is False
    assert review["approve_for_external_use"] is False
    assert review["applied"] is False
    assert refinement["review_required"] is True
    assert refinement["approved"] is False
    assert refinement["applied"] is False


def test_no_action_receipts_show_disallowed_actions_false() -> None:
    receipts = load("seed_locator_retry_result/tiny_seed_no_action_receipts.json")
    assert receipts["receipts"]
    for receipt in receipts["receipts"]:
        assert receipt["authorized_in_l6_10w"] is False
        assert receipt["executed_in_l6_10w"] is False


def test_cieu_fixture_meta_learning_and_readiness() -> None:
    cieu = load("l6_10w_read_model/l6_10w_cieu_like_fixture.json")
    meta = load("l6_10w_read_model/l6_10w_meta_learning_update_candidate.json")
    readiness = load("l6_10w_read_model/l6_10w_readiness_assessment.json")
    assert cieu["event_mode"] == "l6_10w_reviewed_seed_locator_injection_tiny_retry_fixture"
    assert meta["eligible_for_review_queue"] is True
    assert meta["eligible_for_direct_brain_writeback"] is False
    assert meta["eligible_for_direct_memory_ingestion"] is False
    assert meta["approved"] is False
    assert meta["applied"] is False
    assert readiness["reviewed_seed_locator_found"] is False
    assert readiness["user_action_required_generated"] is True
    assert readiness["ready_for_l6_11_controlled_multi_source_corroboration"] is False
    assert readiness["remaining_blocker"] == "user_must_provide_one_reviewed_seed_locator_url"


def test_console_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "reviewed-seed-locator-injection-tiny-retry",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.10W Reviewed Seed Locator Injection Tiny Retry" in result.stdout
    assert "user action required generated: True" in result.stdout
    assert "reviewed seed locator found: False" in result.stdout
