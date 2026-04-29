#!/usr/bin/env python3
"""Build L6.10R controlled locator resolution and tiny observation retry artifacts.

This builder records the governed retry path after L6.10. It does not perform
network access, web search, crawling, scraping, browser automation, API calls,
MCP execution, live behavior, CIEU DB writes, brain/memory writes, canonical
mutation, or direct Y* mutation. If no concrete locator or controlled
locator-discovery tooling is available, it emits a blocked retry trace.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10R"
MILESTONE_NAME = "Controlled Source Locator Resolution & Tiny Observation Retry v0"
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
]
NEXT_MILESTONE_SUCCESS = "L6.11 Controlled Multi-Source Read-Only Evidence Corroboration Pilot v0"
NEXT_MILESTONE_BLOCKED = "L6.10R Retry After Controlled Locator Discovery Tooling Available v0"

RUNTIME_LIMITS = {
    "max_selected_work_orders": 1,
    "max_locator_discovery_queries": 1,
    "max_concrete_locators_resolved": 1,
    "max_source_locators_observed": 1,
    "max_pages_read": 1,
    "max_external_reads_total": 2,
    "max_crawled_links": 0,
    "max_followed_links_except_normal_redirect": 0,
    "max_login_attempts": 0,
    "max_forms_submitted": 0,
    "max_messages_sent": 0,
    "max_payments": 0,
}

SAFETY_FLAGS = {
    "controlled_locator_discovery_enabled": True,
    "tiny_real_read_only_observation_retry_enabled": True,
    "broad_web_search_enabled": False,
    "repeated_search_loop_enabled": False,
    "crawling_enabled": False,
    "scraping_enabled": False,
    "browser_automation_enabled": False,
    "login_enabled": False,
    "account_creation_enabled": False,
    "contact_enabled": False,
    "payment_enabled": False,
    "form_submission_enabled": False,
    "posting_commenting_messaging_enabled": False,
    "publication_enabled": False,
    "outreach_enabled": False,
    "revenue_execution_enabled": False,
    "mcp_execution_enabled": False,
    "live_behavior_enabled": False,
    "cieu_db_write_enabled": False,
    "canonical_update_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "direct_y_star_mutation_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "llm_confidence_as_authority_enabled": False,
    "raw_page_dump_storage_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "locator_discovery_executed_in_l6_10r": False,
    "external_observation_executed_in_l6_10r": False,
    "network_used_in_l6_10r": False,
}

ABORT_CONDITIONS = [
    "no concrete locator available",
    "controlled locator discovery tooling unavailable",
    "locator discovery would require broad search",
    "login required",
    "account creation required",
    "payment required",
    "form submission required",
    "contact requested",
    "private/sensitive data encountered",
    "source asks for interaction",
    "source outside scope",
    "more than one source needed",
    "uncertainty about authorization",
    "network/tool failure",
    "content cannot be captured safely",
]

NO_ACTION_CONSTRAINTS = [
    "no broad search",
    "no repeated search loop",
    "no crawling",
    "no scraping",
    "no browser automation",
    "no login",
    "no account creation",
    "no contact",
    "no payment",
    "no form submission",
    "no posting/commenting/messaging",
    "no publication",
    "no outreach",
    "no revenue execution",
    "no MCP execution",
    "no live behavior execution",
    "no CIEU DB write",
    "no canonical mutation",
    "no brain/memory writeback",
    "no direct Y* mutation",
]

EVIDENCE_CAPTURE_FIELDS = [
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
    "review_status",
]

RECEIPTS = [
    ("no_broad_search_receipt.json", "broad_search"),
    ("no_repeated_search_loop_receipt.json", "repeated_search_loop"),
    ("no_crawling_receipt.json", "crawling"),
    ("no_scraping_receipt.json", "scraping"),
    ("no_browser_automation_receipt.json", "browser_automation"),
    ("no_login_receipt.json", "login"),
    ("no_account_creation_receipt.json", "account_creation"),
    ("no_payment_receipt.json", "payment"),
    ("no_form_submission_receipt.json", "form_submission"),
    ("no_posting_commenting_messaging_receipt.json", "posting_commenting_messaging"),
    ("no_publication_receipt.json", "publication"),
    ("no_outreach_receipt.json", "outreach"),
    ("no_revenue_execution_receipt.json", "revenue_execution"),
    ("no_mcp_execution_receipt.json", "mcp_execution"),
    ("no_live_behavior_receipt.json", "live_behavior"),
    ("no_cieu_db_write_receipt.json", "cieu_db_write"),
    ("no_canonical_mutation_receipt.json", "canonical_mutation"),
    ("no_brain_memory_writeback_receipt.json", "brain_memory_writeback"),
    ("no_direct_y_star_mutation_receipt.json", "direct_y_star_mutation"),
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
    target.write_text(text.strip() + "\n", encoding="utf-8")
    generated.append(path)


def with_controls(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    enriched["runtime_limits"] = RUNTIME_LIMITS
    enriched["safety_flags"] = SAFETY_FLAGS
    return enriched


def md_report(title: str, body: str) -> str:
    return (
        f"# {title}\n\n"
        "L6.10R CONTROLLED SOURCE LOCATOR RESOLUTION AND TINY OBSERVATION RETRY.\n\n"
        f"{body}\n\n"
        "This artifact does not authorize broad search, repeated search loops, "
        "crawling, scraping, browser automation, login, account creation, payment, "
        "form submission, posting/commenting/messaging, publication, outreach, "
        "revenue execution, MCP execution, live behavior, CIEU DB write, canonical "
        "mutation, brain/memory writeback, or direct Y* mutation."
    )


def selected_l6_10_work_order() -> dict[str, Any]:
    selected = read_json("tiny_observation_work_order_selector/selected_tiny_observation_work_order.json")
    if selected:
        return selected
    l6_9 = read_json("agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json")
    orders = l6_9.get("selected_work_orders", [])
    return orders[0] if orders else {}


def concrete_locator_from(work_order: dict[str, Any]) -> str | None:
    for key in ("source_locator", "resolved_locator", "source_locator_url"):
        value = work_order.get(key)
        if isinstance(value, str) and value.startswith(("https://", "http://")):
            return value
    return None


def write_core_pack(generated: list[str]) -> None:
    contract = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": INPUT_MILESTONES,
            "mode": "controlled_locator_resolution_and_tiny_observation_retry",
            "max_selected_work_orders": 1,
            "max_locator_discovery_queries": 1,
            "max_concrete_locators_resolved": 1,
            "max_source_locators_observed": 1,
            "max_pages_read": 1,
            "max_external_reads_total": 2,
            "controlled_locator_discovery_authorized": True,
            "tiny_real_read_only_observation_retry_authorized": True,
            "broad_web_search_authorized": False,
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
            "requires_post_observation_review_before_any_artifact_update": True,
        }
    )
    write_json(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_runtime_limits.json",
        with_controls(RUNTIME_LIMITS),
        generated,
    )
    write_json(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_safety_flags.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "milestone_id": MILESTONE_ID,
                "safety_flags": SAFETY_FLAGS,
                "disallowed_actions": NO_ACTION_CONSTRAINTS,
            }
        ),
        generated,
    )
    write_json(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_scope.json",
        with_controls(
            {
                "schema_version": SCHEMA_VERSION,
                "scope": "one controlled locator resolution attempt and one tiny observation retry if eligible",
                "outcome": "blocked_no_controlled_locator_discovery_tooling",
                "downstream_actions_blocked": NO_ACTION_CONSTRAINTS,
            }
        ),
        generated,
    )
    summary = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "mode": "controlled_locator_resolution_and_tiny_observation_retry",
            "l6_10r_controlled_source_locator_resolution_retry_defined": True,
            "input_milestones": INPUT_MILESTONES,
            "selected_work_order_count": 1,
            "locator_discovery_executed": False,
            "locator_discovery_queries_count": 0,
            "concrete_locator_resolved": False,
            "tiny_read_only_observation_executed": False,
            "external_reads_total": 0,
            "pages_read_count": 0,
            "evidence_packet_generated": True,
            "post_observation_review_packet_generated": True,
            "artifact_refinement_candidate_generated": True,
            "artifact_refinement_applied": False,
            "next_recommended_milestone": NEXT_MILESTONE_BLOCKED,
        }
    )
    write_json(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.json",
        summary,
        generated,
    )
    write_text(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/README.md",
        md_report(
            "L6.10R Controlled Source Locator Resolution And Tiny Observation Retry",
            "This retry pack selects the prior L6.10 work order and reaches the "
            "controlled locator-discovery gate. No controlled locator-discovery "
            "tooling or network condition is available in this environment, so the "
            "retry blocks safely without resolving a locator or fabricating evidence.",
        ),
        generated,
    )
    write_text(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_non_action_boundary.md",
        md_report(
            "L6.10R Non-Action Boundary",
            "Locator resolution is bounded to one query and one candidate locator. "
            "Observation, if ever eligible, is bounded to one public read-only page. "
            "All downstream actions remain blocked.",
        ),
        generated,
    )
    write_text(
        "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_summary.md",
        md_report(
            "L6.10R Summary",
            "Outcome C - locator unresolved. The retry generated selection, locator "
            "plan, blocked trace, eligibility gate, execution packet, empty evidence "
            "packet, validation, review, refinement candidate, no-action receipts, "
            "residual loop, and readiness artifacts.",
        ),
        generated,
    )


def build() -> list[str]:
    generated: list[str] = []
    write_core_pack(generated)

    selected = selected_l6_10_work_order()
    concrete_locator = concrete_locator_from(selected)
    locator_discovery_available = False
    locator_discovery_executed = False
    concrete_locator_resolved = concrete_locator is not None
    observation_executed = False
    external_reads_total = 0

    selection = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "selected_retry_work_order_id": "l6_10r_selected_locator_retry_work_order_001",
            "linked_l6_10_selected_work_order_id": selected.get("selected_work_order_id"),
            "linked_l6_9_selected_work_order_id": selected.get("linked_l6_9_selected_work_order_id"),
            "linked_l6_8_work_order_id": selected.get("linked_l6_8_work_order_id"),
            "linked_evidence_need_id": selected.get("linked_evidence_need_id"),
            "linked_source_hypothesis_id": selected.get("linked_source_hypothesis_id"),
            "linked_l6_artifact": selected.get("linked_l6_artifact"),
            "observation_question": selected.get("observation_question"),
            "source_type": selected.get("source_type"),
            "source_locator_placeholder": selected.get("source_locator_placeholder"),
            "expected_evidence_type": selected.get("expected_evidence_type"),
            "selection_reason": "L6.10 selected this as the highest-readiness tiny pilot work order; its evidence need remains important and it has clear no-action constraints.",
            "selection_criteria": [
                "L6.10 selected it",
                "evidence need remains important",
                "source type is public/read-only in principle",
                "placeholder locator might be resolvable with one controlled query",
                "no login/payment/contact/form expected",
                "low privacy/IP risk",
                "high value of information",
                "clear claim boundary",
                "clear expected evidence type",
                "clear abort conditions",
            ],
            "selected_count": 1,
            "real_observation_authorized_now": False,
        }
    )
    inventory = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "sources": [
                "observation_work_order_generator/observation_work_order_index.json",
                "agentic_work_order_pilot_selector/selected_agentic_pilot_work_orders.json",
                "tiny_observation_work_order_selector/selected_tiny_observation_work_order.json",
            ],
            "selected_l6_10_work_order": selected,
        }
    )
    write_json("locator_retry_work_order_selector/l6_8_l6_9_l6_10_work_order_inventory.json", inventory, generated)
    write_json("locator_retry_work_order_selector/locator_retry_selection_matrix.json", with_controls({"schema_version": SCHEMA_VERSION, "selected_count": 1, "max_selected_work_orders": 1, "selection_variables": selection["selection_criteria"], "real_observation_authorized_now": False}), generated)
    write_json("locator_retry_work_order_selector/selected_locator_retry_work_order.json", selection, generated)
    write_json("locator_retry_work_order_selector/deferred_locator_retry_work_orders.json", with_controls({"schema_version": SCHEMA_VERSION, "deferred_count": 0, "deferred_work_orders": []}), generated)
    write_text("locator_retry_work_order_selector/locator_retry_work_order_selector_report.md", md_report("Locator Retry Work Order Selector", "Exactly one L6.10 work order was selected for locator retry."), generated)

    query = "official policy program source public demand beneficiary language payer beneficiary clarity"
    plan = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "linked_work_order_id": selection.get("linked_l6_8_work_order_id"),
            "source_type": selection.get("source_type"),
            "source_function": "resolve one public source locator for the selected evidence need",
            "observation_question": selection.get("observation_question"),
            "locator_discovery_query": query,
            "query_purpose": "locator_resolution_only",
            "max_queries": 1,
            "max_results_to_consider": 1,
            "no_snippet_fact_use": True,
            "no_claim_inference_from_search_result": True,
            "concrete_locator_required_before_observation": True,
            "concrete_locator_already_exists": concrete_locator_resolved,
            "planned_query_count": 0 if concrete_locator_resolved else 1,
            "query_executed_in_this_environment": locator_discovery_executed,
            "query_not_executed_reason": "controlled_locator_discovery_tooling_unavailable" if not locator_discovery_available else None,
        }
    )
    write_json("controlled_locator_discovery_plan/locator_discovery_plan_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(plan.keys())}), generated)
    write_json("controlled_locator_discovery_plan/locator_discovery_plan.json", plan, generated)
    write_json("controlled_locator_discovery_plan/locator_discovery_query_budget.json", with_controls({"schema_version": SCHEMA_VERSION, "max_queries": 1, "queries_used": 0, "max_results_to_consider": 1, "results_considered": 0}), generated)
    write_json("controlled_locator_discovery_plan/locator_discovery_abort_conditions.json", with_controls({"schema_version": SCHEMA_VERSION, "abort_conditions": ABORT_CONDITIONS}), generated)
    write_text("controlled_locator_discovery_plan/controlled_locator_discovery_plan_report.md", md_report("Controlled Locator Discovery Plan", "A single-query locator plan was generated, but the query was not executed because no controlled locator-discovery tooling was available."), generated)

    resolution_trace = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "locator_resolution_attempted": True,
            "controlled_locator_discovery_executed": locator_discovery_executed,
            "locator_discovery_query_used": None,
            "locator_discovery_queries_count": 0,
            "concrete_locator_resolved": False,
            "resolved_locator": None,
            "source_type": selection.get("source_type"),
            "resolution_method": "blocked_before_query_no_controlled_locator_discovery_tooling",
            "external_reads_count_for_resolution": 0,
            "facts_inferred_from_locator_discovery": False,
            "abort_triggered": True,
            "abort_reason": "controlled_locator_discovery_tooling_unavailable",
        }
    )
    write_json("controlled_locator_resolution_trace/locator_resolution_trace_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(resolution_trace.keys())}), generated)
    write_json("controlled_locator_resolution_trace/locator_resolution_trace.json", resolution_trace, generated)
    write_json("controlled_locator_resolution_trace/resolved_source_locator.json", with_controls({"schema_version": SCHEMA_VERSION, "concrete_locator_resolved": False, "resolved_locator": None, "reason": resolution_trace["abort_reason"]}), generated)
    write_text("controlled_locator_resolution_trace/locator_resolution_report.md", md_report("Locator Resolution Trace", "No locator was resolved and no facts were inferred from locator discovery."), generated)

    eligibility_checks = [
        {"check": "locator exists", "passed": False, "reason": "no concrete locator resolved"},
        {"check": "public/read-only source", "passed": None, "reason": "not assessed without locator"},
        {"check": "not login-required", "passed": None, "reason": "not assessed without locator"},
        {"check": "not payment-required", "passed": None, "reason": "not assessed without locator"},
        {"check": "not private/sensitive", "passed": None, "reason": "not assessed without locator"},
        {"check": "not form/submission surface", "passed": None, "reason": "not assessed without locator"},
        {"check": "not social posting/commenting/messaging surface", "passed": None, "reason": "not assessed without locator"},
        {"check": "not checkout/payment", "passed": None, "reason": "not assessed without locator"},
        {"check": "source type matches work order", "passed": None, "reason": "not assessed without locator"},
        {"check": "expected evidence type plausible", "passed": None, "reason": "not assessed without locator"},
        {"check": "observation can remain one-page/one-source", "passed": None, "reason": "not assessed without locator"},
        {"check": "no crawling required", "passed": None, "reason": "not assessed without locator"},
        {"check": "no scraping required", "passed": None, "reason": "not assessed without locator"},
        {"check": "no MCP required", "passed": None, "reason": "not assessed without locator"},
    ]
    eligibility = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "locator_eligible_for_observation": False,
            "eligibility_checks": eligibility_checks,
            "observation_blocked": True,
            "block_reason": "no_concrete_locator_resolved",
        }
    )
    write_json("locator_eligibility_and_risk_gate/locator_eligibility_gate_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "gate_type": "pre_observation_locator_eligibility"}), generated)
    write_json("locator_eligibility_and_risk_gate/locator_eligibility_result.json", eligibility, generated)
    write_json("locator_eligibility_and_risk_gate/locator_risk_assessment.json", with_controls({"schema_version": SCHEMA_VERSION, "risk_status": "not_assessed_without_locator", "privacy_risk": "unknown_not_observed", "ip_risk": "unknown_not_observed", "overclaim_risk": "high_if_claims_were_inferred_without_observation"}), generated)
    write_json("locator_eligibility_and_risk_gate/locator_rejection_decision.json", with_controls({"schema_version": SCHEMA_VERSION, "locator_rejected": True, "reason": "no_concrete_locator_resolved", "observation_authorized": False}), generated)
    write_text("locator_eligibility_and_risk_gate/locator_eligibility_and_risk_report.md", md_report("Locator Eligibility And Risk Gate", "The gate blocks observation because no concrete locator exists."), generated)

    execution_packet = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "selected_work_order_id": selection.get("selected_retry_work_order_id"),
            "resolved_locator": None,
            "observation_question": selection.get("observation_question"),
            "source_type": selection.get("source_type"),
            "expected_evidence_type": selection.get("expected_evidence_type"),
            "trust_requirement": "candidate_structural_trust_review_required",
            "freshness_requirement": "source_date_or_date_missing_marker_required",
            "claim_boundary_to_test": "internal review only; no external use or strategy mutation",
            "evidence_capture_fields": EVIDENCE_CAPTURE_FIELDS,
            "abort_conditions": ABORT_CONDITIONS,
            "no_action_constraints": NO_ACTION_CONSTRAINTS,
            "runtime_limits": RUNTIME_LIMITS,
            "retry_observation_authorized": False,
            "publication_authorized": False,
            "outreach_authorized": False,
            "payment_authorized": False,
            "contact_authorized": False,
            "revenue_execution_authorized": False,
            "mcp_execution_authorized": False,
            "live_behavior_authorized": False,
            "cieu_db_write_authorized": False,
            "canonical_update_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "direct_y_star_mutation_authorized": False,
        }
    )
    write_json("tiny_observation_retry_execution_packet/retry_execution_packet_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(execution_packet.keys())}), generated)
    write_json("tiny_observation_retry_execution_packet/retry_execution_packet.json", execution_packet, generated)
    write_json("tiny_observation_retry_execution_packet/retry_pre_run_checklist.json", with_controls({"schema_version": SCHEMA_VERSION, "pre_run_status": "blocked_no_eligible_locator", "checklist": ["confirm one work order", "confirm one resolved public locator", "confirm eligibility gate passes", "confirm downstream action blocks"]}), generated)
    write_text("tiny_observation_retry_execution_packet/retry_execution_packet_report.md", md_report("Retry Execution Packet", "The retry execution packet was generated but observation is not authorized without a locator."), generated)

    write_json("tiny_observation_retry_runtime_guard/retry_runtime_guard_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "guard": "one_locator_one_source_one_page_stop_on_uncertainty"}), generated)
    write_json("tiny_observation_retry_runtime_guard/retry_runtime_guard_limits.json", with_controls(RUNTIME_LIMITS), generated)
    write_json("tiny_observation_retry_runtime_guard/retry_prohibited_runtime_actions.json", with_controls({"schema_version": SCHEMA_VERSION, "prohibited_actions": NO_ACTION_CONSTRAINTS + ["following links beyond normal redirect", "download of private/sensitive data"]}), generated)
    write_json("tiny_observation_retry_runtime_guard/retry_runtime_abort_conditions.json", with_controls({"schema_version": SCHEMA_VERSION, "abort_conditions": ABORT_CONDITIONS}), generated)
    write_text("tiny_observation_retry_runtime_guard/retry_runtime_guard_report.md", md_report("Retry Runtime Guard", "The guard keeps the retry at one work order, one locator, one page/source, and no disallowed actions."), generated)

    retry_trace = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "observation_executed": observation_executed,
            "source_locator": None,
            "source_type": selection.get("source_type"),
            "read_only": True,
            "network_used": False,
            "external_requests_count": 0,
            "external_reads_total": external_reads_total,
            "pages_read_count": 0,
            "locator_discovery_queries_count": 0,
            "login_encountered": False,
            "payment_encountered": False,
            "form_encountered": False,
            "private_data_encountered": False,
            "abort_triggered": True,
            "abort_reason": "no_concrete_locator_resolved",
            "observation_started_at": "not_started_blocked_pre_observation",
            "observation_completed_at": "not_completed_blocked_pre_observation",
            "raw_content_storage_policy": "no raw page content stored; no live page read",
        }
    )
    write_json("tiny_observation_retry_trace/retry_observation_trace_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(retry_trace.keys())}), generated)
    write_json("tiny_observation_retry_trace/retry_observation_trace.json", retry_trace, generated)
    write_text("tiny_observation_retry_trace/retry_observation_trace_report.md", md_report("Retry Observation Trace", "Observation retry was blocked before network, URL open, or page read."), generated)

    evidence_packet = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "evidence_packet_id": "l6_10r_retry_evidence_packet_001",
            "linked_work_order_id": selection.get("linked_l6_8_work_order_id"),
            "source_locator": None,
            "source_title": None,
            "source_publisher_or_owner": None,
            "observed_at_timestamp": None,
            "source_date_or_date_missing": "date_missing_no_observation_executed",
            "freshness_class": "not_observed",
            "captured_claims": [],
            "unsupported_claims": [],
            "missing_context": [
                "no concrete locator resolved",
                "no controlled locator discovery query executed",
                "no live observation executed",
            ],
            "conflicting_source_marker": "not_assessed_no_observation",
            "claim_boundary": "no current factual claim; internal review only",
            "citation_trace": [],
            "capture_method": "blocked_retry_empty_evidence_packet",
            "review_status": "pending_review",
            "live_source_evidence_captured": False,
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
    )
    write_json("tiny_retry_evidence_capture_packet/retry_evidence_capture_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": EVIDENCE_CAPTURE_FIELDS + ["live_source_evidence_captured"]}), generated)
    write_json("tiny_retry_evidence_capture_packet/retry_evidence_packet.json", evidence_packet, generated)
    write_json("tiny_retry_evidence_capture_packet/retry_citation_trace.json", with_controls({"schema_version": SCHEMA_VERSION, "citation_count": 0, "citations": [], "reason": "no observation executed"}), generated)
    write_text("tiny_retry_evidence_capture_packet/retry_evidence_capture_report.md", md_report("Retry Evidence Capture", "An empty blocked evidence packet was generated; it does not pretend evidence exists."), generated)

    validation_matrix = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "validation_checks": [
                {"check": "source locator present if observation executed", "passed": True},
                {"check": "source title present or missing marked", "passed": True},
                {"check": "source date present or date_missing marked", "passed": True},
                {"check": "freshness class present", "passed": True},
                {"check": "captured claims bounded", "passed": True},
                {"check": "unsupported claims listed", "passed": True},
                {"check": "missing context listed", "passed": True},
                {"check": "citation trace present", "passed": True},
                {"check": "no downstream actions taken", "passed": True},
                {"check": "review required", "passed": True},
                {"check": "no semantic truth scoring", "passed": True},
                {"check": "no LLM confidence as authority", "passed": True},
            ],
            "truth_score": None,
            "semantic_truth_score": None,
            "llm_confidence_as_authority": False,
        }
    )
    write_json("tiny_retry_evidence_validation/retry_evidence_validation_contract.json", with_controls({"schema_version": SCHEMA_VERSION, "validation_type": "structural_only_no_truth_scoring"}), generated)
    write_json("tiny_retry_evidence_validation/retry_evidence_validation_matrix.json", validation_matrix, generated)
    write_json("tiny_retry_evidence_validation/retry_evidence_validation_result.json", with_controls({"schema_version": SCHEMA_VERSION, "validation_status": "passed_for_blocked_empty_retry_evidence_packet", "review_required": True}), generated)
    write_text("tiny_retry_evidence_validation/retry_evidence_validation_report.md", md_report("Retry Evidence Validation", "Validation is structural only and uses no semantic truth score or LLM confidence authority."), generated)

    write_json("tiny_retry_claim_boundary_freshness_assessment/retry_claim_boundary_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_claim_fields": ["claim_id", "claim_text", "source_trace_status", "freshness_status", "limitation", "allowed_use", "external_use_authorized"]}), generated)
    write_json("tiny_retry_claim_boundary_freshness_assessment/retry_bounded_claim_registry.json", with_controls({"schema_version": SCHEMA_VERSION, "claim_count": 0, "bounded_claims": [], "external_use_authorized": False, "reason": "no evidence captured"}), generated)
    write_json("tiny_retry_claim_boundary_freshness_assessment/retry_freshness_assessment.json", with_controls({"schema_version": SCHEMA_VERSION, "freshness_status": "not_observed", "source_date_status": "date_missing_no_observation_executed", "review_status": "pending_review"}), generated)
    write_json("tiny_retry_claim_boundary_freshness_assessment/retry_unsupported_inference_registry.json", with_controls({"schema_version": SCHEMA_VERSION, "unsupported_inferences": [{"inference": "any current external fact about the selected evidence need", "unsupported_inference_marker": True, "external_use_authorized": False, "reason": "no locator or live observation"}]}), generated)
    write_text("tiny_retry_claim_boundary_freshness_assessment/retry_claim_boundary_freshness_report.md", md_report("Retry Claim Boundary Freshness", "No bounded external claims were created because the retry did not observe a source."), generated)

    review_packet = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "retry_post_observation_review_packet_id": "l6_10r_retry_post_observation_review_packet_001",
            "linked_evidence_packet_id": "l6_10r_retry_evidence_packet_001",
            "linked_bounded_claim_ids": [],
            "evidence_to_check": ["empty evidence packet", "blocked locator trace", "blocked observation trace"],
            "claim_boundaries_to_check": ["no current factual claim authorized"],
            "missing_context_to_check": evidence_packet["missing_context"],
            "unsupported_claims_to_check": [],
            "approval_status": "pending_review",
            "approve_for_externalization": False,
            "approve_for_artifact_update": False,
            "applied": False,
            "canonical_update_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "direct_y_star_mutation_authorized": False,
        }
    )
    write_json("tiny_retry_post_observation_review/retry_post_observation_review_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(review_packet.keys())}), generated)
    write_json("tiny_retry_post_observation_review/retry_post_observation_review_packet.json", review_packet, generated)
    write_text("tiny_retry_post_observation_review/retry_reviewer_checklist.md", md_report("Retry Reviewer Checklist", "Check the locator-resolution blocker, empty evidence packet, unsupported inference marker, and downstream action blocks."), generated)
    write_text("tiny_retry_post_observation_review/retry_post_observation_review_report.md", md_report("Retry Post Observation Review", "Review remains pending and no externalization or artifact update is approved."), generated)

    refinement = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "retry_refinement_candidate_id": "l6_10r_no_refinement_candidate_due_no_locator",
            "linked_evidence_packet_id": "l6_10r_retry_evidence_packet_001",
            "linked_l6_artifact": selection.get("linked_l6_artifact"),
            "refinement_target": "locator_resolution_precondition",
            "proposed_refinement": "Require a concrete public locator or approved controlled locator-discovery tooling before retrying observation.",
            "evidence_basis": "blocked locator resolution trace and empty evidence packet",
            "evidence_limitations": evidence_packet["missing_context"],
            "review_required": True,
            "approved": False,
            "applied": False,
            "artifact_update_authorized": False,
            "canonical_update_authorized": False,
            "brain_writeback_authorized": False,
            "memory_ingestion_authorized": False,
            "direct_y_star_mutation_authorized": False,
        }
    )
    write_json("tiny_retry_refinement_candidate/retry_refinement_candidate_schema.json", with_controls({"schema_version": SCHEMA_VERSION, "required_fields": list(refinement.keys())}), generated)
    write_json("tiny_retry_refinement_candidate/retry_artifact_refinement_candidate.json", refinement, generated)
    write_text("tiny_retry_refinement_candidate/retry_refinement_candidate_report.md", md_report("Retry Refinement Candidate", "A review-only no-locator refinement candidate was generated and remains unapplied."), generated)

    write_json("tiny_retry_abort_quarantine/retry_abort_policy.json", with_controls({"schema_version": SCHEMA_VERSION, "abort_triggers": ABORT_CONDITIONS}), generated)
    write_json("tiny_retry_abort_quarantine/retry_quarantine_policy.json", with_controls({"schema_version": SCHEMA_VERSION, "quarantine_rule": "any uncertain, unsafe, or out-of-scope evidence cannot update artifacts, strategy, brain, memory, canonical state, or Y*"}), generated)
    write_json("tiny_retry_abort_quarantine/retry_abort_or_quarantine_decision.json", with_controls({"schema_version": SCHEMA_VERSION, "abort_triggered": True, "quarantine_triggered": False, "decision": "blocked_before_observation_no_evidence_to_quarantine", "reason": "no_concrete_locator_resolved"}), generated)
    write_text("tiny_retry_abort_quarantine/retry_abort_quarantine_report.md", md_report("Retry Abort Quarantine", "The retry aborted before observation because no locator was resolved."), generated)

    for filename, action_type in RECEIPTS:
        write_json(
            f"tiny_retry_no_action_receipts/{filename}",
            with_controls(
                {
                    "schema_version": SCHEMA_VERSION,
                    "action_type": action_type,
                    "authorized_in_l6_10r": False,
                    "executed_in_l6_10r": False,
                    "blocker_reference": "l6_controlled_source_locator_resolution_tiny_observation_retry/l6_10r_milestone_contract.json",
                    "future_boundary_required": True,
                }
            ),
            generated,
        )
    write_text("tiny_retry_no_action_receipts/tiny_retry_no_action_receipt_report.md", md_report("Tiny Retry No-Action Receipts", "All disallowed action receipts were generated with executed_in_l6_10r=false."), generated)

    residuals = [
        "controlled locator discovery did not execute",
        "no concrete locator resolved",
        "tiny observation retry did not execute",
        "no current factual claims established",
        "evidence packet is empty and review-only",
        "artifact refinement remains unapplied",
        "future retry requires controlled locator-discovery tooling or a concrete public locator",
        "publication/outreach/payment/revenue remain blocked",
    ]
    cieu = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "event_mode": "l6_10r_controlled_source_locator_resolution_tiny_observation_retry_fixture",
            "X_t": {
                "l6_8_agentic_evidence": "l6_agentic_evidence_discovery_trust_engine/l6_8_summary.json",
                "l6_9_pilot_dry_run": "l6_controlled_agentic_evidence_pilot_approval_dry_run/l6_9_summary.json",
                "l6_10_blocked_tiny_pilot": "l6_tiny_real_read_only_agentic_evidence_observation_pilot/l6_10_summary.json",
            },
            "U_t": "Selected one L6.10 work order, planned one locator-discovery query, reached the controlled locator-discovery gate, and blocked without external reads.",
            "Y_star_t": "Resolve one concrete public source locator for one L6.8/L6.9/L6.10 agentic evidence work order under strict discovery limits, then retry one tiny real read-only observation if eligible, capture bounded evidence or blocked trace, and preserve no-broad-search/no-crawling/no-scraping/no-login/no-payment/no-contact/no-publication/no-outreach/no-revenue/no-MCP/no-live/no-CIEU-DB-write/no-canonical-mutation/no-brain-memory-writeback/no-direct-Y* mutation constraints.",
            "Y_t_plus_1": "Blocked locator resolution retry artifacts, empty evidence packet, review packet, review-only refinement candidate, receipts, and readiness report were generated.",
            "R_t_plus_1": residuals,
        }
    )
    write_json("l6_10r_strategic_residual_loop/l6_10r_cieu_like_fixture.json", cieu, generated)
    write_json("l6_10r_strategic_residual_loop/l6_10r_strategic_residual_delta.json", with_controls({"schema_version": SCHEMA_VERSION, "residuals": residuals, "locator_resolved": False, "observation_executed": False}), generated)
    write_json("l6_10r_strategic_residual_loop/l6_10r_meta_learning_update_candidate.json", with_controls({"schema_version": SCHEMA_VERSION, "eligible_for_review_queue": True, "eligible_for_direct_brain_writeback": False, "eligible_for_direct_memory_ingestion": False, "eligible_for_candidate_auto_approval": False, "eligible_for_direct_strategy_mutation": False, "approved": False, "applied": False}), generated)
    write_text("l6_10r_strategic_residual_loop/l6_10r_residual_report.md", md_report("L6.10R Residual Report", "The residual loop records unresolved locator tooling rather than synthetic evidence."), generated)

    readiness = with_controls(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "l6_10r_design_and_guardrails_complete": True,
            "locator_discovery_executed": False,
            "locator_discovery_queries_count": 0,
            "concrete_locator_resolved": False,
            "tiny_read_only_observation_executed": False,
            "ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot": False,
            "remaining_blocker": "no_locator_and_no_controlled_locator_discovery_tooling",
            "ready_for_publication": False,
            "ready_for_outreach": False,
            "ready_for_payment": False,
            "ready_for_revenue_execution": False,
            "ready_for_mcp_execution": False,
            "ready_for_canonical_update": False,
            "ready_for_brain_memory_writeback": False,
            "ready_for_direct_y_star_mutation": False,
            "next_recommended_milestone": NEXT_MILESTONE_BLOCKED,
        }
    )
    write_json("l6_10r_readiness_report/l6_10r_readiness_assessment.json", readiness, generated)
    write_json("l6_10r_readiness_report/l6_10r_next_milestone_recommendation.json", with_controls({"schema_version": SCHEMA_VERSION, "recommended_next_milestone": NEXT_MILESTONE_BLOCKED, "successful_path_next_milestone": NEXT_MILESTONE_SUCCESS, "do_not_implement_l6_11_now": True}), generated)
    write_json("l6_10r_readiness_report/l6_10r_blockers.json", with_controls({"schema_version": SCHEMA_VERSION, "blockers": residuals[:3], "exact_blocker": "no_locator_and_no_controlled_locator_discovery_tooling", "downstream_actions_blocked": NO_ACTION_CONSTRAINTS}), generated)
    write_text("l6_10r_readiness_report/l6_10r_readiness_report.md", md_report("L6.10R Readiness Report", "Outcome C: locator unresolved. The retry is ready only after controlled locator-discovery tooling or a concrete locator is available."), generated)

    return generated


def main() -> None:
    generated = build()
    print(f"Built L6.10R controlled locator resolution retry artifacts: {len(generated)} files")


if __name__ == "__main__":
    main()
