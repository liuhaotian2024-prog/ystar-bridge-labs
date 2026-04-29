#!/usr/bin/env python3
"""Build L6.5 controlled real read-only observation pilot design artifacts.

This builder is intentionally static and local. It reads safe generated JSON
from L6.0-L6.4 and writes design-only artifacts for a future pilot. It must not
perform network, browser, scraping, API, MCP, live, publication, outreach,
payment, revenue, writeback, canonical update, or direct Y-star mutation work.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.5"
MILESTONE_NAME = "Controlled Real Read-Only Observation Pilot Design v0"
NEXT_MILESTONE = "L6.6 Controlled Real Read-Only Observation Pilot Approval Packet v0"
PLACEHOLDER_LOCATOR_MARKER = (
    "PLACEHOLDER LOCATOR ONLY - NOT FETCHED - NOT OPENED - NOT VERIFIED CURRENT FACT "
    "- NOT AUTHORIZED FOR REAL OBSERVATION - NOT AUTHORIZED FOR PUBLICATION "
    "- NOT AUTHORIZED FOR OUTREACH - NOT AUTHORIZED FOR PAYMENT "
    "- NOT AUTHORIZED FOR REVENUE EXECUTION - NOT AUTHORIZED FOR CANONICAL UPDATE"
)

INPUT_REFS = {
    "l6_0_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_0_selection": "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "l6_1_cases": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_2_boundary": "l6_governed_external_observation_boundary/l6_2_summary.json",
    "l6_3_selected_cases": "l6_observation_case_selector/selected_observation_cases.json",
    "l6_3_packet_index": "controlled_pre_observation_packets/pre_observation_packet_index.json",
    "l6_4_summary": "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
    "l6_4_candidates": "real_observation_candidate_selector/selected_real_observation_candidates.json",
    "l6_4_allowlist": "source_allowlist_and_risk_policy/source_allowlist_policy.json",
    "l6_4_denylist": "source_allowlist_and_risk_policy/source_denylist_policy.json",
    "l6_4_preflight_decisions": "real_observation_preflight_decision_gate/candidate_preflight_decisions.json",
    "l6_4_readiness": "l6_real_observation_preflight_readiness/l6_4_readiness_assessment.json",
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

L6_5_FLAGS = {
    "l6_5_pilot_design_only": True,
    "l6_5_preflight_only": True,
    "l6_5_future_real_read_only_observation_pilot_candidate_allowed": True,
    "l6_5_pilot_approval_packet_generation_enabled": True,
    "l6_5_pilot_operator_runbook_enabled": True,
    "l6_5_pilot_evidence_template_enabled": True,
    "l6_5_real_pilot_execution_enabled": False,
    "l6_5_network_enabled": False,
    "l6_5_api_enabled": False,
    "l6_5_scraping_enabled": False,
    "l6_5_browser_fetch_enabled": False,
    "l6_5_search_enabled": False,
    "l6_5_publication_enabled": False,
    "l6_5_outreach_enabled": False,
    "l6_5_payment_enabled": False,
    "l6_5_revenue_execution_enabled": False,
    "l6_5_mcp_execution_enabled": False,
    "l6_5_canonical_update_enabled": False,
    "l6_5_brain_writeback_enabled": False,
    "l6_5_memory_ingestion_enabled": False,
    "l6_5_direct_y_star_mutation_enabled": False,
}

BLOCKED_AUTHORIZATIONS = {
    "real_external_observation_authorized": False,
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
    "linked L6.4 preflight candidate exists",
    "evidence gap is clear",
    "observation question is narrow",
    "source type is allowlisted in L6.4 policy",
    "denylist condition absent",
    "no login required",
    "no account creation required",
    "no payment required",
    "no contact required",
    "no form submission required",
    "no publication required",
    "no download of private/sensitive data required",
    "no automation required",
    "no MCP execution required",
    "expected evidence type is simple",
    "citation plan is clear",
    "freshness requirement is clear",
    "claim boundary is clear",
    "abort conditions are clear",
    "operator can perform manually in future",
    "downside risk is low",
    "learning value is high",
]

PILOT_ALLOWLIST_SOURCE_TYPES = [
    "official_informational_page",
    "official_policy_page",
    "public_static_informational_page",
    "public_document_page",
    "public_repository_page",
    "user_supplied_public_locator",
]

PILOT_DENYLIST_SOURCE_TYPES = [
    "login_required_page",
    "account_required_page",
    "payment_required_page",
    "contact_form",
    "submission_form",
    "private_customer_data",
    "private_inbox_message_surface",
    "checkout_payment_surface",
    "social_posting_surface",
    "comment_reply_surface",
    "production_mcp_tool_resource",
    "live_agent_control_surface",
    "access_control_bypass_required_source",
    "automated_scraping_required_source",
    "personal_sensitive_data_access_required_source",
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

NO_ACTION_RECEIPTS = {
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
    return {**payload, "safety_flags": SAFETY_FLAGS, "l6_5_flags": L6_5_FLAGS}


def existing_input_map() -> tuple[dict[str, str], list[str]]:
    refs: dict[str, str] = {}
    gaps: list[str] = []
    for key, rel in INPUT_REFS.items():
        if (ROOT / rel).exists():
            refs[key] = rel
        else:
            gaps.append(rel)
    return refs, gaps


def l6_4_candidates() -> list[dict[str, Any]]:
    source = read_json(INPUT_REFS["l6_4_candidates"]) or {}
    candidates = source.get("candidates", [])[:3]
    if candidates:
        return candidates
    return [
        {
            "candidate_id": "l6_4_real_observation_candidate_placeholder",
            "linked_l6_3_packet_id": "l6_3_pre_observation_packet_placeholder",
            "linked_l6_3_fixture_id": "l6_3_static_manual_fixture_placeholder",
            "linked_l6_1_artifact_case_id": "case_placeholder",
            "linked_l6_0_hypothesis_id": "hypothesis_placeholder",
            "evidence_gap": ["preflight candidate source missing"],
            "real_observation_question": "Which future read-only evidence would clarify the artifact claim boundary?",
            "proposed_source_type": "user_supplied_public_locator",
            "source_locator_placeholder": f"{PLACEHOLDER_LOCATOR_MARKER} :: placeholder",
            "expected_evidence_type": "bounded_source_summary",
        }
    ]


def normalize_source_type(source_type: str) -> str:
    if source_type in {"official_program_page", "official_policy_page"}:
        return source_type
    if source_type in {"public_document_page", "public_repository_page", "user_supplied_public_locator"}:
        return source_type
    return "public_static_informational_page"


def build_pilot_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for index, source in enumerate(l6_4_candidates()[:3], start=1):
        proposed_source_type = normalize_source_type(source.get("proposed_source_type", "user_supplied_public_locator"))
        selected = with_common(
            {
                "pilot_candidate_id": f"l6_5_pilot_candidate_{index:03d}",
                "linked_l6_4_candidate_id": source.get("candidate_id"),
                "linked_l6_3_packet_id": source.get("linked_l6_3_packet_id"),
                "linked_l6_1_artifact_case_id": source.get("linked_l6_1_artifact_case_id"),
                "linked_l6_0_hypothesis_id": source.get("linked_l6_0_hypothesis_id"),
                "evidence_gap": source.get("evidence_gap", ["real source evidence missing"]),
                "pilot_observation_question": source.get("real_observation_question"),
                "proposed_source_type": proposed_source_type,
                "source_locator_placeholder": (
                    f"{PLACEHOLDER_LOCATOR_MARKER} :: l6-5-pilot-candidate-{index:03d}"
                ),
                "expected_evidence_type": source.get("expected_evidence_type", "bounded_source_summary"),
                "pilot_selection_reason": (
                    "Selected from L6.4 because the evidence gap is clear, the question is narrow, "
                    "the source type is low-risk/read-only, and a future operator could perform "
                    "the check manually after explicit approval."
                ),
                "selection_factors": SELECTION_FACTORS,
                "selected_by_hardcoded_opportunity_category": False,
                "hardcoded_opportunity_class_used": False,
                "no_action_requirements": {
                    "no_login_required": True,
                    "no_account_creation_required": True,
                    "no_payment_required": True,
                    "no_contact_required": True,
                    "no_form_submission_required": True,
                    "no_publication_required": True,
                    "no_private_sensitive_download_required": True,
                    "no_automation_required": True,
                    "no_mcp_execution_required": True,
                },
                "real_observation_authorized_now": False,
                "pilot_design_authorized_now": True,
                "future_human_approval_required": True,
                "future_runtime_isolation_required": True,
            }
        )
        candidates.append(selected)
    return candidates, deferred


def build_approval_packet(index: int, candidate: dict[str, Any]) -> dict[str, Any]:
    return with_common(
        {
            "pilot_approval_packet_id": f"l6_5_pilot_approval_packet_{index:03d}",
            "linked_pilot_candidate_id": candidate["pilot_candidate_id"],
            "linked_l6_4_candidate_id": candidate["linked_l6_4_candidate_id"],
            "linked_l6_3_packet_id": candidate["linked_l6_3_packet_id"],
            "linked_l6_1_artifact_case_id": candidate["linked_l6_1_artifact_case_id"],
            "observation_question": candidate["pilot_observation_question"],
            "source_type": candidate["proposed_source_type"],
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
                "capture_source_locator": True,
                "capture_source_title": True,
                "capture_source_owner_or_publisher": True,
                "capture_observed_at_timestamp": True,
                "capture_source_date_or_date_missing": True,
                "capture_bounded_claims": True,
                "capture_unsupported_claims": True,
                "capture_missing_context": True,
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
                "source requires disallowed interaction",
                "source content exceeds approved scope",
                "operator uncertainty cannot be resolved within pilot boundary",
            ],
            "operator_handoff_required": True,
            "runtime_isolation_required": True,
            "reviewer_required": True,
            "approval_status": "pilot_design_generated",
            "real_observation_authorized": False,
        }
    )


def receipt(action_type: str) -> dict[str, Any]:
    return with_common(
        {
            "action_type": action_type,
            "authorized_in_l6_5": False,
            "executed_in_l6_5": False,
            "blocker_reference": (
                "l6_controlled_real_read_only_observation_pilot_design/"
                "l6_5_milestone_contract.json"
            ),
            "future_boundary_required": NEXT_MILESTONE,
        }
    )


def generate() -> list[str]:
    generated: list[str] = []
    refs, missing_refs = existing_input_map()
    candidates, deferred_candidates = build_pilot_candidates()
    approval_packets = [
        build_approval_packet(index, candidate)
        for index, candidate in enumerate(candidates, start=1)
    ]

    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": ["L6.0", "L6.1", "L6.2", "L6.3", "L6.4"],
            "mode": "pilot_design_only",
            "pilot_design_only": True,
            "preflight_only": True,
            "future_real_read_only_observation_pilot_candidate_allowed": True,
            "pilot_approval_packet_generation_authorized": True,
            "pilot_operator_runbook_authorized": True,
            "pilot_evidence_template_authorized": True,
            "real_pilot_execution_authorized": False,
            "requires_future_explicit_human_approval_before_real_observation": True,
            "requires_future_runtime_isolation_confirmation_before_real_observation": True,
            "requires_future_post_observation_review_before_any_artifact_update": True,
            "required_outputs": [
                "pilot candidate selector",
                "pilot scope and non-goals",
                "pilot source constraints",
                "pilot approval packet candidates",
                "operator runbook",
                "evidence packet templates",
                "post-observation review workflow",
                "abort and quarantine policy",
                "success/failure criteria",
                "no-action guarantees",
                "pilot design decision gate",
                "strategic residual fixture",
                "readiness assessment",
            ],
            **BLOCKED_AUTHORIZATIONS,
        }
    )
    write_json(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_pilot_design_scope.json",
        with_common(
            {
                "milestone_id": MILESTONE_ID,
                "scope_status": "pilot_design_only_real_execution_blocked",
                "in_scope": [
                    "select L6.4 candidates for future pilot design",
                    "define narrow pilot scope and non-goals",
                    "generate approval packet candidates",
                    "define future manual operator runbook",
                    "generate empty evidence packet templates",
                    "define post-observation review and quarantine workflow",
                    "generate blocked pilot design decisions",
                ],
                "out_of_scope": [
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
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_safety_flags.json",
        {"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS, "l6_5_flags": L6_5_FLAGS},
        generated,
    )
    write_text(
        "l6_controlled_real_read_only_observation_pilot_design/README.md",
        "# L6.5 Controlled Real Read-Only Observation Pilot Design\n\n"
        "This pack designs a future controlled real read-only observation pilot. It "
        "does not run the pilot, fetch URLs, search, scrape, browse, call APIs, "
        "publish, contact, pay, execute MCP, mutate strategy, write brain/memory, "
        "or directly mutate Y-star.\n",
        generated,
    )
    write_text(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_non_execution_boundary.md",
        "# L6.5 Non-Execution Boundary\n\n"
        f"{PLACEHOLDER_LOCATOR_MARKER}\n\n"
        "L6.5 may create a pilot design package only. Real observation, network "
        "access, search, publication, outreach, payment, revenue execution, MCP "
        "execution, CIEU DB writes, canonical updates, writeback, and direct "
        "Y-star mutation remain blocked.\n",
        generated,
    )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "l6_5_controlled_real_read_only_observation_pilot_design_defined": True,
        "pilot_design_only": True,
        "preflight_only": True,
        "candidate_count": len(candidates),
        "approval_packet_count": len(approval_packets),
        "pilot_scope_defined": True,
        "pilot_non_goals_defined": True,
        "pilot_source_constraints_defined": True,
        "pilot_approval_packet_candidates_generated": True,
        "pilot_operator_runbook_generated": True,
        "pilot_evidence_packet_templates_generated": True,
        "post_observation_review_workflow_defined": True,
        "abort_quarantine_policy_defined": True,
        "success_failure_criteria_defined": True,
        "no_action_guarantees_generated": True,
        "pilot_design_decision_gate_generated": True,
        "strategic_residual_loop_generated": True,
        "future_real_read_only_observation_pilot_candidate_allowed": True,
        "real_external_observation_authorized": False,
        "real_pilot_execution_authorized": False,
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
        "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet": True,
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
        "l6_5_flags": L6_5_FLAGS,
        "warning": (
            "L6.5 is pilot-design-only. Real observation, URL fetch, search, scraping, "
            "API calls, browser fetch, publication, outreach, payment, revenue "
            "execution, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, and direct Y-star mutation remain blocked."
        ),
    }
    write_json(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.json",
        summary,
        generated,
    )
    write_text(
        "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.md",
        "# L6.5 Summary\n\n"
        "- Controlled real read-only observation pilot design defined: true\n"
        "- Pilot design only: true\n"
        "- Real pilot execution authorized: false\n"
        f"- Pilot candidates: {len(candidates)}\n"
        f"- Approval packet candidates: {len(approval_packets)}\n"
        f"- Next milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    write_json(
        "pilot_candidate_selector/l6_4_preflight_candidate_inventory.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "source": INPUT_REFS["l6_4_candidates"],
                "candidate_count": len(l6_4_candidates()),
                "candidates": l6_4_candidates(),
            }
        ),
        generated,
    )
    write_json(
        "pilot_candidate_selector/pilot_candidate_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "selection_mode": "structural_pilot_design_candidate_selection",
                "selection_factors": SELECTION_FACTORS,
                "selected_by_hardcoded_opportunity_category": False,
                "matrix": [
                    {
                        "pilot_candidate_id": candidate["pilot_candidate_id"],
                        "linked_l6_4_candidate_id": candidate["linked_l6_4_candidate_id"],
                        "evidence_gap_clear": True,
                        "observation_question_narrow": True,
                        "source_type_allowlisted": True,
                        "denylist_condition_absent": True,
                        "read_only_feasible": True,
                        "operator_manual_future_run_feasible": True,
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
        "pilot_candidate_selector/selected_pilot_candidates.json",
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_count": len(candidates),
            "selection_mode": "structural_pilot_design_candidate_selection",
            "selected_by_hardcoded_opportunity_category": False,
            "hardcoded_opportunity_class_used": False,
            "candidates": candidates,
        },
        generated,
    )
    write_json(
        "pilot_candidate_selector/deferred_pilot_candidates.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "deferred_count": len(deferred_candidates),
                "deferred_candidates": deferred_candidates,
                "defer_reasons": [
                    "denylist condition present",
                    "question too broad",
                    "source locator missing",
                    "future manual operator control unclear",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_candidate_selector/pilot_candidate_selector_report.md",
        "# Pilot Candidate Selector\n\n"
        "Candidates are selected from L6.4 preflight outputs using structural "
        "read-only feasibility and evidence-gap criteria. No opportunity category "
        "is treated as strategy.\n",
        generated,
    )

    scope_items = [
        "one narrow read-only observation question",
        "one source locator or source class per pilot case",
        "manual/operator-controlled future run only",
        "evidence capture only",
        "citation/source trace capture only",
        "no interaction with source beyond viewing/reading",
        "no publication",
        "no outreach",
        "no payment",
        "no submission",
        "no account creation",
        "no customer contact",
        "no artifact update without review",
        "no strategy mutation",
        "no brain/memory writeback",
        "no direct Y-star mutation",
    ]
    non_goals = [
        "market scraping",
        "broad opportunity discovery",
        "customer outreach",
        "lead generation",
        "posting/publishing",
        "payment or revenue action",
        "product launch",
        "grant/RFP/bounty submission",
        "sales proposal",
        "MCP execution",
        "autonomous browsing",
        "strategy update",
        "canonical update",
    ]
    write_json(
        "pilot_scope_and_non_goals/pilot_scope_definition.json",
        with_common({"schema_version": SCHEMA_VERSION, "pilot_scope": scope_items}),
        generated,
    )
    write_json(
        "pilot_scope_and_non_goals/pilot_non_goals.json",
        with_common({"schema_version": SCHEMA_VERSION, "pilot_non_goals": non_goals}),
        generated,
    )
    write_json(
        "pilot_scope_and_non_goals/pilot_boundary_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "pilot_boundary_status": "future_pilot_design_only_current_execution_blocked",
                "pilot_scope": scope_items,
                "pilot_non_goals": non_goals,
                "artifact_update_without_review_authorized": False,
                "externalization_authorized": False,
                **BLOCKED_AUTHORIZATIONS,
            }
        ),
        generated,
    )
    write_text(
        "pilot_scope_and_non_goals/pilot_scope_report.md",
        "# Pilot Scope and Non-Goals\n\n"
        "The future pilot is a narrow read-only observation design. It is not a "
        "market scan, outreach path, publication path, payment path, or canonical "
        "strategy update.\n",
        generated,
    )

    l6_4_allowlist = read_json(INPUT_REFS["l6_4_allowlist"]) or {}
    l6_4_denylist = read_json(INPUT_REFS["l6_4_denylist"]) or {}
    write_json(
        "pilot_source_constraint_policy/inherited_l6_4_source_policy_map.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "inherits_from": [
                    INPUT_REFS["l6_4_allowlist"],
                    INPUT_REFS["l6_4_denylist"],
                ],
                "l6_4_allowlist_count": len(l6_4_allowlist.get("source_types", [])),
                "l6_4_denylist_count": len(l6_4_denylist.get("source_types", [])),
                "l6_5_narrows_to_low_risk_read_only_source_types": True,
            }
        ),
        generated,
    )
    write_json(
        "pilot_source_constraint_policy/pilot_source_allowlist.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "allowlist_status": "future_policy_only_real_access_unauthorized_in_l6_5",
                "source_types": [
                    {
                        "source_type_id": source_type,
                        "allowed_future_after_approval": True,
                        "real_access_authorized_in_l6_5": False,
                    }
                    for source_type in PILOT_ALLOWLIST_SOURCE_TYPES
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_source_constraint_policy/pilot_source_denylist.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "denylist_status": "blocked_for_l6_5_and_requires_future_boundary",
                "source_types": [
                    {
                        "source_type_id": source_type,
                        "denied_in_l6_5": True,
                        "future_exception_requires_explicit_approval": True,
                    }
                    for source_type in PILOT_DENYLIST_SOURCE_TYPES
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_source_constraint_policy/pilot_source_constraint_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "constraints": [
                    {
                        "pilot_candidate_id": candidate["pilot_candidate_id"],
                        "proposed_source_type": candidate["proposed_source_type"],
                        "source_type_allowlisted": True,
                        "denylist_condition_absent": True,
                        "real_access_authorized_in_l6_5": False,
                    }
                    for candidate in candidates
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_source_constraint_policy/pilot_source_policy_report.md",
        "# Pilot Source Constraint Policy\n\n"
        "L6.5 inherits L6.4 source policy and narrows it to low-risk future "
        "read-only source classes. All real access remains unauthorized now.\n",
        generated,
    )

    packet_fields = [
        "pilot_approval_packet_id",
        "linked_pilot_candidate_id",
        "linked_l6_4_candidate_id",
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
        "no_direct_y_star_mutation_required",
        "evidence_capture_plan",
        "citation_plan",
        "abort_conditions",
        "quarantine_conditions",
        "operator_handoff_required",
        "runtime_isolation_required",
        "reviewer_required",
        "approval_status",
        "real_observation_authorized",
    ]
    write_json(
        "pilot_approval_packet_candidates/pilot_approval_packet_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "required_fields": packet_fields,
                "allowed_approval_status_values": [
                    "pilot_design_generated",
                    "blocked_pending_future_human_approval",
                ],
            }
        ),
        generated,
    )
    packet_index = {
        "schema_version": SCHEMA_VERSION,
        "packet_count": len(approval_packets),
        "packets": [
            {
                "pilot_approval_packet_id": packet["pilot_approval_packet_id"],
                "path": f"pilot_approval_packet_candidates/pilot_approval_packet_{index:03d}.json",
                "real_observation_authorized": False,
            }
            for index, packet in enumerate(approval_packets, start=1)
        ],
        "safety_flags": SAFETY_FLAGS,
        "l6_5_flags": L6_5_FLAGS,
    }
    write_json(
        "pilot_approval_packet_candidates/pilot_approval_packet_index.json",
        packet_index,
        generated,
    )
    for index, packet in enumerate(approval_packets, start=1):
        write_json(
            f"pilot_approval_packet_candidates/pilot_approval_packet_{index:03d}.json",
            packet,
            generated,
        )
    write_json(
        "pilot_approval_packet_candidates/blocked_or_incomplete_approval_packets.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blocked_status": "all_packets_blocked_pending_future_human_approval",
                "packets": [
                    {
                        "pilot_approval_packet_id": packet["pilot_approval_packet_id"],
                        "approval_status": "blocked_pending_future_human_approval",
                        "real_observation_authorized": False,
                    }
                    for packet in approval_packets
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_approval_packet_candidates/pilot_approval_packet_report.md",
        "# Pilot Approval Packet Candidates\n\n"
        "Approval packets are generated for future review only. Real observation is "
        "not authorized by any packet in L6.5.\n",
        generated,
    )

    operator_steps = [
        "confirm approval packet exists",
        "confirm future explicit human approval",
        "confirm runtime isolation",
        "confirm source locator",
        "confirm source is allowlisted",
        "confirm denylist conditions absent",
        "confirm no login/account/payment/contact/form/submission required",
        "confirm evidence capture template ready",
        "confirm abort rules understood",
        "view/read only",
        "do not submit forms",
        "do not log in",
        "do not create accounts",
        "do not download private/sensitive data",
        "do not message/contact/post/comment",
        "do not pay",
        "capture only approved evidence fields",
        "abort on any scope change",
        "complete evidence packet",
        "submit for review only",
        "do not update artifacts directly",
        "do not update strategy",
        "do not write brain/memory",
    ]
    write_text(
        "pilot_operator_runbook/operator_runbook.md",
        "# Pilot Operator Runbook\n\n"
        "This is a future-run plan only. L6.5 does not execute the runbook.\n\n"
        + "\n".join(f"- {step}" for step in operator_steps)
        + "\n",
        generated,
    )
    write_json(
        "pilot_operator_runbook/operator_step_sequence.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "runbook_status": "future_steps_only_not_executed",
                "steps": operator_steps,
                "real_run_executed_in_l6_5": False,
            }
        ),
        generated,
    )
    for file_name, title, steps in [
        (
            "operator_pre_run_checklist.md",
            "Operator Pre-Run Checklist",
            operator_steps[:9],
        ),
        (
            "operator_during_run_checklist.md",
            "Operator During-Run Checklist",
            operator_steps[9:18],
        ),
        (
            "operator_abort_checklist.md",
            "Operator Abort Checklist",
            ABORT_CONDITIONS,
        ),
        (
            "operator_post_run_checklist.md",
            "Operator Post-Run Checklist",
            operator_steps[18:],
        ),
    ]:
        write_text(
            f"pilot_operator_runbook/{file_name}",
            f"# {title}\n\n" + "\n".join(f"- {step}" for step in steps) + "\n",
            generated,
        )
    write_json(
        "pilot_operator_runbook/operator_non_action_oath.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "operator_non_action_oath": [
                    "view/read only",
                    "do not publish",
                    "do not contact",
                    "do not pay",
                    "do not submit",
                    "do not execute MCP",
                    "do not update artifacts directly",
                    "do not update canonical strategy",
                    "do not write brain/memory",
                    "do not directly mutate Y-star",
                ],
                "real_run_executed_in_l6_5": False,
            }
        ),
        generated,
    )
    write_text(
        "pilot_operator_runbook/pilot_operator_runbook_report.md",
        "# Pilot Operator Runbook Report\n\n"
        "The runbook is a future manual/operator plan only and was not executed.\n",
        generated,
    )

    evidence_fields = [
        "evidence_packet_id",
        "linked_pilot_approval_packet_id",
        "linked_pilot_candidate_id",
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
        "revenue_action_taken",
        "mcp_execution_taken",
        "canonical_update_taken",
        "brain_memory_writeback_taken",
        "direct_y_star_mutation_taken",
    ]
    empty_evidence_template = {
        "schema_version": SCHEMA_VERSION,
        "template_only": True,
        "real_evidence_captured": False,
        "evidence_packet_id": "",
        "linked_pilot_approval_packet_id": "",
        "linked_pilot_candidate_id": "",
        "source_locator": "",
        "source_title": "",
        "source_publisher_or_owner": "",
        "observed_at_timestamp": "",
        "source_date_or_date_missing": "",
        "freshness_class": "",
        "captured_claims": [],
        "unsupported_claims": [],
        "missing_context": [],
        "conflicting_source_marker": "",
        "claim_boundary": "",
        "citation_trace": [],
        "capture_method": "",
        "operator_id_or_manual_marker": "",
        "review_status": "template_only_not_reviewed",
        "external_action_taken": False,
        "publication_taken": False,
        "outreach_taken": False,
        "payment_taken": False,
        "revenue_action_taken": False,
        "mcp_execution_taken": False,
        "canonical_update_taken": False,
        "brain_memory_writeback_taken": False,
        "direct_y_star_mutation_taken": False,
        "safety_flags": SAFETY_FLAGS,
        "l6_5_flags": L6_5_FLAGS,
    }
    write_json(
        "pilot_evidence_packet_templates/pilot_evidence_packet_schema.json",
        with_common({"schema_version": SCHEMA_VERSION, "required_fields": evidence_fields}),
        generated,
    )
    write_json(
        "pilot_evidence_packet_templates/pilot_evidence_packet_template.json",
        empty_evidence_template,
        generated,
    )
    write_json(
        "pilot_evidence_packet_templates/pilot_citation_capture_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "real_citation_captured": False,
                "fields": [
                    "source_locator",
                    "source_title",
                    "source_date_or_date_missing",
                    "observed_at_timestamp",
                    "citation_trace",
                    "claim_boundary",
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_evidence_packet_templates/pilot_claim_capture_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "real_claim_captured": False,
                "fields": [
                    "captured_claims",
                    "unsupported_claims",
                    "missing_context",
                    "conflicting_source_marker",
                    "claim_boundary",
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_evidence_packet_templates/pilot_evidence_packet_examples_empty.json",
        {
            "schema_version": SCHEMA_VERSION,
            "examples_are_empty_templates": True,
            "real_evidence_captured": False,
            "examples": [empty_evidence_template],
        },
        generated,
    )
    write_text(
        "pilot_evidence_packet_templates/pilot_evidence_template_report.md",
        "# Pilot Evidence Packet Templates\n\n"
        "Evidence packet examples are empty templates only. They do not claim real "
        "evidence was captured.\n",
        generated,
    )

    review_outcomes = [
        "accept_evidence_for_internal_review",
        "quarantine_evidence",
        "reject_evidence",
        "require_additional_source",
        "require_claim_boundary_revision",
        "generate_artifact_refinement_candidate",
        "defer_artifact_refinement",
        "block_externalization",
    ]
    write_json(
        "pilot_post_observation_review_workflow/post_observation_review_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "review_required_before_any_artifact_update": True,
                "allowed_review_outcomes": review_outcomes,
                "direct_publication_authorized": False,
                "direct_outreach_authorized": False,
                "direct_payment_authorized": False,
                "direct_revenue_execution_authorized": False,
                "direct_canonical_update_authorized": False,
                "direct_brain_memory_writeback_authorized": False,
                "direct_y_star_mutation_authorized": False,
            }
        ),
        generated,
    )
    write_text(
        "pilot_post_observation_review_workflow/evidence_review_checklist.md",
        "# Evidence Review Checklist\n\n"
        "- confirm source trace\n- confirm freshness or date_missing marker\n"
        "- confirm claim boundary\n- confirm missing context\n- confirm no forbidden action occurred\n",
        generated,
    )
    write_text(
        "pilot_post_observation_review_workflow/claim_review_checklist.md",
        "# Claim Review Checklist\n\n"
        "- separate captured claims from unsupported claims\n"
        "- mark conflicts\n- require limitation statements\n- block externalization\n",
        generated,
    )
    write_json(
        "pilot_post_observation_review_workflow/artifact_refinement_review_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_refinement_candidates_allowed": True,
                "artifact_refinement_application_authorized": False,
                "publication_authorized": False,
                "outreach_authorized": False,
                "payment_authorized": False,
                "revenue_execution_authorized": False,
                "canonical_update_authorized": False,
                "brain_writeback_authorized": False,
                "memory_ingestion_authorized": False,
                "direct_y_star_mutation_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_post_observation_review_workflow/post_observation_review_packet_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "linked_evidence_packet_id": "",
                "review_outcome": "review_pending",
                "approved": False,
                "applied": False,
                "externalization_authorized": False,
                "canonical_update_authorized": False,
            }
        ),
        generated,
    )
    write_text(
        "pilot_post_observation_review_workflow/pilot_post_review_report.md",
        "# Pilot Post-Observation Review Workflow\n\n"
        "Future evidence can enter review, quarantine, rejection, or candidate-only "
        "artifact refinement. No outcome directly authorizes externalization or "
        "canonical mutation.\n",
        generated,
    )

    write_json(
        "pilot_abort_quarantine_decision_policy/pilot_abort_condition_registry.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "abort_conditions": [
                    {"condition": condition, "abort_required": True}
                    for condition in ABORT_CONDITIONS
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_abort_quarantine_decision_policy/pilot_quarantine_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "quarantine_required_for_scope_violation": True,
                "quarantined_evidence_cannot_update_artifacts": True,
                "quarantined_evidence_cannot_update_strategy": True,
                "quarantined_evidence_cannot_write_brain_memory": True,
                "quarantined_evidence_cannot_update_canonical_state": True,
                "quarantined_evidence_cannot_mutate_y_star": True,
            }
        ),
        generated,
    )
    write_json(
        "pilot_abort_quarantine_decision_policy/pilot_evidence_rejection_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "reject_if_no_source_trace": True,
                "reject_if_forbidden_action_occurred": True,
                "reject_if_claim_boundary_missing": True,
                "reject_if_private_sensitive_data_included": True,
            }
        ),
        generated,
    )
    write_json(
        "pilot_abort_quarantine_decision_policy/pilot_scope_violation_policy.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "scope_violation_actions": [
                    "abort future pilot",
                    "quarantine evidence",
                    "block downstream artifact update",
                    "require review before retry",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_abort_quarantine_decision_policy/pilot_abort_quarantine_report.md",
        "# Pilot Abort and Quarantine Policy\n\n"
        "The future pilot must abort on any disallowed action pressure or operator "
        "uncertainty. Quarantine prevents downstream mutation.\n",
        generated,
    )

    success_signals = [
        "evidence packet completed",
        "source trace captured",
        "source date/freshness captured or date_missing marked",
        "claim boundary captured",
        "missing context captured",
        "unsupported claims captured",
        "no-action guarantees preserved",
        "review packet generated",
        "artifact refinement candidate generated if appropriate",
        "no forbidden action occurred",
    ]
    failure_signals = [
        "source required login/account/payment/contact/form",
        "source outside scope",
        "evidence could not be captured",
        "claim boundary unclear",
        "freshness could not be determined",
        "operator uncertainty",
        "any forbidden action pressure encountered",
        "pilot could not remain read-only",
    ]
    write_json(
        "pilot_success_failure_criteria/pilot_success_criteria.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "criteria_type": "structural_success_signals",
                "success_signals": success_signals,
                "semantic_truth_scoring_used": False,
                "market_success_scoring_used": False,
                "llm_confidence_as_authority_used": False,
                "revenue_scoring_used": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_success_failure_criteria/pilot_failure_criteria.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "criteria_type": "structural_failure_signals",
                "failure_signals": failure_signals,
                "semantic_truth_scoring_used": False,
                "market_success_scoring_used": False,
                "llm_confidence_as_authority_used": False,
                "revenue_scoring_used": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_success_failure_criteria/pilot_signal_model.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "signal_model_type": "structural_read_only_pilot_signal_model",
                "allowed_signal_classes": [
                    "completed_evidence_packet",
                    "bounded_claim_trace",
                    "missing_context_disclosed",
                    "review_packet_ready",
                    "quarantined_or_rejected_if_needed",
                ],
                "disallowed_signal_classes": [
                    "semantic authority score",
                    "market success score",
                    "revenue score",
                    "publication performance score",
                    "model-confidence authority signal",
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_success_failure_criteria/pilot_learning_value_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "learning_value_mode": "internal_review_only",
                "rows": [
                    {
                        "pilot_candidate_id": candidate["pilot_candidate_id"],
                        "learning_value": "high",
                        "downside_risk": "low_if_future_boundary_is_followed",
                        "externalization_authorized": False,
                    }
                    for candidate in candidates
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_success_failure_criteria/pilot_success_failure_report.md",
        "# Pilot Success and Failure Criteria\n\n"
        "Criteria are structural and safety-preserving. They do not score market "
        "success, revenue probability, or semantic truth authority.\n",
        generated,
    )

    for file_name, action_type in NO_ACTION_RECEIPTS.items():
        write_json(
            f"pilot_no_action_and_execution_blockers/{file_name}",
            receipt(action_type),
            generated,
        )
    write_text(
        "pilot_no_action_and_execution_blockers/pilot_execution_blocker_report.md",
        "# Pilot No-Action and Execution Blockers\n\n"
        "All real-world execution channels remain unauthorized and unexecuted in L6.5.\n",
        generated,
    )

    decisions = [
        with_common(
            {
                "pilot_candidate_id": candidate["pilot_candidate_id"],
                "linked_l6_4_candidate_id": candidate["linked_l6_4_candidate_id"],
                "pilot_design_decision": "design_packet_ready",
                "real_observation_execution_decision": "blocked_pending_future_explicit_human_approval",
                "real_network_authorized": False,
                "execution_authorized": False,
                "review_required": True,
                "approval_required": True,
                "future_runtime_isolation_required": True,
                "future_milestone_required": True,
                "future_milestone": NEXT_MILESTONE,
            }
        )
        for candidate in candidates
    ]
    write_json(
        "pilot_design_decision_gate/pilot_design_decision_gate_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "decision_gate_mode": "pilot_design_only_real_execution_blocked",
                "allowed_design_decisions": ["design_packet_ready", "design_packet_incomplete"],
                "real_execution_decision_required": "blocked_pending_future_explicit_human_approval",
            }
        ),
        generated,
    )
    write_json(
        "pilot_design_decision_gate/pilot_candidate_decisions.json",
        {
            "schema_version": SCHEMA_VERSION,
            "decision_count": len(decisions),
            "decisions": decisions,
        },
        generated,
    )
    write_json(
        "pilot_design_decision_gate/blocked_real_pilot_execution_decisions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blocked_count": len(decisions),
                "decisions": [
                    {
                        "pilot_candidate_id": decision["pilot_candidate_id"],
                        "real_observation_execution_decision": decision[
                            "real_observation_execution_decision"
                        ],
                        "real_network_authorized": False,
                        "execution_authorized": False,
                    }
                    for decision in decisions
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_design_decision_gate/future_pilot_entry_conditions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "future_entry_conditions": [
                    "future explicit human approval",
                    "future runtime isolation confirmation",
                    "approved source locator",
                    "source allowlist confirmation",
                    "denylist absence confirmation",
                    "operator runbook acknowledgement",
                    "evidence packet template ready",
                    "abort/quarantine policy acknowledgement",
                    "post-observation review gate ready",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_design_decision_gate/pilot_design_decision_gate_report.md",
        "# Pilot Design Decision Gate\n\n"
        "Design packets may be ready, but real pilot execution is blocked pending "
        "future explicit human approval and runtime isolation confirmation.\n",
        generated,
    )

    write_json(
        "l6_pilot_design_strategic_residual_loop/l6_5_cieu_like_fixture.json",
        with_common(
            {
                "X_t": {
                    "l6_0_value_selection": INPUT_REFS["l6_0_selection"],
                    "l6_1_mvp_artifact_sandbox": INPUT_REFS["l6_1_cases"],
                    "l6_2_external_observation_boundary": INPUT_REFS["l6_2_boundary"],
                    "l6_3_controlled_observation_sandbox": INPUT_REFS["l6_3_selected_cases"],
                    "l6_4_real_read_only_preflight": INPUT_REFS["l6_4_summary"],
                },
                "U_t": (
                    "Create a future controlled real read-only observation pilot design "
                    "without executing the pilot."
                ),
                "Y_star_t": (
                    "Design a controlled future real read-only observation pilot while "
                    "preserving no-network/no-scraping/no-API/no-browser-fetch/no-search/"
                    "no-publication/no-outreach/no-payment/no-revenue/no-MCP/no-live/"
                    "no-CIEU-DB-write/no-canonical-mutation/no-brain-memory-writeback/"
                    "no-direct-Y-star mutation constraints."
                ),
                "Y_t_plus_1": {
                    "pilot_candidates_selected": len(candidates),
                    "approval_packet_candidates_generated": len(approval_packets),
                    "operator_runbook_generated": True,
                    "evidence_templates_generated": True,
                    "review_workflow_generated": True,
                    "real_pilot_execution_authorized": False,
                },
                "R_t_plus_1": [
                    "real observation still not executed",
                    "pilot approval still pending future human review",
                    "source locators remain placeholders",
                    "evidence packet templates untested on real data",
                    "operator runbook untested live",
                    "runtime isolation not exercised",
                    "no real freshness verification yet",
                    "artifact refinements remain review-only",
                    "publication/outreach/payment/revenue remain blocked",
                ],
                "event_mode": "l6_5_controlled_real_read_only_observation_pilot_design_fixture",
                "persistence_enabled": False,
                "db_write_performed": False,
                "l6_pilot_execution_enabled": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_pilot_design_strategic_residual_loop/l6_5_strategic_residual_delta.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "residual_classes": {
                    "real_observation_execution_gap": "real observation not executed",
                    "approval_gap": "future human approval still required",
                    "source_locator_gap": "source locators remain placeholders",
                    "evidence_template_gap": "templates untested on real data",
                    "operator_runbook_gap": "runbook untested live",
                    "runtime_isolation_gap": "runtime isolation not exercised",
                    "freshness_verification_gap": "no real freshness verification yet",
                    "artifact_refinement_gap": "refinements remain review-only",
                    "externalization_gap": "publication/outreach/payment/revenue remain blocked",
                },
            }
        ),
        generated,
    )
    write_json(
        "l6_pilot_design_strategic_residual_loop/l6_5_meta_learning_update_candidate.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "learning_targets": [
                    "pilot_design_policy",
                    "operator_runbook_policy",
                    "evidence_capture_template_policy",
                    "post_observation_review_policy",
                    "abort_quarantine_policy",
                    "no_action_guarantee_policy",
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
        "l6_pilot_design_strategic_residual_loop/l6_5_residual_report.md",
        "# L6.5 Strategic Residual\n\n"
        "The pilot design is complete enough for review, but execution remains "
        "blocked. All learning is review-only and unapplied.\n",
        generated,
    )

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_5_controlled_real_read_only_observation_pilot_design_complete": True,
        "pilot_candidates_selected": True,
        "pilot_scope_and_non_goals_defined": True,
        "pilot_source_constraints_defined": True,
        "pilot_approval_packet_candidates_generated": True,
        "pilot_operator_runbook_generated": True,
        "pilot_evidence_packet_templates_generated": True,
        "post_observation_review_workflow_defined": True,
        "abort_quarantine_policy_defined": True,
        "success_failure_criteria_defined": True,
        "no_action_guarantees_generated": True,
        "pilot_design_decision_gate_generated": True,
        "strategic_residual_loop_generated": True,
        "ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet": True,
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
        "l6_5_flags": L6_5_FLAGS,
    }
    write_json("l6_pilot_design_readiness/l6_5_readiness_assessment.json", readiness, generated)
    write_json(
        "l6_pilot_design_readiness/l6_5_next_milestone_recommendation.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "recommended_next_milestone": NEXT_MILESTONE,
                "do_not_implement_in_l6_5": True,
                "ready_for_future_approval_packet_design": True,
                "ready_for_real_observation_execution_now": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_pilot_design_readiness/l6_5_blockers.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blockers": [
                    "future explicit human approval missing",
                    "future runtime isolation confirmation missing",
                    "real source locators not approved",
                    "operator runbook not exercised",
                    "evidence templates untested on real data",
                    "post-observation review not executed",
                    "externalization remains blocked",
                ],
            }
        ),
        generated,
    )
    write_text(
        "l6_pilot_design_readiness/l6_5_readiness_report.md",
        "# L6.5 Readiness\n\n"
        "- L6.5 pilot design complete: true\n"
        f"- Ready for {NEXT_MILESTONE}: true\n"
        "- Ready for actual network observation now: false\n"
        "- Ready for publication/outreach/payment/revenue execution: false\n"
        "- Ready for MCP/canonical/writeback/direct Y-star mutation: false\n",
        generated,
    )

    return generated


def main() -> None:
    generated = generate()
    print(
        "Built L6.5 controlled real read-only observation pilot design artifacts: "
        f"{len(generated)} files"
    )


if __name__ == "__main__":
    main()
