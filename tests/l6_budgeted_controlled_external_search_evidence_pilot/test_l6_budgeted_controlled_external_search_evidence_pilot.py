from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_budgeted_controlled_external_search_evidence_pilot",
    "search_budget_policy",
    "agentic_query_planner",
    "controlled_search_backend_runtime",
    "search_result_triage",
    "bounded_crawl_runtime",
    "source_quality_and_trust_assessment",
    "evidence_extraction_and_claim_boundary",
    "evidence_corroboration_and_conflict_matrix",
    "evidence_review_and_refinement_candidates",
    "external_search_no_action_receipts",
    "l6_10x_read_model",
]

REQUIRED_JSON = [
    "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_milestone_contract.json",
    "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_scope.json",
    "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_budget_policy.json",
    "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_safety_flags.json",
    "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_summary.json",
    "search_budget_policy/search_budget_contract.json",
    "search_budget_policy/search_budget_limits.json",
    "search_budget_policy/budget_enforcement_rules.json",
    "search_budget_policy/budget_exhaustion_policy.json",
    "agentic_query_planner/selected_work_order.json",
    "agentic_query_planner/query_planning_contract.json",
    "agentic_query_planner/generated_query_plan.json",
    "agentic_query_planner/query_priority_matrix.json",
    "controlled_search_backend_runtime/controlled_search_backend_registry.json",
    "controlled_search_backend_runtime/controlled_search_config.example.json",
    "controlled_search_backend_runtime/controlled_search_trace.json",
    "search_result_triage/search_result_triage_contract.json",
    "search_result_triage/search_result_candidates.json",
    "search_result_triage/source_triage_matrix.json",
    "search_result_triage/selected_sources_to_open.json",
    "search_result_triage/rejected_search_results.json",
    "bounded_crawl_runtime/bounded_crawl_contract.json",
    "bounded_crawl_runtime/bounded_crawl_trace.json",
    "bounded_crawl_runtime/opened_page_registry.json",
    "bounded_crawl_runtime/crawl_expansion_decisions.json",
    "source_quality_and_trust_assessment/source_quality_contract.json",
    "source_quality_and_trust_assessment/source_quality_matrix.json",
    "source_quality_and_trust_assessment/trust_assessment_results.json",
    "source_quality_and_trust_assessment/source_freshness_assessment.json",
    "evidence_extraction_and_claim_boundary/evidence_extraction_contract.json",
    "evidence_extraction_and_claim_boundary/evidence_packet_schema.json",
    "evidence_extraction_and_claim_boundary/evidence_packet_index.json",
    "evidence_extraction_and_claim_boundary/evidence_packet_001.json",
    "evidence_extraction_and_claim_boundary/bounded_claim_registry.json",
    "evidence_extraction_and_claim_boundary/unsupported_claim_registry.json",
    "evidence_extraction_and_claim_boundary/missing_context_registry.json",
    "evidence_corroboration_and_conflict_matrix/corroboration_contract.json",
    "evidence_corroboration_and_conflict_matrix/source_corroboration_matrix.json",
    "evidence_corroboration_and_conflict_matrix/claim_corroboration_matrix.json",
    "evidence_corroboration_and_conflict_matrix/conflict_registry.json",
    "evidence_corroboration_and_conflict_matrix/evidence_sufficiency_assessment.json",
    "evidence_review_and_refinement_candidates/review_packet_index.json",
    "evidence_review_and_refinement_candidates/evidence_review_packet.json",
    "evidence_review_and_refinement_candidates/artifact_refinement_candidate_index.json",
    "evidence_review_and_refinement_candidates/artifact_refinement_candidate_001.json",
    "l6_10x_read_model/l6_10x_cieu_like_fixture.json",
    "l6_10x_read_model/l6_10x_strategic_residual_delta.json",
    "l6_10x_read_model/l6_10x_meta_learning_update_candidate.json",
    "l6_10x_read_model/l6_10x_readiness_assessment.json",
    "l6_10x_read_model/l6_10x_blockers.json",
    "l6_10x_read_model/l6_10x_next_milestone_recommendation.json",
    "l6_10x_read_model/l6_10x_read_model_summary.json",
    "console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json",
]

FORBIDDEN_FLAGS = [
    "login_authorized",
    "account_creation_authorized",
    "contact_authorized",
    "payment_authorized",
    "form_submission_authorized",
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


def test_l6_10x_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10x_and_budgeted_boundaries() -> None:
    contract = load(
        "l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.10X"
    assert contract["milestone_name"] == (
        "Budgeted Controlled External Search, Bounded Crawl & Evidence Corroboration Pilot v0"
    )
    assert contract["input_milestones"] == [
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
    assert contract["mode"] == "budgeted_controlled_external_search_evidence_pilot"
    assert contract["controlled_external_search_authorized"] is True
    assert contract["bounded_public_page_read_authorized"] is True
    assert contract["bounded_crawl_authorized"] is True
    assert contract["evidence_corroboration_authorized"] is True
    assert contract["ask_user_for_url_authorized"] is False
    assert contract["user_manual_url_provision_required"] is False
    for field in FORBIDDEN_FLAGS:
        assert contract[field] is False, field


def test_search_and_crawl_budget_values_are_present() -> None:
    limits = load("search_budget_policy/search_budget_limits.json")
    summary = load("l6_budgeted_controlled_external_search_evidence_pilot/l6_10x_summary.json")
    expected = {
        "max_selected_work_orders": 1,
        "max_queries": 5,
        "max_search_results_considered": 20,
        "max_pages_opened": 8,
        "max_domains": 5,
        "max_pages_per_domain": 3,
        "max_crawl_depth": 1,
        "max_total_external_reads": 12,
        "max_evidence_packets": 8,
    }
    for key, value in expected.items():
        assert limits[key] == value
        assert summary[key] == value
    assert limits["rate_limit_required"] is True
    assert limits["stop_on_login_or_payment_or_form"] is True
    assert limits["stop_on_private_or_sensitive_data"] is True
    assert limits["stop_on_scope_drift"] is True


def test_query_planner_generates_multiple_query_categories() -> None:
    selected = load("agentic_query_planner/selected_work_order.json")
    plan = load("agentic_query_planner/generated_query_plan.json")
    categories = {query["query_category"] for query in plan["queries"]}
    assert selected["selected_count"] <= 1
    assert plan["query_count"] == 5
    assert categories == {
        "primary_source_query",
        "official_source_query",
        "corroboration_query",
        "conflict_check_query",
        "freshness_check_query",
    }
    for query in plan["queries"]:
        assert query["linked_work_order_id"] == selected["selected_work_order_id"]
        assert query["no_snippet_fact_use"] is True
        assert query["no_fact_inference_from_search_result"] is True


def test_default_backend_path_does_not_search_or_ask_user_for_url(monkeypatch) -> None:
    monkeypatch.delenv("YSTAR_CONTROLLED_SEARCH_ENABLED", raising=False)
    monkeypatch.delenv("YSTAR_CONTROLLED_SEARCH_BACKEND", raising=False)
    module_path = ROOT / "controlled_search_backend_runtime/controlled_search_runtime.py"
    spec = importlib.util.spec_from_file_location("controlled_search_runtime_l6_10x", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    request = module.ControlledSearchRequest.from_mapping(
        {
            "request_id": "test",
            "selected_work_order_id": "l6_10x_selected_work_order_001",
            "queries": [{"query_id": "q1", "query_text": "locator", "query_category": "primary_source_query", "max_results": 1}],
            "budget": {"max_queries": 5, "max_search_results_considered": 20},
        }
    )
    result = module.ControlledSearchRuntime(config={"controlled_search_enabled": True}).run(request)
    assert result.backend_mode == "disabled"
    assert result.search_executed is False
    assert result.search_query_count == 0
    assert result.search_results_considered == 0
    assert result.trace["network_used"] is False
    assert result.trace["manual_url_request"] is False


def test_search_snippets_are_not_evidence_and_triage_crawl_contracts_exist() -> None:
    trace = load("controlled_search_backend_runtime/controlled_search_trace.json")
    triage = load("search_result_triage/source_triage_matrix.json")
    crawl = load("bounded_crawl_runtime/bounded_crawl_contract.json")
    crawl_trace = load("bounded_crawl_runtime/bounded_crawl_trace.json")
    assert trace["search_executed"] is False
    assert trace["snippets_used_as_evidence"] is False
    assert trace["facts_inferred_from_snippets"] is False
    assert trace["trace"]["manual_url_request"] is False
    assert triage["triage_rows"] == []
    assert crawl["max_crawl_depth"] == 1
    assert crawl["no_login"] is True
    assert crawl["no_payment"] is True
    assert crawl["no_forms"] is True
    assert crawl_trace["opened_pages_count"] == 0
    assert crawl_trace["crawl_depth_used"] == 0


def test_source_quality_assessment_is_structural_not_semantic_truth_scoring() -> None:
    contract = load("source_quality_and_trust_assessment/source_quality_contract.json")
    trust = load("source_quality_and_trust_assessment/trust_assessment_results.json")
    assert "semantic_truth_score" not in contract
    assert "truth_score" not in contract
    assert "semantic_truth_score" not in trust
    assert "truth_score" not in trust
    assert contract["prohibited_authorities"] == ["semantic_truth_score", "llm_confidence"]
    assert trust["llm_confidence_as_authority"] is False


def test_evidence_corrob_review_and_refinement_outputs_are_blocked() -> None:
    schema = load("evidence_extraction_and_claim_boundary/evidence_packet_schema.json")
    evidence = load("evidence_extraction_and_claim_boundary/evidence_packet_001.json")
    corroboration = load("evidence_corroboration_and_conflict_matrix/evidence_sufficiency_assessment.json")
    conflicts = load("evidence_corroboration_and_conflict_matrix/conflict_registry.json")
    review = load("evidence_review_and_refinement_candidates/evidence_review_packet.json")
    refinement = load(
        "evidence_review_and_refinement_candidates/artifact_refinement_candidate_001.json"
    )
    assert "source_locator" in schema["required_fields"]
    assert evidence["live_source_evidence_captured"] is False
    assert evidence["captured_bounded_claims"] == []
    assert evidence["publication_taken"] is False
    assert evidence["outreach_taken"] is False
    assert evidence["payment_taken"] is False
    assert evidence["revenue_action_taken"] is False
    assert evidence["mcp_execution_taken"] is False
    assert evidence["canonical_update_taken"] is False
    assert evidence["brain_memory_writeback_taken"] is False
    assert evidence["direct_y_star_mutation_taken"] is False
    assert corroboration["sufficient_for_external_use"] is False
    assert conflicts["conflict_count"] == 0
    assert review["approve_for_external_use"] is False
    assert refinement["review_required"] is True
    assert refinement["approved"] is False
    assert refinement["applied"] is False
    assert refinement["artifact_update_authorized"] is False


def test_no_action_receipts_show_disallowed_actions_false() -> None:
    receipt_files = sorted((ROOT / "external_search_no_action_receipts").glob("no_*_receipt.json"))
    assert receipt_files
    for receipt_file in receipt_files:
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
        assert receipt["authorized"] is False
        assert receipt["executed"] is False


def test_read_model_summary_cieu_meta_learning_and_readiness() -> None:
    cieu = load("l6_10x_read_model/l6_10x_cieu_like_fixture.json")
    meta = load("l6_10x_read_model/l6_10x_meta_learning_update_candidate.json")
    readiness = load("l6_10x_read_model/l6_10x_readiness_assessment.json")
    summary = load("console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json")
    assert cieu["event_mode"] == "l6_10x_budgeted_controlled_external_search_evidence_pilot_fixture"
    assert meta["eligible_for_review_queue"] is True
    assert meta["eligible_for_direct_brain_writeback"] is False
    assert meta["eligible_for_direct_memory_ingestion"] is False
    assert meta["approved"] is False
    assert meta["applied"] is False
    assert readiness["next_step"] == "configure_controlled_search_backend"
    assert readiness["do_not_ask_user_for_manual_url"] is True
    assert summary["backend_missing"] is True
    assert summary["manual_url_request_avoided"] is True


def test_console_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "budgeted-controlled-external-search-evidence-pilot",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.10X Budgeted Controlled External Search Evidence Pilot" in result.stdout
    assert "manual URL request avoided: True" in result.stdout
    assert "backend missing: True" in result.stdout
