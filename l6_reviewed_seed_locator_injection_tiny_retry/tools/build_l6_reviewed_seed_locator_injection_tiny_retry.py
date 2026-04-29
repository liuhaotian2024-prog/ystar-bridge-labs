#!/usr/bin/env python3
"""Build L6.10W reviewed seed locator injection and tiny retry artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10W"
MILESTONE_NAME = "Reviewed Seed Locator Injection & Tiny Observation Retry v0"
MODE = "reviewed_seed_locator_injection_and_tiny_retry"
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
]

RUNTIME_LIMITS = {
    "max_selected_work_orders": 1,
    "max_seed_locators_injected": 1,
    "max_pages_read": 1,
    "max_total_external_reads": 1,
}

SAFETY_FLAGS = {
    "reviewed_seed_locator_injection_authorized": True,
    "user_action_request_authorized": True,
    "seed_locator_from_existing_repo_artifacts_authorized": True,
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
    previous = read_json("locator_resolution_v_attempt/selected_work_order.json")
    if not previous:
        previous = read_json("controlled_locator_resolution_attempt/selected_work_order.json")
    selected_id = previous.get("selected_work_order_id")
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_work_order_id": "l6_10w_selected_work_order_001",
        "source_selected_work_order_id": selected_id,
        "linked_l6_10v_selected_work_order_id": previous.get("selected_work_order_id"),
        "linked_l6_10u_selected_work_order_id": previous.get("source_selected_work_order_id"),
        "linked_l6_8_work_order_id": previous.get("linked_l6_8_work_order_id"),
        "linked_evidence_need_id": previous.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": previous.get("linked_source_hypothesis_id"),
        "linked_l6_artifact": previous.get("linked_l6_artifact"),
        "source_type": previous.get("source_type"),
        "source_function": previous.get("source_function") or previous.get("source_type"),
        "evidence_need": previous.get("expected_evidence_type"),
        "expected_evidence_type": previous.get("expected_evidence_type"),
        "observation_question": previous.get("observation_question"),
        "claim_boundary_to_test": previous.get(
            "claim_boundary_to_test",
            "internal review claim only; no publication, outreach, payment, revenue, or strategy claim",
        ),
        "selected_count": 1 if selected_id else 0,
        "selection_reason": "Prefer the active L6.10V work order because it is the current unresolved reviewed-seed-locator path.",
    }


def load_registry_entries(path: str) -> list[dict[str, Any]]:
    payload = read_json(path)
    entries = payload.get("reviewed_seed_locators")
    if entries is not None:
        return list(entries)
    return list(payload.get("seed_locators", []))


def entry_matches(selected: dict[str, Any], entry: dict[str, Any]) -> bool:
    work_order_ids = {
        selected.get("selected_work_order_id"),
        selected.get("source_selected_work_order_id"),
        selected.get("linked_l6_10v_selected_work_order_id"),
        selected.get("linked_l6_10u_selected_work_order_id"),
    }
    entry_work_ids = {
        entry.get("linked_work_order_id"),
        entry.get("work_order_id"),
        *(entry.get("work_order_ids", []) if isinstance(entry.get("work_order_ids"), list) else []),
    }
    entry_need_ids = {
        entry.get("linked_evidence_need_id"),
        entry.get("evidence_need_id"),
        *(entry.get("evidence_need_ids", []) if isinstance(entry.get("evidence_need_ids"), list) else []),
    }
    source_type_match = entry.get("source_type") == selected.get("source_type") or (
        selected.get("source_type") in entry.get("source_types", [])
        if isinstance(entry.get("source_types"), list)
        else False
    )
    source_function_match = entry.get("source_function") == selected.get("source_function") or (
        selected.get("source_function") in entry.get("source_functions", [])
        if isinstance(entry.get("source_functions"), list)
        else False
    )
    reviewed = entry.get("reviewed_status") == "reviewed_for_locator_resolution_only"
    locator = entry.get("concrete_locator") or entry.get("locator")
    return (
        bool(locator)
        and url_like(str(locator))
        and reviewed
        and (
            bool(work_order_ids & entry_work_ids)
            or selected.get("linked_evidence_need_id") in entry_need_ids
            or source_type_match
            or source_function_match
        )
    )


def scan_seed_registries(selected: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    registry_paths = [
        "seed_locator_registry/reviewed_seed_locator_registry.json",
        "controlled_locator_resolver_runtime/seed_locator_registry.json",
    ]
    scanned: list[dict[str, Any]] = []
    match: dict[str, Any] | None = None
    for path in registry_paths:
        entries = load_registry_entries(path)
        path_match = next((entry for entry in entries if entry_matches(selected, entry)), None)
        scanned.append(
            {
                "registry_path": path,
                "entries_considered": len(entries),
                "matching_reviewed_locator_found": bool(path_match),
            }
        )
        if path_match and match is None:
            match = path_match
    return (
        {
            "schema_version": SCHEMA_VERSION,
            "scan_id": "l6_10w_existing_seed_registry_scan",
            "selected_work_order_id": selected.get("selected_work_order_id"),
            "scan_scope": "existing_local_seed_registry_files_only",
            "registry_files_scanned": scanned,
            "reviewed_locator_found": bool(match),
            "url_invented": False,
            "facts_inferred_from_seed": False,
        },
        match,
    )


def reviewed_seed_candidate(selected: dict[str, Any], match: dict[str, Any] | None) -> dict[str, Any]:
    locator = match.get("concrete_locator") or match.get("locator") if match else None
    status = "resolved_from_existing_registry" if locator else "user_action_required"
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "l6_10w_reviewed_seed_locator_candidate",
        "status": status,
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_work_order_id": selected.get("source_selected_work_order_id"),
        "source_type": selected.get("source_type"),
        "source_function": selected.get("source_function"),
        "evidence_need_id": selected.get("linked_evidence_need_id"),
        "observation_question": selected.get("observation_question"),
        "concrete_locator": locator,
        "source_title": match.get("source_title") if match else None,
        "source_owner_or_publisher": (
            match.get("source_owner_or_publisher") or match.get("source_owner")
            if match
            else None
        ),
        "reviewed_status": match.get("reviewed_status") if match else "blocked_no_reviewed_locator",
        "facts_inferred_from_seed": False,
        "observation_authorized_by_seed_alone": False,
        "url_invention_authorized": False,
    }


def user_action_request(selected: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": "l6_10w_seed_locator_user_action_required",
        "status": "USER_ACTION_REQUIRED",
        "request_count": 1,
        "requested_item": "one_concrete_public_url",
        "prompt": "Please provide one concrete public URL for the selected work order.",
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "source_selected_work_order_id": selected.get("source_selected_work_order_id"),
        "evidence_need": selected.get("evidence_need"),
        "source_type_needed": selected.get("source_type"),
        "source_function_needed": selected.get("source_function"),
        "observation_question": selected.get("observation_question"),
        "acceptable_source_criteria": [
            "public page",
            "read-only",
            "no login",
            "no payment",
            "no account creation",
            "no form submission",
            "no private/sensitive data",
            "matches the source_type/source_function",
            "can be read as one page/source",
        ],
        "unacceptable_source_criteria": [
            "search results page",
            "login page",
            "checkout/payment page",
            "contact form",
            "private inbox/account page",
            "social posting/commenting surface",
            "page requiring scraping/crawling",
            "broad homepage with no relevant evidence",
        ],
        "paste_url_here": "",
        "optional_source_title": "",
        "optional_source_owner_or_publisher": "",
        "downstream_actions_authorized": False,
    }


def eligibility(selected: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    locator = candidate.get("concrete_locator")
    concrete = url_like(locator)
    checks = {
        "concrete_url_like_locator": concrete,
        "public_read_only_expected": bool(candidate.get("public_read_only_expected", concrete)),
        "no_login_expected": True,
        "no_payment_expected": True,
        "no_form_expected": True,
        "no_contact_expected": True,
        "no_crawling_required": True,
        "no_scraping_required": True,
        "no_mcp_required": True,
        "source_type_matches_work_order": candidate.get("source_type") == selected.get("source_type"),
        "one_page_observation_plausible": concrete,
    }
    failed = [key for key, value in checks.items() if value is not True]
    return {
        "schema_version": SCHEMA_VERSION,
        "eligibility_id": "l6_10w_seed_locator_eligibility_result",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "concrete_locator": locator,
        **checks,
        "locator_eligible_for_tiny_retry": concrete and not failed,
        "failed_checks": failed,
        "blocked_reason": None if concrete and not failed else "user_action_required_no_seed_locator",
    }


def retry_outputs(
    selected: dict[str, Any],
    candidate: dict[str, Any],
    eligibility_result: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    locator = candidate.get("concrete_locator")
    has_locator = bool(locator)
    retry_attempted = has_locator
    observation_executed = False
    reason = (
        "user_action_required_no_seed_locator"
        if not has_locator
        else "seed_locator_resolved_but_observation_blocked"
    )
    trace = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": "l6_10w_tiny_seed_observation_trace",
        "observation_executed": observation_executed,
        "reason": reason,
        "source_locator": locator,
        "network_used": False,
        "external_reads_count": 0,
        "pages_read_count": 0,
        "login_encountered": False,
        "payment_encountered": False,
        "form_encountered": False,
        "private_data_encountered": False,
        "raw_content_storage_policy": "no_raw_page_dump_stored",
    }
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "evidence_packet_id": "l6_10w_tiny_seed_evidence_packet",
        "linked_work_order_id": selected.get("selected_work_order_id"),
        "source_locator": locator,
        "source_title": candidate.get("source_title"),
        "source_publisher_or_owner": candidate.get("source_owner_or_publisher"),
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
        "request": {
            "schema_version": SCHEMA_VERSION,
            "request_id": "l6_10w_seed_locator_retry_request",
            "linked_work_order_id": selected.get("selected_work_order_id"),
            "concrete_locator": locator,
            "retry_attempted": retry_attempted,
            "reason": None if retry_attempted else reason,
            "max_pages_read": 1,
            "max_total_external_reads": 1,
        },
        "trace": {
            "schema_version": SCHEMA_VERSION,
            "trace_id": "l6_10w_seed_locator_retry_trace",
            "retry_attempted": retry_attempted,
            "locator_eligibility_checked": retry_attempted,
            "observation_executed": observation_executed,
            "reason": reason,
            "eligibility_result_ref": eligibility_result.get("eligibility_id"),
        },
        "observation_trace": trace,
        "evidence": evidence,
        "claim_boundary": {
            "schema_version": SCHEMA_VERSION,
            "assessment_id": "l6_10w_tiny_seed_claim_boundary_assessment",
            "linked_evidence_packet_id": evidence["evidence_packet_id"],
            "bounded_claims": [],
            "unsupported_inferences": ["no live source evidence captured"],
            "freshness_status": "not_observed",
            "semantic_truth_scoring_used": False,
            "llm_confidence_used_as_authority": False,
            "external_use_authorized": False,
        },
        "review": {
            "schema_version": SCHEMA_VERSION,
            "review_packet_id": "l6_10w_tiny_seed_post_observation_review_packet",
            "linked_evidence_packet_id": evidence["evidence_packet_id"],
            "current_decision": "review_pending_blocked_no_live_evidence",
            "approve_for_external_use": False,
            "applied": False,
        },
        "refinement": {
            "schema_version": SCHEMA_VERSION,
            "refinement_candidate_id": "l6_10w_tiny_seed_refinement_candidate",
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
            "receipt_set_id": "l6_10w_tiny_seed_no_action_receipts",
            "receipts": [
                {
                    "action_type": action,
                    "authorized_in_l6_10w": False,
                    "executed_in_l6_10w": False,
                }
                for action in NO_ACTIONS
            ],
        },
    }


def build() -> list[str]:
    generated: list[str] = []
    selected = select_work_order()
    scan, match = scan_seed_registries(selected)
    candidate = reviewed_seed_candidate(selected, match)
    user_action = user_action_request(selected)
    eligibility_result = eligibility(selected, candidate)
    retry = retry_outputs(selected, candidate, eligibility_result)

    locator_found = candidate["status"] == "resolved_from_existing_registry"
    user_action_required = not locator_found
    remaining_blocker = (
        "user_must_provide_one_reviewed_seed_locator_url"
        if user_action_required
        else retry["trace"]["reason"]
    )

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
        "reviewed_seed_locator_found": locator_found,
        "concrete_locator": candidate.get("concrete_locator"),
        "user_action_required_generated": user_action_required,
        "retry_attempted": retry["trace"]["retry_attempted"],
        "tiny_read_only_observation_executed": retry["observation_trace"]["observation_executed"],
        "external_reads_count": retry["observation_trace"]["external_reads_count"],
        "pages_read_count": retry["observation_trace"]["pages_read_count"],
        "evidence_packet_generated": True,
        "remaining_blocker": remaining_blocker,
    }

    write_text(
        "l6_reviewed_seed_locator_injection_tiny_retry/README.md",
        f"""# {MILESTONE_ID} {MILESTONE_NAME}

L6.10W narrows the locator blocker: it either uses one existing reviewed seed
locator from local registry artifacts or emits a precise `USER_ACTION_REQUIRED`
packet asking for exactly one public URL tied to the selected work order.
""",
        generated,
    )
    write_json("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_milestone_contract.json", contract, generated)
    write_json("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_scope.json", {
        "schema_version": SCHEMA_VERSION,
        "scope_id": "l6_10w_scope",
        "outcomes": ["reviewed_seed_locator_exists", "user_action_required", "locator_exists_but_observation_blocked"],
        "do_not_invent_urls": True,
        "do_not_search_web_without_enabled_backend": True,
        "downstream_actions_blocked": True,
    }, generated)
    write_json("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_runtime_limits.json", RUNTIME_LIMITS, generated)
    write_json("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_safety_flags.json", SAFETY_FLAGS, generated)
    write_json("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_summary.json", summary, generated)
    write_text("l6_reviewed_seed_locator_injection_tiny_retry/l6_10w_summary.md", f"""# L6.10W Summary

- selected work order: {selected.get('selected_work_order_id')}
- reviewed seed locator found: {locator_found}
- user action required generated: {user_action_required}
- tiny read-only observation executed: {retry['observation_trace']['observation_executed']}
- remaining blocker: {remaining_blocker}
""", generated)

    write_json("reviewed_seed_locator_injection/selected_work_order_for_seed_injection.json", selected, generated)
    write_json("reviewed_seed_locator_injection/seed_locator_injection_schema.json", {
        "schema_version": SCHEMA_VERSION,
        "schema_id": "l6_10w_seed_locator_injection_schema",
        "required_fields": [
            "linked_work_order_id",
            "source_type",
            "source_function",
            "evidence_need_id",
            "observation_question",
            "concrete_locator",
            "source_title",
            "source_owner_or_publisher",
            "reviewed_status",
            "facts_inferred_from_seed",
            "observation_authorized_by_seed_alone",
        ],
        "max_seed_locators_injected": 1,
        "url_invention_authorized": False,
    }, generated)
    write_json("reviewed_seed_locator_injection/existing_seed_registry_scan.json", scan, generated)
    write_json("reviewed_seed_locator_injection/reviewed_seed_locator_candidate.json", candidate, generated)
    write_json("reviewed_seed_locator_injection/reviewed_seed_locator_injection_decision.json", {
        "schema_version": SCHEMA_VERSION,
        "decision_id": "l6_10w_reviewed_seed_locator_injection_decision",
        "decision": "use_reviewed_seed_locator" if locator_found else "generate_user_action_required",
        "reviewed_seed_locator_found": locator_found,
        "url_invented": False,
        "fake_locator_generated": False,
        "observation_authorized_by_seed_alone": False,
    }, generated)
    write_text("reviewed_seed_locator_injection/reviewed_seed_locator_injection_report.md", f"# Reviewed Seed Locator Injection Report\n\nDecision: `{candidate['status']}`.", generated)

    write_text("seed_locator_user_action_request/USER_ACTION_REQUIRED.md", f"""# USER_ACTION_REQUIRED

Please provide one concrete public URL for the selected work order.

Selected work order: `{selected.get('selected_work_order_id')}`
Source work order: `{selected.get('source_selected_work_order_id')}`
Evidence need: `{selected.get('evidence_need')}`
Source type needed: `{selected.get('source_type')}`
Source function needed: `{selected.get('source_function')}`
Observation question: `{selected.get('observation_question')}`

Paste exactly one URL here:

`paste_url_here:`

Acceptable: public, read-only, no login, no payment, no account creation, no
form submission, no private/sensitive data, matches the requested source type,
and can be read as one page/source.

Unacceptable: search results page, login page, checkout/payment page, contact
form, private inbox/account page, social posting/commenting surface, page
requiring scraping/crawling, or broad homepage with no relevant evidence.
""", generated)
    write_json("seed_locator_user_action_request/user_action_required.json", user_action, generated)
    write_json("seed_locator_user_action_request/seed_locator_request_packet.json", {
        "schema_version": SCHEMA_VERSION,
        "packet_id": "l6_10w_seed_locator_request_packet",
        "request_ref": user_action["request_id"],
        "exactly_one_url_requested": True,
        "user_supplied_url_required": user_action_required,
        "agent_may_not_invent_url": True,
    }, generated)
    write_json("seed_locator_user_action_request/seed_locator_submission_template.json", {
        "schema_version": SCHEMA_VERSION,
        "template_id": "l6_10w_seed_locator_submission_template",
        "paste_url_here": "",
        "optional_source_title": "",
        "optional_source_owner_or_publisher": "",
        "attestation": "I am providing one public read-only URL for locator resolution only.",
    }, generated)
    write_text("seed_locator_user_action_request/seed_locator_user_action_report.md", "# Seed Locator User Action Report\n\nGenerated a precise request for exactly one concrete public URL.", generated)

    write_json("seed_locator_retry_attempt/seed_locator_retry_request.json", retry["request"], generated)
    write_json("seed_locator_retry_attempt/seed_locator_retry_trace.json", retry["trace"], generated)
    write_json("seed_locator_retry_attempt/seed_locator_eligibility_result.json", eligibility_result, generated)
    write_text("seed_locator_retry_attempt/seed_locator_retry_report.md", f"# Seed Locator Retry Report\n\nRetry attempted: `{retry['trace']['retry_attempted']}`. Reason: `{retry['trace']['reason']}`.", generated)

    write_json("seed_locator_retry_result/tiny_seed_observation_trace.json", retry["observation_trace"], generated)
    write_json("seed_locator_retry_result/tiny_seed_evidence_packet.json", retry["evidence"], generated)
    write_json("seed_locator_retry_result/tiny_seed_claim_boundary_assessment.json", retry["claim_boundary"], generated)
    write_json("seed_locator_retry_result/tiny_seed_post_observation_review_packet.json", retry["review"], generated)
    write_json("seed_locator_retry_result/tiny_seed_refinement_candidate.json", retry["refinement"], generated)
    write_json("seed_locator_retry_result/tiny_seed_no_action_receipts.json", retry["receipts"], generated)
    write_text("seed_locator_retry_result/seed_locator_retry_result_report.md", "# Seed Locator Retry Result\n\nNo observation executed because no reviewed seed locator was available.", generated)

    cieu = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_10w_reviewed_seed_locator_injection_tiny_retry_fixture",
        "X_t": {"prior_blocker": "no_enabled_locator_resolution_path"},
        "U_t": "Narrow the blocker to either one reviewed seed locator or a precise one-URL user action request.",
        "Y_star_t": "Use at most one reviewed seed locator or ask the user for exactly one URL, optionally retry one tiny read-only observation, and preserve all no-action/no-writeback/no-mutation constraints.",
        "Y_t_plus_1": {
            "reviewed_seed_locator_found": locator_found,
            "user_action_required_generated": user_action_required,
            "tiny_read_only_observation_executed": retry["observation_trace"]["observation_executed"],
        },
        "R_t_plus_1": [remaining_blocker, "L6.11 remains blocked until one reviewed locator and successful tiny observation exist"],
    }
    meta = {
        "schema_version": SCHEMA_VERSION,
        "meta_learning_candidate_id": "l6_10w_meta_learning_update_candidate",
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
        "l6_10w_reviewed_seed_locator_injection_tiny_retry_complete": True,
        "selected_work_order_id": selected.get("selected_work_order_id"),
        "reviewed_seed_locator_found": locator_found,
        "concrete_locator": candidate.get("concrete_locator"),
        "user_action_required_generated": user_action_required,
        "tiny_read_only_observation_executed": retry["observation_trace"]["observation_executed"],
        "ready_for_l6_11_controlled_multi_source_corroboration": False,
        "next_step": "user_must_provide_one_reviewed_seed_locator_url" if user_action_required else "resolve_observation_eligibility_runtime_blocker",
        "remaining_blocker": remaining_blocker,
        "next_recommended_milestone": "L6.10X User-Supplied Reviewed Seed Locator Intake v0" if user_action_required else "L6.10W-R Tiny Observation Eligibility Retry v0",
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
        "primary_blocker": remaining_blocker,
        "blockers": [remaining_blocker],
        "user_action_required": user_action_required,
        "exact_request": "Please provide one concrete public URL for the selected work order." if user_action_required else None,
    }
    recommendation = {
        "schema_version": SCHEMA_VERSION,
        "next_milestone": readiness["next_recommended_milestone"],
        "l6_11_blocked": not readiness["ready_for_l6_11_controlled_multi_source_corroboration"],
        "reason": "A reviewed locator is still missing." if user_action_required else "A locator exists but observation did not complete.",
    }
    read_model_summary = {
        "schema_name": "ystar.console_read_model.l6_10w_read_model_summary",
        "schema_version": SCHEMA_VERSION,
        **summary,
    }
    write_json("l6_10w_read_model/l6_10w_cieu_like_fixture.json", cieu, generated)
    write_json("l6_10w_read_model/l6_10w_strategic_residual_delta.json", {
        "schema_version": SCHEMA_VERSION,
        "residual_id": "l6_10w_strategic_residual_delta",
        "remaining_blocker": remaining_blocker,
        "user_action_required_generated": user_action_required,
    }, generated)
    write_json("l6_10w_read_model/l6_10w_meta_learning_update_candidate.json", meta, generated)
    write_json("l6_10w_read_model/l6_10w_readiness_assessment.json", readiness, generated)
    write_json("l6_10w_read_model/l6_10w_blockers.json", blockers, generated)
    write_json("l6_10w_read_model/l6_10w_next_milestone_recommendation.json", recommendation, generated)
    write_json("l6_10w_read_model/l6_10w_read_model_summary.json", read_model_summary, generated)
    write_text("l6_10w_read_model/l6_10w_report.md", f"# L6.10W Report\n\nRemaining blocker: `{remaining_blocker}`.", generated)
    return generated


if __name__ == "__main__":
    paths = build()
    print(f"generated {len(paths)} L6.10W files")
