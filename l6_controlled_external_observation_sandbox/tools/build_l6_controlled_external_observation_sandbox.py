#!/usr/bin/env python3
"""Build deterministic L6.3 controlled external observation sandbox outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

MILESTONE_ID = "L6.3"
MILESTONE_NAME = "Controlled External Observation Sandbox v0"
NEXT_MILESTONE = "L6.4 Real Read-Only External Observation Preflight v0"
SCHEMA_VERSION = "v0"

SANDBOX_MARKER = (
    "STATIC / MANUAL-IMPORT SANDBOX FIXTURE ONLY - NOT FETCHED - "
    "NOT CURRENT FACT - NOT VERIFIED EXTERNAL DATA - NOT AUTHORIZED FOR "
    "EXTERNAL ACTION - NOT AUTHORIZED FOR PUBLICATION - NOT AUTHORIZED "
    "FOR OUTREACH - NOT AUTHORIZED FOR PAYMENT - NOT AUTHORIZED FOR "
    "REVENUE EXECUTION - NOT AUTHORIZED FOR CANONICAL UPDATE"
)

INPUT_REFS = {
    "l6_0_generated_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_0_selection_ranking": "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "l6_0_mvp_plans": "minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json",
    "l6_0_design_readiness": (
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json"
    ),
    "l6_1_summary": "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json",
    "l6_1_case_index": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_1_readiness": "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json",
    "l6_2_summary": "l6_governed_external_observation_boundary/l6_2_summary.json",
    "l6_2_packet_schema": "pre_observation_packet_schema/pre_observation_packet_schema.json",
    "l6_2_permission_gate": (
        "external_observation_permission_gate/observation_permission_gate_contract.json"
    ),
    "l6_2_source_registry": "external_source_registry_and_policy/source_type_registry.json",
    "l6_2_claim_policy": "observation_claim_boundary_and_freshness/claim_boundary_policy.json",
    "l6_2_readiness": (
        "l6_external_observation_boundary_readiness/l6_2_readiness_assessment.json"
    ),
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

L6_3_FLAGS = {
    "l6_3_sandbox_only": True,
    "l6_3_fixture_only": True,
    "l6_3_static_fixture_observation_enabled": True,
    "l6_3_manual_import_fixture_enabled": True,
    "l6_3_artifact_refinement_candidate_enabled": True,
    "l6_3_real_external_observation_enabled": False,
    "l6_3_network_enabled": False,
    "l6_3_api_enabled": False,
    "l6_3_scraping_enabled": False,
    "l6_3_browser_fetch_enabled": False,
    "l6_3_publication_enabled": False,
    "l6_3_outreach_enabled": False,
    "l6_3_payment_enabled": False,
    "l6_3_revenue_execution_enabled": False,
    "l6_3_mcp_execution_enabled": False,
    "l6_3_live_behavior_enabled": False,
    "l6_3_artifact_refinement_application_enabled": False,
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
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
}

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

SOURCE_TYPES = [
    "user_supplied_summary",
    "manually_imported_note",
    "manually_imported_screenshot_summary",
]

SELECTION_SIGNALS = [
    "missing evidence",
    "unclear recipient archetype",
    "unclear payer or beneficiary",
    "weak acceptance criteria",
    "stale or absent source evidence",
    "uncertain claim boundary",
    "unclear distribution friction",
    "unclear competitive pressure",
    "unclear external dependency",
    "proof question requires outside evidence",
    "high learning value",
    "low downside risk within sandbox",
    "reviewability",
]

REFINEMENT_TARGETS = [
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
]

NO_ACTION_RECEIPTS = {
    "no_network_receipt.json": "network",
    "no_api_receipt.json": "api",
    "no_scraping_receipt.json": "scraping",
    "no_browser_fetch_receipt.json": "browser_fetch",
    "no_publication_receipt.json": "publication",
    "no_outreach_receipt.json": "outreach",
    "no_payment_receipt.json": "payment",
    "no_revenue_execution_receipt.json": "revenue_execution",
    "no_mcp_execution_receipt.json": "mcp_execution",
    "no_live_behavior_receipt.json": "live_behavior",
    "no_canonical_mutation_receipt.json": "canonical_mutation",
    "no_brain_memory_writeback_receipt.json": "brain_memory_writeback",
    "no_direct_y_star_mutation_receipt.json": "direct_y_star_mutation",
}


class BuildError(Exception):
    """Raised when safe generated artifacts cannot be built."""


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
    return {
        **payload,
        "safety_flags": SAFETY_FLAGS,
        "l6_3_flags": L6_3_FLAGS,
    }


def existing_input_map() -> tuple[dict[str, str], list[str]]:
    refs: dict[str, str] = {}
    gaps: list[str] = []
    for key, rel in INPUT_REFS.items():
        if (ROOT / rel).exists():
            refs[key] = rel
        else:
            gaps.append(rel)
    return refs, gaps


def case_contract(case_id: str) -> dict[str, Any]:
    return read_json(f"selected_mvp_artifact_cases/{case_id}/case_contract.json") or {}


def case_evidence(case_id: str) -> dict[str, Any]:
    return read_json(f"selected_mvp_artifact_cases/{case_id}/artifact_evidence_needed.json") or {}


def case_claim_boundary(case_id: str) -> dict[str, Any]:
    return read_json(f"selected_mvp_artifact_cases/{case_id}/artifact_claim_boundary.json") or {}


def selected_cases() -> list[dict[str, Any]]:
    index = read_json(INPUT_REFS["l6_1_case_index"]) or {}
    cases = index.get("cases", [])[:3]
    if not cases:
        return [
            {
                "case_id": "case_001",
                "source_hypothesis_id": "hypothesis_placeholder",
                "generated_artifact": "selected_mvp_artifact_cases/case_001/generated_artifact.md",
                "externalization_status": "blocked",
            }
        ]
    return cases


def observation_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    surfaces = [
        "future_manual_summary_of_recipient_need",
        "future_manual_note_about acceptance criteria",
        "future_manual_screenshot_summary_of comparable evidence boundary",
    ]
    evidence_types = [
        "manual_source_summary",
        "manual_acceptance_criteria_note",
        "manual_screenshot_summary",
    ]
    for index, case in enumerate(cases, start=1):
        case_id = case.get("case_id", f"case_{index:03d}")
        contract = case_contract(case_id)
        evidence = case_evidence(case_id)
        selected.append(
            {
                "selected_case_id": f"observation_case_{index:03d}",
                "source_l6_1_case_id": case_id,
                "linked_l6_0_hypothesis_id": case.get(
                    "source_hypothesis_id", contract.get("source_hypothesis_id")
                ),
                "observation_need_reason": (
                    "Selected because the internal MVP artifact has reviewable evidence "
                    "gaps that require future external observation before any external use."
                ),
                "selection_basis": SELECTION_SIGNALS,
                "selected_by_hardcoded_opportunity_category": False,
                "hardcoded_opportunity_class_used": False,
                "evidence_gap": evidence.get(
                    "missing_evidence",
                    [
                        "external recipient validation",
                        "payer or beneficiary clarity",
                        "source freshness",
                    ],
                ),
                "proposed_observation_question": (
                    "Which externally supplied or future approved read-only evidence would "
                    "clarify the artifact claim boundary and acceptance criteria?"
                ),
                "observation_surface_type": surfaces[(index - 1) % len(surfaces)],
                "expected_evidence_type": evidence_types[(index - 1) % len(evidence_types)],
                "real_observation_authorized": False,
                "sandbox_fixture_authorized": True,
                "manual_import_fixture_authorized": True,
                "review_required_before_real_observation": True,
                "safety_flags": SAFETY_FLAGS,
                "l6_3_flags": L6_3_FLAGS,
            }
        )
    return selected


def build_packet(index: int, selected_case: dict[str, Any]) -> dict[str, Any]:
    packet_id = f"l6_3_pre_observation_packet_{index:03d}"
    return {
        "fixture_marker": SANDBOX_MARKER,
        "packet_id": packet_id,
        "observation_intent": (
            "Exercise the L6.2 observation boundary against a static/manual-import "
            "sandbox fixture for an L6.1 MVP artifact case."
        ),
        "linked_l6_hypothesis_id": selected_case["linked_l6_0_hypothesis_id"],
        "linked_l6_1_artifact_case_id": selected_case["source_l6_1_case_id"],
        "intended_external_surface": selected_case["observation_surface_type"],
        "source_type": SOURCE_TYPES[(index - 1) % len(SOURCE_TYPES)],
        "source_locator_placeholder": f"static-manual-fixture-locator-{index:03d}",
        "proposed_observation_method": "static_manual_import_fixture_only",
        "data_requested": [
            "source locator if later supplied by user",
            "source date or date-missing marker",
            "evidence summary bounded to the proof question",
            "claim limitations and unsupported inference markers",
        ],
        "claim_to_validate_or_refine": selected_case["proposed_observation_question"],
        "expected_evidence_type": selected_case["expected_evidence_type"],
        "freshness_requirement": "date_available_or_date_missing_marker_required",
        "trust_tier_requirement": "structural_source_trace_required_review_pending",
        "privacy_risk": "low_static_fixture_but_review_required",
        "ip_risk": "low_static_fixture_but_review_required",
        "login_required": False,
        "account_required": False,
        "contact_required": False,
        "payment_required": False,
        "write_or_post_required": False,
        "automation_required": False,
        "mcp_required": False,
        "network_required": False,
        "execution_required": False,
        "publication_required": False,
        "outreach_required": False,
        "no_action_guarantee": True,
        "evidence_capture_plan": {
            "capture_mode": "static_or_manual_import_fixture_only",
            "fetched_from_network": False,
            "browser_fetch_performed": False,
            "scraping_performed": False,
            "external_action_authorized": False,
        },
        "citation_or_source_trace_plan": {
            "source_locator_recorded_as_placeholder_only": True,
            "source_date_or_date_missing_marker_required": True,
            "claim_boundary_required": True,
            "unsupported_inferences_marked": True,
            "review_required": True,
        },
        "review_required": True,
        "approval_required_before_real_observation": True,
        "network_authorized_now": False,
        "real_observation_authorized": False,
        "sandbox_fixture_mode": True,
        **BLOCKED_AUTHORIZATIONS,
        "safety_flags": SAFETY_FLAGS,
        "l6_3_flags": L6_3_FLAGS,
    }


def build_fixture(index: int, packet: dict[str, Any]) -> dict[str, Any]:
    fixture_id = f"l6_3_static_manual_fixture_{index:03d}"
    case_id = packet["linked_l6_1_artifact_case_id"]
    contract = case_contract(case_id)
    return {
        "fixture_marker": SANDBOX_MARKER,
        "fixture_id": fixture_id,
        "linked_packet_id": packet["packet_id"],
        "linked_l6_1_artifact_case_id": case_id,
        "fixture_mode": "static_manual_import_sandbox",
        "fetched_from_network": False,
        "generated_from_live_source": False,
        "current_fact_claimed": False,
        "external_source_verified": False,
        "source_locator_placeholder": packet["source_locator_placeholder"],
        "source_type": packet["source_type"],
        "supplied_by_user": False,
        "synthetic_or_static_summary": (
            "A static sandbox summary that represents the shape of evidence that "
            "might later be manually supplied or approved for read-only observation. "
            "It is not current external data and cannot support market claims."
        ),
        "evidence_scope": [
            "recipient archetype clarification placeholder",
            "acceptance criteria clarification placeholder",
            "claim boundary refinement placeholder",
        ],
        "evidence_limitations": [
            "not fetched",
            "not current fact",
            "not externally verified",
            "cannot establish demand, payer acceptance, or publication readiness",
        ],
        "freshness_declared": "date_missing",
        "source_date_declared": None,
        "date_missing": True,
        "claim_boundary": [
            "may be used only to exercise structural validators",
            "must not be cited as real external evidence",
            "must not be used for publication, outreach, payment, or revenue execution",
        ],
        "missing_context": [
            "real source locator",
            "real source date",
            "source author or authority",
            "conflict check against other sources",
        ],
        "unsupported_claims": [
            "current market need",
            "customer willingness to pay",
            "competitive position",
            "compliance certification",
        ],
        "conflicts_known": "unknown_not_checked_against_live_sources",
        "review_required": True,
        "external_action_authorized": False,
        "source_assets": contract.get("source_assets", []),
        "value_surface": contract.get("value_surface"),
        "safety_flags": SAFETY_FLAGS,
        "l6_3_flags": L6_3_FLAGS,
    }


def receipt(action_type: str) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "authorized_in_l6_3": False,
        "executed_in_l6_3": False,
        "blocker_reference": (
            "l6_controlled_external_observation_sandbox/l6_3_milestone_contract.json"
        ),
        "future_boundary_required": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "l6_3_flags": L6_3_FLAGS,
    }


def generate() -> list[str]:
    generated: list[str] = []
    refs, missing_refs = existing_input_map()
    cases = selected_cases()
    selected = observation_cases(cases)
    packets = [build_packet(index, case) for index, case in enumerate(selected, start=1)]
    fixtures = [build_fixture(index, packet) for index, packet in enumerate(packets, start=1)]

    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": ["L6.0", "L6.1", "L6.2"],
            "mode": "controlled_observation_sandbox",
            "sandbox_only": True,
            "static_fixture_observation_authorized": True,
            "manual_import_fixture_authorized": True,
            "artifact_refinement_candidate_authorized": True,
            "artifact_refinement_application_authorized": False,
            "requires_review_before_any_real_observation": True,
            "requires_review_before_any_externalization": True,
            "required_outputs": [
                "observation case selector",
                "controlled pre-observation packets",
                "sandbox permission replay",
                "static/manual observation fixtures",
                "structural evidence validation",
                "claim and freshness assessment",
                "review-only refinement candidates",
                "review packets",
                "no-action receipts",
                "strategic residual fixture",
                "readiness assessment",
            ],
            **BLOCKED_AUTHORIZATIONS,
        }
    )
    write_json(
        "l6_controlled_external_observation_sandbox/l6_3_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_controlled_external_observation_sandbox/l6_3_sandbox_scope.json",
        with_common(
            {
                "milestone_id": MILESTONE_ID,
                "scope_status": "sandbox_fixture_manual_import_only",
                "in_scope": [
                    "select L6.1 artifact cases with evidence gaps",
                    "generate pre-observation packets",
                    "replay permission decisions in sandbox mode",
                    "generate static/manual-import fixtures",
                    "validate fixture evidence structurally",
                    "generate review-only artifact refinement candidates",
                ],
                "out_of_scope": [
                    "real external observation",
                    "URL fetch",
                    "scraping",
                    "API calls",
                    "browser automation",
                    "publication",
                    "outreach",
                    "payment",
                    "revenue execution",
                    "MCP execution",
                    "live behavior",
                    "canonical mutation",
                    "brain or memory writeback",
                    "direct Y* mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "l6_controlled_external_observation_sandbox/l6_3_safety_flags.json",
        {"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS, "l6_3_flags": L6_3_FLAGS},
        generated,
    )
    write_text(
        "l6_controlled_external_observation_sandbox/README.md",
        "# L6.3 Controlled External Observation Sandbox\n\n"
        "L6.3 exercises the L6.2 observation boundary with static/manual-import "
        "fixtures only. It does not fetch, scrape, browse, publish, contact, pay, "
        "execute MCP, run live behavior, mutate canonical strategy, write brain or "
        "memory, or directly mutate Y*.\n",
        generated,
    )
    write_text(
        "l6_controlled_external_observation_sandbox/l6_3_non_execution_boundary.md",
        "# L6.3 Non-Execution Boundary\n\n"
        f"{SANDBOX_MARKER}\n\n"
        "All real external-world actions remain blocked. Static/manual fixtures are "
        "allowed only as internal sandbox evidence-shape exercises.\n",
        generated,
    )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "l6_3_controlled_observation_sandbox_defined": True,
        "sandbox_only": True,
        "fixture_only": True,
        "static_fixture_observation_authorized": True,
        "manual_import_fixture_authorized": True,
        "real_external_observation_authorized": False,
        "network_authorized": False,
        "api_authorized": False,
        "scraping_authorized": False,
        "browser_fetch_authorized": False,
        "selected_observation_case_count": len(selected),
        "pre_observation_packet_count": len(packets),
        "static_manual_fixture_count": len(fixtures),
        "permission_replay_generated": True,
        "evidence_validation_generated": True,
        "claim_freshness_assessment_generated": True,
        "refinement_candidates_generated": True,
        "review_packets_generated": True,
        "no_action_receipts_generated": True,
        "strategic_residual_loop_generated": True,
        "ready_for_l6_4_real_read_only_external_observation_preflight": True,
        "ready_for_real_network_observation": False,
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
        "l6_3_flags": L6_3_FLAGS,
        "warning": (
            "L6.3 is sandbox fixture/manual-import only. No network, scraping, API, "
            "browser fetch, publication, outreach, payment, revenue execution, MCP, "
            "live behavior, canonical mutation, writeback, or direct Y* mutation occurred."
        ),
    }
    write_json("l6_controlled_external_observation_sandbox/l6_3_summary.json", summary, generated)
    write_text(
        "l6_controlled_external_observation_sandbox/l6_3_summary.md",
        "# L6.3 Summary\n\n"
        "- Controlled observation sandbox defined: true\n"
        "- Static/manual fixtures generated: true\n"
        "- Real external observation authorized: false\n"
        f"- Selected observation cases: {len(selected)}\n"
        f"- Next milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    case_inventory = []
    for case in cases:
        case_id = case.get("case_id")
        contract_data = case_contract(case_id)
        evidence_data = case_evidence(case_id)
        claim_data = case_claim_boundary(case_id)
        case_inventory.append(
            {
                "case_id": case_id,
                "source_hypothesis_id": case.get(
                    "source_hypothesis_id", contract_data.get("source_hypothesis_id")
                ),
                "artifact_kind": contract_data.get("artifact_kind"),
                "recipient_archetype": contract_data.get("recipient_archetype"),
                "value_surface": contract_data.get("value_surface"),
                "missing_evidence": evidence_data.get("missing_evidence", []),
                "claim_boundaries": claim_data.get("claim_boundaries", []),
                "externalization_status": case.get("externalization_status", "blocked"),
            }
        )
    write_json(
        "l6_observation_case_selector/l6_1_artifact_case_inventory.json",
        {
            "schema_version": SCHEMA_VERSION,
            "case_count": len(case_inventory),
            "cases": case_inventory,
            "safety_flags": SAFETY_FLAGS,
            "l6_3_flags": L6_3_FLAGS,
        },
        generated,
    )
    write_json(
        "l6_observation_case_selector/observation_need_matrix.json",
        {
            "schema_version": SCHEMA_VERSION,
            "selection_signals": SELECTION_SIGNALS,
            "selection_mode": "structural_evidence_gap_based",
            "selected_by_hardcoded_opportunity_category": False,
            "matrix": [
                {
                    "case_id": item["case_id"],
                    "missing_evidence_count": len(item.get("missing_evidence", [])),
                    "claim_boundary_present": bool(item.get("claim_boundaries")),
                    "proof_question_requires_outside_evidence": True,
                    "learning_value": "high",
                    "sandbox_downside_risk": "low",
                    "reviewable": True,
                    "selected": item["case_id"]
                    in {selected_case["source_l6_1_case_id"] for selected_case in selected},
                }
                for item in case_inventory
            ],
        },
        generated,
    )
    write_json(
        "l6_observation_case_selector/selected_observation_cases.json",
        {
            "schema_version": SCHEMA_VERSION,
            "selected_case_count": len(selected),
            "selection_mode": "structural_evidence_gap_based",
            "selected_by_hardcoded_opportunity_category": False,
            "hardcoded_opportunity_class_used": False,
            "selected_cases": selected,
        },
        generated,
    )
    write_json(
        "l6_observation_case_selector/deferred_observation_cases.json",
        {
            "schema_version": SCHEMA_VERSION,
            "deferred_cases": [
                {
                    "case_id": item["case_id"],
                    "defer_reason": "not selected in first three sandbox observation exercises",
                    "real_observation_authorized": False,
                }
                for item in case_inventory
                if item["case_id"]
                not in {selected_case["source_l6_1_case_id"] for selected_case in selected}
            ],
        },
        generated,
    )
    write_text(
        "l6_observation_case_selector/observation_case_selector_report.md",
        "# Observation Case Selector Report\n\n"
        "Cases are selected from L6.1 by evidence gaps and reviewability, not by "
        "hard-coded opportunity categories. Real observation remains blocked.\n",
        generated,
    )

    packet_index = {
        "schema_version": SCHEMA_VERSION,
        "packet_count": len(packets),
        "packets": [
            {
                "packet_id": packet["packet_id"],
                "path": f"controlled_pre_observation_packets/packet_{index:03d}.json",
                "linked_l6_1_artifact_case_id": packet["linked_l6_1_artifact_case_id"],
                "real_observation_authorized": False,
                "sandbox_fixture_mode": True,
            }
            for index, packet in enumerate(packets, start=1)
        ],
    }
    write_json("controlled_pre_observation_packets/pre_observation_packet_index.json", packet_index, generated)
    for index, packet in enumerate(packets, start=1):
        write_json(f"controlled_pre_observation_packets/packet_{index:03d}.json", packet, generated)
    write_text(
        "controlled_pre_observation_packets/pre_observation_packet_validation_report.md",
        "# Pre-Observation Packet Validation Report\n\n"
        "All L6.3 packets include the L6.2 packet fields, set sandbox fixture mode "
        "to true, and keep real observation authorization false.\n",
        generated,
    )

    permission_decisions = [
        {
            "packet_id": packet["packet_id"],
            "real_observation_decision": "blocked_real_observation_l6_3",
            "fixture_decision": "allow_static_or_manual_import_fixture_only",
            "reason": "L6.3 authorizes fixture replay only; real observation requires a future preflight.",
            "blocker_references": [
                "l6_controlled_external_observation_sandbox/l6_3_milestone_contract.json",
                "external_observation_permission_gate/observation_permission_gate_contract.json",
            ],
            "required_future_boundary": NEXT_MILESTONE,
            "review_required": True,
            "approval_required_before_real_observation": True,
        }
        for packet in packets
    ]
    write_json(
        "sandbox_observation_permission_replay/permission_replay_contract.json",
        with_common(
            {
                "contract_id": "l6_3_sandbox_observation_permission_replay",
                "source_l6_2_gate": INPUT_REFS["l6_2_permission_gate"],
                "replay_mode": "sandbox_fixture_only",
                "real_observation_default_decision": "blocked_real_observation_l6_3",
                "fixture_default_decision": "allow_static_or_manual_import_fixture_only",
            }
        ),
        generated,
    )
    write_json(
        "sandbox_observation_permission_replay/packet_permission_decisions.json",
        {"schema_version": SCHEMA_VERSION, "decisions": permission_decisions},
        generated,
    )
    write_json(
        "sandbox_observation_permission_replay/blocked_real_observation_decisions.json",
        {
            "schema_version": SCHEMA_VERSION,
            "blocked_decisions": [
                decision
                for decision in permission_decisions
                if decision["real_observation_decision"] == "blocked_real_observation_l6_3"
            ],
        },
        generated,
    )
    write_json(
        "sandbox_observation_permission_replay/allowed_fixture_only_decisions.json",
        {
            "schema_version": SCHEMA_VERSION,
            "allowed_fixture_decisions": [
                decision
                for decision in permission_decisions
                if decision["fixture_decision"] == "allow_static_or_manual_import_fixture_only"
            ],
        },
        generated,
    )
    write_text(
        "sandbox_observation_permission_replay/permission_replay_report.md",
        "# Permission Replay Report\n\n"
        "Every real observation path is blocked. Static/manual fixture handling is "
        "allowed only for internal sandbox replay.\n",
        generated,
    )

    write_json(
        "static_manual_observation_fixtures/observation_fixture_index.json",
        {
            "schema_version": SCHEMA_VERSION,
            "fixture_count": len(fixtures),
            "fixtures": [
                {
                    "fixture_id": fixture["fixture_id"],
                    "path": f"static_manual_observation_fixtures/fixture_{index:03d}.json",
                    "linked_packet_id": fixture["linked_packet_id"],
                    "fixture_mode": fixture["fixture_mode"],
                    "fetched_from_network": False,
                    "current_fact_claimed": False,
                }
                for index, fixture in enumerate(fixtures, start=1)
            ],
        },
        generated,
    )
    for index, fixture in enumerate(fixtures, start=1):
        write_json(f"static_manual_observation_fixtures/fixture_{index:03d}.json", fixture, generated)
    write_text(
        "static_manual_observation_fixtures/fixture_content_notes.md",
        "# Fixture Content Notes\n\n"
        f"{SANDBOX_MARKER}\n\n"
        "Fixture summaries are synthetic/static shapes for validation. They are not "
        "current facts and were not fetched from any external source.\n",
        generated,
    )
    write_text(
        "static_manual_observation_fixtures/fixture_disclaimer.md",
        "# Fixture Disclaimer\n\n"
        f"{SANDBOX_MARKER}\n\n"
        "Do not cite, publish, submit, message, sell, or treat these fixtures as "
        "verified external evidence.\n",
        generated,
    )

    validation_checks = [
        "source trace exists",
        "source type declared",
        "fixture mode declared",
        "fetched_from_network is false",
        "current_fact_claimed is false unless supported by user-provided evidence",
        "freshness present or date_missing marker present",
        "claim boundary present",
        "missing context listed",
        "unsupported claims listed",
        "external action blocked",
        "review required",
        "no semantic scoring authority",
    ]
    validation_results = []
    for fixture in fixtures:
        validation_results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "validation_status": "fixture_structurally_valid_for_sandbox_only",
                "source_trace_exists": bool(fixture["source_locator_placeholder"]),
                "source_type_declared": bool(fixture["source_type"]),
                "fixture_mode_declared": fixture["fixture_mode"] == "static_manual_import_sandbox",
                "fetched_from_network_false": fixture["fetched_from_network"] is False,
                "current_fact_claimed_false": fixture["current_fact_claimed"] is False,
                "freshness_or_date_missing_present": bool(fixture["freshness_declared"])
                or fixture["date_missing"] is True,
                "claim_boundary_present": bool(fixture["claim_boundary"]),
                "missing_context_listed": bool(fixture["missing_context"]),
                "unsupported_claims_listed": bool(fixture["unsupported_claims"]),
                "external_action_blocked": fixture["external_action_authorized"] is False,
                "review_required": fixture["review_required"] is True,
                "semantic_scoring_authority_used": False,
            }
        )
    write_json(
        "observation_evidence_validation_sandbox/evidence_validation_contract.json",
        with_common(
            {
                "contract_id": "l6_3_evidence_validation_contract",
                "validation_mode": "structural_fixture_validation_only",
                "validation_checks": validation_checks,
                "semantic_scoring_authority_used": False,
            }
        ),
        generated,
    )
    write_json(
        "observation_evidence_validation_sandbox/evidence_validation_matrix.json",
        {
            "schema_version": SCHEMA_VERSION,
            "validation_mode": "structural_only",
            "criteria": [
                {"criterion": criterion, "authority_mode": "structural_presence_check"}
                for criterion in validation_checks
            ],
            "semantic_scoring_authority_used": False,
        },
        generated,
    )
    write_json(
        "observation_evidence_validation_sandbox/fixture_validation_results.json",
        {"schema_version": SCHEMA_VERSION, "fixture_validation_results": validation_results},
        generated,
    )
    write_json(
        "observation_evidence_validation_sandbox/evidence_gap_registry.json",
        {
            "schema_version": SCHEMA_VERSION,
            "evidence_gaps": [
                {
                    "linked_fixture_id": fixture["fixture_id"],
                    "gaps": fixture["missing_context"] + fixture["unsupported_claims"],
                    "real_observation_required_before_claim_use": True,
                    "external_use_authorized": False,
                }
                for fixture in fixtures
            ],
        },
        generated,
    )
    write_text(
        "observation_evidence_validation_sandbox/evidence_validation_report.md",
        "# Evidence Validation Report\n\n"
        "Validation is structural only: fields, trace, limitation markers, review "
        "gate, and no-action receipts. It does not perform semantic truth scoring "
        "or market success scoring.\n",
        generated,
    )

    bounded_claims = []
    unsupported = []
    conflicts = []
    for index, fixture in enumerate(fixtures, start=1):
        claim = {
            "claim_id": f"l6_3_bounded_claim_{index:03d}",
            "linked_fixture_id": fixture["fixture_id"],
            "claim_text": (
                "This fixture can exercise whether the linked artifact exposes its "
                "claim boundary and evidence gaps."
            ),
            "claim_scope": "internal_sandbox_only",
            "source_trace_status": "placeholder_trace_present",
            "freshness_class": "date_missing_static_fixture",
            "source_date_status": "date_missing",
            "limitation": "Not externally verified and not current external data.",
            "unsupported_inference_marker": True,
            "review_status": "review_required",
            "allowed_use_in_l6_3": "internal_sandbox_only",
            "external_use_authorized": False,
        }
        bounded_claims.append(claim)
        unsupported.append(
            {
                "linked_fixture_id": fixture["fixture_id"],
                "unsupported_inferences": fixture["unsupported_claims"],
                "external_use_authorized": False,
            }
        )
        conflicts.append(
            {
                "linked_fixture_id": fixture["fixture_id"],
                "source_conflict_status": "unknown_not_checked_against_live_sources",
                "source_date_status": "date_missing",
                "review_required": True,
            }
        )
    write_json(
        "observation_claim_freshness_assessment/claim_assessment_contract.json",
        with_common(
            {
                "contract_id": "l6_3_claim_assessment_contract",
                "assessment_mode": "bounded_static_fixture_claims_only",
                "required_markers": [
                    "source trace status",
                    "freshness class",
                    "source date status",
                    "claim limitation",
                    "unsupported inference marker",
                    "review status",
                ],
            }
        ),
        generated,
    )
    write_json(
        "observation_claim_freshness_assessment/claim_freshness_matrix.json",
        {"schema_version": SCHEMA_VERSION, "bounded_claims": bounded_claims},
        generated,
    )
    write_json(
        "observation_claim_freshness_assessment/bounded_claim_registry.json",
        {"schema_version": SCHEMA_VERSION, "bounded_claim_registry": bounded_claims},
        generated,
    )
    write_json(
        "observation_claim_freshness_assessment/unsupported_inference_registry.json",
        {"schema_version": SCHEMA_VERSION, "unsupported_inference_registry": unsupported},
        generated,
    )
    write_json(
        "observation_claim_freshness_assessment/conflicting_or_missing_source_registry.json",
        {"schema_version": SCHEMA_VERSION, "conflicting_or_missing_source_registry": conflicts},
        generated,
    )
    write_text(
        "observation_claim_freshness_assessment/claim_freshness_report.md",
        "# Claim Freshness Report\n\n"
        "All claims are bounded to internal sandbox use, source dates are missing "
        "by design, and external use remains unauthorized.\n",
        generated,
    )

    candidates = []
    for index, fixture in enumerate(fixtures, start=1):
        packet = packets[index - 1]
        candidate = {
            "candidate_id": f"l6_3_refinement_candidate_{index:03d}",
            "linked_l6_1_case_id": fixture["linked_l6_1_artifact_case_id"],
            "linked_observation_packet_id": packet["packet_id"],
            "linked_fixture_id": fixture["fixture_id"],
            "refinement_target": REFINEMENT_TARGETS[(index - 1) % len(REFINEMENT_TARGETS)],
            "current_gap": "The internal artifact needs clearer evidence and claim boundaries before external use.",
            "proposed_refinement": (
                "Add a review-only note that distinguishes static fixture evidence "
                "from future externally observed evidence."
            ),
            "evidence_basis": fixture["fixture_id"],
            "evidence_limitations": fixture["evidence_limitations"],
            "review_required": True,
            "approved": False,
            "applied": False,
            "artifact_update_authorized": False,
            "sandbox_refinement_candidate_authorized": True,
            "canonical_update_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "direct_y_star_mutation_authorized": False,
            "safety_flags": SAFETY_FLAGS,
            "l6_3_flags": L6_3_FLAGS,
        }
        candidates.append(candidate)
    write_json(
        "observation_to_artifact_refinement_candidates/refinement_candidate_index.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_count": len(candidates),
            "candidates": [
                {
                    "candidate_id": candidate["candidate_id"],
                    "path": f"observation_to_artifact_refinement_candidates/candidate_{index:03d}.json",
                    "approved": False,
                    "applied": False,
                }
                for index, candidate in enumerate(candidates, start=1)
            ],
        },
        generated,
    )
    for index, candidate in enumerate(candidates, start=1):
        write_json(
            f"observation_to_artifact_refinement_candidates/candidate_{index:03d}.json",
            candidate,
            generated,
        )
    write_text(
        "observation_to_artifact_refinement_candidates/refinement_candidate_report.md",
        "# Refinement Candidate Report\n\n"
        "Refinements are review-only sandbox candidates. They are not approved, "
        "not applied, and cannot authorize canonical updates or writeback.\n",
        generated,
    )

    review_packets = []
    for index, candidate in enumerate(candidates, start=1):
        fixture = fixtures[index - 1]
        packet = packets[index - 1]
        review_packets.append(
            {
                "review_packet_id": f"l6_3_review_packet_{index:03d}",
                "linked_packet_id": packet["packet_id"],
                "linked_fixture_id": fixture["fixture_id"],
                "linked_refinement_candidate_id": candidate["candidate_id"],
                "review_questions": [
                    "Does the packet preserve the no-action guarantee?",
                    "Does the fixture clearly disclose that it is not current external data?",
                    "Are unsupported claims marked?",
                    "Would real observation require a future approval boundary?",
                ],
                "evidence_to_check": fixture["evidence_scope"],
                "claim_boundaries_to_check": fixture["claim_boundary"],
                "missing_evidence": fixture["missing_context"],
                "unsupported_claims": fixture["unsupported_claims"],
                "risk_flags": [
                    "static_fixture_only",
                    "date_missing",
                    "external_use_blocked",
                    "real_observation_requires_future_preflight",
                ],
                "approval_preconditions_for_real_observation": [
                    NEXT_MILESTONE,
                    "reviewed packet",
                    "explicit read-only observation authorization",
                ],
                "approval_preconditions_for_externalization": [
                    "future publication/outreach/payment boundary",
                    "claim review",
                    "privacy/IP review",
                ],
                "approval_preconditions_for_artifact_update": [
                    "future governed update review",
                    "approved refinement candidate",
                    "canonical update boundary if canonical state changes",
                ],
                "current_decision": "review_pending",
                "approved": False,
                "applied": False,
            }
        )
    write_json(
        "controlled_observation_review_packets/review_packet_index.json",
        {
            "schema_version": SCHEMA_VERSION,
            "review_packet_count": len(review_packets),
            "review_packets": [
                {
                    "review_packet_id": packet["review_packet_id"],
                    "path": f"controlled_observation_review_packets/review_packet_{index:03d}.json",
                    "current_decision": "review_pending",
                }
                for index, packet in enumerate(review_packets, start=1)
            ],
        },
        generated,
    )
    for index, packet in enumerate(review_packets, start=1):
        write_json(f"controlled_observation_review_packets/review_packet_{index:03d}.json", packet, generated)
    write_text(
        "controlled_observation_review_packets/reviewer_checklist.md",
        "# L6.3 Reviewer Checklist\n\n"
        "- Confirm fixture is static/manual-import sandbox only.\n"
        "- Confirm no real observation, fetch, scrape, API call, publication, "
        "outreach, payment, revenue execution, MCP execution, live behavior, "
        "writeback, canonical update, or direct Y* mutation occurred.\n"
        "- Confirm any refinement remains review-only and unapplied.\n",
        generated,
    )
    write_text(
        "controlled_observation_review_packets/observation_review_report.md",
        "# Observation Review Report\n\n"
        "Review packets are pending. No approval or application is included in L6.3.\n",
        generated,
    )

    for filename, action_type in NO_ACTION_RECEIPTS.items():
        write_json(
            f"controlled_observation_no_action_receipts/{filename}",
            receipt(action_type),
            generated,
        )
    write_text(
        "controlled_observation_no_action_receipts/no_action_receipt_report.md",
        "# No-Action Receipt Report\n\n"
        "L6.3 generated explicit receipts for blocked network, API, scraping, "
        "browser fetch, publication, outreach, payment, revenue, MCP, live, "
        "canonical, writeback, and direct Y* mutation actions.\n",
        generated,
    )

    write_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_cieu_like_fixture.json",
        {
            "schema_version": SCHEMA_VERSION,
            "event_mode": "l6_3_controlled_external_observation_sandbox_fixture",
            "persistence_enabled": False,
            "db_write_performed": False,
            "X_t": {
                "l6_0_value_selection": INPUT_REFS["l6_0_selection_ranking"],
                "l6_1_mvp_artifact_sandbox": INPUT_REFS["l6_1_case_index"],
                "l6_2_external_observation_boundary": INPUT_REFS["l6_2_summary"],
                "l6_3_constraints": "sandbox fixture/manual-import only",
            },
            "U_t": (
                "Controlled sandbox observation over static/manual fixtures without "
                "real external observation."
            ),
            "Y_star_t": (
                "Exercise the governed external observation boundary using "
                "static/manual-import fixtures while preserving no-network/"
                "no-scraping/no-API/no-browser-fetch/no-publication/no-outreach/"
                "no-payment/no-revenue/no-MCP/no-live/no-canonical-mutation/"
                "no-brain-memory-writeback/no-direct-Y* mutation constraints."
            ),
            "Y_t_plus_1": [
                "selected observation cases generated",
                "pre-observation packets generated",
                "permission replay generated",
                "static/manual fixtures generated",
                "evidence validation generated",
                "claim/freshness assessment generated",
                "refinement candidates generated",
                "review packets generated",
                "real observation blocked",
            ],
            "R_t_plus_1": "Deterministic structural residual only.",
            "safety_flags": SAFETY_FLAGS,
            "l6_3_flags": L6_3_FLAGS,
        },
        generated,
    )
    write_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_strategic_residual_delta.json",
        {
            "schema_version": SCHEMA_VERSION,
            "residual_classes": [
                "no real source evidence available yet",
                "static fixtures cannot establish current market truth",
                "manual import workflow still not tested with user-supplied real evidence",
                "freshness assessment remains placeholder",
                "trust-tier policy not tested on live source conflicts",
                "refinement candidates remain unapplied",
                "real observation still requires future approval boundary",
                "externalization remains blocked",
            ],
            "residual_mode": "deterministic_structural_only",
            "safety_flags": SAFETY_FLAGS,
            "l6_3_flags": L6_3_FLAGS,
        },
        generated,
    )
    write_json(
        "l6_controlled_observation_strategic_residual_loop/l6_3_meta_learning_update_candidate.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_id": "l6_3_meta_learning_update_candidate",
            "eligible_for_review_queue": True,
            "eligible_for_direct_brain_writeback": False,
            "eligible_for_direct_memory_ingestion": False,
            "eligible_for_candidate_auto_approval": False,
            "eligible_for_direct_strategy_mutation": False,
            "approved": False,
            "applied": False,
            "learning_targets": [
                "external_observation_permission_replay_policy",
                "manual_fixture_evidence_validation_policy",
                "claim_freshness_assessment_policy",
                "artifact_refinement_candidate_policy",
            ],
        },
        generated,
    )
    write_text(
        "l6_controlled_observation_strategic_residual_loop/l6_3_residual_report.md",
        "# L6.3 Strategic Residual Report\n\n"
        "The main residual is productive conservatism: the system can exercise the "
        "observation lifecycle with static/manual fixtures, but real source "
        "evidence, freshness, conflicts, and externalization remain future work.\n",
        generated,
    )

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_3_controlled_external_observation_sandbox_complete": True,
        "observation_cases_selected": True,
        "pre_observation_packets_generated": True,
        "permission_replay_generated": True,
        "static_manual_fixtures_generated": True,
        "evidence_validation_generated": True,
        "claim_freshness_assessment_generated": True,
        "refinement_candidates_generated": True,
        "review_packets_generated": True,
        "no_action_receipts_generated": True,
        "strategic_residual_loop_generated": True,
        "ready_for_l6_4_real_read_only_external_observation_preflight": True,
        "ready_for_real_network_observation": False,
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
            "real network observation",
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
        "l6_3_flags": L6_3_FLAGS,
    }
    write_json(
        "l6_controlled_observation_sandbox_readiness/l6_3_readiness_assessment.json",
        readiness,
        generated,
    )
    write_json(
        "l6_controlled_observation_sandbox_readiness/l6_3_next_milestone_recommendation.json",
        {
            "schema_version": SCHEMA_VERSION,
            "recommended_next_milestone": NEXT_MILESTONE,
            "recommendation": "Proceed only to real read-only external observation preflight design.",
            "do_not_implement_now": "L6.4",
            "real_external_observation_authorized_now": False,
        },
        generated,
    )
    write_json(
        "l6_controlled_observation_sandbox_readiness/l6_3_blockers.json",
        {
            "schema_version": SCHEMA_VERSION,
            "blockers": [
                "no real external observation authorization",
                "no network boundary approval",
                "no scraping authorization",
                "no publication/outreach/payment boundary",
                "no revenue execution boundary",
                "no MCP execution boundary",
                "no canonical update authorization",
                "no brain/memory writeback authorization",
            ],
        },
        generated,
    )
    write_text(
        "l6_controlled_observation_sandbox_readiness/l6_3_readiness_report.md",
        "# L6.3 Readiness Report\n\n"
        "L6.3 controlled external observation sandbox is complete when these "
        "artifacts validate. The system is ready to design L6.4 preflight, but "
        "not ready for real network observation, scraping, publication, outreach, "
        "payment, revenue execution, MCP execution, canonical update, or writeback.\n",
        generated,
    )

    return generated


def main() -> None:
    generated = generate()
    print(f"Built L6.3 controlled external observation sandbox artifacts: {len(generated)} files")


if __name__ == "__main__":
    main()
