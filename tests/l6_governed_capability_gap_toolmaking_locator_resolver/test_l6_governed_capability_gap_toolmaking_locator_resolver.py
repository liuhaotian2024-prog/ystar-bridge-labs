from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_governed_capability_gap_toolmaking_locator_resolver",
    "capability_gap_diagnosis_engine",
    "governed_toolmaking_methodology",
    "controlled_tool_contract_model",
    "tool_authority_and_use_gate",
    "tool_sandbox_validation_harness",
    "toolmaking_residual_learning_loop",
    "locator_resolver_capability_probe",
    "controlled_locator_resolver_interface",
    "locator_resolver_adapter_registry",
    "locator_resolver_input_output_contract",
    "locator_resolver_policy_and_limits",
    "locator_resolver_selection_gate",
    "locator_resolution_adapter_trace",
    "concrete_locator_eligibility_gate",
    "adapter_bound_tiny_observation_retry",
    "adapter_bound_evidence_capture",
    "adapter_bound_review_and_refinement",
    "adapter_bound_blocker_and_fallback_report",
    "adapter_bound_no_action_receipts",
    "l6_10t_strategic_residual_loop",
    "l6_10t_readiness_report",
]

REQUIRED_JSON = [
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_milestone_contract.json",
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_scope.json",
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_safety_flags.json",
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_runtime_limits.json",
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_portability_contract.json",
    "l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_summary.json",
    "capability_gap_diagnosis_engine/blocker_taxonomy.json",
    "capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json",
    "governed_toolmaking_methodology/governed_toolmaking_lifecycle.json",
    "governed_toolmaking_methodology/capability_gap_to_tool_need_map.json",
    "governed_toolmaking_methodology/toolmaking_non_bypass_policy.json",
    "controlled_tool_contract_model/controlled_tool_contract_schema.json",
    "controlled_tool_contract_model/controlled_tool_contract_example_locator_resolver.json",
    "controlled_tool_contract_model/forbidden_tool_contract_patterns.json",
    "tool_authority_and_use_gate/tool_authority_model.json",
    "tool_authority_and_use_gate/tool_use_gate_contract.json",
    "tool_sandbox_validation_harness/tool_validation_test_matrix.json",
    "toolmaking_residual_learning_loop/toolmaking_cieu_like_fixture.json",
    "toolmaking_residual_learning_loop/toolmaking_meta_learning_candidate.json",
    "locator_resolver_capability_probe/resolver_capability_probe_result.json",
    "locator_resolver_adapter_registry/resolver_adapter_registry.json",
    "locator_resolver_input_output_contract/locator_resolution_request_001.json",
    "locator_resolver_input_output_contract/locator_resolution_result_disabled_fixture.json",
    "locator_resolver_policy_and_limits/resolver_runtime_limits.json",
    "locator_resolver_policy_and_limits/resolver_disallowed_actions.json",
    "locator_resolver_selection_gate/resolver_selection_decision.json",
    "locator_resolution_adapter_trace/adapter_trace.json",
    "concrete_locator_eligibility_gate/concrete_locator_eligibility_result.json",
    "adapter_bound_tiny_observation_retry/adapter_bound_retry_trace.json",
    "adapter_bound_evidence_capture/adapter_bound_evidence_packet.json",
    "adapter_bound_review_and_refinement/adapter_bound_refinement_candidate.json",
    "adapter_bound_blocker_and_fallback_report/locator_tooling_blocker.json",
    "l6_10t_strategic_residual_loop/l6_10t_cieu_like_fixture.json",
    "l6_10t_strategic_residual_loop/l6_10t_meta_learning_update_candidate.json",
    "l6_10t_readiness_report/l6_10t_readiness_assessment.json",
    "console_read_model/generated/l6_10t_toolmaking_locator_resolver_summary.json",
]

RECEIPTS = [
    "no_broad_search_receipt.json",
    "no_repeated_search_loop_receipt.json",
    "no_crawling_receipt.json",
    "no_scraping_receipt.json",
    "no_browser_automation_receipt.json",
    "no_login_receipt.json",
    "no_account_creation_receipt.json",
    "no_contact_receipt.json",
    "no_payment_receipt.json",
    "no_form_submission_receipt.json",
    "no_posting_commenting_messaging_receipt.json",
    "no_publication_receipt.json",
    "no_outreach_receipt.json",
    "no_revenue_execution_receipt.json",
    "no_mcp_execution_receipt.json",
    "no_live_behavior_receipt.json",
    "no_cieu_db_write_receipt.json",
    "no_canonical_mutation_receipt.json",
    "no_brain_memory_writeback_receipt.json",
    "no_direct_y_star_mutation_receipt.json",
]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_l6_10t_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_10t_and_portability_boundary() -> None:
    contract = load("l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_milestone_contract.json")
    assert contract["milestone_id"] == "L6.10T"
    assert contract["milestone_name"] == (
        "Governed Capability Gap Tool-Making Methodology & Controlled Locator Resolver Adapter v0"
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
    ]
    assert contract["mode"] == "governed_capability_gap_toolmaking_and_locator_resolver_adapter"
    assert contract["os_neutral_design_required"] is True
    assert contract["mac_only_solution_allowed"] is False
    assert contract["capability_gap_diagnosis_authorized"] is True
    assert contract["controlled_locator_resolver_interface_authorized"] is True
    assert contract["resolver_capability_probe_authorized"] is True
    assert contract["disabled_no_network_resolver_authorized"] is True


def test_forbidden_actions_and_live_tool_authority_are_blocked() -> None:
    contract = load("l6_governed_capability_gap_toolmaking_locator_resolver/l6_10t_milestone_contract.json")
    for field in [
        "tool_external_authority_auto_grant_authorized",
        "broad_web_search_authorized",
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
    ]:
        assert contract[field] is False, field


def test_capability_gap_diagnosis_classifies_l6_10r_blocker() -> None:
    analysis = load("capability_gap_diagnosis_engine/l6_10_l6_10r_blocker_analysis.json")
    diagnosis = analysis["diagnosis"]
    assert diagnosis["blocker_description"] == "no_locator_and_no_controlled_locator_discovery_tooling"
    assert diagnosis["primary_gap_type"] == "tool_capability_gap"
    assert diagnosis["secondary_gap_type"] == "runtime_environment_gap"
    assert diagnosis["not_a_governance_logic_failure"] is True
    assert diagnosis["not_an_agentic_evidence_reasoning_failure"] is True
    assert diagnosis["toolmaking_candidate"] is True
    assert "broad_search" in diagnosis["prohibited_capability_expansion"]
    assert "define_tool_contract" in diagnosis["recommended_governed_toolmaking_path"]


def test_governed_toolmaking_lifecycle_and_non_bypass_policy() -> None:
    lifecycle = load("governed_toolmaking_methodology/governed_toolmaking_lifecycle.json")
    stages = lifecycle["lifecycle_stages"]
    expected_order = [
        "detect_blocker",
        "classify_gap",
        "define_tool_contract",
        "define_adapter_interface",
        "define_sandbox_implementation",
        "define_validation_tests",
        "define_use_gate",
        "generate_residual",
    ]
    for stage in expected_order:
        assert stage in stages
    assert stages.index("detect_blocker") < stages.index("classify_gap")
    assert stages.index("define_tool_contract") < stages.index("define_adapter_interface")
    policy = load("governed_toolmaking_methodology/toolmaking_non_bypass_policy.json")
    assert policy["tests_do_not_equal_approval"] is True
    assert policy["readiness_does_not_equal_approval"] is True
    assert policy["live_external_actions_require_future_approval"] is True


def test_controlled_tool_contract_and_authority_gate_forbid_self_approval() -> None:
    schema = load("controlled_tool_contract_model/controlled_tool_contract_schema.json")
    for field in [
        "tool_contract_id",
        "input_schema",
        "output_schema",
        "runtime_limits",
        "use_gate_required",
        "approval_required_before_live_use",
    ]:
        assert field in schema["required_fields"]
    forbidden = load("controlled_tool_contract_model/forbidden_tool_contract_patterns.json")
    assert "unbounded_search" in forbidden["forbidden_patterns"]
    assert "self_approval" in forbidden["forbidden_patterns"]
    authority = load("tool_authority_and_use_gate/tool_authority_model.json")
    assert authority["tool_generation_is_live_use_approval"] is False
    assert authority["tool_tests_passing_are_live_use_approval"] is False
    assert authority["tool_registration_is_live_use_approval"] is False
    assert authority["sandbox_use_is_live_use_approval"] is False
    assert authority["external_authority_requires_separate_approval"] is True


def test_sandbox_validation_harness_and_residual_loop_exist() -> None:
    matrix = load("tool_sandbox_validation_harness/tool_validation_test_matrix.json")
    categories = {entry["category"] for entry in matrix["validation_tests"]}
    assert {"schema_validation", "disabled_mode_behavior", "no_fake_success"}.issubset(categories)
    fixture = load("toolmaking_residual_learning_loop/toolmaking_cieu_like_fixture.json")
    assert fixture["event_mode"] == "l6_10t_toolmaking_methodology_fixture"
    candidate = load("toolmaking_residual_learning_loop/toolmaking_meta_learning_candidate.json")
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_disabled_no_network_resolver_returns_typed_capability_gap() -> None:
    stub_path = ROOT / "controlled_locator_resolver_interface/controlled_locator_resolver_python_stub.py"
    spec = importlib.util.spec_from_file_location("controlled_locator_resolver_python_stub", stub_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    request = module.LocatorResolutionRequest(
        request_id="test_request",
        linked_work_order_id="l6_8_observation_work_order_001",
        evidence_need_id="l6_8_evidence_need_001",
        source_type="official policy or program source",
        source_function="locator resolution only",
        observation_question="What source could be observed later?",
        locator_discovery_query="placeholder locator resolution only",
    )
    resolver = module.DisabledNoNetworkResolver()
    result = resolver.resolve(request)
    assert resolver.network_enabled is False
    assert result.concrete_locator_resolved is False
    assert result.locator is None
    assert result.error_code == "no_controlled_locator_resolver_available"
    assert result.queries_used == 0
    assert result.external_reads_used == 0
    assert result.facts_inferred is False
    assert result.eligible_for_read_only_observation is False


def test_capability_probe_is_local_only_and_non_networked() -> None:
    probe = load("locator_resolver_capability_probe/resolver_capability_probe_result.json")
    assert probe["probe_local_only"] is True
    assert probe["network_used"] is False
    assert probe["api_called"] is False
    assert probe["browser_launched"] is False
    assert probe["mcp_executed"] is False
    assert probe["controlled_locator_resolver_available"] is False
    assert probe["selected_resolver_adapter_id"] == "disabled_no_network_resolver"
    assert probe["resolver_mode"] == "disabled_no_network"
    assert probe["capability_gap_code"] == "no_controlled_locator_resolver_available"


def test_adapter_registry_io_contract_policy_and_selection_gate() -> None:
    registry = load("locator_resolver_adapter_registry/resolver_adapter_registry.json")
    adapter_ids = {adapter["adapter_id"] for adapter in registry["adapters"]}
    assert "disabled_no_network_resolver" in adapter_ids
    assert registry["selected_default_adapter_id"] == "disabled_no_network_resolver"
    result = load("locator_resolver_input_output_contract/locator_resolution_result_disabled_fixture.json")
    assert result["concrete_locator_resolved"] is False
    assert result["error_code"] == "no_controlled_locator_resolver_available"
    assert result["queries_used"] == 0
    assert result["external_reads_used"] == 0
    limits = load("locator_resolver_policy_and_limits/resolver_runtime_limits.json")
    assert limits["max_queries"] == 1
    assert limits["max_results"] == 1
    assert limits["max_locator_outputs"] == 1
    selection = load("locator_resolver_selection_gate/resolver_selection_decision.json")
    assert selection["decision"] in {"select_disabled_no_network_resolver", "block_due_no_resolver"}
    assert selection["selected_resolver_adapter_id"] == "disabled_no_network_resolver"


def test_adapter_trace_no_fake_locator_and_retry_blocked_when_absent() -> None:
    trace = load("locator_resolution_adapter_trace/adapter_trace.json")
    assert trace["adapter_selected"] == "disabled_no_network_resolver"
    assert trace["locator_discovery_query_executed"] is False
    assert trace["queries_count"] == 0
    assert trace["external_reads_count"] == 0
    assert trace["concrete_locator_resolved"] is False
    assert trace["resolved_locator"] is None
    assert trace["facts_inferred_from_discovery"] is False
    eligibility = load("concrete_locator_eligibility_gate/concrete_locator_eligibility_result.json")
    assert eligibility["eligibility_evaluated"] is False
    assert eligibility["reason"] == "no_concrete_locator"
    retry = load("adapter_bound_tiny_observation_retry/adapter_bound_retry_trace.json")
    assert retry["observation_executed"] is False
    assert retry["network_used"] is False
    assert retry["external_reads_count"] == 0
    assert retry["pages_read_count"] == 0
    assert retry["reason"] == "no_concrete_locator"


def test_blocked_evidence_review_and_refinement_are_review_only() -> None:
    evidence = load("adapter_bound_evidence_capture/adapter_bound_evidence_packet.json")
    assert evidence["live_source_evidence_captured"] is False
    assert evidence["source_locator"] is None
    assert evidence["captured_claims"] == []
    assert "no live observation executed" in evidence["missing_context"]
    assert evidence["publication_taken"] is False
    assert evidence["outreach_taken"] is False
    assert evidence["payment_taken"] is False
    assert evidence["mcp_execution_taken"] is False
    review = load("adapter_bound_review_and_refinement/adapter_bound_review_packet.json")
    assert review["current_decision"] == "review_pending"
    assert review["approve_for_external_use"] is False
    candidate = load("adapter_bound_review_and_refinement/adapter_bound_refinement_candidate.json")
    assert candidate["review_required"] is True
    assert candidate["approved"] is False
    assert candidate["applied"] is False
    assert candidate["artifact_update_authorized"] is False
    assert candidate["canonical_update_authorized"] is False
    assert candidate["brain_writeback_authorized"] is False
    assert candidate["memory_ingestion_authorized"] is False
    assert candidate["direct_y_star_mutation_authorized"] is False


def test_blocker_report_names_exact_missing_capability() -> None:
    blocker = load("adapter_bound_blocker_and_fallback_report/locator_tooling_blocker.json")
    assert blocker["blocker_code"] == "no_controlled_locator_resolver_available"
    assert blocker["locator_fabricated"] is False
    assert blocker["evidence_fabricated"] is False
    fallback = load("adapter_bound_blocker_and_fallback_report/adapter_fallback_decision.json")
    assert fallback["fallback_decision"] == "block_and_report_capability_gap"


def test_no_action_receipts_exist_and_disallowed_actions_false() -> None:
    for filename in RECEIPTS:
        receipt = load(f"adapter_bound_no_action_receipts/{filename}")
        assert receipt["authorized_in_l6_10t"] is False
        assert receipt["executed_in_l6_10t"] is False
        assert receipt["generated_tool_live_authority_granted"] is False


def test_l6_10t_strategic_residual_and_readiness() -> None:
    fixture = load("l6_10t_strategic_residual_loop/l6_10t_cieu_like_fixture.json")
    assert fixture["event_mode"] == "l6_10t_governed_capability_gap_toolmaking_locator_resolver_fixture"
    candidate = load("l6_10t_strategic_residual_loop/l6_10t_meta_learning_update_candidate.json")
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["eligible_for_direct_strategy_mutation"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False
    readiness = load("l6_10t_readiness_report/l6_10t_readiness_assessment.json")
    assert readiness["general_governed_toolmaking_methodology_ready_for_reuse"] is True
    assert readiness["controlled_resolver_adapter_available"] is False
    assert readiness["probe_used_network"] is False
    assert readiness["remaining_blocker"] == "no_controlled_locator_resolver_available"
    assert readiness["ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot"] is False
    assert readiness["next_recommended_milestone"] == "L6.10U Controlled Locator Resolver Enablement Sandbox v0"


def test_console_read_model_command_works() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "console_read_model/cli/team_console.py",
            "governed-capability-gap-toolmaking-locator-resolver",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "L6.10T Governed Capability Gap Toolmaking Locator Resolver" in result.stdout
    assert "selected resolver adapter id: disabled_no_network_resolver" in result.stdout
    assert "probe used network: False" in result.stdout
