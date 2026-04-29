from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "l6_controlled_external_observation_sandbox"
    / "tools"
    / "build_l6_controlled_external_observation_sandbox.py"
)

REQUIRED_DIRS = [
    "l6_controlled_external_observation_sandbox",
    "l6_observation_case_selector",
    "controlled_pre_observation_packets",
    "sandbox_observation_permission_replay",
    "static_manual_observation_fixtures",
    "observation_evidence_validation_sandbox",
    "observation_claim_freshness_assessment",
    "observation_to_artifact_refinement_candidates",
    "controlled_observation_review_packets",
    "controlled_observation_no_action_receipts",
    "l6_controlled_observation_strategic_residual_loop",
    "l6_controlled_observation_sandbox_readiness",
]

REQUIRED_JSON = [
    "l6_controlled_external_observation_sandbox/l6_3_milestone_contract.json",
    "l6_controlled_external_observation_sandbox/l6_3_sandbox_scope.json",
    "l6_controlled_external_observation_sandbox/l6_3_safety_flags.json",
    "l6_controlled_external_observation_sandbox/l6_3_summary.json",
    "l6_observation_case_selector/l6_1_artifact_case_inventory.json",
    "l6_observation_case_selector/observation_need_matrix.json",
    "l6_observation_case_selector/selected_observation_cases.json",
    "l6_observation_case_selector/deferred_observation_cases.json",
    "controlled_pre_observation_packets/pre_observation_packet_index.json",
    "controlled_pre_observation_packets/packet_001.json",
    "controlled_pre_observation_packets/packet_002.json",
    "controlled_pre_observation_packets/packet_003.json",
    "sandbox_observation_permission_replay/permission_replay_contract.json",
    "sandbox_observation_permission_replay/packet_permission_decisions.json",
    "sandbox_observation_permission_replay/blocked_real_observation_decisions.json",
    "sandbox_observation_permission_replay/allowed_fixture_only_decisions.json",
    "static_manual_observation_fixtures/observation_fixture_index.json",
    "static_manual_observation_fixtures/fixture_001.json",
    "static_manual_observation_fixtures/fixture_002.json",
    "static_manual_observation_fixtures/fixture_003.json",
    "observation_evidence_validation_sandbox/evidence_validation_contract.json",
    "observation_evidence_validation_sandbox/evidence_validation_matrix.json",
    "observation_evidence_validation_sandbox/fixture_validation_results.json",
    "observation_evidence_validation_sandbox/evidence_gap_registry.json",
    "observation_claim_freshness_assessment/claim_assessment_contract.json",
    "observation_claim_freshness_assessment/claim_freshness_matrix.json",
    "observation_claim_freshness_assessment/bounded_claim_registry.json",
    "observation_claim_freshness_assessment/unsupported_inference_registry.json",
    "observation_claim_freshness_assessment/conflicting_or_missing_source_registry.json",
    "observation_to_artifact_refinement_candidates/refinement_candidate_index.json",
    "observation_to_artifact_refinement_candidates/candidate_001.json",
    "observation_to_artifact_refinement_candidates/candidate_002.json",
    "observation_to_artifact_refinement_candidates/candidate_003.json",
    "controlled_observation_review_packets/review_packet_index.json",
    "controlled_observation_review_packets/review_packet_001.json",
    "controlled_observation_review_packets/review_packet_002.json",
    "controlled_observation_review_packets/review_packet_003.json",
    "l6_controlled_observation_strategic_residual_loop/l6_3_cieu_like_fixture.json",
    "l6_controlled_observation_strategic_residual_loop/l6_3_strategic_residual_delta.json",
    "l6_controlled_observation_strategic_residual_loop/l6_3_meta_learning_update_candidate.json",
    "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json",
    "l6_controlled_observation_sandbox_readiness/l6_3_next_milestone_recommendation.json",
    "l6_controlled_observation_sandbox_readiness/l6_3_blockers.json",
]

PACKET_FIELDS = [
    "packet_id",
    "observation_intent",
    "linked_l6_hypothesis_id",
    "linked_l6_1_artifact_case_id",
    "intended_external_surface",
    "source_type",
    "source_locator_placeholder",
    "proposed_observation_method",
    "data_requested",
    "claim_to_validate_or_refine",
    "expected_evidence_type",
    "freshness_requirement",
    "trust_tier_requirement",
    "privacy_risk",
    "ip_risk",
    "login_required",
    "account_required",
    "contact_required",
    "payment_required",
    "write_or_post_required",
    "automation_required",
    "mcp_required",
    "network_required",
    "execution_required",
    "publication_required",
    "outreach_required",
    "no_action_guarantee",
    "evidence_capture_plan",
    "citation_or_source_trace_plan",
    "review_required",
    "approval_required_before_real_observation",
]

BLOCKED_FLAGS = [
    "network_enabled",
    "api_enabled",
    "scraping_enabled",
    "browser_fetch_enabled",
    "external_action_enabled",
    "publication_enabled",
    "outreach_enabled",
    "payment_enabled",
    "revenue_execution_enabled",
    "mcp_tool_execution_enabled",
    "live_execution_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "real_canonical_update_application_enabled",
    "real_y_star_direct_mutation_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
]

NO_ACTION_RECEIPTS = [
    "no_network_receipt.json",
    "no_api_receipt.json",
    "no_scraping_receipt.json",
    "no_browser_fetch_receipt.json",
    "no_publication_receipt.json",
    "no_outreach_receipt.json",
    "no_payment_receipt.json",
    "no_revenue_execution_receipt.json",
    "no_mcp_execution_receipt.json",
    "no_live_behavior_receipt.json",
    "no_canonical_mutation_receipt.json",
    "no_brain_memory_writeback_receipt.json",
    "no_direct_y_star_mutation_receipt.json",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)


def test_builder_runs() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert "Built L6.3 controlled external observation sandbox artifacts" in result.stdout


def test_required_directories_and_json_parse() -> None:
    for directory in REQUIRED_DIRS:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_JSON:
        assert (ROOT / path).is_file(), path
        load_json(path)


def test_milestone_contract_sandbox_only_and_safety_flags() -> None:
    contract = load_json(
        "l6_controlled_external_observation_sandbox/l6_3_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.3"
    assert contract["input_milestones"] == ["L6.0", "L6.1", "L6.2"]
    assert contract["mode"] == "controlled_observation_sandbox"
    assert contract["sandbox_only"] is True
    assert contract["static_fixture_observation_authorized"] is True
    assert contract["manual_import_fixture_authorized"] is True
    assert contract["artifact_refinement_candidate_authorized"] is True
    assert contract["artifact_refinement_application_authorized"] is False
    assert contract["requires_review_before_any_real_observation"] is True
    assert contract["requires_review_before_any_externalization"] is True
    for field in [
        "real_external_observation_authorized",
        "network_authorized",
        "api_authorized",
        "scraping_authorized",
        "browser_fetch_authorized",
        "external_action_authorized",
        "publication_authorized",
        "outreach_authorized",
        "payment_authorized",
        "revenue_execution_authorized",
        "mcp_execution_authorized",
        "live_behavior_authorized",
        "canonical_update_authorized",
        "direct_y_star_mutation_authorized",
        "brain_writeback_authorized",
        "memory_ingestion_authorized",
    ]:
        assert contract[field] is False
    for field in BLOCKED_FLAGS:
        assert contract["safety_flags"][field] is False


def test_observation_case_selector_is_structural_not_category_based() -> None:
    selected = load_json("l6_observation_case_selector/selected_observation_cases.json")
    assert 1 <= selected["selected_case_count"] <= 3
    assert selected["selection_mode"] == "structural_evidence_gap_based"
    assert selected["selected_by_hardcoded_opportunity_category"] is False
    assert selected["hardcoded_opportunity_class_used"] is False
    required_selection_signals = {
        "missing evidence",
        "unclear recipient archetype",
        "weak acceptance criteria",
        "stale or absent source evidence",
        "uncertain claim boundary",
        "proof question requires outside evidence",
        "high learning value",
        "reviewability",
    }
    for case in selected["selected_cases"]:
        assert required_selection_signals.issubset(set(case["selection_basis"]))
        assert case["real_observation_authorized"] is False
        assert case["sandbox_fixture_authorized"] is True
        assert case["manual_import_fixture_authorized"] is True
        assert case["review_required_before_real_observation"] is True


def test_pre_observation_packets_include_l6_2_fields_and_block_real_observation() -> None:
    index = load_json("controlled_pre_observation_packets/pre_observation_packet_index.json")
    assert 1 <= index["packet_count"] <= 3
    for entry in index["packets"]:
        packet = load_json(entry["path"])
        for field in PACKET_FIELDS:
            assert field in packet
        assert packet["sandbox_fixture_mode"] is True
        assert packet["real_observation_authorized"] is False
        assert packet["network_authorized_now"] is False
        assert packet["evidence_capture_plan"]["fetched_from_network"] is False
        assert packet["evidence_capture_plan"]["browser_fetch_performed"] is False
        assert packet["evidence_capture_plan"]["scraping_performed"] is False
        assert packet["publication_required"] is False
        assert packet["outreach_required"] is False
        assert packet["approval_required_before_real_observation"] is True


def test_permission_replay_blocks_real_observation_and_allows_fixture_only() -> None:
    decisions = load_json("sandbox_observation_permission_replay/packet_permission_decisions.json")
    assert decisions["decisions"]
    for decision in decisions["decisions"]:
        assert decision["real_observation_decision"] == "blocked_real_observation_l6_3"
        assert decision["fixture_decision"] == "allow_static_or_manual_import_fixture_only"
        assert decision["review_required"] is True
        assert decision["approval_required_before_real_observation"] is True
    blocked = load_json("sandbox_observation_permission_replay/blocked_real_observation_decisions.json")
    allowed = load_json("sandbox_observation_permission_replay/allowed_fixture_only_decisions.json")
    assert len(blocked["blocked_decisions"]) == len(decisions["decisions"])
    assert len(allowed["allowed_fixture_decisions"]) == len(decisions["decisions"])


def test_static_manual_fixtures_are_not_fetched_or_verified_current_facts() -> None:
    index = load_json("static_manual_observation_fixtures/observation_fixture_index.json")
    assert 1 <= index["fixture_count"] <= 3
    disclaimer = (ROOT / "static_manual_observation_fixtures/fixture_disclaimer.md").read_text(
        encoding="utf-8"
    )
    for marker in [
        "STATIC / MANUAL-IMPORT SANDBOX FIXTURE ONLY",
        "NOT FETCHED",
        "NOT CURRENT FACT",
        "NOT VERIFIED EXTERNAL DATA",
        "NOT AUTHORIZED FOR EXTERNAL ACTION",
        "NOT AUTHORIZED FOR PUBLICATION",
        "NOT AUTHORIZED FOR OUTREACH",
        "NOT AUTHORIZED FOR PAYMENT",
        "NOT AUTHORIZED FOR REVENUE EXECUTION",
        "NOT AUTHORIZED FOR CANONICAL UPDATE",
    ]:
        assert marker in disclaimer
    for entry in index["fixtures"]:
        fixture = load_json(entry["path"])
        assert fixture["fixture_mode"] == "static_manual_import_sandbox"
        assert fixture["fetched_from_network"] is False
        assert fixture["generated_from_live_source"] is False
        assert fixture["current_fact_claimed"] is False
        assert fixture["external_source_verified"] is False
        assert fixture["supplied_by_user"] is False
        assert fixture["date_missing"] is True
        assert fixture["review_required"] is True
        assert fixture["external_action_authorized"] is False


def test_fixture_validation_is_structural_and_avoids_scoring_authority() -> None:
    matrix = load_json("observation_evidence_validation_sandbox/evidence_validation_matrix.json")
    assert matrix["validation_mode"] == "structural_only"
    serialized = json.dumps(matrix)
    assert "truth_score" not in serialized
    assert "semantic_truth_score" not in serialized
    assert "market_success_score" not in serialized
    assert matrix["semantic_scoring_authority_used"] is False
    results = load_json("observation_evidence_validation_sandbox/fixture_validation_results.json")
    for result in results["fixture_validation_results"]:
        assert result["validation_status"] == "fixture_structurally_valid_for_sandbox_only"
        assert result["fetched_from_network_false"] is True
        assert result["current_fact_claimed_false"] is True
        assert result["external_action_blocked"] is True
        assert result["semantic_scoring_authority_used"] is False


def test_claim_freshness_assessment_has_trace_freshness_and_limit_markers() -> None:
    claims = load_json("observation_claim_freshness_assessment/claim_freshness_matrix.json")
    assert claims["bounded_claims"]
    for claim in claims["bounded_claims"]:
        assert claim["source_trace_status"]
        assert claim["freshness_class"]
        assert claim["source_date_status"]
        assert claim["limitation"]
        assert claim["unsupported_inference_marker"] is True
        assert claim["review_status"] == "review_required"
        assert claim["allowed_use_in_l6_3"] == "internal_sandbox_only"
        assert claim["external_use_authorized"] is False


def test_refinement_candidates_are_review_only_not_applied() -> None:
    index = load_json(
        "observation_to_artifact_refinement_candidates/refinement_candidate_index.json"
    )
    assert 1 <= index["candidate_count"] <= 3
    allowed_targets = {
        "proof_question",
        "acceptance_criteria",
        "evidence_needed",
        "claim_boundary",
        "recipient_archetype",
        "payer_or_beneficiary_clarity",
        "distribution_friction",
        "competitive_pressure",
        "external_dependency",
        "freshness_requirement",
        "review_preconditions",
    }
    for entry in index["candidates"]:
        candidate = load_json(entry["path"])
        assert candidate["refinement_target"] in allowed_targets
        assert candidate["review_required"] is True
        assert candidate["approved"] is False
        assert candidate["applied"] is False
        assert candidate["artifact_update_authorized"] is False
        assert candidate["canonical_update_authorized"] is False
        assert candidate["brain_writeback_authorized"] is False
        assert candidate["memory_ingestion_authorized"] is False
        assert candidate["direct_y_star_mutation_authorized"] is False


def test_review_packets_are_pending_and_unapplied() -> None:
    index = load_json("controlled_observation_review_packets/review_packet_index.json")
    assert 1 <= index["review_packet_count"] <= 3
    for entry in index["review_packets"]:
        packet = load_json(entry["path"])
        assert packet["current_decision"] == "review_pending"
        assert packet["approved"] is False
        assert packet["applied"] is False
        assert packet["approval_preconditions_for_real_observation"]
        assert packet["approval_preconditions_for_externalization"]
        assert packet["approval_preconditions_for_artifact_update"]


def test_no_action_receipts_all_keep_executed_false() -> None:
    for filename in NO_ACTION_RECEIPTS:
        receipt = load_json(f"controlled_observation_no_action_receipts/{filename}")
        assert receipt["authorized_in_l6_3"] is False
        assert receipt["executed_in_l6_3"] is False
        assert receipt["future_boundary_required"] == (
            "L6.4 Real Read-Only External Observation Preflight v0"
        )


def test_strategic_residual_and_meta_learning_are_review_only() -> None:
    fixture = load_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_cieu_like_fixture.json"
    )
    assert fixture["event_mode"] == "l6_3_controlled_external_observation_sandbox_fixture"
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in fixture
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    residual = load_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_strategic_residual_delta.json"
    )
    assert "no real source evidence available yet" in residual["residual_classes"]
    update = load_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_meta_learning_update_candidate.json"
    )
    assert update["eligible_for_review_queue"] is True
    assert update["eligible_for_direct_brain_writeback"] is False
    assert update["eligible_for_direct_memory_ingestion"] is False
    assert update["eligible_for_candidate_auto_approval"] is False
    assert update["eligible_for_direct_strategy_mutation"] is False
    assert update["approved"] is False
    assert update["applied"] is False


def test_readiness_blocks_real_execution_and_recommends_future_preflight() -> None:
    readiness = load_json(
        "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json"
    )
    assert readiness["l6_3_controlled_external_observation_sandbox_complete"] is True
    assert readiness["ready_for_l6_4_real_read_only_external_observation_preflight"] is True
    for field in [
        "ready_for_real_network_observation",
        "ready_for_scraping",
        "ready_for_publication",
        "ready_for_outreach",
        "ready_for_payment",
        "ready_for_revenue_execution",
        "ready_for_mcp_execution",
        "ready_for_canonical_update",
        "ready_for_brain_memory_writeback",
    ]:
        assert readiness[field] is False
    assert readiness["next_recommended_milestone"] == (
        "L6.4 Real Read-Only External Observation Preflight v0"
    )


def test_l6_3_builder_does_not_import_or_invoke_network_tools() -> None:
    forbidden = [
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "urllib.request",
        "import aiohttp",
        "from aiohttp",
        "import selenium",
        "from selenium",
        "import playwright",
        "from playwright",
        "import socket",
        "from socket",
        "curl ",
        "wget ",
    ]
    for path in (ROOT / "l6_controlled_external_observation_sandbox" / "tools").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text


def test_console_read_model_command_works() -> None:
    run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    result = run_command(
        [
            "python3",
            "console_read_model/cli/team_console.py",
            "controlled-external-observation-sandbox",
        ]
    )
    assert "L6.3 Controlled External Observation Sandbox" in result.stdout
    assert "real external observation authorized: False" in result.stdout
    assert "ready for L6.4 real read-only external observation preflight: True" in result.stdout
