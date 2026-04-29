from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "l6_governed_external_observation_boundary"
    / "tools"
    / "build_l6_governed_external_observation_boundary.py"
)

REQUIRED_DIRS = [
    "l6_governed_external_observation_boundary",
    "external_observation_definition_and_scope",
    "pre_observation_packet_schema",
    "external_source_registry_and_policy",
    "external_observation_permission_gate",
    "manual_external_evidence_import_sandbox",
    "observation_to_mvp_artifact_linker",
    "observation_claim_boundary_and_freshness",
    "external_observation_no_action_receipts",
    "l6_external_observation_strategic_residual_loop",
    "l6_external_observation_boundary_readiness",
]

REQUIRED_JSON = [
    "l6_governed_external_observation_boundary/l6_2_milestone_contract.json",
    "l6_governed_external_observation_boundary/l6_2_boundary_scope.json",
    "l6_governed_external_observation_boundary/l6_2_safety_flags.json",
    "l6_governed_external_observation_boundary/l6_2_summary.json",
    "external_observation_definition_and_scope/external_observation_definition.json",
    "external_observation_definition_and_scope/observation_vs_action_boundary.json",
    "external_observation_definition_and_scope/allowed_future_observation_modes.json",
    "external_observation_definition_and_scope/disallowed_l6_2_observation_modes.json",
    "pre_observation_packet_schema/pre_observation_packet_schema.json",
    "pre_observation_packet_schema/pre_observation_packet_required_fields.json",
    "pre_observation_packet_schema/pre_observation_packet_examples.json",
    "pre_observation_packet_schema/invalid_pre_observation_packet_examples.json",
    "external_source_registry_and_policy/source_type_registry.json",
    "external_source_registry_and_policy/source_trust_tier_policy.json",
    "external_source_registry_and_policy/source_freshness_policy.json",
    "external_source_registry_and_policy/source_risk_policy.json",
    "external_source_registry_and_policy/evidence_trace_policy.json",
    "external_observation_permission_gate/observation_permission_gate_contract.json",
    "external_observation_permission_gate/observation_gate_decision_matrix.json",
    "external_observation_permission_gate/valid_blocked_observation_packet_decisions.json",
    "external_observation_permission_gate/invalid_observation_packet_decisions.json",
    "manual_external_evidence_import_sandbox/manual_import_contract.json",
    "manual_external_evidence_import_sandbox/manual_import_packet_schema.json",
    "manual_external_evidence_import_sandbox/manual_import_static_fixture_examples.json",
    "manual_external_evidence_import_sandbox/manual_import_evidence_registry.json",
    "manual_external_evidence_import_sandbox/manual_import_validation_matrix.json",
    "observation_to_mvp_artifact_linker/observation_to_artifact_link_contract.json",
    "observation_to_mvp_artifact_linker/l6_1_artifact_case_reference_map.json",
    "observation_to_mvp_artifact_linker/observation_refinement_targets.json",
    "observation_to_mvp_artifact_linker/artifact_update_candidate_policy.json",
    "observation_claim_boundary_and_freshness/claim_boundary_policy.json",
    "observation_claim_boundary_and_freshness/freshness_window_policy.json",
    "observation_claim_boundary_and_freshness/evidence_claim_mapping.json",
    "observation_claim_boundary_and_freshness/unsupported_claim_policy.json",
    "observation_claim_boundary_and_freshness/conflicting_source_policy.json",
    "l6_external_observation_strategic_residual_loop/l6_2_cieu_like_fixture.json",
    "l6_external_observation_strategic_residual_loop/l6_2_strategic_residual_delta.json",
    "l6_external_observation_strategic_residual_loop/l6_2_meta_learning_update_candidate.json",
    "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json",
    "l6_external_observation_boundary_readiness/l6_2_next_milestone_recommendation.json",
    "l6_external_observation_boundary_readiness/l6_2_blockers.json",
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

REQUIRED_SOURCE_TYPES = {
    "official_policy_source",
    "official_program_source",
    "public_market_source",
    "public_platform_source",
    "public_repository_source",
    "public_document_source",
    "user_supplied_document",
    "user_supplied_summary",
    "manually_imported_note",
    "manually_imported_screenshot_summary",
    "future_approved_read_only_search_result",
}

NO_ACTION_RECEIPTS = [
    "no_network_receipt.json",
    "no_api_receipt.json",
    "no_scraping_receipt.json",
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
    assert "Built L6.2 governed external observation boundary artifacts" in result.stdout


def test_required_directories_and_json_parse() -> None:
    for directory in REQUIRED_DIRS:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_JSON:
        assert (ROOT / path).is_file(), path
        load_json(path)


def test_contract_boundary_only_and_safety_flags() -> None:
    contract = load_json("l6_governed_external_observation_boundary/l6_2_milestone_contract.json")
    assert contract["milestone_id"] == "L6.2"
    assert contract["input_milestones"] == ["L6.0", "L6.1"]
    assert contract["mode"] == "boundary_only"
    assert contract["sandbox_only"] is True
    assert contract["static_fixture_generation_authorized"] is True
    assert contract["manual_evidence_import_contract_authorized"] is True
    assert contract["requires_review_before_any_real_observation"] is True
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
        "canonical_update_authorized",
        "direct_y_star_mutation_authorized",
        "brain_writeback_authorized",
        "memory_ingestion_authorized",
    ]:
        assert contract[field] is False
    for field in BLOCKED_FLAGS:
        assert contract["safety_flags"][field] is False


def test_observation_definition_distinguishes_observation_from_action() -> None:
    definition = load_json(
        "external_observation_definition_and_scope/external_observation_definition.json"
    )
    assert definition["real_external_observation_authorized_now"] is False
    denied_meanings = set(definition["external_observation_does_not_mean"])
    assert "publication" in denied_meanings
    assert "outreach" in denied_meanings
    assert "payment" in denied_meanings
    boundary = load_json(
        "external_observation_definition_and_scope/observation_vs_action_boundary.json"
    )
    assert boundary["l6_2_all_real_observation_blocked"] is True
    assert all(boundary["action_boundary"].values())


def test_pre_observation_packet_schema_and_examples_are_blocked() -> None:
    schema = load_json("pre_observation_packet_schema/pre_observation_packet_schema.json")
    assert set(PACKET_FIELDS).issubset(schema["required_fields"])
    assert schema["real_observation_authorized_by_schema"] is False
    examples = load_json("pre_observation_packet_schema/pre_observation_packet_examples.json")
    assert examples["example_status"] == "dry_run_static_examples_only"
    assert examples["examples"]
    for packet in examples["examples"]:
        for field in PACKET_FIELDS:
            assert field in packet
        assert packet["network_required"] is False
        assert packet["publication_required"] is False
        assert packet["outreach_required"] is False
        assert packet["approval_required_before_real_observation"] is True
        assert packet["real_external_observation_authorized"] is False


def test_source_registry_is_structural_not_opportunity_strategy() -> None:
    registry = load_json("external_source_registry_and_policy/source_type_registry.json")
    assert registry["source_type_status"] == "source_types_not_opportunity_categories"
    source_types = {entry["source_type"] for entry in registry["source_types"]}
    assert REQUIRED_SOURCE_TYPES.issubset(source_types)
    assert all(entry["not_strategy_category"] is True for entry in registry["source_types"])
    trust = load_json("external_source_registry_and_policy/source_trust_tier_policy.json")
    assert trust["trust_policy_mode"] == "structural_indicators_only"
    assert trust["semantic_truth_scoring_enabled"] is False
    serialized = json.dumps(trust)
    assert "truth_score" not in serialized
    assert "semantic_truth_score" not in serialized
    assert "market_success_score" not in serialized


def test_permission_gate_blocks_real_observation() -> None:
    gate = load_json("external_observation_permission_gate/observation_permission_gate_contract.json")
    assert gate["real_observation_authorized_in_l6_2"] is False
    assert "block_real_observation_l6_2" in gate["decisions"]
    assert "allow_static_fixture_only" in gate["decisions"]
    valid = load_json(
        "external_observation_permission_gate/valid_blocked_observation_packet_decisions.json"
    )
    for decision in valid["packet_decisions"]:
        assert decision["decision"] == "allow_static_fixture_only"
        assert decision["real_observation_authorized"] is False
    invalid = load_json(
        "external_observation_permission_gate/invalid_observation_packet_decisions.json"
    )
    assert {
        "deny_due_to_network_required_now",
        "deny_due_to_contact_required",
        "deny_due_to_missing_trace_plan",
    }.issubset({decision["decision"] for decision in invalid["packet_decisions"]})


def test_manual_import_sandbox_does_not_fetch_urls() -> None:
    contract = load_json("manual_external_evidence_import_sandbox/manual_import_contract.json")
    assert contract["url_fetch_authorized"] is False
    assert contract["external_action_authorized"] is False
    examples = load_json(
        "manual_external_evidence_import_sandbox/manual_import_static_fixture_examples.json"
    )
    for example in examples["examples"]:
        assert example["source_locator_provided"] in {True, False}
        assert example["freshness_declared"] in {
            "not_current_fact",
            "date_missing_static_fixture",
        }
        assert example["external_action_authorized"] is False
        assert example["url_fetched"] is False


def test_observation_to_artifact_linker_creates_candidates_only() -> None:
    linker = load_json(
        "observation_to_mvp_artifact_linker/observation_to_artifact_link_contract.json"
    )
    assert linker["link_mode"] == "candidate_refinement_only"
    assert linker["direct_artifact_mutation_authorized"] is False
    assert linker["canonical_update_authorized"] is False
    policy = load_json(
        "observation_to_mvp_artifact_linker/artifact_update_candidate_policy.json"
    )["candidate_policy"]
    assert policy["eligible_for_review_queue"] is True
    assert policy["approved"] is False
    assert policy["applied"] is False
    assert policy["direct_artifact_mutation_authorized"] is False


def test_claim_boundary_requires_trace_freshness_and_limits() -> None:
    policy = load_json("observation_claim_boundary_and_freshness/claim_boundary_policy.json")
    required = {
        "source trace",
        "date or date_missing marker",
        "freshness class",
        "claim scope",
        "claim limitation",
        "unsupported inference marker",
        "conflict marker if applicable",
        "review status",
    }
    assert required.issubset(set(policy["required_claim_fields"]))
    assert policy["semantic_truth_scoring_enabled"] is False
    freshness = load_json("observation_claim_boundary_and_freshness/freshness_window_policy.json")
    assert freshness["current_fact_claims_authorized_in_l6_2"] is False


def test_no_action_receipts_all_block_execution() -> None:
    for filename in NO_ACTION_RECEIPTS:
        receipt = load_json(f"external_observation_no_action_receipts/{filename}")
        assert receipt["authorized_in_l6_2"] is False
        assert receipt["executed_in_l6_2"] is False
        assert receipt["future_boundary_required"] == "L6.3 Controlled External Observation Sandbox v0"


def test_strategic_residual_and_meta_learning_are_review_only() -> None:
    fixture = load_json(
        "l6_external_observation_strategic_residual_loop/l6_2_cieu_like_fixture.json"
    )
    assert fixture["event_mode"] == "l6_2_governed_external_observation_boundary_fixture"
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in fixture
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    update = load_json(
        "l6_external_observation_strategic_residual_loop/l6_2_meta_learning_update_candidate.json"
    )
    assert update["eligible_for_review_queue"] is True
    assert update["eligible_for_direct_brain_writeback"] is False
    assert update["eligible_for_direct_memory_ingestion"] is False
    assert update["eligible_for_candidate_auto_approval"] is False
    assert update["eligible_for_direct_strategy_mutation"] is False
    assert update["approved"] is False
    assert update["applied"] is False


def test_readiness_blocks_real_network_and_recommends_future_boundary() -> None:
    readiness = load_json(
        "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json"
    )
    assert readiness["l6_2_external_observation_boundary_complete"] is True
    assert readiness["ready_for_l6_3_controlled_external_observation_sandbox"] is True
    for field in [
        "ready_for_real_network_observation",
        "ready_for_publication",
        "ready_for_outreach",
        "ready_for_payment",
        "ready_for_revenue_execution",
        "ready_for_mcp_execution",
        "ready_for_canonical_update",
        "ready_for_brain_memory_writeback",
    ]:
        assert readiness[field] is False


def test_l6_2_code_does_not_import_or_invoke_network_tools() -> None:
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
    for path in (ROOT / "l6_governed_external_observation_boundary").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text


def test_console_read_model_command_works() -> None:
    run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    result = run_command(
        ["python3", "console_read_model/cli/team_console.py", "governed-external-observation-boundary"]
    )
    assert "L6.2 Governed External Observation Boundary" in result.stdout
    assert "real external observation authorized: False" in result.stdout
    assert "ready for L6.3 controlled external observation sandbox: True" in result.stdout
