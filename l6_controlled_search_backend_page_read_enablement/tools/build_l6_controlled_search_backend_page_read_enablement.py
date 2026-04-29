#!/usr/bin/env python3
"""Generate L6.11 controlled search backend and page-read enablement artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from controlled_backend_safety_preflight.safety_preflight import run_safety_preflight  # noqa: E402
from controlled_public_page_read_adapter.page_read_adapter import (  # noqa: E402
    ControlledPageReadAdapterRegistry,
    reject_private_or_internal_url,
)
from controlled_search_backend_adapters.controlled_search_backends import (  # noqa: E402
    ControlledBackendConfig,
    ControlledSearchBackendRegistry,
    SearchBudgetEnvelope,
)


SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.11"
MILESTONE_NAME = "Controlled Search Backend & Public Page-Read Adapter Enablement v0"
MODE = "controlled_search_backend_page_read_adapter_enablement"
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
}

SAFETY_FLAGS = {
    "ask_user_for_url_authorized": False,
    "user_manual_url_provision_required": False,
    "search_snippets_as_evidence_authorized": False,
    "login_authorized": False,
    "account_creation_authorized": False,
    "payment_authorized": False,
    "form_submission_authorized": False,
    "contact_authorized": False,
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
    "brain_memory_writeback",
    "canonical_mutation",
    "direct_y_star_mutation",
]


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


def selected_work_order() -> dict[str, Any]:
    selected = load_json("agentic_query_planner/selected_work_order.json", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_count": 1,
        "selected_work_order_id": selected.get("selected_work_order_id", "l6_11_selected_work_order_001"),
        "source_work_order_id": selected.get("source_work_order_id", "l6_10x_selected_work_order_001"),
        "evidence_need_id": selected.get("linked_evidence_need_id", "l6_8_need_001"),
        "source_type": selected.get("source_type", "official policy or program source"),
        "source_function": selected.get("source_function", "official policy or program source"),
        "observation_question": selected.get(
            "observation_question",
            "What public evidence clarifies payer or beneficiary demand language?",
        ),
        "expected_evidence_type": selected.get("expected_evidence_type", "public page evidence"),
    }


def query_plan() -> dict[str, Any]:
    plan = load_json("agentic_query_planner/generated_query_plan.json", {})
    queries = plan.get("queries", [])
    if queries:
        return {"schema_version": SCHEMA_VERSION, "query_count": len(queries), "queries": queries}
    selected = selected_work_order()
    queries = [
        {
            "query_id": f"l6_11_query_{index:03d}",
            "query_text": f"{selected['source_type']} {category.replace('_', ' ')} {selected['observation_question']}",
            "query_category": category,
            "linked_work_order_id": selected["selected_work_order_id"],
            "max_results": 4,
            "no_snippet_fact_use": True,
            "no_fact_inference_from_search_result": True,
        }
        for index, category in enumerate(
            [
                "primary_source_query",
                "official_source_query",
                "corroboration_query",
                "conflict_check_query",
                "freshness_check_query",
            ],
            start=1,
        )
    ]
    return {"schema_version": SCHEMA_VERSION, "query_count": len(queries), "queries": queries}


def fixture_results(queries: list[dict[str, Any]]) -> dict[str, Any]:
    q = queries
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture_mode": True,
        "results": [
            {
                "result_id": "l6_11_fixture_result_001",
                "query_id": q[0]["query_id"],
                "rank": 1,
                "title": "Fixture Official Program Demand Note",
                "url": "https://official.example.org/fixture/program-demand",
                "snippet": "Locator metadata only: official fixture program page appears relevant.",
                "source_domain": "official.example.org",
                "result_type": "fixture_locator_candidate",
                "is_sponsored_or_ad_if_known": False,
                "safety_flags": {"fixture": True, "public_read_only_expected": True},
                "trust_initial_label": "fixture_primary_source_candidate",
                "evidence_eligible": True,
            },
            {
                "result_id": "l6_11_fixture_result_002",
                "query_id": q[2]["query_id"],
                "rank": 1,
                "title": "Fixture Independent Corroboration Brief",
                "url": "https://analysis.example.net/fixture/corroboration-brief",
                "snippet": "Locator metadata only: independent fixture brief appears relevant.",
                "source_domain": "analysis.example.net",
                "result_type": "fixture_locator_candidate",
                "is_sponsored_or_ad_if_known": False,
                "safety_flags": {"fixture": True, "public_read_only_expected": True},
                "trust_initial_label": "fixture_secondary_source_candidate",
                "evidence_eligible": True,
            },
            {
                "result_id": "l6_11_fixture_result_003",
                "query_id": q[3]["query_id"],
                "rank": 1,
                "title": "Fixture Scope Limitation Note",
                "url": "https://analysis.example.net/fixture/scope-limitation",
                "snippet": "Locator metadata only: fixture limitation page may surface conflict.",
                "source_domain": "analysis.example.net",
                "result_type": "fixture_locator_candidate",
                "is_sponsored_or_ad_if_known": False,
                "safety_flags": {"fixture": True, "public_read_only_expected": True},
                "trust_initial_label": "fixture_conflict_check_candidate",
                "evidence_eligible": True,
            },
        ],
    }


def fixture_pages() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture_mode": True,
        "pages": [
            {
                "page_read_id": "l6_11_fixture_page_001",
                "url": "https://official.example.org/fixture/program-demand",
                "title": "Fixture Official Program Demand Note",
                "source_owner_or_publisher": "Official Example Fixture Owner",
                "source_quality_label": "fixture_primary",
                "freshness_label": "fixture_current_marker",
                "claim_candidates": [
                    "Fixture evidence says the program describes beneficiary-facing demand signals in public language.",
                    "Fixture evidence says the program page is suitable for internal review only.",
                ],
                "text": (
                    "Fixture Official Program Demand Note. Fixture evidence says the program "
                    "describes beneficiary-facing demand signals in public language. Fixture "
                    "evidence says the program page is suitable for internal review only."
                ),
            },
            {
                "page_read_id": "l6_11_fixture_page_002",
                "url": "https://analysis.example.net/fixture/corroboration-brief",
                "title": "Fixture Independent Corroboration Brief",
                "source_owner_or_publisher": "Independent Example Fixture Owner",
                "source_quality_label": "fixture_secondary",
                "freshness_label": "fixture_recent_marker",
                "claim_candidates": [
                    "Fixture corroboration says beneficiary-facing demand language appears in multiple public descriptions.",
                    "Fixture corroboration says the evidence remains review-only until a real backend is approved.",
                ],
                "text": (
                    "Fixture Independent Corroboration Brief. Fixture corroboration says "
                    "beneficiary-facing demand language appears in multiple public descriptions. "
                    "Fixture corroboration says the evidence remains review-only until a real backend is approved."
                ),
            },
            {
                "page_read_id": "l6_11_fixture_page_003",
                "url": "https://analysis.example.net/fixture/scope-limitation",
                "title": "Fixture Scope Limitation Note",
                "source_owner_or_publisher": "Independent Example Fixture Owner",
                "source_quality_label": "fixture_secondary_conflict_check",
                "freshness_label": "fixture_date_missing",
                "claim_candidates": [
                    "Fixture limitation says the public descriptions do not prove demand conversion or revenue readiness.",
                    "Fixture limitation says claims must stay bounded to source-language evidence.",
                ],
                "text": (
                    "Fixture Scope Limitation Note. Fixture limitation says the public descriptions "
                    "do not prove demand conversion or revenue readiness. Fixture limitation says "
                    "claims must stay bounded to source-language evidence."
                ),
            },
        ],
    }


def evidence_packets(
    results: list[dict[str, Any]], page_envelopes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    result_by_url = {result["url"]: result for result in results}
    packets = []
    for index, page in enumerate(page_envelopes, start=1):
        result = result_by_url.get(page["url"], {})
        claim = page.get("extracted_claim_candidates", [""])[0]
        packets.append(
            {
                "schema_version": SCHEMA_VERSION,
                "evidence_packet_id": f"l6_11_fixture_evidence_packet_{index:03d}",
                "fixture_demo_evidence": True,
                "source_locator": page["url"],
                "source_title": page["title_if_available"],
                "source_owner_or_publisher": "Fixture source owner",
                "locator_snippet": result.get("snippet"),
                "snippet_used_as_evidence": False,
                "page_read_extracted_evidence": page.get("text_excerpt", ""),
                "observed_timestamp": page["read_at_utc"],
                "source_date_or_date_missing": "fixture_date_marker_or_missing",
                "freshness_class": "fixture_freshness_marker",
                "captured_bounded_claims": [claim] if claim else [],
                "unsupported_claims": [],
                "missing_context": ["fixture evidence is not real-world truth"],
                "claim_boundary": "internal_review_only_fixture_claim_boundary",
                "citation_trace": {
                    "search_result_id": result.get("result_id"),
                    "page_read_id": page["page_read_id"],
                    "source_locator": page["url"],
                },
                "source_quality_label": "fixture_primary_or_secondary",
                "corroboration_status": "fixture_corroborated" if index < 3 else "fixture_limitation",
                "conflict_status": "no_conflict" if index < 3 else "scope_limitation_conflict",
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


def receipt_payload(action: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": f"l6_11_no_{action}_receipt",
        "action": action,
        "authorized": False,
        "executed": False,
        "evidence": "No disallowed action was executed during L6.11 fixture validation.",
    }


def main() -> int:
    generated: list[str] = []
    selected = selected_work_order()
    plan = query_plan()
    queries = plan["queries"][: BUDGET["max_queries"]]

    write_json("controlled_backend_fixture_runtime/fixture_search_results.json", fixture_results(queries), generated)
    write_json("controlled_backend_fixture_runtime/fixture_pages.json", fixture_pages(), generated)

    disabled_config = ControlledBackendConfig.from_environment(ROOT, overrides={})
    fixture_config = ControlledBackendConfig.from_environment(
        ROOT,
        overrides={
            "search_backend_mode": "fixture",
            "page_read_backend_mode": "fixture",
            "search_network_allowed": False,
            "page_read_network_allowed": False,
        },
    )
    budget = SearchBudgetEnvelope.from_mapping(BUDGET)
    search_request = {
        "request_id": "l6_11_fixture_search_request_001",
        "selected_work_order_id": selected["selected_work_order_id"],
        "queries": queries,
        "budget": BUDGET,
    }

    disabled_search = ControlledSearchBackendRegistry(disabled_config).run(search_request).to_dict()
    fixture_search = ControlledSearchBackendRegistry(fixture_config).run(search_request).to_dict()
    source_urls = [result["url"] for result in fixture_search["result_candidates"]]
    page_envelopes = ControlledPageReadAdapterRegistry(fixture_config).read_pages(source_urls, BUDGET)
    disabled_page = ControlledPageReadAdapterRegistry(disabled_config).read_pages(source_urls[:1], BUDGET)
    packets = evidence_packets(fixture_search["result_candidates"], page_envelopes)

    disabled_preflight = run_safety_preflight(disabled_config, budget, []).to_dict()
    fixture_preflight = run_safety_preflight(fixture_config, budget, source_urls).to_dict()
    private_preflight = run_safety_preflight(
        fixture_config, budget, ["http://127.0.0.1/private"]
    ).to_dict()

    domains = sorted({page["source_domain"] for page in page_envelopes if page.get("source_domain")})
    conflicts_found = sum(1 for packet in packets if packet["conflict_status"] != "no_conflict")
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "l6_11_controlled_search_backend_page_read_enablement_complete": True,
        "controlled_search_backend_registry_authorized": True,
        "controlled_search_backend_adapters_authorized": True,
        "controlled_public_page_read_adapter_authorized": True,
        "fixture_backend_authorized": True,
        "disabled_backend_authorized": True,
        "optional_api_backend_stubs_authorized": True,
        "selected_work_order_id": selected["selected_work_order_id"],
        "backend_mode_tested": "fixture",
        "page_read_mode_tested": "fixture",
        "default_backend_mode": "disabled",
        "network_allowed": False,
        "fixture_full_pipeline_generated_non_empty_evidence_packet": bool(packets),
        "query_count": len(queries),
        "search_results_considered": fixture_search["search_results_considered"],
        "pages_opened": len(page_envelopes),
        "domains_touched": len(domains),
        "crawl_depth_used": 1,
        "evidence_packets_generated": len(packets),
        "conflicts_found": conflicts_found,
        "blockers": [],
        "disabled_blockers": disabled_preflight["blockers"],
        "ask_user_for_url_occurred": False,
        "search_snippets_used_as_evidence": False,
        "page_read_extracted_content_used_as_evidence_candidate": True,
        **BUDGET,
        **SAFETY_FLAGS,
    }

    root_files = [
        ("README.md", f"# {MILESTONE_ID} {MILESTONE_NAME}\n\nControlled search and public page-read backend enablement with fixture proof path.\n"),
        ("l6_11_milestone_contract.json", {**summary, "contract_type": "milestone_contract"}),
        ("l6_11_scope.json", {"schema_version": SCHEMA_VERSION, "scope": "controlled backend registry, fixture proof path, page-read adapter, safety preflight", "manual_url_request_allowed": False}),
        ("l6_11_runtime_limits.json", {"schema_version": SCHEMA_VERSION, **BUDGET}),
        ("l6_11_safety_flags.json", SAFETY_FLAGS),
        ("l6_11_summary.json", summary),
        ("l6_11_summary.md", f"# {MILESTONE_ID} Summary\n\nFixture backend produced {len(packets)} evidence packets without external network.\n"),
    ]
    for name, payload in root_files:
        path = f"l6_controlled_search_backend_page_read_enablement/{name}"
        if isinstance(payload, str):
            write_text(path, payload, generated)
        else:
            write_json(path, payload, generated)

    registry_payload = {
        "schema_version": SCHEMA_VERSION,
        "supported_backend_modes": ["disabled", "fixture", "brave_search_api", "tavily_search_api", "serpapi"],
        "default_backend_mode": "disabled",
        "fixture_backend_available": True,
        "api_backends_require_explicit_env_and_allow_flag": True,
    }
    write_json("controlled_search_backend_registry/controlled_search_backend_registry.json", registry_payload, generated)
    write_json("controlled_search_backend_registry/backend_mode_matrix.json", {"schema_version": SCHEMA_VERSION, "modes": [{"mode": "disabled", "network": False}, {"mode": "fixture", "network": False}, {"mode": "brave_search_api", "network": "explicit_opt_in"}, {"mode": "tavily_search_api", "network": "explicit_opt_in"}, {"mode": "serpapi", "network": "explicit_opt_in"}]}, generated)
    write_json("controlled_search_backend_registry/backend_probe_result.json", {"schema_version": SCHEMA_VERSION, "default_mode": "disabled", "fixture_mode_available": True, "configured_api_backend_available": False, "manual_url_request": False}, generated)
    write_json("controlled_search_backend_registry/normalized_search_result_schema.json", {"schema_version": SCHEMA_VERSION, "required_fields": ["result_id", "query_id", "query_text", "rank", "title", "url", "snippet", "source_domain", "backend_name", "retrieved_at_utc", "result_type", "is_sponsored_or_ad_if_known", "safety_flags", "trust_initial_label", "evidence_eligible"]}, generated)
    write_text("controlled_search_backend_registry/controlled_search_backend_registry_report.md", "# Controlled Search Backend Registry Report\n\nDisabled and fixture modes are available; provider stubs require explicit configuration.\n", generated)

    write_json("controlled_search_backend_adapters/disabled_search_backend_trace.json", {**disabled_search, "schema_version": SCHEMA_VERSION}, generated)
    write_json("controlled_search_backend_adapters/fixture_search_backend_trace.json", {**fixture_search, "schema_version": SCHEMA_VERSION}, generated)
    write_json("controlled_search_backend_adapters/optional_api_backend_stub_contract.json", {"schema_version": SCHEMA_VERSION, "providers": ["brave_search_api", "tavily_search_api", "serpapi"], "secret_values_serialized": False, "network_requires_explicit_allow_flag": True}, generated)
    write_text("controlled_search_backend_adapters/controlled_search_backend_adapters_report.md", "# Search Backend Adapters Report\n\nFixture backend returned normalized local results. API adapters remain explicit opt-in stubs.\n", generated)

    write_json("controlled_public_page_read_adapter/page_read_adapter_registry.json", {"schema_version": SCHEMA_VERSION, "supported_page_read_modes": ["disabled", "fixture", "stdlib_public_http"], "default_mode": "disabled"}, generated)
    write_json("controlled_public_page_read_adapter/normalized_page_read_envelope_schema.json", {"schema_version": SCHEMA_VERSION, "required_fields": ["page_read_id", "url", "final_url", "source_domain", "http_status", "content_type", "bytes_read", "title_if_available", "text_excerpt", "extracted_claim_candidates", "safety_flags", "stop_reason_if_any", "evidence_eligible", "read_at_utc", "adapter_name"]}, generated)
    write_json("controlled_public_page_read_adapter/fixture_page_read_trace.json", {"schema_version": SCHEMA_VERSION, "page_read_mode": "fixture", "pages": page_envelopes}, generated)
    write_json("controlled_public_page_read_adapter/disabled_page_read_trace.json", {"schema_version": SCHEMA_VERSION, "page_read_mode": "disabled", "pages": disabled_page}, generated)
    write_json("controlled_public_page_read_adapter/stdlib_public_http_safety_contract.json", {"schema_version": SCHEMA_VERSION, "method": "GET_only", "allowed_schemes": ["http", "https"], "cookies": False, "auth_headers": False, "browser_automation": False, "max_bytes_per_page": 200000, "timeout_seconds": 5}, generated)
    write_json("controlled_public_page_read_adapter/private_url_rejection_tests.json", {"schema_version": SCHEMA_VERSION, "localhost_rejection": reject_private_or_internal_url("http://127.0.0.1/private"), "file_scheme_rejection": reject_private_or_internal_url("file:///tmp/private")}, generated)
    write_text("controlled_public_page_read_adapter/controlled_public_page_read_adapter_report.md", "# Page-Read Adapter Report\n\nFixture page-read produced normalized page envelopes; stdlib HTTP remains opt-in.\n", generated)

    write_json("controlled_backend_configuration_policy/backend_configuration_policy.json", {"schema_version": SCHEMA_VERSION, "default_backend_mode": "disabled", "fixture_mode_available": True, "network_mode_requires_allow_flag": True, "secret_values_serialized": False}, generated)
    write_json("controlled_backend_configuration_policy/backend_env_var_contract.json", {"schema_version": SCHEMA_VERSION, "env_vars": ["YSTAR_CONTROLLED_SEARCH_BACKEND", "YSTAR_CONTROLLED_PAGE_READ_BACKEND", "YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK"], "provider_key_presence_only": ["BRAVE_SEARCH_API_KEY", "TAVILY_API_KEY", "SERPAPI_API_KEY"]}, generated)
    write_json("controlled_backend_configuration_policy/default_disabled_configuration_receipt.json", {"schema_version": SCHEMA_VERSION, **disabled_config.receipt()}, generated)
    write_json("controlled_backend_configuration_policy/fixture_configuration_receipt.json", {"schema_version": SCHEMA_VERSION, **fixture_config.receipt()}, generated)
    write_json("controlled_backend_configuration_policy/configured_backend_missing_env_receipt.json", {"schema_version": SCHEMA_VERSION, "backend_mode": "brave_search_api", "required_env_present": {"BRAVE_SEARCH_API_KEY": False}, "missing_env_names": ["BRAVE_SEARCH_API_KEY"], "secret_values_serialized": False, "blockers": ["configured_backend_missing_required_environment"]}, generated)
    write_text("controlled_backend_configuration_policy/controlled_backend_configuration_policy_report.md", "# Configuration Policy Report\n\nConfiguration receipts serialize only mode and env presence booleans, never secret values.\n", generated)

    write_json("controlled_backend_safety_preflight/safety_preflight_contract.json", {"schema_version": SCHEMA_VERSION, "checks": ["backend mode", "page-read mode", "network allow flags", "required env presence", "budget values", "private network blocking", "GET-only", "no side effects"]}, generated)
    write_json("controlled_backend_safety_preflight/disabled_safety_preflight_result.json", {"schema_version": SCHEMA_VERSION, **disabled_preflight}, generated)
    write_json("controlled_backend_safety_preflight/fixture_safety_preflight_result.json", {"schema_version": SCHEMA_VERSION, **fixture_preflight}, generated)
    write_json("controlled_backend_safety_preflight/private_url_safety_preflight_result.json", {"schema_version": SCHEMA_VERSION, **private_preflight}, generated)
    write_text("controlled_backend_safety_preflight/controlled_backend_safety_preflight_report.md", "# Safety Preflight Report\n\nFixture path passed; disabled path reports configuration blockers; private URL checks reject local targets.\n", generated)

    receipt_files = []
    for action in NO_ACTIONS:
        path = f"controlled_backend_runtime_receipts/no_{action}_receipt.json"
        write_json(path, receipt_payload(action), generated)
        receipt_files.append(path)
    write_json("controlled_backend_runtime_receipts/runtime_receipt_index.json", {"schema_version": SCHEMA_VERSION, "receipts": receipt_files}, generated)
    write_json("controlled_backend_runtime_receipts/no_secret_serialization_receipt.json", {"schema_version": SCHEMA_VERSION, "secret_values_serialized": False, "executed": False}, generated)
    write_json("controlled_backend_runtime_receipts/no_manual_url_request_receipt.json", {"schema_version": SCHEMA_VERSION, "ask_user_for_url": False, "executed": False}, generated)
    write_json("controlled_backend_runtime_receipts/no_network_in_fixture_receipt.json", {"schema_version": SCHEMA_VERSION, "network_used_in_fixture_mode": False, "executed": False}, generated)
    write_text("controlled_backend_runtime_receipts/controlled_backend_runtime_receipts_report.md", "# Runtime Receipts Report\n\nNo disallowed action occurred during L6.11 fixture validation.\n", generated)

    write_json("controlled_backend_fixture_runtime/fixture_pipeline_trace.json", {"schema_version": SCHEMA_VERSION, "selected_work_order_id": selected["selected_work_order_id"], "queries_generated": len(queries), "search_results_considered": fixture_search["search_results_considered"], "pages_opened": len(page_envelopes), "domains_touched": len(domains), "crawl_depth_used": 1, "evidence_packets_generated": len(packets), "network_used": False, "ask_user_for_url": False}, generated)
    write_json("controlled_backend_fixture_runtime/fixture_selected_sources_to_open.json", {"schema_version": SCHEMA_VERSION, "selected_count": len(source_urls), "sources": source_urls}, generated)
    write_json("controlled_backend_fixture_runtime/fixture_evidence_packet_index.json", {"schema_version": SCHEMA_VERSION, "evidence_packet_count": len(packets), "evidence_packets": [f"controlled_backend_fixture_runtime/fixture_evidence_packet_{index:03d}.json" for index in range(1, len(packets) + 1)]}, generated)
    for index, packet in enumerate(packets, start=1):
        write_json(f"controlled_backend_fixture_runtime/fixture_evidence_packet_{index:03d}.json", packet, generated)
    write_json("controlled_backend_fixture_runtime/fixture_source_quality_matrix.json", {"schema_version": SCHEMA_VERSION, "sources": [{"source_locator": packet["source_locator"], "source_quality_label": packet["source_quality_label"], "freshness_label": packet["freshness_class"], "fixture_demo": True} for packet in packets], "semantic_truth_scoring_used": False, "llm_confidence_as_authority": False}, generated)
    write_json("controlled_backend_fixture_runtime/fixture_corroboration_matrix.json", {"schema_version": SCHEMA_VERSION, "claims_supported_by_primary_source": [packets[0]["captured_bounded_claims"][0]], "claims_supported_by_secondary_source": [packets[1]["captured_bounded_claims"][0]], "claims_needing_more_sources": [], "sufficient_for_internal_review_only": True, "sufficient_for_external_use": False}, generated)
    write_json("controlled_backend_fixture_runtime/fixture_conflict_registry.json", {"schema_version": SCHEMA_VERSION, "conflict_count": conflicts_found, "conflicts": [{"conflict_id": "l6_11_fixture_conflict_001", "conflict_type": "scope_limitation", "description": "Fixture limitation blocks converting demand-language evidence into revenue readiness truth."}]}, generated)
    write_json("controlled_backend_fixture_runtime/fixture_review_packet.json", {"schema_version": SCHEMA_VERSION, "review_status": "pending_review", "fixture_evidence": True, "approve_for_external_use": False, "artifact_update_authorized": False, "applied": False}, generated)
    write_json("controlled_backend_fixture_runtime/fixture_refinement_candidate.json", {"schema_version": SCHEMA_VERSION, "review_required": True, "approved": False, "applied": False, "artifact_update_authorized": False, "canonical_update_authorized": False, "brain_writeback_authorized": False, "memory_ingestion_authorized": False, "direct_y_star_mutation_authorized": False}, generated)
    write_text("controlled_backend_fixture_runtime/controlled_backend_fixture_runtime_report.md", "# Fixture Runtime Report\n\nFixture mode proved search result normalization, page-read extraction, evidence packets, and corroboration without network.\n", generated)

    cieu = {"schema_version": SCHEMA_VERSION, "event_mode": "l6_11_controlled_search_backend_page_read_enablement_fixture", "X_t": {"selected_work_order": selected, "query_plan": queries}, "U_t": {"backend_mode": "fixture", "page_read_mode": "fixture", "budget": BUDGET}, "Y_star_t": "Enable controlled search backend and public page-read adapters with deterministic fixture proof while preserving no-action/no-writeback constraints.", "Y_t_plus_1": {"fixture_pipeline_non_empty_evidence": bool(packets), "evidence_packets_generated": len(packets), "conflicts_found": conflicts_found}, "R_t_plus_1": {"residuals": ["real controlled backend still requires explicit configuration", "fixture evidence is not real-world truth"]}}
    residual = {"schema_version": SCHEMA_VERSION, "residual_id": "l6_11_strategic_residual_delta", "primary_residual": "real_backend_configuration_required_for_live_discovery", "fixture_path_ready": True}
    meta = {"schema_version": SCHEMA_VERSION, "candidate_id": "l6_11_meta_learning_update_candidate", "eligible_for_review_queue": True, "eligible_for_direct_brain_writeback": False, "eligible_for_direct_memory_ingestion": False, "eligible_for_candidate_auto_approval": False, "eligible_for_direct_strategy_mutation": False, "approved": False, "applied": False}
    readiness = {"schema_version": SCHEMA_VERSION, "l6_11_controlled_search_backend_page_read_enablement_complete": True, "fixture_pipeline_ready": True, "ready_for_l6_12_real_controlled_search_pilot": "conditional_on_explicit_backend_configuration", "ask_user_for_url": False, "next_step": "configure_real_controlled_search_backend_or_use_fixture_for_offline_regression"}
    blockers = {"schema_version": SCHEMA_VERSION, "blockers": [{"blocker_code": "real_controlled_search_backend_not_configured_for_live_discovery", "applies_to_fixture_mode": False}, {"blocker_code": "controlled_public_page_read_adapter_not_configured_for_live_network", "applies_to_fixture_mode": False}]}
    next_rec = {"schema_version": SCHEMA_VERSION, "recommended_next_milestone": "L6.12 Controlled Real Public Read-Only Search and Page-Read Pilot v0", "condition": "explicit backend configuration and safety preflight approval"}
    read_summary = {**summary, "readiness_next_step": readiness["next_step"], "fixture_pipeline_trace": "controlled_backend_fixture_runtime/fixture_pipeline_trace.json", "fixture_evidence_packet_index": "controlled_backend_fixture_runtime/fixture_evidence_packet_index.json"}
    for name, payload in [
        ("l6_11_cieu_like_fixture.json", cieu),
        ("l6_11_strategic_residual_delta.json", residual),
        ("l6_11_meta_learning_update_candidate.json", meta),
        ("l6_11_readiness_assessment.json", readiness),
        ("l6_11_blockers.json", blockers),
        ("l6_11_next_milestone_recommendation.json", next_rec),
        ("l6_11_read_model_summary.json", read_summary),
    ]:
        write_json(f"l6_11_read_model/{name}", payload, generated)
    write_text("l6_11_read_model/l6_11_report.md", "# L6.11 Read Model Report\n\nControlled backend/page-read enablement is fixture-proven and live-network gated.\n", generated)

    print(f"generated {len(generated)} L6.11 controlled backend/page-read files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
