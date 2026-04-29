from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_real_evidence_conflict_resolution_sprint",
    "real_evidence_report_ingestion",
    "unresolved_claim_analysis",
    "second_pass_query_planning",
    "second_pass_search_execution",
    "second_pass_page_read_receipts",
    "second_pass_evidence_packets",
    "source_quality_update_matrix",
    "claim_boundary_update",
    "corroboration_conflict_update",
    "conflict_resolution_decision_packet",
    "residual_limitation_report",
    "next_action_recommendation_packet",
    "l6_14_no_action_receipts",
    "l6_14_read_model",
]

REQUIRED_JSON = [
    "l6_real_evidence_conflict_resolution_sprint/l6_14_milestone_contract.json",
    "l6_real_evidence_conflict_resolution_sprint/l6_14_summary.json",
    "real_evidence_report_ingestion/prior_mission_evidence_ingestion.json",
    "unresolved_claim_analysis/unresolved_claim_analysis.json",
    "second_pass_query_planning/second_pass_query_plan.json",
    "second_pass_search_execution/second_pass_search_trace.json",
    "second_pass_page_read_receipts/second_pass_page_read_trace.json",
    "second_pass_evidence_packets/second_pass_evidence_packet_index.json",
    "source_quality_update_matrix/source_quality_update_matrix.json",
    "claim_boundary_update/claim_boundary_update_table.json",
    "corroboration_conflict_update/corroboration_conflict_update_matrix.json",
    "conflict_resolution_decision_packet/conflict_resolution_decision_packet.json",
    "residual_limitation_report/residual_limitation_report.json",
    "next_action_recommendation_packet/next_action_recommendation_packet.json",
    "l6_14_no_action_receipts/no_side_effect_receipt.json",
    "l6_14_read_model/l6_14_read_model_summary.json",
    "console_read_model/generated/l6_14_real_evidence_conflict_resolution_sprint_summary.json",
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

ALLOWED_POST_CLASSIFICATIONS = {
    "conflict_resolved",
    "conflict_bounded",
    "still_conflicted_with_reason",
    "insufficient_evidence_after_second_pass",
    "second_pass_blocked_by_backend_or_network",
    "second_pass_blocked_by_budget_or_safety",
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


def test_l6_14_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_14_and_budget_boundaries() -> None:
    contract = load("l6_real_evidence_conflict_resolution_sprint/l6_14_milestone_contract.json")
    assert contract["milestone_id"] == "L6.14"
    assert contract["input_milestones"][-1] == "L6.13"
    assert contract["mode"] == "real_evidence_conflict_resolution_sprint"
    assert contract["selected_work_order_id"] == "l6_10x_selected_work_order_001"
    assert contract["post_second_pass_classification"] in ALLOWED_POST_CLASSIFICATIONS
    expected_limits = {
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
    }
    for field, expected in expected_limits.items():
        assert contract[field] == expected
    for field in FORBIDDEN_AUTH_FLAGS:
        assert contract[field] is False, field


def test_prior_real_report_ingestion_and_unresolved_claim_extraction() -> None:
    ingestion = load("real_evidence_report_ingestion/prior_mission_evidence_ingestion.json")
    analysis = load("unresolved_claim_analysis/unresolved_claim_analysis.json")
    assert ingestion["prior_report_present"] is True
    assert ingestion["prior_run_classification"] == "real_evidence_collected_with_unresolved_conflicts"
    assert ingestion["prior_real_evidence_packet_count"] >= 1
    assert ingestion["prior_conflict_count"] >= 1
    assert analysis["unresolved_claims"]
    assert analysis["conflicting_claims"]
    assert "blocked_page_reads" in analysis


def test_second_pass_queries_are_targeted_to_unresolved_claims() -> None:
    plan = load("second_pass_query_planning/second_pass_query_plan.json")
    assert 1 <= plan["query_count"] <= 8
    assert any(query.get("linked_unresolved_claim_id") for query in plan["queries"])
    assert any(query.get("linked_conflict_id") for query in plan["queries"])
    for query in plan["queries"]:
        assert query["no_snippet_fact_use"] is True
        assert query["no_fact_inference_from_search_result"] is True
        assert query["query_text"]


def test_search_snippets_are_not_evidence_and_page_content_can_be_evidence() -> None:
    search = load("second_pass_search_execution/second_pass_search_trace.json")
    evidence_index = load("second_pass_evidence_packets/second_pass_evidence_packet_index.json")
    assert search["snippets_used_as_evidence"] is False
    assert search["facts_inferred_from_snippets"] is False
    if evidence_index["new_real_evidence_packet_count"]:
        packet = load(evidence_index["packets"][0]["path"])
        assert packet["real_or_fixture"] == "real"
        assert packet["search_snippet_is_evidence"] is False
        assert packet["snippet_used_as_evidence"] is False
        assert packet["page_read_content_used_as_evidence"] is True
        assert packet["bounded_claim"]
        assert packet["linked_unresolved_claim_id"]
        assert packet["linked_conflict_id"]
    else:
        blocked = load("second_pass_evidence_packets/second_pass_blocked_evidence_packet.json")
        assert blocked["live_source_evidence_captured"] is False


def test_budget_limits_are_enforced_in_summary() -> None:
    summary = load("l6_real_evidence_conflict_resolution_sprint/l6_14_summary.json")
    assert summary["second_pass_queries_generated"] <= summary["max_second_pass_queries"]
    assert summary["search_results_considered"] <= summary["max_search_results_considered"]
    assert summary["pages_opened"] <= summary["max_pages_opened"]
    assert summary["domains_touched"] <= summary["max_domains"]
    assert summary["crawl_depth_used"] <= summary["max_crawl_depth"]
    assert summary["external_reads_used"] <= summary["max_total_external_reads"]
    assert summary["new_real_evidence_packets"] <= summary["max_new_real_evidence_packets"]


def test_conflict_decision_and_updated_mission_report_are_generated() -> None:
    decision = load("conflict_resolution_decision_packet/conflict_resolution_decision_packet.json")
    updated = load("real_mission_evidence_report/l6_14_updated_mission_evidence_report.json")
    assert decision["post_second_pass_classification"] in ALLOWED_POST_CLASSIFICATIONS
    assert decision["decisions"]
    assert updated["summary"]["post_second_pass_classification"] == decision["post_second_pass_classification"]
    for item in decision["decisions"]:
        assert item["post_second_pass_status"] in {
            "resolved",
            "bounded_conflict",
            "still_conflicted_with_reason",
            "insufficient_evidence_after_second_pass",
            "blocked_by_source_access",
            "blocked_by_budget",
            "blocked_by_safety",
        }
        assert item["review_required"] is True


def test_source_quality_claim_boundary_and_next_action_exist() -> None:
    quality = load("source_quality_update_matrix/source_quality_update_matrix.json")
    claims = load("claim_boundary_update/claim_boundary_update_table.json")
    next_action = load("next_action_recommendation_packet/next_action_recommendation_packet.json")
    assert quality["sources"]
    assert {item["source_quality_label"] for item in quality["sources"]} <= set(quality["allowed_labels"])
    assert all(item["llm_confidence_as_truth_authority"] is False for item in quality["sources"])
    assert all(item["semantic_truth_score_used"] is False for item in quality["sources"])
    assert claims["claims"]
    assert all(item["external_use_authorized"] is False for item in claims["claims"])
    assert next_action["recommended_next_action"] in {
        "run_third_pass_observation",
        "broaden_source_types",
        "add_domain_policy",
        "add_better_html_extraction",
        "add_pdf_reader",
        "add_screenshot_or_ocr_reader",
        "add_host_mediated_search",
        "ready_for_human_review",
        "ready_for_governed_planning",
        "blocked_pending_backend_or_network",
    }
    assert next_action["requires_external_side_effects"] is False
    assert next_action["requires_core_writeback"] is False


def test_missing_backend_preflight_blocks_without_user_url_request(monkeypatch) -> None:
    builder = load_module(
        "l6_14_builder_preflight_test",
        "l6_real_evidence_conflict_resolution_sprint/tools/build_l6_real_evidence_conflict_resolution_sprint.py",
    )
    backends = load_module(
        "l6_14_backends_preflight_test",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    monkeypatch.delenv("YSTAR_CONTROLLED_SEARCH_BACKEND", raising=False)
    monkeypatch.delenv("YSTAR_CONTROLLED_PAGE_READ_BACKEND", raising=False)
    config = backends.ControlledBackendConfig.from_environment(ROOT)
    result = builder.preflight(config)
    assert result["decision"] == "blocked"
    assert "configured_search_provider_missing_or_not_real" in result["blockers"]
    assert result["ask_user_for_url"] is False


def test_no_action_receipt_and_no_secret_serialization() -> None:
    receipt = load("l6_14_no_action_receipts/no_side_effect_receipt.json")
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
        "email_customer_outreach",
        "publication",
        "social_media_action",
        "revenue_execution",
        "mcp_execution",
        "live_behavior",
        "cieu_db_write",
        "brain_memory_writeback",
        "canonical_strategy_mutation",
        "direct_y_star_mutation",
        "ask_user_url",
    ]:
        assert actions[action]["executed"] is False
        assert actions[action]["occurred"] is False

    for rel in REQUIRED_JSON + ["real_mission_evidence_report/l6_14_updated_mission_evidence_report.json"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert ("tvly" + "-") not in text
        assert ("TAVILY_API_KEY" + "=") not in text


def test_read_model_summary_and_console_command_work() -> None:
    summary = load("console_read_model/generated/l6_14_real_evidence_conflict_resolution_sprint_summary.json")
    assert summary["mode"] == "real_evidence_conflict_resolution_sprint"
    assert summary["post_second_pass_classification"] in ALLOWED_POST_CLASSIFICATIONS
    completed = subprocess.run(
        ["python3", "console_read_model/cli/team_console.py", "real-evidence-conflict-resolution-sprint"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.14 Real Evidence Conflict Resolution Sprint" in completed.stdout
    assert "ask-user-URL occurred: False" in completed.stdout


def test_l6_13_integration_remains_intact() -> None:
    l6_13 = load("console_read_model/generated/l6_13_real_controlled_external_observation_mission_sprint_summary.json")
    assert l6_13["mode"] == "real_controlled_external_observation_mission_sprint"
    assert l6_13["ask_user_for_url_occurred"] is False
    assert l6_13["search_snippets_used_as_evidence"] is False
