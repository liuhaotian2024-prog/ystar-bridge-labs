#!/usr/bin/env python3
"""Build deterministic L5.10 controlled approval record sandbox artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SANDBOX = ROOT / "controlled_approval_record_sandbox"
RECORD = ROOT / "sandbox_approval_record_instance"
INTEGRITY = ROOT / "approval_record_integrity_validation"
STATE_MACHINE = ROOT / "approval_record_validity_state_machine"
REVOCATION = ROOT / "expiration_revocation_replay"
GATE = ROOT / "approval_record_pre_application_gate_replay"
AUDIT = ROOT / "approval_record_audit_lineage"
CIEU = ROOT / "approval_record_cieu_residual"
READINESS = ROOT / "controlled_approval_record_readiness"

SCHEMA_VERSION = "v0"
NEXT_MILESTONE = "L5.11 Controlled Real Release Preflight v0"

INPUT_REFS = {
    "durable_approval_record_contract": (
        "durable_approval_record_contract/durable_approval_record_contract.json"
    ),
    "approval_record_schema": "durable_approval_record_contract/approval_record_schema_v0.json",
    "approval_record_integrity_requirements": (
        "durable_approval_record_contract/approval_record_integrity_requirements.json"
    ),
    "approval_record_storage_policy": (
        "durable_approval_record_contract/approval_record_storage_policy.json"
    ),
    "real_approval_decision_packet_fixture": (
        "real_approval_decision_packet_fixture/real_approval_decision_packet_fixture.json"
    ),
    "approval_validity_policy": "approval_validity_revocation_policy/approval_validity_policy.json",
    "approval_expiration_policy": (
        "approval_validity_revocation_policy/approval_expiration_policy.json"
    ),
    "approval_revocation_policy": (
        "approval_validity_revocation_policy/approval_revocation_policy.json"
    ),
    "approval_invalidation_triggers": (
        "approval_validity_revocation_policy/approval_invalidation_triggers.json"
    ),
    "approval_evidence_dossier": "approval_evidence_dossier/approval_evidence_dossier.json",
    "approval_invariant_check_index": (
        "approval_evidence_dossier/approval_invariant_check_index.json"
    ),
    "real_application_boundary_gate_contract": (
        "real_application_boundary_gate/real_application_boundary_gate_contract.json"
    ),
    "real_application_blocker": "real_application_boundary_gate/real_application_blocker.json",
    "post_approval_preflight_validation_plan": (
        "post_approval_preflight_validation/post_approval_preflight_validation_plan.json"
    ),
    "approval_operator_checklist": "manual_approval_runbook/approval_operator_checklist.json",
    "real_approval_workflow_readiness": (
        "real_approval_workflow_readiness/real_approval_workflow_readiness.json"
    ),
    "approved_sandbox_update_readiness": (
        "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json"
    ),
    "canonical_update_package_candidate": (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    ),
    "y_star_non_mutation_invariant": (
        "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json"
    ),
}

OPTIONAL_INPUT_REFS: dict[str, str] = {
    "versioned_patch_plan": "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json",
    "rollback_plan": "rollback_and_audit_lineage/rollback_plan.json",
}

SANDBOX_STAGES = [
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
    "real_y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
}

SANDBOX_FLAGS = {
    "sandbox_approval_record_created": True,
    "sandbox_integrity_validation_performed": True,
    "sandbox_state_machine_replayed": True,
    "sandbox_gate_replay_performed": True,
    "sandbox_invalid_record_tests_generated": True,
}

FORBIDDEN_OPERATIONS = [
    "writing durable approval DB records",
    "granting real approval",
    "applying real canonical update",
    "modifying real canonical projection policy",
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

APPROVAL_RECORD_FIELDS = [
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

STATE_MACHINE_STATES = [
    "draft",
    "pending_review",
    "sandbox_valid_for_gate_replay",
    "real_approval_required",
    "expired",
    "revoked",
    "invalidated",
    "consumed_by_application",
    "superseded",
]

INVALID_VARIANTS = {
    "expired_record": {
        "filename": "sandbox_expired_record_variant.json",
        "variant_type": "expired_record",
        "changed_or_missing_fields": ["expiration_policy_ref", "approval_timestamp_placeholder"],
        "reason_codes": ["expired"],
    },
    "revoked_record": {
        "filename": "sandbox_revoked_record_variant.json",
        "variant_type": "revoked_record",
        "changed_or_missing_fields": ["revocation_policy_ref"],
        "reason_codes": ["revoked"],
    },
    "tampered_record": {
        "filename": "sandbox_tampered_record_variant.json",
        "variant_type": "tampered_record",
        "changed_or_missing_fields": ["integrity_hash_placeholder", "approval_scope"],
        "reason_codes": ["tampered_integrity"],
    },
    "wrong_scope_record": {
        "filename": "sandbox_wrong_scope_record_variant.json",
        "variant_type": "wrong_scope_record",
        "changed_or_missing_fields": ["approval_subject_package_id", "approval_scope"],
        "reason_codes": ["scope_mismatch"],
    },
    "missing_evidence_record": {
        "filename": "sandbox_missing_evidence_record_variant.json",
        "variant_type": "missing_evidence_record",
        "changed_or_missing_fields": ["evidence_dossier_id", "audit_lineage_refs"],
        "reason_codes": ["evidence_missing"],
    },
}

GATE_REASON_CODES = [
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
]

RESIDUAL_CLASSES = [
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


def structural_hash_placeholder(record: dict[str, Any]) -> str:
    material = "|".join(
        str(record.get(key))
        for key in [
            "approval_record_id",
            "approval_subject_package_id",
            "evidence_dossier_id",
            "rollback_plan_id",
            "post_validation_plan_id",
            "approval_mode",
        ]
    )
    return "sha256-placeholder-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def bool_summary(value: bool) -> str:
    return "true" if value else "false"


def markdown_report(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(f"- {line}" for line in lines) + "\n"


def main() -> int:
    all_input_refs = {**INPUT_REFS, **OPTIONAL_INPUT_REFS}
    input_statuses, missing_sources = source_status(all_input_refs)

    schema = load_json(INPUT_REFS["approval_record_schema"]) or {}
    package = load_json(INPUT_REFS["canonical_update_package_candidate"]) or {}
    patch_plan = load_json(OPTIONAL_INPUT_REFS["versioned_patch_plan"]) or {}
    evidence = load_json(INPUT_REFS["approval_evidence_dossier"]) or {}
    decision = load_json(INPUT_REFS["real_approval_decision_packet_fixture"]) or {}
    readiness_l5_9 = load_json(INPUT_REFS["real_approval_workflow_readiness"]) or {}
    readiness_l5_8 = load_json(INPUT_REFS["approved_sandbox_update_readiness"]) or {}
    rollback = load_json(OPTIONAL_INPUT_REFS["rollback_plan"]) or {}
    preflight = load_json(INPUT_REFS["post_approval_preflight_validation_plan"]) or {}

    package_id = package.get("package_id", "canonical-update-package-candidate-v0")
    patch_plan_id = patch_plan.get("patch_plan_id", "versioned-canonical-patch-plan-v0")
    evidence_dossier_id = evidence.get("dossier_id", "approval-evidence-dossier-v0")
    rollback_plan_id = rollback.get("rollback_plan_id", "rollback-plan-v0")
    post_validation_plan_id = preflight.get(
        "preflight_plan_id",
        preflight.get("plan_id", "post-approval-preflight-validation-plan-v0"),
    )
    y_star_check_id = "y-star-non-mutation-invariant-v0"
    mcp_check_id = "sandbox-mcp-non-bypass-check-v0"

    denied_scope = [
        "real canonical policy mutation",
        "real canonical update application",
        "durable approval DB write",
        "brain writeback",
        "memory ingestion",
        "strategy mutation",
        "direct Y* mutation",
        "live execution",
        "MCP execution",
        "external action",
        "network/API call",
        "L6 revenue opportunity discovery",
    ]

    approval_scope = {
        "scope_mode": "sandbox_pre_application_gate_replay_only",
        "allowed_subject_package_id": package_id,
        "allowed_patch_plan_id": patch_plan_id,
        "allowed_evidence_dossier_id": evidence_dossier_id,
        "allowed_rollback_plan_id": rollback_plan_id,
        "allowed_post_validation_plan_id": post_validation_plan_id,
        "may_validate_integrity": True,
        "may_validate_scope": True,
        "may_replay_state_machine": True,
        "may_replay_pre_application_gate": True,
        "may_authorize_real_application": False,
    }

    sandbox_record = {
        "schema_name": "ystar.sandbox_approval_record.instance",
        "schema_version": SCHEMA_VERSION,
        "approval_record_id": "sandbox-approval-record-instance-v0",
        "approval_subject_package_id": package_id,
        "approval_scope": approval_scope,
        "denied_scope": denied_scope,
        "approval_decision": "sandbox_valid_for_gate_replay_only",
        "approval_mode": "sandbox_approval_record_fixture",
        "approver_role_refs": ["owner_or_founder", "governance_reviewer", "safety_reviewer"],
        "proposer_ref": "canonical-update-package-candidate-v0-proposer-placeholder",
        "reviewer_ref": "governance-reviewer-placeholder",
        "release_operator_ref": "release-operator-placeholder",
        "rollback_operator_ref": "rollback-operator-placeholder",
        "evidence_dossier_id": evidence_dossier_id,
        "y_star_invariant_check_id": y_star_check_id,
        "mcp_non_bypass_check_id": mcp_check_id,
        "post_validation_plan_id": post_validation_plan_id,
        "rollback_plan_id": rollback_plan_id,
        "approval_timestamp_placeholder": "sandbox-static-timestamp-placeholder",
        "expiration_policy_ref": "approval_validity_revocation_policy/approval_expiration_policy.json",
        "revocation_policy_ref": "approval_validity_revocation_policy/approval_revocation_policy.json",
        "integrity_hash_placeholder": "pending-generated-placeholder",
        "parent_record_ref": "real_approval_decision_packet_fixture/real_approval_decision_packet_fixture.json",
        "audit_lineage_refs": [
            "approval_evidence_dossier/approval_evidence_dossier.json",
            "durable_approval_record_contract/approval_record_schema_v0.json",
            "real_application_boundary_gate/real_application_boundary_gate_contract.json",
        ],
        "application_status": "not_applied",
        "safety_flags": SAFETY_FLAGS,
        "record_mode": "sandbox_only",
        "durable_persistence_performed": False,
        "real_approval_granted": False,
        "real_application_authorized": False,
        "sandbox_gate_replay_authorized": True,
        "candidate_auto_approval_performed": False,
        "canonical_update_applied": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "evidence_refs": list(all_input_refs.values()),
        "sandbox_flags": SANDBOX_FLAGS,
    }
    sandbox_record["integrity_hash_placeholder"] = structural_hash_placeholder(sandbox_record)

    integrity_hash = {
        "schema_name": "ystar.sandbox_approval_record.integrity_hash",
        "schema_version": SCHEMA_VERSION,
        "hash_id": "sandbox-approval-record-integrity-hash-v0",
        "source_record_id": sandbox_record["approval_record_id"],
        "hash_algorithm_placeholder": "sha256-placeholder-no-secret",
        "hash_material_fields": [
            "approval_record_id",
            "approval_subject_package_id",
            "evidence_dossier_id",
            "rollback_plan_id",
            "post_validation_plan_id",
            "approval_mode",
        ],
        "integrity_hash_placeholder": sandbox_record["integrity_hash_placeholder"],
        "real_signature_material_used": False,
        "secret_material_used": False,
        "durable_persistence_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    required_field_checks = {
        field: field in sandbox_record and sandbox_record.get(field) not in (None, "")
        for field in APPROVAL_RECORD_FIELDS
    }
    integrity_validation = {
        "schema_name": "ystar.approval_record.integrity_validation_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "approval-record-integrity-validation-result-v0",
        "source_record_id": sandbox_record["approval_record_id"],
        "all_required_fields_present": all(required_field_checks.values()),
        "scope_present": bool(sandbox_record.get("approval_scope")),
        "denied_scope_present": bool(sandbox_record.get("denied_scope")),
        "evidence_dossier_present": bool(sandbox_record.get("evidence_dossier_id")),
        "rollback_plan_present": bool(sandbox_record.get("rollback_plan_id")),
        "post_validation_plan_present": bool(sandbox_record.get("post_validation_plan_id")),
        "expiration_policy_present": bool(sandbox_record.get("expiration_policy_ref")),
        "revocation_policy_present": bool(sandbox_record.get("revocation_policy_ref")),
        "integrity_hash_placeholder_present": bool(sandbox_record.get("integrity_hash_placeholder")),
        "no_silent_overwrite_semantics_defined": True,
        "durable_persistence_not_performed": True,
        "validation_status": "structurally_valid_for_sandbox_gate_replay",
        "gap_notes": [] if not missing_sources else ["optional or required source gaps recorded in input fixture"],
        "evidence_refs": [str(INPUT_REFS["approval_record_integrity_requirements"])],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    state_machine = {
        "schema_name": "ystar.approval_record.state_machine",
        "schema_version": SCHEMA_VERSION,
        "state_machine_id": "approval-record-state-machine-v0",
        "states": STATE_MACHINE_STATES,
        "allowed_transitions": [
            {"from": "draft", "to": "pending_review", "requires": "complete record fields"},
            {
                "from": "pending_review",
                "to": "sandbox_valid_for_gate_replay",
                "requires": "sandbox fixture validation only",
            },
            {
                "from": "sandbox_valid_for_gate_replay",
                "to": "real_approval_required",
                "requires": "future durable record and explicit approval workflow",
            },
            {"from": "pending_review", "to": "expired", "requires": "expiration policy"},
            {"from": "pending_review", "to": "revoked", "requires": "revocation policy"},
            {"from": "pending_review", "to": "invalidated", "requires": "invalidation trigger"},
            {
                "from": "real_approval_required",
                "to": "consumed_by_application",
                "requires": "future real approval and application; forbidden in L5.10",
            },
            {"from": "sandbox_valid_for_gate_replay", "to": "superseded", "requires": "newer package"},
        ],
        "forbidden_transitions": [
            {"from": "sandbox_valid_for_gate_replay", "to": "consumed_by_application"},
            {"from": "sandbox_valid_for_gate_replay", "to": "real_approved"},
            {"from": "draft", "to": "consumed_by_application"},
            {"from": "expired", "to": "sandbox_valid_for_gate_replay"},
            {"from": "revoked", "to": "sandbox_valid_for_gate_replay"},
            {"from": "invalidated", "to": "sandbox_valid_for_gate_replay"},
        ],
        "terminal_states": ["expired", "revoked", "invalidated", "consumed_by_application", "superseded"],
        "revocation_paths": ["pending_review -> revoked", "sandbox_valid_for_gate_replay -> revoked"],
        "expiration_paths": ["pending_review -> expired", "sandbox_valid_for_gate_replay -> expired"],
        "invalidation_paths": ["pending_review -> invalidated", "sandbox_valid_for_gate_replay -> invalidated"],
        "consumed_by_application_semantics": "future_only_requires_real_approval_and_real_application",
        "real_approval_required_before_real_application": True,
        "safety_flags": SAFETY_FLAGS,
    }

    state_transition_table = {
        "schema_name": "ystar.approval_record.state_transition_table",
        "schema_version": SCHEMA_VERSION,
        "state_machine_id": state_machine["state_machine_id"],
        "states": STATE_MACHINE_STATES,
        "transition_rows": state_machine["allowed_transitions"] + state_machine["forbidden_transitions"],
        "real_approved_state_defined_for_l5_10": False,
        "real_consumed_transition_allowed_for_l5_10": False,
        "safety_flags": SAFETY_FLAGS,
    }

    state_replay = {
        "schema_name": "ystar.sandbox_approval_record.state_replay",
        "schema_version": SCHEMA_VERSION,
        "state_replay_id": "sandbox-approval-record-state-replay-v0",
        "source_record_id": sandbox_record["approval_record_id"],
        "replayed_transitions": [
            {"from": "draft", "to": "pending_review", "result": "allowed_in_sandbox"},
            {
                "from": "pending_review",
                "to": "sandbox_valid_for_gate_replay",
                "result": "allowed_in_sandbox",
            },
        ],
        "transitions_not_taken": [
            "sandbox_valid_for_gate_replay -> real_approved",
            "sandbox_valid_for_gate_replay -> consumed_by_application",
            "real_approval_required -> consumed_by_application",
        ],
        "transitioned_to_real_approved": False,
        "transitioned_to_real_consumed_by_application": False,
        "current_sandbox_state": "sandbox_valid_for_gate_replay",
        "evidence_refs": ["approval_record_validity_state_machine/approval_record_state_machine.json"],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    validity_result = {
        "schema_name": "ystar.approval_record.validity_result",
        "schema_version": SCHEMA_VERSION,
        "validity_result_id": "approval-record-validity-result-v0",
        "source_record_id": sandbox_record["approval_record_id"],
        "current_sandbox_state": "sandbox_valid_for_gate_replay",
        "valid_for_sandbox_gate_replay": True,
        "valid_for_real_application": False,
        "real_approval_required_before_application": True,
        "durable_record_required_before_real_application": True,
        "expiration_policy_validated": True,
        "revocation_policy_validated": True,
        "evidence_bindings_validated": True,
        "y_star_non_mutation_binding_validated": True,
        "mcp_non_bypass_binding_validated": True,
        "evidence_refs": [INPUT_REFS["approval_validity_policy"]],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    invalid_variant_docs: dict[str, dict[str, Any]] = {}
    for key, spec in INVALID_VARIANTS.items():
        invalid_variant_docs[key] = {
            "schema_name": "ystar.sandbox_approval_record.invalid_variant",
            "schema_version": SCHEMA_VERSION,
            "variant_id": f"sandbox-{spec['variant_type']}-variant-v0",
            "variant_type": spec["variant_type"],
            "source_valid_record_id": sandbox_record["approval_record_id"],
            "changed_or_missing_fields": spec["changed_or_missing_fields"],
            "expected_gate_result": "blocked",
            "valid_for_sandbox_gate_replay": False,
            "valid_for_real_application": False,
            "deterministic_reason_codes": spec["reason_codes"],
            "evidence_refs": [INPUT_REFS["approval_invalidation_triggers"]],
            "safety_flags": SAFETY_FLAGS,
        }

    invalid_gate_results = {
        "schema_name": "ystar.approval_record.invalid_gate_results",
        "schema_version": SCHEMA_VERSION,
        "result_id": "invalid-record-gate-results-v0",
        "source_valid_record_id": sandbox_record["approval_record_id"],
        "gate_results": {
            key: {
                "variant_id": doc["variant_id"],
                "gate_result": "blocked",
                "valid_for_sandbox_gate_replay": False,
                "valid_for_real_application": False,
                "reason_codes": doc["deterministic_reason_codes"],
            }
            for key, doc in invalid_variant_docs.items()
        },
        "all_invalid_variants_blocked": True,
        "safety_flags": SAFETY_FLAGS,
    }

    valid_gate_replay = {
        "schema_name": "ystar.approval_record.valid_gate_replay_result",
        "schema_version": SCHEMA_VERSION,
        "gate_replay_id": "valid-record-gate-replay-result-v0",
        "source_sandbox_record_id": sandbox_record["approval_record_id"],
        "gate_name": "real_application_boundary_gate_sandbox_replay",
        "gate_result": "sandbox_gate_replay_passed_real_application_still_blocked",
        "allowed_scope": ["sandbox pre-application gate replay", "structural validation reporting"],
        "denied_scope": denied_scope,
        "real_application_authorized": False,
        "sandbox_pre_application_replay_authorized": True,
        "durable_real_record_required_before_real_application": True,
        "post_approval_preflight_required": True,
        "snapshot_required": True,
        "rollback_required": True,
        "y_star_non_mutation_check_required": True,
        "mcp_non_bypass_check_required": True,
        "evidence_refs": [INPUT_REFS["real_application_boundary_gate_contract"]],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    invalid_gate_matrix = {
        "schema_name": "ystar.approval_record.invalid_gate_replay_matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "invalid-record-gate-replay-matrix-v0",
        "source_valid_record_id": sandbox_record["approval_record_id"],
        "invalid_record_results": {
            key: {
                "variant_id": doc["variant_id"],
                "gate_result": "blocked",
                "real_application_authorized": False,
                "sandbox_pre_application_replay_authorized": False,
                "reason_codes": doc["deterministic_reason_codes"],
            }
            for key, doc in invalid_variant_docs.items()
        },
        "all_invalid_variants_blocked": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    gate_reason_codes = {
        "schema_name": "ystar.approval_record.gate_reason_codes",
        "schema_version": SCHEMA_VERSION,
        "reason_code_set_id": "approval-record-gate-reason-codes-v0",
        "reason_codes": {
            code: {"code": code, "deterministic_meaning": code.replace("_", " ")}
            for code in GATE_REASON_CODES
        },
        "safety_flags": SAFETY_FLAGS,
    }

    event_index = [
        {"event_type": "record_created_in_sandbox", "event_ref": "sandbox_approval_record_instance/sandbox_approval_record_instance.json"},
        {"event_type": "integrity_validated", "event_ref": "approval_record_integrity_validation/approval_record_integrity_validation_result.json"},
        {"event_type": "scope_validated", "event_ref": "sandbox_approval_record_instance/sandbox_approval_record_scope_binding.json"},
        {"event_type": "state_replayed", "event_ref": "approval_record_validity_state_machine/sandbox_approval_record_state_replay.json"},
        {"event_type": "invalid_variant_generated", "event_ref": "expiration_revocation_replay/invalid_record_gate_results.json"},
        {"event_type": "gate_replayed", "event_ref": "approval_record_pre_application_gate_replay/valid_record_gate_replay_result.json"},
        {"event_type": "invalid_variant_blocked", "event_ref": "approval_record_pre_application_gate_replay/invalid_record_gate_replay_matrix.json"},
        {"event_type": "cieu_fixture_emitted", "event_ref": "approval_record_cieu_residual/approval_record_cieu_event_fixture.json"},
    ]

    audit_lineage = {
        "schema_name": "ystar.sandbox_approval_record.audit_lineage",
        "schema_version": SCHEMA_VERSION,
        "audit_lineage_id": "sandbox-approval-record-audit-lineage-v0",
        "source_approval_record_id": sandbox_record["approval_record_id"],
        "source_package_id": package_id,
        "source_evidence_dossier_id": evidence_dossier_id,
        "source_invariant_check_ids": [y_star_check_id, mcp_check_id],
        "source_preflight_plan_id": post_validation_plan_id,
        "source_rollback_plan_id": rollback_plan_id,
        "generated_record_variants": [doc["variant_id"] for doc in invalid_variant_docs.values()],
        "gate_replay_results": [
            valid_gate_replay["gate_replay_id"],
            invalid_gate_matrix["matrix_id"],
        ],
        "integrity_validation_result_id": integrity_validation["validation_result_id"],
        "state_replay_result_id": state_replay["state_replay_id"],
        "cieu_event_refs": ["approval_record_cieu_residual/approval_record_cieu_event_fixture.json"],
        "durable_persistence_performed": False,
        "real_approval_granted": False,
        "real_application_performed": False,
        "evidence_refs": list(all_input_refs.values()),
        "safety_flags": SAFETY_FLAGS,
    }

    predicted_outcome = {
        "schema_name": "ystar.approval_record.predicted_outcome",
        "schema_version": SCHEMA_VERSION,
        "predicted_outcome_id": "approval-record-predicted-outcome-v0",
        "expected_results": [
            "sandbox approval record created",
            "integrity validated",
            "state machine replayed",
            "invalid variants generated and blocked",
            "pre-application gate replayed",
            "no real approval",
            "no durable record write",
            "no real application",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    mock_actual_outcome = {
        "schema_name": "ystar.approval_record.mock_actual_outcome",
        "schema_version": SCHEMA_VERSION,
        "mock_actual_outcome_id": "approval-record-mock-actual-outcome-v0",
        "actual_results": predicted_outcome["expected_results"],
        "real_approval_granted": False,
        "durable_approval_record_written": False,
        "real_application_authorized": False,
        "real_application_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    residual_delta = {
        "schema_name": "ystar.approval_record.residual_delta",
        "schema_version": SCHEMA_VERSION,
        "residual_delta_id": "approval-record-residual-delta-v0",
        "source_predicted_outcome_id": predicted_outcome["predicted_outcome_id"],
        "source_mock_actual_outcome_id": mock_actual_outcome["mock_actual_outcome_id"],
        "residual_classes": [
            {
                "class": residual_class,
                "status": "resolved_in_sandbox_or_blocked_for_real",
                "structural_delta": "sandbox artifact generated while real path remains blocked",
            }
            for residual_class in RESIDUAL_CLASSES
        ],
        "residual_summary": "Sandbox lifecycle matched expected artifact-only path; real approval/application/persistence blockers remain in place.",
        "learning_candidate_generated": False,
        "semantic_truth_scoring_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    cieu_event = {
        "schema_name": "ystar.approval_record.cieu_event_fixture",
        "schema_version": SCHEMA_VERSION,
        "event_id": "approval-record-cieu-event-fixture-v0",
        "event_mode": "approval_record_sandbox_fixture",
        "X_t": {
            "source_contract": INPUT_REFS["durable_approval_record_contract"],
            "source_schema": INPUT_REFS["approval_record_schema"],
            "source_evidence_dossier": INPUT_REFS["approval_evidence_dossier"],
        },
        "U_t": {
            "operation": "controlled approval record sandbox lifecycle",
            "record_id": sandbox_record["approval_record_id"],
            "gate_replay_id": valid_gate_replay["gate_replay_id"],
        },
        "Y_star_t": {
            "declared_target": (
                "Create and validate a sandbox approval record lifecycle without granting "
                "real approval or durable persistence."
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
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    readiness = {
        "schema_name": "ystar.controlled_approval_record.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "controlled-approval-record-readiness-v0",
        "sandbox_approval_record_created": True,
        "integrity_validation_generated": True,
        "scope_validation_generated": True,
        "evidence_binding_validation_generated": True,
        "validity_state_machine_generated": True,
        "expiration_revocation_replay_generated": True,
        "valid_record_gate_replay_generated": True,
        "invalid_record_gate_blocking_generated": True,
        "audit_lineage_generated": True,
        "cieu_fixture_generated": True,
        "durable_persistence_still_blocked": True,
        "real_approval_still_blocked": True,
        "real_application_still_blocked": True,
        "brain_writeback_still_blocked": True,
        "memory_ingestion_still_blocked": True,
        "y_star_direct_mutation_still_blocked": True,
        "mcp_execution_still_blocked": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "ready_for_l5_11_controlled_real_release_preflight": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
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
        "real_approval_granted": False,
        "real_application_authorized": False,
        "durable_approval_record_written": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "strategy_mutation_enabled": False,
        "candidate_auto_approval_enabled": False,
        "revenue_opportunity_discovery_enabled": False,
        "sandbox_approval_record_lifecycle_artifacts_only": True,
        "missing_sources": missing_sources,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    sandbox_contract = {
        "schema_name": "ystar.controlled_approval_record_sandbox.contract",
        "schema_version": SCHEMA_VERSION,
        "sandbox_name": "L5.10 Controlled Approval Record Sandbox + Validity / Revocation Replay v0",
        "purpose": (
            "Generate a sandbox-only approval record lifecycle from the L5.9 durable "
            "approval record contract, then validate integrity, scope, evidence binding, "
            "expiration/revocation, state replay, valid gate replay, and invalid record blocking."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "optional_inputs": list(OPTIONAL_INPUT_REFS.values()),
        "sandbox_stages": SANDBOX_STAGES,
        "required_outputs": [
            "sandbox approval record instance",
            "integrity validation",
            "validity state machine replay",
            "invalid record variants",
            "valid and invalid pre-application gate replay",
            "audit lineage",
            "approval record CIEU-like fixture",
            "readiness",
        ],
        "approval_record_lifecycle_requirements": [
            "record is sandbox_only",
            "state replay cannot transition to real approved",
            "state replay cannot transition to consumed by real application",
        ],
        "integrity_validation_requirements": [
            "required fields present",
            "scope and denied scope present",
            "evidence, rollback, post-validation, expiration, revocation, and integrity bindings present",
        ],
        "validity_validation_requirements": [
            "valid for sandbox gate replay only",
            "invalid for real application",
            "real approval and durable record required before real application",
        ],
        "revocation_validation_requirements": [
            "expired, revoked, tampered, wrong-scope, and missing-evidence records are blocked",
            "approval cannot override Y* non-mutation or MCP non-bypass invariants",
        ],
        "pre_application_gate_replay_requirements": [
            "valid sandbox record may pass sandbox replay only",
            "real application remains blocked",
            "invalid variants are deterministically blocked",
        ],
        "audit_lineage_requirements": [
            "record creation, integrity validation, state replay, invalid variants, gate replay, and CIEU fixture are indexed",
            "durable persistence remains false",
        ],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "real approval",
            "durable approval persistence",
            "real canonical update application",
            "brain or memory writeback",
            "MCP execution",
            "L6 revenue opportunity discovery",
        ],
    }

    input_fixture = {
        "schema_name": "ystar.controlled_approval_record_sandbox.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "input_refs": INPUT_REFS,
        "optional_input_refs": OPTIONAL_INPUT_REFS,
        "input_statuses": input_statuses,
        "missing_sources": missing_sources,
        "gap_handling": "missing optional sources are recorded and do not trigger destructive failure",
        "safety_flags": SAFETY_FLAGS,
    }

    run = {
        "schema_name": "ystar.controlled_approval_record_sandbox.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "controlled-approval-record-sandbox-run-v0",
        "contract_ref": "controlled_approval_record_sandbox/controlled_approval_record_sandbox_contract.json",
        "input_fixture_ref": "controlled_approval_record_sandbox/controlled_approval_record_sandbox_input_fixture.json",
        "sandbox_stages_completed": SANDBOX_STAGES,
        "record_id": sandbox_record["approval_record_id"],
        "integrity_validation_status": integrity_validation["validation_status"],
        "state_replay_state": state_replay["current_sandbox_state"],
        "valid_gate_replay_result": valid_gate_replay["gate_result"],
        "invalid_record_variants_blocked": True,
        "real_approval_granted": False,
        "durable_approval_record_written": False,
        "real_application_authorized": False,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    sandbox_summary = {
        "schema_name": "ystar.controlled_approval_record_sandbox.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_10_controlled_approval_record_sandbox_defined": True,
        "sandbox_approval_record_instance_generated": True,
        "integrity_validation_generated": True,
        "validity_state_machine_replay_generated": True,
        "invalid_record_variants_generated_and_blocked": True,
        "valid_sandbox_record_gate_replay_generated": True,
        "audit_lineage_generated": True,
        "approval_record_cieu_like_fixture_generated": True,
        "real_approval_granted": False,
        "durable_approval_record_written": False,
        "real_application_authorized": False,
        "next_required_milestone": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    field_map = {
        "schema_name": "ystar.sandbox_approval_record.field_map",
        "schema_version": SCHEMA_VERSION,
        "source_schema_ref": INPUT_REFS["approval_record_schema"],
        "source_schema_required_fields": schema.get("required_fields", APPROVAL_RECORD_FIELDS),
        "sandbox_record_ref": "sandbox_approval_record_instance/sandbox_approval_record_instance.json",
        "field_map": {
            field: {
                "present": field in sandbox_record,
                "source": "L5.9 schema field",
                "sandbox_value_class": type(sandbox_record.get(field)).__name__,
            }
            for field in APPROVAL_RECORD_FIELDS
        },
        "all_required_schema_fields_mapped": all(required_field_checks.values()),
        "durable_persistence_performed": False,
        "real_approval_granted": False,
        "safety_flags": SAFETY_FLAGS,
    }

    scope_binding = {
        "schema_name": "ystar.sandbox_approval_record.scope_binding",
        "schema_version": SCHEMA_VERSION,
        "scope_binding_id": "sandbox-approval-record-scope-binding-v0",
        "source_record_id": sandbox_record["approval_record_id"],
        "exact_package_id": package_id,
        "exact_versioned_patch_plan_id": patch_plan_id,
        "exact_evidence_dossier_id": evidence_dossier_id,
        "exact_rollback_plan_id": rollback_plan_id,
        "exact_post_validation_plan_id": post_validation_plan_id,
        "exact_denied_scope": denied_scope,
        "approval_cannot_be_reused_for_other_package_version_or_scope": True,
        "scope_valid_for_sandbox_gate_replay_only": True,
        "valid_for_real_application": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    denied_scope_binding = {
        "schema_name": "ystar.sandbox_approval_record.denied_scope_binding",
        "schema_version": SCHEMA_VERSION,
        "source_record_id": sandbox_record["approval_record_id"],
        "denied_scope": denied_scope,
        "real_approval_denied": True,
        "real_application_denied": True,
        "durable_persistence_denied": True,
        "brain_memory_write_denied": True,
        "direct_y_star_mutation_denied": True,
        "mcp_execution_denied": True,
        "l6_revenue_discovery_denied": True,
        "safety_flags": SAFETY_FLAGS,
    }

    required_fields_check = {
        "schema_name": "ystar.approval_record.required_fields_check",
        "schema_version": SCHEMA_VERSION,
        "check_id": "approval-record-required-fields-check-v0",
        "source_record_id": sandbox_record["approval_record_id"],
        "required_fields": APPROVAL_RECORD_FIELDS,
        "field_results": required_field_checks,
        "all_required_fields_present": all(required_field_checks.values()),
        "safety_flags": SAFETY_FLAGS,
    }

    parent_child_lineage = {
        "schema_name": "ystar.approval_record.parent_child_lineage",
        "schema_version": SCHEMA_VERSION,
        "lineage_id": "approval-record-parent-child-lineage-v0",
        "parent_record_ref": sandbox_record["parent_record_ref"],
        "child_record_id": sandbox_record["approval_record_id"],
        "child_record_mode": "sandbox_only",
        "real_durable_child_record_created": False,
        "lineage_notes": [
            "L5.9 decision packet fixture remains not_granted.",
            "L5.10 sandbox record is generated from contract shape only.",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    cieu_summary = {
        "schema_name": "ystar.approval_record.cieu_summary",
        "schema_version": SCHEMA_VERSION,
        "approval_record_cieu_like_fixture_generated": True,
        "approval_record_residual_delta_generated": True,
        "persistence_enabled": False,
        "db_write_performed": False,
        "durable_approval_record_written": False,
        "residual_classes": RESIDUAL_CLASSES,
        "safety_flags": SAFETY_FLAGS,
    }

    # Top-level pack.
    write_text(
        SANDBOX / "README.md",
        markdown_report(
            "L5.10 Controlled Approval Record Sandbox",
            [
                "Defines sandbox-only approval record lifecycle proof artifacts.",
                "No real approval, durable persistence, or real canonical application is granted.",
                "Expired, revoked, tampered, wrong-scope, and missing-evidence records are blocked.",
            ],
        ),
    )
    write_json(SANDBOX / "controlled_approval_record_sandbox_contract.json", sandbox_contract)
    write_json(SANDBOX / "controlled_approval_record_sandbox_input_fixture.json", input_fixture)
    write_json(SANDBOX / "controlled_approval_record_sandbox_run.json", run)
    write_json(SANDBOX / "controlled_approval_record_sandbox_summary.json", sandbox_summary)
    write_text(
        SANDBOX / "controlled_approval_record_sandbox_report.md",
        markdown_report(
            "Controlled Approval Record Sandbox Report",
            [
                "Sandbox record lifecycle generated: true",
                "Real approval granted: false",
                "Durable approval record written: false",
                "Real application authorized: false",
                f"Ready for {NEXT_MILESTONE}: true",
            ],
        ),
    )

    # Sandbox record pack.
    write_json(RECORD / "sandbox_approval_record_instance.json", sandbox_record)
    write_json(RECORD / "sandbox_approval_record_field_map.json", field_map)
    write_json(RECORD / "sandbox_approval_record_scope_binding.json", scope_binding)
    write_json(RECORD / "sandbox_approval_record_denied_scope_binding.json", denied_scope_binding)
    write_json(
        RECORD / "sandbox_approval_record_summary.json",
        {
            "schema_name": "ystar.sandbox_approval_record.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_approval_record_instance_generated": True,
            "record_mode": "sandbox_only",
            "durable_persistence_performed": False,
            "real_approval_granted": False,
            "real_application_authorized": False,
            "sandbox_gate_replay_authorized": True,
            "canonical_update_applied": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
            "direct_y_star_mutation_performed": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(
        RECORD / "sandbox_approval_record_report.md",
        markdown_report(
            "Sandbox Approval Record Report",
            [
                "The sandbox record satisfies the L5.9 schema fields.",
                "The record is valid for sandbox gate replay only.",
                "It cannot authorize real application or durable approval persistence.",
            ],
        ),
    )

    # Integrity pack.
    write_json(INTEGRITY / "sandbox_approval_record_integrity_hash.json", integrity_hash)
    write_json(INTEGRITY / "approval_record_integrity_validation_result.json", integrity_validation)
    write_json(INTEGRITY / "approval_record_required_fields_check.json", required_fields_check)
    write_text(
        INTEGRITY / "approval_record_integrity_gap_report.md",
        markdown_report(
            "Approval Record Integrity Gap Report",
            [
                f"Validation status: {integrity_validation['validation_status']}",
                f"Missing sources: {missing_sources or 'none'}",
                "No secrets, credentials, or real signatures were used.",
            ],
        ),
    )
    write_json(
        INTEGRITY / "approval_record_integrity_summary.json",
        {
            "schema_name": "ystar.approval_record.integrity_summary",
            "schema_version": SCHEMA_VERSION,
            "integrity_validation_generated": True,
            "validation_status": integrity_validation["validation_status"],
            "all_required_fields_present": integrity_validation["all_required_fields_present"],
            "durable_persistence_not_performed": True,
            "real_signature_material_used": False,
            "secret_material_used": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )

    # State machine pack.
    write_json(STATE_MACHINE / "approval_record_state_machine.json", state_machine)
    write_json(STATE_MACHINE / "approval_record_state_transition_table.json", state_transition_table)
    write_json(STATE_MACHINE / "sandbox_approval_record_state_replay.json", state_replay)
    write_json(STATE_MACHINE / "approval_record_validity_result.json", validity_result)
    write_json(
        STATE_MACHINE / "approval_record_state_machine_summary.json",
        {
            "schema_name": "ystar.approval_record.state_machine_summary",
            "schema_version": SCHEMA_VERSION,
            "validity_state_machine_generated": True,
            "sandbox_state_machine_replayed": True,
            "current_sandbox_state": state_replay["current_sandbox_state"],
            "valid_for_sandbox_gate_replay": True,
            "valid_for_real_application": False,
            "real_approval_required_before_application": True,
            "durable_record_required_before_real_application": True,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(
        STATE_MACHINE / "approval_record_state_machine_report.md",
        markdown_report(
            "Approval Record State Machine Report",
            [
                "Sandbox replay stops at sandbox_valid_for_gate_replay.",
                "No real approved transition exists in L5.10.",
                "Consumed-by-application remains future-only.",
            ],
        ),
    )

    # Expiration/revocation pack.
    for key, spec in INVALID_VARIANTS.items():
        write_json(REVOCATION / spec["filename"], invalid_variant_docs[key])
    write_json(REVOCATION / "invalid_record_gate_results.json", invalid_gate_results)
    write_json(
        REVOCATION / "expiration_revocation_replay_summary.json",
        {
            "schema_name": "ystar.expiration_revocation_replay.summary",
            "schema_version": SCHEMA_VERSION,
            "expiration_revocation_replay_generated": True,
            "invalid_record_variants_generated_and_blocked": True,
            "expired_record_blocked": True,
            "revoked_record_blocked": True,
            "tampered_record_blocked": True,
            "wrong_scope_record_blocked": True,
            "missing_evidence_record_blocked": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(
        REVOCATION / "expiration_revocation_replay_report.md",
        markdown_report(
            "Expiration Revocation Replay Report",
            [
                "Expired records are blocked.",
                "Revoked records are blocked.",
                "Tampered, wrong-scope, and missing-evidence records are blocked.",
            ],
        ),
    )

    # Gate replay pack.
    write_json(GATE / "valid_record_gate_replay_result.json", valid_gate_replay)
    write_json(GATE / "invalid_record_gate_replay_matrix.json", invalid_gate_matrix)
    write_json(GATE / "approval_record_gate_reason_codes.json", gate_reason_codes)
    write_json(
        GATE / "pre_application_gate_replay_summary.json",
        {
            "schema_name": "ystar.approval_record.pre_application_gate_replay_summary",
            "schema_version": SCHEMA_VERSION,
            "valid_record_gate_replay_generated": True,
            "valid_record_gate_result": valid_gate_replay["gate_result"],
            "invalid_record_gate_blocking_generated": True,
            "all_invalid_variants_blocked": True,
            "real_application_authorized": False,
            "sandbox_pre_application_replay_authorized": True,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(
        GATE / "pre_application_gate_replay_report.md",
        markdown_report(
            "Pre-Application Gate Replay Report",
            [
                "The valid sandbox record passes sandbox replay only.",
                "Real application remains blocked because no durable real approval record exists.",
                "Every invalid record variant is blocked with deterministic reason codes.",
            ],
        ),
    )

    # Audit pack.
    write_json(AUDIT / "sandbox_approval_record_audit_lineage.json", audit_lineage)
    write_json(AUDIT / "approval_record_parent_child_lineage.json", parent_child_lineage)
    write_json(
        AUDIT / "approval_record_event_index.json",
        {
            "schema_name": "ystar.approval_record.event_index",
            "schema_version": SCHEMA_VERSION,
            "event_index_id": "approval-record-event-index-v0",
            "events": event_index,
            "event_types": [item["event_type"] for item in event_index],
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(
        AUDIT / "approval_record_audit_gap_report.md",
        markdown_report(
            "Approval Record Audit Gap Report",
            [
                "No durable record exists yet by design.",
                "Future L5.11 must define controlled real release preflight before real application can be considered.",
            ],
        ),
    )
    write_json(
        AUDIT / "approval_record_audit_summary.json",
        {
            "schema_name": "ystar.approval_record.audit_summary",
            "schema_version": SCHEMA_VERSION,
            "audit_lineage_generated": True,
            "event_index_generated": True,
            "durable_persistence_performed": False,
            "real_approval_granted": False,
            "real_application_performed": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )

    # CIEU/residual pack.
    write_json(CIEU / "approval_record_cieu_event_fixture.json", cieu_event)
    write_json(CIEU / "approval_record_predicted_outcome.json", predicted_outcome)
    write_json(CIEU / "approval_record_mock_actual_outcome.json", mock_actual_outcome)
    write_json(CIEU / "approval_record_residual_delta.json", residual_delta)
    write_json(CIEU / "approval_record_cieu_summary.json", cieu_summary)
    write_text(
        CIEU / "approval_record_cieu_report.md",
        markdown_report(
            "Approval Record CIEU Report",
            [
                "CIEU-like fixture emitted without persistence.",
                "Residual classes are deterministic structural checks only.",
                "No durable approval record was written.",
            ],
        ),
    )

    # Readiness pack.
    write_json(READINESS / "controlled_approval_record_readiness.json", readiness)
    write_text(
        READINESS / "controlled_approval_record_readiness.md",
        markdown_report(
            "Controlled Approval Record Readiness",
            [
                f"sandbox_approval_record_created: {bool_summary(readiness['sandbox_approval_record_created'])}",
                f"valid_record_gate_replay_generated: {bool_summary(readiness['valid_record_gate_replay_generated'])}",
                f"durable_persistence_still_blocked: {bool_summary(readiness['durable_persistence_still_blocked'])}",
                f"real_approval_still_blocked: {bool_summary(readiness['real_approval_still_blocked'])}",
                f"real_application_still_blocked: {bool_summary(readiness['real_application_still_blocked'])}",
                f"ready_for_l5_11_controlled_real_release_preflight: {bool_summary(readiness['ready_for_l5_11_controlled_real_release_preflight'])}",
                "ready_for_l6_revenue_opportunity_discovery: false",
            ],
        ),
    )
    write_json(
        READINESS / "l5_11_recommended_next_step.json",
        {
            "schema_name": "ystar.controlled_approval_record.next_step",
            "schema_version": SCHEMA_VERSION,
            "recommended_next_step": NEXT_MILESTONE,
            "purpose": (
                "Define a controlled real release preflight boundary that can consume a "
                "valid durable approval record without enabling real application in L5.10."
            ),
            "l6_revenue_opportunity_discovery_remains_blocked": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )

    print("L5.10 controlled approval record sandbox artifacts generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
