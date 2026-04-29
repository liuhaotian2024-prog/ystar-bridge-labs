#!/usr/bin/env python3
"""Build L6.10X budgeted controlled external search evidence pilot artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from controlled_search_backend_runtime.controlled_search_runtime import (  # noqa: E402
    BACKEND_ENV_VAR,
    ENABLE_ENV_VAR,
    ControlledSearchRequest,
    ControlledSearchRuntime,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.10X"
MILESTONE_NAME = (
    "Budgeted Controlled External Search, Bounded Crawl & Evidence Corroboration Pilot v0"
)
MODE = "budgeted_controlled_external_search_evidence_pilot"
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

BUDGET = {
    "max_selected_work_orders": 1,
    "max_queries": 5,
    "max_search_results_considered": 20,
    "max_pages_opened": 8,
    "max_domains": 5,
    "max_pages_per_domain": 3,
    "max_crawl_depth": 1,
    "max_total_external_reads": 12,
    "max_primary_sources_to_capture": 3,
    "max_secondary_sources_to_capture": 5,
    "max_conflicting_sources_to_capture": 3,
    "max_evidence_packets": 8,
    "max_runtime_minutes": 10,
    "rate_limit_required": True,
    "stop_on_login_or_payment_or_form": True,
    "stop_on_private_or_sensitive_data": True,
    "stop_on_scope_drift": True,
}

SAFETY_FLAGS = {
    "controlled_external_search_authorized": True,
    "bounded_public_page_read_authorized": True,
    "bounded_crawl_authorized": True,
    "evidence_corroboration_authorized": True,
    "ask_user_for_url_authorized": False,
    "user_manual_url_provision_required": False,
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
    "search_snippets_as_evidence_authorized": False,
    "llm_confidence_as_truth_authority_authorized": False,
    "semantic_truth_scoring_authorized": False,
    "private_sensitive_data_collection_authorized": False,
    "high_volume_crawling_authorized": False,
    "unbounded_scraping_authorized": False,
}

NO_ACTIONS = [
    "login",
    "account_creation",
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


def select_work_order() -> dict[str, Any]:
    previous = read_json("reviewed_seed_locator_injection/selected_work_order_for_seed_injection.json")
    if not previous:
        previous = read_json("locator_resolution_v_attempt/selected_work_order.json")
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_work_order_id": "l6_10x_selected_work_order_001",
        "source_selected_work_order_id": previous.get("selected_work_order_id"),
        "linked_l6_10w_selected_work_order_id": previous.get("selected_work_order_id"),
        "linked_l6_10v_selected_work_order_id": previous.get("linked_l6_10v_selected_work_order_id"),
        "linked_l6_8_work_order_id": previous.get("linked_l6_8_work_order_id"),
        "linked_evidence_need_id": previous.get("linked_evidence_need_id"),
        "linked_source_hypothesis_id": previous.get("linked_source_hypothesis_id"),
        "linked_l6_artifact": previous.get("linked_l6_artifact"),
        "evidence_need": previous.get("evidence_need")
        or previous.get("expected_evidence_type")
        or "decision-relevant public evidence",
        "source_type": previous.get("source_type") or "public_source",
        "source_function": previous.get("source_function") or "public evidence source",
        "expected_evidence_type": previous.get("expected_evidence_type")
        or "bounded public evidence",
        "observation_question": previous.get("observation_question")
        or "What public evidence can reduce uncertainty for the selected work order?",
        "claim_boundary": previous.get("claim_boundary_to_test")
        or "internal review only; no external use or strategy mutation",
        "selected_count": 1 if previous else 0,
    }


def query_plan(selected: dict[str, Any]) -> list[dict[str, Any]]:
    base = {
        "linked_work_order_id": selected["selected_work_order_id"],
        "source_type": selected["source_type"],
        "source_function": selected["source_function"],
        "no_snippet_fact_use": True,
        "no_fact_inference_from_search_result": True,
        "max_results": 4,
    }
    need = selected["evidence_need"]
    question = selected["observation_question"]
    source = selected["source_function"]
    return [
        {
            **base,
            "query_id": "l6_10x_query_001",
            "query_category": "primary_source_query",
            "query_text": f"{source} official primary source {need}",
            "priority": 1,
        },
        {
            **base,
            "query_id": "l6_10x_query_002",
            "query_category": "official_source_query",
            "query_text": f"{source} documentation policy program {need}",
            "priority": 2,
        },
        {
            **base,
            "query_id": "l6_10x_query_003",
            "query_category": "corroboration_query",
            "query_text": f"independent analysis corroboration {need} {question}",
            "priority": 3,
        },
        {
            **base,
            "query_id": "l6_10x_query_004",
            "query_category": "conflict_check_query",
            "query_text": f"limitations contradiction risk evidence {need}",
            "priority": 4,
        },
        {
            **base,
            "query_id": "l6_10x_query_005",
            "query_category": "freshness_check_query",
            "query_text": f"latest update date freshness {source} {need}",
            "priority": 5,
        },
    ]


def search_config() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "controlled_search_enabled": False,
        "backend_id": None,
        "backend_available": False,
        "max_queries": BUDGET["max_queries"],
        "max_results": BUDGET["max_search_results_considered"],
        "result_candidates": [],
        "external_network_read_used": False,
        "enablement_env_vars": [ENABLE_ENV_VAR, BACKEND_ENV_VAR],
    }


def search_request(selected: dict[str, Any], queries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "request_id": "l6_10x_controlled_search_request_001",
        "selected_work_order_id": selected["selected_work_order_id"],
        "queries": queries,
        "budget": BUDGET,
        "snippets_are_evidence": False,
        "facts_inferred_from_snippets": False,
    }


def receipt_payload(action: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": f"l6_10x_no_{action}_receipt",
        "action": action,
        "executed": False,
        "authorized": False,
        "evidence": "No disallowed action was executed during L6.10X.",
    }


def main() -> None:
    generated: list[str] = []
    selected = select_work_order()
    queries = query_plan(selected)
    config = search_config()
    request = search_request(selected, queries)
    search_result = ControlledSearchRuntime(config=config).run(
        ControlledSearchRequest.from_mapping(request)
    ).to_dict()
    backend_missing = search_result["error_code"] == "controlled_search_backend_required"
    candidates: list[dict[str, Any]] = search_result.get("result_candidates", [])
    selected_sources: list[dict[str, Any]] = []
    opened_pages: list[dict[str, Any]] = []
    evidence_packets = [
        {
            "schema_version": SCHEMA_VERSION,
            "evidence_packet_id": "l6_10x_evidence_packet_001",
            "source_locator": None,
            "source_title": None,
            "source_owner_or_publisher": None,
            "observed_timestamp": None,
            "source_date_or_date_missing": "not_observed_backend_missing",
            "freshness_class": "not_observed",
            "captured_bounded_claims": [],
            "unsupported_claims": [],
            "missing_context": ["controlled_search_backend_required"],
            "claim_boundary": selected["claim_boundary"],
            "citation_trace": [],
            "review_status": "blocked_no_backend_no_evidence",
            "live_source_evidence_captured": False,
            "publication_taken": False,
            "outreach_taken": False,
            "payment_taken": False,
            "revenue_action_taken": False,
            "mcp_execution_taken": False,
            "canonical_update_taken": False,
            "brain_memory_writeback_taken": False,
            "direct_y_star_mutation_taken": False,
        }
    ]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete": True,
        "selected_work_order_id": selected["selected_work_order_id"],
        "query_count": len(queries),
        "search_backend_mode": search_result["backend_mode"],
        "backend_missing": backend_missing,
        "search_executed": search_result["search_executed"],
        "search_results_considered": search_result["search_results_considered"],
        "pages_opened": len(opened_pages),
        "domains_touched": 0,
        "crawl_depth_used": 0,
        "evidence_packets_generated": len(evidence_packets),
        "conflicts_found": 0,
        "page_read_backend_missing": backend_missing,
        "manual_url_request_avoided": True,
        **BUDGET,
        **SAFETY_FLAGS,
    }

    write_text(
        "l6_budgeted_controlled_external_search_evidence_pilot/README.md",
        f"# {MILESTONE_ID} {MILESTONE_NAME}\n\n"
        "Budgeted external discovery is allowed only through an explicitly configured controlled "
        "search backend and bounded public page-read/crawl adapters. The default path performs no "
        "search, asks for no manual URL, and reports backend enablement requirements.",
        generated,
    )
    for name, payload in [
        ("l6_10x_milestone_contract.json", {**summary, "contract_type": "milestone_contract"}),
        ("l6_10x_scope.json", {"schema_version": SCHEMA_VERSION, "scope": "budgeted search, bounded crawl, corroboration", "manual_url_request_allowed": False}),
        ("l6_10x_budget_policy.json", BUDGET),
        ("l6_10x_safety_flags.json", SAFETY_FLAGS),
        ("l6_10x_summary.json", summary),
    ]:
        write_json(f"l6_budgeted_controlled_external_search_evidence_pilot/{name}", payload, generated)
    write_text(
        "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_summary.md",
        "# L6.10X Summary\n\n"
        f"- Queries planned: {len(queries)}\n"
        f"- Search backend mode: {search_result['backend_mode']}\n"
        f"- Search executed: {search_result['search_executed']}\n"
        f"- Evidence packets generated: {len(evidence_packets)}\n"
        "- Manual URL request avoided: true",
        generated,
    )

    for name, payload in [
        ("search_budget_contract.json", {"schema_version": SCHEMA_VERSION, "budget_contract_id": "l6_10x_search_budget_contract", "budgeted_not_crippled": True}),
        ("search_budget_limits.json", BUDGET),
        ("budget_enforcement_rules.json", {"schema_version": SCHEMA_VERSION, "rules": ["every query counted", "every opened page counted", "every domain counted", "every crawl expansion counted", "budget stop condition", "scope drift stop condition", "login/payment/form/private-data stop condition", "no evidence beyond budget", "no retry loop without new approval"]}),
        ("budget_exhaustion_policy.json", {"schema_version": SCHEMA_VERSION, "on_budget_exhaustion": "stop_and_report_residual", "no_retry_loop_without_new_approval": True}),
    ]:
        write_json(f"search_budget_policy/{name}", payload, generated)
    write_text("search_budget_policy/search_budget_report.md", "# Search Budget Report\n\nBudget limits are explicit and enforce stop conditions.", generated)

    write_json("agentic_query_planner/selected_work_order.json", selected, generated)
    write_json("agentic_query_planner/query_planning_contract.json", {"schema_version": SCHEMA_VERSION, "min_queries": 1, "max_queries": 5, "categories_required": ["primary_source_query", "official_source_query", "corroboration_query", "conflict_check_query", "freshness_check_query"]}, generated)
    write_json("agentic_query_planner/generated_query_plan.json", {"schema_version": SCHEMA_VERSION, "query_count": len(queries), "queries": queries}, generated)
    write_json("agentic_query_planner/query_priority_matrix.json", {"schema_version": SCHEMA_VERSION, "ranked_queries": queries}, generated)
    write_text("agentic_query_planner/query_planner_report.md", "# Query Planner Report\n\nGenerated five targeted query categories from one selected work order.", generated)

    write_json("controlled_search_backend_runtime/controlled_search_backend_registry.json", {"schema_version": SCHEMA_VERSION, "supported_backends": ["brave_search_api", "bing_search_api", "tavily_search_api", "serpapi", "openclaw_read_only_search_adapter", "future_governed_mcp_search_adapter"], "enabled_backend": None}, generated)
    write_json("controlled_search_backend_runtime/controlled_search_config.example.json", config, generated)
    write_json("controlled_search_backend_runtime/controlled_search_trace.json", {**search_result, "schema_version": SCHEMA_VERSION}, generated)
    write_text("controlled_search_backend_runtime/controlled_search_runtime_report.md", "# Controlled Search Runtime Report\n\nDefault backend is disabled and produced controlled_search_backend_required without network use.", generated)

    write_json("search_result_triage/search_result_triage_contract.json", {"schema_version": SCHEMA_VERSION, "triage_dimensions": ["expected primary source", "official/provenance strength", "source specificity", "freshness likelihood", "relevance", "domain diversity", "risk class", "login/payment/form likelihood", "source type", "corroboration value", "conflict discovery value"]}, generated)
    write_json("search_result_triage/search_result_candidates.json", {"schema_version": SCHEMA_VERSION, "candidate_count": len(candidates), "candidates": candidates}, generated)
    write_json("search_result_triage/source_triage_matrix.json", {"schema_version": SCHEMA_VERSION, "triage_rows": [], "blocked_reason": search_result["error_code"]}, generated)
    write_json("search_result_triage/selected_sources_to_open.json", {"schema_version": SCHEMA_VERSION, "selected_count": len(selected_sources), "sources": selected_sources}, generated)
    write_json("search_result_triage/rejected_search_results.json", {"schema_version": SCHEMA_VERSION, "rejected": [], "blocked_reason": search_result["error_code"]}, generated)
    write_text("search_result_triage/search_result_triage_report.md", "# Search Result Triage Report\n\nNo search results were available because no controlled backend is configured.", generated)

    write_json("bounded_crawl_runtime/bounded_crawl_contract.json", {"schema_version": SCHEMA_VERSION, "max_crawl_depth": 1, "max_pages_per_domain": 3, "no_login": True, "no_payment": True, "no_forms": True, "no_private_sensitive_data": True}, generated)
    write_json("bounded_crawl_runtime/bounded_crawl_trace.json", {"schema_version": SCHEMA_VERSION, "crawl_executed": False, "opened_pages_count": 0, "domains_touched": 0, "crawl_depth_used": 0, "blocked_reason": "controlled_search_backend_required"}, generated)
    write_json("bounded_crawl_runtime/opened_page_registry.json", {"schema_version": SCHEMA_VERSION, "opened_pages": opened_pages}, generated)
    write_json("bounded_crawl_runtime/crawl_expansion_decisions.json", {"schema_version": SCHEMA_VERSION, "crawl_expansions": [], "max_depth": 1}, generated)
    write_text("bounded_crawl_runtime/bounded_crawl_report.md", "# Bounded Crawl Report\n\nNo pages were opened because no controlled search backend returned sources.", generated)

    quality_contract = {"schema_version": SCHEMA_VERSION, "dimensions": ["primary_vs_secondary", "official_provenance_status", "source_owner", "source_date", "freshness_class", "claim_specificity", "independence", "reviewability", "conflict_potential", "privacy_ip_cleanliness"], "prohibited_authorities": ["semantic_truth_score", "llm_confidence"], "llm_confidence_as_authority": False}
    write_json("source_quality_and_trust_assessment/source_quality_contract.json", quality_contract, generated)
    write_json("source_quality_and_trust_assessment/source_quality_matrix.json", {"schema_version": SCHEMA_VERSION, "sources": []}, generated)
    write_json("source_quality_and_trust_assessment/trust_assessment_results.json", {"schema_version": SCHEMA_VERSION, "trust_results": [], "llm_confidence_as_authority": False}, generated)
    write_json("source_quality_and_trust_assessment/source_freshness_assessment.json", {"schema_version": SCHEMA_VERSION, "freshness_results": []}, generated)
    write_text("source_quality_and_trust_assessment/source_quality_report.md", "# Source Quality Report\n\nNo sources were assessed; structural scoring only, no semantic truth scoring.", generated)

    write_json("evidence_extraction_and_claim_boundary/evidence_extraction_contract.json", {"schema_version": SCHEMA_VERSION, "max_evidence_packets": 8, "review_status_required": "pending_review", "downstream_actions_false": True}, generated)
    write_json("evidence_extraction_and_claim_boundary/evidence_packet_schema.json", {"schema_version": SCHEMA_VERSION, "required_fields": ["source_locator", "source_title", "source_owner_or_publisher", "observed_timestamp", "source_date_or_date_missing", "freshness_class", "captured_bounded_claims", "unsupported_claims", "missing_context", "claim_boundary", "citation_trace", "review_status"], "downstream_action_fields_must_be_false": ["publication_taken", "outreach_taken", "payment_taken", "revenue_action_taken", "mcp_execution_taken", "canonical_update_taken", "brain_memory_writeback_taken", "direct_y_star_mutation_taken"]}, generated)
    write_json("evidence_extraction_and_claim_boundary/evidence_packet_index.json", {"schema_version": SCHEMA_VERSION, "evidence_packet_count": len(evidence_packets), "evidence_packets": ["evidence_extraction_and_claim_boundary/evidence_packet_001.json"]}, generated)
    write_json("evidence_extraction_and_claim_boundary/evidence_packet_001.json", evidence_packets[0], generated)
    write_json("evidence_extraction_and_claim_boundary/bounded_claim_registry.json", {"schema_version": SCHEMA_VERSION, "bounded_claims": []}, generated)
    write_json("evidence_extraction_and_claim_boundary/unsupported_claim_registry.json", {"schema_version": SCHEMA_VERSION, "unsupported_claims": []}, generated)
    write_json("evidence_extraction_and_claim_boundary/missing_context_registry.json", {"schema_version": SCHEMA_VERSION, "missing_context": ["controlled_search_backend_required"]}, generated)
    write_text("evidence_extraction_and_claim_boundary/evidence_extraction_report.md", "# Evidence Extraction Report\n\nGenerated a blocked evidence packet; no live evidence captured.", generated)

    write_json("evidence_corroboration_and_conflict_matrix/corroboration_contract.json", {"schema_version": SCHEMA_VERSION, "internal_review_only": True}, generated)
    write_json("evidence_corroboration_and_conflict_matrix/source_corroboration_matrix.json", {"schema_version": SCHEMA_VERSION, "sources": []}, generated)
    write_json("evidence_corroboration_and_conflict_matrix/claim_corroboration_matrix.json", {"schema_version": SCHEMA_VERSION, "claims": []}, generated)
    write_json("evidence_corroboration_and_conflict_matrix/conflict_registry.json", {"schema_version": SCHEMA_VERSION, "conflicts": [], "conflict_count": 0}, generated)
    write_json("evidence_corroboration_and_conflict_matrix/evidence_sufficiency_assessment.json", {"schema_version": SCHEMA_VERSION, "sufficient_for_internal_review": False, "sufficient_for_external_use": False, "reason": "no evidence captured"}, generated)
    write_text("evidence_corroboration_and_conflict_matrix/corroboration_report.md", "# Corroboration Report\n\nNo conflicts or corroboration were found because no evidence was captured.", generated)

    review_packet = {"schema_version": SCHEMA_VERSION, "review_packet_id": "l6_10x_evidence_review_packet", "review_status": "pending_review_blocked_no_backend", "external_use_authorized": False, "approve_for_external_use": False, "artifact_update_authorized": False, "applied": False}
    refinement = {"schema_version": SCHEMA_VERSION, "candidate_id": "l6_10x_artifact_refinement_candidate_001", "review_required": True, "approved": False, "applied": False, "artifact_update_authorized": False, "canonical_update_authorized": False, "brain_writeback_authorized": False, "memory_ingestion_authorized": False, "direct_y_star_mutation_authorized": False}
    write_json("evidence_review_and_refinement_candidates/review_packet_index.json", {"schema_version": SCHEMA_VERSION, "review_packets": ["evidence_review_and_refinement_candidates/evidence_review_packet.json"]}, generated)
    write_json("evidence_review_and_refinement_candidates/evidence_review_packet.json", review_packet, generated)
    write_json("evidence_review_and_refinement_candidates/artifact_refinement_candidate_index.json", {"schema_version": SCHEMA_VERSION, "candidates": ["evidence_review_and_refinement_candidates/artifact_refinement_candidate_001.json"]}, generated)
    write_json("evidence_review_and_refinement_candidates/artifact_refinement_candidate_001.json", refinement, generated)
    write_text("evidence_review_and_refinement_candidates/evidence_review_and_refinement_report.md", "# Review And Refinement Report\n\nReview packet and unapplied refinement candidate generated.", generated)

    for action in NO_ACTIONS:
        write_json(f"external_search_no_action_receipts/no_{action}_receipt.json", receipt_payload(action), generated)
    write_text("external_search_no_action_receipts/external_search_no_action_report.md", "# No-Action Report\n\nAll disallowed action receipts are false.", generated)

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "l6_10x_budgeted_controlled_external_search_evidence_pilot_complete": True,
        "ready_for_l6_11_controlled_multi_source_evidence_review_gate": False,
        "next_step": "configure_controlled_search_backend",
        "controlled_search_backend_required": backend_missing,
        "controlled_public_page_read_adapter_required": backend_missing,
        "do_not_ask_user_for_manual_url": True,
        "publication_ready": False,
        "outreach_ready": False,
        "revenue_execution_ready": False,
        "mcp_execution_ready": False,
        "canonical_update_ready": False,
        "brain_memory_writeback_ready": False,
    }
    blockers = {"schema_version": SCHEMA_VERSION, "blockers": [{"blocker_code": "controlled_search_backend_required", "next_step": "configure_controlled_search_backend"}, {"blocker_code": "controlled_public_page_read_adapter_required", "next_step": "configure_controlled_public_page_read_adapter"}]}
    cieu = {"schema_version": SCHEMA_VERSION, "event_mode": "l6_10x_budgeted_controlled_external_search_evidence_pilot_fixture", "X_t": {"selected_work_order": selected, "query_plan": queries}, "U_t": {"budget": BUDGET, "backend_mode": search_result["backend_mode"]}, "Y_star_t": "Run budgeted controlled external search, bounded crawl, and evidence corroboration under strict no-action constraints.", "Y_t_plus_1": {"queries_generated": len(queries), "search_executed": search_result["search_executed"], "evidence_packets_generated": len(evidence_packets)}, "R_t_plus_1": {"residuals": ["controlled_search_backend_required", "controlled_public_page_read_adapter_required", "no live evidence captured"]}}
    meta = {"schema_version": SCHEMA_VERSION, "candidate_id": "l6_10x_meta_learning_update_candidate", "eligible_for_review_queue": True, "eligible_for_direct_brain_writeback": False, "eligible_for_direct_memory_ingestion": False, "eligible_for_candidate_auto_approval": False, "eligible_for_direct_strategy_mutation": False, "approved": False, "applied": False}
    residual = {"schema_version": SCHEMA_VERSION, "residual_id": "l6_10x_strategic_residual_delta", "primary_residual": "controlled_search_backend_required", "manual_url_request_avoided": True}
    next_rec = {"schema_version": SCHEMA_VERSION, "recommended_next_milestone": "L6.10Y Controlled Search Backend Configuration & Page Read Adapter Enablement v0", "do_not_implement_l6_11_until_evidence_batch_exists": True}
    read_summary = {**summary, "readiness_next_step": readiness["next_step"], "generated_refs": {"query_plan": "agentic_query_planner/generated_query_plan.json", "search_trace": "controlled_search_backend_runtime/controlled_search_trace.json", "evidence_index": "evidence_extraction_and_claim_boundary/evidence_packet_index.json", "readiness": "l6_10x_read_model/l6_10x_readiness_assessment.json"}}
    for name, payload in [
        ("l6_10x_cieu_like_fixture.json", cieu),
        ("l6_10x_strategic_residual_delta.json", residual),
        ("l6_10x_meta_learning_update_candidate.json", meta),
        ("l6_10x_readiness_assessment.json", readiness),
        ("l6_10x_blockers.json", blockers),
        ("l6_10x_next_milestone_recommendation.json", next_rec),
        ("l6_10x_read_model_summary.json", read_summary),
    ]:
        write_json(f"l6_10x_read_model/{name}", payload, generated)
    write_text("l6_10x_read_model/l6_10x_report.md", "# L6.10X Read Model Report\n\nBudgeted discovery architecture is ready; backend/page-read adapters remain missing.", generated)
    print(f"generated {len(generated)} L6.10X budgeted search files")


if __name__ == "__main__":
    main()
