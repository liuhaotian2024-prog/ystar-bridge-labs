from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "real_approval_workflow_boundary"
    / "tools"
    / "build_real_approval_workflow_boundary.py"
)

REQUIRED_DIRECTORIES = [
    "real_approval_workflow_boundary",
    "approval_authority_model",
    "approval_evidence_dossier",
    "durable_approval_record_contract",
    "real_approval_decision_packet_fixture",
    "approval_validity_revocation_policy",
    "pre_application_snapshot_policy",
    "real_application_boundary_gate",
    "post_approval_preflight_validation",
    "manual_approval_runbook",
    "approval_workflow_cieu_audit_fixture",
    "real_approval_workflow_readiness",
]

REQUIRED_FILES = [
    "real_approval_workflow_boundary/README.md",
    "real_approval_workflow_boundary/tools/build_real_approval_workflow_boundary.py",
    "real_approval_workflow_boundary/real_approval_workflow_boundary_contract.json",
    "real_approval_workflow_boundary/real_approval_workflow_input_fixture.json",
    "real_approval_workflow_boundary/real_approval_workflow_run.json",
    "real_approval_workflow_boundary/real_approval_workflow_summary.json",
    "real_approval_workflow_boundary/real_approval_workflow_report.md",
    "approval_authority_model/approval_authority_model.json",
    "approval_authority_model/approval_role_registry.json",
    "approval_authority_model/approval_separation_of_duties_policy.json",
    "approval_authority_model/approval_authority_scope_matrix.json",
    "approval_authority_model/approval_authority_summary.json",
    "approval_authority_model/approval_authority_report.md",
    "approval_evidence_dossier/approval_evidence_dossier.json",
    "approval_evidence_dossier/approval_source_artifact_index.json",
    "approval_evidence_dossier/approval_invariant_check_index.json",
    "approval_evidence_dossier/approval_validation_result_index.json",
    "approval_evidence_dossier/approval_missing_evidence_gap_report.json",
    "approval_evidence_dossier/approval_evidence_summary.json",
    "approval_evidence_dossier/approval_evidence_report.md",
    "durable_approval_record_contract/durable_approval_record_contract.json",
    "durable_approval_record_contract/approval_record_schema_v0.json",
    "durable_approval_record_contract/approval_record_integrity_requirements.json",
    "durable_approval_record_contract/approval_record_storage_policy.json",
    "durable_approval_record_contract/approval_record_summary.json",
    "durable_approval_record_contract/approval_record_report.md",
    "real_approval_decision_packet_fixture/real_approval_decision_packet_fixture.json",
    "real_approval_decision_packet_fixture/real_approval_decision_denied_scope.json",
    "real_approval_decision_packet_fixture/real_approval_decision_gap_report.md",
    "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
    "approval_validity_revocation_policy/approval_validity_policy.json",
    "approval_validity_revocation_policy/approval_expiration_policy.json",
    "approval_validity_revocation_policy/approval_revocation_policy.json",
    "approval_validity_revocation_policy/approval_invalidation_triggers.json",
    "approval_validity_revocation_policy/approval_validity_summary.json",
    "approval_validity_revocation_policy/approval_validity_report.md",
    "pre_application_snapshot_policy/pre_application_snapshot_policy.json",
    "pre_application_snapshot_policy/canonical_backup_manifest_contract.json",
    "pre_application_snapshot_policy/pre_application_state_capture_requirements.json",
    "pre_application_snapshot_policy/snapshot_integrity_requirements.json",
    "pre_application_snapshot_policy/snapshot_policy_summary.json",
    "pre_application_snapshot_policy/snapshot_policy_report.md",
    "real_application_boundary_gate/real_application_boundary_gate_contract.json",
    "real_application_boundary_gate/real_application_precondition_matrix.json",
    "real_application_boundary_gate/real_application_blocker.json",
    "real_application_boundary_gate/real_application_denied_operations.json",
    "real_application_boundary_gate/real_application_boundary_summary.json",
    "real_application_boundary_gate/real_application_boundary_report.md",
    "post_approval_preflight_validation/post_approval_preflight_validation_plan.json",
    "post_approval_preflight_validation/post_approval_preflight_validation_matrix.json",
    "post_approval_preflight_validation/post_approval_required_test_targets.json",
    "post_approval_preflight_validation/post_approval_invariant_checks.json",
    "post_approval_preflight_validation/post_approval_preflight_summary.json",
    "post_approval_preflight_validation/post_approval_preflight_report.md",
    "manual_approval_runbook/manual_approval_runbook.md",
    "manual_approval_runbook/approval_operator_checklist.json",
    "manual_approval_runbook/release_operator_checklist.json",
    "manual_approval_runbook/rollback_operator_checklist.json",
    "manual_approval_runbook/emergency_stop_policy.json",
    "manual_approval_runbook/manual_approval_runbook_summary.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_cieu_event_fixture.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_predicted_outcome.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_mock_actual_outcome.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_residual_delta.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_audit_report.md",
    "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
    "real_approval_workflow_readiness/real_approval_workflow_readiness.md",
    "real_approval_workflow_readiness/l5_10_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_8_sandbox_update_readiness",
    "load_sandbox_update_evidence",
    "load_canonical_update_package_candidate",
    "load_y_star_non_mutation_invariant",
    "define_approval_authority_model",
    "build_approval_evidence_dossier",
    "define_durable_approval_record_contract",
    "generate_real_approval_decision_packet_fixture",
    "define_approval_validity_expiration_and_revocation_policy",
    "define_pre_application_backup_snapshot_policy",
    "define_real_application_boundary_gate",
    "define_post_approval_preflight_validation_plan",
    "define_manual_approval_runbook",
    "emit_approval_workflow_cieu_like_fixture",
    "block_real_approval_and_application",
    "produce_l5_10_recommendation",
]

SAFETY_FALSE_FIELDS = {
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
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "strategy_mutation_enabled",
    "candidate_auto_approval_enabled",
    "real_candidate_approval_enabled",
    "real_canonical_policy_mutation_enabled",
    "real_canonical_update_application_enabled",
    "real_y_star_direct_mutation_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "real_approval_granted",
    "real_application_authorized",
    "real_candidate_approved",
    "real_candidate_applied",
    "approval_record_created_as_durable_record",
    "durable_approval_record_written",
    "durable_db_write_performed",
    "real_canonical_policy_mutation_performed",
    "real_canonical_update_application_performed",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "strategy_mutation_performed",
    "direct_y_star_mutation_performed",
    "mcp_server_started",
    "mcp_tool_called",
    "mcp_resource_mutated",
    "network_called",
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
def generated_real_approval_workflow_boundary() -> None:
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


def flatten_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True).lower()


def assert_safety_false_flags(document: Any) -> None:
    for node in walk_json(document):
        for field in SAFETY_FALSE_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"
        if isinstance(node.get("safety_flags"), dict):
            assert all(value is False for value in node["safety_flags"].values())


def test_required_l5_9_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), f"missing directory: {directory}"
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"


def test_all_required_json_artifacts_parse_and_keep_real_flags_false() -> None:
    for relative_path in JSON_FILES:
        document = load_json(relative_path)
        assert_safety_false_flags(document)


def test_contract_contains_required_stages_and_approval_flags() -> None:
    contract = load_json(
        "real_approval_workflow_boundary/real_approval_workflow_boundary_contract.json"
    )
    assert contract["workflow_stages"] == REQUIRED_STAGES
    assert all(value is False for value in contract["safety_flags"].values())
    flags = contract["approval_flags"]
    assert flags["approval_workflow_defined"] is True
    assert flags["approval_record_contract_defined"] is True
    assert flags["approval_decision_packet_fixture_generated"] is True
    assert flags["real_approval_granted"] is False
    assert flags["real_application_authorized"] is False
    for field in [
        "authority_requirements",
        "approval_record_requirements",
        "approval_validity_requirements",
        "revocation_requirements",
        "pre_application_snapshot_requirements",
        "preflight_validation_requirements",
        "audit_lineage_requirements",
        "forbidden_operations",
        "non_goals",
    ]:
        assert contract[field]


def test_input_fixture_references_l5_7_and_l5_8_sources() -> None:
    fixture = load_json("real_approval_workflow_boundary/real_approval_workflow_input_fixture.json")
    refs = fixture["input_refs"]
    assert refs["canonical_update_package_candidate"] == (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    )
    assert refs["versioned_patch_plan"] == (
        "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json"
    )
    assert refs["y_star_non_mutation_invariant"] == (
        "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json"
    )
    assert refs["rollback_plan"] == "rollback_and_audit_lineage/rollback_plan.json"
    assert refs["post_promotion_validation_plan"] == (
        "post_promotion_validation_plan/post_promotion_validation_plan.json"
    )
    assert refs["approved_sandbox_run"] == (
        "approved_canonical_update_sandbox/approved_canonical_update_sandbox_run.json"
    )
    assert refs["sandbox_post_update_validation_result"] == (
        "sandbox_post_update_validation/sandbox_post_update_validation_result.json"
    )
    assert refs["sandbox_y_star_non_mutation_check"] == (
        "sandbox_post_update_validation/sandbox_y_star_non_mutation_check.json"
    )
    assert refs["sandbox_mcp_non_bypass_check"] == (
        "sandbox_post_update_validation/sandbox_mcp_non_bypass_check.json"
    )
    assert refs["approved_sandbox_update_readiness"] == (
        "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json"
    )


def test_approval_authority_model_and_roles_are_bounded() -> None:
    model = load_json("approval_authority_model/approval_authority_model.json")
    assert model["authority_mode"] == "future_explicit_human_or_governance_approval_required"
    for field in [
        "self_approval_forbidden",
        "agent_auto_approval_forbidden",
        "approval_without_evidence_forbidden",
        "approval_without_rollback_forbidden",
        "approval_without_post_validation_forbidden",
        "approval_without_y_star_non_mutation_check_forbidden",
        "approval_without_mcp_non_bypass_check_forbidden",
    ]:
        assert model[field] is True

    roles = load_json("approval_authority_model/approval_role_registry.json")
    role_ids = {role["role_id"] for role in roles["roles"]}
    assert {
        "owner_or_founder",
        "governance_reviewer",
        "safety_reviewer",
        "release_operator",
        "rollback_operator",
    }.issubset(role_ids)
    assert roles["contains_secrets"] is False
    assert roles["contains_credentials"] is False
    assert roles["contains_private_keys"] is False
    assert roles["contains_tokens"] is False
    for role in roles["roles"]:
        assert role["descriptor_only"] is True
        assert role["secret_material_included"] is False
        assert role["credential_material_included"] is False

    duties = load_json("approval_authority_model/approval_separation_of_duties_policy.json")
    assert duties["proposer_must_not_equal_approver"] is True
    assert duties["rollback_operator_defined_before_application"] is True
    assert duties["approver_must_not_equal_release_operator_for_high_risk_updates"] is True


def test_approval_evidence_dossier_and_invariant_index_are_review_only() -> None:
    dossier = load_json("approval_evidence_dossier/approval_evidence_dossier.json")
    assert dossier["safe_for_approval_review"] is True
    assert dossier["safe_for_direct_application"] is False
    assert dossier["evidence_status"] == "complete_for_approval_review"

    checks = load_json("approval_evidence_dossier/approval_invariant_check_index.json")
    check_names = {check["check_name"] for check in checks["checks"]}
    assert {
        "Y* non-mutation check",
        "mission Y* lineage check",
        "behavior Y* projection-derived check",
        "residual did not directly mutate Y* check",
        "MCP non-bypass check",
        "Pre-U required check",
        "bridge receipt required check",
        "CIEU receipt required check",
        "rollback available check",
        "real canonical unchanged in sandbox check",
    }.issubset(check_names)


def test_durable_approval_record_contract_is_schema_only() -> None:
    contract = load_json("durable_approval_record_contract/durable_approval_record_contract.json")
    assert contract["persistence_enabled_now"] is False
    assert contract["durable_db_write_performed"] is False

    schema = load_json("durable_approval_record_contract/approval_record_schema_v0.json")
    assert {
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
    }.issubset(set(schema["required_fields"]))

    integrity = load_json("durable_approval_record_contract/approval_record_integrity_requirements.json")
    integrity_text = flatten_text(integrity["requirements"])
    for phrase in [
        "no approval without evidence dossier",
        "no approval without rollback plan",
        "no approval without post-validation plan",
        "no approval without explicit scope",
        "no approval without denied scope",
        "no approval without expiration/revocation policy",
    ]:
        assert phrase in integrity_text


def test_real_approval_decision_fixture_denies_real_application() -> None:
    packet = load_json(
        "real_approval_decision_packet_fixture/real_approval_decision_packet_fixture.json"
    )
    assert packet["decision_mode"] == "approval_workflow_boundary_fixture"
    assert packet["approval_decision"] == "not_granted"
    assert packet["real_approval_granted"] is False
    assert packet["real_application_authorized"] is False
    assert packet["approval_record_created_as_durable_record"] is False
    required = set(packet["required_before_real_approval"])
    assert {
        "explicit human/governance approval",
        "durable approval record creation",
        "pre-application backup/snapshot",
        "post-approval preflight validation",
        "rollback operator confirmation",
        "final non-bypass invariant check",
        "final Y* non-mutation check",
    }.issubset(required)

    denied = load_json("real_approval_decision_packet_fixture/real_approval_decision_denied_scope.json")
    denied_text = flatten_text(denied["denied_operations"])
    for phrase in [
        "real application",
        "canonical mutation",
        "brain writeback",
        "memory ingestion",
        "strategy mutation",
        "direct y* mutation",
        "live execution",
        "mcp execution",
        "external action",
        "network/api",
        "l6 revenue discovery",
    ]:
        assert phrase in denied_text


def test_approval_validity_and_snapshot_policies_keep_invariants() -> None:
    validity = load_json("approval_validity_revocation_policy/approval_validity_policy.json")
    assert validity["approval_cannot_be_reused_for_different_package_version_scope"] is True
    assert validity["approval_cannot_override_y_star_non_mutation_invariant"] is True
    assert validity["approval_cannot_override_mcp_non_bypass_invariant"] is True
    assert validity["approval_cannot_override_rollback_requirement"] is True

    triggers = load_json("approval_validity_revocation_policy/approval_invalidation_triggers.json")
    trigger_text = flatten_text(triggers["triggers"])
    for phrase in [
        "target package changed",
        "patch plan changed",
        "evidence dossier changed",
        "validation failed",
        "rollback plan missing",
        "y* lineage violation",
        "mcp non-bypass violation",
        "safety flag regression",
        "external action boundary change",
        "brain/memory boundary change",
        "approval record integrity mismatch",
        "approval expired",
        "approval revoked",
    ]:
        assert phrase in trigger_text

    snapshot = load_json("pre_application_snapshot_policy/pre_application_snapshot_policy.json")
    forbidden = flatten_text(snapshot["forbidden_snapshot_sources"])
    for phrase in [
        "raw db dump reading",
        "log content reading",
        "active-agent marker reading",
        "secret/credential capture",
        "unreviewed memory ingestion",
        "brain content writeback",
    ]:
        assert phrase in forbidden

    backup = load_json("pre_application_snapshot_policy/canonical_backup_manifest_contract.json")
    assert backup["persistence_enabled_now"] is False


def test_real_application_boundary_gate_blocks_now() -> None:
    gate = load_json("real_application_boundary_gate/real_application_boundary_gate_contract.json")
    preconditions = set(gate["required_preconditions"])
    assert {
        "durable approval record exists",
        "approval is valid and unexpired",
        "approval scope matches package scope",
        "evidence dossier complete",
        "pre-application snapshot exists",
        "rollback plan exists",
        "post-approval preflight validation passed",
        "Y* non-mutation invariant passed",
        "MCP non-bypass invariant passed",
        "no safety flag regression",
        "release operator assigned",
        "rollback operator assigned",
    }.issubset(preconditions)
    assert gate["real_application_allowed_now"] is False

    blocker = load_json("real_application_boundary_gate/real_application_blocker.json")
    assert blocker["real_application_blocked_now"] is True
    assert blocker["missing_real_approval_record"] is True
    assert blocker["missing_durable_persistence"] is True
    assert blocker["missing_live_release_protocol"] is True

    denied = load_json("real_application_boundary_gate/real_application_denied_operations.json")
    denied_text = flatten_text(denied["denied_operations"])
    for phrase in [
        "applying patch to real canonical state",
        "writing brain",
        "ingesting memory",
        "mutating strategy",
        "direct y* mutation",
        "enabling live execution",
        "enabling mcp execution",
        "modifying y-star-gov",
        "modifying gov-mcp",
    ]:
        assert phrase in denied_text


def test_post_approval_preflight_validation_plan_records_scoped_tests_and_ci_context() -> None:
    plan = load_json("post_approval_preflight_validation/post_approval_preflight_validation_plan.json")
    validations = flatten_text(plan["required_validations"])
    for phrase in [
        "approval record integrity validation",
        "approval scope validation",
        "package version validation",
        "evidence dossier validation",
        "snapshot validation",
        "rollback validation",
        "py_compile",
        "json validation",
        "static read-model validator",
        "local safety wrapper",
        "l5.0-l5.8 targeted pytest",
        "console/read-model smoke",
        "y* non-mutation invariant check",
        "mcp non-bypass invariant check",
        "no direct writeback invariant check",
        "no direct y* mutation check",
    ]:
        assert phrase in validations

    targets = load_json("post_approval_preflight_validation/post_approval_required_test_targets.json")
    assert "tests/real_approval_workflow_boundary/test_real_approval_workflow_boundary.py" in (
        targets["l5_0_to_l5_9_targeted_pytest"]
    )
    issue = targets["known_unrelated_full_pytest_collection_issue"]
    assert issue["test"] == "tests/platform/test_coordinator_reply_5tuple_wire.py"
    assert issue["issue"] == "imports governance.coordinator_audit"
    assert issue["context_only"] is True
    assert issue["approval_blocker_for_artifact_only_milestone"] is False


def test_manual_runbook_checklists_and_emergency_stop_policy() -> None:
    checklist = load_json("manual_approval_runbook/approval_operator_checklist.json")
    items = set(checklist["review_items"])
    assert {
        "verify package id",
        "verify scope",
        "verify denied scope",
        "verify evidence dossier",
        "verify Y* non-mutation",
        "verify MCP non-bypass",
        "verify rollback",
        "verify snapshot",
        "verify validation plan",
        "verify approval expiration/revocation policy",
        "confirm no L6 revenue execution is bundled",
    }.issubset(items)

    emergency = load_json("manual_approval_runbook/emergency_stop_policy.json")
    trigger_text = flatten_text(emergency["triggers"])
    for phrase in [
        "unexpected live execution enabled",
        "unexpected mcp execution enabled",
        "y* lineage break",
        "direct writeback attempt",
        "memory ingestion attempt",
        "external action attempt",
        "network call attempt",
        "validation failure",
        "rollback unavailable",
        "approval integrity mismatch",
    ]:
        assert phrase in trigger_text


def test_approval_workflow_cieu_fixture_and_residual_are_structural_only() -> None:
    event = load_json("approval_workflow_cieu_audit_fixture/approval_workflow_cieu_event_fixture.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "real_approval_workflow_boundary_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    assert event["durable_approval_record_written"] is False

    residual = load_json("approval_workflow_cieu_audit_fixture/approval_workflow_residual_delta.json")
    assert set(residual["residual_classes"]) == {
        "approval_authority_gap",
        "durable_record_gap",
        "evidence_gap",
        "snapshot_gap",
        "preflight_validation_gap",
        "application_boundary_gap",
        "Y_star_invariant_gap",
        "MCP_non_bypass_gap",
        "live_blocker_residual",
        "real_application_blocker_residual",
    }
    assert residual["deterministic_structural_residual_only"] is True
    assert residual["semantic_truth_scoring_enabled"] is False


def test_readiness_blocks_real_approval_application_persistence_and_l6() -> None:
    readiness = load_json("real_approval_workflow_readiness/real_approval_workflow_readiness.json")
    for field in [
        "approval_authority_model_defined",
        "evidence_dossier_generated",
        "durable_approval_record_contract_defined",
        "approval_decision_packet_fixture_generated",
        "approval_validity_revocation_policy_defined",
        "pre_application_snapshot_policy_defined",
        "real_application_boundary_gate_defined",
        "post_approval_preflight_validation_defined",
        "manual_approval_runbook_generated",
        "approval_workflow_cieu_fixture_generated",
        "real_approval_still_blocked",
        "real_application_still_blocked",
        "durable_approval_persistence_still_blocked",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "y_star_direct_mutation_still_blocked",
        "mcp_execution_still_blocked",
        "y_star_gov_unmodified",
        "gov_mcp_unmodified",
        "ready_for_l5_10_controlled_approval_record_sandbox",
    ]:
        assert readiness[field] is True
    for field in [
        "real_approval_granted",
        "real_application_authorized",
        "approval_record_created_as_durable_record",
        "durable_approval_record_written",
        "ready_for_l6_revenue_opportunity_discovery",
    ]:
        assert readiness[field] is False


def test_console_read_model_real_approval_boundary_command_passes() -> None:
    build = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert build.returncode == 0, build.stdout + build.stderr
    result = run_command(["python3", "console_read_model/cli/team_console.py", "real-approval-boundary"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "L5.9 real approval workflow boundary defined: True" in result.stdout
    assert "no real approval granted: True" in result.stdout
    assert "no durable approval record written: True" in result.stdout
    assert "ready for L6 revenue opportunity discovery: False" in result.stdout
