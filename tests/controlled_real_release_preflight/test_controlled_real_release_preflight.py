from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "controlled_real_release_preflight"
    / "tools"
    / "build_controlled_real_release_preflight.py"
)

REQUIRED_DIRECTORIES = [
    "controlled_real_release_preflight",
    "release_candidate_package",
    "release_scope_validation",
    "approval_record_preflight_validation",
    "snapshot_and_rollback_preflight",
    "invariant_preflight_validation",
    "post_release_validation_matrix",
    "release_operator_handoff_packet",
    "release_blocker_decision",
    "release_preflight_cieu_residual",
    "controlled_real_release_preflight_readiness",
]

REQUIRED_FILES = [
    "controlled_real_release_preflight/README.md",
    "controlled_real_release_preflight/tools/build_controlled_real_release_preflight.py",
    "controlled_real_release_preflight/controlled_real_release_preflight_contract.json",
    "controlled_real_release_preflight/controlled_real_release_preflight_input_fixture.json",
    "controlled_real_release_preflight/controlled_real_release_preflight_run.json",
    "controlled_real_release_preflight/controlled_real_release_preflight_summary.json",
    "controlled_real_release_preflight/controlled_real_release_preflight_report.md",
    "release_candidate_package/release_candidate_package.json",
    "release_candidate_package/release_candidate_manifest.json",
    "release_candidate_package/release_candidate_scope.json",
    "release_candidate_package/release_candidate_denied_scope.json",
    "release_candidate_package/release_candidate_summary.json",
    "release_candidate_package/release_candidate_report.md",
    "release_scope_validation/release_scope_validation_result.json",
    "release_scope_validation/release_scope_to_approval_scope_map.json",
    "release_scope_validation/release_denied_scope_preservation_check.json",
    "release_scope_validation/release_scope_gap_report.md",
    "release_scope_validation/release_scope_validation_summary.json",
    "approval_record_preflight_validation/approval_record_preflight_validation_result.json",
    "approval_record_preflight_validation/approval_record_real_vs_sandbox_gap.json",
    "approval_record_preflight_validation/approval_record_durable_persistence_gap.json",
    "approval_record_preflight_validation/approval_record_preflight_summary.json",
    "approval_record_preflight_validation/approval_record_preflight_report.md",
    "snapshot_and_rollback_preflight/snapshot_preflight_validation_result.json",
    "snapshot_and_rollback_preflight/rollback_preflight_validation_result.json",
    "snapshot_and_rollback_preflight/snapshot_rollback_gap_report.md",
    "snapshot_and_rollback_preflight/snapshot_rollback_preflight_summary.json",
    "invariant_preflight_validation/y_star_non_mutation_preflight_result.json",
    "invariant_preflight_validation/mcp_non_bypass_preflight_result.json",
    "invariant_preflight_validation/no_direct_writeback_preflight_result.json",
    "invariant_preflight_validation/invariant_preflight_summary.json",
    "invariant_preflight_validation/invariant_preflight_report.md",
    "post_release_validation_matrix/post_release_validation_matrix.json",
    "post_release_validation_matrix/post_release_required_tests.json",
    "post_release_validation_matrix/post_release_invariant_checks.json",
    "post_release_validation_matrix/post_release_observation_plan.json",
    "post_release_validation_matrix/post_release_validation_summary.json",
    "post_release_validation_matrix/post_release_validation_report.md",
    "release_operator_handoff_packet/release_operator_handoff_packet.json",
    "release_operator_handoff_packet/release_operator_preflight_checklist.json",
    "release_operator_handoff_packet/release_operator_denied_actions.json",
    "release_operator_handoff_packet/emergency_release_stop_conditions.json",
    "release_operator_handoff_packet/release_operator_handoff_summary.json",
    "release_operator_handoff_packet/release_operator_handoff_report.md",
    "release_blocker_decision/release_blocker_decision.json",
    "release_blocker_decision/release_blocker_reason_codes.json",
    "release_blocker_decision/release_preflight_decision_packet.json",
    "release_blocker_decision/release_blocker_summary.json",
    "release_blocker_decision/release_blocker_report.md",
    "release_preflight_cieu_residual/release_preflight_cieu_event_fixture.json",
    "release_preflight_cieu_residual/release_preflight_predicted_outcome.json",
    "release_preflight_cieu_residual/release_preflight_mock_actual_outcome.json",
    "release_preflight_cieu_residual/release_preflight_residual_delta.json",
    "release_preflight_cieu_residual/release_preflight_cieu_summary.json",
    "release_preflight_cieu_residual/release_preflight_cieu_report.md",
    "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
    "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.md",
    "controlled_real_release_preflight_readiness/l5_12_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_7_canonical_update_package_candidate",
    "load_l5_8_sandbox_update_validation",
    "load_l5_9_real_approval_boundary",
    "load_l5_10_approval_record_sandbox",
    "assemble_release_candidate_package",
    "validate_release_scope_against_approval_scope",
    "validate_approval_record_for_preflight",
    "validate_evidence_dossier_for_release",
    "validate_pre_application_snapshot_requirements",
    "validate_rollback_requirements",
    "validate_y_star_non_mutation_invariant",
    "validate_mcp_non_bypass_invariant",
    "validate_post_release_validation_matrix",
    "validate_safety_flags_no_regression",
    "generate_release_operator_handoff_packet",
    "generate_release_blocker_decision",
    "emit_release_preflight_cieu_like_fixture",
    "produce_l5_12_recommendation",
]

SAFETY_FLAG_FIELDS = {
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
}

FALSE_FIELDS = SAFETY_FLAG_FIELDS | {
    "real_release_authorized",
    "real_application_authorized",
    "real_application_performed",
    "canonical_policy_mutation_performed",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "direct_y_star_mutation_performed",
    "valid_for_real_application",
    "real_durable_record_exists",
    "real_approval_granted",
    "real_snapshot_created",
    "real_rollback_record_exists",
    "release_execution_allowed_now",
    "durable_approval_record_written",
    "real_release_performed",
    "db_write_performed",
    "persistence_enabled",
    "ready_for_l6_revenue_opportunity_discovery",
}

PREFLIGHT_TRUE_FIELDS = {
    "release_preflight_defined",
    "release_candidate_assembled",
    "preflight_validation_performed",
    "release_operator_handoff_packet_generated",
}

REQUIRED_INPUT_REFS = {
    "canonical_update_package_candidate/canonical_update_package_candidate.json",
    "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json",
    "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
    "sandbox_post_update_validation/sandbox_post_update_validation_result.json",
    "sandbox_post_update_validation/sandbox_y_star_non_mutation_check.json",
    "sandbox_post_update_validation/sandbox_mcp_non_bypass_check.json",
    "sandbox_rollback_validation/sandbox_rollback_result.json",
    "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
    "durable_approval_record_contract/approval_record_schema_v0.json",
    "real_application_boundary_gate/real_application_boundary_gate_contract.json",
    "post_approval_preflight_validation/post_approval_preflight_validation_plan.json",
    "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
    "sandbox_approval_record_instance/sandbox_approval_record_instance.json",
    "approval_record_integrity_validation/approval_record_integrity_validation_result.json",
    "approval_record_validity_state_machine/approval_record_validity_result.json",
    "approval_record_pre_application_gate_replay/valid_record_gate_replay_result.json",
}

REASON_CODES = {
    "durable_record_missing",
    "real_approval_missing",
    "real_snapshot_missing",
    "real_rollback_record_missing",
    "release_operator_not_confirmed",
    "milestone_blocks_real_release",
    "persistence_disabled",
    "live_execution_disabled",
    "mcp_execution_disabled",
    "canonical_application_disabled",
    "y_star_direct_mutation_forbidden",
}

RESIDUAL_CLASSES = {
    "release_scope_residual",
    "approval_record_residual",
    "snapshot_residual",
    "rollback_residual",
    "y_star_invariant_residual",
    "mcp_non_bypass_residual",
    "post_release_validation_residual",
    "release_operator_handoff_residual",
    "release_blocker_residual",
    "real_application_blocker_residual",
}

L5_TEST_TARGETS = {
    "tests/field_functional_archaeology/test_field_functional_archaeology.py",
    "tests/mission_field_projection_contract/test_mission_field_projection_contract.py",
    "tests/field_functional_auto_projection_core/test_field_functional_auto_projection_core.py",
    "tests/projection_checked_autonomous_work_cycle/test_projection_checked_autonomous_work_cycle.py",
    "tests/review_gated_shadow_projection_cycle/test_review_gated_shadow_projection_cycle.py",
    "tests/cross_repo_governance_contract_proof/test_cross_repo_governance_contract_proof.py",
    "tests/governed_mcp_dry_run_adapter/test_governed_mcp_dry_run_adapter.py",
    "tests/controlled_canonical_learning_design/test_controlled_canonical_learning_design.py",
    "tests/approved_canonical_update_sandbox/test_approved_canonical_update_sandbox.py",
    "tests/real_approval_workflow_boundary/test_real_approval_workflow_boundary.py",
    "tests/controlled_approval_record_sandbox/test_controlled_approval_record_sandbox.py",
    "tests/controlled_real_release_preflight/test_controlled_real_release_preflight.py",
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
        for key, item in value.items():
            yield key, item
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)


def test_builder_regenerates_artifacts() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stderr


def test_required_directories_and_json_parse() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_FILES:
        assert (ROOT / path).exists(), path
    for path in JSON_FILES:
        load_json(path)


def test_contract_stages_flags_and_inputs() -> None:
    contract = load_json("controlled_real_release_preflight/controlled_real_release_preflight_contract.json")
    assert set(REQUIRED_STAGES).issubset(set(contract["preflight_stages"]))
    assert set(SAFETY_FLAG_FIELDS).issubset(contract["safety_flags"])
    assert all(contract["safety_flags"][field] is False for field in SAFETY_FLAG_FIELDS)
    assert contract["preflight_flags"]["release_preflight_defined"] is True
    assert contract["preflight_flags"]["release_candidate_assembled"] is True
    assert contract["preflight_flags"]["release_operator_handoff_packet_generated"] is True
    assert contract["preflight_flags"]["real_release_authorized"] is False

    fixture = load_json("controlled_real_release_preflight/controlled_real_release_preflight_input_fixture.json")
    refs = set(fixture["input_refs"].values())
    assert REQUIRED_INPUT_REFS.issubset(refs)


def test_no_real_safety_flags_are_enabled() -> None:
    for path in JSON_FILES:
        data = load_json(path)
        for key, value in walk_values(data):
            if key in SAFETY_FLAG_FIELDS:
                assert value is False, f"{path}:{key}"
            if key in PREFLIGHT_TRUE_FIELDS:
                assert value is True, f"{path}:{key}"
            if key == "real_release_authorized":
                assert value is False, f"{path}:{key}"


def test_release_candidate_package_and_scope() -> None:
    candidate = load_json("release_candidate_package/release_candidate_package.json")
    assert candidate["release_mode"] == "preflight_only"
    assert candidate["real_release_authorized"] is False
    assert candidate["real_application_performed"] is False
    assert candidate["canonical_policy_mutation_performed"] is False
    assert candidate["brain_writeback_performed"] is False
    assert candidate["memory_ingestion_performed"] is False
    assert candidate["direct_y_star_mutation_performed"] is False

    scope = load_json("release_candidate_package/release_candidate_scope.json")
    for key in [
        "package_id",
        "versioned_patch_plan_id",
        "approval_record_id",
        "evidence_dossier_id",
        "snapshot_policy_id",
        "rollback_plan_id",
        "post_validation_plan_id",
        "denied_scope",
    ]:
        assert key in scope

    denied = load_json("release_candidate_package/release_candidate_denied_scope.json")
    for key in [
        "direct_y_star_mutation_denied",
        "brain_writeback_denied",
        "memory_ingestion_denied",
        "strategy_mutation_denied",
        "mcp_execution_denied",
        "external_action_denied",
        "network_api_denied",
        "y_star_gov_modification_denied",
        "gov_mcp_modification_denied",
        "l6_revenue_discovery_denied",
    ]:
        assert denied[key] is True


def test_release_scope_and_approval_record_preflight() -> None:
    scope = load_json("release_scope_validation/release_scope_validation_result.json")
    assert scope["validation_status"] in {
        "scope_valid_for_preflight_only",
        "scope_invalid_mismatch",
        "scope_invalid_expansion",
        "scope_invalid_denied_scope_gap",
    }
    assert scope["validation_status"] == "scope_valid_for_preflight_only"
    assert scope["denied_scope_preserved"] is True
    assert scope["no_scope_expansion"] is True

    approval = load_json("approval_record_preflight_validation/approval_record_preflight_validation_result.json")
    assert approval["validation_status"] == "sandbox_record_valid_real_release_blocked"
    assert approval["valid_for_real_application"] is False
    assert approval["real_durable_record_exists"] is False
    assert approval["real_approval_granted"] is False
    assert approval["durable_persistence_required_before_real_release"] is True
    assert approval["real_approval_required_before_real_release"] is True

    gap = load_json("approval_record_preflight_validation/approval_record_real_vs_sandbox_gap.json")
    assert gap["sandbox_record_is_not_real_durable_approval_record"] is True
    assert gap["current_milestone_blocks_real_release"] is True


def test_snapshot_rollback_and_invariant_preflight() -> None:
    snapshot = load_json("snapshot_and_rollback_preflight/snapshot_preflight_validation_result.json")
    assert snapshot["real_snapshot_created"] is False
    assert snapshot["real_snapshot_required_before_release"] is True
    assert snapshot["raw_db_dump_forbidden"] is True
    assert snapshot["log_content_capture_forbidden"] is True
    assert snapshot["secret_capture_forbidden"] is True

    rollback = load_json("snapshot_and_rollback_preflight/rollback_preflight_validation_result.json")
    assert rollback["rollback_plan_defined"] is True
    assert rollback["rollback_operator_required"] is True
    assert rollback["real_rollback_record_exists"] is False
    assert rollback["real_rollback_required_before_release"] is True

    y_star = load_json("invariant_preflight_validation/y_star_non_mutation_preflight_result.json")
    assert y_star["residual_did_not_directly_mutate_y_star"] is True
    assert y_star["actual_y_did_not_become_y_star"] is True
    assert y_star["release_candidate_does_not_directly_mutate_y_star"] is True

    mcp = load_json("invariant_preflight_validation/mcp_non_bypass_preflight_result.json")
    assert mcp["release_candidate_does_not_enable_mcp_execution"] is True

    writeback = load_json("invariant_preflight_validation/no_direct_writeback_preflight_result.json")
    assert writeback["release_candidate_does_not_write_brain"] is True
    assert writeback["release_candidate_does_not_ingest_memory"] is True
    assert writeback["release_candidate_does_not_mutate_strategy"] is True


def test_post_release_validation_matrix() -> None:
    tests = load_json("post_release_validation_matrix/post_release_required_tests.json")
    assert L5_TEST_TARGETS.issubset(set(tests["required_tests"]))
    for required in [
        "py_compile",
        "JSON validation",
        "static read-model validator",
        "local safety wrapper",
        "console/read-model smoke",
        "Y* non-mutation invariant check",
        "MCP non-bypass invariant check",
        "no direct writeback invariant check",
        "approval record integrity check",
        "rollback readiness check",
        "release scope check",
    ]:
        assert required in tests["required_tests"]

    invariants = load_json("post_release_validation_matrix/post_release_invariant_checks.json")
    for key in [
        "mission_y_star_lineage_preserved",
        "behavior_y_star_still_projection_derived",
        "residual_did_not_directly_mutate_y_star",
        "Pre-U_validation_still_required",
        "bridge_receipt_still_required",
        "CIEU_receipt_still_required",
        "MCP_non_bypass_preserved",
        "brain_writeback_still_gated",
        "memory_ingestion_still_gated",
        "external_action_still_gated",
        "approval_record_required_for_future_release",
    ]:
        assert invariants[key] is True


def test_release_operator_handoff_and_blocker() -> None:
    handoff = load_json("release_operator_handoff_packet/release_operator_handoff_packet.json")
    assert handoff["real_release_authorized"] is False
    assert handoff["release_execution_allowed_now"] is False

    denied = load_json("release_operator_handoff_packet/release_operator_denied_actions.json")
    denied_actions = set(denied["denied_actions"])
    for action in [
        "applying release without real durable approval record",
        "applying release without snapshot",
        "applying release without rollback operator",
        "applying release after failed preflight",
        "applying release if Y* invariant fails",
        "applying release if MCP non-bypass fails",
        "applying release if scope mismatch exists",
        "applying release if safety flags regress",
        "applying release if L6/revenue behavior is bundled",
    ]:
        assert action in denied_actions

    blocker = load_json("release_blocker_decision/release_blocker_decision.json")
    assert blocker["decision"] == "blocked_real_release_preflight_only"
    assert blocker["real_release_authorized"] is False
    assert blocker["real_application_authorized"] is False

    reason_codes = load_json("release_blocker_decision/release_blocker_reason_codes.json")
    assert REASON_CODES.issubset(reason_codes["reason_codes"])


def test_release_preflight_cieu_and_residual() -> None:
    event = load_json("release_preflight_cieu_residual/release_preflight_cieu_event_fixture.json")
    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in event
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    assert event["durable_approval_record_written"] is False
    assert event["real_release_performed"] is False

    residual = load_json("release_preflight_cieu_residual/release_preflight_residual_delta.json")
    classes = {item["class"] for item in residual["residual_classes"]}
    assert RESIDUAL_CLASSES.issubset(classes)


def test_readiness_blocks_real_release_and_l6() -> None:
    readiness = load_json(
        "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json"
    )
    for key in [
        "real_release_still_blocked",
        "real_approval_still_blocked",
        "durable_persistence_still_blocked",
        "real_canonical_application_still_blocked",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "y_star_direct_mutation_still_blocked",
        "mcp_execution_still_blocked",
        "y_star_gov_unmodified",
        "gov_mcp_unmodified",
    ]:
        assert readiness[key] is True
    assert readiness["ready_for_l5_12_real_release_simulation_sandbox"] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_false_fields_remain_false_in_key_artifacts() -> None:
    key_files = [
        "release_candidate_package/release_candidate_package.json",
        "approval_record_preflight_validation/approval_record_preflight_validation_result.json",
        "release_blocker_decision/release_blocker_decision.json",
        "release_preflight_cieu_residual/release_preflight_cieu_event_fixture.json",
        "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
    ]
    for path in key_files:
        data = load_json(path)
        for key, value in walk_values(data):
            if key in FALSE_FIELDS:
                assert value is False, f"{path}:{key}"


def test_console_command_reports_release_preflight() -> None:
    result = run_command(["python3", "console_read_model/cli/team_console.py", "real-release-preflight"])
    assert result.returncode == 0, result.stderr
    assert "L5.11 controlled real release preflight defined: True" in result.stdout
    assert "no real release authorized: True" in result.stdout
    assert "ready for L5.12 real release simulation sandbox: True" in result.stdout
