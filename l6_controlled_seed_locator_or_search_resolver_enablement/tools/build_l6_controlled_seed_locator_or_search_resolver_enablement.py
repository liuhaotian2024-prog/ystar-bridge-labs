#!/usr/bin/env python3
"""Build L6.10V seed locator or explicit search resolver enablement artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from explicit_controlled_search_resolver.explicit_search_resolver_runtime import (  # noqa: E402
    ExplicitControlledSearchResolver,
    ExplicitSearchResolutionRequest,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10V"
MILESTONE_NAME = (
    "Controlled Seed Locator Registry Population or Explicit Controlled Search Resolver Enablement v0"
)
MODE = "controlled_seed_locator_or_explicit_search_resolver_enablement"
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
]

RUNTIME_LIMITS = {
    "max_selected_work_orders": 1,
    "max_seed_registry_lookups": 1,
    "max_controlled_search_queries": 1,
    "max_concrete_locators_resolved": 1,
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
    "reviewed_seed_locator_registry_authorized": True,
    "explicit_controlled_search_resolver_authorized": True,
    "controlled_search_requires_explicit_enable_flag": True,
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


def selected_work_order() -> dict[str, Any]:
    previous = read_json("controlled_locator_resolution_attempt/selected_work_order.json")
    if not previous:
        previous = read_json("locator_retry_work_order_selector/selected_locator_retry_work_order.json")
    selected_id = previous.get("selected_work_order_id") or previous.get("selected_retry_work_order_id")
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_work_order_id": "l6_10v_selected_work_order_001",
        "source_selected_work_order_id": selected_id,
        "linked_l6_10u_selected_work_order_id": previous.get("selected_work_order_id"),
        "linked_l6_10r_selected_work_order_id": previous.get("linked_l6_10r_selected_work_order_id")
        or previous.get("selected_retry_work_order_id"),
        "linked_l6_8_work_order_id": previous.get("linked_l6_8_work_order_id"),
        "linked_evidence_need_id": previous.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": previous.get("linked_source_hypothesis_id"),
        "linked_l6_artifact": previous.get("linked_l6_artifact"),
        "observation_question": previous.get("observation_question"),
        "source_type": previous.get("source_type"),
        "source_function": previous.get("source_function") or previous.get("source_type"),
        "source_locator_placeholder": previous.get("source_locator_placeholder"),
        "expected_evidence_type": previous.get("expected_evidence_type"),
        "claim_boundary_to_test": previous.get(
            "claim_boundary_to_test",
            "internal review claim only; no publication, outreach, payment, revenue, or strategy claim",
        ),
        "selection_reason": (
            "Preferred the active L6.10U/L6.10R selected work order because it is the "
            "current unresolved locator path and has a clear evidence need."
        ),
        "selected_count": 1 if selected_id else 0,
        "eligible_for_l6_10v_locator_resolution": bool(selected_id),
    }


def seed_schema() -> dict[str, Any]:
    required = [
        "seed_locator_id",
        "linked_work_order_id",
        "linked_evidence_need_id",
        "source_type",
        "source_function",
        "concrete_locator",
        "source_title",
        "source_owner_or_publisher",
        "why_this_locator_matches",
        "reviewed_status",
        "review_required_before_observation",
        "public_read_only_expected",
        "login_expected",
        "payment_expected",
        "form_expected",
        "contact_expected",
        "source_use_allowed",
        "facts_inferred_from_seed",
        "observation_authorized_by_seed_alone",
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "schema_id": "l6_10v_seed_locator_registry_schema",
        "required_fields": required,
        "entry_constraints": {
            "concrete_locator_must_be_url_like": True,
            "reviewed_status_allowed": [
                "reviewed_for_locator_resolution_only",
                "sample_only_not_eligible",
                "pending_review",
            ],
            "source_use_allowed_required_value": "locator_resolution_only",
            "facts_inferred_from_seed_must_be_false": True,
            "observation_authorized_by_seed_alone_must_be_false": True,
        },
    }


def reviewed_seed_registry() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "l6_10v_reviewed_seed_locator_registry",
        "registry_scope": "exactly_one_selected_l6_10v_work_order",
        "selected_work_order_id": "l6_10v_selected_work_order_001",
        "reviewed_seed_locators": [],
        "sample_entries": [],
        "empty_registry_reason": "no_reviewed_seed_locator_available",
        "do_not_invent_urls": True,
        "facts_inferred_from_seed": False,
        "observation_authorized_by_seed_alone": False,
    }


def seed_lookup(selected: dict[str, Any], registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    entries = registry.get("reviewed_seed_locators", [])
    matching = [
        entry
        for entry in entries
        if entry.get("linked_work_order_id") in {
            selected.get("selected_work_order_id"),
            selected.get("source_selected_work_order_id"),
            selected.get("linked_l6_10u_selected_work_order_id"),
            selected.get("linked_l6_10r_selected_work_order_id"),
        }
        and entry.get("reviewed_status") == "reviewed_for_locator_resolution_only"
    ]
    match = matching[0] if matching else None
    return (
        {
            "schema_version": SCHEMA_VERSION,
            "trace_id": "l6_10v_seed_locator_registry_lookup_trace",
            "selected_work_order_id": selected.get("selected_work_order_id"),
            "lookup_executed": True,
            "lookup_count": 1,
            "entries_considered": len(entries),
            "matching_entries": 1 if match else 0,
            "seed_locator_resolved": bool(match and match.get("concrete_locator")),
            "resolved_locator": match.get("concrete_locator") if match else None,
            "facts_inferred_from_seed": False,
            "blocked_reason": None if match else "no_reviewed_seed_locator_available",
        },
        match,
    )


def resolution_request(selected: dict[str, Any]) -> dict[str, Any]:
    query = (
        f"{selected.get('source_type')} {selected.get('expected_evidence_type')} "
        f"{selected.get('observation_question')}"
    ).strip()
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": "l6_10v_locator_resolution_v_request_001",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_selected_work_order_id": selected.get("source_selected_work_order_id"),
        "linked_l6_8_work_order_id": selected.get("linked_l6_8_work_order_id"),
        "linked_evidence_need_id": selected.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": selected.get("linked_source_hypothesis_id"),
        "source_type": selected.get("source_type"),
        "source_function": selected.get("source_function"),
        "observation_question": selected.get("observation_question"),
        "locator_discovery_query": query,
        "query_purpose": "locator_resolution_only",
        "max_queries": 1,
        "max_results": 1,
        "no_snippet_fact_use": True,
        "no_fact_inference_from_search_result": True,
        "no_broad_search": True,
        "no_repeated_search": True,
        "no_crawling": True,
    }


def url_like(locator: str | None) -> bool:
    return bool(locator and (locator.startswith("https://") or locator.startswith("http://")))


def build_eligibility(selected: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    locator = result.get("resolved_locator")
    concrete = bool(result.get("concrete_locator_resolved")) and url_like(locator)
    checks = {
        "locator_is_concrete": concrete,
        "locator_is_url_like": url_like(locator),
        "public_read_only_expected": bool(result.get("public_read_only_expected", False)),
        "no_login_expected": True,
        "no_payment_expected": True,
        "no_form_expected": True,
        "no_contact_expected": True,
        "no_crawling_required": True,
        "no_scraping_required": True,
        "no_mcp_required": True,
        "source_type_matches_work_order": (
            not result.get("source_type") or result.get("source_type") == selected.get("source_type")
        ),
        "expected_evidence_type_plausible": concrete,
    }
    failed = [key for key, value in checks.items() if value is not True]
    return {
        "schema_version": SCHEMA_VERSION,
        "eligibility_id": "l6_10v_locator_resolution_v_eligibility_result",
        "linked_resolution_request_id": "l6_10v_locator_resolution_v_request_001",
        "resolved_locator": locator,
        **checks,
        "locator_eligible_for_observation": concrete and not failed,
        "observation_blocked": not (concrete and not failed),
        "failed_checks": failed,
        "blocked_reason": None if concrete and not failed else (
            "no_concrete_locator" if not concrete else "locator_failed_eligibility"
        ),
    }


def build_observation_outputs(
    selected: dict[str, Any], result: dict[str, Any], eligibility: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    if not result.get("concrete_locator_resolved"):
        reason = "no_concrete_locator"
    elif not eligibility.get("locator_eligible_for_observation"):
        reason = "locator_resolved_but_observation_blocked"
    else:
        reason = "locator_resolved_but_observation_blocked"
    locator = result.get("resolved_locator")
    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10v_tiny_observation_v_trace",
        "observation_executed": False,
        "reason": reason,
        "source_locator": locator,
        "read_only": True,
        "network_used": False,
        "external_reads_count": 0,
        "pages_read_count": 0,
        "controlled_search_query_count": result.get("controlled_search_query_count", 0),
        "login_encountered": False,
        "payment_encountered": False,
        "form_encountered": False,
        "private_data_encountered": False,
        "raw_content_storage_policy": "no_raw_page_dump_stored",
    }
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "evidence_packet_id": "l6_10v_tiny_evidence_v_packet",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_locator": locator,
        "source_title": result.get("source_title"),
        "source_publisher_or_owner": result.get("source_owner_or_publisher"),
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
    return {
        "execution_packet": {
            "schema_version": SCHEMA_VERSION,
            "execution_packet_id": "l6_10v_tiny_observation_v_execution_packet",
            "selected_work_order_id": selected.get("selected_work_order_id"),
            "resolved_locator": locator,
            "tiny_observation_authorized": False,
            "authorization_status": reason,
            "runtime_limits": RUNTIME_LIMITS,
            "all_downstream_actions_authorized": False,
        },
        "trace": trace,
        "evidence": evidence,
        "claim_boundary": {
            "schema_version": SCHEMA_VERSION,
            "claim_boundary_assessment_id": "l6_10v_tiny_claim_boundary_v_assessment",
            "linked_evidence_packet_id": evidence["evidence_packet_id"],
            "bounded_claims": [],
            "unsupported_inferences": ["no live source evidence captured"],
            "freshness_status": "not_observed",
            "semantic_truth_scoring_used": False,
            "llm_confidence_used_as_authority": False,
            "allowed_use": "internal_review_only",
            "external_use_authorized": False,
        },
        "review": {
            "schema_version": SCHEMA_VERSION,
            "review_packet_id": "l6_10v_tiny_post_observation_v_review_packet",
            "linked_evidence_packet_id": evidence["evidence_packet_id"],
            "current_decision": "review_pending_blocked_no_live_evidence",
            "approve_for_artifact_refinement_candidate": False,
            "approve_for_external_use": False,
            "applied": False,
        },
        "refinement": {
            "schema_version": SCHEMA_VERSION,
            "refinement_candidate_id": "l6_10v_tiny_refinement_v_candidate",
            "linked_evidence_packet_id": evidence["evidence_packet_id"],
            "linked_l6_artifact": selected.get("linked_l6_artifact"),
            "proposed_refinement": "No artifact refinement proposed because no live source evidence was captured.",
            "review_required": True,
            "approved": False,
            "applied": False,
            "artifact_update_authorized": False,
            "canonical_update_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "direct_y_star_mutation_authorized": False,
        },
        "receipts": {
            "schema_version": SCHEMA_VERSION,
            "receipt_set_id": "l6_10v_tiny_observation_v_no_action_receipts",
            "receipts": [
                {
                    "action_type": action,
                    "authorized_in_l6_10v": False,
                    "executed_in_l6_10v": False,
                    "blocker_reference": "l6_10v_safety_flags",
                }
                for action in NO_ACTIONS
            ],
        },
    }


def build() -> list[str]:
    generated: list[str] = []
    selected = selected_work_order()
    registry = reviewed_seed_registry()
    lookup_trace, seed_entry = seed_lookup(selected, registry)
    request = resolution_request(selected)

    search_config = {
        "schema_version": SCHEMA_VERSION,
        "controlled_search_enabled": False,
        "requires_environment_variable": "YSTAR_ENABLE_CONTROLLED_LOCATOR_SEARCH=1",
        "controlled_search_backend_available": False,
        "max_queries": 1,
        "max_results": 1,
        "no_snippet_fact_use": True,
        "no_fact_inference_from_search_result": True,
        "disabled_reason": "controlled_search_resolver_disabled_by_default",
    }
    search_result = ExplicitControlledSearchResolver(config=search_config).resolve(
        ExplicitSearchResolutionRequest.from_mapping(request)
    ).to_dict()

    if seed_entry and seed_entry.get("concrete_locator"):
        resolution_path = "reviewed_seed_registry"
        error_code = None
        blocked_reason = None
        resolved_locator = seed_entry.get("concrete_locator")
        source_title = seed_entry.get("source_title")
        source_owner = seed_entry.get("source_owner_or_publisher")
        source_type = seed_entry.get("source_type")
        public_read_only_expected = seed_entry.get("public_read_only_expected", False)
        concrete_locator_resolved = True
    elif search_result.get("concrete_locator_resolved"):
        resolution_path = "explicit_controlled_search"
        error_code = None
        blocked_reason = None
        resolved_locator = search_result.get("resolved_locator")
        source_title = search_result.get("source_title")
        source_owner = None
        source_type = selected.get("source_type")
        public_read_only_expected = False
        concrete_locator_resolved = True
    else:
        resolution_path = "disabled_no_path"
        error_code = "no_enabled_locator_resolution_path"
        blocked_reason = (
            "no_reviewed_seed_locator_available_and_controlled_search_resolver_disabled_by_default"
        )
        resolved_locator = None
        source_title = None
        source_owner = None
        source_type = selected.get("source_type")
        public_read_only_expected = False
        concrete_locator_resolved = False

    result = {
        "schema_version": SCHEMA_VERSION,
        "result_id": "l6_10v_locator_resolution_v_result",
        "resolution_path_used": resolution_path,
        "seed_registry_lookup_count": lookup_trace["lookup_count"],
        "controlled_search_query_count": search_result.get("controlled_search_query_count", 0),
        "external_reads_count": search_result.get("external_reads_count", 0),
        "concrete_locator_resolved": concrete_locator_resolved,
        "resolved_locator": resolved_locator,
        "source_title": source_title,
        "source_owner_or_publisher": source_owner,
        "source_type": source_type,
        "public_read_only_expected": public_read_only_expected,
        "facts_inferred_from_resolution": False,
        "search_snippets_used_as_evidence": False,
        "error_code": error_code,
        "blocked_reason": blocked_reason,
    }
    eligibility = build_eligibility(selected, result)
    observation = build_observation_outputs(selected, result, eligibility)

    contract = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        **SAFETY_FLAGS,
        **RUNTIME_LIMITS,
    }
    summary = {
        **contract,
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "resolution_path_used": result["resolution_path_used"],
        "seed_registry_lookup_count": result["seed_registry_lookup_count"],
        "seed_locator_resolved": resolution_path == "reviewed_seed_registry",
        "controlled_search_enabled": search_result.get("resolver_enabled", False),
        "controlled_search_query_count": result["controlled_search_query_count"],
        "concrete_locator_resolved": result["concrete_locator_resolved"],
        "resolved_locator": result["resolved_locator"],
        "tiny_read_only_observation_executed": observation["trace"]["observation_executed"],
        "external_reads_count": result["external_reads_count"],
        "pages_read_count": observation["trace"]["pages_read_count"],
        "evidence_packet_generated": True,
        "remaining_blocker": error_code,
        "enablement_instructions": [
            "Add one reviewed seed locator entry to seed_locator_registry/reviewed_seed_locator_registry.json, or",
            "Set controlled_search_enabled=true in explicit_search_resolver_config.json and YSTAR_ENABLE_CONTROLLED_LOCATOR_SEARCH=1 with an approved one-result backend.",
        ],
    }

    write_text(
        "l6_controlled_seed_locator_or_search_resolver_enablement/README.md",
        f"""# {MILESTONE_ID} {MILESTONE_NAME}

L6.10V creates two concrete enablement paths for one locator: a reviewed seed
locator registry and an explicit opt-in controlled search resolver. The default
run does not invent a URL, does not execute search, and records exact enablement
requirements when neither path is available.
""",
        generated,
    )
    write_json("l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_milestone_contract.json", contract, generated)
    write_json("l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_scope.json", {
        "schema_version": SCHEMA_VERSION,
        "scope_id": "l6_10v_scope",
        "resolution_priority": ["reviewed_seed_registry", "explicit_controlled_search", "disabled_no_path"],
        "one_work_order_only": True,
        "no_fake_locator": True,
        "search_snippets_are_not_evidence": True,
        "downstream_actions_blocked": True,
    }, generated)
    write_json("l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_runtime_limits.json", RUNTIME_LIMITS, generated)
    write_json("l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_safety_flags.json", SAFETY_FLAGS, generated)
    write_json("l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_summary.json", summary, generated)
    write_text(
        "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_summary.md",
        f"""# L6.10V Summary

- selected work order: {selected.get('selected_work_order_id')}
- resolution path used: {resolution_path}
- seed registry lookup count: {result['seed_registry_lookup_count']}
- controlled search enabled: {search_result.get('resolver_enabled', False)}
- controlled search query count: {result['controlled_search_query_count']}
- concrete locator resolved: {result['concrete_locator_resolved']}
- tiny read-only observation executed: {observation['trace']['observation_executed']}
- remaining blocker: {error_code}
""",
        generated,
    )

    write_json("seed_locator_registry/seed_locator_registry_schema.json", seed_schema(), generated)
    write_json("seed_locator_registry/reviewed_seed_locator_registry.json", registry, generated)
    write_json("seed_locator_registry/seed_locator_review_policy.json", {
        "schema_version": SCHEMA_VERSION,
        "policy_id": "l6_10v_seed_locator_review_policy",
        "review_required_before_observation": True,
        "reviewed_status_required": "reviewed_for_locator_resolution_only",
        "source_use_allowed": "locator_resolution_only",
        "facts_inferred_from_seed": False,
        "observation_authorized_by_seed_alone": False,
        "do_not_invent_urls": True,
    }, generated)
    write_json("seed_locator_registry/seed_locator_registry_lookup_trace.json", lookup_trace, generated)
    write_text("seed_locator_registry/seed_locator_registry_report.md", "# Seed Locator Registry Report\n\nNo reviewed seed locator is present for the selected work order; no URL was invented.", generated)

    write_json("explicit_controlled_search_resolver/explicit_search_resolver_contract.json", {
        "schema_version": SCHEMA_VERSION,
        "resolver_id": "explicit_controlled_search_resolver",
        "disabled_by_default": True,
        "requires_config_flag": "controlled_search_enabled=true",
        "requires_environment_variable": "YSTAR_ENABLE_CONTROLLED_LOCATOR_SEARCH=1",
        "max_queries": 1,
        "max_results": 1,
        "snippets_are_not_evidence": True,
        "facts_inferred_from_search_result": False,
        "browser_automation_allowed": False,
        "scraping_allowed": False,
    }, generated)
    write_json("explicit_controlled_search_resolver/explicit_search_resolver_config.json", search_config, generated)
    write_json("explicit_controlled_search_resolver/explicit_search_resolver_trace.json", search_result, generated)
    write_text("explicit_controlled_search_resolver/explicit_search_resolver_report.md", "# Explicit Search Resolver Report\n\nThe explicit controlled search resolver is disabled by default. No query ran in the L6.10V default path.", generated)

    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10v_locator_resolution_v_trace",
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "resolution_priority": ["reviewed_seed_registry", "explicit_controlled_search", "disabled_no_path"],
        "resolution_path_used": result["resolution_path_used"],
        "seed_registry_lookup_trace": lookup_trace,
        "explicit_search_trace": search_result,
        "concrete_locator_resolved": result["concrete_locator_resolved"],
        "resolved_locator": result["resolved_locator"],
        "facts_inferred_from_resolution": False,
        "blocked_reason": result["blocked_reason"],
        "error_code": result["error_code"],
    }
    write_json("locator_resolution_v_attempt/selected_work_order.json", selected, generated)
    write_json("locator_resolution_v_attempt/locator_resolution_v_request.json", request, generated)
    write_json("locator_resolution_v_attempt/locator_resolution_v_result.json", result, generated)
    write_json("locator_resolution_v_attempt/locator_resolution_v_trace.json", trace, generated)
    write_json("locator_resolution_v_attempt/locator_resolution_v_eligibility_result.json", eligibility, generated)
    write_text("locator_resolution_v_attempt/locator_resolution_v_report.md", f"# Locator Resolution V Attempt\n\nResult: `{result['error_code']}` using `{result['resolution_path_used']}`.", generated)

    write_json("tiny_observation_v_result/tiny_observation_v_execution_packet.json", observation["execution_packet"], generated)
    write_json("tiny_observation_v_result/tiny_observation_v_trace.json", observation["trace"], generated)
    write_json("tiny_observation_v_result/tiny_evidence_v_packet.json", observation["evidence"], generated)
    write_json("tiny_observation_v_result/tiny_claim_boundary_v_assessment.json", observation["claim_boundary"], generated)
    write_json("tiny_observation_v_result/tiny_post_observation_v_review_packet.json", observation["review"], generated)
    write_json("tiny_observation_v_result/tiny_refinement_v_candidate.json", observation["refinement"], generated)
    write_json("tiny_observation_v_result/tiny_observation_v_no_action_receipts.json", observation["receipts"], generated)
    write_text("tiny_observation_v_result/tiny_observation_v_result_report.md", "# Tiny Observation V Result\n\nNo tiny observation executed because no concrete locator was resolved.", generated)

    cieu = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_10v_controlled_seed_locator_or_search_resolver_enablement_fixture",
        "X_t": {"prior_blocker": "no_enabled_locator_resolution_path"},
        "U_t": "Create reviewed seed locator and explicit controlled search enablement paths for one work order.",
        "Y_star_t": "Resolve at most one concrete locator using reviewed seed registry or explicitly enabled controlled search while preserving no broad search, no crawling, no scraping, no browser automation, no publication/outreach/payment/revenue/MCP/live/CIEU/canonical/writeback/direct Y* mutation constraints.",
        "Y_t_plus_1": {
            "reviewed_seed_registry_created": True,
            "explicit_search_resolver_created": True,
            "resolution_path_used": result["resolution_path_used"],
            "concrete_locator_resolved": result["concrete_locator_resolved"],
            "tiny_read_only_observation_executed": observation["trace"]["observation_executed"],
        },
        "R_t_plus_1": [
            result["error_code"],
            "reviewed seed locator still required",
            "explicit controlled search remains disabled by default",
            "no evidence captured yet",
        ],
    }
    meta = {
        "schema_version": SCHEMA_VERSION,
        "meta_learning_candidate_id": "l6_10v_meta_learning_update_candidate",
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
        "l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete": True,
        "reviewed_seed_locator_registry_created": True,
        "explicit_controlled_search_resolver_created": True,
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "resolution_path_used": result["resolution_path_used"],
        "seed_registry_lookup_count": result["seed_registry_lookup_count"],
        "controlled_search_enabled": search_result.get("resolver_enabled", False),
        "controlled_search_query_count": result["controlled_search_query_count"],
        "concrete_locator_resolved": result["concrete_locator_resolved"],
        "tiny_read_only_observation_executed": observation["trace"]["observation_executed"],
        "ready_for_l6_11_controlled_multi_source_corroboration": False,
        "remaining_blocker": result["error_code"],
        "next_step": "reviewed seed locator required or explicit controlled search resolver enablement required",
        "next_recommended_milestone": "L6.10W Reviewed Seed Locator Population or Controlled Search Backend Enablement v0",
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
        "primary_blocker": result["error_code"],
        "blockers": [
            "no_reviewed_seed_locator_available",
            "controlled_search_resolver_disabled_by_default",
        ],
        "exact_enablement_required": summary["enablement_instructions"],
    }
    recommendation = {
        "schema_version": SCHEMA_VERSION,
        "next_milestone": readiness["next_recommended_milestone"],
        "reason": "The resolver paths now exist, but neither has an eligible concrete locator in the default environment.",
        "l6_11_blocked_until_locator_and_tiny_observation_success": True,
    }
    read_model_summary = {
        "schema_name": "ystar.console_read_model.l6_10v_read_model_summary",
        "schema_version": SCHEMA_VERSION,
        **summary,
    }
    write_json("l6_10v_read_model/l6_10v_cieu_like_fixture.json", cieu, generated)
    write_json("l6_10v_read_model/l6_10v_strategic_residual_delta.json", {
        "schema_version": SCHEMA_VERSION,
        "residual_id": "l6_10v_strategic_residual_delta",
        "remaining_blocker": result["error_code"],
        "new_enablement_paths": ["reviewed_seed_registry", "explicit_controlled_search"],
        "downstream_actions_blocked": True,
    }, generated)
    write_json("l6_10v_read_model/l6_10v_meta_learning_update_candidate.json", meta, generated)
    write_json("l6_10v_read_model/l6_10v_readiness_assessment.json", readiness, generated)
    write_json("l6_10v_read_model/l6_10v_blockers.json", blockers, generated)
    write_json("l6_10v_read_model/l6_10v_next_milestone_recommendation.json", recommendation, generated)
    write_json("l6_10v_read_model/l6_10v_read_model_summary.json", read_model_summary, generated)
    write_text("l6_10v_read_model/l6_10v_report.md", f"# L6.10V Report\n\nResolution path used: `{resolution_path}`. Remaining blocker: `{error_code}`.", generated)
    return generated


if __name__ == "__main__":
    paths = build()
    print(f"generated {len(paths)} L6.10V files")
