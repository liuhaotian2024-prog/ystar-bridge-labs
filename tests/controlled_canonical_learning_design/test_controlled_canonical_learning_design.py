from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "controlled_canonical_learning_design"
    / "tools"
    / "build_controlled_canonical_learning_design.py"
)

REQUIRED_DIRECTORIES = [
    "controlled_canonical_learning_design",
    "y_star_non_mutation_invariant",
    "canonical_learning_target_registry",
    "canonical_promotion_evidence_bundle",
    "canonical_promotion_eligibility_gate",
    "canonical_update_package_candidate",
    "versioned_canonical_patch_plan",
    "rollback_and_audit_lineage",
    "post_promotion_validation_plan",
    "dry_run_promotion_decision_fixture",
    "controlled_canonical_learning_readiness",
]

REQUIRED_FILES = [
    "controlled_canonical_learning_design/README.md",
    "controlled_canonical_learning_design/tools/build_controlled_canonical_learning_design.py",
    "controlled_canonical_learning_design/controlled_canonical_learning_contract.json",
    "controlled_canonical_learning_design/controlled_canonical_learning_input_fixture.json",
    "controlled_canonical_learning_design/controlled_canonical_learning_run.json",
    "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
    "controlled_canonical_learning_design/controlled_canonical_learning_report.md",
    "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json",
    "y_star_non_mutation_invariant/residual_to_projection_policy_boundary.json",
    "y_star_non_mutation_invariant/y_star_allowed_change_surface.json",
    "y_star_non_mutation_invariant/y_star_forbidden_change_surface.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_report.md",
    "canonical_learning_target_registry/canonical_learning_target_registry.json",
    "canonical_learning_target_registry/canonical_learning_target_scope_matrix.json",
    "canonical_learning_target_registry/canonical_learning_target_risk_matrix.json",
    "canonical_learning_target_registry/canonical_learning_target_summary.json",
    "canonical_learning_target_registry/canonical_learning_target_report.md",
    "canonical_promotion_evidence_bundle/canonical_promotion_evidence_bundle.json",
    "canonical_promotion_evidence_bundle/source_learning_candidate_index.json",
    "canonical_promotion_evidence_bundle/source_residual_index.json",
    "canonical_promotion_evidence_bundle/source_shadow_effect_index.json",
    "canonical_promotion_evidence_bundle/evidence_completeness_check.json",
    "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
    "canonical_promotion_evidence_bundle/evidence_bundle_report.md",
    "canonical_promotion_eligibility_gate/canonical_promotion_policy.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_eligibility_decision.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_decision_packet.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_denied_scope.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_gate_report.md",
    "canonical_update_package_candidate/canonical_update_package_candidate.json",
    "canonical_update_package_candidate/canonical_update_manifest.json",
    "canonical_update_package_candidate/canonical_update_scope_boundary.json",
    "canonical_update_package_candidate/canonical_update_denied_operations.json",
    "canonical_update_package_candidate/canonical_update_package_summary.json",
    "canonical_update_package_candidate/canonical_update_package_report.md",
    "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json",
    "versioned_canonical_patch_plan/canonical_version_lineage_plan.json",
    "versioned_canonical_patch_plan/canonical_patch_diff_preview.json",
    "versioned_canonical_patch_plan/canonical_patch_application_blocker.json",
    "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
    "versioned_canonical_patch_plan/versioned_patch_plan_report.md",
    "rollback_and_audit_lineage/rollback_plan.json",
    "rollback_and_audit_lineage/rollback_trigger_policy.json",
    "rollback_and_audit_lineage/canonical_learning_audit_lineage_record.json",
    "rollback_and_audit_lineage/canonical_learning_audit_requirements.json",
    "rollback_and_audit_lineage/rollback_audit_summary.json",
    "rollback_and_audit_lineage/rollback_audit_report.md",
    "post_promotion_validation_plan/post_promotion_validation_plan.json",
    "post_promotion_validation_plan/post_promotion_validation_matrix.json",
    "post_promotion_validation_plan/post_promotion_required_test_targets.json",
    "post_promotion_validation_plan/post_promotion_invariant_checks.json",
    "post_promotion_validation_plan/post_promotion_validation_summary.json",
    "post_promotion_validation_plan/post_promotion_validation_report.md",
    "dry_run_promotion_decision_fixture/dry_run_promotion_decision_fixture.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_cieu_event_fixture.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_predicted_outcome.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_mock_actual_outcome.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_residual_delta.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_report.md",
    "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
    "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.md",
    "controlled_canonical_learning_readiness/l5_8_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_shadow_learning_sources",
    "load_review_only_learning_candidates",
    "normalize_learning_candidates",
    "enforce_y_star_non_mutation_invariant",
    "classify_canonical_learning_targets",
    "build_evidence_bundle",
    "run_promotion_eligibility_gate",
    "produce_approval_protocol",
    "generate_canonical_update_package_candidate",
    "generate_versioned_patch_plan",
    "generate_rollback_plan",
    "generate_audit_lineage_record",
    "generate_post_promotion_validation_plan",
    "generate_dry_run_promotion_decision_packet",
    "block_actual_canonical_application",
    "produce_l5_8_recommendation",
]

REQUIRED_TARGETS = {
    "projection_policy",
    "projection_operator_version",
    "behavior_y_star_generation_rule",
    "pre_u_mapping_rule",
    "governance_expectation_mapping",
    "bridge_receipt_requirement",
    "mcp_interface_contract",
    "cieu_receipt_requirement",
    "residual_classification_policy",
    "evidence_collection_policy",
    "review_gate_policy",
    "learning_eligibility_policy",
    "brain_update_policy",
    "memory_ingestion_policy",
    "strategy_update_policy",
}

FALSE_FLAG_FIELDS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "mcp_server_execution_enabled",
    "mcp_tool_execution_enabled",
    "cieu_persistence_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "strategy_mutation_enabled",
    "candidate_auto_approval_enabled",
    "canonical_policy_mutation_enabled",
    "canonical_update_application_enabled",
    "y_star_direct_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "can_be_auto_applied_now",
    "can_mutate_y_star_directly",
    "safe_for_direct_application",
    "approved_for_application",
    "applied",
    "candidate_approved",
    "candidate_applied",
    "canonical_policy_mutation_performed",
    "canonical_update_application_performed",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "strategy_mutation_performed",
    "y_star_direct_mutation_performed",
    "canonical_mutation_performed",
    "brain_memory_mutation_performed",
    "applied_now",
    "canonical_target_files_modified",
    "persistence_enabled",
    "db_write_performed",
    "ready_for_l6_revenue_opportunity_discovery",
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


@pytest.fixture(scope="module", autouse=True)
def generated_controlled_canonical_learning_design() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    assert path.exists(), f"missing file: {relative_path}"
    return json.loads(path.read_text(encoding="utf-8"))


def walk_json(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def assert_false_flags(document: Any) -> None:
    for node in walk_json(document):
        for field in FALSE_FLAG_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"


def test_required_l5_7_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), f"missing directory: {directory}"
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"


def test_all_required_json_artifacts_parse_and_keep_flags_false() -> None:
    for relative_path in JSON_FILES:
        document = load_json(relative_path)
        assert_false_flags(document)


def test_contract_contains_required_stages_and_disabled_flags() -> None:
    contract = load_json("controlled_canonical_learning_design/controlled_canonical_learning_contract.json")
    assert contract["design_stages"] == REQUIRED_STAGES
    for field in [
        "learning_promotion_requirements",
        "canonical_update_requirements",
        "approval_requirements",
        "rollback_requirements",
        "audit_lineage_requirements",
        "post_promotion_validation_requirements",
        "forbidden_operations",
        "non_goals",
    ]:
        assert contract[field]
    assert_false_flags(contract)


def test_input_fixture_references_l5_4_l5_6_learning_shadow_and_mcp_candidates() -> None:
    fixture = load_json("controlled_canonical_learning_design/controlled_canonical_learning_input_fixture.json")
    refs = fixture["input_refs"]
    assert refs["residual_review_gate_decision"] == "residual_review_gate/residual_review_gate_decision.json"
    assert refs["learning_target_classification"] == (
        "learning_target_classifier/learning_target_classification.json"
    )
    assert refs["projection_policy_update_candidate"] == (
        "projection_policy_update_candidate/projection_policy_update_candidate.json"
    )
    assert refs["shadow_projection_policy_patch"] == (
        "shadow_projection_policy_patch/shadow_projection_policy_patch.json"
    )
    assert refs["mcp_learning_candidate"] == "mcp_residual_and_learning_candidate/mcp_learning_candidate.json"
    assert refs["mcp_residual_delta"] == "mcp_residual_and_learning_candidate/mcp_residual_delta.json"


def test_y_star_non_mutation_invariant_and_surfaces() -> None:
    invariant = load_json("y_star_non_mutation_invariant/y_star_non_mutation_invariant.json")
    assert "declared ideal/normative target state" in invariant["y_star_definition"]
    assert invariant["mission_level_y_star_cannot_be_rewritten_by_residual"] is True
    assert invariant["behavior_level_y_star_cannot_be_directly_overwritten_by_residual"] is True
    assert invariant["residual_driven_target_drift_forbidden"] is True
    boundary = load_json("y_star_non_mutation_invariant/residual_to_projection_policy_boundary.json")
    denied = set(boundary["denied_mutation_surfaces"])
    for surface in {
        "mission_y_star_direct_mutation",
        "behavior_y_star_direct_overwrite",
        "brain_direct_writeback",
        "memory_direct_ingestion",
        "canonical_policy_direct_mutation",
        "strategy_direct_mutation",
    }:
        assert surface in denied
    forbidden = load_json("y_star_non_mutation_invariant/y_star_forbidden_change_surface.json")
    forbidden_changes = set(forbidden["forbidden_changes"])
    for change in {
        "residual directly becoming new Y*",
        "actual Y becoming new Y*",
        "automatic target drift",
        "direct mission rewrite",
        "direct canonical policy rewrite",
    }:
        assert change in forbidden_changes


def test_canonical_learning_target_registry_contains_required_targets_and_blocks_auto_apply() -> None:
    registry = load_json("canonical_learning_target_registry/canonical_learning_target_registry.json")
    targets = {target["target_name"]: target for target in registry["target_classes"]}
    assert REQUIRED_TARGETS <= set(targets)
    for target in targets.values():
        assert target["can_be_auto_applied_now"] is False
        assert target["can_mutate_y_star_directly"] is False
        assert target["requires_human_review"] is True
        assert target["requires_governance_review"] is True
        assert target["requires_versioning"] is True
        assert target["requires_rollback_plan"] is True
        assert target["requires_post_update_validation"] is True


def test_evidence_bundle_and_promotion_gate_are_review_only() -> None:
    bundle = load_json("canonical_promotion_evidence_bundle/canonical_promotion_evidence_bundle.json")
    assert bundle["safe_for_direct_application"] is False
    check = load_json("canonical_promotion_evidence_bundle/evidence_completeness_check.json")
    assert check["y_star_non_mutation_invariant_checked"] is True
    assert check["mcp_non_bypass_invariant_checked"] is True
    decision = load_json("canonical_promotion_eligibility_gate/canonical_promotion_eligibility_decision.json")
    assert decision["decision"] in {
        "eligible_for_canonical_update_package_candidate",
        "requires_more_evidence",
        "blocked_from_promotion",
        "context_only_no_promotion",
    }
    assert decision["approved_for_application"] is False
    denied = load_json("canonical_promotion_eligibility_gate/canonical_promotion_denied_scope.json")
    denied_ops = set(denied["denied_operations"])
    for operation in {
        "actual canonical application now",
        "brain writeback now",
        "memory ingestion now",
        "strategy mutation now",
        "direct Y* mutation",
        "live execution",
        "MCP execution",
        "external action",
        "network",
        "candidate approval",
    }:
        assert operation in denied_ops


def test_canonical_update_package_and_patch_plan_are_not_applied() -> None:
    package = load_json("canonical_update_package_candidate/canonical_update_package_candidate.json")
    assert package["approval_status"] == "not_approved"
    assert package["application_status"] == "not_applied"
    for field in [
        "canonical_policy_mutation_performed",
        "brain_writeback_performed",
        "memory_ingestion_performed",
        "strategy_mutation_performed",
        "y_star_direct_mutation_performed",
    ]:
        assert package[field] is False
    boundary = load_json("canonical_update_package_candidate/canonical_update_scope_boundary.json")
    assert boundary["can_be_proposed"]
    assert boundary["cannot_be_applied_now"] is True
    assert boundary["cannot_touch_y_star_directly"] is True
    patch_plan = load_json("versioned_canonical_patch_plan/versioned_canonical_patch_plan.json")
    assert patch_plan["application_mode"] == "blocked_dry_run_plan_only"
    assert patch_plan["applied_now"] is False
    assert (ROOT / "versioned_canonical_patch_plan/canonical_patch_application_blocker.json").exists()


def test_rollback_audit_and_post_promotion_validation_plan() -> None:
    assert (ROOT / "rollback_and_audit_lineage/rollback_plan.json").exists()
    audit = load_json("rollback_and_audit_lineage/canonical_learning_audit_lineage_record.json")
    assert audit["canonical_mutation_performed"] is False
    assert audit["brain_memory_mutation_performed"] is False
    plan = load_json("post_promotion_validation_plan/post_promotion_validation_plan.json")
    required = set(plan["required_validation_targets"])
    for target in {
        "py_compile",
        "JSON validation",
        "static read-model validator",
        "local safety wrapper",
        "L5.0-L5.6 targeted pytest",
        "Y* non-mutation invariant check",
        "MCP non-bypass invariant check",
        "rollback plan check",
        "version lineage check",
    }:
        assert target in required
    invariants = load_json("post_promotion_validation_plan/post_promotion_invariant_checks.json")
    for field in [
        "mission_y_star_lineage_preserved",
        "behavior_y_star_still_projection_derived",
        "residual_did_not_directly_mutate_y_star",
        "Pre-U_validation_still_required",
        "bridge_receipt_still_required",
        "CIEU_receipt_still_required",
        "MCP_non_bypass_preserved",
    ]:
        assert invariants[field] is True


def test_dry_run_promotion_fixture_and_readiness_keep_application_blocked() -> None:
    fixture = load_json("dry_run_promotion_decision_fixture/dry_run_promotion_decision_fixture.json")
    assert fixture["candidate_approved"] is False
    assert fixture["candidate_applied"] is False
    event = load_json("dry_run_promotion_decision_fixture/dry_run_promotion_cieu_event_fixture.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    readiness = load_json("controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json")
    assert readiness["actual_canonical_application_blocked"] is True
    assert readiness["candidate_approval_blocked"] is True
    assert readiness["brain_writeback_blocked"] is True
    assert readiness["memory_ingestion_blocked"] is True
    assert readiness["y_star_direct_mutation_blocked"] is True
    assert readiness["ready_for_l5_8_approved_canonical_update_sandbox"] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_builder_source_avoids_live_external_and_forbidden_file_reads() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    forbidden_snippets = [
        "shell=True",
        "subprocess.run",
        "requests.",
        "urllib.request",
        ".db",
        ".db-wal",
        ".db-shm",
        ".sqlite",
        ".sqlite3",
        ".log",
        "scripts/.logs",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source


def test_console_read_model_integration_passes() -> None:
    build = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert build.returncode == 0, build.stdout + build.stderr
    validate = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validate.returncode == 0, validate.stdout + validate.stderr
    cli = run_command(["python3", "console_read_model/cli/team_console.py", "controlled-canonical-learning"])
    assert cli.returncode == 0, cli.stdout + cli.stderr
    assert "L5.7 controlled canonical learning design defined: True" in cli.stdout
