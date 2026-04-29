from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from controlled_locator_resolver_runtime.controlled_locator_resolver import (  # noqa: E402
    ControlledLocatorResolverRuntime,
    DisabledResolver,
    EnvironmentGatedSearchResolver,
    LocatorResolutionRequest,
    SeedRegistryResolver,
)


REQUIRED_DIRS = [
    "l6_controlled_locator_resolver_enablement",
    "controlled_locator_resolver_runtime",
    "controlled_locator_resolution_attempt",
    "controlled_locator_observation_result",
    "controlled_locator_resolver_read_model",
]

REQUIRED_JSON = [
    "l6_controlled_locator_resolver_enablement/l6_10u_milestone_contract.json",
    "l6_controlled_locator_resolver_enablement/l6_10u_scope.json",
    "l6_controlled_locator_resolver_enablement/l6_10u_runtime_limits.json",
    "l6_controlled_locator_resolver_enablement/l6_10u_safety_flags.json",
    "l6_controlled_locator_resolver_enablement/l6_10u_summary.json",
    "controlled_locator_resolver_runtime/resolver_types.json",
    "controlled_locator_resolver_runtime/resolver_config.example.json",
    "controlled_locator_resolver_runtime/seed_locator_registry.json",
    "controlled_locator_resolution_attempt/selected_work_order.json",
    "controlled_locator_resolution_attempt/locator_resolution_request.json",
    "controlled_locator_resolution_attempt/locator_resolution_result.json",
    "controlled_locator_resolution_attempt/locator_resolution_trace.json",
    "controlled_locator_resolution_attempt/locator_eligibility_result.json",
    "controlled_locator_observation_result/tiny_observation_execution_packet.json",
    "controlled_locator_observation_result/tiny_observation_trace.json",
    "controlled_locator_observation_result/tiny_evidence_packet.json",
    "controlled_locator_observation_result/tiny_claim_boundary_assessment.json",
    "controlled_locator_observation_result/tiny_post_observation_review_packet.json",
    "controlled_locator_observation_result/tiny_refinement_candidate.json",
    "controlled_locator_observation_result/tiny_observation_no_action_receipts.json",
    "controlled_locator_resolver_read_model/l6_10u_cieu_like_fixture.json",
    "controlled_locator_resolver_read_model/l6_10u_strategic_residual_delta.json",
    "controlled_locator_resolver_read_model/l6_10u_meta_learning_update_candidate.json",
    "controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json",
    "controlled_locator_resolver_read_model/l6_10u_blockers.json",
    "controlled_locator_resolver_read_model/l6_10u_next_milestone_recommendation.json",
    "controlled_locator_resolver_read_model/l6_10u_read_model_summary.json",
    "console_read_model/generated/l6_10u_locator_resolver_enablement_summary.json",
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


def request() -> LocatorResolutionRequest:
    return LocatorResolutionRequest(
        request_id="test_request",
        linked_work_order_id="l6_10u_selected_work_order_001",
        evidence_need_id="l6_8_evidence_need_001",
        source_type="official policy or program source",
        source_function="official policy or program source",
        observation_question="What bounded evidence is needed?",
        locator_discovery_query="official policy source bounded evidence",
    )


def test_l6_10u_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10u_and_runtime_limits() -> None:
    contract = load("l6_controlled_locator_resolver_enablement/l6_10u_milestone_contract.json")
    assert contract["milestone_id"] == "L6.10U"
    assert contract["milestone_name"] == "Controlled Locator Resolver Enablement & First Locator Attempt v0"
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
    ]
    assert contract["mode"] == "controlled_locator_resolver_enablement_first_attempt"
    assert contract["seed_registry_resolver_authorized"] is True
    assert contract["environment_gated_controlled_search_resolver_authorized"] is True
    assert contract["disabled_resolver_authorized"] is True
    assert contract["max_selected_work_orders"] == 1
    assert contract["max_locator_resolution_attempts"] == 1
    assert contract["max_search_queries"] == 1
    assert contract["max_seed_registry_lookups"] == 1
    assert contract["max_concrete_locators_returned"] == 1
    assert contract["max_pages_read"] == 1
    assert contract["max_total_external_reads"] == 2


def test_forbidden_actions_are_not_authorized() -> None:
    contract = load("l6_controlled_locator_resolver_enablement/l6_10u_milestone_contract.json")
    for field in FORBIDDEN_FLAGS:
        assert contract[field] is False, field
    assert contract["fake_locator_generation_authorized"] is False
    assert contract["search_snippet_fact_use_authorized"] is False


def test_resolver_runtime_module_and_disabled_default_path() -> None:
    result = DisabledResolver().resolve(request())
    assert result.concrete_locator_resolved is False
    assert result.locator is None
    assert result.error_code == "no_enabled_locator_resolution_path"
    assert result.trace["network_used"] is False
    assert result.trace["fake_locator_returned"] is False


def test_seed_registry_resolver_can_resolve_at_most_one_local_locator(tmp_path: Path) -> None:
    registry = tmp_path / "seed_locator_registry.json"
    registry.write_text(
        json.dumps(
            {
                "seed_locators": [
                    {
                        "locator": "https://example.org/public-program",
                        "source_title": "Example Public Program",
                        "source_type": "official policy or program source",
                        "work_order_ids": ["l6_10u_selected_work_order_001"],
                        "evidence_need_ids": ["l6_8_evidence_need_001"],
                        "source_types": ["official policy or program source"],
                        "source_functions": ["official policy or program source"],
                        "eligible_for_read_only_observation": True,
                    },
                    {
                        "locator": "https://example.org/second",
                        "source_type": "official policy or program source",
                        "work_order_ids": ["l6_10u_selected_work_order_001"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    result = SeedRegistryResolver(registry).resolve(request())
    assert result.resolver_mode == "seed_registry"
    assert result.seed_registry_lookup_count == 1
    assert result.concrete_locator_resolved is True
    assert result.locator == "https://example.org/public-program"
    assert result.external_reads_count == 0
    assert result.trace["matches_returned"] == 1
    assert result.trace["network_used"] is False


def test_environment_gated_search_resolver_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("YSTAR_CONTROLLED_LOCATOR_SEARCH_ENABLED", raising=False)
    result = EnvironmentGatedSearchResolver({"environment_gated_search_enabled": True}).resolve(request())
    assert result.concrete_locator_resolved is False
    assert result.search_query_count == 0
    assert result.external_reads_count == 0
    assert result.error_code == "no_controlled_search_resolver_enabled"
    assert result.trace["search_executed"] is False
    assert result.trace["network_used"] is False


def test_default_runtime_attempt_does_not_perform_search_or_network() -> None:
    req = LocatorResolutionRequest.from_mapping(
        load("controlled_locator_resolution_attempt/locator_resolution_request.json")
    )
    result = ControlledLocatorResolverRuntime(ROOT).resolve(req)
    assert result.seed_registry_lookup_count <= 1
    assert result.search_query_count == 0
    assert result.external_reads_count == 0
    assert result.concrete_locator_resolved is False
    assert result.locator is None
    assert result.error_code == "no_enabled_locator_resolution_path"
    assert result.trace["seed_registry"]["network_used"] is False
    assert result.trace["environment_gated_search"]["search_executed"] is False


def test_resolution_attempt_counts_and_no_fake_locator() -> None:
    selected = load("controlled_locator_resolution_attempt/selected_work_order.json")
    result = load("controlled_locator_resolution_attempt/locator_resolution_result.json")
    trace = load("controlled_locator_resolution_attempt/locator_resolution_trace.json")
    eligibility = load("controlled_locator_resolution_attempt/locator_eligibility_result.json")
    assert selected["selected_count"] <= 1
    assert result["seed_registry_lookup_count"] <= 1
    assert result["search_query_count"] <= 1
    assert result["external_reads_count"] <= 2
    assert result["concrete_locator_resolved"] is False
    assert result["locator"] is None
    assert result["facts_inferred_from_resolution"] is False
    assert trace["concrete_locator_resolved"] is False
    assert eligibility["locator_eligible_for_observation"] is False


def test_evidence_and_observation_packets_exist_even_when_blocked() -> None:
    trace = load("controlled_locator_observation_result/tiny_observation_trace.json")
    evidence = load("controlled_locator_observation_result/tiny_evidence_packet.json")
    refinement = load("controlled_locator_observation_result/tiny_refinement_candidate.json")
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
    assert refinement["review_required"] is True
    assert refinement["approved"] is False
    assert refinement["applied"] is False


def test_no_action_receipts_show_disallowed_actions_false() -> None:
    receipts = load("controlled_locator_observation_result/tiny_observation_no_action_receipts.json")
    assert receipts["receipts"]
    for receipt in receipts["receipts"]:
        assert receipt["authorized_in_l6_10u"] is False
        assert receipt["executed_in_l6_10u"] is False


def test_cieu_fixture_meta_learning_and_readiness() -> None:
    cieu = load("controlled_locator_resolver_read_model/l6_10u_cieu_like_fixture.json")
    meta = load("controlled_locator_resolver_read_model/l6_10u_meta_learning_update_candidate.json")
    readiness = load("controlled_locator_resolver_read_model/l6_10u_readiness_assessment.json")
    assert cieu["event_mode"] == "l6_10u_controlled_locator_resolver_enablement_first_attempt_fixture"
    assert meta["eligible_for_review_queue"] is True
    assert meta["eligible_for_direct_brain_writeback"] is False
    assert meta["eligible_for_direct_memory_ingestion"] is False
    assert meta["approved"] is False
    assert meta["applied"] is False
    assert readiness["resolver_runtime_created"] is True
    assert readiness["ready_for_l6_11_controlled_multi_source_corroboration"] is False
    assert readiness["remaining_blocker"] == "no_enabled_locator_resolution_path"


def test_console_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "controlled-locator-resolver-enable-first-attempt",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.10U Controlled Locator Resolver Enablement First Attempt" in result.stdout
    assert "controlled search executed: False" in result.stdout
