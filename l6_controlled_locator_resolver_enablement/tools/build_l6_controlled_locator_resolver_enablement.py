#!/usr/bin/env python3
"""Build L6.10U controlled locator resolver enablement artifacts.

This builder implements the first practical resolver runtime path while keeping
the default run local-only: seed registry lookup, environment-gated search
disabled unless explicitly enabled, and a disabled resolver fallback.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from controlled_locator_resolver_runtime.controlled_locator_resolver import (  # noqa: E402
    ControlledLocatorResolverRuntime,
    LocatorResolutionRequest,
    RUNTIME_LIMITS,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10U"
MILESTONE_NAME = "Controlled Locator Resolver Enablement & First Locator Attempt v0"
MODE = "controlled_locator_resolver_enablement_first_attempt"
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
]

SAFETY_FLAGS = {
    "seed_registry_resolver_authorized": True,
    "environment_gated_controlled_search_resolver_authorized": True,
    "disabled_resolver_authorized": True,
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
    "fake_locator_generation_authorized": False,
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
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    generated.append(path)


def write_text(path: str, text: str, generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")
    generated.append(path)


def get_selected_work_order() -> dict[str, Any]:
    candidates = [
        read_json("locator_retry_work_order_selector/selected_locator_retry_work_order.json"),
        read_json("tiny_observation_work_order_selector/selected_tiny_observation_work_order.json"),
        read_json("observation_work_order_generator/observation_work_order_001.json"),
    ]
    source = next((candidate for candidate in candidates if candidate), {})
    selected_id = (
        source.get("selected_retry_work_order_id")
        or source.get("selected_work_order_id")
        or source.get("work_order_id")
        or "no_eligible_work_order"
    )
    linked_l6_8 = source.get("linked_l6_8_work_order_id") or source.get("work_order_id")
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_work_order_id": "l6_10u_selected_work_order_001"
        if selected_id != "no_eligible_work_order"
        else "no_eligible_work_order",
        "source_selected_work_order_id": selected_id,
        "linked_l6_8_work_order_id": linked_l6_8,
        "linked_l6_9_selected_work_order_id": source.get("linked_l6_9_selected_work_order_id"),
        "linked_l6_10_selected_work_order_id": source.get("linked_l6_10_selected_work_order_id"),
        "linked_l6_10r_selected_work_order_id": source.get("selected_retry_work_order_id"),
        "linked_evidence_need_id": source.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": source.get("linked_source_hypothesis_id"),
        "linked_l6_artifact": source.get("linked_l6_artifact"),
        "observation_question": source.get("observation_question"),
        "source_type": source.get("source_type"),
        "source_function": source.get("source_function", source.get("source_type")),
        "source_locator_placeholder": source.get("source_locator_placeholder"),
        "expected_evidence_type": source.get("expected_evidence_type"),
        "claim_boundary_to_test": source.get(
            "claim_boundary_to_test",
            "internal review claim only; no publication, outreach, payment, revenue, or strategy claim",
        ),
        "selection_reason": (
            "Preferred the L6.10R selected work order because it is the active unresolved "
            "locator blocker and preserves the L6.8/L6.9/L6.10 lineage."
        ),
        "selected_count": 0 if selected_id == "no_eligible_work_order" else 1,
        "eligible_for_l6_10u_locator_resolution": selected_id != "no_eligible_work_order",
        "runtime_limits": RUNTIME_LIMITS,
        "real_observation_authorized_now": False,
    }


def build_request(selected: dict[str, Any]) -> dict[str, Any]:
    query = (
        f"{selected.get('source_type')} {selected.get('expected_evidence_type')} "
        f"{selected.get('observation_question')}"
    ).strip()
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": "l6_10u_locator_resolution_request_001",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_selected_work_order_id": selected.get("source_selected_work_order_id"),
        "linked_l6_8_work_order_id": selected.get("linked_l6_8_work_order_id"),
        "evidence_need_id": selected.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": selected.get("linked_source_hypothesis_id"),
        "source_type": selected.get("source_type"),
        "source_function": selected.get("source_function"),
        "observation_question": selected.get("observation_question"),
        "locator_discovery_query": query,
        "query_purpose": "locator_resolution_only",
        "max_queries": 1,
        "max_results": 1,
        "no_fact_inference_from_result": True,
        "no_snippet_fact_use": True,
        "no_broad_search": True,
        "no_crawling": True,
        "facts_inferred_from_resolution": False,
        "search_snippets_may_be_used_as_evidence": False,
    }


def url_like(locator: str | None) -> bool:
    return bool(locator and (locator.startswith("https://") or locator.startswith("http://")))


def build_locator_eligibility(
    selected: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    locator = result.get("locator")
    concrete = bool(result.get("concrete_locator_resolved")) and url_like(locator)
    failed_checks: list[str] = []
    if not concrete:
        failed_checks.append("no_concrete_url_like_locator")
    if result.get("source_type") and selected.get("source_type"):
        if result.get("source_type") != selected.get("source_type"):
            failed_checks.append("source_type_mismatch")
    if not concrete:
        reason = "no_concrete_locator"
    elif failed_checks:
        reason = "locator_failed_eligibility"
    else:
        reason = None
    return {
        "schema_version": SCHEMA_VERSION,
        "locator_eligibility_id": "l6_10u_locator_eligibility_001",
        "linked_resolution_request_id": "l6_10u_locator_resolution_request_001",
        "locator": locator,
        "locator_is_concrete": concrete,
        "locator_is_url_like": url_like(locator),
        "source_type_matches_work_order": "source_type_mismatch" not in failed_checks,
        "not_known_login_surface": True,
        "not_known_payment_surface": True,
        "not_known_form_surface": True,
        "not_known_private_surface": True,
        "one_page_read_only_observation_plausible": concrete,
        "no_crawling_required": True,
        "no_scraping_required": True,
        "no_mcp_required": True,
        "locator_eligible_for_observation": concrete and not failed_checks,
        "observation_blocked": not (concrete and not failed_checks),
        "failed_checks": failed_checks,
        "blocked_reason": reason,
        "real_observation_authorized_now": False,
    }


def build_observation_outputs(
    selected: dict[str, Any],
    result: dict[str, Any],
    eligibility: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    locator = result.get("locator")
    if not result.get("concrete_locator_resolved"):
        reason = "no_concrete_locator"
    elif not eligibility.get("locator_eligible_for_observation"):
        reason = "locator_resolved_but_observation_not_enabled_or_blocked"
    else:
        reason = "locator_resolved_but_observation_not_enabled_or_blocked"

    execution_packet = {
        "schema_version": SCHEMA_VERSION,
        "execution_packet_id": "l6_10u_tiny_observation_execution_packet_001",
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "resolved_locator": locator,
        "observation_question": selected.get("observation_question"),
        "source_type": selected.get("source_type"),
        "expected_evidence_type": selected.get("expected_evidence_type"),
        "claim_boundary_to_test": selected.get("claim_boundary_to_test"),
        "runtime_limits": RUNTIME_LIMITS,
        "tiny_observation_authorized": False,
        "authorization_status": reason,
        "publication_authorized": False,
        "outreach_authorized": False,
        "payment_authorized": False,
        "revenue_execution_authorized": False,
        "mcp_execution_authorized": False,
        "canonical_update_authorized": False,
        "brain_memory_writeback_authorized": False,
        "direct_y_star_mutation_authorized": False,
    }
    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10u_tiny_observation_trace_001",
        "linked_execution_packet_id": execution_packet["execution_packet_id"],
        "observation_executed": False,
        "reason": reason,
        "source_locator": locator,
        "read_only": True,
        "network_used": False,
        "external_reads_count": 0,
        "pages_read_count": 0,
        "search_query_count": result.get("search_query_count", 0),
        "login_encountered": False,
        "payment_encountered": False,
        "form_encountered": False,
        "private_data_encountered": False,
        "raw_content_storage_policy": "no_raw_page_dump_stored",
    }
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "evidence_packet_id": "l6_10u_tiny_evidence_packet_001",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_locator": locator,
        "source_title": result.get("source_title"),
        "source_publisher_or_owner": None,
        "observed_at_timestamp": None,
        "source_date_or_date_missing": "not_observed",
        "freshness_class": "not_observed",
        "captured_claims": [],
        "unsupported_claims": [],
        "missing_context": [reason],
        "claim_boundary": selected.get("claim_boundary_to_test"),
        "citation_trace": [],
        "live_source_evidence_captured": False,
        "review_status": "blocked_no_live_evidence",
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
    claim_boundary = {
        "schema_version": SCHEMA_VERSION,
        "claim_boundary_assessment_id": "l6_10u_claim_boundary_assessment_001",
        "linked_evidence_packet_id": evidence["evidence_packet_id"],
        "bounded_claims": [],
        "unsupported_inferences": ["no live source evidence captured"],
        "freshness_status": "not_observed",
        "semantic_truth_scoring_used": False,
        "llm_confidence_used_as_authority": False,
        "allowed_use": "internal_review_only",
        "external_use_authorized": False,
    }
    review = {
        "schema_version": SCHEMA_VERSION,
        "review_packet_id": "l6_10u_post_observation_review_packet_001",
        "linked_evidence_packet_id": evidence["evidence_packet_id"],
        "current_decision": "review_pending_blocked_no_live_evidence",
        "evidence_to_check": [],
        "missing_context_to_check": evidence["missing_context"],
        "approve_for_artifact_refinement_candidate": False,
        "approve_for_external_use": False,
        "applied": False,
    }
    refinement = {
        "schema_version": SCHEMA_VERSION,
        "refinement_candidate_id": "l6_10u_tiny_refinement_candidate_001",
        "linked_evidence_packet_id": evidence["evidence_packet_id"],
        "linked_l6_artifact": selected.get("linked_l6_artifact"),
        "refinement_target": selected.get("linked_l6_artifact"),
        "proposed_refinement": "No artifact refinement proposed because no live source evidence was captured.",
        "evidence_basis": [],
        "evidence_limitations": evidence["missing_context"],
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
        "receipt_set_id": "l6_10u_tiny_observation_no_action_receipts",
        "receipts": [
            {
                "action_type": action,
                "authorized_in_l6_10u": False,
                "executed_in_l6_10u": False,
                "blocker_reference": "l6_10u_safety_flags",
            }
            for action in NO_ACTIONS
        ],
    }
    return {
        "execution_packet": execution_packet,
        "trace": trace,
        "evidence": evidence,
        "claim_boundary": claim_boundary,
        "review": review,
        "refinement": refinement,
        "receipts": receipts,
    }


def build() -> list[str]:
    generated: list[str] = []

    selected = get_selected_work_order()
    request_payload = build_request(selected)
    registry = {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "l6_10u_seed_locator_registry",
        "purpose": "Local repo-controlled seed locator registry for governed locator resolution.",
        "seed_registry_lookup_authorized": True,
        "network_used": False,
        "seed_locators": [],
        "empty_registry_reason": (
            "No user-reviewed concrete public seed locator has been committed for the "
            "selected L6.10U work order; resolver must not invent one."
        ),
    }
    resolver_config = {
        "schema_version": SCHEMA_VERSION,
        "environment_gated_search_enabled": False,
        "requires_env_flag": "YSTAR_CONTROLLED_LOCATOR_SEARCH_ENABLED=1",
        "max_queries": 1,
        "max_results": 1,
        "no_snippet_fact_use": True,
        "no_claim_inference_from_search_result": True,
        "default_mode": "disabled_unless_explicitly_enabled",
    }

    write_json("controlled_locator_resolver_runtime/seed_locator_registry.json", registry, generated)
    write_json("controlled_locator_resolver_runtime/resolver_config.example.json", resolver_config, generated)

    request = LocatorResolutionRequest.from_mapping(request_payload)
    runtime = ControlledLocatorResolverRuntime(ROOT, config=resolver_config)
    result = runtime.resolve(request).to_dict()
    eligibility = build_locator_eligibility(selected, result)
    observation = build_observation_outputs(selected, result, eligibility)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        **SAFETY_FLAGS,
        **RUNTIME_LIMITS,
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "source_selected_work_order_id": selected.get("source_selected_work_order_id"),
        "resolver_mode_used": result.get("resolver_mode"),
        "resolver_id": result.get("resolver_id"),
        "seed_registry_lookup_executed": result.get("seed_registry_lookup_count", 0) > 0,
        "seed_registry_lookup_count": result.get("seed_registry_lookup_count", 0),
        "controlled_search_executed": result.get("search_query_count", 0) > 0,
        "search_query_count": result.get("search_query_count", 0),
        "external_reads_count": result.get("external_reads_count", 0),
        "concrete_locator_resolved": result.get("concrete_locator_resolved", False),
        "resolved_locator": result.get("locator"),
        "tiny_read_only_observation_executed": observation["trace"]["observation_executed"],
        "evidence_packet_generated": True,
        "post_observation_review_packet_generated": True,
        "artifact_refinement_candidate_generated": True,
        "artifact_refinement_applied": False,
        "remaining_blocker": result.get("error_code"),
        "no_fake_locator_generated": True,
        "network_used": False,
        "search_snippets_used_as_evidence": False,
    }
    contract = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        **SAFETY_FLAGS,
        **RUNTIME_LIMITS,
    }
    scope = {
        "schema_version": SCHEMA_VERSION,
        "scope_id": "l6_10u_scope",
        "allowed_resolver_modes": ["seed_registry", "environment_gated_search", "disabled"],
        "selected_work_order_limit": 1,
        "resolver_path_order": ["seed_registry", "environment_gated_search", "disabled"],
        "not_authorized": [action for action in NO_ACTIONS],
        "search_snippets_are_not_evidence": True,
        "fake_locator_forbidden": True,
    }

    write_text(
        "l6_controlled_locator_resolver_enablement/README.md",
        f"""# {MILESTONE_ID} {MILESTONE_NAME}

L6.10U implements the first practical controlled locator resolver enablement
path. The default run performs one local seed registry lookup, observes that no
reviewed seed locator exists for the selected work order, confirms the
environment-gated search path is disabled, and blocks without inventing a URL.

No broad search, crawling, scraping, browser automation, login, payment,
publication, outreach, revenue execution, MCP execution, live behavior, CIEU DB
write, canonical mutation, brain/memory writeback, or direct Y* mutation occurs.
""",
        generated,
    )
    write_json("l6_controlled_locator_resolver_enablement/l6_10u_milestone_contract.json", contract, generated)
    write_json("l6_controlled_locator_resolver_enablement/l6_10u_scope.json", scope, generated)
    write_json("l6_controlled_locator_resolver_enablement/l6_10u_runtime_limits.json", RUNTIME_LIMITS, generated)
    write_json("l6_controlled_locator_resolver_enablement/l6_10u_safety_flags.json", SAFETY_FLAGS, generated)
    write_json("l6_controlled_locator_resolver_enablement/l6_10u_summary.json", summary, generated)
    write_text(
        "l6_controlled_locator_resolver_enablement/l6_10u_summary.md",
        f"""# L6.10U Summary

- selected work order: {selected.get('source_selected_work_order_id')}
- resolver mode used: {result.get('resolver_mode')}
- seed registry lookup count: {result.get('seed_registry_lookup_count')}
- controlled search query count: {result.get('search_query_count')}
- concrete locator resolved: {result.get('concrete_locator_resolved')}
- tiny observation executed: {observation['trace']['observation_executed']}
- remaining blocker: {result.get('error_code')}

The milestone implements the resolver runtime and seed-registry path, but the
current repo-local seed registry contains no reviewed locator and the controlled
search adapter is disabled by default.
""",
        generated,
    )

    resolver_types = {
        "schema_version": SCHEMA_VERSION,
        "types": [
            "LocatorResolutionRequest",
            "LocatorResolutionResult",
            "BaseControlledLocatorResolver",
            "SeedRegistryResolver",
            "EnvironmentGatedSearchResolver",
            "DisabledResolver",
            "ControlledLocatorResolverRuntime",
        ],
        "default_path_network_used": False,
    }
    write_json("controlled_locator_resolver_runtime/resolver_types.json", resolver_types, generated)
    write_text(
        "controlled_locator_resolver_runtime/resolver_runtime_report.md",
        """# Resolver Runtime Report

The portable runtime is implemented in `controlled_locator_resolver.py`.
It attempts one local seed registry lookup, then checks the environment-gated
search resolver only if explicitly enabled, then returns a disabled blocked
result. The default L6.10U run used no network and did not fabricate a locator.
""",
        generated,
    )

    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10u_locator_resolution_trace_001",
        "resolver_mode": result.get("resolver_mode"),
        "resolver_id": result.get("resolver_id"),
        "seed_registry_lookup_count": result.get("seed_registry_lookup_count", 0),
        "search_query_count": result.get("search_query_count", 0),
        "external_reads_count": result.get("external_reads_count", 0),
        "concrete_locator_resolved": result.get("concrete_locator_resolved", False),
        "locator": result.get("locator"),
        "facts_inferred_from_resolution": result.get("facts_inferred_from_resolution", False),
        "blocked_reason": result.get("blocked_reason"),
        "error_code": result.get("error_code"),
        "runtime_trace": result.get("trace", {}),
    }
    write_json("controlled_locator_resolution_attempt/selected_work_order.json", selected, generated)
    write_json("controlled_locator_resolution_attempt/locator_resolution_request.json", request_payload, generated)
    write_json("controlled_locator_resolution_attempt/locator_resolution_result.json", result, generated)
    write_json("controlled_locator_resolution_attempt/locator_resolution_trace.json", trace, generated)
    write_json("controlled_locator_resolution_attempt/locator_eligibility_result.json", eligibility, generated)
    write_text(
        "controlled_locator_resolution_attempt/locator_resolution_attempt_report.md",
        f"""# Locator Resolution Attempt Report

One governed work order was selected from the existing L6.10R lineage. The
resolver runtime performed one local seed-registry lookup, did not run search,
and returned `{result.get('error_code')}` without a fake locator.
""",
        generated,
    )

    write_json("controlled_locator_observation_result/tiny_observation_execution_packet.json", observation["execution_packet"], generated)
    write_json("controlled_locator_observation_result/tiny_observation_trace.json", observation["trace"], generated)
    write_json("controlled_locator_observation_result/tiny_evidence_packet.json", observation["evidence"], generated)
    write_json("controlled_locator_observation_result/tiny_claim_boundary_assessment.json", observation["claim_boundary"], generated)
    write_json("controlled_locator_observation_result/tiny_post_observation_review_packet.json", observation["review"], generated)
    write_json("controlled_locator_observation_result/tiny_refinement_candidate.json", observation["refinement"], generated)
    write_json("controlled_locator_observation_result/tiny_observation_no_action_receipts.json", observation["receipts"], generated)
    write_text(
        "controlled_locator_observation_result/tiny_observation_result_report.md",
        """# Tiny Observation Result Report

No tiny read-only observation executed because no concrete locator was resolved.
An empty blocked evidence packet, pending review packet, and unapplied
refinement candidate were generated without downstream side effects.
""",
        generated,
    )

    cieu = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_10u_controlled_locator_resolver_enablement_first_attempt_fixture",
        "X_t": {
            "prior_state": "L6.10T identified no controlled locator resolver available.",
            "selected_work_order": selected.get("source_selected_work_order_id"),
        },
        "U_t": (
            "Enable a controlled seed-registry resolver path and attempt one bounded "
            "locator resolution request without broad search or fake locator creation."
        ),
        "Y_star_t": (
            "Enable a controlled locator resolver path that can resolve at most one concrete "
            "public locator for one governed work order using seed registry or explicitly "
            "enabled controlled search, optionally perform one tiny read-only observation, "
            "and preserve no-broad-search/no-crawling/no-scraping/no-login/no-payment/"
            "no-contact/no-publication/no-outreach/no-revenue/no-MCP/no-live/"
            "no-CIEU-DB-write/no-canonical-mutation/no-brain-memory-writeback/"
            "no-direct-Y* mutation constraints."
        ),
        "Y_t_plus_1": {
            "resolver_runtime_created": True,
            "seed_registry_lookup_executed": result.get("seed_registry_lookup_count", 0) > 0,
            "controlled_search_executed": result.get("search_query_count", 0) > 0,
            "concrete_locator_resolved": result.get("concrete_locator_resolved", False),
            "tiny_read_only_observation_executed": False,
        },
        "R_t_plus_1": [
            result.get("error_code"),
            "seed registry has no reviewed locator for selected work order",
            "controlled search resolver remains disabled by default",
            "L6.11 remains blocked until a locator is resolved and observation succeeds",
        ],
    }
    residual_delta = {
        "schema_version": SCHEMA_VERSION,
        "residual_id": "l6_10u_strategic_residual_delta",
        "remaining_blockers": [
            "no_seed_locator_available",
            "no_controlled_search_resolver_enabled",
            result.get("error_code"),
        ],
        "new_capability_created": "controlled_locator_resolver_runtime",
        "downstream_actions_blocked": True,
    }
    meta = {
        "schema_version": SCHEMA_VERSION,
        "meta_learning_candidate_id": "l6_10u_meta_learning_update_candidate",
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "eligible_for_direct_strategy_mutation": False,
        "approved": False,
        "applied": False,
    }
    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_10u_controlled_locator_resolver_enablement_complete": True,
        "resolver_runtime_created": True,
        "seed_registry_resolver_created": True,
        "environment_gated_search_resolver_created": True,
        "disabled_resolver_created": True,
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "resolver_mode_used": result.get("resolver_mode"),
        "seed_registry_lookup_executed": result.get("seed_registry_lookup_count", 0) > 0,
        "controlled_search_executed": result.get("search_query_count", 0) > 0,
        "concrete_locator_resolved": result.get("concrete_locator_resolved", False),
        "tiny_read_only_observation_executed": False,
        "ready_for_l6_11_controlled_multi_source_corroboration": False,
        "ready_for_l6_10u_retry_after_seed_or_search_enablement": True,
        "remaining_blocker": result.get("error_code"),
        "blockers": [
            "no_seed_locator_available",
            "no_controlled_search_resolver_enabled",
        ],
        "next_recommended_milestone": (
            "L6.10V Controlled Seed Locator Registry Population or Explicit "
            "Controlled Search Resolver Enablement v0"
        ),
        "publication_authorized": False,
        "outreach_authorized": False,
        "payment_authorized": False,
        "revenue_execution_authorized": False,
        "mcp_execution_authorized": False,
        "canonical_update_authorized": False,
        "brain_writeback_authorized": False,
        "memory_ingestion_authorized": False,
        "direct_y_star_mutation_authorized": False,
    }
    blockers = {
        "schema_version": SCHEMA_VERSION,
        "blockers": readiness["blockers"],
        "primary_blocker": result.get("error_code"),
        "no_fake_evidence_or_locator": True,
    }
    recommendation = {
        "schema_version": SCHEMA_VERSION,
        "next_milestone": readiness["next_recommended_milestone"],
        "reason": "One practical resolver runtime exists, but no seed locator or enabled controlled search path is available.",
        "do_not_implement_l6_11_until_successful_tiny_observation": True,
    }
    read_model_summary = {
        "schema_name": "ystar.console_read_model.l6_10u_read_model_summary",
        "schema_version": SCHEMA_VERSION,
        **summary,
    }
    write_json("controlled_locator_resolver_read_model/l6_10u_cieu_like_fixture.json", cieu, generated)
    write_json("controlled_locator_resolver_read_model/l6_10u_strategic_residual_delta.json", residual_delta, generated)
    write_json("controlled_locator_resolver_read_model/l6_10u_meta_learning_update_candidate.json", meta, generated)
    write_json("controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json", readiness, generated)
    write_json("controlled_locator_resolver_read_model/l6_10u_blockers.json", blockers, generated)
    write_json("controlled_locator_resolver_read_model/l6_10u_next_milestone_recommendation.json", recommendation, generated)
    write_json("controlled_locator_resolver_read_model/l6_10u_read_model_summary.json", read_model_summary, generated)
    write_text(
        "controlled_locator_resolver_read_model/l6_10u_read_model_report.md",
        f"""# L6.10U Read Model Report

L6.10U created a real portable resolver runtime and attempted one bounded
resolution path. The current outcome is blocked by `{result.get('error_code')}`:
the local seed registry contains no reviewed locator and controlled search is
not explicitly enabled. L6.11 remains blocked until a concrete locator can be
resolved and a tiny observation can complete safely.
""",
        generated,
    )
    return generated


if __name__ == "__main__":
    paths = build()
    print(f"generated {len(paths)} L6.10U files")
