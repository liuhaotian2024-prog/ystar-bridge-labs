from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "live_boundary_no_go_framework"
    / "tools"
    / "build_live_boundary_no_go_framework.py"
)

REQUIRED_DIRECTORIES = [
    "live_boundary_no_go_framework",
    "live_capability_domain_registry",
    "no_go_invariant_matrix",
    "live_readiness_evidence_index",
    "live_blocker_risk_register",
    "l6_meta_development_entry_gate",
    "system_no_go_decision_packet",
    "live_boundary_cieu_residual",
    "live_boundary_readiness",
]

REQUIRED_FILES = [
    "live_boundary_no_go_framework/README.md",
    "live_boundary_no_go_framework/tools/build_live_boundary_no_go_framework.py",
    "live_boundary_no_go_framework/live_boundary_no_go_contract.json",
    "live_boundary_no_go_framework/live_boundary_no_go_input_fixture.json",
    "live_boundary_no_go_framework/live_boundary_no_go_run.json",
    "live_boundary_no_go_framework/live_boundary_no_go_summary.json",
    "live_boundary_no_go_framework/live_boundary_no_go_report.md",
    "live_capability_domain_registry/live_capability_domain_registry.json",
    "live_capability_domain_registry/live_capability_status_matrix.json",
    "live_capability_domain_registry/live_capability_dependency_map.json",
    "live_capability_domain_registry/live_capability_denied_scope.json",
    "live_capability_domain_registry/live_capability_summary.json",
    "live_capability_domain_registry/live_capability_report.md",
    "no_go_invariant_matrix/no_go_invariant_matrix.json",
    "no_go_invariant_matrix/permanent_invariant_registry.json",
    "no_go_invariant_matrix/temporary_gate_registry.json",
    "no_go_invariant_matrix/no_go_invariant_gap_report.md",
    "no_go_invariant_matrix/no_go_invariant_summary.json",
    "live_readiness_evidence_index/live_readiness_evidence_index.json",
    "live_readiness_evidence_index/l5_chain_evidence_map.json",
    "live_readiness_evidence_index/evidence_strength_matrix.json",
    "live_readiness_evidence_index/evidence_gap_matrix.json",
    "live_readiness_evidence_index/live_readiness_evidence_summary.json",
    "live_readiness_evidence_index/live_readiness_evidence_report.md",
    "live_blocker_risk_register/live_blocker_risk_register.json",
    "live_blocker_risk_register/live_blocker_priority_matrix.json",
    "live_blocker_risk_register/live_blocker_mitigation_map.json",
    "live_blocker_risk_register/live_blocker_summary.json",
    "live_blocker_risk_register/live_blocker_report.md",
    "l6_meta_development_entry_gate/l6_meta_development_entry_gate.json",
    "l6_meta_development_entry_gate/l6_non_execution_boundary.json",
    "l6_meta_development_entry_gate/l6_generative_principles.json",
    "l6_meta_development_entry_gate/l6_forbidden_hardcoding_policy.json",
    "l6_meta_development_entry_gate/l6_seed_hypothesis_policy.json",
    "l6_meta_development_entry_gate/l6_entry_gate_summary.json",
    "l6_meta_development_entry_gate/l6_entry_gate_report.md",
    "system_no_go_decision_packet/system_no_go_decision_packet.json",
    "system_no_go_decision_packet/system_no_go_decision_reason_codes.json",
    "system_no_go_decision_packet/system_live_boundary_decision_summary.json",
    "system_no_go_decision_packet/system_no_go_decision_report.md",
    "live_boundary_cieu_residual/live_boundary_cieu_event_fixture.json",
    "live_boundary_cieu_residual/live_boundary_predicted_outcome.json",
    "live_boundary_cieu_residual/live_boundary_mock_actual_outcome.json",
    "live_boundary_cieu_residual/live_boundary_residual_delta.json",
    "live_boundary_cieu_residual/live_boundary_cieu_summary.json",
    "live_boundary_cieu_residual/live_boundary_cieu_report.md",
    "live_boundary_readiness/live_boundary_readiness.json",
    "live_boundary_readiness/live_boundary_readiness.md",
    "live_boundary_readiness/l6_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_0_to_l5_12_readiness_chain",
    "load_release_simulation_readiness",
    "load_mcp_boundary_readiness",
    "load_canonical_learning_readiness",
    "load_approval_record_readiness",
    "classify_live_capability_domains",
    "define_no_go_invariants",
    "evaluate_live_readiness_evidence",
    "identify_live_blockers",
    "classify_permanent_vs_temporary_gates",
    "evaluate_l6_design_entry",
    "define_l6_non_execution_boundary",
    "generate_system_no_go_decision_packet",
    "emit_live_boundary_cieu_like_fixture",
    "produce_l5_14_or_l6_recommendation",
]

SAFETY_FLAGS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "mcp_server_execution_enabled",
    "mcp_tool_execution_enabled",
    "cieu_persistence_enabled",
    "durable_approval_persistence_enabled",
    "real_approval_record_write_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "strategy_mutation_enabled",
    "candidate_auto_approval_enabled",
    "real_candidate_approval_enabled",
    "real_canonical_policy_mutation_enabled",
    "real_canonical_update_application_enabled",
    "real_release_execution_enabled",
    "real_y_star_direct_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "revenue_execution_enabled",
}

FALSE_FIELDS = SAFETY_FLAGS | {
    "l6_revenue_execution_allowed",
    "l6_external_observation_allowed",
    "l6_external_action_allowed",
    "l6_network_enabled",
    "l6_publication_enabled",
    "l6_payment_enabled",
    "persistence_enabled",
    "db_write_performed",
    "real_live_mode_enabled",
    "l6_execution_enabled",
    "allowed_now",
    "live_allowed",
    "enabled_now",
    "semantic_truth_scoring_used",
    "ready_for_l6_revenue_opportunity_execution",
}

REQUIRED_INPUT_REFS = {
    "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
    "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
    "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
    "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
    "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
    "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
    "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
    "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
    "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
    "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
    "real_release_simulation_readiness/real_release_simulation_readiness.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json",
    "cross_repo_non_bypass_proof/cross_repo_non_bypass_invariant_map.json",
    "release_blocker_decision/release_blocker_decision.json",
}

LIVE_DOMAINS = {
    "live_behavior_execution",
    "real_mcp_execution",
    "network_api_access",
    "external_action_execution",
    "real_cieu_persistence",
    "durable_approval_persistence",
    "real_canonical_policy_mutation",
    "real_canonical_update_application",
    "brain_writeback",
    "memory_ingestion",
    "strategy_mutation",
    "real_release_execution",
    "revenue_opportunity_discovery",
    "revenue_execution",
    "public_content_publication",
    "payment_or_monetization_action",
}

PERMANENT_INVARIANTS = {
    "residual_cannot_directly_mutate_y_star",
    "actual_y_cannot_become_y_star",
    "mission_y_star_lineage_must_be_preserved",
    "behavior_y_star_must_be_projection_derived",
    "no_mcp_call_without_behavior_y_star",
    "no_mcp_call_without_pre_u",
    "no_mcp_call_without_governance_decision",
    "no_mcp_call_without_bridge_receipt",
    "no_mcp_call_without_cieu_receipt",
    "no_mcp_call_without_residual_delta",
    "no_brain_writeback_without_review_and_approval",
    "no_memory_ingestion_without_review_and_approval",
    "no_external_action_without_explicit_authorization",
    "no_revenue_execution_without_separate_governed_release_path",
    "no_publication_without_review_and_approval",
    "no_payment_action_without_explicit_approval_and_compliance_review",
}

TEMPORARY_GATES = {
    "durable_approval_persistence",
    "real_cieu_persistence",
    "real_mcp_execution",
    "real_release_execution",
    "l6_external_observation",
    "l6_publication",
    "l6_payment_integration",
}

MILESTONES = {
    "L5.0 archaeology",
    "L5.1 projection harness",
    "L5.2 auto-projection core",
    "L5.3 projection-checked cycle",
    "L5.4 shadow learning cycle",
    "L5.5 cross-repo governance proof",
    "L5.6 governed MCP dry-run adapter",
    "L5.7 controlled canonical learning design",
    "L5.8 approved sandbox update",
    "L5.9 real approval workflow boundary",
    "L5.10 approval record sandbox",
    "L5.11 real release preflight",
    "L5.12 release simulation sandbox",
}

EVIDENCE_CLASSES = {
    "strong_dry_run_proof",
    "sandbox_proof",
    "contract_proof",
    "boundary_proof",
    "missing_live_proof",
    "explicit_no_go",
}

BLOCKERS = {
    "no_real_durable_approval_persistence",
    "no_real_cieu_persistence",
    "no_real_mcp_execution_sandbox",
    "no_real_network_boundary",
    "no_real_external_action_boundary",
    "no_real_brain_writeback_boundary",
    "no_real_memory_ingestion_boundary",
    "no_real_strategy_mutation_boundary",
    "no_live_release_protocol",
    "no_live_rollback_protocol",
    "full_pytest_known_unrelated_collection_issue",
    "no_l6_external_observation_boundary",
    "no_l6_publication_approval_boundary",
    "no_l6_payment_or_revenue_compliance_boundary",
}

DENIED_L6_BOUNDARY_PHRASES = {
    "network/API calls",
    "bounty/RFP/grant scraping",
    "YouTube publishing",
    "social media posting",
    "email/message sending",
    "payment integration",
    "customer outreach",
    "external content publication",
    "real revenue pursuit",
    "real market claims",
}

GENERATIVE_PRINCIPLES = {
    "self-modeling",
    "unique asset field discovery",
    "world-value hypothesis generation",
    "value form hypothesis generation",
    "conversion path design",
    "minimum viable proof design",
    "governed experiment design",
    "strategic residual learning",
    "meta-learning loop",
}

RESIDUAL_CLASSES = {
    "live_readiness_residual",
    "evidence_gap_residual",
    "blocker_residual",
    "l6_entry_residual",
    "hardcoding_policy_residual",
    "non_execution_boundary_residual",
    "persistence_blocker_residual",
    "external_action_blocker_residual",
    "revenue_execution_blocker_residual",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load_json(relative_path: str) -> Any:
    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def test_builder_regenerates_l5_13_artifacts() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stderr
    assert "Built L5.13" in result.stdout


def test_required_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_FILES:
        assert (ROOT / path).is_file(), path


def test_all_json_artifacts_parse() -> None:
    for path in JSON_FILES:
        assert load_json(path), path


def test_contract_stages_and_flags() -> None:
    contract = load_json("live_boundary_no_go_framework/live_boundary_no_go_contract.json")
    assert contract["no_go_stages"] == REQUIRED_STAGES
    assert set(contract["safety_flags"]) >= SAFETY_FLAGS
    assert all(contract["safety_flags"][flag] is False for flag in SAFETY_FLAGS)
    assert contract["l6_flags"]["l6_design_entry_allowed"] is True
    for key in {
        "l6_revenue_execution_allowed",
        "l6_external_observation_allowed",
        "l6_external_action_allowed",
        "l6_network_enabled",
        "l6_publication_enabled",
        "l6_payment_enabled",
    }:
        assert contract["l6_flags"][key] is False


def test_no_forbidden_flags_are_true_anywhere() -> None:
    for path in JSON_FILES:
        data = load_json(path)
        for key, value in walk_values(data):
            if key in FALSE_FIELDS:
                assert value is False, f"{path}: {key} must remain false"


def test_input_fixture_references_required_l5_chain_artifacts() -> None:
    fixture = load_json("live_boundary_no_go_framework/live_boundary_no_go_input_fixture.json")
    refs = {entry["path"] for entry in fixture["input_refs"]}
    assert REQUIRED_INPUT_REFS <= refs
    assert fixture["gap_aware_readiness"] is True
    assert fixture["safe_to_continue"] is True


def test_live_capability_domains_are_no_go() -> None:
    registry = load_json("live_capability_domain_registry/live_capability_domain_registry.json")
    status = load_json("live_capability_domain_registry/live_capability_status_matrix.json")
    assert LIVE_DOMAINS <= set(registry["domain_ids"])
    for domain in registry["domains"]:
        assert domain["allowed_now"] is False
        assert domain["denied_now"] is True
        assert domain["current_status"] in {
            "no_go",
            "design_only_allowed",
            "sandbox_only_allowed",
            "future_review_required",
            "permanently_forbidden",
        }
    for row in status["statuses"].values():
        assert row["live_allowed"] is False
        assert row["allowed_now"] is False


def test_invariant_and_temporary_gate_registries() -> None:
    matrix = load_json("no_go_invariant_matrix/no_go_invariant_matrix.json")
    temporary = load_json("no_go_invariant_matrix/temporary_gate_registry.json")
    assert PERMANENT_INVARIANTS <= set(matrix["permanent_invariants"])
    assert matrix["l6_cannot_override"] is True
    gates = {gate["gate_id"] for gate in temporary["temporary_gates"]}
    assert TEMPORARY_GATES <= gates
    for gate in temporary["temporary_gates"]:
        assert gate["required_future_proof_before_enabling"]
        assert gate["enabled_now"] is False


def test_l5_evidence_index_is_structural_only() -> None:
    chain = load_json("live_readiness_evidence_index/l5_chain_evidence_map.json")
    strength = load_json("live_readiness_evidence_index/evidence_strength_matrix.json")
    assert MILESTONES <= set(chain["milestone_ids"])
    assert set(strength["allowed_evidence_classes"]) == EVIDENCE_CLASSES
    for row in strength["evidence_strength_by_milestone"].values():
        assert row["evidence_class"] in EVIDENCE_CLASSES
        assert row["semantic_truth_scoring_used"] is False


def test_live_blocker_risk_register() -> None:
    register = load_json("live_blocker_risk_register/live_blocker_risk_register.json")
    mitigation = load_json("live_blocker_risk_register/live_blocker_mitigation_map.json")
    assert BLOCKERS <= set(register["blocker_ids"])
    assert set(mitigation["mitigations"]) >= BLOCKERS
    for blocker in register["blockers"]:
        assert blocker["can_start_l6_execution_without_resolving"] is False


def test_l6_entry_gate_is_design_only_and_non_executing() -> None:
    gate = load_json("l6_meta_development_entry_gate/l6_meta_development_entry_gate.json")
    boundary = load_json("l6_meta_development_entry_gate/l6_non_execution_boundary.json")
    principles = load_json("l6_meta_development_entry_gate/l6_generative_principles.json")
    hardcoding = load_json("l6_meta_development_entry_gate/l6_forbidden_hardcoding_policy.json")
    seeds = load_json("l6_meta_development_entry_gate/l6_seed_hypothesis_policy.json")
    assert gate["decision"] in {
        "allow_l6_design_only",
        "require_more_l5_boundary_work",
        "deny_l6_entry",
    }
    assert gate["decision"] == "allow_l6_design_only"
    denied = set(boundary["denied_actions"])
    assert DENIED_L6_BOUNDARY_PHRASES <= denied
    assert GENERATIVE_PRINCIPLES <= set(principles["principles"])
    assert principles["not_a_fixed_opportunity_list"] is True
    assert any(
        "hard-coding opportunity types as exhaustive categories" == pattern
        for pattern in hardcoding["forbidden_patterns"]
    )
    assert any(
        "treating examples as bounded strategy" == pattern
        for pattern in hardcoding["forbidden_patterns"]
    )
    for seed in seeds["seed_hypotheses"]:
        assert seed["example_only"] is True
        assert seed["not_exhaustive"] is True
        assert seed["not_authorized_for_execution"] is True


def test_system_no_go_decision_packet() -> None:
    packet = load_json("system_no_go_decision_packet/system_no_go_decision_packet.json")
    reasons = load_json("system_no_go_decision_packet/system_no_go_decision_reason_codes.json")
    assert packet["live_execution_decision"] == "no_go"
    assert packet["real_mcp_execution_decision"] == "no_go"
    assert packet["real_canonical_update_decision"] == "no_go"
    assert packet["brain_memory_writeback_decision"] == "no_go"
    assert packet["durable_persistence_decision"] == "no_go"
    assert packet["real_release_decision"] == "no_go"
    assert packet["l6_design_entry_decision"] == "design_only_go"
    assert packet["l6_execution_decision"] == "no_go"
    assert {
        "live_persistence_missing",
        "durable_approval_persistence_missing",
        "real_cieu_persistence_missing",
        "live_mcp_execution_not_proven",
        "external_action_boundary_missing",
        "revenue_execution_boundary_missing",
        "publication_boundary_missing",
        "payment_boundary_missing",
        "full_pytest_issue_unresolved",
        "human_governance_live_approval_missing",
        "legal_compliance_boundary_missing",
    } <= set(reasons["reason_codes"])


def test_live_boundary_cieu_fixture_and_residual_delta() -> None:
    event = load_json("live_boundary_cieu_residual/live_boundary_cieu_event_fixture.json")
    residual = load_json("live_boundary_cieu_residual/live_boundary_residual_delta.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "live_boundary_no_go_framework_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    assert event["real_live_mode_enabled"] is False
    assert event["l6_execution_enabled"] is False
    assert RESIDUAL_CLASSES <= set(residual["residual_classes"])


def test_live_boundary_readiness_blocks_execution_and_allows_design_only_l6() -> None:
    readiness = load_json("live_boundary_readiness/live_boundary_readiness.json")
    for field in [
        "live_capability_domains_classified",
        "no_go_invariants_defined",
        "l5_evidence_index_generated",
        "live_blockers_identified",
        "permanent_vs_temporary_gates_classified",
        "l6_design_entry_gate_generated",
        "l6_non_execution_boundary_defined",
        "l6_forbidden_hardcoding_policy_defined",
        "system_no_go_decision_packet_generated",
        "live_boundary_cieu_fixture_generated",
        "live_execution_still_blocked",
        "real_mcp_execution_still_blocked",
        "real_canonical_update_still_blocked",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "durable_persistence_still_blocked",
        "real_release_still_blocked",
        "revenue_execution_still_blocked",
        "external_action_still_blocked",
        "network_still_blocked",
        "ready_for_l6_meta_development_generative_engine_design",
    ]:
        assert readiness[field] is True
    assert readiness["ready_for_l6_revenue_opportunity_execution"] is False


def test_console_command_surfaces_l5_13_read_model() -> None:
    result = run_command(["python3", "console_read_model/cli/team_console.py", "live-boundary-no-go"])
    assert result.returncode == 0, result.stderr
    assert "L5.13 live boundary no-go framework defined: True" in result.stdout
    assert "L6 design entry: design_only_go" in result.stdout
    assert "L6 revenue execution: no_go" in result.stdout
