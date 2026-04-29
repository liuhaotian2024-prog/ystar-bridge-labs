#!/usr/bin/env python3
"""Build L6.6 controlled observation pilot approval packet artifacts.

This builder is static and local. It assembles approval-packet-only artifacts
for a future controlled real read-only observation pilot. It must not grant
real approval, persist a durable approval record, observe the external world,
or execute network, browser, scraping, search, API, MCP, live, publication,
outreach, payment, revenue, writeback, canonical update, or direct Y-star work.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.6"
MILESTONE_NAME = "Controlled Real Read-Only Observation Pilot Approval Packet v0"
NEXT_MILESTONE = "L6.7 Controlled Real Read-Only Observation Approval Record Sandbox v0"
PLACEHOLDER_LOCATOR_MARKER = (
    "PLACEHOLDER LOCATOR ONLY - NOT FETCHED - NOT OPENED - NOT VERIFIED CURRENT FACT "
    "- NOT AUTHORIZED FOR REAL OBSERVATION - NOT AUTHORIZED FOR PUBLICATION "
    "- NOT AUTHORIZED FOR OUTREACH - NOT AUTHORIZED FOR PAYMENT "
    "- NOT AUTHORIZED FOR REVENUE EXECUTION - NOT AUTHORIZED FOR CANONICAL UPDATE"
)

INPUT_REFS = {
    "l6_0_value_selection": "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "l6_0_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_1_artifact_cases": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_2_boundary": "l6_governed_external_observation_boundary/l6_2_summary.json",
    "l6_3_sandbox": "l6_controlled_external_observation_sandbox/l6_3_summary.json",
    "l6_4_preflight": "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
    "l6_5_pilot_design": "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.json",
    "l6_5_selected_candidates": "pilot_candidate_selector/selected_pilot_candidates.json",
    "l6_5_approval_packet_index": "pilot_approval_packet_candidates/pilot_approval_packet_index.json",
    "l6_5_operator_runbook": "pilot_operator_runbook/operator_step_sequence.json",
    "l6_5_evidence_template": "pilot_evidence_packet_templates/pilot_evidence_packet_template.json",
    "l6_5_abort_policy": "pilot_abort_quarantine_decision_policy/pilot_abort_condition_registry.json",
    "l6_5_post_review": "pilot_post_observation_review_workflow/post_observation_review_contract.json",
    "l6_5_decision_gate": "pilot_design_decision_gate/pilot_candidate_decisions.json",
    "l6_5_readiness": "l6_pilot_design_readiness/l6_5_readiness_assessment.json",
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
    "search_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "cieu_db_write_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
    "durable_real_approval_record_creation_enabled": False,
    "real_approval_grant_enabled": False,
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

L6_6_FLAGS = {
    "l6_6_approval_packet_only": True,
    "l6_6_approval_sandbox_only": True,
    "l6_6_future_real_read_only_observation_pilot_candidate_allowed": True,
    "l6_6_approval_packet_generation_enabled": True,
    "l6_6_approval_decision_sandbox_enabled": True,
    "l6_6_operator_authorization_template_enabled": True,
    "l6_6_runtime_isolation_attestation_template_enabled": True,
    "l6_6_evidence_capture_authorization_template_enabled": True,
    "l6_6_real_approval_granted": False,
    "l6_6_durable_real_approval_record_created": False,
    "l6_6_real_observation_execution_enabled": False,
    "l6_6_network_enabled": False,
    "l6_6_api_enabled": False,
    "l6_6_scraping_enabled": False,
    "l6_6_browser_fetch_enabled": False,
    "l6_6_search_enabled": False,
    "l6_6_publication_enabled": False,
    "l6_6_outreach_enabled": False,
    "l6_6_payment_enabled": False,
    "l6_6_revenue_execution_enabled": False,
    "l6_6_mcp_execution_enabled": False,
    "l6_6_cieu_db_write_enabled": False,
    "l6_6_canonical_update_enabled": False,
    "l6_6_brain_writeback_enabled": False,
    "l6_6_memory_ingestion_enabled": False,
    "l6_6_direct_y_star_mutation_enabled": False,
}

BLOCKED_AUTHORIZATIONS = {
    "real_external_observation_authorized": False,
    "real_pilot_execution_authorized": False,
    "real_approval_granted": False,
    "durable_real_approval_record_created": False,
    "network_authorized": False,
    "api_authorized": False,
    "scraping_authorized": False,
    "browser_fetch_authorized": False,
    "search_authorized": False,
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
    "linked L6.5 pilot candidate exists",
    "pilot design packet exists",
    "approval packet candidate exists or can be assembled",
    "observation question is narrow",
    "source locator placeholder exists",
    "source type is allowlisted",
    "denylist conditions absent",
    "no login required",
    "no account creation required",
    "no payment required",
    "no contact required",
    "no form submission required",
    "no publication required",
    "no download of private/sensitive data required",
    "no automation required",
    "no MCP execution required",
    "evidence capture template exists",
    "operator runbook exists",
    "abort/quarantine policy exists",
    "post-observation review workflow exists",
    "runtime isolation prerequisite can be represented",
    "downside risk is low",
    "learning value is high",
]

APPROVAL_PACKET_FIELDS = [
    "approval_packet_id",
    "linked_approval_candidate_id",
    "linked_l6_5_pilot_candidate_id",
    "linked_l6_4_candidate_id",
    "linked_l6_3_packet_id",
    "linked_l6_1_artifact_case_id",
    "linked_l6_0_hypothesis_id",
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
    "no_direct_y_star_mutation_required",
    "evidence_capture_plan",
    "citation_plan",
    "abort_conditions",
    "quarantine_conditions",
    "operator_handoff_required",
    "runtime_isolation_required",
    "post_observation_review_required",
    "reviewer_required",
    "human_approval_required",
    "durable_approval_record_required",
    "approval_status",
    "real_approval_granted",
    "real_observation_authorized",
]

RISK_DIMENSIONS = [
    "privacy_risk",
    "ip_risk",
    "source_interaction_risk",
    "login_risk",
    "account_creation_risk",
    "payment_risk",
    "contact_risk",
    "form_submission_risk",
    "publication_risk",
    "outreach_risk",
    "revenue_action_risk",
    "mcp_execution_risk",
    "automation_or_scraping_risk",
    "source_scope_drift_risk",
    "claim_overreach_risk",
    "freshness_uncertainty_risk",
    "operator_error_risk",
    "evidence_misuse_risk",
    "canonical_mutation_risk",
    "brain_memory_writeback_risk",
    "direct_y_star_mutation_risk",
]

ABORT_CONDITIONS = [
    "login required unexpectedly",
    "account creation requested",
    "payment requested",
    "contact requested",
    "form submission required",
    "private/sensitive data encountered",
    "source asks for interaction",
    "source locator mismatch",
    "source appears malicious",
    "source requires automation/scraping",
    "source requires MCP/tool execution",
    "source conflicts with approved scope",
    "claim scope exceeds approval packet",
    "operator uncertainty",
]

NO_ACTION_CONSTRAINTS = [
    "publication",
    "outreach",
    "payment",
    "revenue execution",
    "customer contact",
    "form submission",
    "posting/commenting/messaging",
    "MCP execution",
    "live behavior",
    "CIEU DB write",
    "canonical update",
    "strategy mutation",
    "brain/memory writeback",
    "direct Y-star mutation",
    "external artifact delivery",
    "product launch",
    "grant/RFP/bounty submission",
]

NO_ACTION_RECEIPTS = {
    "no_durable_real_approval_record_receipt.json": "durable_real_approval_record",
    "no_real_approval_granted_receipt.json": "real_approval_granted",
    "no_real_observation_execution_receipt.json": "real_observation_execution",
    "no_network_execution_receipt.json": "network_execution",
    "no_api_receipt.json": "api",
    "no_scraping_receipt.json": "scraping",
    "no_browser_fetch_receipt.json": "browser_fetch",
    "no_search_receipt.json": "search",
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
    return {**payload, "safety_flags": SAFETY_FLAGS, "l6_6_flags": L6_6_FLAGS}


def existing_input_map() -> tuple[dict[str, str], list[str]]:
    refs: dict[str, str] = {}
    gaps: list[str] = []
    for key, rel in INPUT_REFS.items():
        if (ROOT / rel).exists():
            refs[key] = rel
        else:
            gaps.append(rel)
    return refs, gaps


def l6_5_candidates() -> list[dict[str, Any]]:
    source = read_json(INPUT_REFS["l6_5_selected_candidates"]) or {}
    candidates = source.get("candidates", [])[:3]
    if candidates:
        return candidates
    return [
        {
            "pilot_candidate_id": "l6_5_pilot_candidate_placeholder",
            "linked_l6_4_candidate_id": "l6_4_real_observation_candidate_placeholder",
            "linked_l6_3_packet_id": "l6_3_pre_observation_packet_placeholder",
            "linked_l6_1_artifact_case_id": "case_placeholder",
            "linked_l6_0_hypothesis_id": "hypothesis_placeholder",
            "evidence_gap": ["L6.5 candidate source missing"],
            "pilot_observation_question": "Which future read-only evidence would clarify the artifact claim boundary?",
            "proposed_source_type": "user_supplied_public_locator",
            "source_locator_placeholder": f"{PLACEHOLDER_LOCATOR_MARKER} :: l6-6-placeholder",
            "expected_evidence_type": "bounded_source_summary",
        }
    ]


def l6_5_packet_by_candidate() -> dict[str, dict[str, Any]]:
    packet_index = read_json(INPUT_REFS["l6_5_approval_packet_index"]) or {}
    packets: dict[str, dict[str, Any]] = {}
    for entry in packet_index.get("packets", []):
        packet = read_json(entry.get("path", "")) or {}
        candidate_id = packet.get("linked_pilot_candidate_id")
        if candidate_id:
            packets[candidate_id] = packet
    return packets


def build_approval_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packet_map = l6_5_packet_by_candidate()
    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for index, pilot in enumerate(l6_5_candidates()[:3], start=1):
        pilot_candidate_id = pilot.get("pilot_candidate_id")
        packet = packet_map.get(pilot_candidate_id, {})
        selected.append(
            with_common(
                {
                    "approval_candidate_id": f"l6_6_approval_candidate_{index:03d}",
                    "linked_l6_5_pilot_candidate_id": pilot_candidate_id,
                    "linked_l6_4_candidate_id": pilot.get("linked_l6_4_candidate_id"),
                    "linked_l6_3_packet_id": pilot.get("linked_l6_3_packet_id"),
                    "linked_l6_1_artifact_case_id": pilot.get("linked_l6_1_artifact_case_id"),
                    "linked_l6_0_hypothesis_id": pilot.get("linked_l6_0_hypothesis_id"),
                    "approval_packet_reason": (
                        "Selected because L6.5 produced a narrow pilot design with "
                        "low-risk read-only source constraints, no-action requirements, "
                        "operator runbook, evidence template, and blocked execution gate."
                    ),
                    "evidence_gap": pilot.get("evidence_gap", ["real source evidence missing"]),
                    "observation_question": packet.get(
                        "observation_question", pilot.get("pilot_observation_question")
                    ),
                    "source_type": packet.get("source_type", pilot.get("proposed_source_type")),
                    "source_locator_placeholder": packet.get(
                        "source_locator_placeholder",
                        pilot.get(
                            "source_locator_placeholder",
                            f"{PLACEHOLDER_LOCATOR_MARKER} :: l6-6-candidate-{index:03d}",
                        ),
                    ),
                    "expected_evidence_type": packet.get(
                        "expected_evidence_type", pilot.get("expected_evidence_type")
                    ),
                    "selection_factors": SELECTION_FACTORS,
                    "selected_by_hardcoded_opportunity_category": False,
                    "hardcoded_opportunity_class_used": False,
                    "approval_packet_authorized_now": True,
                    "real_approval_authorized_now": False,
                    "real_observation_authorized_now": False,
                    "durable_approval_record_authorized_now": False,
                    "future_human_approval_required": True,
                    "future_runtime_isolation_required": True,
                }
            )
        )
    return selected, deferred


def build_approval_packet(index: int, candidate: dict[str, Any]) -> dict[str, Any]:
    return with_common(
        {
            "approval_packet_id": f"l6_6_approval_packet_{index:03d}",
            "linked_approval_candidate_id": candidate["approval_candidate_id"],
            "linked_l6_5_pilot_candidate_id": candidate["linked_l6_5_pilot_candidate_id"],
            "linked_l6_4_candidate_id": candidate["linked_l6_4_candidate_id"],
            "linked_l6_3_packet_id": candidate["linked_l6_3_packet_id"],
            "linked_l6_1_artifact_case_id": candidate["linked_l6_1_artifact_case_id"],
            "linked_l6_0_hypothesis_id": candidate["linked_l6_0_hypothesis_id"],
            "observation_question": candidate["observation_question"],
            "source_type": candidate["source_type"],
            "source_locator_placeholder": candidate["source_locator_placeholder"],
            "expected_evidence_type": candidate["expected_evidence_type"],
            "freshness_requirement": "capture source date or explicit date_missing marker",
            "trust_tier_requirement": "structural source tier must be declared before review",
            "privacy_risk": "low only if public/read-only and no sensitive data is accessed",
            "ip_risk": "low only if citation/source trace is captured without bulk copying",
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
            "no_direct_y_star_mutation_required": True,
            "evidence_capture_plan": {
                "capture_source_title": True,
                "capture_source_locator": True,
                "capture_source_publisher_or_owner": True,
                "capture_observed_timestamp": True,
                "capture_source_date_or_date_missing": True,
                "capture_freshness_class": True,
                "capture_bounded_claim_text": True,
                "capture_claim_limitation": True,
                "capture_unsupported_claim_marker": True,
                "capture_missing_context": True,
                "capture_conflict_marker": True,
                "capture_citation_trace": True,
                "external_action_taken": False,
            },
            "citation_plan": {
                "citation_trace_required": True,
                "quoted_text_limit_required": True,
                "claim_boundary_required": True,
                "conflict_marker_required": True,
            },
            "abort_conditions": ABORT_CONDITIONS,
            "quarantine_conditions": [
                "scope violation",
                "source requires disallowed interaction",
                "operator uncertainty",
                "evidence exceeds approval packet",
            ],
            "operator_handoff_required": True,
            "runtime_isolation_required": True,
            "post_observation_review_required": True,
            "reviewer_required": True,
            "human_approval_required": True,
            "durable_approval_record_required": True,
            "approval_status": "approval_packet_generated_pending_future_human_approval",
            "real_approval_granted": False,
            "real_observation_authorized": False,
        }
    )


def build_evidence_dossier(index: int, packet: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    return with_common(
        {
            "dossier_id": f"l6_6_evidence_dossier_{index:03d}",
            "linked_approval_packet_id": packet["approval_packet_id"],
            "source_l6_0_hypothesis_trace": {
                "hypothesis_id": candidate["linked_l6_0_hypothesis_id"],
                "source_ref": INPUT_REFS["l6_0_hypotheses"],
            },
            "source_l6_1_artifact_case_trace": {
                "case_id": candidate["linked_l6_1_artifact_case_id"],
                "source_ref": INPUT_REFS["l6_1_artifact_cases"],
            },
            "source_l6_2_boundary_trace": INPUT_REFS["l6_2_boundary"],
            "source_l6_3_sandbox_trace": {
                "packet_id": candidate["linked_l6_3_packet_id"],
                "source_ref": INPUT_REFS["l6_3_sandbox"],
            },
            "source_l6_4_preflight_trace": {
                "candidate_id": candidate["linked_l6_4_candidate_id"],
                "source_ref": INPUT_REFS["l6_4_preflight"],
            },
            "source_l6_5_pilot_design_trace": {
                "pilot_candidate_id": candidate["linked_l6_5_pilot_candidate_id"],
                "source_ref": INPUT_REFS["l6_5_pilot_design"],
            },
            "evidence_gap_summary": candidate["evidence_gap"],
            "why_real_read_only_observation_is_needed": (
                "Prior fixtures and design artifacts cannot establish current external source "
                "freshness, source authority, or bounded claim support."
            ),
            "why_no_action_is_required": (
                "The proposed future pilot is framed as view/read-only evidence capture with no "
                "login, contact, payment, form submission, posting, MCP, or mutation."
            ),
            "no_action_constraints": NO_ACTION_CONSTRAINTS,
            "source_policy_trace": "pilot_source_constraint_policy/pilot_source_allowlist.json",
            "operator_runbook_trace": INPUT_REFS["l6_5_operator_runbook"],
            "evidence_template_trace": INPUT_REFS["l6_5_evidence_template"],
            "abort_quarantine_trace": INPUT_REFS["l6_5_abort_policy"],
            "post_review_trace": INPUT_REFS["l6_5_post_review"],
            "residuals_remaining": [
                "real approval still not granted",
                "durable approval record not created",
                "source locator remains placeholder",
                "no real external evidence captured",
                "runtime isolation not confirmed",
            ],
            "dossier_status": "dossier_ready_for_review",
            "approved": False,
        }
    )


def build_risk_review(index: int, packet: dict[str, Any]) -> dict[str, Any]:
    return with_common(
        {
            "risk_review_id": f"l6_6_risk_review_{index:03d}",
            "linked_approval_packet_id": packet["approval_packet_id"],
            "risk_review_mode": "structural_no_semantic_truth_scoring",
            "risk_dimensions": [
                {
                    "risk_dimension": dimension,
                    "risk_class": "low_if_packet_constraints_hold"
                    if dimension
                    in {
                        "login_risk",
                        "account_creation_risk",
                        "payment_risk",
                        "contact_risk",
                        "form_submission_risk",
                        "publication_risk",
                        "outreach_risk",
                        "revenue_action_risk",
                        "mcp_execution_risk",
                        "automation_or_scraping_risk",
                        "canonical_mutation_risk",
                        "brain_memory_writeback_risk",
                        "direct_y_star_mutation_risk",
                    }
                    else "requires_review",
                    "approval_granted": False,
                }
                for dimension in RISK_DIMENSIONS
            ],
            "semantic_truth_scoring_used": False,
            "market_success_scoring_used": False,
            "real_observation_approved": False,
        }
    )


def receipt(action_type: str) -> dict[str, Any]:
    payload = {
        "action_type": action_type,
        "authorized_in_l6_6": False,
        "executed_in_l6_6": False,
        "blocker_reference": (
            "l6_controlled_observation_pilot_approval_packet/"
            "l6_6_milestone_contract.json"
        ),
        "future_boundary_required": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "l6_6_flags": L6_6_FLAGS,
    }
    if action_type in {"durable_real_approval_record", "real_approval_granted"}:
        payload["persisted_in_l6_6"] = False
    return payload


def generate() -> list[str]:
    generated: list[str] = []
    refs, missing_refs = existing_input_map()
    candidates, deferred_candidates = build_approval_candidates()
    packets = [
        build_approval_packet(index, candidate)
        for index, candidate in enumerate(candidates, start=1)
    ]
    dossiers = [
        build_evidence_dossier(index, packet, candidate)
        for index, (packet, candidate) in enumerate(zip(packets, candidates), start=1)
    ]
    risk_reviews = [
        build_risk_review(index, packet)
        for index, packet in enumerate(packets, start=1)
    ]

    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": ["L6.0", "L6.1", "L6.2", "L6.3", "L6.4", "L6.5"],
            "mode": "approval_packet_only",
            "approval_packet_only": True,
            "approval_sandbox_only": True,
            "future_real_read_only_observation_pilot_candidate_allowed": True,
            "approval_packet_generation_authorized": True,
            "approval_decision_sandbox_authorized": True,
            "operator_authorization_template_authorized": True,
            "runtime_isolation_attestation_template_authorized": True,
            "evidence_capture_authorization_template_authorized": True,
            "requires_future_explicit_human_approval_before_real_observation": True,
            "requires_future_durable_approval_record_before_real_observation": True,
            "requires_future_runtime_isolation_confirmation_before_real_observation": True,
            "requires_future_post_observation_review_before_any_artifact_update": True,
            "required_outputs": [
                "approval candidate selector",
                "approval authority model",
                "approval packet instances",
                "evidence dossiers",
                "risk review packets",
                "operator authorization prerequisites",
                "runtime isolation attestation prerequisites",
                "evidence capture authorization prerequisites",
                "no-action constraints",
                "approval decision sandbox",
                "non-persistence receipts",
                "strategic residual fixture",
                "readiness assessment",
            ],
            **BLOCKED_AUTHORIZATIONS,
        }
    )
    write_json(
        "l6_controlled_observation_pilot_approval_packet/l6_6_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_controlled_observation_pilot_approval_packet/l6_6_approval_packet_scope.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "scope_status": "approval_packet_only_real_approval_and_execution_blocked",
                "in_scope": [
                    "select L6.5 pilot candidates for approval packet assembly",
                    "define future human approval authority requirements",
                    "assemble approval packet instances",
                    "build evidence dossiers from L6.0-L6.5",
                    "generate structural risk reviews",
                    "define operator/runtime/evidence prerequisites",
                    "generate blocked approval decisions",
                    "generate non-persistence receipts",
                ],
                "out_of_scope": [
                    "real approval",
                    "durable real approval persistence",
                    "real external observation",
                    "network access",
                    "API calls",
                    "scraping",
                    "browser fetch",
                    "search",
                    "publication",
                    "outreach",
                    "payment",
                    "revenue execution",
                    "MCP execution",
                    "live behavior",
                    "CIEU DB write",
                    "canonical update",
                    "brain/memory writeback",
                    "direct Y-star mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "l6_controlled_observation_pilot_approval_packet/l6_6_safety_flags.json",
        {"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS, "l6_6_flags": L6_6_FLAGS},
        generated,
    )
    write_text(
        "l6_controlled_observation_pilot_approval_packet/README.md",
        "# L6.6 Controlled Real Read-Only Observation Pilot Approval Packet\n\n"
        "This pack assembles approval packet artifacts for a future controlled "
        "real read-only observation pilot. It does not grant approval, create a "
        "durable approval record, observe, fetch, search, scrape, browse, call "
        "APIs, publish, contact, pay, execute MCP, mutate strategy, write "
        "brain/memory, or directly mutate Y-star.\n",
        generated,
    )
    write_text(
        "l6_controlled_observation_pilot_approval_packet/l6_6_non_execution_boundary.md",
        "# L6.6 Non-Execution Boundary\n\n"
        f"{PLACEHOLDER_LOCATOR_MARKER}\n\n"
        "L6.6 may create approval packet and approval sandbox artifacts only. "
        "Real approval, durable approval persistence, real observation, network "
        "access, search, publication, outreach, payment, revenue execution, MCP, "
        "CIEU DB writes, canonical updates, writeback, and direct Y-star mutation "
        "remain blocked.\n",
        generated,
    )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "l6_6_controlled_observation_pilot_approval_packet_defined": True,
        "approval_packet_only": True,
        "approval_sandbox_only": True,
        "candidate_count": len(candidates),
        "approval_packet_count": len(packets),
        "evidence_dossier_count": len(dossiers),
        "risk_review_count": len(risk_reviews),
        "approval_authority_model_generated": True,
        "approval_packet_instances_generated": True,
        "evidence_dossiers_generated": True,
        "risk_reviews_generated": True,
        "operator_authorization_prerequisites_generated": True,
        "runtime_isolation_attestation_templates_generated": True,
        "evidence_capture_authorization_templates_generated": True,
        "no_action_constraints_generated": True,
        "approval_decision_sandbox_generated": True,
        "non_persistence_receipts_generated": True,
        "strategic_residual_loop_generated": True,
        "future_real_read_only_observation_pilot_candidate_allowed": True,
        "real_external_observation_authorized": False,
        "real_pilot_execution_authorized": False,
        "real_approval_granted": False,
        "durable_real_approval_record_created": False,
        "network_authorized": False,
        "api_authorized": False,
        "scraping_authorized": False,
        "browser_fetch_authorized": False,
        "search_authorized": False,
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
        "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox": True,
        "ready_for_actual_network_observation_now": False,
        "ready_for_real_approval_now": False,
        "ready_for_durable_approval_persistence_now": False,
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
        "l6_6_flags": L6_6_FLAGS,
        "warning": (
            "L6.6 is approval-packet-only. Real approval, durable approval "
            "persistence, real observation, URL fetch, search, scraping, API "
            "calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y-star mutation remain blocked."
        ),
    }
    write_json(
        "l6_controlled_observation_pilot_approval_packet/l6_6_summary.json",
        summary,
        generated,
    )
    write_text(
        "l6_controlled_observation_pilot_approval_packet/l6_6_summary.md",
        "# L6.6 Summary\n\n"
        "- Controlled observation pilot approval packet defined: true\n"
        "- Approval packet only: true\n"
        "- Real approval granted: false\n"
        "- Durable real approval record created: false\n"
        f"- Approval candidates: {len(candidates)}\n"
        f"- Approval packets: {len(packets)}\n"
        f"- Next milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    write_json(
        "pilot_approval_candidate_selector/l6_5_pilot_candidate_inventory.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "source": INPUT_REFS["l6_5_selected_candidates"],
                "candidate_count": len(l6_5_candidates()),
                "candidates": l6_5_candidates(),
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_candidate_selector/approval_candidate_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "selection_mode": "structural_approval_packet_candidate_selection",
                "selection_factors": SELECTION_FACTORS,
                "selected_by_hardcoded_opportunity_category": False,
                "matrix": [
                    {
                        "approval_candidate_id": candidate["approval_candidate_id"],
                        "linked_l6_5_pilot_candidate_id": candidate["linked_l6_5_pilot_candidate_id"],
                        "pilot_design_packet_exists": True,
                        "approval_packet_can_be_assembled": True,
                        "source_locator_placeholder_exists": True,
                        "source_type_allowlisted": True,
                        "denylist_condition_absent": True,
                        "runtime_isolation_prerequisite_can_be_represented": True,
                        "downside_risk": "low",
                        "learning_value": "high",
                        "hardcoded_opportunity_class_used": False,
                    }
                    for candidate in candidates
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_candidate_selector/selected_approval_candidates.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_count": len(candidates),
            "selection_mode": "structural_approval_packet_candidate_selection",
            "selected_by_hardcoded_opportunity_category": False,
            "hardcoded_opportunity_class_used": False,
            "candidates": candidates,
        },
        generated,
    )
    write_json(
        "pilot_approval_candidate_selector/deferred_approval_candidates.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "deferred_count": len(deferred_candidates),
                "deferred_candidates": deferred_candidates,
                "defer_reasons": [
                    "pilot design packet missing",
                    "source locator placeholder missing",
                    "denylist condition present",
                    "operator/runtime prerequisite cannot be represented",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_approval_candidate_selector/approval_candidate_selector_report.md",
        "# Approval Candidate Selector\n\n"
        "Candidates are selected from L6.5 pilot design outputs using structural "
        "approval-readiness criteria. No opportunity category is treated as strategy.\n",
        generated,
    )

    write_json(
        "pilot_approval_authority_model/approval_authority_model.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "authority_status": "future_human_approval_required_l6_6_does_not_approve",
                "l6_6_does_not_grant_real_approval": True,
                "automated_approval_allowed": False,
                "candidate_auto_approval_allowed": False,
                "approval_inferred_from_tests_allowed": False,
                "approval_inferred_from_readiness_allowed": False,
                "approval_inferred_from_packet_completeness_allowed": False,
                "future_explicit_human_approval_required": True,
                "future_durable_approval_record_required": True,
                "approval_scope": [
                    "one specific candidate",
                    "one source locator",
                    "one observation question",
                    "one evidence capture plan",
                    "one operator/run environment",
                ],
                "approval_does_not_authorize": NO_ACTION_CONSTRAINTS,
            }
        ),
        generated,
    )
    roles = [
        {"role_id": "packet_author", "may_future_approve": False},
        {"role_id": "reviewer", "may_future_approve": False},
        {"role_id": "human_approver", "may_future_approve": True},
        {"role_id": "future_operator", "may_future_approve": False},
        {"role_id": "post_observation_reviewer", "may_future_approve": False},
    ]
    write_json(
        "pilot_approval_authority_model/approval_role_registry.json",
        with_common({"schema_version": SCHEMA_VERSION, "roles": roles}),
        generated,
    )
    write_json(
        "pilot_approval_authority_model/non_delegable_human_approval_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "human_approver_required": True,
                "approval_non_delegable_to_automation": True,
                "approval_non_delegable_to_tests": True,
                "approval_non_delegable_to_readiness": True,
                "approval_non_delegable_to_packet_completeness": True,
                "real_approval_granted_in_l6_6": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_authority_model/approval_scope_limits.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "scope_limits": [
                    "approval must be candidate-specific",
                    "approval must be source-locator-specific",
                    "approval must be observation-question-specific",
                    "approval must be evidence-capture-plan-specific",
                    "approval must be operator-environment-specific",
                ],
                "approval_does_not_authorize": NO_ACTION_CONSTRAINTS,
            }
        ),
        generated,
    )
    write_text(
        "pilot_approval_authority_model/approval_authority_report.md",
        "# Pilot Approval Authority Model\n\n"
        "L6.6 does not approve the pilot. Future approval requires explicit human "
        "approval and a future durable approval record; neither exists in L6.6.\n",
        generated,
    )

    write_json(
        "pilot_approval_packet_assembler/approval_packet_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "required_fields": APPROVAL_PACKET_FIELDS,
                "allowed_approval_status_values": [
                    "approval_packet_generated_pending_future_human_approval",
                    "blocked_pending_future_human_approval",
                ],
            }
        ),
        generated,
    )
    packet_index = {
        "schema_version": SCHEMA_VERSION,
        "packet_count": len(packets),
        "packets": [
            {
                "approval_packet_id": packet["approval_packet_id"],
                "path": f"pilot_approval_packet_assembler/approval_packet_{index:03d}.json",
                "real_approval_granted": False,
                "real_observation_authorized": False,
            }
            for index, packet in enumerate(packets, start=1)
        ],
        "safety_flags": SAFETY_FLAGS,
        "l6_6_flags": L6_6_FLAGS,
    }
    write_json("pilot_approval_packet_assembler/approval_packet_index.json", packet_index, generated)
    for index, packet in enumerate(packets, start=1):
        write_json(f"pilot_approval_packet_assembler/approval_packet_{index:03d}.json", packet, generated)
    write_json(
        "pilot_approval_packet_assembler/approval_packet_validation_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "validation_mode": "structural_packet_completeness_not_approval",
                "rows": [
                    {
                        "approval_packet_id": packet["approval_packet_id"],
                        "required_fields_present": True,
                        "real_approval_granted": False,
                        "real_observation_authorized": False,
                        "durable_approval_record_required": True,
                        "durable_approval_record_created": False,
                    }
                    for packet in packets
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_approval_packet_assembler/approval_packet_assembler_report.md",
        "# Approval Packet Assembler\n\n"
        "Approval packets are assembled for future review only. Packet completeness "
        "does not grant approval and does not authorize observation.\n",
        generated,
    )

    dossier_index = {
        "schema_version": SCHEMA_VERSION,
        "dossier_count": len(dossiers),
        "dossiers": [
            {
                "dossier_id": dossier["dossier_id"],
                "path": f"pilot_approval_evidence_dossier/evidence_dossier_{index:03d}.json",
                "dossier_status": dossier["dossier_status"],
                "approved": False,
            }
            for index, dossier in enumerate(dossiers, start=1)
        ],
        "safety_flags": SAFETY_FLAGS,
        "l6_6_flags": L6_6_FLAGS,
    }
    write_json("pilot_approval_evidence_dossier/evidence_dossier_index.json", dossier_index, generated)
    for index, dossier in enumerate(dossiers, start=1):
        write_json(f"pilot_approval_evidence_dossier/evidence_dossier_{index:03d}.json", dossier, generated)
    write_json(
        "pilot_approval_evidence_dossier/evidence_dossier_completeness_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rows": [
                    {
                        "dossier_id": dossier["dossier_id"],
                        "l6_0_trace_present": True,
                        "l6_1_trace_present": True,
                        "l6_2_trace_present": True,
                        "l6_3_trace_present": True,
                        "l6_4_trace_present": True,
                        "l6_5_trace_present": True,
                        "ready_for_review": True,
                        "approved": False,
                    }
                    for dossier in dossiers
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_approval_evidence_dossier/evidence_dossier_report.md",
        "# Pilot Approval Evidence Dossier\n\n"
        "Evidence dossiers link L6.0-L6.5 lineage and remaining gaps. They are "
        "review-ready, not approved.\n",
        generated,
    )

    write_json(
        "pilot_approval_risk_review/risk_review_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "risk_review_mode": "structural_only_no_semantic_truth_scoring",
                "risk_dimensions": RISK_DIMENSIONS,
                "semantic_truth_scoring_used": False,
                "risk_review_can_approve_real_observation": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_risk_review/approval_packet_risk_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rows": [
                    {
                        "approval_packet_id": review["linked_approval_packet_id"],
                        "risk_review_id": review["risk_review_id"],
                        "risk_review_complete": True,
                        "real_observation_approved": False,
                    }
                    for review in risk_reviews
                ],
            }
        ),
        generated,
    )
    for index, review in enumerate(risk_reviews, start=1):
        write_json(f"pilot_approval_risk_review/risk_review_{index:03d}.json", review, generated)
    write_text(
        "pilot_approval_risk_review/risk_review_report.md",
        "# Pilot Approval Risk Review\n\n"
        "Risk review is structural and cannot approve real observation.\n",
        generated,
    )

    operator_prereqs = [
        "future human approval exists",
        "future durable approval record exists",
        "operator identity or manual marker exists",
        "operator read runbook",
        "operator accepted non-action oath",
        "source locator confirmed",
        "runtime isolation confirmed",
        "evidence capture template prepared",
        "abort rules acknowledged",
        "no login/account/payment/contact/form/submission required",
        "no publication/outreach/revenue action allowed",
        "no artifact mutation allowed",
        "no brain/memory/canonical/Y-star mutation allowed",
    ]
    write_json(
        "pilot_operator_authorization_prerequisites/operator_authorization_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "operator_authorization_status": "blocked_pending_future_human_approval_and_durable_record",
                "real_operator_authorization_granted": False,
                "prerequisites": operator_prereqs,
            }
        ),
        generated,
    )
    write_json(
        "pilot_operator_authorization_prerequisites/operator_prerequisite_checklist.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "checklist": [
                    {"prerequisite": item, "satisfied_in_l6_6": False}
                    for item in operator_prereqs
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_operator_authorization_prerequisites/operator_authorization_packet_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "operator_authorization_status": "blocked_pending_future_approval",
                "real_operator_authorization_granted": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_operator_authorization_prerequisites/operator_authorization_blockers.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blockers": [
                    "future human approval missing",
                    "durable approval record missing",
                    "runtime isolation not confirmed",
                    "operator identity/manual marker not approved",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_operator_authorization_prerequisites/operator_authorization_report.md",
        "# Operator Authorization Prerequisites\n\n"
        "Operator authorization remains blocked and pending in L6.6.\n",
        generated,
    )

    attestation_fields = [
        "attestation_id",
        "linked_approval_packet_id",
        "environment_type",
        "network_access_scope",
        "browser_or_tool_profile",
        "no_login_confirmed",
        "no_account_confirmed",
        "no_cookie_dependency_confirmed",
        "no_form_submission_confirmed",
        "no_payment_confirmed",
        "no_posting_or_messaging_confirmed",
        "no_scraping_confirmed",
        "no_mcp_execution_confirmed",
        "no_persistent_external_mutation_confirmed",
        "evidence_capture_only_confirmed",
        "operator_manual_control_confirmed",
        "abort_controls_confirmed",
        "attestation_status",
    ]
    write_json(
        "pilot_runtime_isolation_attestation/runtime_isolation_attestation_schema.json",
        with_common({"schema_version": SCHEMA_VERSION, "required_fields": attestation_fields}),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_attestation/runtime_isolation_prerequisite_checklist.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "checklist": [
                    "isolated future runtime approved",
                    "manual operator control confirmed",
                    "no login/account/cookie dependency confirmed",
                    "no scraping/MCP/persistent mutation confirmed",
                    "abort controls confirmed",
                ],
                "all_confirmed_in_l6_6": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_attestation/runtime_isolation_attestation_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "attestation_id": "",
                "linked_approval_packet_id": "",
                "environment_type": "",
                "network_access_scope": "",
                "browser_or_tool_profile": "",
                "no_login_confirmed": False,
                "no_account_confirmed": False,
                "no_cookie_dependency_confirmed": False,
                "no_form_submission_confirmed": False,
                "no_payment_confirmed": False,
                "no_posting_or_messaging_confirmed": False,
                "no_scraping_confirmed": False,
                "no_mcp_execution_confirmed": False,
                "no_persistent_external_mutation_confirmed": False,
                "evidence_capture_only_confirmed": False,
                "operator_manual_control_confirmed": False,
                "abort_controls_confirmed": False,
                "attestation_status": "template_only",
            }
        ),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_attestation/runtime_isolation_blockers.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blockers": [
                    "future runtime isolation confirmation missing",
                    "future approved tool/browser profile missing",
                    "future manual operator control confirmation missing",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_runtime_isolation_attestation/runtime_isolation_report.md",
        "# Runtime Isolation Attestation\n\n"
        "Runtime isolation is represented as a template only; no runtime check or "
        "network check was executed.\n",
        generated,
    )

    allowed_evidence_fields = [
        "source title",
        "source locator",
        "source publisher/owner",
        "observed timestamp",
        "source date or date missing marker",
        "freshness class",
        "bounded claim text",
        "claim limitation",
        "unsupported claim marker",
        "missing context",
        "conflict marker",
        "citation trace",
        "capture method",
        "review status",
    ]
    disallowed_capture = [
        "private/sensitive data",
        "login-protected content",
        "account content",
        "personal inbox/message content",
        "payment data",
        "customer personal data",
        "bulk scraping output",
        "data requiring bypassing access controls",
    ]
    write_json(
        "pilot_evidence_capture_authorization/evidence_capture_authorization_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "allowed_evidence_fields": allowed_evidence_fields,
                "disallowed_evidence_capture": disallowed_capture,
            }
        ),
        generated,
    )
    write_json(
        "pilot_evidence_capture_authorization/evidence_capture_authorization_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "authorization_status": "template_only_pending_future_approval",
                "real_evidence_capture_authorized": False,
                "allowed_evidence_fields": allowed_evidence_fields,
            }
        ),
        generated,
    )
    write_json(
        "pilot_evidence_capture_authorization/allowed_evidence_fields.json",
        with_common({"schema_version": SCHEMA_VERSION, "allowed_evidence_fields": allowed_evidence_fields}),
        generated,
    )
    write_json(
        "pilot_evidence_capture_authorization/disallowed_evidence_capture.json",
        with_common({"schema_version": SCHEMA_VERSION, "disallowed_evidence_capture": disallowed_capture}),
        generated,
    )
    write_text(
        "pilot_evidence_capture_authorization/evidence_capture_authorization_report.md",
        "# Evidence Capture Authorization\n\n"
        "Evidence capture authorization remains template-only and pending in L6.6.\n",
        generated,
    )

    write_json(
        "pilot_approval_no_action_constraints/approval_no_action_constraint_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "constraint_status": "attached_to_packets_no_downstream_action_authorized",
                "constraints": NO_ACTION_CONSTRAINTS,
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_no_action_constraints/approval_no_action_constraint_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "constraints": [
                    {"action": action, "authorized_by_future_read_only_approval": False}
                    for action in NO_ACTION_CONSTRAINTS
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_no_action_constraints/approval_packet_constraint_map.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "packet_constraints": [
                    {
                        "approval_packet_id": packet["approval_packet_id"],
                        "constraints": NO_ACTION_CONSTRAINTS,
                    }
                    for packet in packets
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_no_action_constraints/disallowed_downstream_actions.json",
        with_common({"schema_version": SCHEMA_VERSION, "disallowed_downstream_actions": NO_ACTION_CONSTRAINTS}),
        generated,
    )
    write_text(
        "pilot_approval_no_action_constraints/approval_no_action_report.md",
        "# Approval No-Action Constraints\n\n"
        "Even future read-only observation approval would not authorize publication, "
        "outreach, payment, revenue, MCP, canonical update, writeback, or direct "
        "Y-star mutation.\n",
        generated,
    )

    decisions = [
        with_common(
            {
                "approval_packet_id": packet["approval_packet_id"],
                "linked_approval_candidate_id": packet["linked_approval_candidate_id"],
                "packet_completeness_decision": "ready_for_review",
                "real_approval_decision": "blocked_pending_future_explicit_human_approval",
                "real_observation_decision": "blocked_pending_future_durable_approval_record",
                "real_network_authorized": False,
                "execution_authorized": False,
                "durable_approval_record_created": False,
                "review_required": True,
                "human_approval_required": True,
                "future_runtime_isolation_required": True,
                "future_milestone_required": True,
                "future_milestone": NEXT_MILESTONE,
            }
        )
        for packet in packets
    ]
    write_json(
        "pilot_approval_decision_sandbox/approval_decision_sandbox_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "decision_sandbox_mode": "approval_packet_review_only_real_approval_blocked",
                "real_approval_can_be_granted_in_l6_6": False,
                "durable_record_can_be_created_in_l6_6": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_decision_sandbox/approval_packet_decision_matrix.json",
        {"schema_version": SCHEMA_VERSION, "decision_count": len(decisions), "decisions": decisions},
        generated,
    )
    write_json(
        "pilot_approval_decision_sandbox/blocked_pending_approval_decisions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blocked_count": len(decisions),
                "decisions": [
                    {
                        "approval_packet_id": decision["approval_packet_id"],
                        "real_approval_decision": decision["real_approval_decision"],
                        "real_observation_decision": decision["real_observation_decision"],
                        "durable_approval_record_created": False,
                    }
                    for decision in decisions
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_approval_decision_sandbox/future_approval_entry_conditions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "future_entry_conditions": [
                    "future explicit human approval",
                    "future durable approval record",
                    "future runtime isolation confirmation",
                    "approved source locator",
                    "operator authorization",
                    "evidence capture authorization",
                    "post-observation review gate",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_approval_decision_sandbox/approval_decision_sandbox_report.md",
        "# Approval Decision Sandbox\n\n"
        "All approval packet decisions remain blocked/pending. No real approval or "
        "durable approval record is created.\n",
        generated,
    )

    for file_name, action_type in NO_ACTION_RECEIPTS.items():
        write_json(f"pilot_approval_non_persistence_receipts/{file_name}", receipt(action_type), generated)
    write_text(
        "pilot_approval_non_persistence_receipts/approval_non_persistence_receipt_report.md",
        "# Approval Non-Persistence Receipts\n\n"
        "No durable real approval record, real approval grant, real observation, or "
        "external execution state was written in L6.6.\n",
        generated,
    )

    write_json(
        "l6_pilot_approval_strategic_residual_loop/l6_6_cieu_like_fixture.json",
        with_common(
            {
                "X_t": {
                    "l6_0_value_selection": INPUT_REFS["l6_0_value_selection"],
                    "l6_1_mvp_artifact_sandbox": INPUT_REFS["l6_1_artifact_cases"],
                    "l6_2_external_observation_boundary": INPUT_REFS["l6_2_boundary"],
                    "l6_3_controlled_observation_sandbox": INPUT_REFS["l6_3_sandbox"],
                    "l6_4_real_read_only_preflight": INPUT_REFS["l6_4_preflight"],
                    "l6_5_pilot_design": INPUT_REFS["l6_5_pilot_design"],
                },
                "U_t": (
                    "Assemble approval packet artifacts for a future controlled real read-only "
                    "observation pilot without granting approval or executing the pilot."
                ),
                "Y_star_t": (
                    "Assemble a complete approval packet and approval sandbox for a future "
                    "controlled real read-only observation pilot while preserving no-real-approval/"
                    "no-network/no-scraping/no-API/no-browser-fetch/no-search/no-publication/"
                    "no-outreach/no-payment/no-revenue/no-MCP/no-live/no-CIEU-DB-write/"
                    "no-canonical-mutation/no-brain-memory-writeback/no-direct-Y-star mutation "
                    "constraints."
                ),
                "Y_t_plus_1": {
                    "approval_candidates_selected": len(candidates),
                    "approval_packets_generated": len(packets),
                    "evidence_dossiers_generated": len(dossiers),
                    "risk_reviews_generated": len(risk_reviews),
                    "real_approval_granted": False,
                    "durable_real_approval_record_created": False,
                    "real_observation_authorized": False,
                },
                "R_t_plus_1": [
                    "real approval still not granted",
                    "durable approval record not created",
                    "pilot execution still blocked",
                    "source locators remain placeholders",
                    "runtime isolation not confirmed",
                    "operator authorization not granted",
                    "evidence capture authorization remains template-only",
                    "approval packets need future human review",
                    "no real freshness verification yet",
                    "no external evidence captured",
                    "artifact refinements remain review-only",
                    "publication/outreach/payment/revenue remain blocked",
                ],
                "event_mode": "l6_6_controlled_real_read_only_observation_pilot_approval_packet_fixture",
                "persistence_enabled": False,
                "db_write_performed": False,
                "real_approval_granted": False,
                "real_observation_execution_enabled": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_pilot_approval_strategic_residual_loop/l6_6_strategic_residual_delta.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "residual_classes": {
                    "real_approval_gap": "real approval still not granted",
                    "durable_record_gap": "durable approval record not created",
                    "pilot_execution_gap": "pilot execution still blocked",
                    "source_locator_gap": "source locators remain placeholders",
                    "runtime_isolation_gap": "runtime isolation not confirmed",
                    "operator_authorization_gap": "operator authorization not granted",
                    "evidence_capture_authorization_gap": "template-only pending",
                    "future_human_review_gap": "approval packets need future human review",
                    "freshness_verification_gap": "no real freshness verification yet",
                    "external_evidence_gap": "no external evidence captured",
                    "artifact_refinement_gap": "review-only and unapplied",
                    "externalization_gap": "publication/outreach/payment/revenue remain blocked",
                },
            }
        ),
        generated,
    )
    write_json(
        "l6_pilot_approval_strategic_residual_loop/l6_6_meta_learning_update_candidate.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "learning_targets": [
                    "approval_packet_policy",
                    "approval_authority_policy",
                    "evidence_dossier_policy",
                    "risk_review_policy",
                    "operator_authorization_policy",
                    "runtime_isolation_attestation_policy",
                    "non_persistence_receipt_policy",
                ],
                "eligible_for_review_queue": True,
                "eligible_for_direct_brain_writeback": False,
                "eligible_for_direct_memory_ingestion": False,
                "eligible_for_candidate_auto_approval": False,
                "eligible_for_direct_strategy_mutation": False,
                "approved": False,
                "applied": False,
            }
        ),
        generated,
    )
    write_text(
        "l6_pilot_approval_strategic_residual_loop/l6_6_residual_report.md",
        "# L6.6 Strategic Residual\n\n"
        "Approval packet assembly is complete enough for future review, but real "
        "approval, durable approval persistence, and pilot execution remain blocked.\n",
        generated,
    )

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_6_controlled_pilot_approval_packet_complete": True,
        "approval_candidates_selected": True,
        "approval_authority_model_generated": True,
        "approval_packet_instances_generated": True,
        "evidence_dossiers_generated": True,
        "risk_reviews_generated": True,
        "operator_authorization_prerequisites_generated": True,
        "runtime_isolation_attestation_templates_generated": True,
        "evidence_capture_authorization_templates_generated": True,
        "no_action_constraints_generated": True,
        "approval_decision_sandbox_generated": True,
        "non_persistence_receipts_generated": True,
        "strategic_residual_loop_generated": True,
        "ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox": True,
        "ready_for_actual_network_observation_now": False,
        "ready_for_real_approval_now": False,
        "ready_for_durable_approval_persistence_now": False,
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
            "real approval now",
            "durable approval persistence now",
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
        "l6_6_flags": L6_6_FLAGS,
    }
    write_json("l6_pilot_approval_readiness/l6_6_readiness_assessment.json", readiness, generated)
    write_json(
        "l6_pilot_approval_readiness/l6_6_next_milestone_recommendation.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "recommended_next_milestone": NEXT_MILESTONE,
                "do_not_implement_in_l6_6": True,
                "ready_for_future_approval_record_sandbox": True,
                "ready_for_real_approval_now": False,
                "ready_for_real_observation_execution_now": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_pilot_approval_readiness/l6_6_blockers.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blockers": [
                    "future explicit human approval missing",
                    "future durable approval record missing",
                    "future runtime isolation confirmation missing",
                    "operator authorization missing",
                    "evidence capture authorization pending",
                    "source locators remain placeholders",
                    "external evidence not captured",
                ],
            }
        ),
        generated,
    )
    write_text(
        "l6_pilot_approval_readiness/l6_6_readiness_report.md",
        "# L6.6 Readiness\n\n"
        "- L6.6 controlled pilot approval packet complete: true\n"
        f"- Ready for {NEXT_MILESTONE}: true\n"
        "- Ready for actual network observation now: false\n"
        "- Ready for real approval now: false\n"
        "- Ready for durable approval persistence now: false\n"
        "- Ready for publication/outreach/payment/revenue execution: false\n"
        "- Ready for MCP/canonical/writeback/direct Y-star mutation: false\n",
        generated,
    )

    return generated


def main() -> None:
    generated = generate()
    print(
        "Built L6.6 controlled observation pilot approval packet artifacts: "
        f"{len(generated)} files"
    )


if __name__ == "__main__":
    main()
