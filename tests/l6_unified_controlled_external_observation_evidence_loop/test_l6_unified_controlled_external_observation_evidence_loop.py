from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_unified_controlled_external_observation_evidence_loop",
    "real_backend_activation",
    "real_page_read_activation",
    "controlled_observation_orchestrator",
    "controlled_query_execution",
    "controlled_result_triage",
    "controlled_bounded_crawl",
    "controlled_evidence_packets",
    "controlled_claim_boundary",
    "controlled_source_quality",
    "controlled_corroboration_conflict",
    "controlled_review_packet",
    "controlled_query_refinement",
    "controlled_capability_gap_report",
    "controlled_no_action_receipts",
    "controlled_observation_run_reports",
    "l6_12_read_model",
]

REQUIRED_JSON = [
    "l6_unified_controlled_external_observation_evidence_loop/l6_12_milestone_contract.json",
    "l6_unified_controlled_external_observation_evidence_loop/l6_12_scope.json",
    "l6_unified_controlled_external_observation_evidence_loop/l6_12_budget_policy.json",
    "l6_unified_controlled_external_observation_evidence_loop/l6_12_safety_flags.json",
    "l6_unified_controlled_external_observation_evidence_loop/l6_12_run_classification_schema.json",
    "l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json",
    "real_backend_activation/backend_configuration_receipt.json",
    "real_backend_activation/provider_presence_matrix.json",
    "real_page_read_activation/page_read_configuration_receipt.json",
    "controlled_observation_orchestrator/selected_work_order.json",
    "controlled_observation_orchestrator/observation_loop_run_trace.json",
    "controlled_query_execution/generated_query_plan.json",
    "controlled_query_execution/search_execution_trace.json",
    "controlled_result_triage/source_triage_matrix.json",
    "controlled_bounded_crawl/bounded_crawl_trace.json",
    "controlled_evidence_packets/evidence_packet_schema.json",
    "controlled_evidence_packets/evidence_packet_index.json",
    "controlled_evidence_packets/evidence_packet_001.json",
    "controlled_claim_boundary/bounded_claim_registry.json",
    "controlled_source_quality/source_quality_matrix.json",
    "controlled_corroboration_conflict/claim_corroboration_matrix.json",
    "controlled_corroboration_conflict/conflict_registry.json",
    "controlled_review_packet/evidence_review_packet.json",
    "controlled_query_refinement/query_refinement_candidate_index.json",
    "controlled_capability_gap_report/capability_gap_registry.json",
    "controlled_no_action_receipts/no_side_effect_receipt.json",
    "l6_12_read_model/l6_12_cieu_like_fixture.json",
    "l6_12_read_model/l6_12_meta_learning_update_candidate.json",
    "l6_12_read_model/l6_12_readiness_assessment.json",
    "l6_12_read_model/l6_12_read_model_summary.json",
    "console_read_model/generated/l6_12_unified_controlled_external_observation_evidence_loop_summary.json",
]

FORBIDDEN_FLAGS = [
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


def test_l6_12_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_12_and_budgeted_boundaries() -> None:
    contract = load(
        "l6_unified_controlled_external_observation_evidence_loop/l6_12_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.12"
    assert contract["input_milestones"][-1] == "L6.11"
    assert contract["mode"] == "unified_controlled_external_observation_evidence_loop"
    assert contract["selected_work_order_id"] == "l6_10x_selected_work_order_001"
    assert contract["ask_user_for_url_authorized"] is False
    assert contract["user_manual_url_provision_required"] is False
    for field in FORBIDDEN_FLAGS:
        assert contract[field] is False, field
    expected_budget = {
        "max_selected_work_orders": 1,
        "max_queries": 8,
        "max_search_results_considered": 20,
        "max_pages_opened": 8,
        "max_domains": 5,
        "max_pages_per_domain": 3,
        "max_crawl_depth": 1,
        "max_total_external_reads": 12,
        "max_evidence_packets": 8,
    }
    for field, expected in expected_budget.items():
        assert contract[field] == expected


def test_disabled_backend_is_configuration_blocked_but_engineering_ready() -> None:
    summary = load("l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json")
    trace = load("controlled_observation_orchestrator/observation_loop_run_trace.json")
    assert summary["run_classification"] == "configuration_blocked_but_engineering_ready"
    assert summary["backend_mode"] == "disabled"
    assert summary["page_read_mode"] == "disabled"
    assert summary["network_allowed"] is False
    assert summary["real_observation_executed"] is False
    assert summary["fixture_proof_executed"] is True
    assert summary["ask_user_for_url_occurred"] is False
    assert trace["real_run"]["search_executed"] is False
    assert "controlled_search_backend_not_configured" in summary["blockers"]
    assert "controlled_public_page_read_adapter_not_configured" in summary["blockers"]


def test_fixture_full_loop_produces_non_empty_fixture_evidence() -> None:
    summary = load("l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json")
    index = load("controlled_evidence_packets/evidence_packet_index.json")
    packet = load("controlled_evidence_packets/evidence_packet_001.json")
    assert summary["fixture_evidence_packets_generated"] == 3
    assert summary["real_evidence_packets_generated"] == 0
    assert summary["run_classification"] != "real_controlled_observation_loop_executed"
    assert index["evidence_packet_count"] == 3
    assert packet["real_or_fixture"] == "fixture"
    assert packet["search_snippet_locator"]
    assert packet["snippet_used_as_evidence"] is False
    assert packet["search_snippet_is_evidence"] is False
    assert packet["page_read_content_used_as_evidence"] is True
    assert packet["bounded_claim"]
    assert packet["review_status"] == "pending_review"


def test_real_backend_secret_presence_is_boolean_only(monkeypatch) -> None:
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_BACKEND", "brave_search_api")
    monkeypatch.setenv("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "1")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "super-secret-value")
    backends = load_module(
        "controlled_search_backends_l6_12",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(ROOT)
    receipt = config.receipt()
    serialized = json.dumps(receipt)
    assert receipt["backend_mode"] == "brave_search_api"
    assert receipt["required_env_present"]["BRAVE_SEARCH_API_KEY"] is True
    assert "super-secret-value" not in serialized


def test_unsafe_preflight_blocks_private_internal_url() -> None:
    builder = load_module(
        "l6_12_builder_private_url_test",
        "l6_unified_controlled_external_observation_evidence_loop/tools/build_l6_unified_controlled_external_observation_evidence_loop.py",
    )
    backends = load_module(
        "controlled_search_backends_l6_12_private",
        "controlled_search_backend_adapters/controlled_search_backends.py",
    )
    config = backends.ControlledBackendConfig.from_environment(
        ROOT,
        overrides={"search_backend_mode": "fixture", "page_read_backend_mode": "fixture"},
    )
    budget = backends.SearchBudgetEnvelope(max_queries=8)
    result = builder.l6_12_safety_preflight(config, budget, ["http://127.0.0.1/private"])
    assert result["decision"] == "blocked"
    assert "private_or_internal_url_rejected" in result["blockers"]
    assert result["private_url_rejections"]["http://127.0.0.1/private"]


def test_budget_limits_are_enforced_by_generated_run() -> None:
    summary = load("l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json")
    assert summary["query_count"] <= summary["max_queries"]
    assert summary["search_results_considered"] <= summary["max_search_results_considered"]
    assert summary["pages_opened"] <= summary["max_pages_opened"]
    assert summary["domains_touched"] <= summary["max_domains"]
    assert summary["crawl_depth_used"] <= summary["max_crawl_depth"]
    assert summary["external_reads_used"] <= summary["max_total_external_reads"]
    assert summary["evidence_packets_generated"] <= summary["max_evidence_packets"]


def test_source_quality_labels_are_deterministic_without_truth_scores() -> None:
    matrix = load("controlled_source_quality/source_quality_matrix.json")
    allowed = {
        "official_primary",
        "official_secondary",
        "institutional",
        "documentation",
        "reputable_media",
        "community",
        "commercial_vendor",
        "unknown",
        "blocked_or_ineligible",
    }
    labels = {source["source_quality_label"] for source in matrix["sources"]}
    assert labels
    assert labels <= allowed
    assert "official_primary" in labels
    for source in matrix["sources"]:
        assert source["llm_confidence_as_truth_authority"] is False
        assert source["semantic_truth_score_used"] is False


def test_conflict_matrix_review_packet_refinements_and_gaps_exist() -> None:
    claim_matrix = load("controlled_corroboration_conflict/claim_corroboration_matrix.json")
    review = load("controlled_review_packet/evidence_review_packet.json")
    refinements = load("controlled_query_refinement/query_refinement_candidate_index.json")
    gaps = load("controlled_capability_gap_report/capability_gap_registry.json")
    statuses = {claim["corroboration_status"] for claim in claim_matrix["claims"]}
    assert {"single_source_supported", "corroborated", "conflicted"} <= statuses
    assert review["run_classification"] == "configuration_blocked_but_engineering_ready"
    assert review["real_observation_executed"] is False
    assert review["fixture_proof_executed"] is True
    assert refinements["candidate_count"] == 3
    assert gaps["gap_count"] >= 15
    assert any(gap["gap_name"] == "configured_search_provider" for gap in gaps["gaps"])


def test_no_action_receipts_prove_no_side_effects() -> None:
    index = load("controlled_no_action_receipts/no_action_receipt_index.json")
    summary = load("controlled_no_action_receipts/no_side_effect_receipt.json")
    assert summary["external_side_effects_occurred"] is False
    assert summary["core_writeback_occurred"] is False
    assert summary["ask_user_for_url_occurred"] is False
    for rel in index["receipts"]:
        receipt = load(rel)
        assert receipt["executed"] is False, rel
        assert receipt["occurred"] is False, rel
        assert receipt["authorized"] is False, rel


def test_read_model_summary_and_console_command_work() -> None:
    generated = load(
        "console_read_model/generated/l6_12_unified_controlled_external_observation_evidence_loop_summary.json"
    )
    assert generated["run_classification"] == "configuration_blocked_but_engineering_ready"
    assert generated["fixture_proof_executed"] is True
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "unified-controlled-external-observation-evidence-loop",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.12 Unified Controlled External Observation Evidence Loop" in result.stdout
    assert "ask-user-URL occurred: False" in result.stdout


def test_l6_10x_l6_11_integration_remains_intact() -> None:
    l6_10x = load("console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json")
    l6_11 = load("console_read_model/generated/l6_11_controlled_backend_page_read_enablement_summary.json")
    l6_12 = load("console_read_model/generated/l6_12_unified_controlled_external_observation_evidence_loop_summary.json")
    assert l6_10x["selected_work_order_id"] == l6_12["selected_work_order_id"]
    assert l6_11["fixture_full_pipeline_generated_non_empty_evidence_packet"] is True
    assert l6_12["evidence_packets_generated"] >= l6_11["evidence_packets_generated"]


def test_run_classification_schema_is_deterministic() -> None:
    schema = load(
        "l6_unified_controlled_external_observation_evidence_loop/l6_12_run_classification_schema.json"
    )
    allowed = schema["allowed_run_classifications"]
    assert allowed == [
        "real_controlled_observation_loop_executed",
        "configuration_blocked_but_engineering_ready",
        "preflight_blocked_but_engineering_ready",
        "partial_real_observation_no_evidence",
        "real_pages_read_but_conflict_unresolved",
    ]
    summary = load("l6_unified_controlled_external_observation_evidence_loop/l6_12_summary.json")
    assert summary["run_classification"] in allowed
