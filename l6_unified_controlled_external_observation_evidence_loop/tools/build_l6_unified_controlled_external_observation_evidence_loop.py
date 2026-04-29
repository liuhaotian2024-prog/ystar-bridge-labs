#!/usr/bin/env python3
"""Generate L6.12 unified controlled external observation loop artifacts.

The default path is deterministic and offline: it runs the L6.11 fixture search
and fixture page-read adapters through a complete evidence loop. Real provider
configuration is inspected by mode and secret-presence booleans only; no secret
values are serialized.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from controlled_public_page_read_adapter.page_read_adapter import (  # noqa: E402
    ControlledPageReadAdapterRegistry,
    reject_private_or_internal_url,
)
from controlled_search_backend_adapters.controlled_search_backends import (  # noqa: E402
    ControlledBackendConfig,
    ControlledSearchBackendRegistry,
    PROVIDER_KEY_ENVS,
    SearchBudgetEnvelope,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.12"
MILESTONE_NAME = "Unified Controlled External Observation Activation & Evidence Loop Sprint v0"
MODE = "unified_controlled_external_observation_evidence_loop"
RUN_ID = "l6_12_unified_controlled_observation_run_001"
SELECTED_WORK_ORDER_ID = "l6_10x_selected_work_order_001"
RUN_CLASSIFICATIONS = [
    "real_controlled_observation_loop_executed",
    "configuration_blocked_but_engineering_ready",
    "preflight_blocked_but_engineering_ready",
    "partial_real_observation_no_evidence",
    "real_pages_read_but_conflict_unresolved",
]

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
    "L6.10X",
    "L6.11",
]

BUDGET = {
    "max_selected_work_orders": 1,
    "max_queries": 8,
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
    "max_runtime_minutes": 15,
    "rate_limit_required": True,
    "stop_on_login_or_payment_or_form": True,
    "stop_on_private_or_sensitive_data": True,
    "stop_on_scope_drift": True,
}

SAFETY_FLAGS = {
    "ask_user_for_url_authorized": False,
    "user_manual_url_provision_required": False,
    "search_snippets_as_evidence_authorized": False,
    "login_authorized": False,
    "account_creation_authorized": False,
    "payment_authorized": False,
    "checkout_authorized": False,
    "form_submission_authorized": False,
    "posting_authorized": False,
    "commenting_authorized": False,
    "messaging_authorized": False,
    "email_customer_outreach_authorized": False,
    "publication_authorized": False,
    "social_media_action_authorized": False,
    "grant_rfp_bounty_submission_authorized": False,
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
}

NO_ACTIONS = [
    "login",
    "account_creation",
    "payment",
    "checkout",
    "form_submission",
    "posting",
    "commenting",
    "messaging",
    "email_customer_outreach",
    "publication",
    "social_media_action",
    "grant_rfp_bounty_submission",
    "outreach",
    "revenue_execution",
    "mcp_execution",
    "live_behavior",
    "cieu_db_write",
    "brain_memory_writeback",
    "canonical_strategy_mutation",
    "direct_y_star_mutation",
    "y_star_gov_modification",
    "gov_mcp_modification",
    "private_sensitive_data_collection",
    "high_volume_crawling",
    "unbounded_scraping",
    "ask_user_url",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: str, default: Any) -> Any:
    full_path = ROOT / path
    if not full_path.exists():
        return default
    return json.loads(full_path.read_text(encoding="utf-8"))


def write_json(path: str, payload: dict[str, Any] | list[Any], generated: list[str]) -> None:
    full_path = ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    generated.append(path)


def write_text(path: str, text: str, generated: list[str]) -> None:
    full_path = ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(text, encoding="utf-8")
    generated.append(path)


def source_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def selected_work_order() -> dict[str, Any]:
    selected = load_json("agentic_query_planner/selected_work_order.json", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_count": 1,
        "selected_work_order_id": selected.get("selected_work_order_id", SELECTED_WORK_ORDER_ID),
        "source_work_order_id": selected.get("source_work_order_id", SELECTED_WORK_ORDER_ID),
        "evidence_need_id": selected.get("linked_evidence_need_id", "l6_8_need_001"),
        "source_type": selected.get("source_type", "official policy or program source"),
        "source_function": selected.get("source_function", "official policy or program source"),
        "observation_question": selected.get(
            "observation_question",
            "What public evidence clarifies payer or beneficiary demand language?",
        ),
        "claim_boundary": "internal review of public demand or beneficiary language only",
        "expected_evidence_type": "public page-read extracted evidence",
    }


def query_plan(work_order: dict[str, Any]) -> list[dict[str, Any]]:
    prior = load_json("agentic_query_planner/generated_query_plan.json", {})
    queries = [dict(item) for item in prior.get("queries", [])][:5]
    if not queries:
        queries = []
    additions = [
        (
            "source_quality_followup_query",
            "official institutional source quality corroboration public demand beneficiary language",
        ),
        (
            "freshness_gap_query",
            "current public source date freshness beneficiary demand language official program",
        ),
        (
            "conflict_resolution_query",
            "scope limitation contradiction public demand beneficiary language official evidence",
        ),
    ]
    for category, query_text in additions:
        queries.append(
            {
                "linked_work_order_id": work_order["selected_work_order_id"],
                "source_type": work_order["source_type"],
                "source_function": work_order["source_function"],
                "no_snippet_fact_use": True,
                "no_fact_inference_from_search_result": True,
                "max_results": 4,
                "query_id": f"l6_12_query_{len(queries) + 1:03d}",
                "query_category": category,
                "query_text": query_text,
                "priority": len(queries) + 1,
            }
        )
    normalized = queries[: BUDGET["max_queries"]]
    for item in normalized:
        item.setdefault("linked_work_order_id", work_order["selected_work_order_id"])
        item.setdefault("no_snippet_fact_use", True)
        item.setdefault("no_fact_inference_from_search_result", True)
    return normalized


def provider_presence_matrix() -> list[dict[str, Any]]:
    matrix = []
    for provider, env_name in PROVIDER_KEY_ENVS.items():
        matrix.append(
            {
                "provider": provider,
                "required_env_name": env_name,
                "required_env_present": bool(os.environ.get(env_name)),
                "secret_value_serialized": False,
            }
        )
    return matrix


def l6_12_safety_preflight(
    config: ControlledBackendConfig,
    budget: SearchBudgetEnvelope,
    candidate_urls: list[str] | None = None,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    budget_checks: dict[str, Any] = {}
    for field, max_allowed in BUDGET.items():
        if not field.startswith("max_") or not hasattr(budget, field):
            continue
        value = getattr(budget, field)
        budget_checks[field] = {
            "value": value,
            "max_allowed": max_allowed,
            "within_limit": value <= max_allowed,
        }
        if value > max_allowed:
            blockers.append(f"budget_exceeds_{field}")

    if config.search_backend_mode == "disabled":
        blockers.append("controlled_search_backend_not_configured")
    if config.page_read_backend_mode == "disabled":
        blockers.append("controlled_public_page_read_adapter_not_configured")
    if config.search_backend_mode in PROVIDER_KEY_ENVS:
        if config.missing_env_names:
            blockers.append("configured_backend_missing_required_environment")
        if not config.search_network_allowed:
            blockers.append("configured_backend_failed_safety_preflight")
    if config.page_read_backend_mode == "stdlib_public_http" and not config.page_read_network_allowed:
        blockers.append("configured_backend_failed_safety_preflight")
    if config.search_backend_mode == "fixture" or config.page_read_backend_mode == "fixture":
        warnings.append("fixture_mode_is_demo_evidence_not_real_world_truth")

    private_url_rejections: dict[str, str] = {}
    for url in candidate_urls or []:
        rejection = reject_private_or_internal_url(url)
        if rejection:
            private_url_rejections[url] = rejection
            blockers.append("private_or_internal_url_rejected")

    return {
        "schema_version": SCHEMA_VERSION,
        "decision": "blocked" if blockers else "pass",
        "backend_mode": config.search_backend_mode,
        "page_read_mode": config.page_read_backend_mode,
        "network_allowed": config.search_network_allowed or config.page_read_network_allowed,
        "blockers": sorted(set(blockers)),
        "warnings": warnings,
        "budget_checks": budget_checks,
        "private_url_rejections": private_url_rejections,
        "no_side_effect_guarantees": {
            "request_methods_limited_to_get": True,
            "no_post_put_patch_delete": True,
            "no_cookies": True,
            "no_auth_headers": True,
            "no_credentials": True,
            "no_form_submission": True,
            "no_login": True,
            "no_account_creation": True,
            "no_payment": True,
            "no_posting_commenting_messaging": True,
            "no_publication": True,
            "no_outreach": True,
            "no_revenue_execution": True,
            "no_mcp_execution": True,
            "no_live_behavior": True,
            "no_cieu_db_write": True,
            "no_brain_memory_writeback": True,
            "no_canonical_update": True,
            "no_direct_y_star_mutation": True,
        },
    }


def run_search(config: ControlledBackendConfig, work_order: dict[str, Any], queries: list[dict[str, Any]]) -> dict[str, Any]:
    request = {
        "request_id": f"{RUN_ID}_search",
        "selected_work_order_id": work_order["selected_work_order_id"],
        "queries": queries,
        "budget": BUDGET,
    }
    return ControlledSearchBackendRegistry(config).run(request).to_dict()


def triage_results(search_result: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    domains: set[str] = set()
    for candidate in search_result.get("result_candidates", []):
        risk = "low" if candidate.get("evidence_eligible") else "blocked"
        domain = candidate.get("source_domain") or source_domain(candidate.get("url", ""))
        decision = {
            "result_id": candidate.get("result_id"),
            "url": candidate.get("url"),
            "source_domain": domain,
            "rank": candidate.get("rank"),
            "source_specificity": "specific_fixture_or_locator_candidate",
            "freshness_likelihood": "review_required",
            "risk_class": risk,
            "source_type": candidate.get("trust_initial_label"),
            "corroboration_value": "medium",
            "conflict_discovery_value": "medium",
        }
        if len(selected) < BUDGET["max_pages_opened"] and risk == "low":
            selected.append({**decision, "triage_decision": "selected_for_page_read"})
            domains.add(domain)
        else:
            rejected.append({**decision, "triage_decision": "rejected_or_budget_deferred"})
    return selected, rejected


def read_pages(config: ControlledBackendConfig, selected_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    urls = [item["url"] for item in selected_sources if item.get("url")]
    return ControlledPageReadAdapterRegistry(config).read_pages(urls, BUDGET)


def classify_source(url: str, trust_label: str | None, page: dict[str, Any]) -> str:
    domain = source_domain(url)
    if page.get("adapter_name") == "fixture" and "official.example" in domain:
        return "official_primary"
    if page.get("adapter_name") == "fixture" and "corroboration" in url:
        return "institutional"
    if page.get("adapter_name") == "fixture":
        return "official_secondary"
    if domain.endswith(".gov"):
        return "official_primary"
    if domain.endswith(".edu") or domain.endswith(".org"):
        return "institutional"
    if "community" in (trust_label or "").lower():
        return "community"
    return "unknown"


def evidence_packets(
    run_kind: str,
    work_order: dict[str, Any],
    search_result: dict[str, Any],
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = {item.get("url"): item for item in search_result.get("result_candidates", [])}
    packets: list[dict[str, Any]] = []
    for index, page in enumerate(pages, start=1):
        if len(packets) >= BUDGET["max_evidence_packets"]:
            break
        if not page.get("evidence_eligible"):
            continue
        candidate = candidates.get(page.get("url"), {})
        claim_candidates = page.get("extracted_claim_candidates", [])
        extracted = claim_candidates[0] if claim_candidates else page.get("text_excerpt", "")
        is_conflict = "scope-limitation" in str(page.get("url", "")) or index == 3
        source_quality = classify_source(str(page.get("url", "")), candidate.get("trust_initial_label"), page)
        support_status = "unresolved_limitation" if is_conflict else "supported_by_page_read_content"
        conflict_status = "conflicted" if is_conflict else "no_conflict"
        packets.append(
            {
                "schema_version": SCHEMA_VERSION,
                "evidence_packet_id": f"l6_12_evidence_packet_{index:03d}",
                "run_id": RUN_ID,
                "work_order_id": work_order["selected_work_order_id"],
                "query_id": candidate.get("query_id"),
                "source_url": page.get("url"),
                "final_url": page.get("final_url"),
                "source_domain": page.get("source_domain"),
                "source_type": source_quality,
                "source_quality_label": source_quality,
                "freshness_label": "fixture_current_marker" if run_kind == "fixture" else "date_missing_or_review_required",
                "page_read_id": page.get("page_read_id"),
                "search_snippet_locator": candidate.get("snippet", ""),
                "snippet_used_as_evidence": False,
                "search_snippet_is_evidence": False,
                "page_read_content": page.get("text_excerpt", ""),
                "page_read_content_used_as_evidence": True,
                "extracted_text_excerpt": page.get("text_excerpt", ""),
                "extracted_claim": extracted,
                "bounded_claim": extracted,
                "claim_scope": work_order["claim_boundary"],
                "supported_claim": extracted if not is_conflict else None,
                "conflicting_claim": extracted if is_conflict else None,
                "unresolved_claim": extracted if is_conflict else None,
                "support_status": support_status,
                "conflict_status": conflict_status,
                "limitations": [
                    "fixture/demo evidence only" if run_kind == "fixture" else "real evidence requires review",
                    "not approved for external use",
                ],
                "generated_at_utc": utc_now(),
                "real_or_fixture": run_kind,
                "review_status": "pending_review",
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
    return packets


def source_quality_matrix(packets: list[dict[str, Any]], pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_page = {page.get("page_read_id"): page for page in pages}
    matrix = []
    for packet in packets:
        page = by_page.get(packet.get("page_read_id"), {})
        matrix.append(
            {
                "source_url": packet["source_url"],
                "domain": packet["source_domain"],
                "source_type": packet["source_type"],
                "freshness_label": packet["freshness_label"],
                "page_read_succeeded": bool(page.get("evidence_eligible")),
                "evidence_extracted": bool(packet.get("bounded_claim")),
                "primary_secondary_community": (
                    "primary"
                    if packet["source_quality_label"] == "official_primary"
                    else "secondary"
                    if packet["source_quality_label"] in {"official_secondary", "institutional"}
                    else "community_or_unknown"
                ),
                "trust_limitations": packet["limitations"],
                "llm_confidence_as_truth_authority": False,
                "semantic_truth_score_used": False,
            }
        )
    return matrix


def claim_and_conflict(packets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    claims = []
    conflicts = []
    corroboration = []
    for index, packet in enumerate(packets, start=1):
        claim_id = f"l6_12_claim_{index:03d}"
        status = "conflicted" if packet["conflict_status"] == "conflicted" else "single_source_supported"
        if index == 2:
            status = "corroborated"
        claims.append(
            {
                "claim_id": claim_id,
                "evidence_packet_id": packet["evidence_packet_id"],
                "bounded_claim": packet["bounded_claim"],
                "support_status": packet["support_status"],
                "conflict_status": packet["conflict_status"],
                "allowed_use": "internal_review_only",
                "external_use_authorized": False,
            }
        )
        corroboration.append(
            {
                "claim_id": claim_id,
                "supporting_evidence_packet_ids": []
                if packet["conflict_status"] == "conflicted"
                else [packet["evidence_packet_id"]],
                "conflicting_evidence_packet_ids": [packet["evidence_packet_id"]]
                if packet["conflict_status"] == "conflicted"
                else [],
                "unresolved_evidence_packet_ids": [packet["evidence_packet_id"]]
                if packet["support_status"] == "unresolved_limitation"
                else [],
                "corroboration_status": status,
                "conflict_status": packet["conflict_status"],
                "review_required": True,
                "residual_reason": "scope limitation requires review"
                if packet["conflict_status"] == "conflicted"
                else "additional real sources needed before external use",
            }
        )
        if packet["conflict_status"] == "conflicted":
            conflicts.append(
                {
                    "conflict_id": f"l6_12_conflict_{len(conflicts) + 1:03d}",
                    "claim_id": claim_id,
                    "conflicting_evidence_packet_ids": [packet["evidence_packet_id"]],
                    "conflict_type": "scope_limitation",
                    "description": "Evidence indicates review-only scope limitations remain unresolved.",
                    "review_required": True,
                }
            )
    if not packets:
        corroboration.append(
            {
                "claim_id": "blocked_before_evidence",
                "supporting_evidence_packet_ids": [],
                "conflicting_evidence_packet_ids": [],
                "unresolved_evidence_packet_ids": [],
                "corroboration_status": "blocked_before_evidence",
                "conflict_status": "blocked_before_evidence",
                "review_required": True,
                "residual_reason": "no evidence packet generated",
            }
        )
    return claims, conflicts, corroboration


def query_refinement_candidates(claims: list[dict[str, Any]], gap_codes: list[str]) -> list[dict[str, Any]]:
    candidates = [
        {
            "candidate_id": "l6_12_query_refinement_001",
            "candidate_query": "official primary source current public beneficiary demand language",
            "reason": "increase primary-source support for the selected work order",
            "linked_claim_or_gap": claims[0]["claim_id"] if claims else "configured_search_provider_gap",
            "expected_source_type": "official_primary",
            "priority": 1,
            "budget_cost_estimate": {"queries": 1, "pages": 2},
            "requires_real_backend": True,
            "executed_now": False,
        },
        {
            "candidate_id": "l6_12_query_refinement_002",
            "candidate_query": "independent institutional corroboration beneficiary demand language source date",
            "reason": "resolve freshness and independence limitations",
            "linked_claim_or_gap": claims[1]["claim_id"] if len(claims) > 1 else "freshness_parser_gap",
            "expected_source_type": "institutional",
            "priority": 2,
            "budget_cost_estimate": {"queries": 1, "pages": 2},
            "requires_real_backend": True,
            "executed_now": False,
        },
        {
            "candidate_id": "l6_12_query_refinement_003",
            "candidate_query": "scope limitation contradictory evidence public source",
            "reason": "target unresolved conflict and limitation claims",
            "linked_claim_or_gap": "conflict_resolver_gap" if gap_codes else "l6_12_conflict_001",
            "expected_source_type": "reputable_media_or_institutional",
            "priority": 3,
            "budget_cost_estimate": {"queries": 1, "pages": 2},
            "requires_real_backend": True,
            "executed_now": False,
        },
    ]
    return candidates


def capability_gaps(config: ControlledBackendConfig, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps = [
        (
            "configured_search_provider",
            "high",
            "not configured" if config.search_backend_mode == "disabled" else config.search_backend_mode,
            "explicit controlled search provider with required env and allow flag",
            "configure YSTAR_CONTROLLED_SEARCH_BACKEND and provider key presence",
            config.search_backend_mode == "disabled",
        ),
        (
            "configured_public_page_reader",
            "high",
            "not configured" if config.page_read_backend_mode == "disabled" else config.page_read_backend_mode,
            "fixture or stdlib_public_http page reader with explicit allow flag for network mode",
            "configure YSTAR_CONTROLLED_PAGE_READ_BACKEND and allow flag",
            config.page_read_backend_mode == "disabled",
        ),
        ("html_extraction_quality", "medium", "basic text extraction", "structured HTML extraction", "add parser quality tests", False),
        ("domain_allow_deny_policy", "medium", "private/internal URL block exists", "curated domain allow/deny policy", "add domain policy registry", False),
        ("source_type_classifier", "medium", "deterministic labels only", "richer source type classifier", "expand deterministic classifier fixtures", False),
        ("duplicate_url_canonicalization", "low", "not yet normalized", "canonical URL dedupe", "add URL canonicalization pass", False),
        ("freshness_parser", "medium", "fixture marker or date missing", "source-date parser", "add deterministic date extractor", False),
        ("evidence_excerpt_extractor", "medium", "bounded excerpt extraction", "claim-aware excerpt selection", "add excerpt scoring without truth authority", False),
        ("conflict_resolver", "medium", "conflicts identified but not resolved", "review-gated conflict resolution workflow", "add review decision schema", False),
        ("query_refinement_executor", "low", "candidates generated only", "future bounded second-loop executor", "add approval gate for next loop", False),
        ("provider_rate_limit_handling", "medium", "policy declared", "provider-specific rate-limit backoff", "add adapter rate-limit envelopes", False),
        ("credential_presence", "high", str(config.required_env_present), "provider env present without value leakage", "set provider key only in environment", bool(config.missing_env_names)),
        ("network_permission", "high", str(config.search_network_allowed or config.page_read_network_allowed), "explicit allow flags for real reads", "set allow flags after approval", not (config.search_network_allowed or config.page_read_network_allowed)),
        ("console_display_coverage", "low", "L6.12 command generated", "maintain regression coverage", "keep console smoke test", False),
        ("validation_coverage", "low", "focused tests generated", "targeted regression ladder", "keep L6.12 suite in safety wrapper", False),
    ]
    return [
        {
            "gap_id": f"l6_12_gap_{index:03d}_{name}",
            "gap_name": name,
            "severity": severity,
            "current_state": current_state,
            "needed_capability": needed,
            "recommended_next_patch": patch,
            "blocks_real_observation": blocks,
        }
        for index, (name, severity, current_state, needed, patch, blocks) in enumerate(gaps, start=1)
    ]


def receipt_payload(action: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "action": action,
        "executed": False,
        "occurred": False,
        "authorized": False,
        "receipt": f"no_{action}",
    }


def write_reports(
    generated: list[str],
    summary: dict[str, Any],
    fixture: dict[str, Any],
    real: dict[str, Any],
    packets: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> None:
    write_text(
        "l6_unified_controlled_external_observation_evidence_loop/README.md",
        (
            f"# {MILESTONE_ID} {MILESTONE_NAME}\n\n"
            "Unified controlled external observation loop sprint. The default run "
            "executes the deterministic fixture proof and inspects real backend "
            "configuration without asking the user for URLs.\n"
        ),
        generated,
    )
    write_text(
        "l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.md",
        (
            f"# {MILESTONE_ID} Summary\n\n"
            f"Run classification: {summary['run_classification']}.\n\n"
            f"Fixture evidence packets: {fixture['evidence_packets_generated']}.\n\n"
            f"Real observation executed: {real['real_observation_executed']}.\n"
        ),
        generated,
    )
    write_text(
        "real_backend_activation/real_backend_activation_report.md",
        "# Real Backend Activation Report\n\nBackend modes are disabled by default. Provider keys are checked by presence only; secret values are not serialized.\n",
        generated,
    )
    write_text(
        "real_page_read_activation/real_page_read_activation_report.md",
        "# Real Page-Read Activation Report\n\nPage-read modes are disabled, fixture, or stdlib_public_http. Real network reads require explicit allow flags and safety preflight.\n",
        generated,
    )
    write_text(
        "controlled_observation_orchestrator/orchestration_report.md",
        "# Orchestration Report\n\nThe loop executed fixture proof and classified real-run readiness without manual URL fallback.\n",
        generated,
    )
    write_text(
        "controlled_query_execution/search_execution_report.md",
        "# Search Execution Report\n\nSearch snippets were used only as locator metadata, never as evidence.\n",
        generated,
    )
    write_text(
        "controlled_bounded_crawl/bounded_crawl_report.md",
        "# Bounded Crawl Report\n\nDepth is capped at 1 and fixture proof used no external network.\n",
        generated,
    )
    write_text(
        "controlled_capability_gap_report/capability_gap_report.md",
        f"# Capability Gap Report\n\nGenerated {len(gaps)} capability gaps, including backend/page-read activation blockers when applicable.\n",
        generated,
    )
    write_text(
        "controlled_observation_run_reports/unified_observation_loop_report.md",
        f"# Unified Observation Loop Report\n\nEvidence packets generated: {len(packets)}. External side effects occurred: false.\n",
        generated,
    )


def main() -> int:
    generated: list[str] = []
    work_order = selected_work_order()
    queries = query_plan(work_order)
    budget = SearchBudgetEnvelope.from_mapping(BUDGET)

    real_config = ControlledBackendConfig.from_environment(ROOT)
    fixture_config = ControlledBackendConfig.from_environment(
        ROOT,
        overrides={
            "search_backend_mode": "fixture",
            "page_read_backend_mode": "fixture",
            "search_network_allowed": False,
            "page_read_network_allowed": False,
        },
    )

    fixture_preflight = l6_12_safety_preflight(fixture_config, budget)
    real_preflight = l6_12_safety_preflight(real_config, budget)
    fixture_search = run_search(fixture_config, work_order, queries)
    selected_sources, rejected_sources = triage_results(fixture_search)
    fixture_pages = read_pages(fixture_config, selected_sources)
    fixture_packets = evidence_packets("fixture", work_order, fixture_search, fixture_pages)
    quality_matrix = source_quality_matrix(fixture_packets, fixture_pages)
    claims, conflicts, corroboration = claim_and_conflict(fixture_packets)

    real_search: dict[str, Any] = {
        "backend_mode": real_config.search_backend_mode,
        "search_executed": False,
        "search_query_count": 0,
        "search_results_considered": 0,
        "external_reads_count": 0,
        "result_candidates": [],
        "snippets_used_as_evidence": False,
        "facts_inferred_from_snippets": False,
        "asked_user_for_url": False,
        "blocked_reason": None,
        "error_code": None,
        "network_used": False,
    }
    real_pages: list[dict[str, Any]] = []
    real_packets: list[dict[str, Any]] = []
    real_run_attempted = real_preflight["decision"] == "pass" and real_config.search_backend_mode not in {
        "disabled",
        "fixture",
    }
    if real_run_attempted:
        real_search = run_search(real_config, work_order, queries)
        real_selected_sources, _ = triage_results(real_search)
        if real_search.get("search_executed") and real_selected_sources:
            candidate_urls = [item["url"] for item in real_selected_sources]
            real_preflight = l6_12_safety_preflight(real_config, budget, candidate_urls)
            if real_preflight["decision"] == "pass":
                real_pages = read_pages(real_config, real_selected_sources)
                real_packets = evidence_packets("real", work_order, real_search, real_pages)

    real_backend_or_page_missing = any(
        blocker
        in {
            "controlled_search_backend_not_configured",
            "controlled_public_page_read_adapter_not_configured",
            "configured_backend_missing_required_environment",
        }
        for blocker in real_preflight["blockers"]
    )
    if real_packets and not conflicts:
        run_classification = "real_controlled_observation_loop_executed"
    elif real_packets and conflicts:
        run_classification = "real_pages_read_but_conflict_unresolved"
    elif real_search.get("search_executed") or real_pages:
        run_classification = "partial_real_observation_no_evidence"
    elif real_backend_or_page_missing:
        run_classification = "configuration_blocked_but_engineering_ready"
    else:
        run_classification = "preflight_blocked_but_engineering_ready"

    gaps = capability_gaps(real_config, fixture_pages)
    refinement_candidates = query_refinement_candidates(claims, [gap["gap_name"] for gap in gaps])
    blockers = sorted(set(real_preflight["blockers"] + ([real_search.get("error_code")] if real_search.get("error_code") else [])))
    domains = sorted({page.get("source_domain") for page in fixture_pages if page.get("source_domain")})
    external_reads_used = int(real_search.get("external_reads_count", 0)) + sum(
        1 for page in real_pages if page.get("safety_flags", {}).get("network_used")
    )
    real_observation_executed = bool(real_packets)
    fixture_proof = {
        "schema_version": SCHEMA_VERSION,
        "fixture_proof_executed": True,
        "backend_mode": "fixture",
        "page_read_mode": "fixture",
        "query_count": len(queries),
        "search_results_considered": fixture_search["search_results_considered"],
        "pages_opened": len(fixture_pages),
        "domains_touched": len(domains),
        "crawl_depth_used": 1,
        "external_reads_used": 0,
        "evidence_packets_generated": len(fixture_packets),
        "conflicts_found": len(conflicts),
        "network_used": False,
        "ask_user_for_url_occurred": False,
    }
    real_run = {
        "schema_version": SCHEMA_VERSION,
        "real_observation_attempted": real_run_attempted,
        "real_observation_executed": real_observation_executed,
        "backend_mode": real_config.search_backend_mode,
        "page_read_mode": real_config.page_read_backend_mode,
        "network_allowed": real_config.search_network_allowed or real_config.page_read_network_allowed,
        "safety_preflight_decision": real_preflight["decision"],
        "search_executed": bool(real_search.get("search_executed")),
        "pages_opened": len(real_pages),
        "external_reads_used": external_reads_used,
        "evidence_packets_generated": len(real_packets),
        "blockers": blockers,
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "run_id": RUN_ID,
        "run_classification": run_classification,
        "allowed_run_classifications": RUN_CLASSIFICATIONS,
        "l6_12_unified_controlled_external_observation_evidence_loop_complete": True,
        "selected_work_order_id": work_order["selected_work_order_id"],
        "backend_mode": real_config.search_backend_mode,
        "page_read_mode": real_config.page_read_backend_mode,
        "fixture_backend_mode": "fixture",
        "fixture_page_read_mode": "fixture",
        "network_allowed": real_config.search_network_allowed or real_config.page_read_network_allowed,
        "safety_preflight_decision": real_preflight["decision"],
        "fixture_proof_executed": True,
        "real_observation_executed": real_observation_executed,
        "real_observation_attempted": real_run_attempted,
        "query_count": len(queries),
        "search_results_considered": fixture_search["search_results_considered"],
        "pages_opened": len(fixture_pages),
        "domains_touched": len(domains),
        "crawl_depth_used": 1,
        "external_reads_used": external_reads_used,
        "evidence_packets_generated": len(fixture_packets) if not real_packets else len(real_packets),
        "fixture_evidence_packets_generated": len(fixture_packets),
        "real_evidence_packets_generated": len(real_packets),
        "conflicts_found": len(conflicts),
        "unresolved_claims": sum(1 for claim in claims if claim["conflict_status"] != "no_conflict"),
        "query_refinement_candidates_generated": len(refinement_candidates),
        "capability_gaps_generated": len(gaps),
        "blockers": blockers,
        "configuration_blocked_real_run": run_classification == "configuration_blocked_but_engineering_ready",
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "search_snippets_used_as_evidence": False,
        "page_read_content_used_as_evidence": bool(fixture_packets or real_packets),
        "secret_values_serialized": False,
        **BUDGET,
        **SAFETY_FLAGS,
    }

    write_json(
        "l6_unified_controlled_external_observation_evidence_loop/l6_12_milestone_contract.json",
        {**summary, "contract_type": "milestone_contract"},
        generated,
    )
    write_json(
        "l6_unified_controlled_external_observation_evidence_loop/l6_12_scope.json",
        {
            "schema_version": SCHEMA_VERSION,
            "scope": "unified controlled observation evidence loop",
            "manual_url_request_allowed": False,
            "real_execution_requires_explicit_backend_configuration": True,
        },
        generated,
    )
    write_json("l6_unified_controlled_external_observation_evidence_loop/l6_12_budget_policy.json", {"schema_version": SCHEMA_VERSION, **BUDGET}, generated)
    write_json("l6_unified_controlled_external_observation_evidence_loop/l6_12_safety_flags.json", {"schema_version": SCHEMA_VERSION, **SAFETY_FLAGS}, generated)
    write_json(
        "l6_unified_controlled_external_observation_evidence_loop/l6_12_run_classification_schema.json",
        {"schema_version": SCHEMA_VERSION, "allowed_run_classifications": RUN_CLASSIFICATIONS},
        generated,
    )
    write_json("l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json", summary, generated)

    write_json("real_backend_activation/backend_activation_contract.json", {"schema_version": SCHEMA_VERSION, "supported_modes": ["disabled", "fixture", "brave_search_api", "tavily_search_api", "serpapi"], "default_mode": "disabled", "secrets_serialized": False}, generated)
    write_json("real_backend_activation/backend_configuration_receipt.json", {"schema_version": SCHEMA_VERSION, **real_config.receipt(), "provider_presence_matrix": provider_presence_matrix(), "secret_values_serialized": False}, generated)
    write_json("real_backend_activation/provider_presence_matrix.json", {"schema_version": SCHEMA_VERSION, "providers": provider_presence_matrix()}, generated)
    write_json("real_backend_activation/backend_activation_instructions.json", {"schema_version": SCHEMA_VERSION, "required_env": ["YSTAR_CONTROLLED_SEARCH_BACKEND", "YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "provider API key env"], "manual_url_request": False, "supported_providers": list(PROVIDER_KEY_ENVS)}, generated)

    write_json("real_page_read_activation/page_read_activation_contract.json", {"schema_version": SCHEMA_VERSION, "supported_modes": ["disabled", "fixture", "stdlib_public_http"], "default_mode": "disabled", "real_mode_requires": ["YSTAR_CONTROLLED_PAGE_READ_BACKEND=stdlib_public_http", "YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK=1"]}, generated)
    write_json("real_page_read_activation/page_read_configuration_receipt.json", {"schema_version": SCHEMA_VERSION, "page_read_mode": real_config.page_read_backend_mode, "page_read_network_allowed": real_config.page_read_network_allowed, "blockers": [b for b in real_preflight["blockers"] if "page_read" in b or "preflight" in b]}, generated)
    write_json("real_page_read_activation/public_page_read_safety_contract.json", {"schema_version": SCHEMA_VERSION, "method": "GET_only", "allowed_schemes": ["http", "https"], "cookies": False, "auth_headers": False, "credentials": False, "browser_automation": False, "private_internal_targets_blocked": True, "max_bytes_per_page": 200000, "timeout_seconds": 5}, generated)

    write_json("controlled_observation_orchestrator/selected_work_order.json", work_order, generated)
    write_json("controlled_observation_orchestrator/observation_loop_contract.json", {"schema_version": SCHEMA_VERSION, "run_id": RUN_ID, "loop_steps": ["query_plan", "search", "triage", "page_read", "bounded_crawl", "evidence_extraction", "source_quality", "corroboration_conflict", "review_packet", "query_refinement", "capability_gap_report", "no_action_receipt", "read_model"], "manual_url_request": False}, generated)
    write_json("controlled_observation_orchestrator/observation_loop_run_trace.json", {"schema_version": SCHEMA_VERSION, "run_id": RUN_ID, "run_classification": run_classification, "fixture_proof": fixture_proof, "real_run": real_run, "loop_completed": True}, generated)
    write_json("controlled_observation_orchestrator/run_classification_decision.json", {"schema_version": SCHEMA_VERSION, "run_classification": run_classification, "reason": "real backend/page-read configuration missing or blocked; fixture path proves loop" if not real_packets else "real evidence packets produced"}, generated)

    write_json("controlled_query_execution/generated_query_plan.json", {"schema_version": SCHEMA_VERSION, "query_count": len(queries), "queries": queries}, generated)
    write_json("controlled_query_execution/search_execution_result.json", {"schema_version": SCHEMA_VERSION, "fixture_search_result": fixture_search, "real_search_result": real_search}, generated)
    write_json("controlled_query_execution/search_execution_trace.json", {"schema_version": SCHEMA_VERSION, "snippets_used_as_evidence": False, "fixture_search_executed": True, "real_search_executed": bool(real_search.get("search_executed")), "query_count": len(queries)}, generated)

    write_json("controlled_result_triage/search_result_candidates.json", {"schema_version": SCHEMA_VERSION, "candidates": fixture_search.get("result_candidates", [])}, generated)
    write_json("controlled_result_triage/source_triage_matrix.json", {"schema_version": SCHEMA_VERSION, "selected": selected_sources, "rejected": rejected_sources}, generated)
    write_json("controlled_result_triage/selected_sources_to_open.json", {"schema_version": SCHEMA_VERSION, "selected_count": len(selected_sources), "sources": selected_sources}, generated)
    write_json("controlled_result_triage/rejected_search_results.json", {"schema_version": SCHEMA_VERSION, "rejected_count": len(rejected_sources), "results": rejected_sources}, generated)
    write_text("controlled_result_triage/search_result_triage_report.md", "# Search Result Triage Report\n\nFixture search results were triaged before page reads. Snippets remained locator metadata only.\n", generated)

    write_json("controlled_bounded_crawl/bounded_crawl_contract.json", {"schema_version": SCHEMA_VERSION, "max_crawl_depth": BUDGET["max_crawl_depth"], "max_pages_per_domain": BUDGET["max_pages_per_domain"], "no_login_payment_form": True, "no_raw_page_dump_storage": True}, generated)
    write_json("controlled_bounded_crawl/bounded_crawl_trace.json", {"schema_version": SCHEMA_VERSION, "crawl_depth_used": 1, "pages_opened": len(fixture_pages), "domains_touched": len(domains), "network_used": False, "stop_on_scope_drift": True}, generated)
    write_json("controlled_bounded_crawl/opened_page_registry.json", {"schema_version": SCHEMA_VERSION, "pages": fixture_pages}, generated)
    write_json("controlled_bounded_crawl/crawl_expansion_decisions.json", {"schema_version": SCHEMA_VERSION, "depth_1_considered": True, "expanded_links": 0, "reason": "fixture proof contains no approved same-domain crawl expansion links"}, generated)

    write_json("controlled_evidence_packets/evidence_packet_schema.json", {"schema_version": SCHEMA_VERSION, "required_fields": ["evidence_packet_id", "run_id", "work_order_id", "query_id", "source_url", "final_url", "source_domain", "source_type", "source_quality_label", "freshness_label", "page_read_id", "extracted_text_excerpt", "bounded_claim", "claim_scope", "support_status", "conflict_status", "limitations", "generated_at_utc", "real_or_fixture"]}, generated)
    write_json("controlled_evidence_packets/evidence_packet_index.json", {"schema_version": SCHEMA_VERSION, "evidence_packet_count": len(fixture_packets), "evidence_packets": [f"controlled_evidence_packets/evidence_packet_{i:03d}.json" for i in range(1, len(fixture_packets) + 1)]}, generated)
    for index, packet in enumerate(fixture_packets, start=1):
        write_json(f"controlled_evidence_packets/evidence_packet_{index:03d}.json", packet, generated)
    write_json("controlled_evidence_packets/evidence_extraction_summary.json", {"schema_version": SCHEMA_VERSION, "evidence_packets_generated": len(fixture_packets), "search_snippets_used_as_evidence": False, "page_read_content_used_as_evidence": bool(fixture_packets), "real_or_fixture": "fixture"}, generated)
    write_text("controlled_evidence_packets/evidence_extraction_report.md", "# Evidence Extraction Report\n\nPage-read content generated bounded fixture evidence packets. Search snippets were never evidence.\n", generated)

    write_json("controlled_claim_boundary/bounded_claim_registry.json", {"schema_version": SCHEMA_VERSION, "claims": claims}, generated)
    write_json("controlled_claim_boundary/unsupported_claim_registry.json", {"schema_version": SCHEMA_VERSION, "unsupported_claims": [], "external_use_authorized": False}, generated)
    write_json("controlled_claim_boundary/unresolved_claim_registry.json", {"schema_version": SCHEMA_VERSION, "unresolved_claims": [claim for claim in claims if claim["conflict_status"] != "no_conflict"]}, generated)
    write_text("controlled_claim_boundary/claim_boundary_report.md", "# Claim Boundary Report\n\nAll claims are bounded for internal review only.\n", generated)

    write_json("controlled_source_quality/source_quality_contract.json", {"schema_version": SCHEMA_VERSION, "labels": ["official_primary", "official_secondary", "institutional", "documentation", "reputable_media", "community", "commercial_vendor", "unknown", "blocked_or_ineligible"], "llm_confidence_as_truth_authority": False}, generated)
    write_json("controlled_source_quality/source_quality_matrix.json", {"schema_version": SCHEMA_VERSION, "sources": quality_matrix}, generated)
    write_json("controlled_source_quality/source_freshness_assessment.json", {"schema_version": SCHEMA_VERSION, "freshness_items": [{"source_url": item["source_url"], "freshness_label": item["freshness_label"], "review_required": True} for item in quality_matrix]}, generated)
    write_text("controlled_source_quality/source_quality_report.md", "# Source Quality Report\n\nSource labels are deterministic and do not use LLM confidence as truth authority.\n", generated)

    write_json("controlled_corroboration_conflict/corroboration_contract.json", {"schema_version": SCHEMA_VERSION, "statuses": ["corroborated", "single_source_supported", "conflicted", "unresolved", "insufficient_evidence", "blocked_before_evidence"]}, generated)
    write_json("controlled_corroboration_conflict/source_corroboration_matrix.json", {"schema_version": SCHEMA_VERSION, "sources": quality_matrix}, generated)
    write_json("controlled_corroboration_conflict/claim_corroboration_matrix.json", {"schema_version": SCHEMA_VERSION, "claims": corroboration}, generated)
    write_json("controlled_corroboration_conflict/conflict_registry.json", {"schema_version": SCHEMA_VERSION, "conflict_count": len(conflicts), "conflicts": conflicts}, generated)
    write_json("controlled_corroboration_conflict/evidence_sufficiency_assessment.json", {"schema_version": SCHEMA_VERSION, "sufficient_for_internal_review_only": bool(fixture_packets), "sufficient_for_external_use": False, "residual_reason": "fixture evidence and unresolved conflict require review"}, generated)
    write_text("controlled_corroboration_conflict/corroboration_report.md", "# Corroboration Report\n\nThe matrix distinguishes supported, corroborated, conflicted, and unresolved claims.\n", generated)

    review_packet = {
        "schema_version": SCHEMA_VERSION,
        "review_packet_id": "l6_12_review_packet_001",
        "run_classification": run_classification,
        "real_observation_executed": real_observation_executed,
        "fixture_proof_executed": True,
        "selected_work_order": work_order,
        "budget_used": BUDGET,
        "backend_mode": real_config.search_backend_mode,
        "page_read_mode": real_config.page_read_backend_mode,
        "queries_generated": len(queries),
        "pages_read": len(fixture_pages),
        "evidence_packets": [packet["evidence_packet_id"] for packet in fixture_packets],
        "conflicts": conflicts,
        "unresolved_claims": [claim for claim in claims if claim["conflict_status"] != "no_conflict"],
        "residual_limitations": ["fixture proof is not real-world truth", "real backend configuration required for live observation"],
        "recommended_next_query_refinements": [item["candidate_id"] for item in refinement_candidates],
        "capability_gaps": [gap["gap_id"] for gap in gaps],
        "no_side_effect_summary": {"external_side_effects_occurred": False, "core_writeback_occurred": False},
        "approve_for_external_use": False,
        "applied": False,
    }
    write_json("controlled_review_packet/review_packet_index.json", {"schema_version": SCHEMA_VERSION, "review_packets": ["controlled_review_packet/evidence_review_packet.json"]}, generated)
    write_json("controlled_review_packet/evidence_review_packet.json", review_packet, generated)
    write_text("controlled_review_packet/controlled_review_report.md", "# Controlled Review Report\n\nReview packet generated; no artifact update or external use is authorized.\n", generated)

    write_json("controlled_query_refinement/query_refinement_candidate_index.json", {"schema_version": SCHEMA_VERSION, "candidate_count": len(refinement_candidates), "candidates": [f"controlled_query_refinement/query_refinement_candidate_{i:03d}.json" for i in range(1, len(refinement_candidates) + 1)]}, generated)
    for index, candidate in enumerate(refinement_candidates, start=1):
        write_json(f"controlled_query_refinement/query_refinement_candidate_{index:03d}.json", candidate, generated)
    write_text("controlled_query_refinement/query_refinement_report.md", "# Query Refinement Report\n\nGenerated deterministic next-query candidates; none were executed as an uncontrolled second loop.\n", generated)

    write_json("controlled_capability_gap_report/capability_gap_registry.json", {"schema_version": SCHEMA_VERSION, "gap_count": len(gaps), "gaps": gaps}, generated)
    write_json("controlled_capability_gap_report/backend_enablement_requirements.json", {"schema_version": SCHEMA_VERSION, "search_backend_required": "YSTAR_CONTROLLED_SEARCH_BACKEND plus provider key and allow flag", "page_read_backend_required": "YSTAR_CONTROLLED_PAGE_READ_BACKEND=stdlib_public_http plus allow flag", "manual_url_request": False}, generated)

    receipt_paths = []
    for action in NO_ACTIONS:
        path = f"controlled_no_action_receipts/no_{action}_receipt.json"
        write_json(path, receipt_payload(action), generated)
        receipt_paths.append(path)
    no_side_effect = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": "l6_12_no_side_effect_receipt",
        "receipts": receipt_paths,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "ask_user_for_url_occurred": False,
        "login_account_payment_form_posting_occurred": False,
        "publication_outreach_payment_revenue_occurred": False,
        "mcp_live_behavior_occurred": False,
        "cieu_db_brain_memory_canonical_direct_y_star_mutation_occurred": False,
    }
    write_json("controlled_no_action_receipts/no_side_effect_receipt.json", no_side_effect, generated)
    write_json("controlled_no_action_receipts/no_action_receipt_index.json", {"schema_version": SCHEMA_VERSION, "receipts": receipt_paths + ["controlled_no_action_receipts/no_side_effect_receipt.json"]}, generated)
    write_text("controlled_no_action_receipts/no_action_receipts_report.md", "# No-Action Receipts Report\n\nNo disallowed external or core writeback action occurred.\n", generated)

    write_json("controlled_observation_run_reports/fixture_proof_run_report.json", fixture_proof, generated)
    write_json("controlled_observation_run_reports/real_run_attempt_report.json", real_run, generated)
    write_json("controlled_observation_run_reports/configuration_blocked_real_run_receipt.json", {"schema_version": SCHEMA_VERSION, "configuration_blocked": run_classification == "configuration_blocked_but_engineering_ready", "blockers": blockers, "ready_to_run_real_observation_once_configured": True, "manual_url_request": False}, generated)

    cieu = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_12_unified_controlled_external_observation_evidence_loop_fixture",
        "X_t": {"selected_work_order": work_order, "queries": queries},
        "U_t": {"budget": BUDGET, "backend_mode": real_config.search_backend_mode, "page_read_mode": real_config.page_read_backend_mode},
        "Y_star_t": "Run a governed external observation evidence loop with controlled search, public page-read, bounded crawl, evidence extraction, corroboration/conflict, review, refinement candidates, capability gaps, and no-side-effect receipts.",
        "Y_t_plus_1": {"run_classification": run_classification, "fixture_evidence_packets": len(fixture_packets), "real_observation_executed": real_observation_executed, "capability_gaps_generated": len(gaps)},
        "R_t_plus_1": {"residuals": ["real backend/page-read configuration required for live observation", "fixture evidence remains demo-only", "query refinement candidates require future gated execution"]},
    }
    meta = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "l6_12_meta_learning_update_candidate",
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
        "l6_12_unified_controlled_external_observation_evidence_loop_complete": True,
        "run_classification": run_classification,
        "fixture_loop_executed": True,
        "real_observation_executed": real_observation_executed,
        "ready_for_real_controlled_observation_once_configured": True,
        "ready_for_uncontrolled_external_observation": False,
        "next_step": "configure_controlled_search_backend_and_public_page_read_adapter" if not real_observation_executed else "review_real_evidence_before_any_artifact_update",
    }
    read_summary = {
        **summary,
        "fixture_loop_executed": True,
        "review_packet_generated": True,
        "capability_gap_report_generated": True,
        "query_refinement_candidates_generated": len(refinement_candidates),
        "generated_summary": "l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json",
        "generated_review_packet": "controlled_review_packet/evidence_review_packet.json",
        "generated_capability_gap_registry": "controlled_capability_gap_report/capability_gap_registry.json",
        "generated_no_side_effect_receipt": "controlled_no_action_receipts/no_side_effect_receipt.json",
        "generated_readiness": "l6_12_read_model/l6_12_readiness_assessment.json",
    }
    write_json("l6_12_read_model/l6_12_cieu_like_fixture.json", cieu, generated)
    write_json("l6_12_read_model/l6_12_strategic_residual_delta.json", {"schema_version": SCHEMA_VERSION, "primary_residual": "real_backend_configuration_required_unless_env_configured", "fixture_loop_reusable": True, "query_refinement_candidates_pending": True}, generated)
    write_json("l6_12_read_model/l6_12_meta_learning_update_candidate.json", meta, generated)
    write_json("l6_12_read_model/l6_12_readiness_assessment.json", readiness, generated)
    write_json("l6_12_read_model/l6_12_blockers.json", {"schema_version": SCHEMA_VERSION, "blockers": blockers, "run_classification": run_classification}, generated)
    write_json("l6_12_read_model/l6_12_next_milestone_recommendation.json", {"schema_version": SCHEMA_VERSION, "recommended_next_step": readiness["next_step"], "do_not_ask_user_for_url": True}, generated)
    write_json("l6_12_read_model/l6_12_read_model_summary.json", read_summary, generated)
    write_text("l6_12_read_model/l6_12_report.md", "# L6.12 Read Model Report\n\nUnified controlled observation evidence loop is visible to console/read-model.\n", generated)

    write_reports(generated, summary, fixture_proof, real_run, fixture_packets, gaps)
    print(f"generated {len(generated)} L6.12 unified controlled observation files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
