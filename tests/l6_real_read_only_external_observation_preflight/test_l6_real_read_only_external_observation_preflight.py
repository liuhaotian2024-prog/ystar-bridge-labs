from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "l6_real_read_only_external_observation_preflight"
    / "tools"
    / "build_l6_real_read_only_external_observation_preflight.py"
)

REQUIRED_DIRS = [
    "l6_real_read_only_external_observation_preflight",
    "real_observation_candidate_selector",
    "real_read_only_observation_preflight_contract",
    "source_allowlist_and_risk_policy",
    "real_observation_approval_packet_schema",
    "observation_operator_handoff",
    "observation_network_isolation_preflight",
    "observation_evidence_capture_preflight",
    "observation_abort_rollback_quarantine_policy",
    "read_only_observation_no_action_guarantees",
    "real_observation_preflight_decision_gate",
    "l6_real_observation_preflight_strategic_residual_loop",
    "l6_real_observation_preflight_readiness",
]

REQUIRED_JSON = [
    "l6_real_read_only_external_observation_preflight/l6_4_milestone_contract.json",
    "l6_real_read_only_external_observation_preflight/l6_4_preflight_scope.json",
    "l6_real_read_only_external_observation_preflight/l6_4_safety_flags.json",
    "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
    "real_observation_candidate_selector/l6_3_observation_case_inventory.json",
    "real_observation_candidate_selector/real_observation_candidate_matrix.json",
    "real_observation_candidate_selector/selected_real_observation_candidates.json",
    "real_observation_candidate_selector/deferred_real_observation_candidates.json",
    "real_read_only_observation_preflight_contract/read_only_observation_definition.json",
    "real_read_only_observation_preflight_contract/preflight_requirement_registry.json",
    "real_read_only_observation_preflight_contract/read_only_vs_action_boundary.json",
    "real_read_only_observation_preflight_contract/real_observation_disallowed_action_registry.json",
    "source_allowlist_and_risk_policy/source_allowlist_policy.json",
    "source_allowlist_and_risk_policy/source_denylist_policy.json",
    "source_allowlist_and_risk_policy/source_risk_tier_policy.json",
    "source_allowlist_and_risk_policy/source_locator_policy.json",
    "real_observation_approval_packet_schema/real_observation_approval_packet_schema.json",
    "real_observation_approval_packet_schema/approval_packet_required_fields.json",
    "real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json",
    "real_observation_approval_packet_schema/invalid_approval_packet_examples.json",
    "observation_operator_handoff/operator_handoff_contract.json",
    "observation_operator_handoff/operator_handoff_packet_examples.json",
    "observation_operator_handoff/operator_non_action_oath.json",
    "observation_network_isolation_preflight/network_isolation_requirement.json",
    "observation_network_isolation_preflight/permitted_future_tool_profile.json",
    "observation_network_isolation_preflight/prohibited_tool_profile.json",
    "observation_network_isolation_preflight/environment_preflight_checklist.json",
    "observation_evidence_capture_preflight/evidence_capture_contract.json",
    "observation_evidence_capture_preflight/citation_capture_schema.json",
    "observation_evidence_capture_preflight/source_snapshot_metadata_schema.json",
    "observation_evidence_capture_preflight/evidence_packet_schema.json",
    "observation_abort_rollback_quarantine_policy/abort_condition_registry.json",
    "observation_abort_rollback_quarantine_policy/quarantine_policy.json",
    "observation_abort_rollback_quarantine_policy/evidence_rejection_policy.json",
    "observation_abort_rollback_quarantine_policy/rollback_non_mutation_policy.json",
    "real_observation_preflight_decision_gate/preflight_decision_gate_contract.json",
    "real_observation_preflight_decision_gate/candidate_preflight_decisions.json",
    "real_observation_preflight_decision_gate/blocked_real_observation_decisions.json",
    "real_observation_preflight_decision_gate/future_entry_conditions.json",
    "l6_real_observation_preflight_strategic_residual_loop/l6_4_cieu_like_fixture.json",
    "l6_real_observation_preflight_strategic_residual_loop/l6_4_strategic_residual_delta.json",
    "l6_real_observation_preflight_strategic_residual_loop/l6_4_meta_learning_update_candidate.json",
    "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json",
    "l6_real_observation_preflight_readiness/l6_4_next_milestone_recommendation.json",
    "l6_real_observation_preflight_readiness/l6_4_blockers.json",
]

RECEIPTS = [
    "no_network_execution_receipt.json",
    "no_real_observation_receipt.json",
    "no_api_receipt.json",
    "no_scraping_receipt.json",
    "no_browser_fetch_receipt.json",
    "no_publication_receipt.json",
    "no_outreach_receipt.json",
    "no_payment_receipt.json",
    "no_revenue_execution_receipt.json",
    "no_mcp_execution_receipt.json",
    "no_live_behavior_receipt.json",
    "no_cieu_db_write_receipt.json",
    "no_canonical_mutation_receipt.json",
    "no_brain_memory_writeback_receipt.json",
    "no_direct_y_star_mutation_receipt.json",
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
    "cieu_db_write_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "real_canonical_update_application_enabled",
    "real_y_star_direct_mutation_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
]

APPROVAL_PACKET_FIELDS = [
    "approval_packet_id",
    "linked_candidate_id",
    "linked_l6_3_packet_id",
    "linked_l6_1_artifact_case_id",
    "observation_question",
    "source_type",
    "source_locator_placeholder",
    "expected_evidence_type",
    "freshness_requirement",
    "trust_tier_requirement",
    "privacy_risk",
    "ip_risk",
    "no_login_required",
    "no_account_required",
    "no_contact_required",
    "no_payment_required",
    "no_form_submission_required",
    "no_write_or_post_required",
    "no_download_sensitive_data_required",
    "no_mcp_required",
    "no_publication_required",
    "no_outreach_required",
    "no_revenue_action_required",
    "no_canonical_update_required",
    "no_brain_memory_writeback_required",
    "evidence_capture_plan",
    "citation_plan",
    "abort_conditions",
    "quarantine_conditions",
    "operator_handoff_required",
    "reviewer_required",
    "approval_status",
    "real_observation_authorized",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)


def test_builder_runs() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert "Built L6.4 real read-only external observation preflight artifacts" in result.stdout


def test_required_directories_and_json_parse() -> None:
    for directory in REQUIRED_DIRS:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_JSON:
        assert (ROOT / path).is_file(), path
        load_json(path)


def test_contract_is_preflight_only_and_blocks_real_execution() -> None:
    contract = load_json(
        "l6_real_read_only_external_observation_preflight/l6_4_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.4"
    assert contract["input_milestones"] == ["L6.0", "L6.1", "L6.2", "L6.3"]
    assert contract["mode"] == "preflight_only"
    assert contract["preflight_only"] is True
    assert contract["sandbox_only"] is True
    assert contract["future_real_read_only_observation_candidate_allowed"] is True
    assert contract["approval_packet_generation_authorized"] is True
    assert contract["operator_handoff_plan_authorized"] is True
    assert contract["evidence_capture_plan_authorized"] is True
    assert contract["real_observation_execution_authorized"] is False
    assert contract["requires_future_explicit_approval_before_real_observation"] is True
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
        "cieu_db_write_authorized",
        "canonical_update_authorized",
        "direct_y_star_mutation_authorized",
        "brain_writeback_authorized",
        "memory_ingestion_authorized",
    ]:
        assert contract[field] is False
    for flag in BLOCKED_FLAGS:
        assert contract["safety_flags"][flag] is False


def test_candidate_selector_is_structural_read_only_preflight() -> None:
    selected = load_json("real_observation_candidate_selector/selected_real_observation_candidates.json")
    assert 1 <= selected["candidate_count"] <= 3
    assert selected["selection_mode"] == "structural_read_only_preflight_candidate_selection"
    assert selected["selected_by_hardcoded_opportunity_category"] is False
    assert selected["hardcoded_opportunity_class_used"] is False
    for candidate in selected["candidates"]:
        factors = set(candidate["selection_factors"])
        assert "evidence gap remains after L6.3 fixture" in factors
        assert "real source evidence is necessary" in factors
        assert "observation can be read-only" in factors
        assert "no contact required" in factors
        assert "no login required" in factors
        assert "no payment required" in factors
        assert "no form submission required" in factors
        assert "no publication required" in factors
        assert "no account creation required" in factors
        assert "no MCP execution required" in factors
        assert "source locator can be represented" in factors
        assert "claim boundary is clear" in factors
        assert "expected evidence type is clear" in factors
        assert "freshness requirement is clear" in factors
        assert candidate["real_observation_authorized_now"] is False
        assert candidate["preflight_authorized_now"] is True
        assert candidate["future_approval_required"] is True


def test_read_only_definition_excludes_external_actions() -> None:
    definition = load_json(
        "real_read_only_observation_preflight_contract/read_only_observation_definition.json"
    )
    means = set(definition["means"])
    for forbidden_boundary in [
        "no account creation",
        "no comment/post/message",
        "no form submission",
        "no purchase/payment",
        "no scraping automation",
        "no external mutation",
        "no customer contact",
        "no publication",
        "no revenue action",
        "no canonical update",
        "no brain/memory writeback",
        "no direct Y* mutation",
    ]:
        assert forbidden_boundary in means
    assert definition["real_observation_authorized_in_l6_4"] is False


def test_source_allowlist_and_denylist_exist() -> None:
    allowlist = load_json("source_allowlist_and_risk_policy/source_allowlist_policy.json")
    denylist = load_json("source_allowlist_and_risk_policy/source_denylist_policy.json")
    allow_ids = {item["source_type_id"] for item in allowlist["source_types"]}
    deny_ids = {item["source_type_id"] for item in denylist["source_types"]}
    assert "official_program_page" in allow_ids
    assert "official_policy_page" in allow_ids
    assert "public_repository_page" in allow_ids
    assert "public_static_informational_page" in allow_ids
    for denied in [
        "login_required_page",
        "payment_required_page",
        "private_customer_data",
        "form_submission_endpoint",
        "account_creation_flow",
        "shopping_checkout",
        "payment_processor_page",
        "production_mcp_tool_or_resource",
        "live_agent_control_surface",
        "access_control_bypass_required_page",
    ]:
        assert denied in deny_ids
    for item in allowlist["source_types"]:
        assert item["real_access_authorized_in_l6_4"] is False
    for item in denylist["source_types"]:
        assert item["denied_in_l6_4"] is True


def test_approval_packet_schema_and_examples_block_real_observation() -> None:
    schema = load_json("real_observation_approval_packet_schema/real_observation_approval_packet_schema.json")
    examples = load_json("real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json")
    assert set(APPROVAL_PACKET_FIELDS).issubset(set(schema["required_fields"]))
    assert examples["example_count"] == len(examples["approval_packets"])
    for packet in examples["approval_packets"]:
        for field in APPROVAL_PACKET_FIELDS:
            assert field in packet
        assert packet["approval_status"] in {
            "preflight_generated",
            "blocked_pending_future_approval",
        }
        assert packet["real_observation_authorized"] is False
        assert packet["no_login_required"] is True
        assert packet["no_account_required"] is True
        assert packet["no_contact_required"] is True
        assert packet["no_payment_required"] is True
        assert packet["no_form_submission_required"] is True
        assert packet["no_write_or_post_required"] is True
        assert packet["no_mcp_required"] is True
        assert packet["no_publication_required"] is True
        assert packet["no_outreach_required"] is True
        assert packet["no_revenue_action_required"] is True
        assert packet["no_canonical_update_required"] is True
        assert packet["no_brain_memory_writeback_required"] is True


def test_operator_handoff_and_network_isolation_are_plan_only() -> None:
    handoff = load_json("observation_operator_handoff/operator_handoff_contract.json")
    oath = load_json("observation_operator_handoff/operator_non_action_oath.json")
    network = load_json("observation_network_isolation_preflight/network_isolation_requirement.json")
    assert handoff["handoff_mode"] == "future_operator_plan_only"
    assert handoff["operator_handoff_exercised_in_l6_4"] is False
    assert handoff["real_observation_authorized_in_l6_4"] is False
    assert "no payment" in oath["operator_affirms"]
    assert "no contact" in oath["operator_affirms"]
    assert network["requirement_mode"] == "requirements_only_no_network_check_executed"
    assert network["network_checks_executed"] is False
    assert network["real_network_authorized"] is False


def test_evidence_capture_has_citation_freshness_claim_boundary_and_no_action_fields() -> None:
    contract = load_json("observation_evidence_capture_preflight/evidence_capture_contract.json")
    evidence_schema = load_json("observation_evidence_capture_preflight/evidence_packet_schema.json")
    required = set(contract["required_capture_fields"])
    for field in [
        "source_locator",
        "source_title",
        "observed_at_timestamp",
        "source_date_or_date_missing",
        "freshness_class",
        "claim_boundary",
        "citation_trace",
        "external_action_taken",
        "publication_taken",
        "outreach_taken",
        "payment_taken",
    ]:
        assert field in required
    defaults = evidence_schema["default_no_action_fields"]
    assert defaults["external_action_taken"] is False
    assert defaults["publication_taken"] is False
    assert defaults["outreach_taken"] is False
    assert defaults["payment_taken"] is False


def test_abort_quarantine_policy_includes_disallowed_action_triggers() -> None:
    registry = load_json("observation_abort_rollback_quarantine_policy/abort_condition_registry.json")
    conditions = {item["condition"] for item in registry["abort_conditions"]}
    for condition in [
        "login required unexpectedly",
        "payment required unexpectedly",
        "account creation requested",
        "form submission required",
        "contact action required",
        "private/sensitive data encountered",
        "source asks for interaction",
        "source appears malicious",
        "source conflicts with approved scope",
        "page requires automation/scraping",
        "source locator mismatch",
        "claim scope exceeds approval packet",
        "operator uncertainty",
    ]:
        assert condition in conditions


def test_no_action_receipts_all_executed_flags_false() -> None:
    for filename in RECEIPTS:
        receipt = load_json(f"read_only_observation_no_action_guarantees/{filename}")
        assert receipt["authorized_in_l6_4"] is False
        assert receipt["executed_in_l6_4"] is False
        assert receipt["future_boundary_required"] == (
            "L6.5 Controlled Real Read-Only Observation Pilot Design v0"
        )


def test_preflight_decision_gate_blocks_real_observation() -> None:
    decisions = load_json("real_observation_preflight_decision_gate/candidate_preflight_decisions.json")
    assert decisions["decision_count"] == len(decisions["decisions"])
    for decision in decisions["decisions"]:
        assert decision["real_observation_decision"] == "blocked_pending_future_explicit_approval"
        assert decision["preflight_decision"] == "preflight_packet_ready"
        assert decision["real_network_authorized"] is False
        assert decision["execution_authorized"] is False
        assert decision["review_required"] is True
        assert decision["approval_required"] is True
        assert decision["future_milestone_required"] is True


def test_cieu_fixture_and_meta_learning_candidate_are_review_only() -> None:
    fixture = load_json("l6_real_observation_preflight_strategic_residual_loop/l6_4_cieu_like_fixture.json")
    learning = load_json(
        "l6_real_observation_preflight_strategic_residual_loop/l6_4_meta_learning_update_candidate.json"
    )
    assert fixture["event_mode"] == "l6_4_real_read_only_external_observation_preflight_fixture"
    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in fixture
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert fixture["real_observation_performed"] is False
    assert learning["eligible_for_review_queue"] is True
    assert learning["eligible_for_direct_brain_writeback"] is False
    assert learning["eligible_for_direct_memory_ingestion"] is False
    assert learning["eligible_for_candidate_auto_approval"] is False
    assert learning["eligible_for_direct_strategy_mutation"] is False
    assert learning["approved"] is False
    assert learning["applied"] is False


def test_readiness_blocks_actual_network_observation_and_recommends_l6_5() -> None:
    readiness = load_json("l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json")
    assert readiness["l6_4_real_read_only_observation_preflight_complete"] is True
    assert readiness["ready_for_l6_5_controlled_real_read_only_observation_pilot_design"] is True
    assert readiness["ready_for_actual_network_observation_now"] is False
    assert readiness["ready_for_scraping"] is False
    assert readiness["ready_for_publication"] is False
    assert readiness["ready_for_outreach"] is False
    assert readiness["ready_for_payment"] is False
    assert readiness["ready_for_revenue_execution"] is False
    assert readiness["ready_for_mcp_execution"] is False
    assert readiness["ready_for_canonical_update"] is False
    assert readiness["ready_for_brain_memory_writeback"] is False
    assert readiness["next_recommended_milestone"] == (
        "L6.5 Controlled Real Read-Only Observation Pilot Design v0"
    )


def test_console_command_works() -> None:
    run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    result = run_command(
        ["python3", "console_read_model/cli/team_console.py", "real-read-only-observation-preflight"]
    )
    assert "# L6.4 Real Read-Only External Observation Preflight" in result.stdout
    assert "real external observation authorized: False" in result.stdout
    assert "ready for actual network observation now: False" in result.stdout


def test_l6_4_builder_does_not_import_or_call_network_execution_tools() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    forbidden_snippets = [
        "import requests",
        "import httpx",
        "import urllib.request",
        "import aiohttp",
        "import selenium",
        "import playwright",
        "import socket",
        "subprocess.run",
        "curl ",
        "wget ",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
