#!/usr/bin/env python3
"""Build L6.10X controlled external search resolver locator discovery artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from controlled_search_resolver_runtime.controlled_search_resolver import (  # noqa: E402
    BACKEND_ENV_VAR,
    ENABLE_ENV_VAR,
    ControlledSearchResolverRuntime,
    LocatorSearchRequest,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10X"
MILESTONE_NAME = (
    "Controlled External Search Resolver Enablement & First Autonomous Locator Discovery v0"
)
MODE = "controlled_external_search_resolver_first_locator_discovery"
INPUT_MILESTONES = [
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
    "L6.10W",
]

RUNTIME_LIMITS = {
    "max_selected_work_orders": 1,
    "max_locator_discovery_queries": 1,
    "max_search_results_considered": 1,
    "max_concrete_locators_returned": 1,
    "max_pages_read": 1,
    "max_total_external_reads": 2,
    "max_crawled_links": 0,
    "max_followed_links_except_normal_redirect": 0,
    "max_login_attempts": 0,
    "max_forms_submitted": 0,
    "max_messages_sent": 0,
    "max_payments": 0,
}

SAFETY_FLAGS = {
    "autonomous_locator_query_generation_authorized": True,
    "controlled_external_search_resolver_authorized": True,
    "backend_must_be_explicitly_configured": True,
    "user_manual_url_provision_required": False,
    "ask_user_for_url_authorized": False,
    "url_invention_authorized": False,
    "fake_locator_authorized": False,
    "broad_search_authorized": False,
    "repeated_search_loop_authorized": False,
    "crawling_authorized": False,
    "scraping_authorized": False,
    "browser_automation_authorized": False,
    "login_authorized": False,
    "account_creation_authorized": False,
    "contact_authorized": False,
    "payment_authorized": False,
    "form_submission_authorized": False,
    "posting_commenting_messaging_authorized": False,
    "publication_authorized": False,
    "outreach_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "live_behavior_authorized": False,
    "cieu_db_write_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
    "artifact_refinement_candidate_generation_authorized": True,
    "artifact_refinement_application_authorized": False,
    "semantic_truth_scoring_authorized": False,
    "llm_confidence_as_authority_authorized": False,
    "search_snippet_fact_use_authorized": False,
}

NO_ACTIONS = [
    "broad_search",
    "repeated_search_loop",
    "crawling",
    "scraping",
    "browser_automation",
    "login",
    "account_creation",
    "contact",
    "payment",
    "form_submission",
    "posting_commenting_messaging",
    "publication",
    "outreach",
    "revenue_execution",
    "mcp_execution",
    "live_behavior",
    "cieu_db_write",
    "canonical_mutation",
    "brain_memory_writeback",
    "direct_y_star_mutation",
]


def read_json(path: str) -> dict[str, Any]:
    target = ROOT / path
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def write_json(path: str, payload: dict[str, Any] | list[Any], generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    generated.append(path)


def write_text(path: str, text: str, generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")
    generated.append(path)


def url_like(locator: str | None) -> bool:
    return bool(locator and (locator.startswith("https://") or locator.startswith("http://")))


def select_work_order() -> dict[str, Any]:
    previous = read_json("reviewed_seed_locator_injection/selected_work_order_for_seed_injection.json")
    if not previous:
        previous = read_json("locator_resolution_v_attempt/selected_work_order.json")
    selected_id = previous.get("selected_work_order_id")
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_work_order_id": "l6_10x_selected_work_order_001",
        "source_selected_work_order_id": selected_id,
        "linked_l6_10w_selected_work_order_id": previous.get("selected_work_order_id"),
        "linked_l6_10v_selected_work_order_id": previous.get("linked_l6_10v_selected_work_order_id"),
        "linked_l6_10u_selected_work_order_id": previous.get("linked_l6_10u_selected_work_order_id"),
        "linked_l6_8_work_order_id": previous.get("linked_l6_8_work_order_id"),
        "linked_evidence_need_id": previous.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": previous.get("linked_source_hypothesis_id"),
        "linked_l6_artifact": previous.get("linked_l6_artifact"),
        "source_type": previous.get("source_type") or "primary_official_source",
        "source_function": previous.get("source_function")
        or previous.get("source_type")
        or "public read-only source",
        "evidence_need": previous.get("evidence_need") or previous.get("expected_evidence_type"),
        "expected_evidence_type": previous.get("expected_evidence_type")
        or previous.get("evidence_need")
        or "bounded public evidence",
        "observation_question": previous.get("observation_question")
        or "Which public source can answer the selected evidence need?",
        "trust_requirement": "candidate_structural_trust_review_required",
        "freshness_requirement": "freshness_check_required",
        "claim_boundary_to_test": previous.get(
            "claim_boundary_to_test",
            "internal review claim only; no publication, outreach, payment, revenue, or strategy claim",
        ),
        "selected_count": 1 if selected_id else 0,
        "selection_reason": (
            "Prefer the L6.10W work order, but replace manual URL provision with one "
            "autonomous controlled locator discovery query."
        ),
    }


def generated_query(selected: dict[str, Any]) -> dict[str, Any]:
    parts = [
        selected.get("source_function"),
        selected.get("source_type"),
        selected.get("expected_evidence_type"),
        selected.get("observation_question"),
    ]
    query_text = " ".join(str(part).strip() for part in parts if part).replace("\n", " ")
    return {
        "schema_version": SCHEMA_VERSION,
        "query_id": "l6_10x_locator_discovery_query_001",
        "query_text": query_text[:240],
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_type": selected.get("source_type"),
        "source_function": selected.get("source_function"),
        "expected_locator_type": "one_concrete_public_url",
        "expected_evidence_type": selected.get("expected_evidence_type"),
        "trust_requirement": selected.get("trust_requirement"),
        "freshness_requirement": selected.get("freshness_requirement"),
        "query_purpose": "locator_discovery_only",
        "no_snippet_fact_use": True,
        "no_fact_inference_from_search_result": True,
        "max_queries": 1,
        "max_results": 1,
    }


def backend_registry() -> dict[str, Any]:
    profiles = [
        "brave_search_api",
        "bing_search_api",
        "tavily_search_api",
        "serpapi",
        "openclaw_read_only_search_adapter",
        "future_governed_mcp_search_adapter",
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "l6_10x_controlled_search_backend_registry",
        "supported_backend_profiles": [
            {
                "backend_id": profile,
                "enabled": False,
                "requires_explicit_enable_flag": True,
                "search_use": "locator_candidate_only",
                "snippets_are_evidence": False,
            }
            for profile in profiles
        ],
        "default_backend_mode": "disabled",
        "enabled_backend_count": 0,
        "manual_url_request_fallback_allowed": False,
    }


def backend_config_example() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "controlled_search_enabled": False,
        "backend_id": None,
        "backend_available": False,
        "max_queries": 1,
        "max_results": 1,
        "approved_single_result_locator": None,
        "approved_single_result_title": None,
        "external_network_read_used": False,
        "enablement_env_vars": {
            "enabled_flag": ENABLE_ENV_VAR,
            "backend_selector": BACKEND_ENV_VAR,
        },
        "snippets_used_as_evidence": False,
        "facts_inferred_from_search_result": False,
    }


def backend_probe(config: dict[str, Any]) -> dict[str, Any]:
    configured = bool(config.get("controlled_search_enabled") and config.get("backend_id"))
    return {
        "schema_version": SCHEMA_VERSION,
        "probe_id": "l6_10x_controlled_search_backend_probe",
        "probe_mode": "local_config_and_environment_gate_only",
        "network_used": False,
        "browser_used": False,
        "mcp_used": False,
        "backend_explicitly_configured": False,
        "configured_backend_id": config.get("backend_id") if configured else None,
        "backend_available": False,
        "backend_mode": "disabled",
        "error_code": "controlled_search_backend_not_configured",
        "blocked_reason": "controlled_search_backend_not_configured",
        "manual_url_request_fallback_allowed": False,
    }


def locator_request(selected: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": "l6_10x_locator_discovery_request_001",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_selected_work_order_id": selected.get("source_selected_work_order_id"),
        "evidence_need_id": selected.get("linked_evidence_need_id"),
        "source_type": selected.get("source_type"),
        "source_function": selected.get("source_function"),
        "observation_question": selected.get("observation_question"),
        "expected_evidence_type": selected.get("expected_evidence_type"),
        "trust_requirement": selected.get("trust_requirement"),
        "freshness_requirement": selected.get("freshness_requirement"),
        "query_text": query.get("query_text"),
        "max_queries": 1,
        "max_results": 1,
        "no_snippet_fact_use": True,
        "no_fact_inference_from_search_result": True,
        "no_broad_search": True,
        "no_repeated_search": True,
        "no_crawling": True,
    }


def eligibility(selected: dict[str, Any], result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    locator = result.get("resolved_locator")
    evaluated = bool(locator)
    checks = {
        "locator_exists": bool(locator),
        "locator_is_url_like": url_like(locator),
        "public_read_only_expected": bool(locator),
        "not_login_page_expected": True,
        "not_payment_page_expected": True,
        "not_checkout_expected": True,
        "not_contact_form_expected": True,
        "not_private_account_or_inbox_expected": True,
        "not_social_posting_commenting_surface_expected": True,
        "source_type_matches_work_order": bool(locator),
        "one_page_observation_plausible": bool(locator),
        "no_crawling_required": True,
        "no_scraping_required": True,
        "no_mcp_required": True,
    }
    passed = evaluated and all(checks.values())
    return (
        {
            "schema_version": SCHEMA_VERSION,
            "eligibility_result_id": "l6_10x_locator_candidate_eligibility_result",
            "selected_work_order_id": selected.get("selected_work_order_id"),
            "locator_candidate": locator,
            "eligibility_evaluated": evaluated,
            "eligible_for_tiny_read_only_observation": passed,
            "reason": None if passed else ("no_locator_candidate" if not locator else "locator_candidate_failed_gate"),
            "checks": checks,
            "no_crawling_required": True,
            "no_scraping_required": True,
            "no_mcp_required": True,
        },
        {
            "schema_version": SCHEMA_VERSION,
            "risk_assessment_id": "l6_10x_locator_candidate_risk_assessment",
            "locator_candidate": locator,
            "risk_assessed": evaluated,
            "risk_class": "not_assessed_no_locator" if not locator else "low_candidate_pending_review",
            "privacy_ip_risk": "not_assessed_no_locator" if not locator else "low_expected_public_read_only",
            "overclaim_risk": "blocked_until_post_observation_review",
            "rejection_reason": None if passed else ("no_locator_candidate" if not locator else "locator_candidate_failed_gate"),
        },
    )


def observation_outputs(
    selected: dict[str, Any],
    discovery_result: dict[str, Any],
    eligibility_result: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    locator = discovery_result.get("resolved_locator")
    eligible = bool(eligibility_result.get("eligible_for_tiny_read_only_observation"))
    observation_executed = False
    reason = "no_locator_candidate" if not locator else "locator_resolved_but_observation_blocked"
    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10x_autonomous_tiny_observation_trace",
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "source_locator": locator,
        "observation_executed": observation_executed,
        "reason": reason,
        "eligible_locator_available": eligible,
        "read_only": True,
        "network_used": False,
        "external_reads_count": 0,
        "pages_read_count": 0,
        "search_query_count": discovery_result.get("search_query_count", 0),
        "login_encountered": False,
        "payment_encountered": False,
        "form_encountered": False,
        "private_data_encountered": False,
        "raw_content_storage_policy": "no_raw_page_dump",
    }
    packet = {
        "schema_version": SCHEMA_VERSION,
        "execution_packet_id": "l6_10x_autonomous_tiny_observation_execution_packet",
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "source_locator": locator,
        "observation_question": selected.get("observation_question"),
        "runtime_limits": RUNTIME_LIMITS,
        "tiny_observation_authorized_if_eligible": True,
        "observation_executed_in_l6_10x": observation_executed,
        "all_downstream_actions_authorized": False,
    }
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "evidence_packet_id": "l6_10x_autonomous_tiny_evidence_packet",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_locator": locator,
        "source_title": discovery_result.get("source_title"),
        "source_publisher_or_owner": None,
        "observed_at_timestamp": None,
        "source_date_or_date_missing": "not_observed",
        "freshness_class": "not_observed",
        "live_source_evidence_captured": False,
        "captured_claims": [],
        "unsupported_claims": [],
        "missing_context": [reason],
        "claim_boundary": selected.get("claim_boundary_to_test"),
        "citation_trace": [],
        "capture_method": "blocked_no_locator_or_no_observation",
        "review_status": "blocked_pending_controlled_search_backend"
        if not locator
        else "blocked_pending_tiny_observation_runtime",
        "external_action_taken": False,
        "publication_taken": False,
        "outreach_taken": False,
        "payment_taken": False,
        "revenue_action_taken": False,
        "mcp_execution_taken": False,
        "canonical_update_taken": False,
        "brain_memory_writeback_taken": False,
        "direct_y_star_mutation_taken": False,
    }
    claim = {
        "schema_version": SCHEMA_VERSION,
        "assessment_id": "l6_10x_autonomous_tiny_claim_boundary_assessment",
        "bounded_claims": [],
        "unsupported_inferences": ["no factual claim may be inferred from search result or snippet"],
        "freshness_assessment": "not_observed",
        "allowed_use": "internal_review_only",
        "external_use_authorized": False,
    }
    review = {
        "schema_version": SCHEMA_VERSION,
        "review_packet_id": "l6_10x_autonomous_tiny_post_observation_review_packet",
        "linked_evidence_packet_id": evidence["evidence_packet_id"],
        "current_decision": "review_pending_no_live_evidence",
        "approve_for_external_use": False,
        "approve_for_artifact_refinement_candidate": False,
        "applied": False,
    }
    refinement = {
        "schema_version": SCHEMA_VERSION,
        "refinement_candidate_id": "l6_10x_autonomous_tiny_refinement_candidate",
        "linked_evidence_packet_id": evidence["evidence_packet_id"],
        "review_required": True,
        "approved": False,
        "applied": False,
        "artifact_update_authorized": False,
        "canonical_update_authorized": False,
        "brain_writeback_authorized": False,
        "memory_ingestion_authorized": False,
        "direct_y_star_mutation_authorized": False,
    }
    receipts = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": "l6_10x_autonomous_tiny_no_action_receipts",
        "network_used_for_observation": False,
        **{f"{action}_executed": False for action in NO_ACTIONS},
    }
    return packet, trace, evidence, claim, review, refinement, receipts


def main() -> None:
    generated: list[str] = []
    selected = select_work_order()
    query = generated_query(selected)
    config = backend_config_example()
    probe = backend_probe(config)
    request_payload = locator_request(selected, query)
    result = ControlledSearchResolverRuntime(config=config).resolve(
        LocatorSearchRequest.from_mapping(request_payload)
    )
    result_payload = result.to_dict()
    result_payload["schema_version"] = SCHEMA_VERSION
    result_payload["selected_work_order_id"] = selected.get("selected_work_order_id")
    result_payload["generated_query"] = query.get("query_text")
    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10x_locator_discovery_trace",
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "backend_mode": result.backend_mode,
        "backend_explicitly_configured": result.backend_explicitly_configured,
        "controlled_search_executed": result.controlled_search_executed,
        "search_query_count": result.search_query_count,
        "search_results_considered": result.search_results_considered,
        "external_reads_count": result.external_reads_count,
        "concrete_locator_resolved": result.concrete_locator_resolved,
        "resolved_locator": result.resolved_locator,
        "snippets_used_as_evidence": False,
        "facts_inferred_from_search_result": False,
        "blocked_reason": result.blocked_reason,
        "error_code": result.error_code,
    }
    eligibility_result, risk_assessment = eligibility(selected, result_payload)
    (
        observation_packet,
        observation_trace,
        evidence_packet,
        claim_assessment,
        review_packet,
        refinement_candidate,
        no_action_receipts,
    ) = observation_outputs(selected, result_payload, eligibility_result)
    remaining_blocker = (
        "configure_controlled_search_backend"
        if result.error_code == "controlled_search_backend_not_configured"
        else result.error_code
    )
    readiness = {
        "schema_version": SCHEMA_VERSION,
        "l6_10x_controlled_external_search_resolver_locator_discovery_complete": True,
        "locator_resolved": result.concrete_locator_resolved,
        "tiny_observation_executed": observation_trace["observation_executed"],
        "ready_for_l6_11_controlled_multi_source_corroboration": False,
        "next_step": "configure_controlled_search_backend",
        "do_not_ask_user_to_manually_search_url": True,
        "publication_ready": False,
        "outreach_ready": False,
        "payment_ready": False,
        "revenue_execution_ready": False,
        "mcp_execution_ready": False,
        "canonical_update_ready": False,
        "brain_memory_writeback_ready": False,
    }
    blockers = {
        "schema_version": SCHEMA_VERSION,
        "blockers": [
            {
                "blocker_id": "l6_10x_controlled_search_backend_not_configured",
                "blocker_code": result.error_code,
                "description": "No explicit controlled external search backend is configured.",
                "next_step": "configure_controlled_search_backend",
                "manual_url_request_allowed": False,
            }
        ],
    }
    next_milestone = {
        "schema_version": SCHEMA_VERSION,
        "recommended_next_milestone": "L6.10Y Controlled Search Backend Configuration v0",
        "reason": "Autonomous locator discovery is architected, but default backend mode is disabled.",
        "do_not_implement_l6_11_until_locator_or_observation_succeeds": True,
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "mode": MODE,
        "l6_10x_controlled_external_search_resolver_locator_discovery_complete": True,
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "generated_locator_query": query.get("query_text"),
        "backend_mode": result.backend_mode,
        "backend_explicitly_configured": result.backend_explicitly_configured,
        "controlled_search_executed": result.controlled_search_executed,
        "search_query_count": result.search_query_count,
        "search_results_considered": result.search_results_considered,
        "concrete_locator_resolved": result.concrete_locator_resolved,
        "resolved_locator": result.resolved_locator,
        "snippets_used_as_evidence": False,
        "facts_inferred_from_search_result": False,
        "tiny_read_only_observation_executed": observation_trace["observation_executed"],
        "evidence_packet_generated": True,
        "remaining_blocker": remaining_blocker,
        **SAFETY_FLAGS,
        **RUNTIME_LIMITS,
    }
    cieu = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_10x_controlled_external_search_resolver_locator_discovery_fixture",
        "X_t": {"selected_work_order": selected, "generated_query": query},
        "U_t": {
            "runtime_limits": RUNTIME_LIMITS,
            "backend_mode": result.backend_mode,
            "controlled_search_executed": result.controlled_search_executed,
        },
        "Y_star_t": (
            "Generate one autonomous controlled locator discovery query for one governed work "
            "order, use an explicitly configured controlled search backend if available, "
            "return at most one locator, and preserve all no-action/writeback boundaries."
        ),
        "Y_t_plus_1": {
            "query_generated": True,
            "backend_configured": result.backend_explicitly_configured,
            "locator_resolved": result.concrete_locator_resolved,
            "observation_executed": observation_trace["observation_executed"],
        },
        "R_t_plus_1": {
            "residuals": [
                "controlled_search_backend_not_configured",
                "no locator resolved in default path",
                "no live evidence captured",
                "L6.11 remains blocked",
            ]
        },
    }
    meta_candidate = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "l6_10x_meta_learning_update_candidate",
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "eligible_for_direct_strategy_mutation": False,
        "approved": False,
        "applied": False,
    }
    residual = {
        "schema_version": SCHEMA_VERSION,
        "residual_id": "l6_10x_strategic_residual_delta",
        "primary_residual": remaining_blocker,
        "manual_url_request_removed": True,
        "controlled_search_backend_required": True,
    }
    read_summary = {
        **summary,
        "readiness_next_step": readiness["next_step"],
        "generated_refs": {
            "milestone_summary": "l6_controlled_external_search_resolver_locator_discovery/l6_10x_summary.json",
            "query": "autonomous_locator_query_generator/generated_locator_discovery_query.json",
            "discovery_result": "autonomous_locator_discovery_attempt/locator_discovery_result.json",
            "evidence_packet": "autonomous_locator_observation_result/autonomous_tiny_evidence_packet.json",
            "readiness": "l6_10x_read_model/l6_10x_readiness_assessment.json",
        },
    }

    write_text(
        "l6_controlled_external_search_resolver_locator_discovery/README.md",
        f"# {MILESTONE_ID} {MILESTONE_NAME}\n\n"
        "Creates an autonomous controlled external search resolver path for one locator discovery query. "
        "The default path is disabled, performs no search/network access, and reports controlled search "
        "backend enablement requirements instead of asking the user to manually find a URL.",
        generated,
    )
    write_json(
        "l6_controlled_external_search_resolver_locator_discovery/l6_10x_milestone_contract.json",
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": INPUT_MILESTONES,
            "mode": MODE,
            **SAFETY_FLAGS,
            **RUNTIME_LIMITS,
        },
        generated,
    )
    write_json(
        "l6_controlled_external_search_resolver_locator_discovery/l6_10x_scope.json",
        {
            "schema_version": SCHEMA_VERSION,
            "scope_id": "l6_10x_scope",
            "included": [
                "one work order selection",
                "one autonomous locator discovery query generation",
                "controlled search backend registry and runtime interface",
                "default disabled no-search attempt",
                "locator eligibility gate",
                "blocked evidence and review packets",
            ],
            "excluded": [
                "manual URL request path",
                "broad web search",
                "repeated search loops",
                "crawling",
                "scraping",
                "browser automation",
                "downstream externalization or writeback",
            ],
        },
        generated,
    )
    write_json("l6_controlled_external_search_resolver_locator_discovery/l6_10x_runtime_limits.json", RUNTIME_LIMITS, generated)
    write_json("l6_controlled_external_search_resolver_locator_discovery/l6_10x_safety_flags.json", SAFETY_FLAGS, generated)
    write_json("l6_controlled_external_search_resolver_locator_discovery/l6_10x_summary.json", summary, generated)
    write_text(
        "l6_controlled_external_search_resolver_locator_discovery/l6_10x_summary.md",
        "# L6.10X Summary\n\n"
        "- Autonomous locator query generated: yes\n"
        f"- Backend mode: {result.backend_mode}\n"
        f"- Controlled search executed: {result.controlled_search_executed}\n"
        "- Manual URL request path: removed\n"
        f"- Remaining blocker: {remaining_blocker}",
        generated,
    )

    write_json("autonomous_locator_query_generator/selected_work_order_for_locator_discovery.json", selected, generated)
    write_json(
        "autonomous_locator_query_generator/locator_query_generation_contract.json",
        {
            "schema_version": SCHEMA_VERSION,
            "contract_id": "l6_10x_locator_query_generation_contract",
            "derivation_fields": [
                "evidence_need",
                "source_type",
                "source_function",
                "observation_question",
                "expected_evidence_type",
                "trust_requirement",
                "freshness_requirement",
            ],
            "query_purpose": "locator_discovery_only",
            "max_queries": 1,
            "max_results": 1,
            "no_snippet_fact_use": True,
            "no_fact_inference_from_search_result": True,
        },
        generated,
    )
    write_json("autonomous_locator_query_generator/generated_locator_discovery_query.json", query, generated)
    write_json(
        "autonomous_locator_query_generator/query_generation_trace.json",
        {
            "schema_version": SCHEMA_VERSION,
            "trace_id": "l6_10x_query_generation_trace",
            "selected_work_order_id": selected.get("selected_work_order_id"),
            "fields_used": [
                "source_function",
                "source_type",
                "expected_evidence_type",
                "observation_question",
            ],
            "query_count_generated": 1,
            "manual_url_requested": False,
        },
        generated,
    )
    write_text(
        "autonomous_locator_query_generator/autonomous_locator_query_report.md",
        "# Autonomous Locator Query Report\n\n"
        "Generated exactly one locator-discovery-only query from the selected work order. "
        "Search snippets are not evidence and no fact inference is allowed from search results.",
        generated,
    )

    write_json("controlled_search_backend_registry/controlled_search_backend_registry.json", backend_registry(), generated)
    write_json("controlled_search_backend_registry/controlled_search_backend_config.example.json", config, generated)
    write_json(
        "controlled_search_backend_registry/controlled_search_backend_enablement_requirements.json",
        {
            "schema_version": SCHEMA_VERSION,
            "requirements_id": "l6_10x_controlled_search_backend_enablement_requirements",
            "required_env_vars": [ENABLE_ENV_VAR, BACKEND_ENV_VAR],
            "required_config": [
                "controlled_search_enabled: true",
                "backend_id",
                "backend_available: true",
                "max_queries: 1",
                "max_results: 1",
            ],
            "manual_url_request_is_not_an_enablement_path": True,
            "search_result_snippets_are_not_evidence": True,
        },
        generated,
    )
    write_json("controlled_search_backend_registry/controlled_search_backend_probe_result.json", probe, generated)
    write_text(
        "controlled_search_backend_registry/controlled_search_backend_registry_report.md",
        "# Controlled Search Backend Registry Report\n\n"
        "No backend is enabled by default. The next engineering step is controlled search backend "
        "configuration, not asking the user to manually search for a URL.",
        generated,
    )

    write_json(
        "controlled_search_resolver_runtime/controlled_search_resolver_types.json",
        {
            "schema_version": SCHEMA_VERSION,
            "request_type": "LocatorSearchRequest",
            "result_type": "LocatorSearchResult",
            "backend_config_type": "SearchBackendConfig",
            "default_error_code": "controlled_search_backend_not_configured",
        },
        generated,
    )
    write_json(
        "controlled_search_resolver_runtime/controlled_search_resolver_policy.json",
        {
            "schema_version": SCHEMA_VERSION,
            "policy_id": "l6_10x_controlled_search_resolver_policy",
            "max_queries": 1,
            "max_results": 1,
            "max_locator_outputs": 1,
            "snippets_used_as_evidence": False,
            "facts_inferred_from_search_result": False,
            "manual_url_request_allowed": False,
            "broad_search_allowed": False,
            "repeated_search_loop_allowed": False,
            "crawling_allowed": False,
            "scraping_allowed": False,
            "browser_automation_allowed": False,
        },
        generated,
    )
    write_json("controlled_search_resolver_runtime/controlled_search_resolver_trace.json", result_payload, generated)
    write_text(
        "controlled_search_resolver_runtime/controlled_search_resolver_report.md",
        "# Controlled Search Resolver Runtime Report\n\n"
        f"Runtime backend mode: `{result.backend_mode}`. Search executed: `{result.controlled_search_executed}`. "
        "Default execution performs no external request and returns controlled_search_backend_not_configured.",
        generated,
    )

    write_json("autonomous_locator_discovery_attempt/locator_discovery_request.json", request_payload, generated)
    write_json("autonomous_locator_discovery_attempt/locator_discovery_result.json", result_payload, generated)
    write_json("autonomous_locator_discovery_attempt/locator_discovery_trace.json", trace, generated)
    write_text(
        "autonomous_locator_discovery_attempt/locator_discovery_attempt_report.md",
        "# Locator Discovery Attempt Report\n\n"
        f"Generated query: `{query.get('query_text')}`\n\n"
        f"Backend mode: `{result.backend_mode}`. Concrete locator resolved: `{result.concrete_locator_resolved}`. "
        "The default path does not ask the user for a URL.",
        generated,
    )

    write_json(
        "locator_candidate_eligibility_gate/locator_candidate_eligibility_contract.json",
        {
            "schema_version": SCHEMA_VERSION,
            "contract_id": "l6_10x_locator_candidate_eligibility_contract",
            "checks": [
                "locator exists",
                "locator is URL-like",
                "public/read-only expected",
                "not login page",
                "not payment page",
                "not checkout",
                "not contact form",
                "not private account/inbox",
                "not social posting/commenting surface",
                "source type matches work order",
                "one-page observation plausible",
                "no crawling required",
                "no scraping required",
                "no MCP required",
            ],
        },
        generated,
    )
    write_json("locator_candidate_eligibility_gate/locator_candidate_eligibility_result.json", eligibility_result, generated)
    write_json("locator_candidate_eligibility_gate/locator_candidate_risk_assessment.json", risk_assessment, generated)
    write_text(
        "locator_candidate_eligibility_gate/locator_candidate_eligibility_report.md",
        "# Locator Candidate Eligibility Report\n\n"
        "No locator candidate was produced in the default path, so eligibility was not evaluated.",
        generated,
    )

    write_json("autonomous_locator_observation_result/autonomous_tiny_observation_execution_packet.json", observation_packet, generated)
    write_json("autonomous_locator_observation_result/autonomous_tiny_observation_trace.json", observation_trace, generated)
    write_json("autonomous_locator_observation_result/autonomous_tiny_evidence_packet.json", evidence_packet, generated)
    write_json("autonomous_locator_observation_result/autonomous_tiny_claim_boundary_assessment.json", claim_assessment, generated)
    write_json("autonomous_locator_observation_result/autonomous_tiny_post_observation_review_packet.json", review_packet, generated)
    write_json("autonomous_locator_observation_result/autonomous_tiny_refinement_candidate.json", refinement_candidate, generated)
    write_json("autonomous_locator_observation_result/autonomous_tiny_no_action_receipts.json", no_action_receipts, generated)
    write_text(
        "autonomous_locator_observation_result/autonomous_locator_observation_result_report.md",
        "# Autonomous Locator Observation Result Report\n\n"
        "No locator candidate was available, so no observation executed. A blocked evidence packet, review "
        "packet, and unapplied refinement candidate were generated.",
        generated,
    )

    write_json("l6_10x_read_model/l6_10x_cieu_like_fixture.json", cieu, generated)
    write_json("l6_10x_read_model/l6_10x_strategic_residual_delta.json", residual, generated)
    write_json("l6_10x_read_model/l6_10x_meta_learning_update_candidate.json", meta_candidate, generated)
    write_json("l6_10x_read_model/l6_10x_readiness_assessment.json", readiness, generated)
    write_json("l6_10x_read_model/l6_10x_blockers.json", blockers, generated)
    write_json("l6_10x_read_model/l6_10x_next_milestone_recommendation.json", next_milestone, generated)
    write_json("l6_10x_read_model/l6_10x_read_model_summary.json", read_summary, generated)
    write_text(
        "l6_10x_read_model/l6_10x_report.md",
        "# L6.10X Read Model Report\n\n"
        "L6.10X replaces the manual URL fallback with autonomous controlled locator discovery architecture. "
        "The default run is blocked because no controlled search backend is configured.",
        generated,
    )
    print(f"generated {len(generated)} L6.10X files")


if __name__ == "__main__":
    main()
