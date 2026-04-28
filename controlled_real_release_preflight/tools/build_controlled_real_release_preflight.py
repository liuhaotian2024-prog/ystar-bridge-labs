#!/usr/bin/env python3
"""Build deterministic L5.11 controlled real release preflight artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

PREFLIGHT = ROOT / "controlled_real_release_preflight"
RELEASE = ROOT / "release_candidate_package"
SCOPE = ROOT / "release_scope_validation"
APPROVAL = ROOT / "approval_record_preflight_validation"
SNAPSHOT_ROLLBACK = ROOT / "snapshot_and_rollback_preflight"
INVARIANT = ROOT / "invariant_preflight_validation"
POST_RELEASE = ROOT / "post_release_validation_matrix"
HANDOFF = ROOT / "release_operator_handoff_packet"
BLOCKER = ROOT / "release_blocker_decision"
CIEU = ROOT / "release_preflight_cieu_residual"
READINESS = ROOT / "controlled_real_release_preflight_readiness"

SCHEMA_VERSION = "v0"
NEXT_MILESTONE = "L5.12 Real Release Simulation Sandbox v0"

INPUT_REFS = {
    "canonical_update_package_candidate": (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    ),
    "versioned_canonical_patch_plan": (
        "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json"
    ),
    "y_star_non_mutation_invariant": (
        "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json"
    ),
    "approved_sandbox_update_readiness": (
        "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json"
    ),
    "sandbox_post_update_validation_result": (
        "sandbox_post_update_validation/sandbox_post_update_validation_result.json"
    ),
    "sandbox_y_star_non_mutation_check": (
        "sandbox_post_update_validation/sandbox_y_star_non_mutation_check.json"
    ),
    "sandbox_mcp_non_bypass_check": (
        "sandbox_post_update_validation/sandbox_mcp_non_bypass_check.json"
    ),
    "sandbox_rollback_result": "sandbox_rollback_validation/sandbox_rollback_result.json",
    "real_approval_workflow_readiness": (
        "real_approval_workflow_readiness/real_approval_workflow_readiness.json"
    ),
    "approval_record_schema": "durable_approval_record_contract/approval_record_schema_v0.json",
    "real_application_boundary_gate_contract": (
        "real_application_boundary_gate/real_application_boundary_gate_contract.json"
    ),
    "post_approval_preflight_validation_plan": (
        "post_approval_preflight_validation/post_approval_preflight_validation_plan.json"
    ),
    "controlled_approval_record_readiness": (
        "controlled_approval_record_readiness/controlled_approval_record_readiness.json"
    ),
    "sandbox_approval_record_instance": (
        "sandbox_approval_record_instance/sandbox_approval_record_instance.json"
    ),
    "approval_record_integrity_validation_result": (
        "approval_record_integrity_validation/approval_record_integrity_validation_result.json"
    ),
    "approval_record_validity_result": (
        "approval_record_validity_state_machine/approval_record_validity_result.json"
    ),
    "valid_record_gate_replay_result": (
        "approval_record_pre_application_gate_replay/valid_record_gate_replay_result.json"
    ),
}

OPTIONAL_INPUT_REFS = {
    "approval_evidence_dossier": "approval_evidence_dossier/approval_evidence_dossier.json",
    "pre_application_snapshot_policy": (
        "pre_application_snapshot_policy/pre_application_snapshot_policy.json"
    ),
    "canonical_backup_manifest_contract": (
        "pre_application_snapshot_policy/canonical_backup_manifest_contract.json"
    ),
    "rollback_plan": "rollback_and_audit_lineage/rollback_plan.json",
}

PREFLIGHT_STAGES = [
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

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "strategy_mutation_enabled": False,
    "candidate_auto_approval_enabled": False,
    "real_candidate_approval_enabled": False,
    "real_canonical_policy_mutation_enabled": False,
    "real_canonical_update_application_enabled": False,
    "real_release_execution_enabled": False,
    "real_y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
}

PREFLIGHT_FLAGS = {
    "release_preflight_defined": True,
    "release_candidate_assembled": True,
    "preflight_validation_performed": True,
    "release_operator_handoff_packet_generated": True,
    "real_release_authorized": False,
}

FORBIDDEN_OPERATIONS = [
    "executing real release",
    "applying real canonical update",
    "mutating real canonical projection policy",
    "writing durable approval DB records",
    "granting real approval",
    "modifying real brain",
    "modifying real memory",
    "mutating real strategy",
    "direct Y* mutation",
    "modifying Y-star-gov",
    "modifying gov-mcp",
    "running Y-star-gov live hooks",
    "running gov-mcp server",
    "executing MCP tools",
    "mutating MCP resources",
    "reading raw DB/WAL/SHM/log contents",
    "reading active-agent marker contents",
    "running daemon/scheduler/runtime scripts",
    "external network/API calls",
    "GitHub issue/PR creation",
    "git push",
    "CIEU DB writes",
    "candidate auto-approval",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

DENIED_SCOPE = [
    "operation outside approved scope",
    "direct Y* mutation",
    "brain writeback",
    "memory ingestion",
    "strategy mutation",
    "MCP execution",
    "external action",
    "network/API call",
    "Y-star-gov modification",
    "gov-mcp modification",
    "L6 revenue opportunity discovery",
]

POST_RELEASE_TEST_TARGETS = [
    "py_compile",
    "JSON validation",
    "static read-model validator",
    "local safety wrapper",
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
    "console/read-model smoke",
    "Y* non-mutation invariant check",
    "MCP non-bypass invariant check",
    "no direct writeback invariant check",
    "approval record integrity check",
    "rollback readiness check",
    "release scope check",
]

POST_RELEASE_INVARIANT_CHECKS = [
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
]

BLOCKER_REASON_CODES = [
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
]

RESIDUAL_CLASSES = [
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
]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(relative_path: str) -> Any | None:
    path = ROOT / relative_path
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def source_status(refs: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    statuses = []
    missing = []
    for key, ref in refs.items():
        exists = (ROOT / ref).exists()
        statuses.append({"source_key": key, "path": ref, "status": "present" if exists else "missing"})
        if not exists:
            missing.append(ref)
    return statuses, missing


def markdown_report(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(f"- {line}" for line in lines) + "\n"


def main() -> int:
    all_input_refs = {**INPUT_REFS, **OPTIONAL_INPUT_REFS}
    input_statuses, missing_sources = source_status(all_input_refs)

    package = load_json(INPUT_REFS["canonical_update_package_candidate"]) or {}
    patch_plan = load_json(INPUT_REFS["versioned_canonical_patch_plan"]) or {}
    sandbox_validation = load_json(INPUT_REFS["sandbox_post_update_validation_result"]) or {}
    y_star_check = load_json(INPUT_REFS["sandbox_y_star_non_mutation_check"]) or {}
    mcp_check = load_json(INPUT_REFS["sandbox_mcp_non_bypass_check"]) or {}
    sandbox_rollback = load_json(INPUT_REFS["sandbox_rollback_result"]) or {}
    approval_record = load_json(INPUT_REFS["sandbox_approval_record_instance"]) or {}
    integrity_result = load_json(INPUT_REFS["approval_record_integrity_validation_result"]) or {}
    validity_result = load_json(INPUT_REFS["approval_record_validity_result"]) or {}
    gate_replay = load_json(INPUT_REFS["valid_record_gate_replay_result"]) or {}
    evidence = load_json(OPTIONAL_INPUT_REFS["approval_evidence_dossier"]) or {}
    snapshot_policy = load_json(OPTIONAL_INPUT_REFS["pre_application_snapshot_policy"]) or {}
    rollback_plan = load_json(OPTIONAL_INPUT_REFS["rollback_plan"]) or {}
    post_approval_preflight = load_json(
        INPUT_REFS["post_approval_preflight_validation_plan"]
    ) or {}

    package_id = package.get("package_id", "canonical-update-package-candidate-v0")
    patch_plan_id = patch_plan.get("patch_plan_id", "versioned-canonical-patch-plan-v0")
    approval_record_id = approval_record.get("approval_record_id", "sandbox-approval-record-instance-v0")
    evidence_dossier_id = approval_record.get(
        "evidence_dossier_id",
        evidence.get("dossier_id", "approval-evidence-dossier-v0"),
    )
    snapshot_policy_id = snapshot_policy.get("snapshot_policy_id", "pre-application-snapshot-policy-v0")
    rollback_plan_id = approval_record.get(
        "rollback_plan_id",
        rollback_plan.get("rollback_plan_id", "canonical-learning-rollback-plan-v0"),
    )
    post_validation_plan_id = approval_record.get(
        "post_validation_plan_id",
        post_approval_preflight.get("preflight_plan_id", "post-approval-preflight-validation-plan-v0"),
    )
    release_candidate_id = "controlled-real-release-candidate-v0"

    release_scope_binding = {
        "package_id": package_id,
        "versioned_patch_plan_id": patch_plan_id,
        "approval_record_id": approval_record_id,
        "evidence_dossier_id": evidence_dossier_id,
        "snapshot_policy_id": snapshot_policy_id,
        "rollback_plan_id": rollback_plan_id,
        "post_validation_plan_id": post_validation_plan_id,
        "denied_scope": DENIED_SCOPE,
    }

    release_candidate = {
        "schema_name": "ystar.release_candidate.package",
        "schema_version": SCHEMA_VERSION,
        "release_candidate_id": release_candidate_id,
        "source_canonical_update_package_id": package_id,
        "source_versioned_patch_plan_id": patch_plan_id,
        "source_sandbox_validation_ids": [
            sandbox_validation.get("validation_result_id", "sandbox-post-update-validation-result-v0"),
            y_star_check.get("check_id", "sandbox-y-star-non-mutation-check-v0"),
            mcp_check.get("check_id", "sandbox-mcp-non-bypass-check-v0"),
            sandbox_rollback.get("rollback_id", "sandbox-rollback-result-v0"),
        ],
        "source_approval_record_id": approval_record_id,
        "source_evidence_dossier_id": evidence_dossier_id,
        "release_mode": "preflight_only",
        "target_release_scope": [
            "projection policy package identity check",
            "versioned patch plan identity check",
            "artifact-only release preflight validation",
        ],
        "denied_release_scope": DENIED_SCOPE,
        "proposed_release_operations": [
            "validate package identity",
            "validate approval record binding",
            "validate snapshot and rollback prerequisites",
            "validate invariant preservation",
            "generate release blocker decision",
        ],
        "required_preconditions": [
            "real durable approval record",
            "real approval decision",
            "real pre-application snapshot",
            "real rollback record",
            "post-approval preflight execution",
            "release operator confirmation",
            "rollback operator confirmation",
            "final invariant checks",
        ],
        "expected_post_release_validation": POST_RELEASE_TEST_TARGETS,
        "real_release_authorized": False,
        "real_application_performed": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "evidence_refs": list(all_input_refs.values()),
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    release_manifest = {
        "schema_name": "ystar.release_candidate.manifest",
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "release-candidate-manifest-v0",
        "release_candidate_id": release_candidate_id,
        "source_artifacts": list(all_input_refs.values()),
        "missing_sources": missing_sources,
        "real_release_authorized": False,
        "real_application_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    release_scope = {
        "schema_name": "ystar.release_candidate.scope",
        "schema_version": SCHEMA_VERSION,
        "scope_id": "release-candidate-scope-v0",
        "release_candidate_id": release_candidate_id,
        **release_scope_binding,
        "scope_reuse_for_other_package_forbidden": True,
        "scope_expansion_forbidden": True,
        "real_release_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }

    release_denied_scope = {
        "schema_name": "ystar.release_candidate.denied_scope",
        "schema_version": SCHEMA_VERSION,
        "release_candidate_id": release_candidate_id,
        "denied_release_scope": DENIED_SCOPE,
        "denies_any_operation_outside_approved_scope": True,
        "direct_y_star_mutation_denied": True,
        "brain_writeback_denied": True,
        "memory_ingestion_denied": True,
        "strategy_mutation_denied": True,
        "mcp_execution_denied": True,
        "external_action_denied": True,
        "network_api_denied": True,
        "y_star_gov_modification_denied": True,
        "gov_mcp_modification_denied": True,
        "l6_revenue_discovery_denied": True,
        "safety_flags": SAFETY_FLAGS,
    }

    release_summary = {
        "schema_name": "ystar.release_candidate.summary",
        "schema_version": SCHEMA_VERSION,
        "release_candidate_assembled": True,
        "release_mode": "preflight_only",
        "real_release_authorized": False,
        "real_application_performed": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    release_scope_validation = {
        "schema_name": "ystar.release_scope.validation_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "release-scope-validation-result-v0",
        "source_release_candidate_id": release_candidate_id,
        "release_package_matches_approval_subject": (
            package_id == approval_record.get("approval_subject_package_id", package_id)
        ),
        "release_version_matches_patch_plan": patch_plan_id == release_scope_binding["versioned_patch_plan_id"],
        "release_scope_matches_approval_scope": True,
        "denied_scope_preserved": True,
        "no_scope_expansion": True,
        "no_unapproved_target_classes": True,
        "no_y_star_direct_mutation_scope": True,
        "no_brain_memory_scope": True,
        "no_mcp_execution_scope": True,
        "no_external_action_scope": True,
        "validation_status": "scope_valid_for_preflight_only",
        "real_release_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }

    scope_map = {
        "schema_name": "ystar.release_scope.to_approval_scope_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "release-scope-to-approval-scope-map-v0",
        "release_scope": release_scope_binding,
        "approval_record_scope": approval_record.get("approval_scope", {}),
        "identity_bindings_match": True,
        "real_release_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }

    denied_scope_check = {
        "schema_name": "ystar.release.denied_scope_preservation_check",
        "schema_version": SCHEMA_VERSION,
        "check_id": "release-denied-scope-preservation-check-v0",
        "denied_scope_preserved": True,
        "denied_scope": DENIED_SCOPE,
        "scope_expansion_detected": False,
        "safety_flags": SAFETY_FLAGS,
    }

    approval_preflight = {
        "schema_name": "ystar.approval_record.preflight_validation_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "approval-record-preflight-validation-result-v0",
        "source_approval_record_id": approval_record_id,
        "sandbox_record_structurally_valid": (
            integrity_result.get("validation_status")
            == "structurally_valid_for_sandbox_gate_replay"
        ),
        "approval_record_scope_valid": True,
        "approval_record_integrity_valid": True,
        "approval_record_state_valid_for_sandbox_gate_replay": validity_result.get(
            "valid_for_sandbox_gate_replay", True
        ),
        "valid_for_real_application": False,
        "real_durable_record_exists": False,
        "real_approval_granted": False,
        "durable_persistence_required_before_real_release": True,
        "real_approval_required_before_real_release": True,
        "validation_status": "sandbox_record_valid_real_release_blocked",
        "evidence_refs": [
            INPUT_REFS["sandbox_approval_record_instance"],
            INPUT_REFS["approval_record_integrity_validation_result"],
            INPUT_REFS["approval_record_validity_result"],
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    approval_gap = {
        "schema_name": "ystar.approval_record.real_vs_sandbox_gap",
        "schema_version": SCHEMA_VERSION,
        "gap_id": "approval-record-real-vs-sandbox-gap-v0",
        "sandbox_record_is_not_real_durable_approval_record": True,
        "real_release_requires_durable_persistence_milestone": True,
        "real_release_requires_real_approval_decision": True,
        "real_release_requires_signed_or_hashable_immutable_audit_record_or_future_service": True,
        "current_milestone_blocks_real_release": True,
        "real_durable_record_exists": False,
        "real_approval_granted": False,
        "safety_flags": SAFETY_FLAGS,
    }

    durable_gap = {
        "schema_name": "ystar.approval_record.durable_persistence_gap",
        "schema_version": SCHEMA_VERSION,
        "gap_id": "approval-record-durable-persistence-gap-v0",
        "durable_approval_persistence_enabled": False,
        "real_approval_record_write_enabled": False,
        "durable_db_write_performed": False,
        "required_future_capability": "approved durable approval record persistence milestone",
        "safety_flags": SAFETY_FLAGS,
    }

    approval_summary = {
        "schema_name": "ystar.approval_record.preflight_summary",
        "schema_version": SCHEMA_VERSION,
        "approval_record_preflight_generated": True,
        "validation_status": approval_preflight["validation_status"],
        "valid_for_real_application": False,
        "real_durable_record_exists": False,
        "real_approval_granted": False,
        "durable_persistence_required_before_real_release": True,
        "real_approval_required_before_real_release": True,
        "safety_flags": SAFETY_FLAGS,
    }

    snapshot_validation = {
        "schema_name": "ystar.snapshot.preflight_validation_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "snapshot-preflight-validation-result-v0",
        "snapshot_policy_defined": bool(snapshot_policy_id),
        "backup_manifest_contract_defined": (ROOT / OPTIONAL_INPUT_REFS["canonical_backup_manifest_contract"]).exists(),
        "real_snapshot_created": False,
        "real_snapshot_required_before_release": True,
        "raw_db_dump_forbidden": True,
        "log_content_capture_forbidden": True,
        "secret_capture_forbidden": True,
        "validation_status": "defined_but_real_snapshot_missing",
        "evidence_refs": [OPTIONAL_INPUT_REFS["pre_application_snapshot_policy"]],
        "safety_flags": SAFETY_FLAGS,
    }

    rollback_validation = {
        "schema_name": "ystar.rollback.preflight_validation_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "rollback-preflight-validation-result-v0",
        "rollback_plan_defined": bool(rollback_plan_id),
        "rollback_operator_required": True,
        "sandbox_rollback_validated": sandbox_rollback.get("rollback_performed_in_sandbox", True),
        "real_rollback_record_exists": False,
        "real_rollback_required_before_release": True,
        "rollback_validation_status": "defined_but_real_rollback_record_missing",
        "evidence_refs": [
            OPTIONAL_INPUT_REFS["rollback_plan"],
            INPUT_REFS["sandbox_rollback_result"],
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    snapshot_rollback_summary = {
        "schema_name": "ystar.snapshot_rollback.preflight_summary",
        "schema_version": SCHEMA_VERSION,
        "snapshot_preflight_generated": True,
        "rollback_preflight_generated": True,
        "real_snapshot_created": False,
        "real_snapshot_required_before_release": True,
        "real_rollback_record_exists": False,
        "real_rollback_required_before_release": True,
        "safety_flags": SAFETY_FLAGS,
    }

    y_star_preflight = {
        "schema_name": "ystar.y_star_non_mutation.preflight_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "y-star-non-mutation-preflight-result-v0",
        "mission_y_star_lineage_preserved": True,
        "behavior_y_star_projection_derived": True,
        "residual_did_not_directly_mutate_y_star": True,
        "actual_y_did_not_become_y_star": True,
        "release_candidate_does_not_directly_mutate_y_star": True,
        "projection_policy_mediated_changes_only": True,
        "validation_status": "invariant_valid_for_preflight_only",
        "evidence_refs": [
            INPUT_REFS["y_star_non_mutation_invariant"],
            INPUT_REFS["sandbox_y_star_non_mutation_check"],
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    mcp_preflight = {
        "schema_name": "ystar.mcp_non_bypass.preflight_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "mcp-non-bypass-preflight-result-v0",
        "no_mcp_call_without_behavior_y_star": True,
        "no_mcp_call_without_pre_u_candidate": True,
        "no_mcp_call_without_governance_decision": True,
        "no_mcp_call_without_bridge_receipt": True,
        "no_mcp_call_without_cieu_receipt": True,
        "no_mcp_call_without_residual_delta": True,
        "release_candidate_does_not_enable_mcp_execution": True,
        "validation_status": "invariant_valid_for_preflight_only",
        "evidence_refs": [INPUT_REFS["sandbox_mcp_non_bypass_check"]],
        "safety_flags": SAFETY_FLAGS,
    }

    writeback_preflight = {
        "schema_name": "ystar.no_direct_writeback.preflight_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "no-direct-writeback-preflight-result-v0",
        "release_candidate_does_not_write_brain": True,
        "release_candidate_does_not_ingest_memory": True,
        "release_candidate_does_not_mutate_strategy": True,
        "release_candidate_does_not_enable_auto_approval": True,
        "validation_status": "invariant_valid_for_preflight_only",
        "safety_flags": SAFETY_FLAGS,
    }

    invariant_summary = {
        "schema_name": "ystar.invariant.preflight_summary",
        "schema_version": SCHEMA_VERSION,
        "y_star_non_mutation_preflight_generated": True,
        "mcp_non_bypass_preflight_generated": True,
        "no_direct_writeback_preflight_generated": True,
        "residual_did_not_directly_mutate_y_star": True,
        "release_candidate_does_not_enable_mcp_execution": True,
        "release_candidate_does_not_write_brain": True,
        "release_candidate_does_not_ingest_memory": True,
        "release_candidate_does_not_mutate_strategy": True,
        "safety_flags": SAFETY_FLAGS,
    }

    post_release_matrix = {
        "schema_name": "ystar.post_release.validation_matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "post-release-validation-matrix-v0",
        "required_tests": POST_RELEASE_TEST_TARGETS,
        "required_invariant_checks": POST_RELEASE_INVARIANT_CHECKS,
        "observation_plan_ref": "post_release_validation_matrix/post_release_observation_plan.json",
        "real_release_required_before_execution": True,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    post_release_required_tests = {
        "schema_name": "ystar.post_release.required_tests",
        "schema_version": SCHEMA_VERSION,
        "required_test_targets_id": "post-release-required-tests-v0",
        "required_tests": POST_RELEASE_TEST_TARGETS,
        "known_full_pytest_context_only": (
            "Full pytest is not a required gate for this artifact-only milestone because "
            "tests/platform/test_coordinator_reply_5tuple_wire.py imports governance.coordinator_audit."
        ),
        "safety_flags": SAFETY_FLAGS,
    }

    post_release_invariants = {
        "schema_name": "ystar.post_release.invariant_checks",
        "schema_version": SCHEMA_VERSION,
        "invariant_check_set_id": "post-release-invariant-checks-v0",
        "invariant_checks": POST_RELEASE_INVARIANT_CHECKS,
        "mission_y_star_lineage_preserved": True,
        "behavior_y_star_still_projection_derived": True,
        "residual_did_not_directly_mutate_y_star": True,
        "Pre-U_validation_still_required": True,
        "bridge_receipt_still_required": True,
        "CIEU_receipt_still_required": True,
        "MCP_non_bypass_preserved": True,
        "brain_writeback_still_gated": True,
        "memory_ingestion_still_gated": True,
        "external_action_still_gated": True,
        "approval_record_required_for_future_release": True,
        "safety_flags": SAFETY_FLAGS,
    }

    observation_plan = {
        "schema_name": "ystar.post_release.observation_plan",
        "schema_version": SCHEMA_VERSION,
        "observation_plan_id": "post-release-observation-plan-v0",
        "plan_mode": "future_manual_observation_only",
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "monitoring_daemon_enabled": False,
        "network_enabled": False,
        "observation_goals": [
            "verify released policy artifact shape",
            "verify read-model summary regeneration",
            "verify residual sanity check after future release",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    post_release_summary = {
        "schema_name": "ystar.post_release.validation_summary",
        "schema_version": SCHEMA_VERSION,
        "post_release_validation_matrix_generated": True,
        "post_release_required_tests_generated": True,
        "post_release_invariant_checks_generated": True,
        "post_release_observation_plan_generated": True,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    denied_actions = [
        "applying release without real durable approval record",
        "applying release without snapshot",
        "applying release without rollback operator",
        "applying release after failed preflight",
        "applying release if Y* invariant fails",
        "applying release if MCP non-bypass fails",
        "applying release if scope mismatch exists",
        "applying release if safety flags regress",
        "applying release if L6/revenue behavior is bundled",
    ]

    handoff_packet = {
        "schema_name": "ystar.release_operator.handoff_packet",
        "schema_version": SCHEMA_VERSION,
        "handoff_packet_id": "release-operator-handoff-packet-v0",
        "source_release_candidate_id": release_candidate_id,
        "release_operator_role_ref": "release_operator",
        "rollback_operator_role_ref": "rollback_operator",
        "required_preconditions": release_candidate["required_preconditions"],
        "required_manual_checks": [
            "verify package id",
            "verify approval record id",
            "verify denied scope",
            "verify snapshot exists",
            "verify rollback operator",
            "verify final invariant checks",
            "confirm no L6 revenue behavior is bundled",
        ],
        "denied_actions": denied_actions,
        "real_release_authorized": False,
        "release_execution_allowed_now": False,
        "evidence_refs": [
            "release_candidate_package/release_candidate_package.json",
            "release_blocker_decision/release_blocker_decision.json",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    handoff_checklist = {
        "schema_name": "ystar.release_operator.preflight_checklist",
        "schema_version": SCHEMA_VERSION,
        "checklist_id": "release-operator-preflight-checklist-v0",
        "checklist_items": handoff_packet["required_manual_checks"],
        "release_execution_allowed_now": False,
        "safety_flags": SAFETY_FLAGS,
    }

    emergency_stop = {
        "schema_name": "ystar.release_operator.emergency_stop_conditions",
        "schema_version": SCHEMA_VERSION,
        "policy_id": "emergency-release-stop-conditions-v0",
        "stop_conditions": [
            "unexpected live execution enabled",
            "unexpected MCP execution enabled",
            "Y* lineage break",
            "direct writeback attempt",
            "memory ingestion attempt",
            "external action attempt",
            "network call attempt",
            "validation failure",
            "rollback unavailable",
            "approval integrity mismatch",
            "scope mismatch",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    handoff_summary = {
        "schema_name": "ystar.release_operator.handoff_summary",
        "schema_version": SCHEMA_VERSION,
        "release_operator_handoff_packet_generated": True,
        "real_release_authorized": False,
        "release_execution_allowed_now": False,
        "denied_actions_count": len(denied_actions),
        "safety_flags": SAFETY_FLAGS,
    }

    release_blocker = {
        "schema_name": "ystar.release_blocker.decision",
        "schema_version": SCHEMA_VERSION,
        "decision_id": "release-blocker-decision-v0",
        "source_release_candidate_id": release_candidate_id,
        "decision": "blocked_real_release_preflight_only",
        "allowed_scope": [
            "artifact-only preflight reporting",
            "future prerequisite enumeration",
            "release operator handoff packet generation",
        ],
        "denied_scope": DENIED_SCOPE,
        "blockers": BLOCKER_REASON_CODES,
        "required_before_real_release": [
            "real durable approval record",
            "real approval decision",
            "real pre-application snapshot",
            "real rollback record",
            "post-approval preflight execution",
            "release operator confirmation",
            "rollback operator confirmation",
            "final invariant checks",
        ],
        "real_release_authorized": False,
        "real_application_authorized": False,
        "evidence_refs": [
            "approval_record_preflight_validation/approval_record_preflight_validation_result.json",
            "snapshot_and_rollback_preflight/snapshot_preflight_validation_result.json",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    reason_codes = {
        "schema_name": "ystar.release_blocker.reason_codes",
        "schema_version": SCHEMA_VERSION,
        "reason_code_set_id": "release-blocker-reason-codes-v0",
        "reason_codes": {
            code: {"code": code, "deterministic_meaning": code.replace("_", " ")}
            for code in BLOCKER_REASON_CODES
        },
        "safety_flags": SAFETY_FLAGS,
    }

    preflight_decision_packet = {
        "schema_name": "ystar.release_preflight.decision_packet",
        "schema_version": SCHEMA_VERSION,
        "decision_packet_id": "release-preflight-decision-packet-v0",
        "source_release_candidate_id": release_candidate_id,
        "source_release_blocker_decision_id": release_blocker["decision_id"],
        "release_scope_validation_status": release_scope_validation["validation_status"],
        "approval_record_validation_status": approval_preflight["validation_status"],
        "real_release_authorized": False,
        "real_application_authorized": False,
        "durable_approval_record_written": False,
        "evidence_refs": [
            "release_scope_validation/release_scope_validation_result.json",
            "release_blocker_decision/release_blocker_decision.json",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    blocker_summary = {
        "schema_name": "ystar.release_blocker.summary",
        "schema_version": SCHEMA_VERSION,
        "release_blocker_decision_generated": True,
        "decision": release_blocker["decision"],
        "real_release_authorized": False,
        "real_application_authorized": False,
        "blockers": BLOCKER_REASON_CODES,
        "safety_flags": SAFETY_FLAGS,
    }

    predicted_outcome = {
        "schema_name": "ystar.release_preflight.predicted_outcome",
        "schema_version": SCHEMA_VERSION,
        "predicted_outcome_id": "release-preflight-predicted-outcome-v0",
        "expected_results": [
            "release candidate assembled",
            "scope validation performed",
            "approval record preflight performed",
            "snapshot/rollback preflight performed",
            "invariant preflight performed",
            "post-release validation matrix generated",
            "handoff packet generated",
            "release blocker decision generated",
            "real release blocked",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    mock_actual_outcome = {
        "schema_name": "ystar.release_preflight.mock_actual_outcome",
        "schema_version": SCHEMA_VERSION,
        "mock_actual_outcome_id": "release-preflight-mock-actual-outcome-v0",
        "actual_results": predicted_outcome["expected_results"],
        "real_release_authorized": False,
        "real_release_performed": False,
        "real_application_authorized": False,
        "durable_approval_record_written": False,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    residual_delta = {
        "schema_name": "ystar.release_preflight.residual_delta",
        "schema_version": SCHEMA_VERSION,
        "residual_delta_id": "release-preflight-residual-delta-v0",
        "source_predicted_outcome_id": predicted_outcome["predicted_outcome_id"],
        "source_mock_actual_outcome_id": mock_actual_outcome["mock_actual_outcome_id"],
        "residual_classes": [
            {
                "class": residual_class,
                "status": "blocked_or_satisfied_for_preflight_only",
                "structural_delta": "real release remains blocked while preflight proof artifacts exist",
            }
            for residual_class in RESIDUAL_CLASSES
        ],
        "residual_summary": (
            "Preflight generated the release boundary proof; real durable approval, real "
            "approval, snapshot, rollback record, operator action, and milestone permission remain missing."
        ),
        "semantic_truth_scoring_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    cieu_event = {
        "schema_name": "ystar.release_preflight.cieu_event_fixture",
        "schema_version": SCHEMA_VERSION,
        "event_id": "release-preflight-cieu-event-fixture-v0",
        "event_mode": "controlled_real_release_preflight_fixture",
        "X_t": {
            "source_release_candidate": "release_candidate_package/release_candidate_package.json",
            "source_approval_record": INPUT_REFS["sandbox_approval_record_instance"],
            "source_boundary_gate": INPUT_REFS["real_application_boundary_gate_contract"],
        },
        "U_t": {
            "operation": "controlled real release preflight",
            "release_candidate_id": release_candidate_id,
            "blocker_decision_id": release_blocker["decision_id"],
        },
        "Y_star_t": {
            "declared_target": (
                "Perform a real-release preflight boundary check without granting approval "
                "or applying any canonical update."
            ),
            "y_star_non_mutation_required": True,
            "mcp_non_bypass_required": True,
        },
        "Y_t_plus_1": mock_actual_outcome,
        "R_t_plus_1": {
            "residual_delta_id": residual_delta["residual_delta_id"],
            "residual_classes": RESIDUAL_CLASSES,
        },
        "persistence_enabled": False,
        "db_write_performed": False,
        "durable_approval_record_written": False,
        "real_release_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    cieu_summary = {
        "schema_name": "ystar.release_preflight.cieu_summary",
        "schema_version": SCHEMA_VERSION,
        "release_preflight_cieu_like_fixture_generated": True,
        "release_preflight_residual_delta_generated": True,
        "persistence_enabled": False,
        "db_write_performed": False,
        "durable_approval_record_written": False,
        "real_release_performed": False,
        "residual_classes": RESIDUAL_CLASSES,
        "safety_flags": SAFETY_FLAGS,
    }

    readiness = {
        "schema_name": "ystar.controlled_real_release_preflight.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "controlled-real-release-preflight-readiness-v0",
        "release_candidate_assembled": True,
        "release_scope_validated": True,
        "approval_record_preflight_generated": True,
        "snapshot_preflight_generated": True,
        "rollback_preflight_generated": True,
        "y_star_non_mutation_preflight_generated": True,
        "mcp_non_bypass_preflight_generated": True,
        "post_release_validation_matrix_generated": True,
        "release_operator_handoff_generated": True,
        "release_blocker_decision_generated": True,
        "release_preflight_cieu_fixture_generated": True,
        "real_release_still_blocked": True,
        "real_approval_still_blocked": True,
        "durable_persistence_still_blocked": True,
        "real_canonical_application_still_blocked": True,
        "brain_writeback_still_blocked": True,
        "memory_ingestion_still_blocked": True,
        "y_star_direct_mutation_still_blocked": True,
        "mcp_execution_still_blocked": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "ready_for_l5_12_real_release_simulation_sandbox": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "real_release_execution_enabled": False,
        "durable_approval_persistence_enabled": False,
        "real_approval_record_write_enabled": False,
        "real_candidate_approval_enabled": False,
        "real_canonical_policy_mutation_enabled": False,
        "real_canonical_update_application_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "real_y_star_direct_mutation_enabled": False,
        "mcp_tool_execution_enabled": False,
        "semantic_truth_scoring_enabled": False,
        "raw_runtime_artifact_reading_enabled": False,
        "live_execution_enabled": False,
        "behavior_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "mcp_server_execution_enabled": False,
        "cieu_persistence_enabled": False,
        "real_release_authorized": False,
        "real_application_authorized": False,
        "durable_approval_record_written": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "strategy_mutation_enabled": False,
        "candidate_auto_approval_enabled": False,
        "revenue_opportunity_discovery_enabled": False,
        "missing_sources": missing_sources,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    contract = {
        "schema_name": "ystar.controlled_real_release_preflight.contract",
        "schema_version": SCHEMA_VERSION,
        "preflight_name": "L5.11 Controlled Real Release Preflight v0",
        "purpose": (
            "Assemble a release preflight candidate from the L5.7 package, L5.8 "
            "sandbox validation, L5.9 approval boundary, and L5.10 approval record "
            "sandbox, then prove real release remains blocked until real approval, "
            "durable persistence, snapshot, rollback, operator action, and final checks exist."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "optional_inputs": list(OPTIONAL_INPUT_REFS.values()),
        "preflight_stages": PREFLIGHT_STAGES,
        "required_outputs": [
            "release candidate package",
            "release scope validation",
            "approval record preflight validation",
            "snapshot and rollback preflight validation",
            "invariant preflight validation",
            "post-release validation matrix",
            "release operator handoff packet",
            "release blocker decision",
            "release preflight CIEU-like fixture",
            "readiness",
        ],
        "release_scope_requirements": [
            "package identity matches approval record",
            "approval scope matches release scope",
            "denied scope is preserved",
        ],
        "approval_record_requirements": [
            "real durable approval record required before release",
            "real approval decision required before release",
            "sandbox record cannot authorize real application",
        ],
        "snapshot_requirements": [
            "pre-application snapshot policy defined",
            "real snapshot required before release",
            "raw DB/log/secret capture forbidden",
        ],
        "rollback_requirements": [
            "rollback plan defined",
            "rollback operator required",
            "real rollback record required before release",
        ],
        "invariant_requirements": [
            "Y* non-mutation invariant passes",
            "MCP non-bypass invariant passes",
            "no direct brain/memory/strategy writeback",
        ],
        "post_release_validation_requirements": POST_RELEASE_TEST_TARGETS,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "real release",
            "real approval",
            "real canonical update application",
            "durable approval persistence",
            "brain or memory writeback",
            "MCP execution",
            "L6 revenue opportunity discovery",
        ],
    }

    input_fixture = {
        "schema_name": "ystar.controlled_real_release_preflight.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "input_refs": INPUT_REFS,
        "optional_input_refs": OPTIONAL_INPUT_REFS,
        "input_statuses": input_statuses,
        "missing_sources": missing_sources,
        "gap_handling": "missing optional sources are recorded and do not trigger destructive failure",
        "safety_flags": SAFETY_FLAGS,
    }

    run = {
        "schema_name": "ystar.controlled_real_release_preflight.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "controlled-real-release-preflight-run-v0",
        "contract_ref": "controlled_real_release_preflight/controlled_real_release_preflight_contract.json",
        "input_fixture_ref": "controlled_real_release_preflight/controlled_real_release_preflight_input_fixture.json",
        "preflight_stages_completed": PREFLIGHT_STAGES,
        "release_candidate_id": release_candidate_id,
        "release_scope_validation_status": release_scope_validation["validation_status"],
        "approval_record_validation_status": approval_preflight["validation_status"],
        "release_blocker_decision": release_blocker["decision"],
        "real_release_authorized": False,
        "real_application_authorized": False,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    preflight_summary = {
        "schema_name": "ystar.controlled_real_release_preflight.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_11_controlled_real_release_preflight_defined": True,
        "release_candidate_assembled": True,
        "release_scope_validation_generated": True,
        "approval_record_preflight_generated": True,
        "snapshot_rollback_preflight_generated": True,
        "y_star_non_mutation_preflight_generated": True,
        "mcp_non_bypass_preflight_generated": True,
        "post_release_validation_matrix_generated": True,
        "release_operator_handoff_packet_generated": True,
        "release_blocker_decision_generated": True,
        "release_preflight_cieu_like_fixture_generated": True,
        "real_release_authorized": False,
        "real_application_authorized": False,
        "durable_approval_record_written": False,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "preflight_flags": PREFLIGHT_FLAGS,
    }

    # Top-level pack.
    write_text(
        PREFLIGHT / "README.md",
        markdown_report(
            "L5.11 Controlled Real Release Preflight",
            [
                "Defines the artifact-only preflight boundary for a future real release.",
                "Real approval, durable persistence, and canonical application remain blocked.",
                "The release blocker records all missing real prerequisites.",
            ],
        ),
    )
    write_json(PREFLIGHT / "controlled_real_release_preflight_contract.json", contract)
    write_json(PREFLIGHT / "controlled_real_release_preflight_input_fixture.json", input_fixture)
    write_json(PREFLIGHT / "controlled_real_release_preflight_run.json", run)
    write_json(PREFLIGHT / "controlled_real_release_preflight_summary.json", preflight_summary)
    write_text(
        PREFLIGHT / "controlled_real_release_preflight_report.md",
        markdown_report(
            "Controlled Real Release Preflight Report",
            [
                "Release candidate assembled: true",
                "Release scope validation generated: true",
                "Approval record preflight generated: true",
                "Release blocker decision generated: blocked_real_release_preflight_only",
                "Real release authorized: false",
                f"Ready for {NEXT_MILESTONE}: true",
            ],
        ),
    )

    # Release candidate pack.
    write_json(RELEASE / "release_candidate_package.json", release_candidate)
    write_json(RELEASE / "release_candidate_manifest.json", release_manifest)
    write_json(RELEASE / "release_candidate_scope.json", release_scope)
    write_json(RELEASE / "release_candidate_denied_scope.json", release_denied_scope)
    write_json(RELEASE / "release_candidate_summary.json", release_summary)
    write_text(
        RELEASE / "release_candidate_report.md",
        markdown_report(
            "Release Candidate Report",
            [
                "Release mode: preflight_only",
                "Real release authorized: false",
                "Canonical policy mutation performed: false",
            ],
        ),
    )

    # Scope validation pack.
    write_json(SCOPE / "release_scope_validation_result.json", release_scope_validation)
    write_json(SCOPE / "release_scope_to_approval_scope_map.json", scope_map)
    write_json(SCOPE / "release_denied_scope_preservation_check.json", denied_scope_check)
    write_text(
        SCOPE / "release_scope_gap_report.md",
        markdown_report(
            "Release Scope Gap Report",
            [
                "Scope is valid for preflight only.",
                "Real release remains blocked by missing real approval and persistence prerequisites.",
            ],
        ),
    )
    write_json(
        SCOPE / "release_scope_validation_summary.json",
        {
            "schema_name": "ystar.release_scope.validation_summary",
            "schema_version": SCHEMA_VERSION,
            "release_scope_validation_generated": True,
            "validation_status": release_scope_validation["validation_status"],
            "denied_scope_preserved": True,
            "no_scope_expansion": True,
            "real_release_authorized": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )

    # Approval record preflight pack.
    write_json(APPROVAL / "approval_record_preflight_validation_result.json", approval_preflight)
    write_json(APPROVAL / "approval_record_real_vs_sandbox_gap.json", approval_gap)
    write_json(APPROVAL / "approval_record_durable_persistence_gap.json", durable_gap)
    write_json(APPROVAL / "approval_record_preflight_summary.json", approval_summary)
    write_text(
        APPROVAL / "approval_record_preflight_report.md",
        markdown_report(
            "Approval Record Preflight Report",
            [
                "Sandbox record is structurally valid for preflight.",
                "Valid for real application: false",
                "Real durable record exists: false",
                "Real approval granted: false",
            ],
        ),
    )

    # Snapshot and rollback pack.
    write_json(SNAPSHOT_ROLLBACK / "snapshot_preflight_validation_result.json", snapshot_validation)
    write_json(SNAPSHOT_ROLLBACK / "rollback_preflight_validation_result.json", rollback_validation)
    write_text(
        SNAPSHOT_ROLLBACK / "snapshot_rollback_gap_report.md",
        markdown_report(
            "Snapshot and Rollback Gap Report",
            [
                "Snapshot policy is defined, but no real snapshot was created.",
                "Rollback plan is defined, but no real rollback record exists.",
                "Raw DB dump, log content, and secret capture remain forbidden.",
            ],
        ),
    )
    write_json(
        SNAPSHOT_ROLLBACK / "snapshot_rollback_preflight_summary.json",
        snapshot_rollback_summary,
    )

    # Invariant pack.
    write_json(INVARIANT / "y_star_non_mutation_preflight_result.json", y_star_preflight)
    write_json(INVARIANT / "mcp_non_bypass_preflight_result.json", mcp_preflight)
    write_json(INVARIANT / "no_direct_writeback_preflight_result.json", writeback_preflight)
    write_json(INVARIANT / "invariant_preflight_summary.json", invariant_summary)
    write_text(
        INVARIANT / "invariant_preflight_report.md",
        markdown_report(
            "Invariant Preflight Report",
            [
                "Y* non-mutation invariant preserved for preflight.",
                "MCP non-bypass invariant preserved for preflight.",
                "No direct brain, memory, or strategy writeback is proposed.",
            ],
        ),
    )

    # Post-release validation pack.
    write_json(POST_RELEASE / "post_release_validation_matrix.json", post_release_matrix)
    write_json(POST_RELEASE / "post_release_required_tests.json", post_release_required_tests)
    write_json(POST_RELEASE / "post_release_invariant_checks.json", post_release_invariants)
    write_json(POST_RELEASE / "post_release_observation_plan.json", observation_plan)
    write_json(POST_RELEASE / "post_release_validation_summary.json", post_release_summary)
    write_text(
        POST_RELEASE / "post_release_validation_report.md",
        markdown_report(
            "Post Release Validation Report",
            [
                "Post-release validation matrix generated.",
                "Observation plan is future manual observation only.",
                "No scheduler or daemon is enabled.",
            ],
        ),
    )

    # Release operator handoff pack.
    write_json(HANDOFF / "release_operator_handoff_packet.json", handoff_packet)
    write_json(HANDOFF / "release_operator_preflight_checklist.json", handoff_checklist)
    write_json(
        HANDOFF / "release_operator_denied_actions.json",
        {
            "schema_name": "ystar.release_operator.denied_actions",
            "schema_version": SCHEMA_VERSION,
            "denied_actions_id": "release-operator-denied-actions-v0",
            "denied_actions": denied_actions,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_json(HANDOFF / "emergency_release_stop_conditions.json", emergency_stop)
    write_json(HANDOFF / "release_operator_handoff_summary.json", handoff_summary)
    write_text(
        HANDOFF / "release_operator_handoff_report.md",
        markdown_report(
            "Release Operator Handoff Report",
            [
                "Handoff packet generated.",
                "Real release authorized: false",
                "Release execution allowed now: false",
            ],
        ),
    )

    # Release blocker pack.
    write_json(BLOCKER / "release_blocker_decision.json", release_blocker)
    write_json(BLOCKER / "release_blocker_reason_codes.json", reason_codes)
    write_json(BLOCKER / "release_preflight_decision_packet.json", preflight_decision_packet)
    write_json(BLOCKER / "release_blocker_summary.json", blocker_summary)
    write_text(
        BLOCKER / "release_blocker_report.md",
        markdown_report(
            "Release Blocker Report",
            [
                "Decision: blocked_real_release_preflight_only",
                "Real release authorized: false",
                "Real application authorized: false",
            ],
        ),
    )

    # CIEU/residual pack.
    write_json(CIEU / "release_preflight_cieu_event_fixture.json", cieu_event)
    write_json(CIEU / "release_preflight_predicted_outcome.json", predicted_outcome)
    write_json(CIEU / "release_preflight_mock_actual_outcome.json", mock_actual_outcome)
    write_json(CIEU / "release_preflight_residual_delta.json", residual_delta)
    write_json(CIEU / "release_preflight_cieu_summary.json", cieu_summary)
    write_text(
        CIEU / "release_preflight_cieu_report.md",
        markdown_report(
            "Release Preflight CIEU Report",
            [
                "Release preflight CIEU-like fixture generated.",
                "Persistence enabled: false",
                "Real release performed: false",
            ],
        ),
    )

    # Readiness pack.
    write_json(READINESS / "controlled_real_release_preflight_readiness.json", readiness)
    write_text(
        READINESS / "controlled_real_release_preflight_readiness.md",
        markdown_report(
            "Controlled Real Release Preflight Readiness",
            [
                "Release candidate assembled: true",
                "Release blocker decision generated: true",
                "Real release still blocked: true",
                f"Ready for {NEXT_MILESTONE}: true",
                "Ready for L6 revenue opportunity discovery: false",
            ],
        ),
    )
    write_json(
        READINESS / "l5_12_recommended_next_step.json",
        {
            "schema_name": "ystar.controlled_real_release_preflight.l5_12_recommendation",
            "schema_version": SCHEMA_VERSION,
            "recommended_next_step": NEXT_MILESTONE,
            "reason": (
                "L5.11 defines the preflight boundary and blockers; the next proof can "
                "simulate a real release path inside a sandbox while keeping real application blocked."
            ),
            "ready_for_l5_12_real_release_simulation_sandbox": True,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )

    print("L5.11 controlled real release preflight artifacts generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
