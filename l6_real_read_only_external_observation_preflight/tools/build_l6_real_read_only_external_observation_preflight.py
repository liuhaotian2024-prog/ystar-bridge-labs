#!/usr/bin/env python3
"""Build deterministic L6.4 real read-only external observation preflight outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.4"
MILESTONE_NAME = "Real Read-Only External Observation Preflight v0"
NEXT_MILESTONE = "L6.5 Controlled Real Read-Only Observation Pilot Design v0"

PLACEHOLDER_LOCATOR_MARKER = (
    "PLACEHOLDER LOCATOR ONLY - NOT FETCHED - NOT OPENED - NOT VERIFIED CURRENT FACT - "
    "NOT AUTHORIZED FOR REAL OBSERVATION - NOT AUTHORIZED FOR PUBLICATION - "
    "NOT AUTHORIZED FOR OUTREACH - NOT AUTHORIZED FOR PAYMENT - NOT AUTHORIZED FOR "
    "REVENUE EXECUTION - NOT AUTHORIZED FOR CANONICAL UPDATE"
)

INPUT_REFS = {
    "l6_0_generated_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_0_selection_ranking": "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "l6_0_mvp_plans": "minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json",
    "l6_0_readiness": (
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json"
    ),
    "l6_1_summary": "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
    "l6_1_case_index": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_1_readiness": "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
    "l6_2_summary": "l6_governed_external_observation_boundary/l6_2_summary.json",
    "l6_2_pre_observation_schema": (
        "pre_observation_packet_schema/pre_observation_packet_schema.json"
    ),
    "l6_2_source_registry": "external_source_registry_and_policy/source_type_registry.json",
    "l6_2_permission_gate": (
        "external_observation_permission_gate/observation_permission_gate_contract.json"
    ),
    "l6_2_readiness": (
        "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json"
    ),
    "l6_3_summary": "l6_controlled_external_observation_sandbox/l6_3_summary.json",
    "l6_3_selected_cases": "l6_observation_case_selector/selected_observation_cases.json",
    "l6_3_packet_index": "controlled_pre_observation_packets/pre_observation_packet_index.json",
    "l6_3_fixture_index": "static_manual_observation_fixtures/observation_fixture_index.json",
    "l6_3_refinement_index": (
        "observation_to_artifact_refinement_candidates/refinement_candidate_index.json"
    ),
    "l6_3_readiness": "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "external_observation_execution_enabled": False,
    "network_enabled": False,
    "api_enabled": False,
    "scraping_enabled": False,
    "browser_fetch_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "cieu_db_write_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "strategy_mutation_enabled": False,
    "candidate_auto_approval_enabled": False,
    "real_candidate_approval_enabled": False,
    "real_canonical_policy_mutation_enabled": False,
    "real_canonical_update_application_enabled": False,
    "real_release_execution_enabled": False,
    "real_y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
    "revenue_execution_enabled": False,
    "external_market_scan_enabled": False,
    "public_content_publication_enabled": False,
    "publication_enabled": False,
    "outreach_enabled": False,
    "payment_enabled": False,
}

L6_4_FLAGS = {
    "l6_4_preflight_only": True,
    "l6_4_sandbox_only": True,
    "l6_4_future_real_read_only_observation_candidate_allowed": True,
    "l6_4_approval_packet_generation_enabled": True,
    "l6_4_operator_handoff_plan_enabled": True,
    "l6_4_evidence_capture_plan_enabled": True,
    "l6_4_real_observation_execution_enabled": False,
    "l6_4_network_enabled": False,
    "l6_4_api_enabled": False,
    "l6_4_scraping_enabled": False,
    "l6_4_browser_fetch_enabled": False,
    "l6_4_publication_enabled": False,
    "l6_4_outreach_enabled": False,
    "l6_4_payment_enabled": False,
    "l6_4_revenue_execution_enabled": False,
    "l6_4_mcp_execution_enabled": False,
    "l6_4_live_behavior_enabled": False,
    "l6_4_canonical_update_enabled": False,
    "l6_4_brain_writeback_enabled": False,
    "l6_4_memory_ingestion_enabled": False,
    "l6_4_direct_y_star_mutation_enabled": False,
}

BLOCKED_AUTHORIZATIONS = {
    "real_external_observation_authorized": False,
    "network_authorized": False,
    "api_authorized": False,
    "scraping_authorized": False,
    "browser_fetch_authorized": False,
    "external_action_authorized": False,
    "publication_authorized": False,
    "outreach_authorized": False,
    "payment_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "live_behavior_authorized": False,
    "cieu_db_write_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
}

SELECTION_FACTORS = [
    "evidence gap remains after L6.3 fixture",
    "real source evidence is necessary",
    "observation can be read-only",
    "no contact required",
    "no login required",
    "no payment required",
    "no form submission required",
    "no publication required",
    "no account creation required",
    "no MCP execution required",
    "source locator can be represented",
    "claim boundary is clear",
    "expected evidence type is clear",
    "freshness requirement is clear",
    "review value is high",
    "downside risk is low",
    "future operator execution can be manually controlled",
]

PRE_FLIGHT_REQUIREMENTS = [
    "candidate linked to L6.3 packet",
    "observation question defined",
    "source type declared",
    "source locator placeholder present",
    "expected evidence type declared",
    "freshness requirement declared",
    "trust tier requirement declared",
    "privacy risk assessed",
    "IP risk assessed",
    "no-contact guarantee present",
    "no-payment guarantee present",
    "no-publication guarantee present",
    "no-write guarantee present",
    "evidence capture plan present",
    "citation/source trace plan present",
    "abort conditions present",
    "quarantine policy present",
    "review required",
    "explicit future approval required",
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

ALLOWLIST_SOURCE_TYPES = [
    "official_program_page",
    "official_policy_page",
    "official_platform_policy_page",
    "public_repository_page",
    "public_document_page",
    "user_supplied_public_locator",
    "user_supplied_document",
    "public_static_informational_page",
]

DENYLIST_SOURCE_TYPES = [
    "login_required_page",
    "payment_required_page",
    "private_customer_data",
    "personal_account_inbox",
    "private_social_media_messages",
    "form_submission_endpoint",
    "account_creation_flow",
    "shopping_checkout",
    "payment_processor_page",
    "production_mcp_tool_or_resource",
    "live_agent_control_surface",
    "access_control_bypass_required_page",
]

ABORT_CONDITIONS = [
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
]

NO_ACTION_RECEIPTS = {
    "no_network_execution_receipt.json": "network_execution",
    "no_real_observation_receipt.json": "real_observation",
    "no_api_receipt.json": "api",
    "no_scraping_receipt.json": "scraping",
    "no_browser_fetch_receipt.json": "browser_fetch",
    "no_publication_receipt.json": "publication",
    "no_outreach_receipt.json": "outreach",
    "no_payment_receipt.json": "payment",
    "no_revenue_execution_receipt.json": "revenue_execution",
    "no_mcp_execution_receipt.json": "mcp_execution",
    "no_live_behavior_receipt.json": "live_behavior",
    "no_cieu_db_write_receipt.json": "cieu_db_write",
    "no_canonical_mutation_receipt.json": "canonical_mutation",
    "no_brain_memory_writeback_receipt.json": "brain_memory_writeback",
    "no_direct_y_star_mutation_receipt.json": "direct_y_star_mutation",
}


class BuildError(Exception):
    """Raised when generated artifacts cannot be built safely."""


def read_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BuildError(f"Refusing to read outside repo: {relative_path}") from exc
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(relative_path: str, payload: Any, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
        f.write("\n")
    generated.append(relative_path)


def write_text(relative_path: str, text: str, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated.append(relative_path)


def with_common(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, "safety_flags": SAFETY_FLAGS, "l6_4_flags": L6_4_FLAGS}


def existing_input_map() -> tuple[dict[str, str], list[str]]:
    refs: dict[str, str] = {}
    gaps: list[str] = []
    for key, rel in INPUT_REFS.items():
        if (ROOT / rel).exists():
            refs[key] = rel
        else:
            gaps.append(rel)
    return refs, gaps


def packet_by_id() -> dict[str, dict[str, Any]]:
    packet_index = read_json(INPUT_REFS["l6_3_packet_index"]) or {}
    packets: dict[str, dict[str, Any]] = {}
    for entry in packet_index.get("packets", []):
        packet = read_json(entry.get("path", "")) or {}
        if packet.get("packet_id"):
            packets[packet["packet_id"]] = packet
    return packets


def fixture_by_packet_id() -> dict[str, dict[str, Any]]:
    fixture_index = read_json(INPUT_REFS["l6_3_fixture_index"]) or {}
    fixtures: dict[str, dict[str, Any]] = {}
    for entry in fixture_index.get("fixtures", []):
        fixture = read_json(entry.get("path", "")) or {}
        if fixture.get("linked_packet_id"):
            fixtures[fixture["linked_packet_id"]] = fixture
    return fixtures


def selected_l6_3_cases() -> list[dict[str, Any]]:
    selected = read_json(INPUT_REFS["l6_3_selected_cases"]) or {}
    cases = selected.get("selected_cases", [])[:3]
    if cases:
        return cases
    return [
        {
            "selected_case_id": "observation_case_001",
            "source_l6_1_case_id": "case_001",
            "linked_l6_0_hypothesis_id": "hypothesis_placeholder",
            "evidence_gap": ["missing external evidence"],
            "proposed_observation_question": "What future read-only source evidence is needed?",
            "expected_evidence_type": "source_summary",
        }
    ]


def build_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packets = packet_by_id()
    fixtures = fixture_by_packet_id()
    selected_cases = selected_l6_3_cases()
    source_types = [
        "official_policy_page",
        "public_document_page",
        "user_supplied_public_locator",
    ]
    candidates: list[dict[str, Any]] = []
    for index, case in enumerate(selected_cases[:3], start=1):
        packet_id = f"l6_3_pre_observation_packet_{index:03d}"
        packet = packets.get(packet_id, {})
        fixture = fixtures.get(packet_id, {})
        source_type = source_types[(index - 1) % len(source_types)]
        candidates.append(
            with_common(
                {
                    "candidate_id": f"l6_4_real_observation_candidate_{index:03d}",
                    "linked_l6_3_packet_id": packet.get("packet_id", packet_id),
                    "linked_l6_3_fixture_id": fixture.get(
                        "fixture_id", f"l6_3_static_manual_fixture_{index:03d}"
                    ),
                    "linked_l6_1_artifact_case_id": case.get(
                        "source_l6_1_case_id",
                        packet.get("linked_l6_1_artifact_case_id"),
                    ),
                    "linked_l6_0_hypothesis_id": case.get(
                        "linked_l6_0_hypothesis_id",
                        packet.get("linked_l6_hypothesis_id"),
                    ),
                    "evidence_gap": case.get(
                        "evidence_gap",
                        fixture.get("missing_context", ["real source evidence missing"]),
                    ),
                    "real_observation_question": packet.get(
                        "claim_to_validate_or_refine",
                        case.get("proposed_observation_question"),
                    ),
                    "proposed_source_type": source_type,
                    "source_locator_placeholder": (
                        f"{PLACEHOLDER_LOCATOR_MARKER} :: l6-4-candidate-{index:03d}"
                    ),
                    "expected_evidence_type": packet.get(
                        "expected_evidence_type",
                        case.get("expected_evidence_type", "bounded_source_summary"),
                    ),
                    "why_read_only_observation_is_needed": (
                        "The L6.3 fixture deliberately cannot establish current source "
                        "freshness, source authority, or real claim support."
                    ),
                    "why_no_action_is_required": (
                        "The evidence need can be framed as future view/read-only source "
                        "inspection; no contact, form submission, payment, posting, or "
                        "external mutation is required."
                    ),
                    "selection_factors": SELECTION_FACTORS,
                    "selected_by_hardcoded_opportunity_category": False,
                    "hardcoded_opportunity_class_used": False,
                    "login_required": False,
                    "account_required": False,
                    "contact_required": False,
                    "payment_required": False,
                    "form_submission_required": False,
                    "publication_required": False,
                    "mcp_execution_required": False,
                    "future_operator_execution_can_be_manually_controlled": True,
                    "real_observation_authorized_now": False,
                    "preflight_authorized_now": True,
                    "future_approval_required": True,
                }
            )
        )
    return candidates, []


def build_approval_packet(index: int, candidate: dict[str, Any]) -> dict[str, Any]:
    packet = with_common(
        {
            "approval_packet_id": f"l6_4_approval_packet_{index:03d}",
            "linked_candidate_id": candidate["candidate_id"],
            "linked_l6_3_packet_id": candidate["linked_l6_3_packet_id"],
            "linked_l6_1_artifact_case_id": candidate["linked_l6_1_artifact_case_id"],
            "observation_question": candidate["real_observation_question"],
            "source_type": candidate["proposed_source_type"],
            "source_locator_placeholder": candidate["source_locator_placeholder"],
            "expected_evidence_type": candidate["expected_evidence_type"],
            "freshness_requirement": "freshness_class_declared_before_review",
            "trust_tier_requirement": "structural_source_tier_declared_before_review",
            "privacy_risk": "low_if_public_read_only_and_no_sensitive_download",
            "ip_risk": "low_if citation-only-and-no bulk copying",
            "no_login_required": True,
            "no_account_required": True,
            "no_contact_required": True,
            "no_payment_required": True,
            "no_form_submission_required": True,
            "no_write_or_post_required": True,
            "no_download_sensitive_data_required": True,
            "no_mcp_required": True,
            "no_publication_required": True,
            "no_outreach_required": True,
            "no_revenue_action_required": True,
            "no_canonical_update_required": True,
            "no_brain_memory_writeback_required": True,
            "evidence_capture_plan": {
                "capture_title": True,
                "capture_locator": True,
                "capture_observed_at_timestamp": True,
                "capture_source_date_or_date_missing": True,
                "capture_claim_boundary": True,
                "capture_missing_context": True,
                "external_action_taken": False,
            },
            "citation_plan": {
                "citation_trace_required": True,
                "unsupported_claims_marked": True,
                "conflicts_marked_for_review": True,
            },
            "abort_conditions": ABORT_CONDITIONS,
            "quarantine_conditions": [
                "evidence exceeds approved scope",
                "source requires disallowed interaction",
                "operator uncertainty remains unresolved",
            ],
            "operator_handoff_required": True,
            "reviewer_required": True,
            "approval_status": "preflight_generated",
            "real_observation_authorized": False,
        }
    )
    return packet


def receipt(action_type: str) -> dict[str, Any]:
    return with_common(
        {
            "action_type": action_type,
            "authorized_in_l6_4": False,
            "executed_in_l6_4": False,
            "blocker_reference": (
                "l6_real_read_only_external_observation_preflight/"
                "l6_4_milestone_contract.json"
            ),
            "future_boundary_required": NEXT_MILESTONE,
        }
    )


def generate() -> list[str]:
    generated: list[str] = []
    refs, missing_refs = existing_input_map()
    candidates, deferred = build_candidates()
    approval_packets = [
        build_approval_packet(index, candidate)
        for index, candidate in enumerate(candidates, start=1)
    ]

    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": ["L6.0", "L6.1", "L6.2", "L6.3"],
            "mode": "preflight_only",
            "preflight_only": True,
            "sandbox_only": True,
            "future_real_read_only_observation_candidate_allowed": True,
            "approval_packet_generation_authorized": True,
            "operator_handoff_plan_authorized": True,
            "evidence_capture_plan_authorized": True,
            "real_observation_execution_authorized": False,
            "requires_future_explicit_approval_before_real_observation": True,
            "required_outputs": [
                "real observation candidate selector",
                "read-only observation preflight contract",
                "source allowlist and risk policy",
                "approval packet schema and blocked examples",
                "operator handoff plan",
                "network isolation requirements",
                "evidence capture requirements",
                "abort rollback quarantine policy",
                "no-action guarantees",
                "preflight decision gate",
                "strategic residual fixture",
                "readiness assessment",
            ],
            **BLOCKED_AUTHORIZATIONS,
        }
    )
    write_json(
        "l6_real_read_only_external_observation_preflight/l6_4_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_real_read_only_external_observation_preflight/l6_4_preflight_scope.json",
        with_common(
            {
                "milestone_id": MILESTONE_ID,
                "scope_status": "real_read_only_observation_preflight_only",
                "in_scope": [
                    "select L6.3 observation cases as future candidates",
                    "define read-only observation preflight requirements",
                    "generate blocked approval packets",
                    "define source allowlist and denylist policies",
                    "define operator handoff and no-action constraints",
                    "define evidence capture and quarantine requirements",
                    "generate blocked preflight decisions",
                ],
                "out_of_scope": [
                    "real external observation",
                    "network calls",
                    "API calls",
                    "scraping",
                    "browser fetch",
                    "publication",
                    "outreach",
                    "payment",
                    "revenue execution",
                    "MCP execution",
                    "live behavior",
                    "CIEU DB write",
                    "canonical mutation",
                    "brain or memory writeback",
                    "direct Y* mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "l6_real_read_only_external_observation_preflight/l6_4_safety_flags.json",
        {"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS, "l6_4_flags": L6_4_FLAGS},
        generated,
    )
    write_text(
        "l6_real_read_only_external_observation_preflight/README.md",
        "# L6.4 Real Read-Only External Observation Preflight\n\n"
        "This pack defines the preflight conditions required before a future real "
        "read-only observation milestone can be considered. It does not observe, "
        "fetch, scrape, browse, publish, contact, pay, execute MCP, mutate "
        "canonical strategy, write brain/memory, or directly mutate Y*.\n",
        generated,
    )
    write_text(
        "l6_real_read_only_external_observation_preflight/l6_4_non_execution_boundary.md",
        "# L6.4 Non-Execution Boundary\n\n"
        f"{PLACEHOLDER_LOCATOR_MARKER}\n\n"
        "L6.4 may generate preflight packets, handoff plans, source policies, "
        "evidence-capture contracts, no-action guarantees, and blocked decisions. "
        "It may not execute observation or external-world actions.\n",
        generated,
    )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "l6_4_real_read_only_observation_preflight_defined": True,
        "preflight_only": True,
        "sandbox_only": True,
        "candidate_count": len(candidates),
        "approval_packet_count": len(approval_packets),
        "source_allowlist_defined": True,
        "source_denylist_defined": True,
        "operator_handoff_plan_generated": True,
        "network_isolation_preflight_defined": True,
        "evidence_capture_preflight_defined": True,
        "abort_rollback_quarantine_policy_defined": True,
        "no_action_guarantees_generated": True,
        "preflight_decision_gate_generated": True,
        "strategic_residual_loop_generated": True,
        "future_real_read_only_observation_candidate_allowed": True,
        "real_external_observation_authorized": False,
        "real_observation_execution_authorized": False,
        "network_authorized": False,
        "api_authorized": False,
        "scraping_authorized": False,
        "browser_fetch_authorized": False,
        "publication_authorized": False,
        "outreach_authorized": False,
        "payment_authorized": False,
        "revenue_execution_authorized": False,
        "mcp_execution_authorized": False,
        "live_behavior_authorized": False,
        "cieu_db_write_authorized": False,
        "canonical_update_authorized": False,
        "brain_writeback_authorized": False,
        "memory_ingestion_authorized": False,
        "direct_y_star_mutation_authorized": False,
        "ready_for_l6_5_controlled_real_read_only_observation_pilot_design": True,
        "ready_for_actual_network_observation_now": False,
        "ready_for_scraping": False,
        "ready_for_publication": False,
        "ready_for_outreach": False,
        "ready_for_payment": False,
        "ready_for_revenue_execution": False,
        "ready_for_mcp_execution": False,
        "ready_for_canonical_update": False,
        "ready_for_brain_memory_writeback": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "input_refs": refs,
        "missing_optional_refs": missing_refs,
        "safety_flags": SAFETY_FLAGS,
        "l6_4_flags": L6_4_FLAGS,
        "warning": (
            "L6.4 is preflight-only. Real external observation, URL fetch, scraping, "
            "API calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y* mutation remain blocked."
        ),
    }
    write_json("l6_real_read_only_external_observation_preflight/l6_4_summary.json", summary, generated)
    write_text(
        "l6_real_read_only_external_observation_preflight/l6_4_summary.md",
        "# L6.4 Summary\n\n"
        "- Real read-only observation preflight defined: true\n"
        "- Candidate packets generated: true\n"
        "- Real observation authorized: false\n"
        f"- Candidate count: {len(candidates)}\n"
        f"- Next milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    write_json(
        "real_observation_candidate_selector/l6_3_observation_case_inventory.json",
        {
            "schema_version": SCHEMA_VERSION,
            "source": INPUT_REFS["l6_3_selected_cases"],
            "case_count": len(selected_l6_3_cases()),
            "cases": selected_l6_3_cases(),
            "safety_flags": SAFETY_FLAGS,
            "l6_4_flags": L6_4_FLAGS,
        },
        generated,
    )
    write_json(
        "real_observation_candidate_selector/real_observation_candidate_matrix.json",
        {
            "schema_version": SCHEMA_VERSION,
            "selection_mode": "structural_read_only_preflight_candidate_selection",
            "selection_factors": SELECTION_FACTORS,
            "selected_by_hardcoded_opportunity_category": False,
            "matrix": [
                {
                    "candidate_id": candidate["candidate_id"],
                    "linked_l6_3_packet_id": candidate["linked_l6_3_packet_id"],
                    "evidence_gap_remains": True,
                    "real_source_evidence_necessary": True,
                    "read_only_feasible": True,
                    "no_contact_required": True,
                    "no_login_required": True,
                    "no_payment_required": True,
                    "no_form_submission_required": True,
                    "no_publication_required": True,
                    "no_account_creation_required": True,
                    "no_mcp_execution_required": True,
                    "source_locator_can_be_represented": True,
                    "claim_boundary_clear": True,
                    "expected_evidence_type_clear": True,
                    "freshness_requirement_clear": True,
                    "review_value": "high",
                    "downside_risk": "low",
                    "selected": True,
                }
                for candidate in candidates
            ],
        },
        generated,
    )
    write_json(
        "real_observation_candidate_selector/selected_real_observation_candidates.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_count": len(candidates),
            "selection_mode": "structural_read_only_preflight_candidate_selection",
            "selected_by_hardcoded_opportunity_category": False,
            "hardcoded_opportunity_class_used": False,
            "candidates": candidates,
        },
        generated,
    )
    write_json(
        "real_observation_candidate_selector/deferred_real_observation_candidates.json",
        {
            "schema_version": SCHEMA_VERSION,
            "deferred_candidates": deferred,
            "real_observation_authorized_now": False,
        },
        generated,
    )
    write_text(
        "real_observation_candidate_selector/real_observation_candidate_selector_report.md",
        "# Real Observation Candidate Selector Report\n\n"
        "Candidates are selected from L6.3 packet/case evidence gaps and read-only "
        "feasibility, not opportunity categories. Preflight is authorized; real "
        "observation is not.\n",
        generated,
    )

    write_json(
        "real_read_only_observation_preflight_contract/read_only_observation_definition.json",
        with_common(
            {
                "definition": "view/read only future observation under explicit approval",
                "means": [
                    "view/read only",
                    "no login unless future approved",
                    "no account creation",
                    "no comment/post/message",
                    "no form submission",
                    "no purchase/payment",
                    "no download of sensitive/private data",
                    "no bypassing access controls",
                    "no scraping automation",
                    "no browser automation unless future separately approved",
                    "no MCP execution unless future separately approved",
                    "no external mutation",
                    "no customer contact",
                    "no publication",
                    "no revenue action",
                    "no canonical update",
                    "no brain/memory writeback",
                    "no direct Y* mutation",
                ],
                "real_observation_authorized_in_l6_4": False,
            }
        ),
        generated,
    )
    write_json(
        "real_read_only_observation_preflight_contract/preflight_requirement_registry.json",
        with_common(
            {
                "requirements": [
                    {
                        "requirement_id": f"preflight_requirement_{index:03d}",
                        "requirement": requirement,
                        "required_before_real_observation": True,
                        "satisfied_for_preflight_packet_generation": True,
                        "satisfied_for_real_observation": False,
                    }
                    for index, requirement in enumerate(PRE_FLIGHT_REQUIREMENTS, start=1)
                ]
            }
        ),
        generated,
    )
    write_json(
        "real_read_only_observation_preflight_contract/read_only_vs_action_boundary.json",
        with_common(
            {
                "read_only_allowed_future_after_approval": [
                    "view approved public source",
                    "capture bounded citation metadata",
                    "record claim boundary and missing context",
                ],
                "action_forbidden": [
                    "login",
                    "account creation",
                    "comment/post/message",
                    "form submission",
                    "purchase/payment",
                    "download sensitive/private data",
                    "bypass access controls",
                    "scraping automation",
                    "browser automation without future approval",
                    "MCP execution without future approval",
                    "external mutation",
                    "customer contact",
                    "publication",
                    "revenue action",
                    "canonical update",
                    "brain/memory writeback",
                    "direct Y* mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "real_read_only_observation_preflight_contract/real_observation_disallowed_action_registry.json",
        with_common(
            {
                "disallowed_actions": [
                    {"action_id": action.replace(" ", "_").replace("/", "_"), "action": action}
                    for action in [
                        "login",
                        "account creation",
                        "comment post message",
                        "form submission",
                        "purchase payment",
                        "sensitive private data download",
                        "access control bypass",
                        "scraping automation",
                        "browser automation",
                        "MCP execution",
                        "external mutation",
                        "customer contact",
                        "publication",
                        "revenue action",
                        "canonical update",
                        "brain memory writeback",
                        "direct Y* mutation",
                    ]
                ]
            }
        ),
        generated,
    )
    write_text(
        "real_read_only_observation_preflight_contract/preflight_contract_report.md",
        "# Preflight Contract Report\n\n"
        "The L6.4 contract defines conditions for a future real read-only observation "
        "but blocks observation now. Read-only is explicitly separated from action.\n",
        generated,
    )

    write_json(
        "source_allowlist_and_risk_policy/source_allowlist_policy.json",
        with_common(
            {
                "allowlist_status": "future_policy_only_real_access_unauthorized_in_l6_4",
                "source_types": [
                    {
                        "source_type_id": source_type,
                        "label": source_type.replace("_", " "),
                        "allowed_future_after_approval": True,
                        "real_access_authorized_in_l6_4": False,
                    }
                    for source_type in ALLOWLIST_SOURCE_TYPES
                ],
            }
        ),
        generated,
    )
    write_json(
        "source_allowlist_and_risk_policy/source_denylist_policy.json",
        with_common(
            {
                "denylist_status": "blocked_for_l6_4_and_requires_future_boundary",
                "source_types": [
                    {
                        "source_type_id": source_type,
                        "denied_in_l6_4": True,
                        "future_exception_requires_explicit_approval": True,
                    }
                    for source_type in DENYLIST_SOURCE_TYPES
                ],
            }
        ),
        generated,
    )
    write_json(
        "source_allowlist_and_risk_policy/source_risk_tier_policy.json",
        with_common(
            {
                "risk_tiers": [
                    {
                        "tier": "low_read_only_public",
                        "description": "Public read-only source with no interaction required.",
                        "real_access_authorized_in_l6_4": False,
                    },
                    {
                        "tier": "medium_public_with_ip_or_privacy_review",
                        "description": "Public source that needs reviewer attention before use.",
                        "real_access_authorized_in_l6_4": False,
                    },
                    {
                        "tier": "blocked_interactive_or_private",
                        "description": "Login, payment, private, form, contact, or action surface.",
                        "real_access_authorized_in_l6_4": False,
                    },
                ],
                "truth_scoring_used": False,
                "semantic_truth_scoring_used": False,
            }
        ),
        generated,
    )
    write_json(
        "source_allowlist_and_risk_policy/source_locator_policy.json",
        with_common(
            {
                "locator_policy": "placeholder_locator_only_in_l6_4",
                "placeholder_marker": PLACEHOLDER_LOCATOR_MARKER,
                "locator_may_be_recorded": True,
                "locator_may_be_fetched": False,
                "locator_may_be_opened": False,
                "locator_may_be_verified_as_current_fact": False,
            }
        ),
        generated,
    )
    write_text(
        "source_allowlist_and_risk_policy/source_policy_report.md",
        "# Source Policy Report\n\n"
        "L6.4 defines future allowlist/denylist policy and risk tiers. All real "
        "access remains unauthorized.\n",
        generated,
    )

    write_json(
        "real_observation_approval_packet_schema/real_observation_approval_packet_schema.json",
        with_common(
            {
                "schema_name": "l6_4.real_observation_approval_packet",
                "required_fields": APPROVAL_PACKET_FIELDS,
                "field_definitions": {
                    field: "required before any future real read-only observation"
                    for field in APPROVAL_PACKET_FIELDS
                },
                "real_observation_authorized_in_l6_4": False,
            }
        ),
        generated,
    )
    write_json(
        "real_observation_approval_packet_schema/approval_packet_required_fields.json",
        {"schema_version": SCHEMA_VERSION, "required_fields": APPROVAL_PACKET_FIELDS},
        generated,
    )
    write_json(
        "real_observation_approval_packet_schema/approval_packet_examples_blocked_now.json",
        {
            "schema_version": SCHEMA_VERSION,
            "example_count": len(approval_packets),
            "approval_packets": approval_packets,
        },
        generated,
    )
    write_json(
        "real_observation_approval_packet_schema/invalid_approval_packet_examples.json",
        with_common(
            {
                "invalid_examples": [
                    {
                        "invalid_reason": "real observation incorrectly authorized",
                        "real_observation_authorized": True,
                    },
                    {
                        "invalid_reason": "login/account/payment/action required",
                        "no_login_required": False,
                        "no_account_required": False,
                        "no_payment_required": False,
                    },
                    {
                        "invalid_reason": "missing citation and abort plan",
                        "citation_plan": None,
                        "abort_conditions": [],
                    },
                ]
            }
        ),
        generated,
    )
    write_text(
        "real_observation_approval_packet_schema/approval_packet_schema_report.md",
        "# Approval Packet Schema Report\n\n"
        "Approval packet examples are generated for preflight only. They do not "
        "authorize real observation.\n",
        generated,
    )

    write_json(
        "observation_operator_handoff/operator_handoff_contract.json",
        with_common(
            {
                "handoff_mode": "future_operator_plan_only",
                "operator_handoff_required": True,
                "operator_handoff_exercised_in_l6_4": False,
                "operator_must_submit_evidence_for_review_only": True,
                "operator_may_mutate_artifacts_directly": False,
                "real_observation_authorized_in_l6_4": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_operator_handoff/operator_handoff_packet_examples.json",
        {
            "schema_version": SCHEMA_VERSION,
            "packet_count": len(approval_packets),
            "handoff_packets": [
                with_common(
                    {
                        "operator_handoff_packet_id": f"l6_4_operator_handoff_{index:03d}",
                        "linked_approval_packet_id": packet["approval_packet_id"],
                        "confirm_source_locator": True,
                        "confirm_no_login_account_payment_contact_required": True,
                        "confirm_no_form_submission": True,
                        "confirm_no_publication": True,
                        "confirm_no_outreach": True,
                        "capture_evidence_only_as_permitted": True,
                        "record_source_title_date_locator": True,
                        "record_claim_boundary": True,
                        "abort_if_disallowed_action_appears": True,
                        "do_not_mutate_artifacts_directly": True,
                        "submit_evidence_packet_for_review_only": True,
                        "real_observation_authorized_in_l6_4": False,
                    }
                )
                for index, packet in enumerate(approval_packets, start=1)
            ],
        },
        generated,
    )
    write_json(
        "observation_operator_handoff/operator_non_action_oath.json",
        with_common(
            {
                "oath_id": "l6_4_operator_non_action_oath",
                "operator_affirms": [
                    "no login",
                    "no account",
                    "no payment",
                    "no contact",
                    "no form submission",
                    "no publication",
                    "no outreach",
                    "no sensitive/private data download",
                    "no artifact mutation",
                    "review-only evidence packet submission",
                ],
                "active_in_l6_4": "plan_only",
            }
        ),
        generated,
    )
    write_text(
        "observation_operator_handoff/operator_checklist.md",
        "# Operator Checklist\n\n"
        "- Confirm source locator.\n"
        "- Confirm no login/account/payment/contact required.\n"
        "- Confirm no form submission.\n"
        "- Confirm no publication or outreach.\n"
        "- Confirm no downloads of sensitive/private data.\n"
        "- Capture evidence only as permitted.\n"
        "- Record source title/date/locator.\n"
        "- Record claim boundary and missing context.\n"
        "- Abort if any disallowed action appears.\n"
        "- Do not mutate artifacts directly.\n"
        "- Submit evidence packet for review only.\n",
        generated,
    )
    write_text(
        "observation_operator_handoff/operator_handoff_report.md",
        "# Operator Handoff Report\n\n"
        "L6.4 creates a future handoff plan only. No operator executed real "
        "observation in this milestone.\n",
        generated,
    )

    write_json(
        "observation_network_isolation_preflight/network_isolation_requirement.json",
        with_common(
            {
                "requirement_mode": "requirements_only_no_network_check_executed",
                "network_checks_executed": False,
                "real_network_authorized": False,
                "requirements": [
                    "manual approval before any future read-only browser/search session",
                    "no login",
                    "no cookies required",
                    "no account creation",
                    "no form submission",
                    "no posting",
                    "no payment",
                    "no automated scraping",
                    "source capture only",
                ],
            }
        ),
        generated,
    )
    write_json(
        "observation_network_isolation_preflight/permitted_future_tool_profile.json",
        with_common(
            {
                "profile_mode": "future_profile_only",
                "permitted_after_future_approval": [
                    "manually approved read-only browser/search session",
                    "no login",
                    "no cookies required",
                    "no account creation",
                    "no form submission",
                    "no posting",
                    "no payment",
                    "no automated scraping",
                    "source capture only",
                ],
                "enabled_in_l6_4": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_network_isolation_preflight/prohibited_tool_profile.json",
        with_common(
            {
                "prohibited": [
                    "autonomous browsing",
                    "scraping loop",
                    "login automation",
                    "account creation",
                    "checkout/payment",
                    "posting/commenting/messaging",
                    "bulk download",
                    "MCP execution",
                    "agent live control",
                    "persistent external session mutation",
                ]
            }
        ),
        generated,
    )
    write_json(
        "observation_network_isolation_preflight/environment_preflight_checklist.json",
        with_common(
            {
                "checklist_mode": "paper_preflight_only",
                "checks_executed": False,
                "items": [
                    "approval packet exists",
                    "operator handoff packet exists",
                    "source allowlist type confirmed",
                    "denylist checked structurally",
                    "abort/quarantine policy acknowledged",
                    "no-action guarantees acknowledged",
                ],
            }
        ),
        generated,
    )
    write_text(
        "observation_network_isolation_preflight/network_isolation_preflight_report.md",
        "# Network Isolation Preflight Report\n\n"
        "This pack defines future isolation requirements only. No network or tool "
        "checks that access the network were executed.\n",
        generated,
    )

    evidence_packet_fields = [
        "evidence_packet_id",
        "linked_approval_packet_id",
        "source_locator",
        "source_title",
        "source_publisher_or_owner",
        "observed_at_timestamp",
        "source_date_or_date_missing",
        "freshness_class",
        "captured_claims",
        "unsupported_claims",
        "missing_context",
        "conflicting_source_marker",
        "claim_boundary",
        "citation_trace",
        "capture_method",
        "operator_id_or_manual_marker",
        "review_status",
        "external_action_taken",
        "publication_taken",
        "outreach_taken",
        "payment_taken",
    ]
    write_json(
        "observation_evidence_capture_preflight/evidence_capture_contract.json",
        with_common(
            {
                "capture_mode": "future_evidence_packet_schema_only",
                "real_evidence_captured_in_l6_4": False,
                "required_capture_fields": evidence_packet_fields,
                "review_required": True,
            }
        ),
        generated,
    )
    write_json(
        "observation_evidence_capture_preflight/citation_capture_schema.json",
        with_common(
            {
                "required_fields": [
                    "source_locator",
                    "source_title",
                    "source_publisher_or_owner",
                    "observed_at_timestamp",
                    "source_date_or_date_missing",
                    "citation_trace",
                ],
                "citation_may_authorize_publication": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_evidence_capture_preflight/source_snapshot_metadata_schema.json",
        with_common(
            {
                "required_fields": [
                    "source_locator",
                    "source_title",
                    "observed_at_timestamp",
                    "freshness_class",
                    "claim_boundary",
                    "missing_context",
                ],
                "snapshot_created_in_l6_4": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_evidence_capture_preflight/evidence_packet_schema.json",
        with_common(
            {
                "schema_name": "l6_4.future_read_only_evidence_packet",
                "required_fields": evidence_packet_fields,
                "default_no_action_fields": {
                    "external_action_taken": False,
                    "publication_taken": False,
                    "outreach_taken": False,
                    "payment_taken": False,
                },
            }
        ),
        generated,
    )
    write_text(
        "observation_evidence_capture_preflight/evidence_capture_preflight_report.md",
        "# Evidence Capture Preflight Report\n\n"
        "The evidence packet schema requires citation/source/freshness/claim-boundary "
        "fields and no-action markers. No real evidence was captured.\n",
        generated,
    )

    write_json(
        "observation_abort_rollback_quarantine_policy/abort_condition_registry.json",
        with_common(
            {
                "abort_conditions": [
                    {"condition_id": f"abort_condition_{index:03d}", "condition": condition}
                    for index, condition in enumerate(ABORT_CONDITIONS, start=1)
                ]
            }
        ),
        generated,
    )
    write_json(
        "observation_abort_rollback_quarantine_policy/quarantine_policy.json",
        with_common(
            {
                "quarantine_required_when": [
                    "source exceeds approved scope",
                    "evidence conflicts with approval packet",
                    "operator uncertainty",
                    "sensitive/private data encountered",
                    "unsupported claim cannot be bounded",
                ],
                "quarantine_effect": "evidence packet cannot flow downstream without review",
            }
        ),
        generated,
    )
    write_json(
        "observation_abort_rollback_quarantine_policy/evidence_rejection_policy.json",
        with_common(
            {
                "reject_evidence_when": [
                    "disallowed action was required",
                    "locator mismatch",
                    "source asks for interaction",
                    "claim scope exceeds approval packet",
                    "citation trace missing",
                ],
                "rejection_is_not_canonical_update": True,
            }
        ),
        generated,
    )
    write_json(
        "observation_abort_rollback_quarantine_policy/rollback_non_mutation_policy.json",
        with_common(
            {
                "rollback_meaning": (
                    "Because L6.4 and future read-only observation must not mutate "
                    "canonical state, rollback means rejecting or quarantining evidence "
                    "packets and preventing downstream application."
                ),
                "canonical_state_mutated_before_rollback": False,
                "brain_memory_mutated_before_rollback": False,
            }
        ),
        generated,
    )
    write_text(
        "observation_abort_rollback_quarantine_policy/abort_rollback_quarantine_report.md",
        "# Abort, Rollback, and Quarantine Report\n\n"
        "Abort triggers cover unexpected login, payment, account, form, contact, "
        "private data, malicious source, scope mismatch, automation, and operator "
        "uncertainty. Rollback is non-mutation evidence rejection/quarantine.\n",
        generated,
    )

    for filename, action_type in NO_ACTION_RECEIPTS.items():
        write_json(
            f"read_only_observation_no_action_guarantees/{filename}",
            receipt(action_type),
            generated,
        )
    write_text(
        "read_only_observation_no_action_guarantees/no_action_guarantee_report.md",
        "# No-Action Guarantee Report\n\n"
        "All L6.4 no-action receipts show authorization=false and executed=false. "
        "Real observation and external action remain blocked.\n",
        generated,
    )

    decisions = [
        with_common(
            {
                "candidate_id": candidate["candidate_id"],
                "linked_l6_3_packet_id": candidate["linked_l6_3_packet_id"],
                "real_observation_decision": "blocked_pending_future_explicit_approval",
                "preflight_decision": "preflight_packet_ready",
                "real_network_authorized": False,
                "execution_authorized": False,
                "review_required": True,
                "approval_required": True,
                "future_milestone_required": True,
                "future_milestone": NEXT_MILESTONE,
            }
        )
        for candidate in candidates
    ]
    write_json(
        "real_observation_preflight_decision_gate/preflight_decision_gate_contract.json",
        with_common(
            {
                "gate_mode": "preflight_decision_only",
                "all_real_observation_blocked_in_l6_4": True,
                "decision_values": [
                    "blocked_pending_future_explicit_approval",
                    "preflight_packet_ready",
                    "preflight_packet_incomplete",
                ],
            }
        ),
        generated,
    )
    write_json(
        "real_observation_preflight_decision_gate/candidate_preflight_decisions.json",
        {"schema_version": SCHEMA_VERSION, "decision_count": len(decisions), "decisions": decisions},
        generated,
    )
    write_json(
        "real_observation_preflight_decision_gate/blocked_real_observation_decisions.json",
        {
            "schema_version": SCHEMA_VERSION,
            "blocked_decisions": [
                decision
                for decision in decisions
                if decision["real_observation_decision"]
                == "blocked_pending_future_explicit_approval"
            ],
        },
        generated,
    )
    write_json(
        "real_observation_preflight_decision_gate/future_entry_conditions.json",
        with_common(
            {
                "future_entry_milestone": NEXT_MILESTONE,
                "conditions": [
                    "explicit approval boundary",
                    "operator handoff accepted",
                    "source allowlist match",
                    "no denylist triggers",
                    "network/tool isolation approved",
                    "evidence capture contract accepted",
                    "abort/quarantine policy accepted",
                    "no-action guarantee preserved",
                ],
                "real_network_authorized_now": False,
            }
        ),
        generated,
    )
    write_text(
        "real_observation_preflight_decision_gate/preflight_decision_gate_report.md",
        "# Preflight Decision Gate Report\n\n"
        "Every L6.4 candidate is blocked for real observation pending future "
        "explicit approval. Preflight packet readiness does not authorize execution.\n",
        generated,
    )

    write_json(
        "l6_real_observation_preflight_strategic_residual_loop/l6_4_cieu_like_fixture.json",
        {
            "schema_version": SCHEMA_VERSION,
            "event_mode": "l6_4_real_read_only_external_observation_preflight_fixture",
            "X_t": {
                "l6_0": "value hypothesis selection exists",
                "l6_1": "internal MVP artifact sandbox exists",
                "l6_2": "external observation boundary exists",
                "l6_3": "controlled static/manual observation sandbox exists",
            },
            "U_t": (
                "Create preflight conditions for future real read-only observation "
                "without executing real observation."
            ),
            "Y_star_t": (
                "Define a complete preflight system for future real read-only external "
                "observation while preserving no-network/no-scraping/no-API/"
                "no-browser-fetch/no-publication/no-outreach/no-payment/no-revenue/"
                "no-MCP/no-live/no-canonical-mutation/no-brain-memory-writeback/"
                "no-direct-Y* mutation constraints."
            ),
            "Y_t_plus_1": [
                "real observation candidates selected for preflight",
                "read-only contract generated",
                "source allowlist/denylist generated",
                "blocked approval packets generated",
                "operator handoff generated",
                "network isolation requirements generated",
                "evidence capture preflight generated",
                "abort/rollback/quarantine policy generated",
                "no-action guarantees generated",
                "preflight decisions block real observation",
            ],
            "R_t_plus_1": "deterministic structural residual only",
            "persistence_enabled": False,
            "db_write_performed": False,
            "real_observation_performed": False,
            "real_network_enabled": False,
        },
        generated,
    )
    write_json(
        "l6_real_observation_preflight_strategic_residual_loop/l6_4_strategic_residual_delta.json",
        with_common(
            {
                "residual_classes": {
                    "real_observation_not_executed": "expected_blocker",
                    "source_policies_untested_on_real_pages": "remaining_gap",
                    "operator_handoff_not_exercised_live": "remaining_gap",
                    "evidence_capture_not_tested_on_real_current_data": "remaining_gap",
                    "approval_packet_remains_blocked": "expected_blocker",
                    "no_real_freshness_verification_yet": "remaining_gap",
                    "quarantine_policy_not_tested_on_live_source_conflict": "remaining_gap",
                    "future_approval_boundary_still_required": "expected_blocker",
                }
            }
        ),
        generated,
    )
    write_json(
        "l6_real_observation_preflight_strategic_residual_loop/l6_4_meta_learning_update_candidate.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_id": "l6_4_meta_learning_update_candidate",
            "learning_targets": [
                "real_read_only_observation_preflight_policy",
                "source_allowlist_policy",
                "operator_handoff_policy",
                "evidence_capture_policy",
                "abort_quarantine_policy",
            ],
            "eligible_for_review_queue": True,
            "eligible_for_direct_brain_writeback": False,
            "eligible_for_direct_memory_ingestion": False,
            "eligible_for_candidate_auto_approval": False,
            "eligible_for_direct_strategy_mutation": False,
            "approved": False,
            "applied": False,
        },
        generated,
    )
    write_text(
        "l6_real_observation_preflight_strategic_residual_loop/l6_4_residual_report.md",
        "# L6.4 Strategic Residual Report\n\n"
        "The main residual is intentional: real observation is still not executed. "
        "Source policies, operator handoff, evidence capture, freshness, and "
        "quarantine remain untested on real current data until a future approved milestone.\n",
        generated,
    )

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_4_real_read_only_observation_preflight_complete": True,
        "real_observation_candidates_selected": True,
        "read_only_preflight_contract_generated": True,
        "source_allowlist_and_risk_policy_generated": True,
        "approval_packet_schema_generated": True,
        "operator_handoff_plan_generated": True,
        "network_isolation_preflight_defined": True,
        "evidence_capture_preflight_defined": True,
        "abort_rollback_quarantine_policy_generated": True,
        "no_action_guarantees_generated": True,
        "preflight_decision_gate_generated": True,
        "strategic_residual_loop_generated": True,
        "ready_for_l6_5_controlled_real_read_only_observation_pilot_design": True,
        "ready_for_actual_network_observation_now": False,
        "ready_for_scraping": False,
        "ready_for_publication": False,
        "ready_for_outreach": False,
        "ready_for_payment": False,
        "ready_for_revenue_execution": False,
        "ready_for_mcp_execution": False,
        "ready_for_canonical_update": False,
        "ready_for_brain_memory_writeback": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "blocked_capabilities": [
            "actual network observation now",
            "scraping",
            "publication",
            "outreach",
            "payment",
            "revenue execution",
            "MCP execution",
            "canonical update",
            "brain/memory writeback",
        ],
        "safety_flags": SAFETY_FLAGS,
        "l6_4_flags": L6_4_FLAGS,
    }
    write_json(
        "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json",
        readiness,
        generated,
    )
    write_json(
        "l6_real_observation_preflight_readiness/l6_4_next_milestone_recommendation.json",
        {
            "schema_version": SCHEMA_VERSION,
            "recommended_next_milestone": NEXT_MILESTONE,
            "do_not_implement_in_l6_4": True,
            "recommended_scope": [
                "controlled pilot design",
                "still no actual observation unless separately approved",
                "review future operator/tool isolation",
            ],
            "ready_for_actual_network_observation_now": False,
        },
        generated,
    )
    write_json(
        "l6_real_observation_preflight_readiness/l6_4_blockers.json",
        {
            "schema_version": SCHEMA_VERSION,
            "blockers": [
                "future explicit approval boundary missing",
                "real source evidence not yet observed",
                "operator handoff not exercised live",
                "network isolation not approved for execution",
                "evidence capture not tested on real current data",
                "publication/outreach/payment/revenue remain forbidden",
            ],
        },
        generated,
    )
    write_text(
        "l6_real_observation_preflight_readiness/l6_4_readiness_report.md",
        "# L6.4 Readiness Report\n\n"
        "L6.4 preflight is complete when validation passes. It is ready to design "
        "L6.5, but not ready for actual network observation, scraping, publication, "
        "outreach, payment, revenue execution, MCP execution, canonical update, or "
        "brain/memory writeback.\n",
        generated,
    )

    return generated


def main() -> None:
    generated = generate()
    print(f"Built L6.4 real read-only external observation preflight artifacts: {len(generated)} files")


if __name__ == "__main__":
    main()
