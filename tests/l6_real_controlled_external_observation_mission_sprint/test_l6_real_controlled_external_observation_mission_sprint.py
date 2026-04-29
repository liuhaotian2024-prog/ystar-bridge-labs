from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_real_controlled_external_observation_mission_sprint",
    "real_backend_activation_kit",
    "real_provider_env_checks",
    "real_page_read_activation",
    "real_observation_orchestrator",
    "real_query_plan",
    "real_search_execution_receipts",
    "real_page_read_receipts",
    "real_bounded_crawl_receipts",
    "real_evidence_packets",
    "real_source_quality_matrix",
    "real_claim_boundary",
    "real_corroboration_conflict_matrix",
    "real_mission_evidence_report",
    "real_review_packet",
    "real_query_refinement_candidates",
    "real_capability_gap_closure",
    "real_no_action_receipts",
    "l6_13_read_model",
]

REQUIRED_JSON = [
    "l6_real_controlled_external_observation_mission_sprint/l6_13_milestone_contract.json",
    "l6_real_controlled_external_observation_mission_sprint/l6_13_summary.json",
    "real_backend_activation_kit/activation_kit_manifest.json",
    "real_provider_env_checks/env_presence_receipt.json",
    "real_observation_orchestrator/real_observation_run_trace.json",
    "real_query_plan/generated_query_plan.json",
    "real_search_execution_receipts/search_execution_trace.json",
    "real_page_read_receipts/page_read_trace.json",
    "real_evidence_packets/evidence_packet_index.json",
    "real_evidence_packets/evidence_packet_001.json",
    "real_source_quality_matrix/source_quality_matrix.json",
    "real_claim_boundary/bounded_claim_registry.json",
    "real_corroboration_conflict_matrix/claim_corroboration_matrix.json",
    "real_mission_evidence_report/mission_evidence_report.json",
    "real_review_packet/review_packet.json",
    "real_query_refinement_candidates/query_refinement_candidate_index.json",
    "real_capability_gap_closure/capability_gap_closure_matrix.json",
    "real_no_action_receipts/no_side_effect_receipt.json",
    "l6_13_read_model/l6_13_readiness_assessment.json",
    "console_read_model/generated/l6_13_real_controlled_external_observation_mission_sprint_summary.json",
]

FORBIDDEN_AUTH_FLAGS = [
    "login_authorized",
    "account_creation_authorized",
    "payment_authorized",
    "checkout_authorized",
    "form_submission_authorized",
    "posting_authorized",
    "commenting_authorized",
    "messaging_authorized",
    "publication_authorized",
    "outreach_authorized",
    "revenue_execution_authorized",
    "mcp_execution_authorized",
    "live_behavior_authorized",
    "cieu_db_write_authorized",
    "canonical_update_authorized",
    "brain_writeback_authorized",
    "memory_ingestion_authorized",
    "direct_y_star_mutation_authorized",
    "artifact_refinement_application_authorized",
]

EVIDENCE_FIELDS = [
    "evidence_packet_id",
    "run_id",
    "real_or_fixture",
    "work_order_id",
    "query_id",
    "source_url",
    "final_url",
    "source_domain",
    "source_type",
    "source_quality_label",
    "freshness_label",
    "page_read_id",
    "extracted_text_excerpt",
    "bounded_claim",
    "claim_scope",
    "support_status",
    "conflict_status",
    "limitations",
    "generated_at_utc",
]

ALLOWED_RUN_CLASSIFICATIONS = {
    "real_controlled_observation_loop_executed",
    "real_backend_activation_blocked_with_complete_activation_kit",
    "preflight_blocked_with_complete_activation_kit",
    "partial_real_search_no_page_read",
    "partial_real_page_read_no_evidence",
    "real_evidence_collected_with_unresolved_conflicts",
    "real_evidence_collected_and_review_ready",
}


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


def test_l6_13_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_13_and_real_mission_budget() -> None:
    contract = load("l6_real_controlled_external_observation_mission_sprint/l6_13_milestone_contract.json")
    assert contract["milestone_id"] == "L6.13"
    assert contract["input_milestones"][-1] == "L6.12"
    assert contract["mode"] == "real_controlled_external_observation_mission_sprint"
    assert contract["selected_work_order_id"] == "l6_10x_selected_work_order_001"
    expected_budget = {
        "max_selected_work_orders": 1,
        "max_queries": 10,
        "max_search_results_considered": 25,
        "max_pages_opened": 10,
        "max_domains": 6,
        "max_pages_per_domain": 3,
        "max_crawl_depth": 1,
        "max_total_external_reads": 15,
        "max_evidence_packets": 10,
    }
    for field, expected in expected_budget.items():
        assert contract[field] == expected
    for field in FORBIDDEN_AUTH_FLAGS:
        assert contract[field] is False, field


def test_activation_kit_generated_when_backend_disabled_and_no_url_request() -> None:
    summary = load("l6_real_controlled_external_observation_mission_sprint/l6_13_summary.json")
    kit = load("real_backend_activation_kit/activation_kit_manifest.json")
    assert summary["run_classification"] in ALLOWED_RUN_CLASSIFICATIONS
    assert summary["activation_kit_generated"] is True
    assert summary["ask_user_for_url_occurred"] is False
    assert kit["manual_url_request_required"] is False
    if summary["run_classification"] == "real_backend_activation_blocked_with_complete_activation_kit":
        assert summary["backend_mode"] == "disabled"
        assert summary["page_read_mode"] == "disabled"
        assert summary["network_allowed"] is False
        assert "YSTAR_CONTROLLED_SEARCH_BACKEND" in kit["missing_configuration_fields"]
        assert "YSTAR_CONTROLLED_PAGE_READ_BACKEND" in kit["missing_configuration_fields"]


def test_fixture_proof_exists_but_is_not_real_evidence() -> None:
    summary = load("l6_real_controlled_external_observation_mission_sprint/l6_13_summary.json")
    index = load("real_evidence_packets/evidence_packet_index.json")
    packet = load("real_evidence_packets/evidence_packet_001.json")
    assert summary["fixture_proof_executed"] is True
    assert summary["fixture_evidence_packets_generated"] == 3
    assert index["fixture_evidence_packet_count"] == 3
    if summary["real_observation_executed"]:
        assert summary["real_evidence_packets_generated"] > 0
        assert index["real_evidence_packet_count"] > 0
    else:
        assert summary["real_evidence_packets_generated"] == 0
        assert packet["real_or_fixture"] == "fixture"
        assert "fixture/demo evidence only" in packet["limitations"]
    assert packet["snippet_used_as_evidence"] is False
    assert packet["search_snippet_is_evidence"] is False
    assert packet["page_read_content_used_as_evidence"] is True


def test_evidence_packets_have_required_fields_and_page_content_claims() -> None:
    packet = load("real_evidence_packets/evidence_packet_001.json")
    for field in EVIDENCE_FIELDS:
        assert field in packet, field
    assert packet["bounded_claim"]
    assert packet["extracted_text_excerpt"]
    assert packet["search_snippet_is_evidence"] is False
    assert packet["page_read_content_used_as_evidence"] is True


def test_real_provider_env_presence_checks_do_not_leak_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_BACKEND", "brave_search_api")
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "1")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "super-secret-value")
    backends = load_module(
        "controlled_search_backends_l6_13_secret_test",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(ROOT)
    receipt = config.receipt()
    serialized = json.dumps(receipt)
    assert receipt["required_env_present"]["BRAVE_SEARCH_API_KEY"] is True
    assert "super-secret-value" not in serialized


def test_missing_provider_key_creates_structured_blocker(monkeypatch) -> None:
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_BACKEND", "brave_search_api")
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "1")
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    backends = load_module(
        "controlled_search_backends_l6_13_missing_key",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(ROOT)
    result = backends.ControlledSearchBackendRegistry(config).run(
        {
            "request_id": "test",
            "selected_work_order_id": "l6_10x_selected_work_order_001",
            "queries": [{"query_id": "q1", "query_text": "example", "query_category": "test"}],
            "budget": {"max_queries": 1, "max_search_results_considered": 1},
        }
    ).to_dict()
    assert result["search_executed"] is False
    assert result["error_code"] == "configured_backend_missing_required_environment"
    assert result["asked_user_for_url"] is False


def test_network_allow_flags_required_before_provider_search(monkeypatch) -> None:
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_BACKEND", "brave_search_api")
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "0")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "present-but-not-used")
    backends = load_module(
        "controlled_search_backends_l6_13_allow_flag",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(ROOT)
    result = backends.ControlledSearchBackendRegistry(config).run(
        {
            "request_id": "test",
            "selected_work_order_id": "l6_10x_selected_work_order_001",
            "queries": [{"query_id": "q1", "query_text": "example", "query_category": "test"}],
            "budget": {"max_queries": 1, "max_search_results_considered": 1},
        }
    ).to_dict()
    assert result["search_executed"] is False
    assert result["error_code"] == "configured_backend_failed_safety_preflight"


def test_tavily_adapter_uses_bearer_auth_without_serializing_key(monkeypatch) -> None:
    backends = load_module(
        "controlled_search_backends_l6_13_tavily_auth",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    captured = {}

    class FakeResponse:
        status = 200

        headers = {"content-type": "application/json"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, _limit):
            return b'{"results": [{"title": "Example", "url": "https://example.com/public", "content": "Locator metadata only."}]}'

    def fake_urlopen(request, timeout):
        captured["headers"] = dict(request.header_items())
        captured["body"] = request.data.decode("utf-8")
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(backends, "urlopen", fake_urlopen)
    query = backends.SearchQueryEnvelope("q1", "example public source", "test", max_results=1)
    results = backends.ApiSearchBackendStub("tavily_search_api")._tavily_query(
        query, "secret-tavily-key", 1
    )
    assert results[0]["url"] == "https://example.com/public"
    assert captured["headers"]["Authorization"] == "Bearer secret-tavily-key"
    assert "secret-tavily-key" not in captured["body"]
    assert "\"api_key\"" not in captured["body"]


def test_private_local_internal_urls_are_rejected() -> None:
    page_adapter = load_module(
        "page_read_adapter_l6_13_private",
        "controlled_public_page_read_adapter/page_read_adapter.py",
    )
    assert page_adapter.reject_private_or_internal_url("http://127.0.0.1/private")
    assert page_adapter.reject_private_or_internal_url("http://localhost/private")
    assert page_adapter.reject_private_or_internal_url("file:///tmp/private")
    assert page_adapter.reject_private_or_internal_url("https://example.com/public") is None


def test_page_read_http_errors_become_blocked_receipts_and_policy_terms_are_not_misclassified(monkeypatch) -> None:
    page_adapter = load_module(
        "page_read_adapter_l6_13_http_error",
        "controlled_public_page_read_adapter/page_read_adapter.py",
    )
    backends = load_module(
        "controlled_search_backends_l6_13_http_error",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )

    def fake_urlopen(request, timeout):
        raise page_adapter.HTTPError(request.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(page_adapter, "urlopen", fake_urlopen)
    config = backends.ControlledBackendConfig.from_environment(
        ROOT,
        overrides={
            "search_backend_mode": "fixture",
            "page_read_backend_mode": "stdlib_public_http",
            "page_read_network_allowed": True,
        },
    )
    pages = page_adapter.StdlibPublicHttpPageReadAdapter().read_pages(
        ["https://example.com/public"], config, backends.SearchBudgetEnvelope(max_pages_opened=1)
    )
    assert pages[0].http_status == 403
    assert pages[0].stop_reason_if_any == "http_error_403"
    assert pages[0].evidence_eligible is False
    assert page_adapter.stop_reason_from_text(
        "This public policy page discusses payment terms and submit deadlines."
    ) is None


def test_page_read_policy_is_get_only_and_blocks_interactions() -> None:
    policy = load("real_page_read_activation/l6_13_public_page_read_policy.json")
    assert policy["method"] == "GET_only"
    assert policy["auth"] is False
    assert policy["cookies"] is False
    assert policy["credentials"] is False
    assert policy["form_submit"] is False
    assert policy["javascript_execution"] is False
    assert policy["browser_automation"] is False
    assert policy["localhost_private_internal_blocked"] is True


def test_source_quality_claim_boundary_and_conflict_matrix_exist() -> None:
    quality = load("real_source_quality_matrix/source_quality_matrix.json")
    claims = load("real_claim_boundary/bounded_claim_registry.json")
    matrix = load("real_corroboration_conflict_matrix/claim_corroboration_matrix.json")
    conflicts = load("real_corroboration_conflict_matrix/conflict_registry.json")
    labels = {source["source_quality_label"] for source in quality["sources"]}
    assert labels
    assert labels <= set(quality["allowed_labels"])
    assert claims["claims"]
    assert matrix["claims"]
    assert conflicts["conflict_count"] == 1
    for source in quality["sources"]:
        assert source["llm_confidence_as_truth_authority"] is False
        assert source["semantic_truth_score_used"] is False
    for claim in claims["claims"]:
        assert claim["external_use_authorized"] is False


def test_mission_report_and_capability_gap_closure_are_generated() -> None:
    report = load("real_mission_evidence_report/mission_evidence_report.json")
    gaps = load("real_capability_gap_closure/capability_gap_closure_matrix.json")
    md = (ROOT / "real_mission_evidence_report/mission_evidence_report.md").read_text(encoding="utf-8")
    classification = report["summary"]["run_classification"]
    assert classification in ALLOWED_RUN_CLASSIFICATIONS
    if classification in {
        "real_backend_activation_blocked_with_complete_activation_kit",
        "preflight_blocked_with_complete_activation_kit",
        "partial_real_search_no_page_read",
        "partial_real_page_read_no_evidence",
    }:
        assert "Real external evidence not collected" in md
    statuses = {gap["l6_13_status"] for gap in gaps["gaps"]}
    assert "resolved_in_l6_13" in statuses
    if classification in {
        "real_backend_activation_blocked_with_complete_activation_kit",
        "preflight_blocked_with_complete_activation_kit",
    }:
        assert "still_blocking_real_observation" in statuses
        assert any(gap["still_blocks_real_observation"] for gap in gaps["gaps"])


def test_query_refinement_candidates_and_review_packet_are_generated() -> None:
    refinements = load("real_query_refinement_candidates/query_refinement_candidate_index.json")
    review = load("real_review_packet/review_packet.json")
    assert refinements["candidate_count"] == 3
    assert all(candidate["requires_real_backend"] for candidate in refinements["candidates"])
    assert review["review_status"] == "pending_review"
    assert review["real_observation_executed"] in {False, True}
    assert review["fixture_proof_executed"] is True


def test_no_action_receipt_covers_forbidden_side_effects() -> None:
    receipt = load("real_no_action_receipts/no_side_effect_receipt.json")
    assert receipt["ask_user_for_url_occurred"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False
    actions = {item["action"]: item for item in receipt["actions"]}
    for action in [
        "login",
        "account_creation",
        "payment",
        "form_submission",
        "posting",
        "commenting",
        "messaging",
        "outreach",
        "publication",
        "revenue_execution",
        "mcp_execution",
        "live_behavior",
        "cieu_db_write",
        "brain_memory_writeback",
        "canonical_strategy_mutation",
        "direct_y_star_mutation",
        "y_star_gov_modification",
        "gov_mcp_modification",
        "ask_user_url",
    ]:
        assert actions[action]["executed"] is False
        assert actions[action]["occurred"] is False


def test_read_model_summary_and_console_command_work() -> None:
    summary = load("console_read_model/generated/l6_13_real_controlled_external_observation_mission_sprint_summary.json")
    assert summary["mode"] == "real_controlled_external_observation_mission_sprint"
    assert summary["run_classification"] in summary.get("allowed_run_classifications", []) or summary["run_classification"]
    completed = subprocess.run(
        ["python3", "console_read_model/cli/team_console.py", "real-controlled-external-observation-mission-sprint"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.13 Real Controlled External Observation Mission Sprint" in completed.stdout
    assert "ask-user-URL occurred: False" in completed.stdout


def test_l6_12_integration_remains_intact() -> None:
    l6_12 = load("console_read_model/generated/l6_12_unified_controlled_external_observation_evidence_loop_summary.json")
    assert l6_12["mode"] == "unified_controlled_external_observation_evidence_loop"
    assert l6_12["fixture_proof_executed"] is True
    assert l6_12["ask_user_for_url_occurred"] is False


def test_run_classification_schema_is_deterministic() -> None:
    schema = load("l6_real_controlled_external_observation_mission_sprint/l6_13_run_classification_schema.json")
    decision = load("real_observation_orchestrator/run_classification_decision.json")
    assert decision["run_classification"] in schema["allowed_run_classifications"]
    assert len(schema["allowed_run_classifications"]) == 7
