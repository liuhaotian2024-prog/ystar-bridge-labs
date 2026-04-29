from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from explicit_controlled_search_resolver.explicit_search_resolver_runtime import (  # noqa: E402
    ExplicitControlledSearchResolver,
    ExplicitSearchResolutionRequest,
)


REQUIRED_DIRS = [
    "l6_controlled_seed_locator_or_search_resolver_enablement",
    "seed_locator_registry",
    "explicit_controlled_search_resolver",
    "locator_resolution_v_attempt",
    "tiny_observation_v_result",
    "l6_10v_read_model",
]

REQUIRED_JSON = [
    "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_milestone_contract.json",
    "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_scope.json",
    "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_runtime_limits.json",
    "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_safety_flags.json",
    "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_summary.json",
    "seed_locator_registry/seed_locator_registry_schema.json",
    "seed_locator_registry/reviewed_seed_locator_registry.json",
    "seed_locator_registry/seed_locator_review_policy.json",
    "seed_locator_registry/seed_locator_registry_lookup_trace.json",
    "explicit_controlled_search_resolver/explicit_search_resolver_contract.json",
    "explicit_controlled_search_resolver/explicit_search_resolver_config.json",
    "explicit_controlled_search_resolver/explicit_search_resolver_trace.json",
    "locator_resolution_v_attempt/selected_work_order.json",
    "locator_resolution_v_attempt/locator_resolution_v_request.json",
    "locator_resolution_v_attempt/locator_resolution_v_result.json",
    "locator_resolution_v_attempt/locator_resolution_v_trace.json",
    "locator_resolution_v_attempt/locator_resolution_v_eligibility_result.json",
    "tiny_observation_v_result/tiny_observation_v_execution_packet.json",
    "tiny_observation_v_result/tiny_observation_v_trace.json",
    "tiny_observation_v_result/tiny_evidence_v_packet.json",
    "tiny_observation_v_result/tiny_claim_boundary_v_assessment.json",
    "tiny_observation_v_result/tiny_post_observation_v_review_packet.json",
    "tiny_observation_v_result/tiny_refinement_v_candidate.json",
    "tiny_observation_v_result/tiny_observation_v_no_action_receipts.json",
    "l6_10v_read_model/l6_10v_cieu_like_fixture.json",
    "l6_10v_read_model/l6_10v_strategic_residual_delta.json",
    "l6_10v_read_model/l6_10v_meta_learning_update_candidate.json",
    "l6_10v_read_model/l6_10v_readiness_assessment.json",
    "l6_10v_read_model/l6_10v_blockers.json",
    "l6_10v_read_model/l6_10v_next_milestone_recommendation.json",
    "l6_10v_read_model/l6_10v_read_model_summary.json",
    "console_read_model/generated/l6_10v_seed_or_search_resolver_enablement_summary.json",
]

FORBIDDEN_FLAGS = [
    "broad_search_authorized",
    "repeated_search_loop_authorized",
    "crawling_authorized",
    "scraping_authorized",
    "browser_automation_authorized",
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


def explicit_request() -> ExplicitSearchResolutionRequest:
    payload = load("locator_resolution_v_attempt/locator_resolution_v_request.json")
    return ExplicitSearchResolutionRequest.from_mapping(payload)


def test_l6_10v_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10v_and_inputs() -> None:
    contract = load(
        "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_milestone_contract.json"
    )
    assert contract["milestone_id"] == "L6.10V"
    assert (
        contract["milestone_name"]
        == "Controlled Seed Locator Registry Population or Explicit Controlled Search Resolver Enablement v0"
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
    ]
    assert contract["mode"] == "controlled_seed_locator_or_explicit_search_resolver_enablement"
    assert contract["reviewed_seed_locator_registry_authorized"] is True
    assert contract["explicit_controlled_search_resolver_authorized"] is True
    assert contract["controlled_search_requires_explicit_enable_flag"] is True


def test_runtime_limits_and_forbidden_actions() -> None:
    contract = load(
        "l6_controlled_seed_locator_or_search_resolver_enablement/l6_10v_milestone_contract.json"
    )
    assert contract["max_selected_work_orders"] == 1
    assert contract["max_seed_registry_lookups"] == 1
    assert contract["max_controlled_search_queries"] == 1
    assert contract["max_concrete_locators_resolved"] == 1
    assert contract["max_pages_read"] == 1
    assert contract["max_total_external_reads"] == 2
    for field in FORBIDDEN_FLAGS:
        assert contract[field] is False, field
    assert contract["search_snippet_fact_use_authorized"] is False
    assert contract["fake_locator_generation_authorized"] is False


def test_reviewed_seed_locator_registry_schema_and_empty_default() -> None:
    schema = load("seed_locator_registry/seed_locator_registry_schema.json")
    registry = load("seed_locator_registry/reviewed_seed_locator_registry.json")
    trace = load("seed_locator_registry/seed_locator_registry_lookup_trace.json")
    required = set(schema["required_fields"])
    for field in [
        "seed_locator_id",
        "linked_work_order_id",
        "linked_evidence_need_id",
        "concrete_locator",
        "reviewed_status",
        "source_use_allowed",
        "facts_inferred_from_seed",
        "observation_authorized_by_seed_alone",
    ]:
        assert field in required
    assert registry["reviewed_seed_locators"] == []
    assert registry["empty_registry_reason"] == "no_reviewed_seed_locator_available"
    assert registry["do_not_invent_urls"] is True
    assert trace["lookup_executed"] is True
    assert trace["lookup_count"] <= 1
    assert trace["seed_locator_resolved"] is False
    assert trace["resolved_locator"] is None
    assert trace["facts_inferred_from_seed"] is False


def test_explicit_search_resolver_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("YSTAR_ENABLE_CONTROLLED_LOCATOR_SEARCH", raising=False)
    config = load("explicit_controlled_search_resolver/explicit_search_resolver_config.json")
    result = ExplicitControlledSearchResolver(config=config).resolve(explicit_request())
    assert result.resolver_enabled is False
    assert result.concrete_locator_resolved is False
    assert result.controlled_search_query_count == 0
    assert result.external_reads_count == 0
    assert result.error_code == "controlled_search_resolver_disabled_by_default"
    assert result.trace["search_executed"] is False
    assert result.trace["network_used"] is False


def test_no_search_runs_without_explicit_config_even_with_env_flag(monkeypatch) -> None:
    monkeypatch.setenv("YSTAR_ENABLE_CONTROLLED_LOCATOR_SEARCH", "1")
    config = load("explicit_controlled_search_resolver/explicit_search_resolver_config.json")
    result = ExplicitControlledSearchResolver(config=config).resolve(explicit_request())
    assert config["controlled_search_enabled"] is False
    assert result.concrete_locator_resolved is False
    assert result.controlled_search_query_count == 0
    assert result.external_reads_count == 0


def test_locator_resolution_attempt_counts_and_no_fake_url() -> None:
    selected = load("locator_resolution_v_attempt/selected_work_order.json")
    result = load("locator_resolution_v_attempt/locator_resolution_v_result.json")
    trace = load("locator_resolution_v_attempt/locator_resolution_v_trace.json")
    eligibility = load("locator_resolution_v_attempt/locator_resolution_v_eligibility_result.json")
    assert selected["selected_count"] <= 1
    assert result["resolution_path_used"] == "disabled_no_path"
    assert result["seed_registry_lookup_count"] <= 1
    assert result["controlled_search_query_count"] <= 1
    assert result["external_reads_count"] <= 2
    assert result["concrete_locator_resolved"] is False
    assert result["resolved_locator"] is None
    assert result["facts_inferred_from_resolution"] is False
    assert result["search_snippets_used_as_evidence"] is False
    assert result["error_code"] == "no_enabled_locator_resolution_path"
    assert trace["concrete_locator_resolved"] is False
    assert eligibility["locator_eligible_for_observation"] is False


def test_observation_trace_and_evidence_packet_exist_when_blocked() -> None:
    trace = load("tiny_observation_v_result/tiny_observation_v_trace.json")
    evidence = load("tiny_observation_v_result/tiny_evidence_v_packet.json")
    review = load("tiny_observation_v_result/tiny_post_observation_v_review_packet.json")
    refinement = load("tiny_observation_v_result/tiny_refinement_v_candidate.json")
    assert trace["observation_executed"] is False
    assert trace["network_used"] is False
    assert trace["external_reads_count"] == 0
    assert trace["pages_read_count"] == 0
    assert evidence["live_source_evidence_captured"] is False
    assert evidence["captured_claims"] == []
    assert evidence["publication_taken"] is False
    assert evidence["outreach_taken"] is False
    assert evidence["payment_taken"] is False
    assert evidence["revenue_action_taken"] is False
    assert evidence["mcp_execution_taken"] is False
    assert review["approve_for_external_use"] is False
    assert review["applied"] is False
    assert refinement["review_required"] is True
    assert refinement["approved"] is False
    assert refinement["applied"] is False


def test_no_action_receipts_show_disallowed_actions_false() -> None:
    receipts = load("tiny_observation_v_result/tiny_observation_v_no_action_receipts.json")
    assert receipts["receipts"]
    for receipt in receipts["receipts"]:
        assert receipt["authorized_in_l6_10v"] is False
        assert receipt["executed_in_l6_10v"] is False


def test_cieu_fixture_meta_learning_and_readiness() -> None:
    cieu = load("l6_10v_read_model/l6_10v_cieu_like_fixture.json")
    meta = load("l6_10v_read_model/l6_10v_meta_learning_update_candidate.json")
    readiness = load("l6_10v_read_model/l6_10v_readiness_assessment.json")
    assert cieu["event_mode"] == "l6_10v_controlled_seed_locator_or_search_resolver_enablement_fixture"
    assert meta["eligible_for_review_queue"] is True
    assert meta["eligible_for_direct_brain_writeback"] is False
    assert meta["eligible_for_direct_memory_ingestion"] is False
    assert meta["approved"] is False
    assert meta["applied"] is False
    assert readiness["reviewed_seed_locator_registry_created"] is True
    assert readiness["explicit_controlled_search_resolver_created"] is True
    assert readiness["ready_for_l6_11_controlled_multi_source_corroboration"] is False
    assert readiness["remaining_blocker"] == "no_enabled_locator_resolution_path"


def test_console_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "controlled-seed-locator-or-search-resolver-enablement",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.10V Controlled Seed Locator Or Search Resolver Enablement" in result.stdout
    assert "controlled search enabled: False" in result.stdout
    assert "concrete locator resolved: False" in result.stdout
