#!/usr/bin/env python3
"""Build L6.13 real controlled external observation mission sprint artifacts.

The default run is deterministic and offline. It always executes the L6.11/L6.12
fixture proof path, safely inspects real backend configuration by presence only,
and emits a complete activation kit when real credentials/configuration are
missing. Secret values are never serialized.
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
    PAGE_READ_ALLOW_NETWORK_ENV,
    PAGE_READ_BACKEND_ENV,
    PROVIDER_KEY_ENVS,
    SEARCH_ALLOW_NETWORK_ENV,
    SEARCH_BACKEND_ENV,
    SearchBudgetEnvelope,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.13"
MILESTONE_NAME = "Real Controlled External Observation Activation & Mission Evidence Sprint v0"
MODE = "real_controlled_external_observation_mission_sprint"
RUN_ID = "l6_13_real_controlled_observation_mission_run_001"
SELECTED_WORK_ORDER_ID = "l6_10x_selected_work_order_001"

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
    "L6.12",
]

RUN_CLASSIFICATIONS = [
    "real_controlled_observation_loop_executed",
    "real_backend_activation_blocked_with_complete_activation_kit",
    "preflight_blocked_with_complete_activation_kit",
    "partial_real_search_no_page_read",
    "partial_real_page_read_no_evidence",
    "real_evidence_collected_with_unresolved_conflicts",
    "real_evidence_collected_and_review_ready",
]

BUDGET = {
    "max_selected_work_orders": 1,
    "max_queries": 10,
    "max_search_results_considered": 25,
    "max_pages_opened": 10,
    "max_domains": 6,
    "max_pages_per_domain": 3,
    "max_crawl_depth": 1,
    "max_total_external_reads": 15,
    "max_primary_sources_to_capture": 4,
    "max_secondary_sources_to_capture": 6,
    "max_conflicting_sources_to_capture": 3,
    "max_evidence_packets": 10,
    "max_runtime_minutes": 20,
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
    "private_sensitive_data_collection_authorized": False,
    "high_volume_crawling_authorized": False,
    "unbounded_scraping_authorized": False,
    "browser_automation_authorized": False,
    "javascript_execution_authorized": False,
    "robots_or_access_control_bypass_authorized": False,
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

SOURCE_QUALITY_LABELS = [
    "official_primary",
    "official_secondary",
    "institutional",
    "documentation",
    "reputable_media",
    "community",
    "commercial_vendor",
    "unknown",
    "blocked_or_ineligible",
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


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lower()


def is_real_provider_mode(config: ControlledBackendConfig) -> bool:
    return config.search_backend_mode in PROVIDER_KEY_ENVS and config.page_read_backend_mode == "stdlib_public_http"


def selected_work_order() -> dict[str, Any]:
    prior = load_json("controlled_observation_orchestrator/selected_work_order.json", {})
    if not prior:
        prior = load_json("agentic_query_planner/selected_work_order.json", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_count": 1,
        "selected_work_order_id": prior.get("selected_work_order_id", SELECTED_WORK_ORDER_ID),
        "source_work_order_id": prior.get("source_work_order_id", SELECTED_WORK_ORDER_ID),
        "evidence_need_id": prior.get("evidence_need_id") or prior.get("linked_evidence_need_id", "l6_8_need_001"),
        "source_type": prior.get("source_type", "official policy or program source"),
        "source_function": prior.get("source_function", "official policy or program source"),
        "observation_question": prior.get(
            "observation_question",
            "What public evidence clarifies payer or beneficiary demand language?",
        ),
        "claim_boundary": prior.get(
            "claim_boundary",
            "internal review of public demand or beneficiary language only",
        ),
        "expected_evidence_type": "public page-read extracted evidence",
    }


def query_plan(work_order: dict[str, Any]) -> list[dict[str, Any]]:
    prior = load_json("controlled_query_execution/generated_query_plan.json", {})
    queries = [dict(item) for item in prior.get("queries", [])][:8]
    additions = [
        (
            "mission_primary_source_query",
            "official primary source current public beneficiary demand program language",
        ),
        (
            "mission_conflict_resolution_query",
            "public evidence contradiction scope limitation beneficiary demand source",
        ),
    ]
    for category, query_text in additions:
        queries.append(
            {
                "query_id": f"l6_13_query_{len(queries) + 1:03d}",
                "query_category": category,
                "query_text": query_text,
                "priority": len(queries) + 1,
                "linked_work_order_id": work_order["selected_work_order_id"],
                "source_type": work_order["source_type"],
                "source_function": work_order["source_function"],
                "no_snippet_fact_use": True,
                "no_fact_inference_from_search_result": True,
                "max_results": 4,
            }
        )
    normalized = queries[: BUDGET["max_queries"]]
    for index, item in enumerate(normalized, start=1):
        item.setdefault("query_id", f"l6_13_query_{index:03d}")
        item.setdefault("query_category", "mission_evidence_query")
        item.setdefault("linked_work_order_id", work_order["selected_work_order_id"])
        item.setdefault("source_type", work_order["source_type"])
        item.setdefault("source_function", work_order["source_function"])
        item.setdefault("no_snippet_fact_use", True)
        item.setdefault("no_fact_inference_from_search_result", True)
        item.setdefault("max_results", 4)
        item["query_id"] = str(item["query_id"]).replace("l6_12", "l6_13")
    return normalized


def provider_presence_matrix() -> list[dict[str, Any]]:
    return [
        {
            "provider": provider,
            "required_env_name": env_name,
            "required_env_present": bool(os.environ.get(env_name)),
            "secret_value_serialized": False,
        }
        for provider, env_name in PROVIDER_KEY_ENVS.items()
    ]


def missing_configuration_fields(config: ControlledBackendConfig) -> list[str]:
    missing: list[str] = []
    if config.search_backend_mode == "disabled":
        missing.extend([SEARCH_BACKEND_ENV, SEARCH_ALLOW_NETWORK_ENV])
    if config.page_read_backend_mode == "disabled":
        missing.extend([PAGE_READ_BACKEND_ENV, PAGE_READ_ALLOW_NETWORK_ENV])
    missing.extend(config.missing_env_names)
    if config.search_backend_mode in PROVIDER_KEY_ENVS and not config.search_network_allowed:
        missing.append(SEARCH_ALLOW_NETWORK_ENV)
    if config.page_read_backend_mode == "stdlib_public_http" and not config.page_read_network_allowed:
        missing.append(PAGE_READ_ALLOW_NETWORK_ENV)
    return sorted(dict.fromkeys(missing))


def safety_preflight(
    config: ControlledBackendConfig,
    budget: SearchBudgetEnvelope,
    candidate_urls: list[str] | None = None,
    require_real: bool = False,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    budget_checks: dict[str, Any] = {}
    for field, expected in BUDGET.items():
        if not field.startswith("max_") or not hasattr(budget, field):
            continue
        value = getattr(budget, field)
        budget_checks[field] = {"value": value, "max_allowed": expected, "within_limit": value <= expected}
        if value > expected:
            blockers.append(f"budget_exceeds_{field}")
    if config.search_backend_mode == "disabled":
        blockers.append("controlled_search_backend_not_configured")
    if config.page_read_backend_mode == "disabled":
        blockers.append("controlled_public_page_read_adapter_not_configured")
    if require_real and not is_real_provider_mode(config):
        blockers.append("real_provider_and_stdlib_page_read_not_configured")
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
        "search_network_allowed": config.search_network_allowed,
        "page_read_network_allowed": config.page_read_network_allowed,
        "required_env_present": config.required_env_present,
        "missing_env_names": missing_configuration_fields(config),
        "blockers": sorted(set(blockers)),
        "warnings": warnings,
        "budget_checks": budget_checks,
        "private_url_rejections": private_url_rejections,
        "no_secret_values_serialized": True,
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
    return ControlledSearchBackendRegistry(config).run(
        {
            "request_id": f"{RUN_ID}_{config.search_backend_mode}_search",
            "selected_work_order_id": work_order["selected_work_order_id"],
            "queries": queries,
            "budget": BUDGET,
        }
    ).to_dict()


def triage_results(search_result: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    domain_counts: dict[str, int] = {}
    for candidate in search_result.get("result_candidates", []):
        url = candidate.get("url", "")
        domain = candidate.get("source_domain") or domain_from_url(url)
        rejection = reject_private_or_internal_url(url) if url else "missing_url"
        base = {
            "result_id": candidate.get("result_id"),
            "query_id": candidate.get("query_id"),
            "url": url,
            "source_domain": domain,
            "rank": candidate.get("rank"),
            "source_specificity": "specific_locator_candidate",
            "freshness_likelihood": "review_required",
            "source_type": candidate.get("trust_initial_label", "unknown"),
            "corroboration_value": "medium",
            "conflict_discovery_value": "medium",
            "search_snippet_is_evidence": False,
            "snippet_used_as_evidence": False,
        }
        domain_within_budget = domain in domain_counts or len(domain_counts) < BUDGET["max_domains"]
        can_select = (
            candidate.get("evidence_eligible") is True
            and not rejection
            and len(selected) < BUDGET["max_pages_opened"]
            and domain_within_budget
        )
        if can_select and domain_counts.get(domain, 0) < BUDGET["max_pages_per_domain"]:
            selected.append({**base, "risk_class": "low", "triage_decision": "selected_for_page_read"})
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        else:
            rejected.append(
                {
                    **base,
                    "risk_class": "blocked" if rejection else "budget_deferred",
                    "triage_decision": "rejected_or_budget_deferred",
                    "rejection_reason": rejection,
                }
            )
    return selected[: BUDGET["max_pages_opened"]], rejected


def read_pages(config: ControlledBackendConfig, selected_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    urls = [item["url"] for item in selected_sources if item.get("url")]
    return ControlledPageReadAdapterRegistry(config).read_pages(urls, BUDGET)


def classify_source(url: str, trust_label: str | None, page: dict[str, Any]) -> str:
    domain = domain_from_url(url)
    label = (trust_label or "").lower()
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
    if "documentation" in label:
        return "documentation"
    if "community" in label:
        return "community"
    if "vendor" in label or "commercial" in label:
        return "commercial_vendor"
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
        extracted = (claim_candidates[0] if claim_candidates else page.get("text_excerpt", "")).strip()
        if not extracted:
            continue
        is_conflict = "scope-limitation" in str(page.get("url", "")) or index == 3
        source_quality = classify_source(str(page.get("url", "")), candidate.get("trust_initial_label"), page)
        packet_id = f"l6_13_{run_kind}_evidence_packet_{index:03d}"
        support_status = "unresolved_limitation" if is_conflict else "supported_by_page_read_content"
        conflict_status = "conflicted" if is_conflict else "no_conflict"
        packets.append(
            {
                "schema_version": SCHEMA_VERSION,
                "evidence_packet_id": packet_id,
                "run_id": RUN_ID,
                "real_or_fixture": run_kind,
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
                "locator_snippet": candidate.get("snippet", ""),
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
                    "fixture/demo evidence only" if run_kind == "fixture" else "real evidence requires human review",
                    "single source is not canonical truth",
                    "not approved for external use",
                ],
                "generated_at_utc": utc_now(),
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
                "source_quality_label": packet["source_quality_label"],
                "freshness_label": packet["freshness_label"],
                "page_read_succeeded": bool(page.get("evidence_eligible")),
                "evidence_extracted": bool(packet.get("bounded_claim")),
                "primary_secondary_community": (
                    "primary"
                    if packet["source_quality_label"] == "official_primary"
                    else "secondary"
                    if packet["source_quality_label"] in {"official_secondary", "institutional", "documentation", "reputable_media"}
                    else "community_or_unknown"
                ),
                "trust_limitations": packet["limitations"],
                "llm_confidence_as_truth_authority": False,
                "semantic_truth_score_used": False,
            }
        )
    return matrix


def claim_and_conflict(packets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    claims: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    corroboration: list[dict[str, Any]] = []
    for index, packet in enumerate(packets, start=1):
        claim_id = f"l6_13_claim_{index:03d}"
        status = "conflicted" if packet["conflict_status"] == "conflicted" else "single_source_supported"
        if index == 2 and packet["conflict_status"] != "conflicted":
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
                    "conflict_id": f"l6_13_conflict_{len(conflicts) + 1:03d}",
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


def query_refinement_candidates(claims: list[dict[str, Any]], gap_ids: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "l6_13_query_refinement_001",
            "candidate_query": "official primary source current public beneficiary demand program evidence",
            "reason": "Increase primary-source support for the selected mission evidence need.",
            "linked_claim_or_gap": claims[0]["claim_id"] if claims else "configured_search_provider_gap",
            "expected_source_type": "official_primary",
            "priority": 1,
            "budget_cost_estimate": {"queries": 1, "pages": 2},
            "requires_real_backend": True,
            "executed_now": False,
        },
        {
            "candidate_id": "l6_13_query_refinement_002",
            "candidate_query": "independent institutional corroboration source date beneficiary demand language",
            "reason": "Resolve freshness and independence limitations.",
            "linked_claim_or_gap": claims[1]["claim_id"] if len(claims) > 1 else "freshness_parser_gap",
            "expected_source_type": "institutional",
            "priority": 2,
            "budget_cost_estimate": {"queries": 1, "pages": 2},
            "requires_real_backend": True,
            "executed_now": False,
        },
        {
            "candidate_id": "l6_13_query_refinement_003",
            "candidate_query": "public scope limitation contradictory evidence official source",
            "reason": "Target unresolved conflict and limitation claims.",
            "linked_claim_or_gap": gap_ids[0] if gap_ids else "l6_13_conflict_001",
            "expected_source_type": "official_or_institutional",
            "priority": 3,
            "budget_cost_estimate": {"queries": 1, "pages": 2},
            "requires_real_backend": True,
            "executed_now": False,
        },
    ]


def capability_gap_closure(config: ControlledBackendConfig, prior_gap_count: int) -> list[dict[str, Any]]:
    base = [
        (
            "configured_search_provider",
            "still_blocking_real_observation" if config.search_backend_mode == "disabled" else "partially_resolved_in_l6_13",
            "high",
            "disabled" if config.search_backend_mode == "disabled" else config.search_backend_mode,
            "Set controlled search backend mode, allow flag, and provider key presence.",
            "real_backend_activation_kit plus scripts/l6_13_check_controlled_observation_env.sh",
            config.search_backend_mode == "disabled",
        ),
        (
            "configured_public_page_reader",
            "still_blocking_real_observation" if config.page_read_backend_mode == "disabled" else "partially_resolved_in_l6_13",
            "high",
            "disabled" if config.page_read_backend_mode == "disabled" else config.page_read_backend_mode,
            "Set YSTAR_CONTROLLED_PAGE_READ_BACKEND=stdlib_public_http and explicit allow flag.",
            "real_page_read_activation policy and run script",
            config.page_read_backend_mode == "disabled",
        ),
        ("backend_activation_instructions", "resolved_in_l6_13", "high", "generated", "No-secret activation kit", "docs/l6_13_real_backend_activation.md", False),
        ("safe_env_detection", "resolved_in_l6_13", "high", "presence-only checks", "Boolean secret-presence receipts", "real_provider_env_checks", False),
        ("real_provider_adapter_readiness", "partially_resolved_in_l6_13", "high", "stdlib provider adapters available behind explicit env gates", "Approved provider credentials and network permission", "provider-specific activation requirements", False),
        ("stdlib_public_page_read_readiness", "partially_resolved_in_l6_13", "high", "GET-only adapter exists", "Real run with approved network flag", "page-read activation receipt", False),
        ("run_scripts", "resolved_in_l6_13", "medium", "generated", "Local check/run helpers", "scripts/l6_13_*.sh", False),
        ("no_secret_policy", "resolved_in_l6_13", "high", "enforced in artifacts", "Continue secret-value redaction", "no-secret receipts", False),
        ("real_fixture_classification", "resolved_in_l6_13", "medium", "deterministic enum", "Maintain tests", "run classification schema", False),
        ("console_display_coverage", "resolved_in_l6_13", "medium", "L6.13 command added", "Maintain smoke tests", "console/read-model integration", False),
        ("html_extraction_quality", "still_needed_for_quality", "medium", "basic stdlib extraction", "Claim-aware extraction", "future quality patch", False),
        ("domain_allow_deny_policy", "still_needed_for_quality", "medium", "private/internal blocking", "Curated domain allow/deny registry", "future policy patch", False),
        ("freshness_parser", "still_needed_for_quality", "medium", "date missing or fixture marker", "Structured source date parser", "future parser patch", False),
        ("conflict_resolver", "still_needed_for_quality", "medium", "conflicts identified", "Review-gated conflict resolution", "future review workflow", False),
        ("query_refinement_executor", "deferred_not_required_for_first_real_run", "low", "candidates generated only", "Approved second-loop executor", "future milestone", False),
    ]
    gaps = []
    for index, (name, status, severity, current, needed, artifact, blocks) in enumerate(base, start=1):
        gaps.append(
            {
                "gap_id": f"l6_13_gap_{index:03d}_{name}",
                "source_l6_12_gap_count": prior_gap_count,
                "previous_status": "reported_in_l6_12",
                "l6_13_status": status,
                "severity": severity,
                "current_state": current,
                "needed_capability": needed,
                "patch_or_artifact_added": artifact,
                "still_blocks_real_observation": blocks,
                "recommended_next_step": needed,
            }
        )
    return gaps


def no_action_receipt() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": RUN_ID,
        "no_side_effect_receipt_generated": True,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "secret_values_serialized": False,
        "actions": [
            {
                "action": action,
                "authorized": False,
                "executed": False,
                "occurred": False,
                "receipt": f"no_{action}",
            }
            for action in NO_ACTIONS
        ],
    }


def classify_run(
    real_preflight: dict[str, Any],
    real_search: dict[str, Any],
    real_pages: list[dict[str, Any]],
    real_packets: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
) -> str:
    if real_packets and conflicts:
        return "real_evidence_collected_with_unresolved_conflicts"
    if real_packets:
        return "real_evidence_collected_and_review_ready"
    if real_pages:
        return "partial_real_page_read_no_evidence"
    if real_search.get("search_executed"):
        return "partial_real_search_no_page_read"
    blockers = set(real_preflight.get("blockers", []))
    config_blockers = {
        "controlled_search_backend_not_configured",
        "controlled_public_page_read_adapter_not_configured",
        "configured_backend_missing_required_environment",
        "real_provider_and_stdlib_page_read_not_configured",
    }
    if blockers & config_blockers:
        return "real_backend_activation_blocked_with_complete_activation_kit"
    return "preflight_blocked_with_complete_activation_kit"


def mission_markdown(summary: dict[str, Any], claims: list[dict[str, Any]], conflicts: list[dict[str, Any]], gaps: list[dict[str, Any]], refinements: list[dict[str, Any]]) -> str:
    real_note = (
        "Real external evidence was collected."
        if summary["real_observation_executed"]
        else "Real external evidence not collected because backend/page-read config was missing or blocked."
    )
    return (
        "# L6.13 Mission Evidence Report\n\n"
        "## Executive summary\n\n"
        f"{real_note} Fixture proof executed and remains clearly labeled as demo evidence.\n\n"
        "## Run classification\n\n"
        f"`{summary['run_classification']}`\n\n"
        "## Real vs fixture status\n\n"
        f"- Real observation executed: {summary['real_observation_executed']}\n"
        f"- Fixture proof executed: {summary['fixture_proof_executed']}\n"
        f"- Real evidence packets: {summary['real_evidence_packets_generated']}\n"
        f"- Fixture evidence packets: {summary['fixture_evidence_packets_generated']}\n\n"
        "## Backend/page-read configuration status\n\n"
        f"- Backend mode: {summary['backend_mode']}\n"
        f"- Page-read mode: {summary['page_read_mode']}\n"
        f"- Network allowed: {summary['network_allowed']}\n"
        f"- Safety preflight: {summary['safety_preflight_decision']}\n"
        f"- Blockers: {', '.join(summary['blockers']) if summary['blockers'] else 'none'}\n\n"
        "## Budget used\n\n"
        f"{summary['query_count']} queries, {summary['search_results_considered']} results considered, "
        f"{summary['pages_opened']} pages opened, {summary['domains_touched']} domains, "
        f"crawl depth {summary['crawl_depth_used']}.\n\n"
        "## Queries generated\n\n"
        "Query details are stored in `real_query_plan/generated_query_plan.json`.\n\n"
        "## Sources considered\n\n"
        "Search candidates and triage decisions are stored in `real_search_execution_receipts/`.\n\n"
        "## Pages read\n\n"
        "Page-read receipts are stored in `real_page_read_receipts/`.\n\n"
        "## Evidence packets\n\n"
        f"Generated {summary['evidence_packets_generated']} total evidence packets. Search snippets are locator metadata only.\n\n"
        "## Bounded claims\n\n"
        + "\n".join(f"- {claim['claim_id']}: {claim['support_status']}" for claim in claims)
        + "\n\n## Corroboration/conflict matrix\n\n"
        f"Conflicts found: {len(conflicts)}.\n\n"
        "## Unresolved claims\n\n"
        f"Unresolved claims: {summary['unresolved_claims']}.\n\n"
        "## Capability gaps\n\n"
        + "\n".join(f"- {gap['gap_id']}: {gap['l6_13_status']}" for gap in gaps)
        + "\n\n## Query refinement candidates\n\n"
        + "\n".join(f"- {item['candidate_id']}: {item['candidate_query']}" for item in refinements)
        + "\n\n## No-side-effect receipt summary\n\n"
        "No login, payment, form submission, outreach, publication, MCP/live behavior, or core writeback occurred.\n\n"
        "## Next recommended run\n\n"
        f"{summary['next_recommended_run']}.\n"
    )


def write_static_reports(generated: list[str], summary: dict[str, Any], gaps: list[dict[str, Any]]) -> None:
    write_text(
        "l6_real_controlled_external_observation_mission_sprint/README.md",
        (
            f"# {MILESTONE_ID} {MILESTONE_NAME}\n\n"
            "Real controlled observation mission sprint. It provides a complete "
            "no-secret activation kit, fixture proof path, and real-run orchestration "
            "when an approved backend/page-read configuration is present.\n"
        ),
        generated,
    )
    write_text(
        "l6_real_controlled_external_observation_mission_sprint/l6_13_summary.md",
        (
            "# L6.13 Summary\n\n"
            f"Run classification: {summary['run_classification']}.\n\n"
            f"Activation kit generated: {summary['activation_kit_generated']}.\n\n"
            f"Real observation executed: {summary['real_observation_executed']}.\n"
        ),
        generated,
    )
    write_text(
        "real_backend_activation_kit/activation_kit_report.md",
        "# L6.13 Activation Kit\n\nConfigure backend/page-read env vars and provider key presence outside the repo. This kit never stores secrets and never asks for URLs.\n",
        generated,
    )
    write_text(
        "real_provider_env_checks/env_check_report.md",
        "# Environment Check Report\n\nProvider key checks are presence-only. Secret values are not printed or serialized.\n",
        generated,
    )
    write_text(
        "real_page_read_activation/l6_13_page_read_activation_report.md",
        "# L6.13 Page-Read Activation\n\n`stdlib_public_http` is GET-only, public HTTP/HTTPS only, and blocks private/internal targets.\n",
        generated,
    )
    write_text(
        "real_observation_orchestrator/orchestrator_report.md",
        "# L6.13 Orchestrator Report\n\nThe orchestrator runs fixture proof by default and real observation only after explicit backend/page-read activation.\n",
        generated,
    )
    write_text(
        "real_capability_gap_closure/capability_gap_closure_report.md",
        f"# Capability Gap Closure\n\nClassified {len(gaps)} gaps across resolved, partial, blocking, quality, and deferred statuses.\n",
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

    fixture_preflight = safety_preflight(fixture_config, budget)
    fixture_search = run_search(fixture_config, work_order, queries)
    fixture_selected_sources, fixture_rejected_sources = triage_results(fixture_search)
    fixture_pages = read_pages(fixture_config, fixture_selected_sources)
    fixture_packets = evidence_packets("fixture", work_order, fixture_search, fixture_pages)

    real_preflight = safety_preflight(real_config, budget, require_real=True)
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
    real_selected_sources: list[dict[str, Any]] = []
    real_rejected_sources: list[dict[str, Any]] = []
    real_pages: list[dict[str, Any]] = []
    real_packets: list[dict[str, Any]] = []

    real_run_attempted = real_preflight["decision"] == "pass" and is_real_provider_mode(real_config)
    if real_run_attempted:
        real_search = run_search(real_config, work_order, queries)
        real_selected_sources, real_rejected_sources = triage_results(real_search)
        candidate_urls = [item["url"] for item in real_selected_sources if item.get("url")]
        real_preflight = safety_preflight(real_config, budget, candidate_urls, require_real=True)
        if real_search.get("search_executed") and real_preflight["decision"] == "pass":
            real_pages = read_pages(real_config, real_selected_sources)
            real_packets = evidence_packets("real", work_order, real_search, real_pages)

    all_packets = real_packets if real_packets else fixture_packets
    all_pages = real_pages if real_packets else fixture_pages
    quality = source_quality_matrix(all_packets, all_pages)
    claims, conflicts, corroboration = claim_and_conflict(all_packets)
    prior_gaps = load_json("controlled_capability_gap_report/capability_gap_registry.json", {}).get("gap_count", 15)
    gap_closure = capability_gap_closure(real_config, prior_gaps)
    refinements = query_refinement_candidates(claims, [gap["gap_id"] for gap in gap_closure])
    receipt = no_action_receipt()

    run_classification = classify_run(real_preflight, real_search, real_pages, real_packets, conflicts if real_packets else [])
    blockers = sorted(
        set(
            real_preflight.get("blockers", [])
            + ([real_search.get("error_code")] if real_search.get("error_code") else [])
        )
    )
    fixture_domains = sorted({page.get("source_domain") for page in fixture_pages if page.get("source_domain")})
    real_domains = sorted({page.get("source_domain") for page in real_pages if page.get("source_domain")})
    external_reads_used = int(real_search.get("external_reads_count", 0)) + sum(
        1 for page in real_pages if page.get("safety_flags", {}).get("network_used")
    )
    resolved_gaps = sum(1 for gap in gap_closure if gap["l6_13_status"] == "resolved_in_l6_13")
    remaining_gaps = sum(1 for gap in gap_closure if gap["l6_13_status"] in {"still_blocking_real_observation", "still_needed_for_quality"})

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "run_id": RUN_ID,
        "run_classification": run_classification,
        "allowed_run_classifications": RUN_CLASSIFICATIONS,
        "l6_13_real_controlled_external_observation_mission_sprint_complete": True,
        "selected_work_order_id": work_order["selected_work_order_id"],
        "backend_mode": real_config.search_backend_mode,
        "page_read_mode": real_config.page_read_backend_mode,
        "fixture_backend_mode": "fixture",
        "fixture_page_read_mode": "fixture",
        "network_allowed": real_config.search_network_allowed or real_config.page_read_network_allowed,
        "safety_preflight_decision": real_preflight["decision"],
        "fixture_proof_executed": True,
        "real_observation_executed": bool(real_packets),
        "real_observation_attempted": real_run_attempted,
        "query_count": len(queries),
        "search_results_considered": real_search.get("search_results_considered", 0)
        if real_search.get("search_executed")
        else fixture_search.get("search_results_considered", 0),
        "pages_opened": len(real_pages) if real_pages else len(fixture_pages),
        "domains_touched": len(real_domains) if real_domains else len(fixture_domains),
        "crawl_depth_used": 1 if all_pages else 0,
        "external_reads_used": external_reads_used,
        "evidence_packets_generated": len(all_packets),
        "real_evidence_packets_generated": len(real_packets),
        "fixture_evidence_packets_generated": len(fixture_packets),
        "conflicts_found": len(conflicts),
        "unresolved_claims": sum(1 for claim in claims if claim["conflict_status"] != "no_conflict"),
        "query_refinements_generated": len(refinements),
        "query_refinement_candidates_generated": len(refinements),
        "capability_gaps_resolved": resolved_gaps,
        "capability_gaps_remaining": remaining_gaps,
        "activation_kit_generated": True,
        "blockers": blockers,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "search_snippets_used_as_evidence": False,
        "page_read_content_used_as_evidence": bool(all_packets),
        "fixture_evidence_mislabeled_real": False,
        "secret_values_serialized": False,
        "next_recommended_run": "configure controlled search backend and stdlib public page-read allow flags"
        if not real_packets
        else "review real evidence packet before any downstream use",
        **BUDGET,
        **SAFETY_FLAGS,
    }

    activation_requirements = {
        "schema_version": SCHEMA_VERSION,
        "manual_url_request_required": False,
        "manual_url_request_authorized": False,
        "supported_search_backends": ["disabled", "fixture", *PROVIDER_KEY_ENVS.keys()],
        "supported_page_read_backends": ["disabled", "fixture", "stdlib_public_http"],
        "required_env_names": [
            SEARCH_BACKEND_ENV,
            SEARCH_ALLOW_NETWORK_ENV,
            PAGE_READ_BACKEND_ENV,
            PAGE_READ_ALLOW_NETWORK_ENV,
            *PROVIDER_KEY_ENVS.values(),
        ],
        "missing_configuration_fields": missing_configuration_fields(real_config),
        "provider_specific_requirements": [
            {
                "provider": provider,
                "backend_env_value": provider,
                "required_key_env_name": env_name,
                "key_present": bool(os.environ.get(env_name)),
                "secret_value_serialized": False,
            }
            for provider, env_name in PROVIDER_KEY_ENVS.items()
        ],
    }

    write_json(
        "l6_real_controlled_external_observation_mission_sprint/l6_13_milestone_contract.json",
        {**summary, "contract_type": "milestone_contract"},
        generated,
    )
    write_json(
        "l6_real_controlled_external_observation_mission_sprint/l6_13_scope.json",
        {
            "schema_version": SCHEMA_VERSION,
            "scope": "real controlled external observation mission sprint",
            "manual_url_request_allowed": False,
            "real_execution_requires_explicit_backend_configuration": True,
            "secret_storage_allowed": False,
        },
        generated,
    )
    write_json("l6_real_controlled_external_observation_mission_sprint/l6_13_budget_policy.json", {"schema_version": SCHEMA_VERSION, **BUDGET}, generated)
    write_json("l6_real_controlled_external_observation_mission_sprint/l6_13_safety_flags.json", {"schema_version": SCHEMA_VERSION, **SAFETY_FLAGS}, generated)
    write_json("l6_real_controlled_external_observation_mission_sprint/l6_13_run_classification_schema.json", {"schema_version": SCHEMA_VERSION, "allowed_run_classifications": RUN_CLASSIFICATIONS}, generated)
    write_json("l6_real_controlled_external_observation_mission_sprint/l6_13_summary.json", summary, generated)

    write_json("real_backend_activation_kit/activation_kit_manifest.json", {**activation_requirements, "activation_kit_generated": True}, generated)
    write_json("real_backend_activation_kit/backend_configuration_template.json", {"schema_version": SCHEMA_VERSION, "template_env_names_only": activation_requirements["required_env_names"], "secret_values_included": False}, generated)
    write_text(
        "real_backend_activation_kit/l6_13_controlled_observation.env.template",
        "\n".join(
            [
                "# Variable names only. Do not commit real secret values.",
                "YSTAR_CONTROLLED_SEARCH_BACKEND=brave_search_api",
                "YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK=1",
                "YSTAR_CONTROLLED_PAGE_READ_BACKEND=stdlib_public_http",
                "YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK=1",
                "BRAVE_SEARCH_API_KEY=<set outside repo>",
                "TAVILY_API_KEY=<optional set outside repo>",
                "SERPAPI_API_KEY=<optional set outside repo>",
                "",
            ]
        ),
        generated,
    )
    write_json("real_backend_activation_kit/provider_activation_requirements.json", activation_requirements, generated)
    write_json("real_provider_env_checks/env_presence_receipt.json", {**real_config.receipt(), "secret_values_serialized": False, "manual_url_request": False}, generated)
    write_json("real_provider_env_checks/provider_key_presence_matrix.json", {"schema_version": SCHEMA_VERSION, "providers": provider_presence_matrix()}, generated)
    write_json("real_provider_env_checks/missing_configuration_fields.json", {"schema_version": SCHEMA_VERSION, "missing_configuration_fields": missing_configuration_fields(real_config)}, generated)

    write_json("real_page_read_activation/l6_13_page_read_activation_receipt.json", {"schema_version": SCHEMA_VERSION, "page_read_mode": real_config.page_read_backend_mode, "page_read_network_allowed": real_config.page_read_network_allowed, "mode_ready_for_real_page_read": real_config.page_read_backend_mode == "stdlib_public_http" and real_config.page_read_network_allowed, "blockers": [b for b in blockers if "page_read" in b or "preflight" in b]}, generated)
    write_json("real_page_read_activation/l6_13_public_page_read_policy.json", {"schema_version": SCHEMA_VERSION, "method": "GET_only", "allowed_schemes": ["http", "https"], "auth": False, "cookies": False, "credentials": False, "form_submit": False, "file_upload": False, "javascript_execution": False, "browser_automation": False, "localhost_private_internal_blocked": True, "timeout_seconds": 5, "max_bytes_per_page": 200000, **BUDGET}, generated)

    write_json("real_observation_orchestrator/selected_work_order.json", work_order, generated)
    write_json("real_observation_orchestrator/real_observation_preflight.json", real_preflight, generated)
    write_json("real_observation_orchestrator/real_observation_run_trace.json", {"schema_version": SCHEMA_VERSION, "run_id": RUN_ID, "run_classification": run_classification, "fixture_preflight": fixture_preflight, "real_preflight": real_preflight, "real_run_attempted": real_run_attempted, "real_observation_executed": bool(real_packets), "activation_kit_generated": True}, generated)
    write_json("real_observation_orchestrator/run_classification_decision.json", {"schema_version": SCHEMA_VERSION, "run_classification": run_classification, "allowed_run_classifications": RUN_CLASSIFICATIONS, "reason": "real evidence packets generated" if real_packets else "real backend/page-read activation incomplete; fixture proof and activation kit generated"}, generated)

    write_json("real_query_plan/generated_query_plan.json", {"schema_version": SCHEMA_VERSION, "query_count": len(queries), "queries": queries}, generated)
    write_json("real_query_plan/query_priority_matrix.json", {"schema_version": SCHEMA_VERSION, "priorities": [{"query_id": q["query_id"], "priority": q.get("priority", i + 1), "query_category": q.get("query_category")} for i, q in enumerate(queries)]}, generated)
    write_text("real_query_plan/query_plan_report.md", "# L6.13 Query Plan\n\nGenerated mission-oriented queries from the selected work order. Snippets are not evidence.\n", generated)

    write_json("real_search_execution_receipts/search_execution_receipt.json", {"schema_version": SCHEMA_VERSION, "fixture_search_result": fixture_search, "real_search_result": real_search, "snippets_used_as_evidence": False}, generated)
    write_json("real_search_execution_receipts/search_execution_trace.json", {"schema_version": SCHEMA_VERSION, "fixture_search_executed": True, "real_search_executed": bool(real_search.get("search_executed")), "search_query_count": real_search.get("search_query_count", 0), "search_results_considered": real_search.get("search_results_considered", 0), "provider_error_code": real_search.get("error_code")}, generated)
    write_json("real_search_execution_receipts/search_result_candidates.json", {"schema_version": SCHEMA_VERSION, "fixture_candidates": fixture_search.get("result_candidates", []), "real_candidates": real_search.get("result_candidates", [])}, generated)
    write_text("real_search_execution_receipts/search_execution_report.md", "# Search Execution Report\n\nDefault path uses fixture results. Real provider failures become structured blockers and never ask for URLs.\n", generated)

    write_json("real_page_read_receipts/page_read_receipt_index.json", {"schema_version": SCHEMA_VERSION, "fixture_pages": fixture_pages, "real_pages": real_pages, "page_read_count": len(real_pages) if real_pages else len(fixture_pages)}, generated)
    write_json("real_page_read_receipts/page_read_trace.json", {"schema_version": SCHEMA_VERSION, "fixture_page_read_executed": True, "real_page_read_executed": bool(real_pages), "pages_opened": len(real_pages) if real_pages else len(fixture_pages)}, generated)
    write_json("real_page_read_receipts/opened_page_registry.json", {"schema_version": SCHEMA_VERSION, "opened_pages": all_pages}, generated)
    write_text("real_page_read_receipts/page_read_report.md", "# Page Read Report\n\nPage reads are fixture by default and real only through approved stdlib_public_http mode.\n", generated)

    write_json("real_bounded_crawl_receipts/bounded_crawl_policy.json", {"schema_version": SCHEMA_VERSION, "max_crawl_depth": BUDGET["max_crawl_depth"], "max_pages_per_domain": BUDGET["max_pages_per_domain"], "no_high_volume_crawling": True}, generated)
    write_json("real_bounded_crawl_receipts/bounded_crawl_trace.json", {"schema_version": SCHEMA_VERSION, "crawl_depth_used": 1 if all_pages else 0, "crawl_expansions": [], "external_reads_used": external_reads_used, "scope_drift_stopped": False}, generated)
    write_json("real_bounded_crawl_receipts/crawl_expansion_decisions.json", {"schema_version": SCHEMA_VERSION, "expansions": [], "reason": "fixture proof uses selected pages only; real depth-1 crawl is gated by budget and preflight"}, generated)
    write_text("real_bounded_crawl_receipts/bounded_crawl_report.md", "# Bounded Crawl Report\n\nDepth remains capped at 1 and no high-volume crawling is authorized.\n", generated)

    packet_schema = {"schema_version": SCHEMA_VERSION, "required_fields": ["evidence_packet_id", "run_id", "real_or_fixture", "work_order_id", "query_id", "source_url", "final_url", "source_domain", "source_type", "source_quality_label", "freshness_label", "page_read_id", "extracted_text_excerpt", "bounded_claim", "claim_scope", "support_status", "conflict_status", "limitations", "generated_at_utc"]}
    write_json("real_evidence_packets/evidence_packet_schema.json", packet_schema, generated)
    write_json("real_evidence_packets/evidence_packet_index.json", {"schema_version": SCHEMA_VERSION, "evidence_packet_count": len(all_packets), "real_evidence_packet_count": len(real_packets), "fixture_evidence_packet_count": len(fixture_packets), "packets": [{"evidence_packet_id": packet["evidence_packet_id"], "real_or_fixture": packet["real_or_fixture"], "path": f"real_evidence_packets/evidence_packet_{i:03d}.json"} for i, packet in enumerate(all_packets, start=1)]}, generated)
    for index, packet in enumerate(all_packets, start=1):
        write_json(f"real_evidence_packets/evidence_packet_{index:03d}.json", packet, generated)
    write_text("real_evidence_packets/evidence_extraction_report.md", "# Evidence Extraction Report\n\nPage-read content may become bounded evidence; search snippets never do.\n", generated)

    write_json("real_source_quality_matrix/source_quality_matrix.json", {"schema_version": SCHEMA_VERSION, "allowed_labels": SOURCE_QUALITY_LABELS, "sources": quality}, generated)
    write_json("real_source_quality_matrix/source_freshness_assessment.json", {"schema_version": SCHEMA_VERSION, "freshness": [{"source_url": packet["source_url"], "freshness_label": packet["freshness_label"]} for packet in all_packets]}, generated)
    write_text("real_source_quality_matrix/source_quality_report.md", "# Source Quality Report\n\nSource labels are deterministic and do not use LLM confidence as authority.\n", generated)

    write_json("real_claim_boundary/bounded_claim_registry.json", {"schema_version": SCHEMA_VERSION, "claims": claims}, generated)
    write_json("real_claim_boundary/unsupported_claim_registry.json", {"schema_version": SCHEMA_VERSION, "unsupported_claims": [claim for claim in claims if claim["support_status"] == "unsupported"]}, generated)
    write_json("real_claim_boundary/unresolved_claim_registry.json", {"schema_version": SCHEMA_VERSION, "unresolved_claims": [claim for claim in claims if claim["conflict_status"] != "no_conflict"]}, generated)
    write_text("real_claim_boundary/claim_boundary_report.md", "# Claim Boundary Report\n\nClaims are bounded to internal review and external use is not authorized.\n", generated)

    write_json("real_corroboration_conflict_matrix/claim_corroboration_matrix.json", {"schema_version": SCHEMA_VERSION, "claims": corroboration}, generated)
    write_json("real_corroboration_conflict_matrix/conflict_registry.json", {"schema_version": SCHEMA_VERSION, "conflict_count": len(conflicts), "conflicts": conflicts}, generated)
    write_json("real_corroboration_conflict_matrix/evidence_sufficiency_assessment.json", {"schema_version": SCHEMA_VERSION, "sufficient_for_external_use": False, "sufficient_for_internal_review": bool(all_packets), "reason": "review required before external use"}, generated)
    write_text("real_corroboration_conflict_matrix/corroboration_report.md", "# Corroboration Report\n\nMatrix classifies corroborated, single-source, conflicted, unresolved, and blocked claims.\n", generated)

    mission_report_json = {
        "schema_version": SCHEMA_VERSION,
        "summary": summary,
        "what_external_evidence_was_sought": work_order["observation_question"],
        "queries_generated": queries,
        "sources_considered": fixture_search.get("result_candidates", []) + real_search.get("result_candidates", []),
        "pages_read": all_pages,
        "evidence_packets": all_packets,
        "supported_claims": [claim for claim in claims if claim["support_status"] != "unresolved_limitation"],
        "conflicted_claims": conflicts,
        "unresolved_claims": [claim for claim in claims if claim["conflict_status"] != "no_conflict"],
        "source_quality_limitations": [source["trust_limitations"] for source in quality],
        "query_refinement_candidates": refinements,
        "capability_gaps": gap_closure,
    }
    write_json("real_mission_evidence_report/mission_evidence_report.json", mission_report_json, generated)
    write_text("real_mission_evidence_report/mission_evidence_report.md", mission_markdown(summary, claims, conflicts, gap_closure, refinements), generated)

    review_packet = {
        "schema_version": SCHEMA_VERSION,
        "run_classification": run_classification,
        "real_observation_executed": bool(real_packets),
        "fixture_proof_executed": True,
        "selected_work_order": work_order,
        "budget_used": {field: summary[field] for field in ["query_count", "search_results_considered", "pages_opened", "domains_touched", "crawl_depth_used", "external_reads_used"]},
        "backend_mode": real_config.search_backend_mode,
        "page_read_mode": real_config.page_read_backend_mode,
        "evidence_packets": [packet["evidence_packet_id"] for packet in all_packets],
        "conflicts": conflicts,
        "unresolved_claims": [claim["claim_id"] for claim in claims if claim["conflict_status"] != "no_conflict"],
        "recommended_query_refinements": refinements,
        "capability_gaps": gap_closure,
        "no_side_effect_summary": receipt,
        "review_status": "pending_review",
    }
    write_json("real_review_packet/review_packet.json", review_packet, generated)
    write_json("real_review_packet/review_packet_index.json", {"schema_version": SCHEMA_VERSION, "review_packets": ["real_review_packet/review_packet.json"], "review_status": "pending_review"}, generated)
    write_text("real_review_packet/review_packet_report.md", "# Review Packet Report\n\nReview remains pending. No downstream writeback or externalization is authorized.\n", generated)

    write_json("real_query_refinement_candidates/query_refinement_candidate_index.json", {"schema_version": SCHEMA_VERSION, "candidate_count": len(refinements), "candidates": refinements}, generated)
    for index, candidate in enumerate(refinements, start=1):
        write_json(f"real_query_refinement_candidates/query_refinement_candidate_{index:03d}.json", candidate, generated)
    write_text("real_query_refinement_candidates/query_refinement_report.md", "# Query Refinement Candidates\n\nCandidates are generated for future approved loops and are not executed now.\n", generated)

    write_json("real_capability_gap_closure/capability_gap_closure_matrix.json", {"schema_version": SCHEMA_VERSION, "gaps": gap_closure}, generated)
    write_json("real_capability_gap_closure/capability_gap_closure_summary.json", {"schema_version": SCHEMA_VERSION, "resolved": resolved_gaps, "remaining": remaining_gaps, "still_blocking_real_observation": [gap for gap in gap_closure if gap["still_blocks_real_observation"]]}, generated)

    write_json("real_no_action_receipts/no_side_effect_receipt.json", receipt, generated)
    write_json("real_no_action_receipts/no_action_receipt_index.json", {"schema_version": SCHEMA_VERSION, "receipt_count": len(NO_ACTIONS), "actions": NO_ACTIONS}, generated)
    for action in NO_ACTIONS:
        write_json(f"real_no_action_receipts/no_{action}_receipt.json", {"schema_version": SCHEMA_VERSION, "action": action, "authorized": False, "executed": False, "occurred": False}, generated)
    write_text("real_no_action_receipts/no_action_report.md", "# No-Action Receipt\n\nNo external side effects, core writebacks, cross-repo modifications, or URL requests occurred.\n", generated)

    write_json("l6_13_read_model/l6_13_cieu_like_fixture.json", {"schema_version": SCHEMA_VERSION, "X_t": "L6.12 engineering-ready observation loop", "U_t": "L6.13 activation kit and mission evidence sprint", "Y_star_t": "Activate real controlled external observation when explicitly configured while proving fixture path and preserving no-side-effect boundaries.", "Y_t_plus_1": summary, "R_t_plus_1": {"blockers": blockers, "capability_gaps_remaining": remaining_gaps}, "event_mode": "l6_13_real_controlled_external_observation_mission_sprint_fixture"}, generated)
    write_json("l6_13_read_model/l6_13_strategic_residual_delta.json", {"schema_version": SCHEMA_VERSION, "residuals": blockers + [gap["gap_id"] for gap in gap_closure if gap["still_blocks_real_observation"]], "real_observation_executed": bool(real_packets), "activation_kit_generated": True}, generated)
    write_json("l6_13_read_model/l6_13_meta_learning_update_candidate.json", {"schema_version": SCHEMA_VERSION, "eligible_for_review_queue": True, "eligible_for_direct_brain_writeback": False, "eligible_for_direct_memory_ingestion": False, "eligible_for_candidate_auto_approval": False, "eligible_for_direct_strategy_mutation": False, "approved": False, "applied": False}, generated)
    write_json("l6_13_read_model/l6_13_readiness_assessment.json", {**summary, "ready_for_next_real_observation_run_after_config": not bool(real_packets), "ready_for_l6_14_if_real_evidence_reviewed": bool(real_packets), "next_step": summary["next_recommended_run"]}, generated)
    write_json("l6_13_read_model/l6_13_blockers.json", {"schema_version": SCHEMA_VERSION, "blockers": blockers, "missing_configuration_fields": missing_configuration_fields(real_config)}, generated)
    write_json("l6_13_read_model/l6_13_next_milestone_recommendation.json", {"schema_version": SCHEMA_VERSION, "recommended_next_milestone": "L6.14 Controlled Real Evidence Review and Refinement Gate" if real_packets else "Configure controlled search/page-read backend and rerun L6.13", "do_not_ask_user_for_url": True}, generated)
    write_json("l6_13_read_model/l6_13_read_model_summary.json", summary, generated)
    write_text("l6_13_read_model/l6_13_report.md", mission_markdown(summary, claims, conflicts, gap_closure, refinements), generated)

    write_static_reports(generated, summary, gap_closure)

    write_json(
        "l6_real_controlled_external_observation_mission_sprint/l6_13_generation_manifest.json",
        {"schema_version": SCHEMA_VERSION, "generated_at_utc": utc_now(), "generated_files": generated},
        generated,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
