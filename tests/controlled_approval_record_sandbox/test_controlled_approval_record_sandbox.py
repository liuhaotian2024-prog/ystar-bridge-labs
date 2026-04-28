from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "controlled_approval_record_sandbox"
    / "tools"
    / "build_controlled_approval_record_sandbox.py"
)

REQUIRED_DIRECTORIES = [
    "controlled_approval_record_sandbox",
    "sandbox_approval_record_instance",
    "approval_record_integrity_validation",
    "approval_record_validity_state_machine",
    "expiration_revocation_replay",
    "approval_record_pre_application_gate_replay",
    "approval_record_audit_lineage",
    "approval_record_cieu_residual",
    "controlled_approval_record_readiness",
]

REQUIRED_FILES = [
    "controlled_approval_record_sandbox/README.md",
    "controlled_approval_record_sandbox/tools/build_controlled_approval_record_sandbox.py",
    "controlled_approval_record_sandbox/controlled_approval_record_sandbox_contract.json",
    "controlled_approval_record_sandbox/controlled_approval_record_sandbox_input_fixture.json",
    "controlled_approval_record_sandbox/controlled_approval_record_sandbox_run.json",
    "controlled_approval_record_sandbox/controlled_approval_record_sandbox_summary.json",
    "controlled_approval_record_sandbox/controlled_approval_record_sandbox_report.md",
    "sandbox_approval_record_instance/sandbox_approval_record_instance.json",
    "sandbox_approval_record_instance/sandbox_approval_record_field_map.json",
    "sandbox_approval_record_instance/sandbox_approval_record_scope_binding.json",
    "sandbox_approval_record_instance/sandbox_approval_record_denied_scope_binding.json",
    "sandbox_approval_record_instance/sandbox_approval_record_summary.json",
    "sandbox_approval_record_instance/sandbox_approval_record_report.md",
    "approval_record_integrity_validation/sandbox_approval_record_integrity_hash.json",
    "approval_record_integrity_validation/approval_record_integrity_validation_result.json",
    "approval_record_integrity_validation/approval_record_required_fields_check.json",
    "approval_record_integrity_validation/approval_record_integrity_gap_report.md",
    "approval_record_integrity_validation/approval_record_integrity_summary.json",
    "approval_record_validity_state_machine/approval_record_state_machine.json",
    "approval_record_validity_state_machine/approval_record_state_transition_table.json",
    "approval_record_validity_state_machine/sandbox_approval_record_state_replay.json",
    "approval_record_validity_state_machine/approval_record_validity_result.json",
    "approval_record_validity_state_machine/approval_record_state_machine_summary.json",
    "approval_record_validity_state_machine/approval_record_state_machine_report.md",
    "expiration_revocation_replay/sandbox_expired_record_variant.json",
    "expiration_revocation_replay/sandbox_revoked_record_variant.json",
    "expiration_revocation_replay/sandbox_tampered_record_variant.json",
    "expiration_revocation_replay/sandbox_wrong_scope_record_variant.json",
    "expiration_revocation_replay/sandbox_missing_evidence_record_variant.json",
    "expiration_revocation_replay/invalid_record_gate_results.json",
    "expiration_revocation_replay/expiration_revocation_replay_summary.json",
    "expiration_revocation_replay/expiration_revocation_replay_report.md",
    "approval_record_pre_application_gate_replay/valid_record_gate_replay_result.json",
    "approval_record_pre_application_gate_replay/invalid_record_gate_replay_matrix.json",
    "approval_record_pre_application_gate_replay/approval_record_gate_reason_codes.json",
    "approval_record_pre_application_gate_replay/pre_application_gate_replay_summary.json",
    "approval_record_pre_application_gate_replay/pre_application_gate_replay_report.md",
    "approval_record_audit_lineage/sandbox_approval_record_audit_lineage.json",
    "approval_record_audit_lineage/approval_record_parent_child_lineage.json",
    "approval_record_audit_lineage/approval_record_event_index.json",
    "approval_record_audit_lineage/approval_record_audit_gap_report.md",
    "approval_record_audit_lineage/approval_record_audit_summary.json",
    "approval_record_cieu_residual/approval_record_cieu_event_fixture.json",
    "approval_record_cieu_residual/approval_record_predicted_outcome.json",
    "approval_record_cieu_residual/approval_record_mock_actual_outcome.json",
    "approval_record_cieu_residual/approval_record_residual_delta.json",
    "approval_record_cieu_residual/approval_record_cieu_summary.json",
    "approval_record_cieu_residual/approval_record_cieu_report.md",
    "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
    "controlled_approval_record_readiness/controlled_approval_record_readiness.md",
    "controlled_approval_record_readiness/l5_11_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_9_approval_record_contract",
    "load_l5_9_approval_workflow_boundary",
    "load_l5_9_evidence_dossier",
    "create_sandbox_approval_record_instance",
    "generate_sandbox_integrity_hash_placeholder",
    "validate_approval_record_integrity",
    "validate_approval_record_scope",
    "validate_evidence_bindings",
    "validate_y_star_non_mutation_binding",
    "validate_mcp_non_bypass_binding",
    "validate_expiration_policy",
    "validate_revocation_policy",
    "replay_approval_record_state_machine",
    "generate_invalid_record_variants",
    "replay_pre_application_gate_for_valid_record",
    "replay_pre_application_gate_for_invalid_records",
    "emit_approval_record_cieu_like_fixture",
    "compute_approval_record_residual_delta",
    "produce_l5_11_recommendation",
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
    "real_y_star_direct_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
}

FALSE_FIELDS = SAFETY_FLAG_FIELDS | {
    "durable_persistence_performed",
    "real_approval_granted",
    "real_application_authorized",
    "candidate_auto_approval_performed",
    "canonical_update_applied",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "direct_y_star_mutation_performed",
    "valid_for_real_application",
    "real_application_performed",
    "durable_approval_record_written",
    "db_write_performed",
    "persistence_enabled",
    "ready_for_l6_revenue_opportunity_discovery",
}

SANDBOX_TRUE_FIELDS = {
    "sandbox_approval_record_created",
    "sandbox_integrity_validation_performed",
    "sandbox_state_machine_replayed",
    "sandbox_gate_replay_performed",
    "sandbox_invalid_record_tests_generated",
}

SCHEMA_FIELDS = [
    "approval_record_id",
    "approval_subject_package_id",
    "approval_scope",
    "denied_scope",
    "approval_decision",
    "approval_mode",
    "approver_role_refs",
    "proposer_ref",
    "reviewer_ref",
    "release_operator_ref",
    "rollback_operator_ref",
    "evidence_dossier_id",
    "y_star_invariant_check_id",
    "mcp_non_bypass_check_id",
    "post_validation_plan_id",
    "rollback_plan_id",
    "approval_timestamp_placeholder",
    "expiration_policy_ref",
    "revocation_policy_ref",
    "integrity_hash_placeholder",
    "parent_record_ref",
    "audit_lineage_refs",
    "application_status",
    "safety_flags",
]

REQUIRED_STATES = {
    "draft",
    "pending_review",
    "sandbox_valid_for_gate_replay",
    "real_approval_required",
    "expired",
    "revoked",
    "invalidated",
    "consumed_by_application",
    "superseded",
}

INVALID_VARIANT_FILES = {
    "expired_record": "expiration_revocation_replay/sandbox_expired_record_variant.json",
    "revoked_record": "expiration_revocation_replay/sandbox_revoked_record_variant.json",
    "tampered_record": "expiration_revocation_replay/sandbox_tampered_record_variant.json",
    "wrong_scope_record": "expiration_revocation_replay/sandbox_wrong_scope_record_variant.json",
    "missing_evidence_record": (
        "expiration_revocation_replay/sandbox_missing_evidence_record_variant.json"
    ),
}

REASON_CODES = {
    "missing_required_field",
    "scope_mismatch",
    "denied_scope_missing",
    "evidence_missing",
    "expired",
    "revoked",
    "tampered_integrity",
    "invariant_missing",
    "rollback_missing",
    "post_validation_missing",
    "durable_record_missing_for_real_application",
    "real_approval_not_granted",
    "real_application_blocked_by_milestone_boundary",
}

EVENT_TYPES = {
    "record_created_in_sandbox",
    "integrity_validated",
    "scope_validated",
    "state_replayed",
    "invalid_variant_generated",
    "gate_replayed",
    "invalid_variant_blocked",
    "cieu_fixture_emitted",
}

RESIDUAL_CLASSES = {
    "approval_record_integrity_residual",
    "approval_record_scope_residual",
    "evidence_binding_residual",
    "expiration_revocation_residual",
    "state_machine_residual",
    "pre_application_gate_residual",
    "audit_lineage_residual",
    "durable_persistence_blocker_residual",
    "real_approval_blocker_residual",
    "real_application_blocker_residual",
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
def generated_controlled_approval_record_sandbox() -> None:
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


def assert_real_safety_flags_false(document: Any) -> None:
    for node in walk_json(document):
        for field in FALSE_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"
        if isinstance(node.get("safety_flags"), dict):
            if not all(isinstance(value, bool) for value in node["safety_flags"].values()):
                continue
            assert set(SAFETY_FLAG_FIELDS).issubset(node["safety_flags"])
            assert all(value is False for value in node["safety_flags"].values())


def test_required_l5_10_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), f"missing directory: {directory}"
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"


def test_all_required_json_artifacts_parse_and_keep_real_flags_false() -> None:
    for relative_path in JSON_FILES:
        document = load_json(relative_path)
        assert_real_safety_flags_false(document)


def test_contract_contains_required_stages_flags_and_boundaries() -> None:
    contract = load_json(
        "controlled_approval_record_sandbox/controlled_approval_record_sandbox_contract.json"
    )
    assert contract["sandbox_stages"] == REQUIRED_STAGES
    assert set(SAFETY_FLAG_FIELDS).issubset(contract["safety_flags"])
    assert all(value is False for value in contract["safety_flags"].values())
    assert set(SANDBOX_TRUE_FIELDS).issubset(contract["sandbox_flags"])
    assert all(value is True for value in contract["sandbox_flags"].values())
    for forbidden in [
        "writing durable approval DB records",
        "granting real approval",
        "applying real canonical update",
        "direct Y* mutation",
        "executing MCP tools",
        "L6 revenue opportunity discovery",
    ]:
        assert forbidden in contract["forbidden_operations"]


def test_input_fixture_references_l5_9_and_prior_sources() -> None:
    fixture = load_json(
        "controlled_approval_record_sandbox/controlled_approval_record_sandbox_input_fixture.json"
    )
    refs = {**fixture["input_refs"], **fixture["optional_input_refs"]}
    for key in [
        "durable_approval_record_contract",
        "approval_record_schema",
        "approval_record_integrity_requirements",
        "approval_record_storage_policy",
        "real_approval_decision_packet_fixture",
        "approval_validity_policy",
        "approval_expiration_policy",
        "approval_revocation_policy",
        "approval_invalidation_triggers",
        "approval_evidence_dossier",
        "approval_invariant_check_index",
        "real_application_boundary_gate_contract",
        "real_application_blocker",
        "post_approval_preflight_validation_plan",
        "approval_operator_checklist",
        "real_approval_workflow_readiness",
        "approved_sandbox_update_readiness",
        "canonical_update_package_candidate",
        "y_star_non_mutation_invariant",
        "versioned_patch_plan",
        "rollback_plan",
    ]:
        assert key in refs


def test_sandbox_approval_record_instance_schema_fields_and_blockers() -> None:
    record = load_json("sandbox_approval_record_instance/sandbox_approval_record_instance.json")
    for field in SCHEMA_FIELDS:
        assert field in record
    assert record["record_mode"] == "sandbox_only"
    assert record["approval_decision"] == "sandbox_valid_for_gate_replay_only"
    assert record["approval_mode"] == "sandbox_approval_record_fixture"
    assert record["application_status"] == "not_applied"
    assert record["durable_persistence_performed"] is False
    assert record["real_approval_granted"] is False
    assert record["real_application_authorized"] is False
    assert record["sandbox_gate_replay_authorized"] is True
    assert record["candidate_auto_approval_performed"] is False
    assert record["canonical_update_applied"] is False
    assert record["brain_writeback_performed"] is False
    assert record["memory_ingestion_performed"] is False
    assert record["direct_y_star_mutation_performed"] is False


def test_scope_binding_exact_package_patch_evidence_rollback_validation_and_denied_scope() -> None:
    binding = load_json("sandbox_approval_record_instance/sandbox_approval_record_scope_binding.json")
    assert binding["exact_package_id"] == "canonical-update-package-candidate-v0"
    assert binding["exact_versioned_patch_plan_id"] == "versioned-canonical-patch-plan-v0"
    assert binding["exact_evidence_dossier_id"] == "approval-evidence-dossier-v0"
    assert binding["exact_rollback_plan_id"]
    assert binding["exact_post_validation_plan_id"]
    assert binding["exact_denied_scope"]
    assert binding["approval_cannot_be_reused_for_other_package_version_or_scope"] is True
    assert binding["scope_valid_for_sandbox_gate_replay_only"] is True
    assert binding["valid_for_real_application"] is False


def test_integrity_validation_and_required_field_check() -> None:
    result = load_json(
        "approval_record_integrity_validation/approval_record_integrity_validation_result.json"
    )
    assert result["validation_status"] == "structurally_valid_for_sandbox_gate_replay"
    assert result["all_required_fields_present"] is True
    assert result["scope_present"] is True
    assert result["denied_scope_present"] is True
    assert result["evidence_dossier_present"] is True
    assert result["rollback_plan_present"] is True
    assert result["post_validation_plan_present"] is True
    assert result["expiration_policy_present"] is True
    assert result["revocation_policy_present"] is True
    assert result["integrity_hash_placeholder_present"] is True
    assert result["durable_persistence_not_performed"] is True
    checks = load_json("approval_record_integrity_validation/approval_record_required_fields_check.json")
    assert checks["all_required_fields_present"] is True
    for field in SCHEMA_FIELDS:
        assert checks["field_results"][field] is True


def test_validity_state_machine_includes_required_states_and_sandbox_replay_only() -> None:
    state_machine = load_json("approval_record_validity_state_machine/approval_record_state_machine.json")
    assert REQUIRED_STATES.issubset(set(state_machine["states"]))
    replay = load_json(
        "approval_record_validity_state_machine/sandbox_approval_record_state_replay.json"
    )
    assert replay["current_sandbox_state"] == "sandbox_valid_for_gate_replay"
    assert replay["transitioned_to_real_approved"] is False
    assert replay["transitioned_to_real_consumed_by_application"] is False
    assert "sandbox_valid_for_gate_replay -> real_approved" in replay["transitions_not_taken"]
    validity = load_json("approval_record_validity_state_machine/approval_record_validity_result.json")
    assert validity["valid_for_sandbox_gate_replay"] is True
    assert validity["valid_for_real_application"] is False
    assert validity["real_approval_required_before_application"] is True
    assert validity["durable_record_required_before_real_application"] is True


def test_expired_revoked_tampered_wrong_scope_and_missing_evidence_variants_are_blocked() -> None:
    for variant_type, relative_path in INVALID_VARIANT_FILES.items():
        variant = load_json(relative_path)
        assert variant["variant_type"] == variant_type
        assert variant["expected_gate_result"] == "blocked"
        assert variant["valid_for_sandbox_gate_replay"] is False
        assert variant["valid_for_real_application"] is False
        assert variant["deterministic_reason_codes"]
    results = load_json("expiration_revocation_replay/invalid_record_gate_results.json")
    assert results["all_invalid_variants_blocked"] is True
    assert set(results["gate_results"]) == set(INVALID_VARIANT_FILES)
    for result in results["gate_results"].values():
        assert result["gate_result"] == "blocked"
        assert result["reason_codes"]


def test_valid_and_invalid_pre_application_gate_replays() -> None:
    valid = load_json("approval_record_pre_application_gate_replay/valid_record_gate_replay_result.json")
    assert valid["gate_result"] == "sandbox_gate_replay_passed_real_application_still_blocked"
    assert valid["real_application_authorized"] is False
    assert valid["sandbox_pre_application_replay_authorized"] is True
    assert valid["durable_real_record_required_before_real_application"] is True
    assert valid["post_approval_preflight_required"] is True
    assert valid["snapshot_required"] is True
    assert valid["rollback_required"] is True
    assert valid["y_star_non_mutation_check_required"] is True
    assert valid["mcp_non_bypass_check_required"] is True

    matrix = load_json(
        "approval_record_pre_application_gate_replay/invalid_record_gate_replay_matrix.json"
    )
    assert matrix["all_invalid_variants_blocked"] is True
    assert set(matrix["invalid_record_results"]) == set(INVALID_VARIANT_FILES)
    for result in matrix["invalid_record_results"].values():
        assert result["gate_result"] == "blocked"
        assert result["real_application_authorized"] is False
        assert result["sandbox_pre_application_replay_authorized"] is False

    reason_codes = load_json(
        "approval_record_pre_application_gate_replay/approval_record_gate_reason_codes.json"
    )
    assert REASON_CODES.issubset(set(reason_codes["reason_codes"]))


def test_audit_lineage_and_event_index_are_sandbox_only() -> None:
    lineage = load_json("approval_record_audit_lineage/sandbox_approval_record_audit_lineage.json")
    assert lineage["durable_persistence_performed"] is False
    assert lineage["real_approval_granted"] is False
    assert lineage["real_application_performed"] is False
    assert len(lineage["generated_record_variants"]) == len(INVALID_VARIANT_FILES)
    event_index = load_json("approval_record_audit_lineage/approval_record_event_index.json")
    assert EVENT_TYPES.issubset(set(event_index["event_types"]))


def test_approval_record_cieu_fixture_and_residual_delta() -> None:
    fixture = load_json("approval_record_cieu_residual/approval_record_cieu_event_fixture.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in fixture
    assert fixture["event_mode"] == "approval_record_sandbox_fixture"
    assert fixture["persistence_enabled"] is False
    assert fixture["db_write_performed"] is False
    assert fixture["durable_approval_record_written"] is False
    residual = load_json("approval_record_cieu_residual/approval_record_residual_delta.json")
    classes = {item["class"] for item in residual["residual_classes"]}
    assert RESIDUAL_CLASSES == classes


def test_readiness_marks_real_paths_blocked_and_l6_disabled() -> None:
    readiness = load_json("controlled_approval_record_readiness/controlled_approval_record_readiness.json")
    for field in [
        "sandbox_approval_record_created",
        "integrity_validation_generated",
        "scope_validation_generated",
        "evidence_binding_validation_generated",
        "validity_state_machine_generated",
        "expiration_revocation_replay_generated",
        "valid_record_gate_replay_generated",
        "invalid_record_gate_blocking_generated",
        "audit_lineage_generated",
        "cieu_fixture_generated",
        "durable_persistence_still_blocked",
        "real_approval_still_blocked",
        "real_application_still_blocked",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "y_star_direct_mutation_still_blocked",
        "mcp_execution_still_blocked",
        "y_star_gov_unmodified",
        "gov_mcp_unmodified",
        "ready_for_l5_11_controlled_real_release_preflight",
        "sandbox_approval_record_lifecycle_artifacts_only",
    ]:
        assert readiness[field] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False
    assert readiness["durable_approval_record_written"] is False
    assert readiness["real_approval_granted"] is False
    assert readiness["real_application_authorized"] is False


def test_cli_approval_record_sandbox_command_passes() -> None:
    run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    result = run_command(["python3", "console_read_model/cli/team_console.py", "approval-record-sandbox"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "L5.10 controlled approval record sandbox defined" in result.stdout
    assert "ready for L5.11 controlled real release preflight: True" in result.stdout
