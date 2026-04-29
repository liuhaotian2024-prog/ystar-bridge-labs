#!/usr/bin/env python3
"""Build L6.14 real evidence conflict-resolution sprint artifacts.

The builder consumes the L6.13 real mission evidence report, plans a targeted
second pass against unresolved/conflicting claims, and executes a governed
read-only Tavily/stdib-public-HTTP loop when repo-external configuration is
present. Secret values are never serialized.
"""

from __future__ import annotations

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
MILESTONE_ID = "L6.14"
MILESTONE_NAME = "Real Evidence Conflict Resolution & Iterative Observation Sprint"
MODE = "real_evidence_conflict_resolution_sprint"
RUN_ID = "l6_14_real_evidence_conflict_resolution_run_001"
PRIOR_RUN_ID = "l6_13_real_controlled_observation_mission_run_001"
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
    "L6.13",
]

POST_SECOND_PASS_CLASSIFICATIONS = [
    "conflict_resolved",
    "conflict_bounded",
    "still_conflicted_with_reason",
    "insufficient_evidence_after_second_pass",
    "second_pass_blocked_by_backend_or_network",
    "second_pass_blocked_by_budget_or_safety",
]

BUDGET = {
    "max_selected_work_orders": 1,
    "max_second_pass_queries": 8,
    "max_search_results_considered": 20,
    "max_pages_opened": 8,
    "max_domains": 6,
    "max_pages_per_domain": 3,
    "max_crawl_depth": 1,
    "max_total_external_reads": 12,
    "max_new_real_evidence_packets": 8,
    "max_conflict_resolution_targets": 3,
    "max_runtime_minutes": 15,
    "rate_limit_required": True,
    "stop_on_login_or_payment_or_form": True,
    "stop_on_private_or_sensitive_data": True,
    "stop_on_scope_drift": True,
}

SAFETY_FLAGS = {
    "ask_user_for_url_authorized": False,
    "user_manual_search_authorized": False,
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


def write_json(path: str, payload: dict[str, Any] | list[Any], generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    generated.append(path)


def write_text(path: str, payload: str, generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    generated.append(path)


def load_json(path: str, default: Any) -> Any:
    target = ROOT / path
    if not target.exists():
        return default
    return json.loads(target.read_text(encoding="utf-8"))


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lower()


def truncate(value: str, limit: int = 500) -> str:
    clean = " ".join(str(value).split())
    return clean[:limit]


def selected_work_order() -> dict[str, Any]:
    prior = load_json("real_observation_orchestrator/selected_work_order.json", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_count": 1,
        "selected_work_order_id": prior.get("selected_work_order_id", SELECTED_WORK_ORDER_ID),
        "source_work_order_id": prior.get("source_work_order_id", SELECTED_WORK_ORDER_ID),
        "evidence_need_id": prior.get("evidence_need_id", "l6_8_need_001"),
        "source_type": prior.get("source_type", "official policy or program source"),
        "source_function": prior.get("source_function", "official policy or program source"),
        "observation_question": prior.get(
            "observation_question",
            "What future read-only evidence would reduce payer or beneficiary clarity uncertainty?",
        ),
        "claim_boundary": prior.get(
            "claim_boundary",
            "internal review of public demand or beneficiary language only",
        ),
        "expected_evidence_type": "public page-read extracted evidence",
    }


def ingest_prior_report() -> dict[str, Any]:
    mission = load_json("real_mission_evidence_report/mission_evidence_report.json", {})
    summary = load_json("l6_13_read_model/l6_13_read_model_summary.json", {})
    evidence_index = load_json("real_evidence_packets/evidence_packet_index.json", {})
    prior_packets = []
    for item in evidence_index.get("packets", []):
        path = item.get("path")
        if path:
            packet = load_json(path, None)
            if packet:
                prior_packets.append(packet)
    conflicts = load_json("real_corroboration_conflict_matrix/conflict_registry.json", {}).get(
        "conflicts", mission.get("conflicted_claims", [])
    )
    unresolved = load_json("real_claim_boundary/unresolved_claim_registry.json", {}).get(
        "unresolved_claims", mission.get("unresolved_claims", [])
    )
    refinements = load_json("real_query_refinement_candidates/query_refinement_candidate_index.json", {}).get(
        "candidates", mission.get("query_refinement_candidates", [])
    )
    page_index = load_json("real_page_read_receipts/page_read_receipt_index.json", {})
    real_pages = page_index.get("real_pages", [])
    blocked_pages = [
        page for page in real_pages if page.get("evidence_eligible") is not True
    ]
    weak_claims = [
        packet
        for packet in prior_packets
        if packet.get("real_or_fixture") == "real"
        and (
            packet.get("source_quality_label") == "unknown"
            or "single source is not canonical truth" in packet.get("limitations", [])
        )
    ]
    single_source_claims = [
        packet
        for packet in prior_packets
        if packet.get("real_or_fixture") == "real"
        and packet.get("support_status") == "supported_by_page_read_content"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "prior_report_present": bool(mission),
        "prior_run_id": summary.get("run_id", PRIOR_RUN_ID),
        "prior_run_classification": summary.get(
            "run_classification",
            mission.get("summary", {}).get("run_classification", "unknown"),
        ),
        "prior_real_observation_executed": bool(summary.get("real_observation_executed")),
        "selected_work_order_id": summary.get("selected_work_order_id", SELECTED_WORK_ORDER_ID),
        "prior_queries": mission.get("queries_generated", []),
        "prior_real_evidence_packets": prior_packets,
        "prior_real_evidence_packet_count": sum(
            1 for packet in prior_packets if packet.get("real_or_fixture") == "real"
        ),
        "prior_conflicts": conflicts,
        "prior_conflict_count": len(conflicts),
        "prior_unresolved_claims": unresolved,
        "prior_unresolved_claim_count": len(unresolved),
        "prior_query_refinement_candidates": refinements,
        "blocked_or_failed_page_reads": blocked_pages,
        "blocked_or_failed_page_read_count": len(blocked_pages),
        "weakly_supported_claims": weak_claims,
        "single_source_claims": single_source_claims,
    }


def plan_second_pass_queries(
    work_order: dict[str, Any], ingestion: dict[str, Any]
) -> list[dict[str, Any]]:
    planned: list[dict[str, Any]] = []
    unresolved = ingestion.get("prior_unresolved_claims", [])
    conflicts = {item.get("claim_id"): item for item in ingestion.get("prior_conflicts", [])}
    refinements = ingestion.get("prior_query_refinement_candidates", [])

    for index, claim in enumerate(unresolved[: BUDGET["max_conflict_resolution_targets"]], start=1):
        claim_text = truncate(claim.get("bounded_claim", ""), 110)
        conflict = conflicts.get(claim.get("claim_id"), {})
        planned.append(
            {
                "query_id": f"l6_14_second_pass_query_{len(planned) + 1:03d}",
                "query_text": (
                    "official source beneficiary demand program evidence scope limitation "
                    f"{claim_text}"
                ).strip(),
                "linked_unresolved_claim_id": claim.get("claim_id"),
                "linked_conflict_id": conflict.get("conflict_id"),
                "intended_source_type": "official_primary",
                "reason": "Target the unresolved/conflicting claim with official primary-source evidence.",
                "expected_evidence_value": "Clarify whether the prior claim is evidence, boilerplate, or unrelated context.",
                "priority": index,
                "budget_cost_estimate": {"queries": 1, "results": 4, "pages": 2},
                "query_category": "conflict_resolution_primary_source_query",
                "source_type": work_order["source_type"],
                "source_function": work_order["source_function"],
                "no_snippet_fact_use": True,
                "no_fact_inference_from_search_result": True,
                "max_results": 4,
            }
        )

    for item in refinements:
        if len(planned) >= BUDGET["max_second_pass_queries"]:
            break
        planned.append(
            {
                "query_id": f"l6_14_second_pass_query_{len(planned) + 1:03d}",
                "query_text": str(item.get("candidate_query", ""))[:220],
                "linked_unresolved_claim_id": item.get("linked_claim_or_gap"),
                "linked_conflict_id": None,
                "intended_source_type": item.get("expected_source_type", "official_or_institutional"),
                "reason": item.get("reason", "Execute L6.13 query refinement candidate."),
                "expected_evidence_value": "Add independent support or contradiction for prior evidence state.",
                "priority": item.get("priority", len(planned) + 1),
                "budget_cost_estimate": item.get("budget_cost_estimate", {"queries": 1, "pages": 2}),
                "query_category": "prior_query_refinement_execution",
                "source_type": work_order["source_type"],
                "source_function": work_order["source_function"],
                "no_snippet_fact_use": True,
                "no_fact_inference_from_search_result": True,
                "max_results": 4,
            }
        )

    fallback_queries = [
        ("official_source_disambiguation_query", "site:.gov beneficiary demand public program evidence source language"),
        ("institutional_corroboration_query", "institutional report beneficiary demand public program evidence source language"),
        ("conflict_check_query", "public evidence limitation beneficiary demand program language not revenue readiness"),
        ("freshness_check_query", "current official public beneficiary demand program guidance source date"),
        ("blocked_page_alternative_query", "alternative official source public program beneficiary demand evidence"),
    ]
    for category, text in fallback_queries:
        if len(planned) >= BUDGET["max_second_pass_queries"]:
            break
        planned.append(
            {
                "query_id": f"l6_14_second_pass_query_{len(planned) + 1:03d}",
                "query_text": text,
                "linked_unresolved_claim_id": unresolved[0].get("claim_id") if unresolved else None,
                "linked_conflict_id": ingestion.get("prior_conflicts", [{}])[0].get("conflict_id")
                if ingestion.get("prior_conflicts")
                else None,
                "intended_source_type": "official_or_institutional",
                "reason": "Bound uncertainty by adding targeted corroboration or contradiction.",
                "expected_evidence_value": "Improve conflict review by adding source diversity.",
                "priority": len(planned) + 1,
                "budget_cost_estimate": {"queries": 1, "results": 4, "pages": 1},
                "query_category": category,
                "source_type": work_order["source_type"],
                "source_function": work_order["source_function"],
                "no_snippet_fact_use": True,
                "no_fact_inference_from_search_result": True,
                "max_results": 4,
            }
        )
    return planned[: BUDGET["max_second_pass_queries"]]


def preflight(config: ControlledBackendConfig, candidate_urls: list[str] | None = None) -> dict[str, Any]:
    blockers: list[str] = []
    if config.search_backend_mode not in PROVIDER_KEY_ENVS:
        blockers.append("configured_search_provider_missing_or_not_real")
    if config.page_read_backend_mode != "stdlib_public_http":
        blockers.append("configured_public_page_read_adapter_missing_or_not_real")
    if config.missing_env_names:
        blockers.append("configured_backend_missing_required_environment")
    if config.search_backend_mode in PROVIDER_KEY_ENVS and not config.search_network_allowed:
        blockers.append("search_network_allow_flag_missing")
    if config.page_read_backend_mode == "stdlib_public_http" and not config.page_read_network_allowed:
        blockers.append("page_read_network_allow_flag_missing")
    private_rejections = {}
    for url in candidate_urls or []:
        reason = reject_private_or_internal_url(url)
        if reason:
            blockers.append("private_or_internal_url_rejected")
            private_rejections[url] = reason
    return {
        "schema_version": SCHEMA_VERSION,
        "decision": "blocked" if blockers else "pass",
        "backend_mode": config.search_backend_mode,
        "page_read_mode": config.page_read_backend_mode,
        "network_allowed": config.search_network_allowed or config.page_read_network_allowed,
        "search_network_allowed": config.search_network_allowed,
        "page_read_network_allowed": config.page_read_network_allowed,
        "required_env_present": config.required_env_present,
        "missing_env_names": config.missing_env_names,
        "private_url_rejections": private_rejections,
        "blockers": sorted(set(blockers)),
        "secret_values_serialized": False,
        "ask_user_for_url": False,
        "no_side_effect_guarantees": {f"no_{action}": True for action in NO_ACTIONS},
    }


def run_second_pass_search(
    config: ControlledBackendConfig, work_order: dict[str, Any], queries: list[dict[str, Any]]
) -> dict[str, Any]:
    return ControlledSearchBackendRegistry(config).run(
        {
            "request_id": f"{RUN_ID}_search",
            "selected_work_order_id": work_order["selected_work_order_id"],
            "queries": queries,
            "budget": {
                "max_queries": BUDGET["max_second_pass_queries"],
                "max_search_results_considered": BUDGET["max_search_results_considered"],
                "max_pages_opened": BUDGET["max_pages_opened"],
                "max_domains": BUDGET["max_domains"],
                "max_pages_per_domain": BUDGET["max_pages_per_domain"],
                "max_crawl_depth": BUDGET["max_crawl_depth"],
                "max_total_external_reads": BUDGET["max_total_external_reads"],
            },
        }
    ).to_dict()


def triage_results(search_result: dict[str, Any], prior_pages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    prior_blocked_urls = {page.get("url") for page in prior_pages if page.get("evidence_eligible") is not True}
    domain_counts: dict[str, int] = {}
    for candidate in search_result.get("result_candidates", []):
        url = str(candidate.get("url", ""))
        domain = candidate.get("source_domain") or domain_from_url(url)
        rejection = reject_private_or_internal_url(url) if url else "missing_url"
        already_blocked = url in prior_blocked_urls
        domain_within_budget = domain in domain_counts or len(domain_counts) < BUDGET["max_domains"]
        can_select = (
            candidate.get("evidence_eligible") is True
            and not rejection
            and not already_blocked
            and len(selected) < BUDGET["max_pages_opened"]
            and domain_within_budget
            and domain_counts.get(domain, 0) < BUDGET["max_pages_per_domain"]
        )
        record = {
            "result_id": candidate.get("result_id"),
            "query_id": candidate.get("query_id"),
            "rank": candidate.get("rank"),
            "title": candidate.get("title"),
            "url": url,
            "source_domain": domain,
            "snippet_used_as_evidence": False,
            "search_snippet_is_evidence": False,
            "risk_class": "low" if can_select else "blocked_or_deferred",
            "prior_blocked_url": already_blocked,
            "rejection_reason": rejection or ("prior_blocked_url" if already_blocked else None),
        }
        if can_select:
            selected.append({**record, "triage_decision": "selected_for_second_pass_page_read"})
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        else:
            rejected.append({**record, "triage_decision": "rejected_or_budget_deferred"})
    return selected, rejected


def read_pages(config: ControlledBackendConfig, selected_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    urls = [item["url"] for item in selected_sources if item.get("url")]
    return ControlledPageReadAdapterRegistry(config).read_pages(
        urls,
        {
            "max_pages_opened": BUDGET["max_pages_opened"],
            "max_domains": BUDGET["max_domains"],
            "max_pages_per_domain": BUDGET["max_pages_per_domain"],
            "max_crawl_depth": BUDGET["max_crawl_depth"],
            "max_total_external_reads": BUDGET["max_total_external_reads"],
        },
    )


def classify_source(url: str, title: str | None = None) -> str:
    domain = domain_from_url(url)
    title_lower = (title or "").lower()
    if domain.endswith(".gov") or domain.endswith(".mil"):
        return "official_primary"
    if domain.endswith(".edu"):
        return "institutional"
    if domain.endswith(".org"):
        return "institutional"
    if "documentation" in title_lower or "docs" in domain:
        return "documentation"
    if any(token in domain for token in ["reuters", "apnews", "nytimes", "wsj", "statnews"]):
        return "reputable_media"
    if any(token in domain for token in ["reddit", "forum", "community"]):
        return "community"
    if any(token in domain for token in ["vendor", "company", "solutions"]):
        return "commercial_vendor"
    return "unknown"


def evidence_packets(
    work_order: dict[str, Any],
    ingestion: dict[str, Any],
    search_result: dict[str, Any],
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = {item.get("url"): item for item in search_result.get("result_candidates", [])}
    unresolved = ingestion.get("prior_unresolved_claims", [])
    conflict = (ingestion.get("prior_conflicts") or [{}])[0]
    packets: list[dict[str, Any]] = []
    for index, page in enumerate(pages, start=1):
        if len(packets) >= BUDGET["max_new_real_evidence_packets"]:
            break
        if page.get("evidence_eligible") is not True:
            continue
        candidate = candidates.get(page.get("url"), {})
        claim_candidates = [str(item).strip() for item in page.get("extracted_claim_candidates", []) if str(item).strip()]
        extracted = claim_candidates[0] if claim_candidates else truncate(page.get("text_excerpt", ""), 220)
        if not extracted:
            continue
        text = " ".join([page.get("text_excerpt", ""), extracted]).lower()
        source_quality = classify_source(str(page.get("final_url") or page.get("url")), page.get("title_if_available"))
        conflict_indicators = ["does not prove", "limitation", "insufficient", "not evidence", "paywall", "forbidden"]
        support_indicators = ["beneficiary", "demand", "program", "official", "policy", "grant", "acquisition"]
        conflict_status = "still_conflicted" if any(token in text for token in conflict_indicators) else "no_direct_conflict_detected"
        support_status = (
            "second_pass_supported_by_page_read_content"
            if any(token in text for token in support_indicators)
            else "second_pass_context_requires_review"
        )
        packets.append(
            {
                "schema_version": SCHEMA_VERSION,
                "evidence_packet_id": f"l6_14_real_evidence_packet_{len(packets) + 1:03d}",
                "run_id": RUN_ID,
                "prior_run_id": ingestion.get("prior_run_id", PRIOR_RUN_ID),
                "real_or_fixture": "real",
                "work_order_id": work_order["selected_work_order_id"],
                "query_id": candidate.get("query_id"),
                "linked_unresolved_claim_id": unresolved[0].get("claim_id") if unresolved else None,
                "linked_conflict_id": conflict.get("conflict_id"),
                "source_url": page.get("url"),
                "final_url": page.get("final_url"),
                "source_domain": page.get("source_domain"),
                "source_type": source_quality,
                "source_quality_label": source_quality,
                "freshness_label": "date_missing_or_review_required",
                "page_read_id": page.get("page_read_id"),
                "search_snippet_locator": truncate(candidate.get("snippet", ""), 280),
                "snippet_used_as_evidence": False,
                "search_snippet_is_evidence": False,
                "page_read_content_used_as_evidence": True,
                "extracted_text_excerpt": truncate(page.get("text_excerpt", ""), 500),
                "bounded_claim": truncate(extracted, 260),
                "claim_scope": work_order["claim_boundary"],
                "support_status": support_status,
                "conflict_status": conflict_status,
                "limitations": [
                    "real evidence requires human review",
                    "second-pass evidence reduces uncertainty but is not canonical truth",
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


def source_quality_matrix(prior_packets: list[dict[str, Any]], new_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for packet in prior_packets + new_packets:
        label = packet.get("source_quality_label", "unknown")
        matrix.append(
            {
                "evidence_packet_id": packet.get("evidence_packet_id"),
                "run_id": packet.get("run_id"),
                "real_or_fixture": packet.get("real_or_fixture"),
                "source_url": packet.get("source_url"),
                "domain": packet.get("source_domain"),
                "source_quality_label": label,
                "freshness_label": packet.get("freshness_label"),
                "page_read_succeeded": bool(packet.get("extracted_text_excerpt")),
                "evidence_extracted": bool(packet.get("bounded_claim")),
                "primary_secondary_community": (
                    "primary"
                    if label == "official_primary"
                    else "secondary"
                    if label in {"official_secondary", "institutional", "documentation", "reputable_media"}
                    else "community_or_unknown"
                ),
                "trust_limitations": packet.get("limitations", []),
                "llm_confidence_as_truth_authority": False,
                "semantic_truth_score_used": False,
            }
        )
    return matrix


def build_claim_boundary_update(
    ingestion: dict[str, Any], new_packets: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    prior_unresolved = ingestion.get("prior_unresolved_claims", [])
    updated_claims: list[dict[str, Any]] = []
    unresolved_after: list[dict[str, Any]] = []
    for claim in prior_unresolved:
        linked_packets = [
            packet for packet in new_packets if packet.get("linked_unresolved_claim_id") == claim.get("claim_id")
        ]
        status = "bounded_by_second_pass_evidence" if linked_packets else "unchanged_no_new_evidence"
        updated = {
            "claim_id": claim.get("claim_id"),
            "prior_status": claim.get("support_status"),
            "prior_conflict_status": claim.get("conflict_status"),
            "bounded_claim": claim.get("bounded_claim"),
            "new_evidence_packet_ids": [packet["evidence_packet_id"] for packet in linked_packets],
            "post_second_pass_claim_boundary": status,
            "external_use_authorized": False,
            "review_required": True,
        }
        updated_claims.append(updated)
        if status != "bounded_by_second_pass_evidence":
            unresolved_after.append(updated)
    for packet in new_packets:
        updated_claims.append(
            {
                "claim_id": f"l6_14_claim_{len(updated_claims) + 1:03d}",
                "prior_status": None,
                "prior_conflict_status": None,
                "bounded_claim": packet.get("bounded_claim"),
                "new_evidence_packet_ids": [packet["evidence_packet_id"]],
                "post_second_pass_claim_boundary": packet.get("support_status"),
                "external_use_authorized": False,
                "review_required": True,
            }
        )
    return updated_claims, unresolved_after


def conflict_decisions(
    ingestion: dict[str, Any], new_packets: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    conflicts = ingestion.get("prior_conflicts", [])
    unresolved = {item.get("claim_id"): item for item in ingestion.get("prior_unresolved_claims", [])}
    for index, conflict in enumerate(conflicts or [{"conflict_id": "l6_14_no_prior_conflict"}], start=1):
        claim_id = conflict.get("claim_id")
        claim = unresolved.get(claim_id, {})
        linked = [
            packet
            for packet in new_packets
            if packet.get("linked_conflict_id") == conflict.get("conflict_id")
            or packet.get("linked_unresolved_claim_id") == claim_id
        ]
        supporting = [
            packet for packet in linked if packet.get("conflict_status") != "still_conflicted"
        ]
        conflicting = [
            packet for packet in linked if packet.get("conflict_status") == "still_conflicted"
        ]
        if supporting and not conflicting:
            status = "bounded_conflict"
            residual = "Second-pass evidence adds reviewable support, but the prior conflict still needs human review before being marked resolved."
        elif supporting and conflicting:
            status = "still_conflicted_with_reason"
            residual = "Second-pass found both supporting and limiting evidence."
        elif linked:
            status = "insufficient_evidence_after_second_pass"
            residual = "Second-pass pages were readable but did not add decisive support."
        else:
            status = "insufficient_evidence_after_second_pass"
            residual = "No new evidence packet linked to this conflict."
        decisions.append(
            {
                "conflict_id": conflict.get("conflict_id", f"l6_14_conflict_{index:03d}"),
                "unresolved_claim_id": claim_id,
                "prior_status": claim.get("support_status", "unknown"),
                "new_evidence_packet_ids": [packet["evidence_packet_id"] for packet in linked],
                "supporting_sources": [packet.get("source_url") for packet in supporting],
                "conflicting_sources": [packet.get("source_url") for packet in conflicting],
                "source_quality_comparison": {
                    "supporting": [packet.get("source_quality_label") for packet in supporting],
                    "conflicting": [packet.get("source_quality_label") for packet in conflicting],
                },
                "freshness_comparison": {
                    "supporting": [packet.get("freshness_label") for packet in supporting],
                    "conflicting": [packet.get("freshness_label") for packet in conflicting],
                },
                "claim_boundary_update": "internal_review_only_with_second_pass_context",
                "post_second_pass_status": status,
                "residual_reason": residual,
                "review_required": True,
                "recommended_next_action": "ready_for_human_review"
                if supporting
                else "run_third_pass_observation",
            }
        )
    return decisions


def classify_post_second_pass(
    preflight_result: dict[str, Any],
    search_result: dict[str, Any],
    pages: list[dict[str, Any]],
    packets: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> str:
    if preflight_result.get("decision") != "pass":
        blockers = set(preflight_result.get("blockers", []))
        if any("budget" in blocker or "private_or_internal" in blocker for blocker in blockers):
            return "second_pass_blocked_by_budget_or_safety"
        return "second_pass_blocked_by_backend_or_network"
    if not search_result.get("search_executed"):
        return "second_pass_blocked_by_backend_or_network"
    if not pages and search_result.get("search_executed"):
        return "second_pass_blocked_by_budget_or_safety"
    if not packets:
        return "insufficient_evidence_after_second_pass"
    statuses = {item.get("post_second_pass_status") for item in decisions}
    if statuses == {"resolved"}:
        return "conflict_resolved"
    if "bounded_conflict" in statuses:
        return "conflict_bounded"
    if "still_conflicted_with_reason" in statuses:
        return "still_conflicted_with_reason"
    return "insufficient_evidence_after_second_pass"


def next_action_packet(post_classification: str, decisions: list[dict[str, Any]]) -> dict[str, Any]:
    if post_classification in {"conflict_resolved", "conflict_bounded"}:
        action = "ready_for_human_review"
    elif post_classification == "still_conflicted_with_reason":
        action = "run_third_pass_observation"
    elif post_classification == "second_pass_blocked_by_backend_or_network":
        action = "blocked_pending_backend_or_network"
    else:
        action = "add_better_html_extraction"
    return {
        "schema_version": SCHEMA_VERSION,
        "recommended_next_action": action,
        "reason": "Second-pass evidence reduced uncertainty enough for review."
        if action == "ready_for_human_review"
        else "Additional governed observation or extraction quality is needed.",
        "evidence_basis": [item.get("conflict_id") for item in decisions],
        "risk": "low_read_only_review_risk",
        "expected_value": "Improve decision usefulness without downstream action.",
        "requires_external_side_effects": False,
        "requires_core_writeback": False,
    }


def no_action_receipt() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": RUN_ID,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "actions": [
            {
                "action": action,
                "authorized": False,
                "executed": False,
                "occurred": False,
            }
            for action in NO_ACTIONS
        ],
    }


def mission_report_md(summary: dict[str, Any], decisions: list[dict[str, Any]], next_action: dict[str, Any]) -> str:
    return (
        "# L6.14 Updated Mission Evidence Report\n\n"
        "## Executive Summary\n\n"
        f"Post-second-pass classification: `{summary['post_second_pass_classification']}`. "
        f"Second-pass real observation executed: {summary['second_pass_real_observation_executed']}.\n\n"
        "## Prior L6.13 Evidence State\n\n"
        f"- Prior classification: {summary['prior_run_classification']}\n"
        f"- Prior real evidence packets: {summary['prior_real_evidence_packets']}\n"
        f"- Conflicts before: {summary['conflicts_before']}\n"
        f"- Unresolved claims before: {summary['unresolved_claims_before']}\n\n"
        "## L6.14 Second-Pass Objective\n\n"
        "Resolve or bound the unresolved L6.13 conflict using targeted controlled search and public page reads.\n\n"
        "## Second-Pass Results\n\n"
        f"- Queries generated: {summary['second_pass_queries_generated']}\n"
        f"- Search results considered: {summary['search_results_considered']}\n"
        f"- Pages opened: {summary['pages_opened']}\n"
        f"- Domains touched: {summary['domains_touched']}\n"
        f"- External reads used: {summary['external_reads_used']}\n"
        f"- New real evidence packets: {summary['new_real_evidence_packets']}\n\n"
        "## Conflict Resolution Decision\n\n"
        + "\n".join(
            f"- {item['conflict_id']}: {item['post_second_pass_status']} ({item['residual_reason']})"
            for item in decisions
        )
        + "\n\n## Next Action Recommendation\n\n"
        f"`{next_action['recommended_next_action']}`: {next_action['reason']}\n\n"
        "## No-Side-Effect Receipt\n\n"
        "No login, payment, form submission, posting, outreach, publication, MCP/live behavior, "
        "core writeback, or user URL request occurred.\n"
    )


def write_static_files(summary: dict[str, Any], generated: list[str]) -> None:
    write_text(
        "l6_real_evidence_conflict_resolution_sprint/README.md",
        f"# {MILESTONE_ID} {MILESTONE_NAME}\n\nIterative real evidence refinement over the L6.13 mission evidence state.\n",
        generated,
    )
    write_text(
        "l6_real_evidence_conflict_resolution_sprint/l6_14_summary.md",
        f"# L6.14 Summary\n\nPost-second-pass classification: {summary['post_second_pass_classification']}.\n",
        generated,
    )
    reports = {
        "real_evidence_report_ingestion/real_evidence_report_ingestion_report.md": "Prior L6.13 real evidence report ingested and normalized.",
        "unresolved_claim_analysis/unresolved_claim_analysis_report.md": "Unresolved, conflicting, weak, single-source, and blocked page-read claims analyzed.",
        "second_pass_query_planning/second_pass_query_planning_report.md": "Targeted second-pass queries generated from unresolved claims and L6.13 refinements.",
        "second_pass_search_execution/second_pass_search_execution_report.md": "Controlled search executed only when repo-external backend config passed preflight.",
        "second_pass_page_read_receipts/second_pass_page_read_report.md": "Public page reads used GET-only stdlib adapter and blocked unsafe pages.",
        "second_pass_evidence_packets/second_pass_evidence_report.md": "Second-pass evidence packets come from page-read content, never snippets.",
        "source_quality_update_matrix/source_quality_update_report.md": "Source quality labels remain deterministic and review-oriented.",
        "claim_boundary_update/claim_boundary_update_report.md": "Claim boundaries remain internal-review-only.",
        "corroboration_conflict_update/corroboration_conflict_update_report.md": "Conflict matrix updated with second-pass evidence.",
        "conflict_resolution_decision_packet/conflict_resolution_decision_report.md": "Decision packet bounds or reports unresolved conflicts.",
        "residual_limitation_report/residual_limitation_report.md": "Residual limitations remain review-gated.",
        "next_action_recommendation_packet/next_action_recommendation_report.md": "Next action is generated without external side effects.",
    }
    for path, text in reports.items():
        write_text(path, f"# {Path(path).stem.replace('_', ' ').title()}\n\n{text}\n", generated)


def main() -> int:
    generated: list[str] = []
    work_order = selected_work_order()
    ingestion = ingest_prior_report()
    queries = plan_second_pass_queries(work_order, ingestion)
    config = ControlledBackendConfig.from_environment(ROOT)
    first_preflight = preflight(config)

    search_result = {
        "backend_mode": config.search_backend_mode,
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
    selected_sources: list[dict[str, Any]] = []
    rejected_sources: list[dict[str, Any]] = []
    second_preflight = first_preflight
    pages: list[dict[str, Any]] = []
    new_packets: list[dict[str, Any]] = []

    if first_preflight["decision"] == "pass":
        search_result = run_second_pass_search(config, work_order, queries)
        selected_sources, rejected_sources = triage_results(
            search_result, ingestion.get("blocked_or_failed_page_reads", [])
        )
        remaining_page_reads = max(
            0,
            BUDGET["max_total_external_reads"] - int(search_result.get("external_reads_count", 0)),
        )
        if len(selected_sources) > remaining_page_reads:
            rejected_sources.extend(
                {
                    **item,
                    "triage_decision": "rejected_or_budget_deferred",
                    "rejection_reason": "max_total_external_reads_remaining_page_budget",
                }
                for item in selected_sources[remaining_page_reads:]
            )
            selected_sources = selected_sources[:remaining_page_reads]
        second_preflight = preflight(config, [item["url"] for item in selected_sources])
        if search_result.get("search_executed") and second_preflight["decision"] == "pass":
            pages = read_pages(config, selected_sources)
            new_packets = evidence_packets(work_order, ingestion, search_result, pages)

    quality = source_quality_matrix(ingestion.get("prior_real_evidence_packets", []), new_packets)
    updated_claims, unresolved_after = build_claim_boundary_update(ingestion, new_packets)
    decisions = conflict_decisions(ingestion, new_packets)
    post_classification = classify_post_second_pass(
        second_preflight, search_result, pages, new_packets, decisions
    )
    next_action = next_action_packet(post_classification, decisions)
    receipt = no_action_receipt()
    domains_touched = sorted({page.get("source_domain") for page in pages if page.get("source_domain")})
    external_reads_used = int(search_result.get("external_reads_count", 0)) + sum(
        1 for page in pages if page.get("safety_flags", {}).get("network_used")
    )
    blockers = sorted(
        set(
            first_preflight.get("blockers", [])
            + second_preflight.get("blockers", [])
            + ([search_result.get("error_code")] if search_result.get("error_code") else [])
        )
    )
    conflicts_after = sum(
        1
        for item in decisions
        if item.get("post_second_pass_status")
        in {"still_conflicted_with_reason", "bounded_conflict", "insufficient_evidence_after_second_pass"}
    )
    unresolved_after_count = len(unresolved_after) if not new_packets else sum(
        1 for item in decisions if item.get("post_second_pass_status") != "resolved"
    )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "run_id": RUN_ID,
        "prior_run_id": ingestion.get("prior_run_id", PRIOR_RUN_ID),
        "prior_run_classification": ingestion.get("prior_run_classification"),
        "post_second_pass_classification": post_classification,
        "allowed_post_second_pass_classifications": POST_SECOND_PASS_CLASSIFICATIONS,
        "l6_14_real_evidence_conflict_resolution_sprint_complete": True,
        "selected_work_order_id": work_order["selected_work_order_id"],
        "backend_mode": config.search_backend_mode,
        "page_read_mode": config.page_read_backend_mode,
        "network_allowed": config.search_network_allowed or config.page_read_network_allowed,
        "safety_preflight_decision": second_preflight.get("decision"),
        "second_pass_real_observation_executed": bool(new_packets),
        "second_pass_search_executed": bool(search_result.get("search_executed")),
        "second_pass_queries_generated": len(queries),
        "search_results_considered": search_result.get("search_results_considered", 0),
        "pages_opened": len(pages),
        "domains_touched": len(domains_touched),
        "crawl_depth_used": 1 if pages else 0,
        "external_reads_used": external_reads_used,
        "prior_real_evidence_packets": ingestion.get("prior_real_evidence_packet_count", 0),
        "new_real_evidence_packets": len(new_packets),
        "total_real_evidence_packets": ingestion.get("prior_real_evidence_packet_count", 0) + len(new_packets),
        "conflicts_before": ingestion.get("prior_conflict_count", 0),
        "conflicts_after": conflicts_after,
        "unresolved_claims_before": ingestion.get("prior_unresolved_claim_count", 0),
        "unresolved_claims_after": unresolved_after_count,
        "conflict_resolution_status": decisions[0].get("post_second_pass_status") if decisions else "not_evaluated",
        "next_action_recommendation": next_action["recommended_next_action"],
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "search_snippets_used_as_evidence": False,
        "page_read_content_used_as_evidence": bool(new_packets),
        "blockers": blockers,
        **BUDGET,
        **SAFETY_FLAGS,
    }

    write_json(
        "l6_real_evidence_conflict_resolution_sprint/l6_14_milestone_contract.json",
        {**summary, "contract_type": "milestone_contract"},
        generated,
    )
    write_json(
        "l6_real_evidence_conflict_resolution_sprint/l6_14_scope.json",
        {
            "schema_version": SCHEMA_VERSION,
            "scope": "second-pass real evidence conflict resolution",
            "manual_url_request_allowed": False,
            "manual_search_request_allowed": False,
            "real_public_read_only_observation_allowed_if_configured": True,
        },
        generated,
    )
    write_json("l6_real_evidence_conflict_resolution_sprint/l6_14_budget_policy.json", {"schema_version": SCHEMA_VERSION, **BUDGET}, generated)
    write_json("l6_real_evidence_conflict_resolution_sprint/l6_14_safety_flags.json", {"schema_version": SCHEMA_VERSION, **SAFETY_FLAGS}, generated)
    write_json("l6_real_evidence_conflict_resolution_sprint/l6_14_summary.json", summary, generated)

    write_json("real_evidence_report_ingestion/prior_mission_evidence_ingestion.json", ingestion, generated)
    write_json(
        "real_evidence_report_ingestion/prior_real_evidence_packet_index.json",
        {
            "schema_version": SCHEMA_VERSION,
            "prior_real_evidence_packet_count": ingestion.get("prior_real_evidence_packet_count", 0),
            "packets": [
                {
                    "evidence_packet_id": packet.get("evidence_packet_id"),
                    "source_url": packet.get("source_url"),
                    "support_status": packet.get("support_status"),
                    "conflict_status": packet.get("conflict_status"),
                }
                for packet in ingestion.get("prior_real_evidence_packets", [])
            ],
        },
        generated,
    )
    write_json("unresolved_claim_analysis/unresolved_claim_analysis.json", {"schema_version": SCHEMA_VERSION, "unresolved_claims": ingestion.get("prior_unresolved_claims", []), "conflicting_claims": ingestion.get("prior_conflicts", []), "weakly_supported_claims": ingestion.get("weakly_supported_claims", []), "single_source_claims": ingestion.get("single_source_claims", []), "blocked_page_reads": ingestion.get("blocked_or_failed_page_reads", [])}, generated)
    write_json("unresolved_claim_analysis/conflict_resolution_targets.json", {"schema_version": SCHEMA_VERSION, "target_count": min(ingestion.get("prior_conflict_count", 0), BUDGET["max_conflict_resolution_targets"]), "targets": ingestion.get("prior_conflicts", [])[: BUDGET["max_conflict_resolution_targets"]]}, generated)

    write_json("second_pass_query_planning/second_pass_query_plan.json", {"schema_version": SCHEMA_VERSION, "query_count": len(queries), "queries": queries}, generated)
    write_json("second_pass_query_planning/second_pass_query_priority_matrix.json", {"schema_version": SCHEMA_VERSION, "priorities": [{"query_id": item["query_id"], "priority": item["priority"], "linked_unresolved_claim_id": item.get("linked_unresolved_claim_id"), "linked_conflict_id": item.get("linked_conflict_id")} for item in queries]}, generated)
    write_json("second_pass_search_execution/second_pass_search_result.json", search_result, generated)
    write_json("second_pass_search_execution/second_pass_search_trace.json", {"schema_version": SCHEMA_VERSION, "search_executed": bool(search_result.get("search_executed")), "backend_mode": config.search_backend_mode, "search_query_count": search_result.get("search_query_count", 0), "search_results_considered": search_result.get("search_results_considered", 0), "snippets_used_as_evidence": False, "facts_inferred_from_snippets": False, "asked_user_for_url": False, "blockers": blockers}, generated)
    write_json("second_pass_search_execution/selected_sources_to_open.json", {"schema_version": SCHEMA_VERSION, "selected_count": len(selected_sources), "sources": selected_sources}, generated)
    write_json("second_pass_search_execution/rejected_search_results.json", {"schema_version": SCHEMA_VERSION, "rejected_count": len(rejected_sources), "results": rejected_sources}, generated)

    write_json("second_pass_page_read_receipts/second_pass_page_read_trace.json", {"schema_version": SCHEMA_VERSION, "page_read_executed": bool(pages), "pages_opened": len(pages), "domains_touched": domains_touched, "crawl_depth_used": 1 if pages else 0, "external_reads_used": external_reads_used}, generated)
    write_json("second_pass_page_read_receipts/second_pass_page_read_receipt_index.json", {"schema_version": SCHEMA_VERSION, "page_read_count": len(pages), "pages": pages}, generated)
    write_json("second_pass_page_read_receipts/blocked_page_read_registry.json", {"schema_version": SCHEMA_VERSION, "blocked_page_count": sum(1 for page in pages if page.get("evidence_eligible") is not True), "blocked_pages": [page for page in pages if page.get("evidence_eligible") is not True]}, generated)

    write_json("second_pass_evidence_packets/second_pass_evidence_packet_schema.json", {"schema_version": SCHEMA_VERSION, "required_fields": ["evidence_packet_id", "run_id", "prior_run_id", "real_or_fixture", "work_order_id", "query_id", "linked_unresolved_claim_id", "linked_conflict_id", "source_url", "final_url", "source_domain", "source_type", "source_quality_label", "freshness_label", "page_read_id", "extracted_text_excerpt", "bounded_claim", "claim_scope", "support_status", "conflict_status", "limitations", "generated_at_utc"]}, generated)
    write_json("second_pass_evidence_packets/second_pass_evidence_packet_index.json", {"schema_version": SCHEMA_VERSION, "new_real_evidence_packet_count": len(new_packets), "packets": [{"evidence_packet_id": packet["evidence_packet_id"], "path": f"second_pass_evidence_packets/second_pass_evidence_packet_{index:03d}.json", "real_or_fixture": packet["real_or_fixture"]} for index, packet in enumerate(new_packets, start=1)]}, generated)
    if new_packets:
        for index, packet in enumerate(new_packets, start=1):
            write_json(f"second_pass_evidence_packets/second_pass_evidence_packet_{index:03d}.json", packet, generated)
    else:
        write_json("second_pass_evidence_packets/second_pass_blocked_evidence_packet.json", {"schema_version": SCHEMA_VERSION, "live_source_evidence_captured": False, "reason": post_classification, "search_snippets_used_as_evidence": False}, generated)

    write_json("source_quality_update_matrix/source_quality_update_matrix.json", {"schema_version": SCHEMA_VERSION, "allowed_labels": SOURCE_QUALITY_LABELS, "sources": quality}, generated)
    write_json("claim_boundary_update/claim_boundary_update_table.json", {"schema_version": SCHEMA_VERSION, "claims": updated_claims}, generated)
    write_json("claim_boundary_update/unresolved_claims_after_second_pass.json", {"schema_version": SCHEMA_VERSION, "unresolved_claim_count": unresolved_after_count, "unresolved_claims": unresolved_after}, generated)
    write_json("corroboration_conflict_update/corroboration_conflict_update_matrix.json", {"schema_version": SCHEMA_VERSION, "decisions": decisions}, generated)
    write_json("corroboration_conflict_update/conflict_registry_after_second_pass.json", {"schema_version": SCHEMA_VERSION, "conflicts_before": ingestion.get("prior_conflict_count", 0), "conflicts_after": conflicts_after, "conflicts": decisions}, generated)
    write_json("conflict_resolution_decision_packet/conflict_resolution_decision_packet.json", {"schema_version": SCHEMA_VERSION, "post_second_pass_classification": post_classification, "decisions": decisions}, generated)
    write_json("residual_limitation_report/residual_limitation_report.json", {"schema_version": SCHEMA_VERSION, "residuals": [item["residual_reason"] for item in decisions], "blockers": blockers, "limitations": ["Evidence remains review-gated.", "No downstream action authorized.", "Search snippets remain locator metadata only."]}, generated)
    write_json("next_action_recommendation_packet/next_action_recommendation_packet.json", next_action, generated)
    write_json("l6_14_no_action_receipts/no_side_effect_receipt.json", receipt, generated)
    write_json("l6_14_no_action_receipts/no_action_receipt_index.json", {"schema_version": SCHEMA_VERSION, "receipt_count": len(NO_ACTIONS), "actions": NO_ACTIONS}, generated)
    write_text("l6_14_no_action_receipts/no_action_receipt_report.md", "# L6.14 No-Action Receipt\n\nNo login, payment, form submission, posting, outreach, publication, MCP/live behavior, core writeback, or user URL request occurred.\n", generated)

    updated_report = {
        "schema_version": SCHEMA_VERSION,
        "summary": summary,
        "prior_l6_13_evidence_state": ingestion,
        "l6_14_second_pass_objective": "Resolve or bound unresolved real evidence conflict from L6.13.",
        "second_pass_queries": queries,
        "sources_considered": search_result.get("result_candidates", []),
        "pages_read": pages,
        "new_real_evidence_packets": new_packets,
        "source_quality_update": quality,
        "claim_boundary_update": updated_claims,
        "corroboration_conflict_update": decisions,
        "conflict_resolution_decision": decisions,
        "remaining_residuals": [item["residual_reason"] for item in decisions],
        "next_action_recommendation": next_action,
        "no_side_effect_receipt": receipt,
    }
    write_json("real_mission_evidence_report/l6_14_updated_mission_evidence_report.json", updated_report, generated)
    write_text("real_mission_evidence_report/l6_14_updated_mission_evidence_report.md", mission_report_md(summary, decisions, next_action), generated)

    write_json("l6_14_read_model/l6_14_cieu_like_fixture.json", {"schema_version": SCHEMA_VERSION, "X_t": "L6.13 real evidence collected with unresolved conflicts", "U_t": "L6.14 second-pass real evidence conflict-resolution sprint", "Y_star_t": "Run a bounded second-pass observation loop to reduce uncertainty and keep all downstream side effects blocked.", "Y_t_plus_1": summary, "R_t_plus_1": {"blockers": blockers, "next_action": next_action}, "event_mode": "l6_14_real_evidence_conflict_resolution_sprint_fixture"}, generated)
    write_json("l6_14_read_model/l6_14_strategic_residual_delta.json", {"schema_version": SCHEMA_VERSION, "residuals": [item["residual_reason"] for item in decisions], "post_second_pass_classification": post_classification}, generated)
    write_json("l6_14_read_model/l6_14_meta_learning_update_candidate.json", {"schema_version": SCHEMA_VERSION, "eligible_for_review_queue": True, "eligible_for_direct_brain_writeback": False, "eligible_for_direct_memory_ingestion": False, "eligible_for_candidate_auto_approval": False, "eligible_for_direct_strategy_mutation": False, "approved": False, "applied": False}, generated)
    write_json("l6_14_read_model/l6_14_readiness_assessment.json", {**summary, "ready_for_human_review": next_action["recommended_next_action"] == "ready_for_human_review", "ready_for_governed_planning": post_classification in {"conflict_resolved", "conflict_bounded"}, "next_step": next_action["recommended_next_action"]}, generated)
    write_json("l6_14_read_model/l6_14_blockers.json", {"schema_version": SCHEMA_VERSION, "blockers": blockers, "post_second_pass_classification": post_classification}, generated)
    write_json("l6_14_read_model/l6_14_next_action_recommendation.json", next_action, generated)
    write_json("l6_14_read_model/l6_14_read_model_summary.json", summary, generated)
    write_text("l6_14_read_model/l6_14_report.md", mission_report_md(summary, decisions, next_action), generated)

    write_json("l6_real_evidence_conflict_resolution_sprint/l6_14_generation_manifest.json", {"schema_version": SCHEMA_VERSION, "generated_at_utc": utc_now(), "generated_files": generated}, generated)
    write_static_files(summary, generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
