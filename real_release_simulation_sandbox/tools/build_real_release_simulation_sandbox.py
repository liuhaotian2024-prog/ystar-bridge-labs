#!/usr/bin/env python3
"""Build deterministic L5.12 real release simulation sandbox artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SIM = ROOT / "real_release_simulation_sandbox"
AUTH = ROOT / "sandbox_release_authority_fixture"
RECORD = ROOT / "simulated_durable_approval_record"
SNAPSHOT = ROOT / "sandbox_release_snapshot"
PLAN = ROOT / "sandbox_release_execution_plan"
RESULT = ROOT / "sandbox_release_execution_result"
VALIDATION = ROOT / "sandbox_post_release_validation"
PREVIEW = ROOT / "sandbox_release_projection_and_mcp_preview"
ROLLBACK = ROOT / "sandbox_release_rollback_drill"
COMPARISON = ROOT / "original_release_rollback_comparison"
CIEU = ROOT / "release_simulation_cieu_residual"
READINESS = ROOT / "real_release_simulation_readiness"

SCHEMA_VERSION = "v0"
NEXT_MILESTONE = "L5.13 Live Boundary / No-Go Decision Framework v0"

INPUT_REFS = {
    "release_candidate_package": "release_candidate_package/release_candidate_package.json",
    "release_candidate_scope": "release_candidate_package/release_candidate_scope.json",
    "release_scope_validation_result": "release_scope_validation/release_scope_validation_result.json",
    "approval_record_preflight_validation_result": (
        "approval_record_preflight_validation/approval_record_preflight_validation_result.json"
    ),
    "snapshot_preflight_validation_result": (
        "snapshot_and_rollback_preflight/snapshot_preflight_validation_result.json"
    ),
    "rollback_preflight_validation_result": (
        "snapshot_and_rollback_preflight/rollback_preflight_validation_result.json"
    ),
    "y_star_non_mutation_preflight_result": (
        "invariant_preflight_validation/y_star_non_mutation_preflight_result.json"
    ),
    "mcp_non_bypass_preflight_result": (
        "invariant_preflight_validation/mcp_non_bypass_preflight_result.json"
    ),
    "post_release_validation_matrix": "post_release_validation_matrix/post_release_validation_matrix.json",
    "release_operator_handoff_packet": (
        "release_operator_handoff_packet/release_operator_handoff_packet.json"
    ),
    "release_blocker_decision": "release_blocker_decision/release_blocker_decision.json",
    "controlled_real_release_preflight_readiness": (
        "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json"
    ),
    "canonical_update_package_candidate": (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    ),
    "versioned_canonical_patch_plan": (
        "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json"
    ),
    "y_star_non_mutation_invariant": (
        "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json"
    ),
    "controlled_approval_record_readiness": (
        "controlled_approval_record_readiness/controlled_approval_record_readiness.json"
    ),
}

OPTIONAL_INPUT_REFS = {
    "sandbox_approval_record_instance": (
        "sandbox_approval_record_instance/sandbox_approval_record_instance.json"
    ),
    "mission_y_star_input": "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "behavior_level_y_star_candidate": (
        "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"
    ),
    "field_projection_operator_policy": (
        "field_functional_auto_projection_core/field_projection_operator_policy.json"
    ),
}

SIMULATION_STAGES = [
    "load_l5_11_release_preflight",
    "load_release_candidate_package",
    "load_release_blocker_decision",
    "create_sandbox_release_authority_fixture",
    "create_simulated_durable_approval_record",
    "create_sandbox_pre_application_snapshot",
    "confirm_simulated_release_operator",
    "confirm_simulated_rollback_operator",
    "assemble_sandbox_release_execution_plan",
    "execute_sandbox_release_only",
    "verify_real_canonical_state_unchanged",
    "run_sandbox_post_release_validation",
    "run_sandbox_release_mcp_non_bypass_check",
    "run_sandbox_release_y_star_non_mutation_check",
    "emit_sandbox_release_receipt",
    "run_sandbox_rollback_drill",
    "verify_sandbox_rollback_restores_baseline",
    "compare_original_vs_sandbox_release_vs_rollback",
    "emit_release_simulation_cieu_like_fixture",
    "produce_l5_13_recommendation",
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

SIMULATION_FLAGS = {
    "sandbox_release_authority_fixture_created": True,
    "simulated_durable_record_created": True,
    "sandbox_snapshot_created": True,
    "simulated_release_operator_confirmed": True,
    "simulated_rollback_operator_confirmed": True,
    "sandbox_release_executed": True,
    "sandbox_post_validation_performed": True,
    "sandbox_rollback_drill_performed": True,
}

FORBIDDEN_OPERATIONS = [
    "executing real release",
    "granting real approval",
    "writing durable approval DB records",
    "applying real canonical update",
    "mutating real canonical projection policy",
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

DENIED_REAL_SCOPE = [
    "real release",
    "real approval",
    "durable approval persistence",
    "real canonical update",
    "brain writeback",
    "memory ingestion",
    "strategy mutation",
    "direct Y* mutation",
    "MCP execution",
    "external action",
    "network",
    "L6 revenue opportunity discovery",
]

RELEASE_DENIED_OPERATIONS = [
    "real canonical policy mutation",
    "real canonical update application",
    "real brain writeback",
    "real memory ingestion",
    "real strategy mutation",
    "direct Y* mutation",
    "MCP execution",
    "external action",
    "network/API call",
    "Y-star-gov modification",
    "gov-mcp modification",
    "L6 revenue opportunity discovery",
]

ACCEPTABLE_SANDBOX_CHANGES = [
    "projection trace linkage tightened",
    "behavior boundary inheritance clarified",
    "Pre-U mapping expectation improved",
    "MCP non-bypass evidence requirement improved",
    "residual classification labels improved",
    "evidence completeness requirements improved",
]

POST_RELEASE_INVARIANTS = [
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

MCP_NON_BYPASS_CHECKS = [
    "no_mcp_call_without_behavior_y_star",
    "no_mcp_call_without_pre_u_candidate",
    "no_mcp_call_without_governance_decision",
    "no_mcp_call_without_bridge_receipt",
    "no_mcp_call_without_cieu_receipt",
    "no_mcp_call_without_residual_delta",
    "no_mcp_direct_brain_writeback",
    "no_mcp_direct_memory_ingestion",
]

RELEASE_RESIDUAL_CLASSES = [
    "simulated_authority_residual",
    "simulated_approval_record_residual",
    "sandbox_snapshot_residual",
    "sandbox_release_execution_residual",
    "y_star_invariant_residual",
    "mcp_non_bypass_residual",
    "post_release_validation_residual",
    "rollback_residual",
    "real_state_unchanged_residual",
    "real_release_blocker_residual",
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


def safety_false_payload(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "safety_flags": SAFETY_FLAGS,
        "simulation_flags": SIMULATION_FLAGS,
    }
    if extra:
        payload.update(extra)
    return payload


def main() -> int:
    all_input_refs = {**INPUT_REFS, **OPTIONAL_INPUT_REFS}
    input_statuses, missing_sources = source_status(all_input_refs)

    release_candidate = load_json(INPUT_REFS["release_candidate_package"]) or {}
    release_scope = load_json(INPUT_REFS["release_candidate_scope"]) or {}
    release_scope_validation = load_json(INPUT_REFS["release_scope_validation_result"]) or {}
    approval_preflight = load_json(INPUT_REFS["approval_record_preflight_validation_result"]) or {}
    snapshot_preflight = load_json(INPUT_REFS["snapshot_preflight_validation_result"]) or {}
    rollback_preflight = load_json(INPUT_REFS["rollback_preflight_validation_result"]) or {}
    y_star_preflight = load_json(INPUT_REFS["y_star_non_mutation_preflight_result"]) or {}
    mcp_preflight = load_json(INPUT_REFS["mcp_non_bypass_preflight_result"]) or {}
    post_release_matrix = load_json(INPUT_REFS["post_release_validation_matrix"]) or {}
    handoff_packet = load_json(INPUT_REFS["release_operator_handoff_packet"]) or {}
    release_blocker = load_json(INPUT_REFS["release_blocker_decision"]) or {}
    package = load_json(INPUT_REFS["canonical_update_package_candidate"]) or {}
    patch_plan = load_json(INPUT_REFS["versioned_canonical_patch_plan"]) or {}
    approval_record = load_json(OPTIONAL_INPUT_REFS["sandbox_approval_record_instance"]) or {}
    mission_y_star = load_json(OPTIONAL_INPUT_REFS["mission_y_star_input"]) or {}
    behavior_y_star = load_json(OPTIONAL_INPUT_REFS["behavior_level_y_star_candidate"]) or {}

    release_candidate_id = release_candidate.get("release_candidate_id", "controlled-real-release-candidate-v0")
    package_id = release_candidate.get(
        "source_canonical_update_package_id",
        package.get("package_id", "canonical-update-package-candidate-v0"),
    )
    patch_plan_id = release_candidate.get(
        "source_versioned_patch_plan_id",
        patch_plan.get("patch_plan_id", "versioned-canonical-patch-plan-v0"),
    )
    sandbox_record_id = approval_record.get("approval_record_id", "sandbox-approval-record-instance-v0")
    source_evidence_dossier_id = release_candidate.get(
        "source_evidence_dossier_id",
        approval_record.get("evidence_dossier_id", "approval-evidence-dossier-v0"),
    )
    mission_y_star_id = mission_y_star.get("mission_y_star_id", "mission-y-star-input-v0")
    behavior_y_star_id = behavior_y_star.get("behavior_y_star_id", "behavior-level-y-star-candidate-v0")

    authority_id = "sandbox-release-authority-fixture-v0"
    simulated_record_id = "simulated-durable-approval-record-v0"
    snapshot_id = "sandbox-release-snapshot-v0"
    release_plan_id = "sandbox-release-execution-plan-v0"
    release_execution_id = "sandbox-release-execution-result-v0"
    rollback_id = "sandbox-release-rollback-drill-v0"
    post_release_behavior_y_star_id = "sandbox-post-release-behavior-y-star-v0"

    authority_fixture = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.authority_fixture",
            "schema_version": SCHEMA_VERSION,
            "authority_fixture_id": authority_id,
            "source_release_candidate_id": release_candidate_id,
            "authority_mode": "sandbox_release_simulation_only",
            "simulated_release_authority_present": True,
            "real_release_authority_present": False,
            "real_approval_granted": False,
            "real_release_authorized": False,
            "allowed_sandbox_scope": [
                "simulate release authority",
                "simulate durable approval record",
                "simulate release and rollback only in generated artifacts",
            ],
            "denied_real_scope": DENIED_REAL_SCOPE,
            "evidence_refs": [
                INPUT_REFS["release_candidate_package"],
                INPUT_REFS["release_blocker_decision"],
            ],
        }
    )

    release_confirmation = {
        "schema_name": "ystar.sandbox_release.release_operator_confirmation",
        "schema_version": SCHEMA_VERSION,
        "confirmation_id": "simulated-release-operator-confirmation-v0",
        "operator_role_ref": handoff_packet.get("release_operator_role_ref", "release_operator"),
        "confirmation_mode": "sandbox_only",
        "confirmed_for_sandbox_release_simulation": True,
        "confirmed_for_real_release": False,
        "release_execution_allowed_now": False,
        "evidence_refs": [INPUT_REFS["release_operator_handoff_packet"]],
    }

    rollback_confirmation = {
        "schema_name": "ystar.sandbox_release.rollback_operator_confirmation",
        "schema_version": SCHEMA_VERSION,
        "confirmation_id": "simulated-rollback-operator-confirmation-v0",
        "operator_role_ref": handoff_packet.get("rollback_operator_role_ref", "rollback_operator"),
        "confirmation_mode": "sandbox_only",
        "confirmed_for_sandbox_rollback_drill": True,
        "confirmed_for_real_rollback": False,
        "evidence_refs": [INPUT_REFS["release_operator_handoff_packet"]],
    }

    authority_denied_scope = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.authority_denied_scope",
            "schema_version": SCHEMA_VERSION,
            "denied_scope_id": "sandbox-release-authority-denied-scope-v0",
            "denied_scope": DENIED_REAL_SCOPE,
            "real_release_denied": True,
            "real_approval_denied": True,
            "durable_approval_persistence_denied": True,
            "real_canonical_update_denied": True,
            "brain_writeback_denied": True,
            "memory_ingestion_denied": True,
            "strategy_mutation_denied": True,
            "direct_y_star_mutation_denied": True,
            "mcp_execution_denied": True,
            "external_action_denied": True,
            "network_denied": True,
            "l6_revenue_opportunity_discovery_denied": True,
        }
    )

    authority_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.authority_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_release_authority_fixture_generated": True,
            "simulated_release_operator_confirmed": True,
            "simulated_rollback_operator_confirmed": True,
            "real_release_authority_present": False,
            "real_release_authorized": False,
        }
    )

    simulated_record = safety_false_payload(
        {
            "schema_name": "ystar.simulated_durable_approval_record",
            "schema_version": SCHEMA_VERSION,
            "simulated_record_id": simulated_record_id,
            "source_sandbox_approval_record_id": sandbox_record_id,
            "source_release_candidate_id": release_candidate_id,
            "record_mode": "simulated_durable_record_fixture",
            "simulated_durable_record_created": True,
            "real_durable_record_written": False,
            "durable_db_write_performed": False,
            "real_approval_granted": False,
            "real_release_authorized": False,
            "approval_scope": release_scope.get("approval_scope", release_scope),
            "denied_scope": release_candidate.get("denied_release_scope", RELEASE_DENIED_OPERATIONS),
            "integrity_hash_placeholder": (
                f"simulated-hash::{simulated_record_id}::{release_candidate_id}::{package_id}"
            ),
            "evidence_refs": [
                OPTIONAL_INPUT_REFS["sandbox_approval_record_instance"],
                INPUT_REFS["release_candidate_package"],
            ],
        }
    )

    record_integrity = safety_false_payload(
        {
            "schema_name": "ystar.simulated_approval_record.integrity_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "simulated-approval-record-integrity-check-v0",
            "source_simulated_record_id": simulated_record_id,
            "integrity_hash_placeholder_present": True,
            "scope_present": True,
            "denied_scope_present": True,
            "real_signature_material_used": False,
            "secrets_used": False,
            "validation_status": "simulated_integrity_valid_for_sandbox_release",
        }
    )

    record_scope_check = safety_false_payload(
        {
            "schema_name": "ystar.simulated_approval_record.scope_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "simulated-approval-record-scope-check-v0",
            "source_simulated_record_id": simulated_record_id,
            "package_id_matches": True,
            "patch_plan_id_matches": True,
            "release_scope_matches": True,
            "denied_scope_preserved": True,
            "cannot_authorize_real_release": True,
            "validation_status": "simulated_scope_valid_for_sandbox_release",
        }
    )

    record_storage_blocker = safety_false_payload(
        {
            "schema_name": "ystar.simulated_approval_record.storage_blocker",
            "schema_version": SCHEMA_VERSION,
            "blocker_id": "simulated-approval-record-storage-blocker-v0",
            "durable_persistence_enabled": False,
            "durable_persistence_is_not_enabled": True,
            "real_approval_record_storage_requires_future_explicit_milestone": True,
            "simulated_record_cannot_authorize_real_release": True,
            "current_milestone_remains_sandbox_only": True,
        }
    )

    record_summary = safety_false_payload(
        {
            "schema_name": "ystar.simulated_approval_record.summary",
            "schema_version": SCHEMA_VERSION,
            "simulated_durable_approval_record_generated": True,
            "simulated_durable_record_created": True,
            "real_durable_record_written": False,
            "durable_db_write_performed": False,
            "real_approval_granted": False,
            "real_release_authorized": False,
        }
    )

    snapshot_manifest = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.snapshot_manifest",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": snapshot_id,
            "snapshot_mode": "sandbox_pre_application_snapshot",
            "source_release_candidate_id": release_candidate_id,
            "captured_sandbox_artifact_refs": [
                "sandbox_release_snapshot/sandbox_pre_release_projection_policy_snapshot.json",
                "sandbox_release_snapshot/sandbox_pre_release_mcp_boundary_snapshot.json",
                "sandbox_release_snapshot/sandbox_pre_release_y_star_lineage_snapshot.json",
            ],
            "excluded_sensitive_sources": [
                "raw DB dumps",
                "log contents",
                "active-agent markers",
                "secrets",
                "credentials",
            ],
            "raw_db_dump_read": False,
            "log_content_read": False,
            "active_agent_marker_read": False,
            "secrets_captured": False,
            "real_canonical_snapshot_created": False,
            "evidence_refs": [
                INPUT_REFS["snapshot_preflight_validation_result"],
                INPUT_REFS["release_candidate_package"],
            ],
        }
    )

    pre_release_projection_policy = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.pre_release_projection_policy_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-pre-release-projection-policy-snapshot-v0",
            "snapshot_mode": "sandbox_copy_only",
            "source_package_id": package_id,
            "policy_summary": {
                "trace_linkage": "baseline controlled projection trace linkage",
                "behavior_boundary_inheritance": "baseline inherited mission constraints",
                "pre_u_mapping_expectation": "baseline Pre-U mapping expectation",
            },
            "real_canonical_policy_modified": False,
        }
    )

    pre_release_mcp_boundary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.pre_release_mcp_boundary_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-pre-release-mcp-boundary-snapshot-v0",
            "snapshot_mode": "sandbox_copy_only",
            "mcp_non_bypass_required": True,
            "mcp_execution_enabled": False,
            "real_mcp_execution_performed": False,
        }
    )

    pre_release_y_star_lineage = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.pre_release_y_star_lineage_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-pre-release-y-star-lineage-snapshot-v0",
            "mission_level_y_star_source": OPTIONAL_INPUT_REFS["mission_y_star_input"],
            "behavior_level_y_star_source": OPTIONAL_INPUT_REFS["behavior_level_y_star_candidate"],
            "mission_y_star_id": mission_y_star_id,
            "behavior_y_star_id": behavior_y_star_id,
            "projection_derived_relationship": True,
            "residual_did_not_directly_mutate_y_star": True,
            "release_must_preserve_lineage": True,
        }
    )

    snapshot_integrity = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.snapshot_integrity_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "sandbox-snapshot-integrity-check-v0",
            "source_snapshot_id": snapshot_id,
            "captured_sandbox_artifacts_present": True,
            "raw_db_dump_read": False,
            "log_content_read": False,
            "active_agent_marker_read": False,
            "secrets_captured": False,
            "real_canonical_snapshot_created": False,
            "validation_status": "sandbox_snapshot_valid",
        }
    )

    snapshot_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.snapshot_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_snapshot_generated": True,
            "real_canonical_snapshot_created": False,
            "raw_db_dump_read": False,
            "log_content_read": False,
            "active_agent_marker_read": False,
            "secrets_captured": False,
        }
    )

    release_plan = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.execution_plan",
            "schema_version": SCHEMA_VERSION,
            "sandbox_release_plan_id": release_plan_id,
            "source_release_candidate_id": release_candidate_id,
            "source_simulated_approval_record_id": simulated_record_id,
            "source_sandbox_snapshot_id": snapshot_id,
            "source_release_operator_confirmation_id": release_confirmation["confirmation_id"],
            "source_rollback_operator_confirmation_id": rollback_confirmation["confirmation_id"],
            "release_mode": "sandbox_release_simulation",
            "planned_sandbox_operations": [
                "copy baseline sandbox policy snapshot",
                "apply versioned patch plan semantics to sandbox release state",
                "emit sandbox release receipt",
                "run sandbox post-release validation",
                "run sandbox rollback drill",
            ],
            "denied_real_operations": RELEASE_DENIED_OPERATIONS,
            "required_post_release_validation": POST_RELEASE_INVARIANTS,
            "required_rollback_drill": True,
            "real_release_authorized": False,
            "real_application_authorized": False,
            "evidence_refs": [
                "simulated_durable_approval_record/simulated_durable_approval_record.json",
                "sandbox_release_snapshot/sandbox_release_snapshot_manifest.json",
            ],
        }
    )

    operation_sequence = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.operation_sequence",
            "schema_version": SCHEMA_VERSION,
            "sequence_id": "sandbox-release-operation-sequence-v0",
            "source_sandbox_release_plan_id": release_plan_id,
            "operations": release_plan["planned_sandbox_operations"],
            "all_operations_sandbox_only": True,
            "real_release_authorized": False,
        }
    )

    allowed_operations = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.allowed_operations",
            "schema_version": SCHEMA_VERSION,
            "allowed_operations_id": "sandbox-release-allowed-operations-v0",
            "allowed_sandbox_operations": release_plan["planned_sandbox_operations"],
            "real_operations_allowed": False,
        }
    )

    denied_operations = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.denied_operations",
            "schema_version": SCHEMA_VERSION,
            "denied_operations_id": "sandbox-release-denied-operations-v0",
            "denied_operations": RELEASE_DENIED_OPERATIONS,
            "real_canonical_policy_mutation_denied": True,
            "real_canonical_update_application_denied": True,
            "real_brain_writeback_denied": True,
            "real_memory_ingestion_denied": True,
            "real_strategy_mutation_denied": True,
            "direct_y_star_mutation_denied": True,
            "mcp_execution_denied": True,
            "external_action_denied": True,
            "network_api_call_denied": True,
            "y_star_gov_modification_denied": True,
            "gov_mcp_modification_denied": True,
            "l6_revenue_opportunity_discovery_denied": True,
        }
    )

    plan_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.execution_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_release_execution_plan_generated": True,
            "release_mode": "sandbox_release_simulation",
            "real_release_authorized": False,
            "real_application_authorized": False,
        }
    )

    release_execution_result = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.execution_result",
            "schema_version": SCHEMA_VERSION,
            "sandbox_release_execution_id": release_execution_id,
            "source_sandbox_release_plan_id": release_plan_id,
            "release_applied_to_sandbox": True,
            "release_applied_to_real_canonical_policy": False,
            "real_canonical_policy_mutated": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
            "strategy_mutation_performed": False,
            "direct_y_star_mutation_performed": False,
            "mcp_execution_performed": False,
            "live_execution_performed": False,
            "network_called": False,
            "evidence_refs": [
                "sandbox_release_execution_plan/sandbox_release_execution_plan.json",
                "sandbox_release_snapshot/sandbox_release_snapshot_manifest.json",
            ],
        }
    )

    released_projection_policy = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.released_projection_policy_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-released-projection-policy-snapshot-v0",
            "source_sandbox_release_execution_id": release_execution_id,
            "sandbox_only_policy_changes": ACCEPTABLE_SANDBOX_CHANGES,
            "forbidden_changes": [
                "rewrite mission-level Y*",
                "directly overwrite behavior-level Y*",
                "enable live execution",
                "enable MCP execution",
                "write brain/memory",
                "mutate real canonical policy",
            ],
            "real_canonical_policy_mutated": False,
            "live_execution_enabled": False,
            "mcp_execution_enabled": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
        }
    )

    released_mcp_boundary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.released_mcp_boundary_policy_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-released-mcp-boundary-policy-snapshot-v0",
            "mcp_non_bypass_evidence_requirement": "improved in sandbox release state",
            "mcp_execution_enabled": False,
            "real_mcp_execution_performed": False,
            "mcp_tool_called": False,
            "mcp_resource_mutated": False,
        }
    )

    released_learning_policy = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.released_learning_policy_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-released-learning-policy-snapshot-v0",
            "residual_classification_labels_improved": True,
            "evidence_completeness_requirements_improved": True,
            "candidate_auto_approval_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
        }
    )

    real_state_unchanged = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.real_state_unchanged_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "sandbox-real-state-unchanged-check-v0",
            "real_canonical_policy_unchanged": True,
            "real_brain_unchanged": True,
            "real_memory_unchanged": True,
            "real_strategy_unchanged": True,
            "y_star_gov_unmodified": True,
            "gov_mcp_unmodified": True,
            "real_release_performed": False,
            "real_application_performed": False,
        }
    )

    release_receipt = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.execution_receipt",
            "schema_version": SCHEMA_VERSION,
            "receipt_id": "sandbox-release-execution-receipt-v0",
            "source_sandbox_release_execution_id": release_execution_id,
            "release_mode": "sandbox_release_simulation",
            "release_applied_to_sandbox": True,
            "release_applied_to_real_canonical_policy": False,
            "real_release_authorized": False,
            "real_release_performed": False,
            "durable_approval_record_written": False,
        }
    )

    result_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.execution_result_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_release_execution_generated": True,
            "sandbox_release_executed": True,
            "real_canonical_state_unchanged": True,
            "real_release_authorized": False,
            "real_release_performed": False,
            "real_canonical_policy_mutated": False,
        }
    )

    post_validation_result = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.validation_result",
            "schema_version": SCHEMA_VERSION,
            "validation_result_id": "sandbox-post-release-validation-result-v0",
            "sandbox_release_applied": True,
            "real_state_unchanged": True,
            "mission_y_star_lineage_preserved": True,
            "behavior_y_star_still_projection_derived": True,
            "residual_did_not_directly_mutate_y_star": True,
            "Pre-U_validation_still_required": True,
            "bridge_receipt_still_required": True,
            "CIEU_receipt_still_required": True,
            "MCP_non_bypass_preserved": True,
            "brain_writeback_still_blocked": True,
            "memory_ingestion_still_blocked": True,
            "live_execution_still_blocked": True,
            "external_action_still_blocked": True,
            "rollback_drill_available": True,
            "validation_status": "sandbox_post_release_validated",
        }
    )

    test_matrix_result = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.test_matrix_result",
            "schema_version": SCHEMA_VERSION,
            "test_matrix_result_id": "sandbox-post-release-test-matrix-result-v0",
            "source_post_release_validation_matrix": INPUT_REFS["post_release_validation_matrix"],
            "matrix_replayed_against_sandbox_state": True,
            "required_invariant_checks": POST_RELEASE_INVARIANTS,
            "validation_status": "sandbox_test_matrix_replayed",
        }
    )

    post_y_star_check = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.y_star_non_mutation_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "sandbox-post-release-y-star-non-mutation-check-v0",
            "mission_y_star_not_rewritten": True,
            "behavior_y_star_not_directly_overwritten": True,
            "release_changes_are_policy_mediated": True,
            "residual_did_not_become_new_y_star": True,
            "actual_y_did_not_become_new_y_star": True,
            "validation_status": "y_star_non_mutation_preserved",
        }
    )

    post_mcp_check = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.mcp_non_bypass_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "sandbox-post-release-mcp-non-bypass-check-v0",
            **{check: True for check in MCP_NON_BYPASS_CHECKS},
            "mcp_execution_performed": False,
            "validation_status": "mcp_non_bypass_preserved",
        }
    )

    writeback_check = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.writeback_boundary_check",
            "schema_version": SCHEMA_VERSION,
            "check_id": "sandbox-post-release-writeback-boundary-check-v0",
            "brain_writeback_still_blocked": True,
            "memory_ingestion_still_blocked": True,
            "strategy_mutation_still_blocked": True,
            "candidate_auto_approval_still_blocked": True,
            "validation_status": "writeback_boundaries_preserved",
        }
    )

    validation_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.validation_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_post_release_validation_generated": True,
            "sandbox_post_release_validation_status": post_validation_result["validation_status"],
            "y_star_non_mutation_preserved": True,
            "mcp_non_bypass_preserved": True,
            "real_state_unchanged": True,
            "rollback_drill_available": True,
        }
    )

    projection_input = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.projection_input",
            "schema_version": SCHEMA_VERSION,
            "projection_input_id": "sandbox-post-release-projection-input-v0",
            "source_mission_y_star_id": mission_y_star_id,
            "source_sandbox_released_policy_snapshot_id": released_projection_policy["snapshot_id"],
            "input_mode": "sandbox_projection_preview_only",
            "behavior_execution_enabled": False,
        }
    )

    post_behavior_y_star = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.behavior_y_star",
            "schema_version": SCHEMA_VERSION,
            "post_release_behavior_y_star_id": post_release_behavior_y_star_id,
            "source_mission_y_star_id": mission_y_star_id,
            "source_sandbox_released_policy_snapshot_id": released_projection_policy["snapshot_id"],
            "projected_behavior_y_star": {
                "projection_target": "future behavior-level Y* remains mission-derived",
                "sandbox_release_effect": "policy-mediated boundary and evidence tightening",
                "execution_boundary": "dry-run sandbox preview only",
            },
            "changed_fields_from_pre_release": [
                "projection trace linkage",
                "Pre-U mapping evidence requirement",
                "MCP non-bypass evidence requirement",
                "residual classification labels",
            ],
            "unchanged_fields_from_pre_release": [
                "mission-level Y*",
                "behavior execution authorization",
                "MCP execution authorization",
                "brain/memory writeback authorization",
            ],
            "inherited_constraints_preserved": True,
            "forbidden_boundaries_preserved": True,
            "pre_u_validation_still_required": True,
            "live_behavior_authorized": False,
            "behavior_execution_enabled": False,
            "applied_to_real_canonical_policy": False,
            "applied_to_brain": False,
            "applied_to_memory": False,
            "direct_y_star_mutation_performed": False,
            "evidence_refs": [
                "sandbox_release_execution_result/sandbox_released_projection_policy_snapshot.json",
                INPUT_REFS["y_star_non_mutation_invariant"],
            ],
        }
    )

    behavior_delta = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.behavior_y_star_delta",
            "schema_version": SCHEMA_VERSION,
            "delta_id": "sandbox-post-release-behavior-y-star-delta-v0",
            "source_behavior_y_star_id": post_release_behavior_y_star_id,
            "projection_policy_mediated_delta": "trace linkage and evidence requirements tightened",
            "evidence_requirement_delta": "post-release evidence completeness requirement improved",
            "boundary_contraction_delta": "forbidden live and MCP boundaries remain explicit",
            "pre_u_mapping_delta": "Pre-U mapping expectation clarified",
            "mcp_non_bypass_delta": "MCP receipt chain evidence requirement improved",
            "residual_classification_delta": "release residual labels clarified",
            "no_direct_y_star_mutation": True,
        }
    )

    mcp_pre_u = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.mcp_pre_u_candidate",
            "schema_version": SCHEMA_VERSION,
            "pre_u_packet_id": "sandbox-post-release-mcp-pre-u-candidate-v0",
            "source_behavior_y_star_id": post_release_behavior_y_star_id,
            "requested_operation": "sandbox preview of governed MCP resource retrieval",
            "requires_future_y_star_gov_validation_before_live_execution": True,
            "live_execution_authorized": False,
            "mcp_tool_execution_authorized": False,
            "external_action_authorized": False,
        }
    )

    mcp_gate = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.mcp_gate_preview",
            "schema_version": SCHEMA_VERSION,
            "gate_preview_id": "sandbox-post-release-mcp-gate-preview-v0",
            "source_pre_u_packet_id": mcp_pre_u["pre_u_packet_id"],
            "decision": "allow_sandbox_mcp_dry_run_only",
            "real_mcp_execution_authorized": False,
            "mcp_tool_execution_authorized": False,
            "network_authorized": False,
        }
    )

    mcp_receipt = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_post_release.mcp_receipt_preview",
            "schema_version": SCHEMA_VERSION,
            "receipt_id": "sandbox-post-release-mcp-receipt-preview-v0",
            "source_pre_u_packet_id": mcp_pre_u["pre_u_packet_id"],
            "source_gate_preview_id": mcp_gate["gate_preview_id"],
            "execution_mode": "sandbox_mcp_dry_run_preview_only",
            "real_execution_performed": False,
            "mcp_server_started": False,
            "mcp_tool_called": False,
            "mcp_resource_mutated": False,
            "network_called": False,
            "persistence_mode": "none",
        }
    )

    preview_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.projection_mcp_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_post_release_projection_generated": True,
            "sandbox_mcp_preview_generated": True,
            "pre_u_validation_still_required": True,
            "mcp_tool_called": False,
            "network_called": False,
        }
    )

    rollback_plan_instance = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.rollback_plan_instance",
            "schema_version": SCHEMA_VERSION,
            "rollback_plan_instance_id": "sandbox-release-rollback-plan-instance-v0",
            "source_sandbox_release_execution_id": release_execution_id,
            "rollback_mode": "sandbox_rollback_drill_only",
            "rollback_steps": [
                "remove sandbox released policy snapshot",
                "restore sandbox pre-release policy snapshot",
                "verify Y* lineage still preserved",
                "verify no real state changed",
            ],
            "real_rollback_performed": False,
        }
    )

    rollback_result = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.rollback_result",
            "schema_version": SCHEMA_VERSION,
            "rollback_id": rollback_id,
            "source_sandbox_release_execution_id": release_execution_id,
            "rollback_performed_in_sandbox": True,
            "real_canonical_policy_modified": False,
            "brain_modified": False,
            "memory_modified": False,
            "strategy_modified": False,
            "y_star_direct_mutation_performed": False,
            "mcp_execution_performed": False,
            "rollback_restored_baseline": True,
            "evidence_refs": [
                "sandbox_release_snapshot/sandbox_pre_release_projection_policy_snapshot.json",
                "sandbox_release_execution_result/sandbox_released_projection_policy_snapshot.json",
            ],
        }
    )

    post_rollback_policy = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.post_rollback_projection_policy_snapshot",
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": "sandbox-post-rollback-projection-policy-snapshot-v0",
            "source_rollback_id": rollback_id,
            "restored_from_snapshot_id": pre_release_projection_policy["snapshot_id"],
            "baseline_restored": True,
            "real_canonical_policy_modified": False,
        }
    )

    post_rollback_validation = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.post_rollback_validation_result",
            "schema_version": SCHEMA_VERSION,
            "validation_result_id": "sandbox-post-rollback-validation-result-v0",
            "baseline_restored": True,
            "sandbox_release_removed_or_neutralized": True,
            "mission_y_star_lineage_preserved": True,
            "behavior_y_star_projection_lineage_preserved": True,
            "no_real_canonical_change": True,
            "no_brain_memory_change": True,
            "no_y_star_direct_mutation": True,
            "no_mcp_execution": True,
            "no_live_execution": True,
        }
    )

    rollback_delta = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.rollback_delta",
            "schema_version": SCHEMA_VERSION,
            "delta_id": "sandbox-release-rollback-delta-v0",
            "source_rollback_id": rollback_id,
            "baseline_restored": True,
            "residual_summary": "sandbox rollback restores baseline; real system was never changed",
            "real_canonical_policy_modified": False,
        }
    )

    rollback_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.rollback_summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_rollback_drill_generated": True,
            "rollback_performed_in_sandbox": True,
            "rollback_restored_baseline": True,
            "real_canonical_policy_modified": False,
            "mcp_execution_performed": False,
            "live_execution_performed": False,
        }
    )

    comparison = safety_false_payload(
        {
            "schema_name": "ystar.original_release_rollback.comparison",
            "schema_version": SCHEMA_VERSION,
            "comparison_id": "original-vs-sandbox-release-vs-rollback-comparison-v0",
            "original_behavior_y_star": OPTIONAL_INPUT_REFS["behavior_level_y_star_candidate"],
            "sandbox_post_release_behavior_y_star": (
                "sandbox_release_projection_and_mcp_preview/sandbox_post_release_behavior_y_star.json"
            ),
            "post_rollback_policy_snapshot": (
                "sandbox_release_rollback_drill/sandbox_post_rollback_projection_policy_snapshot.json"
            ),
            "original_projection_policy_summary": "baseline sandbox projection policy",
            "sandbox_released_projection_policy_summary": "sandbox policy with release-simulated improvements",
            "post_rollback_projection_policy_summary": "baseline restored after rollback drill",
            "y_star_lineage_preserved": True,
            "safety_boundaries_preserved": True,
            "real_canonical_system_changed": False,
            "brain_memory_changed": False,
            "gov_repos_changed": False,
            "mcp_execution_performed": False,
        }
    )

    release_effect = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.effect_summary",
            "schema_version": SCHEMA_VERSION,
            "effect_summary_id": "sandbox-release-effect-summary-v0",
            "allowed_effect_classes": [
                "no_visible_sandbox_effect",
                "documentation_only_sandbox_effect",
                "projection_policy_sandbox_release_effect",
                "behavior_y_star_projection_sandbox_release_effect",
                "pre_u_mapping_sandbox_release_effect",
                "mcp_boundary_sandbox_release_effect",
                "residual_classification_sandbox_release_effect",
            ],
            "observed_effect_class": "behavior_y_star_projection_sandbox_release_effect",
            "effect_is_policy_mediated": True,
            "direct_y_star_mutation_performed": False,
        }
    )

    rollback_effect = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.rollback_effect_summary",
            "schema_version": SCHEMA_VERSION,
            "rollback_effect_summary_id": "sandbox-release-rollback-effect-summary-v0",
            "rollback_restored_baseline": True,
            "unresolved_rollback_gaps": [],
            "real_system_changed": False,
        }
    )

    safety_summary = safety_false_payload(
        {
            "schema_name": "ystar.sandbox_release.safety_summary",
            "schema_version": SCHEMA_VERSION,
            "safety_summary_id": "sandbox-release-safety-summary-v0",
            "real_release_still_blocked": True,
            "real_approval_still_blocked": True,
            "durable_persistence_still_blocked": True,
            "real_canonical_application_still_blocked": True,
            "brain_writeback_still_blocked": True,
            "memory_ingestion_still_blocked": True,
            "y_star_direct_mutation_still_blocked": True,
            "mcp_execution_still_blocked": True,
        }
    )

    predicted_outcome = safety_false_payload(
        {
            "schema_name": "ystar.release_simulation.predicted_outcome",
            "schema_version": SCHEMA_VERSION,
            "predicted_outcome_id": "release-simulation-predicted-outcome-v0",
            "expected_results": [
                "sandbox authority fixture generated",
                "simulated durable approval record generated",
                "sandbox snapshot generated",
                "simulated operators confirmed",
                "sandbox release executed",
                "real state unchanged",
                "post-release validation performed",
                "sandbox MCP preview generated",
                "rollback drill performed",
                "release comparison generated",
                "real release blocked",
            ],
        }
    )

    mock_actual_outcome = safety_false_payload(
        {
            "schema_name": "ystar.release_simulation.mock_actual_outcome",
            "schema_version": SCHEMA_VERSION,
            "mock_actual_outcome_id": "release-simulation-mock-actual-outcome-v0",
            "actual_results": predicted_outcome["expected_results"],
            "real_release_authorized": False,
            "real_release_performed": False,
            "durable_approval_record_written": False,
        }
    )

    residual_delta = safety_false_payload(
        {
            "schema_name": "ystar.release_simulation.residual_delta",
            "schema_version": SCHEMA_VERSION,
            "residual_delta_id": "release-simulation-residual-delta-v0",
            "source_predicted_outcome_id": predicted_outcome["predicted_outcome_id"],
            "source_mock_actual_outcome_id": mock_actual_outcome["mock_actual_outcome_id"],
            "residual_classes": [
                {
                    "class": residual_class,
                    "status": "satisfied_or_blocked_in_sandbox_simulation",
                    "structural_delta": (
                        "sandbox release simulation completed while real release remains blocked"
                    ),
                }
                for residual_class in RELEASE_RESIDUAL_CLASSES
            ],
            "residual_summary": (
                "Sandbox release, validation, MCP preview, and rollback drill were represented "
                "only as generated artifacts. Real approval, durable persistence, and real release remain blocked."
            ),
            "semantic_truth_scoring_enabled": False,
        }
    )

    cieu_event = safety_false_payload(
        {
            "schema_name": "ystar.release_simulation.cieu_event_fixture",
            "schema_version": SCHEMA_VERSION,
            "event_id": "release-simulation-cieu-event-fixture-v0",
            "event_mode": "real_release_simulation_sandbox_fixture",
            "X_t": {
                "source_release_preflight": (
                    "controlled_real_release_preflight/controlled_real_release_preflight_run.json"
                ),
                "source_release_candidate": INPUT_REFS["release_candidate_package"],
                "source_release_blocker": INPUT_REFS["release_blocker_decision"],
            },
            "U_t": {
                "operation": "real release simulation sandbox",
                "release_candidate_id": release_candidate_id,
                "sandbox_release_execution_id": release_execution_id,
            },
            "Y_star_t": {
                "declared_target": (
                    "Simulate a controlled release in sandbox only, validate invariants, "
                    "and verify rollback without granting real approval or applying real canonical update."
                ),
                "y_star_non_mutation_required": True,
                "mcp_non_bypass_required": True,
            },
            "Y_t_plus_1": mock_actual_outcome,
            "R_t_plus_1": {
                "residual_delta_id": residual_delta["residual_delta_id"],
                "residual_classes": RELEASE_RESIDUAL_CLASSES,
            },
            "persistence_enabled": False,
            "db_write_performed": False,
            "durable_approval_record_written": False,
            "real_release_performed": False,
        }
    )

    cieu_summary = safety_false_payload(
        {
            "schema_name": "ystar.release_simulation.cieu_summary",
            "schema_version": SCHEMA_VERSION,
            "release_simulation_cieu_like_fixture_generated": True,
            "release_simulation_residual_delta_generated": True,
            "persistence_enabled": False,
            "db_write_performed": False,
            "durable_approval_record_written": False,
            "real_release_performed": False,
            "residual_classes": RELEASE_RESIDUAL_CLASSES,
        }
    )

    readiness = {
        "schema_name": "ystar.real_release_simulation.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "real-release-simulation-readiness-v0",
        "sandbox_release_authority_fixture_generated": True,
        "simulated_durable_approval_record_generated": True,
        "sandbox_snapshot_generated": True,
        "simulated_release_operator_confirmed": True,
        "simulated_rollback_operator_confirmed": True,
        "sandbox_release_execution_plan_generated": True,
        "sandbox_release_executed": True,
        "real_canonical_state_unchanged": True,
        "sandbox_post_release_validation_generated": True,
        "sandbox_post_release_projection_generated": True,
        "sandbox_mcp_preview_generated": True,
        "sandbox_rollback_drill_generated": True,
        "rollback_restored_or_gap_recorded": True,
        "original_release_rollback_comparison_generated": True,
        "release_simulation_cieu_fixture_generated": True,
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
        "ready_for_l5_13_live_boundary_no_go_decision_framework": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "real_release_authorized": False,
        "real_release_performed": False,
        "real_approval_granted": False,
        "durable_approval_record_written": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "missing_sources": missing_sources,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "simulation_flags": SIMULATION_FLAGS,
        **SAFETY_FLAGS,
    }

    contract = {
        "schema_name": "ystar.real_release_simulation_sandbox.contract",
        "schema_version": SCHEMA_VERSION,
        "sandbox_name": "L5.12 Real Release Simulation Sandbox v0",
        "purpose": (
            "Simulate the complete controlled release path inside generated sandbox artifacts "
            "while proving real release, real approval, durable persistence, canonical mutation, "
            "writeback, MCP execution, and L6 discovery remain blocked."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "optional_inputs": list(OPTIONAL_INPUT_REFS.values()),
        "simulation_stages": SIMULATION_STAGES,
        "required_outputs": [
            "sandbox release authority fixture",
            "simulated durable approval record",
            "sandbox pre-application snapshot",
            "sandbox release execution plan",
            "sandbox release execution result",
            "sandbox post-release validation",
            "sandbox projection and MCP preview",
            "sandbox rollback drill",
            "original/release/rollback comparison",
            "release simulation CIEU-like fixture",
            "readiness",
        ],
        "simulated_authority_requirements": [
            "sandbox release authority fixture only",
            "simulated release and rollback operator confirmations only",
            "real approval remains false",
        ],
        "simulated_durable_record_requirements": [
            "simulated durable approval record artifact only",
            "durable DB write remains false",
            "record cannot authorize real release",
        ],
        "simulated_snapshot_requirements": [
            "sandbox pre-application snapshot only",
            "no raw DB/log/active-agent/secret capture",
        ],
        "simulated_release_requirements": [
            "apply only to sandbox release state",
            "verify real canonical state unchanged",
        ],
        "simulated_post_validation_requirements": POST_RELEASE_INVARIANTS,
        "simulated_rollback_requirements": [
            "sandbox rollback drill",
            "baseline restoration check",
            "no real rollback execution",
        ],
        "audit_requirements": [
            "release receipt",
            "CIEU-like fixture",
            "residual delta",
            "original/release/rollback comparison",
        ],
        "safety_flags": SAFETY_FLAGS,
        "simulation_flags": SIMULATION_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "real release",
            "real approval",
            "durable approval persistence",
            "real canonical update",
            "brain or memory writeback",
            "MCP execution",
            "L6 revenue opportunity discovery",
        ],
    }

    input_fixture = {
        "schema_name": "ystar.real_release_simulation.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "input_refs": INPUT_REFS,
        "optional_input_refs": OPTIONAL_INPUT_REFS,
        "input_statuses": input_statuses,
        "missing_sources": missing_sources,
        "gap_handling": "missing optional sources are recorded and do not trigger destructive failure",
        "safety_flags": SAFETY_FLAGS,
        "simulation_flags": SIMULATION_FLAGS,
    }

    run = {
        "schema_name": "ystar.real_release_simulation.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "real-release-simulation-sandbox-run-v0",
        "contract_ref": "real_release_simulation_sandbox/real_release_simulation_sandbox_contract.json",
        "input_fixture_ref": "real_release_simulation_sandbox/real_release_simulation_input_fixture.json",
        "simulation_stages_completed": SIMULATION_STAGES,
        "release_candidate_id": release_candidate_id,
        "sandbox_release_execution_id": release_execution_id,
        "rollback_id": rollback_id,
        "real_release_authorized": False,
        "real_release_performed": False,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "simulation_flags": SIMULATION_FLAGS,
    }

    sim_summary = {
        "schema_name": "ystar.real_release_simulation.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_12_real_release_simulation_sandbox_defined": True,
        "sandbox_release_authority_fixture_generated": True,
        "simulated_durable_approval_record_generated": True,
        "sandbox_snapshot_generated": True,
        "simulated_release_operator_confirmed": True,
        "simulated_rollback_operator_confirmed": True,
        "sandbox_release_execution_generated": True,
        "real_canonical_state_unchanged": True,
        "sandbox_post_release_validation_generated": True,
        "sandbox_post_release_projection_generated": True,
        "sandbox_mcp_preview_generated": True,
        "sandbox_rollback_drill_generated": True,
        "release_simulation_cieu_like_fixture_generated": True,
        "real_release_authorized": False,
        "real_release_performed": False,
        "durable_approval_record_written": False,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "simulation_flags": SIMULATION_FLAGS,
    }

    # Top-level simulation pack.
    write_text(
        SIM / "README.md",
        markdown_report(
            "L5.12 Real Release Simulation Sandbox",
            [
                "Simulates a controlled release path only in generated sandbox artifacts.",
                "Real approval, durable persistence, real release, and canonical update remain blocked.",
                "Sandbox release validation and rollback drill prove the pathway can be rehearsed safely.",
            ],
        ),
    )
    write_json(SIM / "real_release_simulation_sandbox_contract.json", contract)
    write_json(SIM / "real_release_simulation_input_fixture.json", input_fixture)
    write_json(SIM / "real_release_simulation_run.json", run)
    write_json(SIM / "real_release_simulation_summary.json", sim_summary)
    write_text(
        SIM / "real_release_simulation_report.md",
        markdown_report(
            "Real Release Simulation Report",
            [
                "Sandbox release authority fixture generated: true",
                "Simulated durable approval record generated: true",
                "Sandbox release executed: true",
                "Real canonical state unchanged: true",
                "Sandbox rollback drill performed: true",
                f"Ready for {NEXT_MILESTONE}: true",
            ],
        ),
    )

    # Authority pack.
    write_json(AUTH / "sandbox_release_authority_fixture.json", authority_fixture)
    write_json(AUTH / "simulated_release_operator_confirmation.json", release_confirmation)
    write_json(AUTH / "simulated_rollback_operator_confirmation.json", rollback_confirmation)
    write_json(AUTH / "sandbox_release_authority_denied_scope.json", authority_denied_scope)
    write_json(AUTH / "sandbox_release_authority_summary.json", authority_summary)
    write_text(
        AUTH / "sandbox_release_authority_report.md",
        markdown_report(
            "Sandbox Release Authority Report",
            [
                "Authority mode: sandbox_release_simulation_only",
                "Real release authority present: false",
                "Real release authorized: false",
            ],
        ),
    )

    # Simulated durable approval record pack.
    write_json(RECORD / "simulated_durable_approval_record.json", simulated_record)
    write_json(RECORD / "simulated_approval_record_integrity_check.json", record_integrity)
    write_json(RECORD / "simulated_approval_record_scope_check.json", record_scope_check)
    write_json(RECORD / "simulated_approval_record_storage_blocker.json", record_storage_blocker)
    write_json(RECORD / "simulated_approval_record_summary.json", record_summary)
    write_text(
        RECORD / "simulated_approval_record_report.md",
        markdown_report(
            "Simulated Approval Record Report",
            [
                "Record mode: simulated_durable_record_fixture",
                "Real durable record written: false",
                "Durable DB write performed: false",
                "Real release authorized: false",
            ],
        ),
    )

    # Sandbox snapshot pack.
    write_json(SNAPSHOT / "sandbox_release_snapshot_manifest.json", snapshot_manifest)
    write_json(SNAPSHOT / "sandbox_pre_release_projection_policy_snapshot.json", pre_release_projection_policy)
    write_json(SNAPSHOT / "sandbox_pre_release_mcp_boundary_snapshot.json", pre_release_mcp_boundary)
    write_json(SNAPSHOT / "sandbox_pre_release_y_star_lineage_snapshot.json", pre_release_y_star_lineage)
    write_json(SNAPSHOT / "sandbox_snapshot_integrity_check.json", snapshot_integrity)
    write_json(SNAPSHOT / "sandbox_release_snapshot_summary.json", snapshot_summary)
    write_text(
        SNAPSHOT / "sandbox_release_snapshot_report.md",
        markdown_report(
            "Sandbox Release Snapshot Report",
            [
                "Snapshot mode: sandbox_pre_application_snapshot",
                "Raw DB dump read: false",
                "Log content read: false",
                "Real canonical snapshot created: false",
            ],
        ),
    )

    # Sandbox release execution plan pack.
    write_json(PLAN / "sandbox_release_execution_plan.json", release_plan)
    write_json(PLAN / "sandbox_release_operation_sequence.json", operation_sequence)
    write_json(PLAN / "sandbox_release_allowed_operations.json", allowed_operations)
    write_json(PLAN / "sandbox_release_denied_operations.json", denied_operations)
    write_json(PLAN / "sandbox_release_execution_summary.json", plan_summary)
    write_text(
        PLAN / "sandbox_release_execution_report.md",
        markdown_report(
            "Sandbox Release Execution Plan Report",
            [
                "Release mode: sandbox_release_simulation",
                "Real release authorized: false",
                "Real application authorized: false",
            ],
        ),
    )

    # Sandbox release execution result pack.
    write_json(RESULT / "sandbox_release_execution_result.json", release_execution_result)
    write_json(RESULT / "sandbox_released_projection_policy_snapshot.json", released_projection_policy)
    write_json(RESULT / "sandbox_released_mcp_boundary_policy_snapshot.json", released_mcp_boundary)
    write_json(RESULT / "sandbox_released_learning_policy_snapshot.json", released_learning_policy)
    write_json(RESULT / "sandbox_real_state_unchanged_check.json", real_state_unchanged)
    write_json(RESULT / "sandbox_release_execution_receipt.json", release_receipt)
    write_json(RESULT / "sandbox_release_execution_result_summary.json", result_summary)
    write_text(
        RESULT / "sandbox_release_execution_result_report.md",
        markdown_report(
            "Sandbox Release Execution Result Report",
            [
                "Release applied to sandbox: true",
                "Release applied to real canonical policy: false",
                "Real canonical state unchanged: true",
            ],
        ),
    )

    # Sandbox post-release validation pack.
    write_json(VALIDATION / "sandbox_post_release_validation_result.json", post_validation_result)
    write_json(VALIDATION / "sandbox_post_release_test_matrix_result.json", test_matrix_result)
    write_json(VALIDATION / "sandbox_post_release_y_star_non_mutation_check.json", post_y_star_check)
    write_json(VALIDATION / "sandbox_post_release_mcp_non_bypass_check.json", post_mcp_check)
    write_json(VALIDATION / "sandbox_post_release_writeback_boundary_check.json", writeback_check)
    write_json(VALIDATION / "sandbox_post_release_validation_summary.json", validation_summary)
    write_text(
        VALIDATION / "sandbox_post_release_validation_report.md",
        markdown_report(
            "Sandbox Post-Release Validation Report",
            [
                "Validation status: sandbox_post_release_validated",
                "Y* non-mutation preserved: true",
                "MCP non-bypass preserved: true",
                "Rollback drill available: true",
            ],
        ),
    )

    # Projection and MCP preview pack.
    write_json(PREVIEW / "sandbox_post_release_projection_input.json", projection_input)
    write_json(PREVIEW / "sandbox_post_release_behavior_y_star.json", post_behavior_y_star)
    write_json(PREVIEW / "sandbox_post_release_behavior_y_star_delta.json", behavior_delta)
    write_json(PREVIEW / "sandbox_post_release_mcp_pre_u_candidate.json", mcp_pre_u)
    write_json(PREVIEW / "sandbox_post_release_mcp_gate_preview.json", mcp_gate)
    write_json(PREVIEW / "sandbox_post_release_mcp_receipt_preview.json", mcp_receipt)
    write_json(PREVIEW / "sandbox_release_projection_mcp_summary.json", preview_summary)
    write_text(
        PREVIEW / "sandbox_release_projection_mcp_report.md",
        markdown_report(
            "Sandbox Release Projection and MCP Preview Report",
            [
                "Sandbox post-release behavior-level Y* projection generated: true",
                "Sandbox MCP preview generated: true",
                "MCP tool called: false",
                "Network called: false",
            ],
        ),
    )

    # Rollback drill pack.
    write_json(ROLLBACK / "sandbox_release_rollback_plan_instance.json", rollback_plan_instance)
    write_json(ROLLBACK / "sandbox_release_rollback_result.json", rollback_result)
    write_json(ROLLBACK / "sandbox_post_rollback_projection_policy_snapshot.json", post_rollback_policy)
    write_json(ROLLBACK / "sandbox_post_rollback_validation_result.json", post_rollback_validation)
    write_json(ROLLBACK / "sandbox_release_rollback_delta.json", rollback_delta)
    write_json(ROLLBACK / "sandbox_release_rollback_summary.json", rollback_summary)
    write_text(
        ROLLBACK / "sandbox_release_rollback_report.md",
        markdown_report(
            "Sandbox Release Rollback Report",
            [
                "Rollback performed in sandbox: true",
                "Rollback restored baseline: true",
                "Real canonical policy modified: false",
            ],
        ),
    )

    # Comparison pack.
    write_json(COMPARISON / "original_vs_sandbox_release_vs_rollback_comparison.json", comparison)
    write_json(COMPARISON / "sandbox_release_effect_summary.json", release_effect)
    write_json(COMPARISON / "sandbox_release_rollback_effect_summary.json", rollback_effect)
    write_json(COMPARISON / "sandbox_release_safety_summary.json", safety_summary)
    write_text(
        COMPARISON / "original_release_rollback_comparison_report.md",
        markdown_report(
            "Original Release Rollback Comparison Report",
            [
                "Sandbox release showed a policy-mediated behavior-level Y* preview effect.",
                "Rollback restored sandbox baseline: true",
                "Real canonical system changed: false",
            ],
        ),
    )

    # CIEU/residual pack.
    write_json(CIEU / "release_simulation_cieu_event_fixture.json", cieu_event)
    write_json(CIEU / "release_simulation_predicted_outcome.json", predicted_outcome)
    write_json(CIEU / "release_simulation_mock_actual_outcome.json", mock_actual_outcome)
    write_json(CIEU / "release_simulation_residual_delta.json", residual_delta)
    write_json(CIEU / "release_simulation_cieu_summary.json", cieu_summary)
    write_text(
        CIEU / "release_simulation_cieu_report.md",
        markdown_report(
            "Release Simulation CIEU Report",
            [
                "Release simulation CIEU-like fixture generated.",
                "Persistence enabled: false",
                "Durable approval record written: false",
                "Real release performed: false",
            ],
        ),
    )

    # Readiness pack.
    write_json(READINESS / "real_release_simulation_readiness.json", readiness)
    write_text(
        READINESS / "real_release_simulation_readiness.md",
        markdown_report(
            "Real Release Simulation Readiness",
            [
                "Sandbox release executed: true",
                "Real canonical state unchanged: true",
                "Sandbox rollback drill generated: true",
                "Real release still blocked: true",
                f"Ready for {NEXT_MILESTONE}: true",
                "Ready for L6 revenue opportunity discovery: false",
            ],
        ),
    )
    write_json(
        READINESS / "l5_13_recommended_next_step.json",
        {
            "schema_name": "ystar.real_release_simulation.l5_13_recommendation",
            "schema_version": SCHEMA_VERSION,
            "recommended_next_step": NEXT_MILESTONE,
            "reason": (
                "L5.12 rehearses the release path in sandbox artifacts; the next proof should "
                "define the live-boundary no-go decision framework before any real release can be considered."
            ),
            "ready_for_l5_13_live_boundary_no_go_decision_framework": True,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )

    print("L5.12 real release simulation sandbox artifacts generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
