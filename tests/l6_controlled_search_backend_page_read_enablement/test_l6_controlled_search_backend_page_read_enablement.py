from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_controlled_search_backend_page_read_enablement",
    "controlled_search_backend_registry",
    "controlled_search_backend_adapters",
    "controlled_public_page_read_adapter",
    "controlled_backend_configuration_policy",
    "controlled_backend_safety_preflight",
    "controlled_backend_runtime_receipts",
    "controlled_backend_fixture_runtime",
    "l6_11_read_model",
]

REQUIRED_JSON = [
    "l6_controlled_search_backend_page_read_enablement/l6_11_milestone_contract.json",
    "l6_controlled_search_backend_page_read_enablement/l6_11_scope.json",
    "l6_controlled_search_backend_page_read_enablement/l6_11_runtime_limits.json",
    "l6_controlled_search_backend_page_read_enablement/l6_11_safety_flags.json",
    "l6_controlled_search_backend_page_read_enablement/l6_11_summary.json",
    "controlled_search_backend_registry/controlled_search_backend_registry.json",
    "controlled_search_backend_registry/normalized_search_result_schema.json",
    "controlled_search_backend_registry/backend_probe_result.json",
    "controlled_search_backend_adapters/disabled_search_backend_trace.json",
    "controlled_search_backend_adapters/fixture_search_backend_trace.json",
    "controlled_public_page_read_adapter/page_read_adapter_registry.json",
    "controlled_public_page_read_adapter/normalized_page_read_envelope_schema.json",
    "controlled_public_page_read_adapter/fixture_page_read_trace.json",
    "controlled_backend_configuration_policy/default_disabled_configuration_receipt.json",
    "controlled_backend_configuration_policy/fixture_configuration_receipt.json",
    "controlled_backend_safety_preflight/disabled_safety_preflight_result.json",
    "controlled_backend_safety_preflight/fixture_safety_preflight_result.json",
    "controlled_backend_safety_preflight/private_url_safety_preflight_result.json",
    "controlled_backend_fixture_runtime/fixture_search_results.json",
    "controlled_backend_fixture_runtime/fixture_pages.json",
    "controlled_backend_fixture_runtime/fixture_pipeline_trace.json",
    "controlled_backend_fixture_runtime/fixture_evidence_packet_index.json",
    "controlled_backend_fixture_runtime/fixture_evidence_packet_001.json",
    "controlled_backend_fixture_runtime/fixture_corroboration_matrix.json",
    "controlled_backend_fixture_runtime/fixture_conflict_registry.json",
    "controlled_backend_fixture_runtime/fixture_review_packet.json",
    "controlled_backend_fixture_runtime/fixture_refinement_candidate.json",
    "controlled_backend_runtime_receipts/runtime_receipt_index.json",
    "l6_11_read_model/l6_11_cieu_like_fixture.json",
    "l6_11_read_model/l6_11_meta_learning_update_candidate.json",
    "l6_11_read_model/l6_11_readiness_assessment.json",
    "l6_11_read_model/l6_11_read_model_summary.json",
    "console_read_model/generated/l6_11_controlled_backend_page_read_enablement_summary.json",
]

FORBIDDEN_FIELDS = [
    "login_authorized",
    "account_creation_authorized",
    "payment_authorized",
    "form_submission_authorized",
    "contact_authorized",
    "posting_commenting_messaging_authorized",
    "publication_authorized",
    "outreach_authorized",
    "revenue_execution_authorized",
    "mcp_execution_authorized",
    "live_behavior_authorized",
    "cieu_db_write_authorized",
    "canonical_update_authorized",
    "direct_y_star_mutation_authorized",
    "brain_writeback_authorized",
    "memory_ingestion_authorized",
    "artifact_refinement_application_authorized",
]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_l6_11_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_11_and_boundaries() -> None:
    contract = load(
        "l6_controlled_search_backend_page_read_enablement/l6_11_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.11"
    assert contract["input_milestones"][-1] == "L6.10X"
    assert contract["mode"] == "controlled_search_backend_page_read_adapter_enablement"
    assert contract["controlled_search_backend_registry_authorized"] is True
    assert contract["controlled_public_page_read_adapter_authorized"] is True
    assert contract["fixture_backend_authorized"] is True
    assert contract["ask_user_for_url_authorized"] is False
    assert contract["user_manual_url_provision_required"] is False
    for field in FORBIDDEN_FIELDS:
        assert contract[field] is False, field


def test_disabled_backend_produces_configure_blocker_not_url_request() -> None:
    backends = load_module(
        "controlled_search_backends_l6_11",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(
        ROOT,
        overrides={"search_backend_mode": "disabled", "page_read_backend_mode": "disabled"},
    )
    result = backends.ControlledSearchBackendRegistry(config).run(
        {
            "request_id": "disabled_test",
            "selected_work_order_id": "l6_10x_selected_work_order_001",
            "queries": [{"query_id": "q1", "query_text": "fixture locator", "query_category": "primary_source_query"}],
            "budget": {"max_queries": 5, "max_search_results_considered": 20},
        }
    )
    payload = result.to_dict()
    assert payload["backend_mode"] == "disabled"
    assert payload["search_executed"] is False
    assert payload["error_code"] == "controlled_search_backend_not_configured"
    assert payload["asked_user_for_url"] is False


def test_fixture_backend_returns_normalized_results() -> None:
    backends = load_module(
        "controlled_search_backends_l6_11_fixture",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(
        ROOT,
        overrides={"search_backend_mode": "fixture", "page_read_backend_mode": "fixture"},
    )
    result = backends.ControlledSearchBackendRegistry(config).run(
        {
            "request_id": "fixture_test",
            "selected_work_order_id": "l6_10x_selected_work_order_001",
            "queries": [
                {"query_id": "l6_10x_query_001", "query_text": "official fixture", "query_category": "official_source_query"},
                {"query_id": "l6_10x_query_003", "query_text": "corroboration fixture", "query_category": "corroboration_query"},
            ],
            "budget": {"max_queries": 5, "max_search_results_considered": 20},
        }
    ).to_dict()
    assert result["backend_mode"] == "fixture"
    assert result["network_used"] is False
    assert result["search_executed"] is True
    assert result["search_results_considered"] >= 2
    for candidate in result["result_candidates"]:
        for field in [
            "result_id",
            "query_id",
            "query_text",
            "rank",
            "title",
            "url",
            "snippet",
            "source_domain",
            "backend_name",
            "retrieved_at_utc",
            "result_type",
            "safety_flags",
            "trust_initial_label",
            "evidence_eligible",
        ]:
            assert field in candidate
    assert result["snippets_used_as_evidence"] is False
    assert result["facts_inferred_from_snippets"] is False


def test_fixture_page_read_returns_normalized_page_envelopes() -> None:
    backends = load_module(
        "controlled_search_backends_l6_11_page",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    page_read = load_module(
        "page_read_adapter_l6_11",
        "controlled_public_page_read_adapter/page_read_adapter.py",
    )
    config = backends.ControlledBackendConfig.from_environment(
        ROOT,
        overrides={"search_backend_mode": "fixture", "page_read_backend_mode": "fixture"},
    )
    pages = page_read.ControlledPageReadAdapterRegistry(config).read_pages(
        ["https://official.example.org/fixture/program-demand"],
        {"max_pages_opened": 8, "max_domains": 5, "max_pages_per_domain": 3},
    )
    assert len(pages) == 1
    envelope = pages[0]
    assert envelope["adapter_name"] == "fixture"
    assert envelope["evidence_eligible"] is True
    assert envelope["safety_flags"]["network_used"] is False
    assert envelope["text_excerpt"]
    assert envelope["extracted_claim_candidates"]


def test_fixture_full_pipeline_generates_non_empty_evidence_packet() -> None:
    summary = load("l6_controlled_search_backend_page_read_enablement/l6_11_summary.json")
    pipeline = load("controlled_backend_fixture_runtime/fixture_pipeline_trace.json")
    index = load("controlled_backend_fixture_runtime/fixture_evidence_packet_index.json")
    packet = load("controlled_backend_fixture_runtime/fixture_evidence_packet_001.json")
    assert summary["fixture_full_pipeline_generated_non_empty_evidence_packet"] is True
    assert pipeline["network_used"] is False
    assert index["evidence_packet_count"] == 3
    assert packet["fixture_demo_evidence"] is True
    assert packet["locator_snippet"]
    assert packet["snippet_used_as_evidence"] is False
    assert packet["page_read_extracted_evidence"]
    assert packet["captured_bounded_claims"]
    assert packet["review_status"] == "pending_review"


def test_budget_enforcement_and_safety_preflight() -> None:
    summary = load("l6_controlled_search_backend_page_read_enablement/l6_11_summary.json")
    expected_limits = {
        "max_queries": 5,
        "max_search_results_considered": 20,
        "max_pages_opened": 8,
        "max_domains": 5,
        "max_pages_per_domain": 3,
        "max_crawl_depth": 1,
        "max_total_external_reads": 12,
        "max_evidence_packets": 8,
    }
    for field, limit in expected_limits.items():
        assert summary[field] == limit
    assert summary["query_count"] <= summary["max_queries"]
    assert summary["search_results_considered"] <= summary["max_search_results_considered"]
    assert summary["pages_opened"] <= summary["max_pages_opened"]
    assert summary["domains_touched"] <= summary["max_domains"]
    assert summary["crawl_depth_used"] <= summary["max_crawl_depth"]
    assert summary["evidence_packets_generated"] <= summary["max_evidence_packets"]

    disabled = load("controlled_backend_safety_preflight/disabled_safety_preflight_result.json")
    fixture = load("controlled_backend_safety_preflight/fixture_safety_preflight_result.json")
    assert "controlled_search_backend_not_configured" in disabled["blockers"]
    assert "controlled_public_page_read_adapter_not_configured" in disabled["blockers"]
    assert fixture["decision"] == "pass"
    assert fixture["backend_mode"] == "fixture"
    assert fixture["page_read_mode"] == "fixture"


def test_private_local_internal_urls_are_rejected() -> None:
    page_read = load_module(
        "page_read_adapter_l6_11_private",
        "controlled_public_page_read_adapter/page_read_adapter.py",
    )
    for url in [
        "http://localhost/private",
        "http://127.0.0.1/private",
        "http://10.0.0.1/private",
        "file:///tmp/private",
    ]:
        assert page_read.reject_private_or_internal_url(url) is not None
    preflight = load("controlled_backend_safety_preflight/private_url_safety_preflight_result.json")
    assert preflight["decision"] == "blocked"


def test_no_action_receipts_and_review_only_refinement() -> None:
    index = load("controlled_backend_runtime_receipts/runtime_receipt_index.json")
    for receipt_path in index["receipts"]:
        receipt = load(receipt_path)
        assert receipt["executed"] is False, receipt_path
    candidate = load("controlled_backend_fixture_runtime/fixture_refinement_candidate.json")
    assert candidate["review_required"] is True
    assert candidate["approved"] is False
    assert candidate["applied"] is False
    assert candidate["artifact_update_authorized"] is False
    assert candidate["canonical_update_authorized"] is False
    assert candidate["brain_writeback_authorized"] is False
    assert candidate["memory_ingestion_authorized"] is False
    assert candidate["direct_y_star_mutation_authorized"] is False


def test_read_model_summary_and_console_command_work() -> None:
    summary = load("console_read_model/generated/l6_11_controlled_backend_page_read_enablement_summary.json")
    assert summary["backend_mode_tested"] == "fixture"
    assert summary["page_read_mode_tested"] == "fixture"
    assert summary["ask_user_for_url_occurred"] is False
    assert summary["real_network_use_requires_explicit_backend_configuration"] is True
    assert summary["manual_url_request_replaced_by_backend_configuration"] is True
    assert summary["fixture_full_pipeline_generated_non_empty_evidence_packet"] is True
    for field in FORBIDDEN_FIELDS:
        assert summary[field] is False, field

    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "controlled-search-backend-page-read-enablement",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.11 Controlled Search Backend" in result.stdout
    assert "ask-user-URL occurred: False" in result.stdout


def test_l6_10x_runtime_can_use_l6_11_fixture_registry() -> None:
    runtime = load_module(
        "controlled_search_runtime_l6_11_integration",
        "controlled_search_backend_runtime/controlled_search_runtime.py",
    )
    request = runtime.ControlledSearchRequest.from_mapping(
        {
            "request_id": "l6_11_integration_test",
            "selected_work_order_id": "l6_10x_selected_work_order_001",
            "queries": [
                {"query_id": "l6_10x_query_001", "query_text": "official fixture", "query_category": "official_source_query", "max_results": 1}
            ],
            "budget": {"max_queries": 5, "max_search_results_considered": 20},
        }
    )
    result = runtime.ControlledSearchRuntime(
        config={
            "l6_11_backend_registry_enabled": True,
            "search_backend_mode": "fixture",
            "page_read_backend_mode": "fixture",
        }
    ).run(request)
    assert result.backend_mode == "fixture"
    assert result.search_executed is True
    assert result.search_results_considered == 1
    assert result.snippets_used_as_evidence is False
    assert result.trace["network_used"] is False
    assert result.trace["asked_user_for_url"] is False
