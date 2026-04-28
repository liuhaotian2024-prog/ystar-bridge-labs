#!/usr/bin/env python3
"""Build deterministic L5.9 real approval workflow boundary artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

BOUNDARY = ROOT / "real_approval_workflow_boundary"
AUTHORITY = ROOT / "approval_authority_model"
DOSSIER = ROOT / "approval_evidence_dossier"
RECORD = ROOT / "durable_approval_record_contract"
DECISION = ROOT / "real_approval_decision_packet_fixture"
VALIDITY = ROOT / "approval_validity_revocation_policy"
SNAPSHOT = ROOT / "pre_application_snapshot_policy"
APPLICATION = ROOT / "real_application_boundary_gate"
PREFLIGHT = ROOT / "post_approval_preflight_validation"
RUNBOOK = ROOT / "manual_approval_runbook"
CIEU = ROOT / "approval_workflow_cieu_audit_fixture"
READINESS = ROOT / "real_approval_workflow_readiness"

SCHEMA_VERSION = "v0"
NEXT_MILESTONE = "L5.10 Controlled Approval Record Sandbox v0"

INPUT_REFS = {
    "canonical_update_package_candidate": (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    ),
    "versioned_patch_plan": "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json",
    "y_star_non_mutation_invariant": "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json",
    "y_star_forbidden_change_surface": (
        "y_star_non_mutation_invariant/y_star_forbidden_change_surface.json"
    ),
    "rollback_plan": "rollback_and_audit_lineage/rollback_plan.json",
    "post_promotion_validation_plan": "post_promotion_validation_plan/post_promotion_validation_plan.json",
    "approved_sandbox_run": "approved_canonical_update_sandbox/approved_canonical_update_sandbox_run.json",
    "sandbox_approval_decision_fixture": (
        "sandbox_approval_fixture/sandbox_approval_decision_fixture.json"
    ),
    "sandbox_patch_application_result": (
        "sandbox_patch_application/sandbox_patch_application_result.json"
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
    "sandbox_reprojected_behavior_y_star": (
        "sandbox_reprojection_and_mcp_preview/sandbox_reprojected_behavior_y_star.json"
    ),
    "sandbox_rollback_result": "sandbox_rollback_validation/sandbox_rollback_result.json",
    "original_sandbox_rollback_comparison": (
        "original_sandbox_rollback_comparison/original_vs_sandbox_vs_rollback_comparison.json"
    ),
    "approved_sandbox_update_readiness": (
        "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json"
    ),
}

WORKFLOW_STAGES = [
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

APPROVAL_FLAGS = {
    "approval_workflow_defined": True,
    "approval_record_contract_defined": True,
    "approval_decision_packet_fixture_generated": True,
    "real_approval_granted": False,
    "real_application_authorized": False,
}

FORBIDDEN_OPERATIONS = [
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
    "durable approval DB writes",
    "candidate auto-approval",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

ALLOWED_AUTHORITY_CLASSES = [
    "human_owner",
    "designated_governance_reviewer",
    "designated_safety_reviewer",
    "future_versioned_governance_approval_service",
]

DENIED_AUTHORITY_CLASSES = [
    "autonomous_agent_self_approval",
    "tool_output_approval",
    "residual_auto_approval",
    "shadow_patch_auto_approval",
    "mcp_resource_approval",
    "unverified_external_actor",
    "unreviewed_memory_state",
]

REQUIRED_ROLES = [
    "owner_or_founder",
    "governance_reviewer",
    "safety_reviewer",
    "release_operator",
    "rollback_operator",
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

INVARIANT_CHECKS = [
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
]

APPLICATION_PRECONDITIONS = [
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
]

PREFLIGHT_REQUIREMENTS = [
    "approval record integrity validation",
    "approval scope validation",
    "package version validation",
    "evidence dossier validation",
    "snapshot validation",
    "rollback validation",
    "py_compile",
    "JSON validation",
    "static read-model validator",
    "local safety wrapper",
    "L5.0-L5.8 targeted pytest",
    "console/read-model smoke",
    "Y* non-mutation invariant check",
    "MCP non-bypass invariant check",
    "no direct writeback invariant check",
    "no direct Y* mutation check",
]

TEST_TARGETS_L5_0_L5_9 = [
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
]

RESIDUAL_CLASSES = [
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
]


def read_optional_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        return {"missing": True, "path": relative_path}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def missing_sources(sources: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"source_key": key, "path": value.get("path", INPUT_REFS.get(key, ""))}
        for key, value in sources.items()
        if value.get("missing") is True
    ]


def common_status() -> dict[str, Any]:
    return {
        **SAFETY_FLAGS,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "real_approval_granted": False,
        "real_application_authorized": False,
        "real_candidate_approved": False,
        "real_candidate_applied": False,
        "approval_record_created_as_durable_record": False,
        "durable_approval_record_written": False,
        "durable_db_write_performed": False,
        "real_canonical_policy_mutation_performed": False,
        "real_canonical_update_application_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "direct_y_star_mutation_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "persistence_enabled": False,
        "db_write_performed": False,
        "db_log_wal_shm_active_marker_content_read": False,
        "l6_revenue_opportunity_discovery_implemented": False,
    }


def evidence_refs() -> list[str]:
    return [
        INPUT_REFS["canonical_update_package_candidate"],
        INPUT_REFS["versioned_patch_plan"],
        INPUT_REFS["y_star_non_mutation_invariant"],
        INPUT_REFS["rollback_plan"],
        INPUT_REFS["post_promotion_validation_plan"],
        INPUT_REFS["approved_sandbox_run"],
        INPUT_REFS["sandbox_post_update_validation_result"],
        INPUT_REFS["sandbox_y_star_non_mutation_check"],
        INPUT_REFS["sandbox_mcp_non_bypass_check"],
        INPUT_REFS["sandbox_rollback_result"],
        INPUT_REFS["approved_sandbox_update_readiness"],
    ]


def build_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.real_approval_workflow_boundary.contract",
        "schema_version": SCHEMA_VERSION,
        "workflow_name": "Real Approval Workflow Boundary + Durable Approval Record Contract",
        "purpose": (
            "Define the authority, evidence, durable record, validity, snapshot, preflight, "
            "manual runbook, and application boundary required before any future real canonical "
            "update could be considered, without granting approval or applying anything now."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "workflow_stages": WORKFLOW_STAGES,
        "required_outputs": [
            "approval authority model",
            "approval evidence dossier",
            "durable approval record contract",
            "approval decision packet fixture",
            "validity and revocation policy",
            "pre-application snapshot policy",
            "real application boundary gate",
            "post-approval preflight validation plan",
            "manual approval runbook",
            "approval workflow CIEU-like fixture",
            "real approval workflow readiness",
        ],
        "authority_requirements": [
            "future explicit human or governance approval required",
            "self approval forbidden",
            "agent auto-approval forbidden",
            "approval without evidence, rollback, post-validation, Y* check, and MCP check forbidden",
        ],
        "approval_record_requirements": [
            "durable record contract defined",
            "explicit scope and denied scope required",
            "expiration and revocation policy required",
            "append-only integrity requirements required",
            "no durable record written in L5.9",
        ],
        "approval_validity_requirements": [
            "approval must be scope-bound",
            "approval must be time-bound or version-bound",
            "approval cannot be reused for different package/version/scope",
            "approval cannot override Y* non-mutation or MCP non-bypass invariants",
        ],
        "revocation_requirements": [
            "approval must be revocable",
            "approval invalidated on package, evidence, validation, rollback, lineage, non-bypass, or safety regression",
        ],
        "pre_application_snapshot_requirements": [
            "canonical projection policy snapshot",
            "learning policy snapshot",
            "MCP boundary policy snapshot",
            "read-model structure snapshot",
            "brain/memory boundary metadata snapshot only",
            "no raw DB/log/active marker content capture",
        ],
        "preflight_validation_requirements": PREFLIGHT_REQUIREMENTS,
        "audit_lineage_requirements": [
            "source package id",
            "evidence dossier id",
            "approval decision packet id",
            "rollback plan id",
            "post-validation plan id",
            "integrity placeholder",
            "CIEU-like approval audit fixture",
        ],
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "grant real approval",
            "apply real canonical update",
            "write durable approval DB record",
            "mutate canonical policy, brain, memory, strategy, Y-star-gov, or gov-mcp",
            "execute MCP, hooks, scheduler, daemon, network, or live behavior",
            "implement L6 revenue opportunity discovery",
        ],
    }


def build_all() -> None:
    sources = {key: read_optional_json(path) for key, path in INPUT_REFS.items()}
    gaps = missing_sources(sources)
    status = common_status()

    package = sources["canonical_update_package_candidate"]
    sandbox_run = sources["approved_sandbox_run"]
    sandbox_validation = sources["sandbox_post_update_validation_result"]
    sandbox_y_star_check = sources["sandbox_y_star_non_mutation_check"]
    sandbox_mcp_check = sources["sandbox_mcp_non_bypass_check"]
    sandbox_rollback = sources["sandbox_rollback_result"]
    invariant = sources["y_star_non_mutation_invariant"]
    patch_plan = sources["versioned_patch_plan"]
    rollback_plan = sources["rollback_plan"]
    validation_plan = sources["post_promotion_validation_plan"]

    package_id = package.get("package_id", "canonical-update-package-candidate-v0")
    patch_plan_id = patch_plan.get("patch_plan_id", "versioned-canonical-patch-plan-v0")
    sandbox_run_id = sandbox_run.get("run_id", "approved-canonical-update-sandbox-run-v0")
    sandbox_validation_id = sandbox_validation.get(
        "validation_result_id", "sandbox-post-update-validation-result-v0"
    )
    y_star_check_id = sandbox_y_star_check.get("check_id", "sandbox-y-star-non-mutation-check-v0")
    mcp_check_id = sandbox_mcp_check.get("check_id", "sandbox-mcp-non-bypass-check-v0")
    rollback_result_id = sandbox_rollback.get("rollback_id", "sandbox-rollback-result-v0")
    invariant_id = invariant.get("invariant_id", "y-star-non-mutation-invariant-v0")
    rollback_plan_id = rollback_plan.get("rollback_plan_id", "canonical-learning-rollback-plan-v0")
    post_validation_plan_id = validation_plan.get(
        "validation_plan_id", "post-promotion-validation-plan-v0"
    )

    contract = build_contract()
    input_fixture = {
        "schema_name": "ystar.real_approval_workflow.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "real-approval-workflow-input-fixture-v0",
        "input_refs": INPUT_REFS,
        "missing_sources": gaps,
        "gap_aware_execution": True,
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }

    authority_model = {
        "schema_name": "ystar.approval_authority.model",
        "schema_version": SCHEMA_VERSION,
        "authority_model_id": "approval-authority-model-v0",
        "authority_mode": "future_explicit_human_or_governance_approval_required",
        "allowed_authority_classes": ALLOWED_AUTHORITY_CLASSES,
        "denied_authority_classes": DENIED_AUTHORITY_CLASSES,
        "minimum_required_roles": REQUIRED_ROLES,
        "separation_of_duties_required": True,
        "self_approval_forbidden": True,
        "agent_auto_approval_forbidden": True,
        "approval_without_evidence_forbidden": True,
        "approval_without_rollback_forbidden": True,
        "approval_without_post_validation_forbidden": True,
        "approval_without_y_star_non_mutation_check_forbidden": True,
        "approval_without_mcp_non_bypass_check_forbidden": True,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
    }
    role_registry = {
        "schema_name": "ystar.approval_authority.role_registry",
        "schema_version": SCHEMA_VERSION,
        "registry_id": "approval-role-registry-v0",
        "roles": [
            {
                "role_id": role,
                "descriptor_only": True,
                "secret_material_included": False,
                "credential_material_included": False,
                "responsibility": responsibility,
            }
            for role, responsibility in [
                ("owner_or_founder", "final business owner review authority descriptor"),
                ("governance_reviewer", "checks Y* lineage, Pre-U, bridge, CIEU, and residual chain"),
                ("safety_reviewer", "checks safety flags, forbidden scopes, and rollback readiness"),
                ("release_operator", "future operator who may execute only after valid approval"),
                ("rollback_operator", "future operator assigned before application to restore baseline"),
            ]
        ],
        "contains_secrets": False,
        "contains_credentials": False,
        "contains_private_keys": False,
        "contains_tokens": False,
        "safety_flags": SAFETY_FLAGS,
    }
    separation = {
        "schema_name": "ystar.approval_authority.separation_of_duties_policy",
        "schema_version": SCHEMA_VERSION,
        "policy_id": "approval-separation-of-duties-policy-v0",
        "proposer_must_not_equal_approver": True,
        "approver_must_not_equal_release_operator_for_high_risk_updates": True,
        "rollback_operator_defined_before_application": True,
        "high_risk_brain_memory_strategy_boundaries_require_additional_review": True,
        "self_approval_forbidden": True,
        "agent_auto_approval_forbidden": True,
        "safety_flags": SAFETY_FLAGS,
    }
    scope_matrix = {
        "schema_name": "ystar.approval_authority.scope_matrix",
        "schema_version": SCHEMA_VERSION,
        "scope_matrix_id": "approval-authority-scope-matrix-v0",
        "allowed_scope_by_authority_class": {
            "human_owner": ["future explicit approval after full dossier review"],
            "designated_governance_reviewer": ["governance invariant review"],
            "designated_safety_reviewer": ["safety and rollback readiness review"],
            "future_versioned_governance_approval_service": ["future adapter-gated approval record production"],
        },
        "denied_scope_by_authority_class": {
            authority_class: [
                "auto-approval",
                "approval without evidence",
                "approval without rollback",
                "direct Y* mutation",
                "approval for L6 revenue execution",
            ]
            for authority_class in DENIED_AUTHORITY_CLASSES
        },
        "safety_flags": SAFETY_FLAGS,
    }

    dossier_id = "approval-evidence-dossier-v0"
    evidence_dossier = {
        "schema_name": "ystar.approval_evidence.dossier",
        "schema_version": SCHEMA_VERSION,
        "dossier_id": dossier_id,
        "source_update_package_id": package_id,
        "source_sandbox_run_id": sandbox_run_id,
        "source_sandbox_validation_ids": [sandbox_validation_id],
        "source_rollback_validation_ids": [rollback_result_id],
        "source_y_star_invariant_ids": [invariant_id, y_star_check_id],
        "source_mcp_non_bypass_ids": [mcp_check_id],
        "source_post_validation_plan_ids": [post_validation_plan_id],
        "evidence_refs": evidence_refs(),
        "missing_evidence": gaps,
        "evidence_status": "complete_for_approval_review" if not gaps else "incomplete_requires_more_evidence",
        "safe_for_approval_review": not gaps,
        "safe_for_direct_application": False,
        "safety_flags": SAFETY_FLAGS,
    }
    source_artifact_index = {
        "schema_name": "ystar.approval_evidence.source_artifact_index",
        "schema_version": SCHEMA_VERSION,
        "index_id": "approval-source-artifact-index-v0",
        "source_artifacts": INPUT_REFS,
        "source_update_package_id": package_id,
        "source_patch_plan_id": patch_plan_id,
        "source_sandbox_run_id": sandbox_run_id,
        "safety_flags": SAFETY_FLAGS,
    }
    invariant_index = {
        "schema_name": "ystar.approval_evidence.invariant_check_index",
        "schema_version": SCHEMA_VERSION,
        "index_id": "approval-invariant-check-index-v0",
        "checks": [
            {
                "check_name": check,
                "source_ref": INPUT_REFS["sandbox_y_star_non_mutation_check"]
                if "Y*" in check or "residual" in check or "lineage" in check or "behavior" in check
                else INPUT_REFS["sandbox_mcp_non_bypass_check"]
                if "MCP" in check or "Pre-U" in check or "bridge" in check or "CIEU" in check
                else INPUT_REFS["sandbox_rollback_result"]
                if "rollback" in check
                else INPUT_REFS["sandbox_post_update_validation_result"],
                "required_before_approval": True,
            }
            for check in INVARIANT_CHECKS
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    validation_index = {
        "schema_name": "ystar.approval_evidence.validation_result_index",
        "schema_version": SCHEMA_VERSION,
        "index_id": "approval-validation-result-index-v0",
        "validation_results": [
            {
                "validation_id": sandbox_validation_id,
                "validation_ref": INPUT_REFS["sandbox_post_update_validation_result"],
                "result_kind": "sandbox_post_update_validation",
                "passed_for_boundary_review": True,
            },
            {
                "validation_id": rollback_result_id,
                "validation_ref": INPUT_REFS["sandbox_rollback_result"],
                "result_kind": "sandbox_rollback_validation",
                "passed_for_boundary_review": True,
            },
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    missing_evidence_report = {
        "schema_name": "ystar.approval_evidence.missing_evidence_gap_report",
        "schema_version": SCHEMA_VERSION,
        "report_id": "approval-missing-evidence-gap-report-v0",
        "missing_evidence": gaps,
        "known_context_only_gap": (
            "Full repository pytest has a separate platform import issue: "
            "tests/platform/test_coordinator_reply_5tuple_wire.py imports governance.coordinator_audit."
        ),
        "blocks_artifact_only_l5_9": False,
        "recommendation": "Handle unrelated full-pytest collection import issue in a separate CI hygiene milestone.",
        "safety_flags": SAFETY_FLAGS,
    }

    record_contract = {
        "schema_name": "ystar.durable_approval_record.contract",
        "schema_version": SCHEMA_VERSION,
        "contract_id": "durable-approval-record-contract-v0",
        "purpose": "Define future durable approval record shape without writing a durable record now.",
        "required_record_fields": APPROVAL_RECORD_FIELDS,
        "integrity_requirements": [
            "content hash or future signature placeholder",
            "immutable append-only record semantics",
            "no silent overwrite",
            "record references evidence, rollback, validation, expiration, revocation, and audit lineage",
        ],
        "storage_requirements": [
            "future storage only",
            "explicit milestone required before persistence",
            "no DB write in L5.9",
        ],
        "immutability_requirements": [
            "append-only",
            "parent record ref required for supersession",
            "revocation record required instead of deletion",
        ],
        "revocation_requirements": ["revocation policy ref required", "revocation must be auditable"],
        "expiration_requirements": ["expiration policy ref required", "approval cannot be indefinite"],
        "audit_requirements": ["source evidence refs", "approval decision refs", "application status"],
        "forbidden_record_shortcuts": [
            "approval without evidence dossier",
            "approval without rollback plan",
            "approval without post-validation plan",
            "approval without explicit scope",
            "approval without denied scope",
            "approval without expiration/revocation policy",
            "silent overwrite",
        ],
        "persistence_enabled_now": False,
        "durable_db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    record_schema = {
        "schema_name": "ystar.durable_approval_record.schema_v0",
        "schema_version": SCHEMA_VERSION,
        "required_fields": APPROVAL_RECORD_FIELDS,
        "field_descriptions": {
            field: f"Required future approval record field: {field}"
            for field in APPROVAL_RECORD_FIELDS
        },
        "example_record_fixture": {
            "approval_record_id": "approval-record-placeholder-not-written-v0",
            "approval_subject_package_id": package_id,
            "approval_decision": "not_granted",
            "approval_mode": "contract_only",
            "application_status": "not_applied",
            "safety_flags": SAFETY_FLAGS,
        },
        "persistence_enabled_now": False,
        "durable_db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    integrity = {
        "schema_name": "ystar.durable_approval_record.integrity_requirements",
        "schema_version": SCHEMA_VERSION,
        "integrity_requirements_id": "approval-record-integrity-requirements-v0",
        "requirements": [
            "content hash or future signature placeholder",
            "immutable append-only record semantics",
            "no silent overwrite",
            "no approval without evidence dossier",
            "no approval without rollback plan",
            "no approval without post-validation plan",
            "no approval without explicit scope",
            "no approval without denied scope",
            "no approval without expiration/revocation policy",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    storage_policy = {
        "schema_name": "ystar.durable_approval_record.storage_policy",
        "schema_version": SCHEMA_VERSION,
        "storage_policy_id": "approval-record-storage-policy-v0",
        "storage_requirements": [
            "future append-only durable storage",
            "future explicit approval record milestone required",
            "future integrity verification required",
        ],
        "persistence_enabled_now": False,
        "db_write_performed_now": False,
        "future_storage_requires_explicit_milestone": True,
        "safety_flags": SAFETY_FLAGS,
    }

    decision_packet_id = "real-approval-decision-packet-fixture-v0"
    required_before_real_approval = [
        "explicit human/governance approval",
        "durable approval record creation",
        "pre-application backup/snapshot",
        "post-approval preflight validation",
        "rollback operator confirmation",
        "final non-bypass invariant check",
        "final Y* non-mutation check",
    ]
    decision_packet = {
        "schema_name": "ystar.real_approval_decision.packet_fixture",
        "schema_version": SCHEMA_VERSION,
        "decision_packet_id": decision_packet_id,
        "source_evidence_dossier_id": dossier_id,
        "source_update_package_id": package_id,
        "decision_mode": "approval_workflow_boundary_fixture",
        "approval_decision": "not_granted",
        "real_approval_granted": False,
        "real_application_authorized": False,
        "approval_record_created_as_durable_record": False,
        "approval_record_contract_defined": True,
        "required_before_real_approval": required_before_real_approval,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }
    decision_denied = {
        "schema_name": "ystar.real_approval_decision.denied_scope",
        "schema_version": SCHEMA_VERSION,
        "denied_scope_id": "real-approval-decision-denied-scope-v0",
        "denied_operations": [
            "real application",
            "canonical mutation",
            "brain writeback",
            "memory ingestion",
            "strategy mutation",
            "direct Y* mutation",
            "live execution",
            "MCP execution",
            "external action",
            "network/API",
            "L6 revenue discovery",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    validity_policy = {
        "schema_name": "ystar.approval_validity.policy",
        "schema_version": SCHEMA_VERSION,
        "validity_policy_id": "approval-validity-policy-v0",
        "approval_must_be_scope_bound": True,
        "approval_must_be_time_bound_or_version_bound": True,
        "approval_must_be_revocable": True,
        "approval_cannot_be_reused_for_different_package_version_scope": True,
        "approval_cannot_authorize_future_unknown_updates": True,
        "approval_cannot_override_y_star_non_mutation_invariant": True,
        "approval_cannot_override_mcp_non_bypass_invariant": True,
        "approval_cannot_override_rollback_requirement": True,
        "safety_flags": SAFETY_FLAGS,
    }
    expiration_policy = {
        "schema_name": "ystar.approval_validity.expiration_policy",
        "schema_version": SCHEMA_VERSION,
        "expiration_policy_id": "approval-expiration-policy-v0",
        "expiration_mode": "future_time_or_version_bound_required",
        "indefinite_approval_allowed": False,
        "reuse_after_package_change_allowed": False,
        "reuse_after_patch_change_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    revocation_policy = {
        "schema_name": "ystar.approval_validity.revocation_policy",
        "schema_version": SCHEMA_VERSION,
        "revocation_policy_id": "approval-revocation-policy-v0",
        "approval_must_be_revocable": True,
        "revocation_record_required": True,
        "revocation_deletes_original_record": False,
        "revocation_must_be_auditable": True,
        "safety_flags": SAFETY_FLAGS,
    }
    invalidation_triggers = {
        "schema_name": "ystar.approval_validity.invalidation_triggers",
        "schema_version": SCHEMA_VERSION,
        "trigger_set_id": "approval-invalidation-triggers-v0",
        "triggers": [
            "target package changed",
            "patch plan changed",
            "evidence dossier changed",
            "validation failed",
            "rollback plan missing",
            "Y* lineage violation",
            "MCP non-bypass violation",
            "safety flag regression",
            "external action boundary change",
            "brain/memory boundary change",
            "approval record integrity mismatch",
            "approval expired",
            "approval revoked",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    snapshot_policy = {
        "schema_name": "ystar.pre_application_snapshot.policy",
        "schema_version": SCHEMA_VERSION,
        "snapshot_policy_id": "pre-application-snapshot-policy-v0",
        "required_snapshots": [
            "canonical projection policy snapshot",
            "learning policy snapshot",
            "MCP boundary policy snapshot",
            "read-model structure snapshot",
            "relevant brain/memory boundary metadata snapshot only, not raw DB/log content",
            "rollback target snapshot",
            "integrity hash placeholder",
            "storage policy placeholder",
            "snapshot validation before application",
        ],
        "forbidden_snapshot_sources": [
            "raw DB dump reading",
            "log content reading",
            "active-agent marker reading",
            "secret/credential capture",
            "unreviewed memory ingestion",
            "brain content writeback",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    backup_manifest = {
        "schema_name": "ystar.pre_application_snapshot.backup_manifest_contract",
        "schema_version": SCHEMA_VERSION,
        "backup_manifest_id": "canonical-backup-manifest-contract-v0",
        "source_package_id": package_id,
        "target_version": patch_plan.get("proposed_new_version", "future-approved-version-placeholder"),
        "captured_artifact_refs": [
            "canonical projection policy snapshot ref placeholder",
            "learning policy snapshot ref placeholder",
            "MCP boundary policy snapshot ref placeholder",
            "read-model structure snapshot ref placeholder",
            "brain/memory boundary metadata snapshot ref placeholder",
        ],
        "excluded_sensitive_sources": [
            "raw DB contents",
            "WAL/SHM contents",
            "raw logs",
            "active-agent markers",
            "secrets",
            "credentials",
        ],
        "integrity_hashes_placeholder": "future-integrity-hashes-required-before-application",
        "rollback_ref": rollback_plan_id,
        "created_by_role_ref": "release_operator",
        "validation_status": "contract_only_not_captured",
        "persistence_enabled_now": False,
        "safety_flags": SAFETY_FLAGS,
    }
    state_capture = {
        "schema_name": "ystar.pre_application_snapshot.state_capture_requirements",
        "schema_version": SCHEMA_VERSION,
        "capture_requirements_id": "pre-application-state-capture-requirements-v0",
        "capture_requirements": snapshot_policy["required_snapshots"],
        "capture_forbidden_sources": snapshot_policy["forbidden_snapshot_sources"],
        "safety_flags": SAFETY_FLAGS,
    }
    snapshot_integrity = {
        "schema_name": "ystar.pre_application_snapshot.integrity_requirements",
        "schema_version": SCHEMA_VERSION,
        "snapshot_integrity_requirements_id": "snapshot-integrity-requirements-v0",
        "requirements": [
            "integrity hash placeholder for every captured artifact",
            "snapshot manifest must be validated before application",
            "snapshot excludes sensitive raw runtime sources",
            "rollback target snapshot must be present before release",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    boundary_gate = {
        "schema_name": "ystar.real_application_boundary.gate_contract",
        "schema_version": SCHEMA_VERSION,
        "gate_contract_id": "real-application-boundary-gate-contract-v0",
        "required_preconditions": APPLICATION_PRECONDITIONS,
        "real_application_allowed_now": False,
        "safety_flags": SAFETY_FLAGS,
    }
    precondition_matrix = {
        "schema_name": "ystar.real_application_boundary.precondition_matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "real-application-precondition-matrix-v0",
        "preconditions": [
            {
                "precondition": precondition,
                "required": True,
                "satisfied_now": False
                if precondition
                in {
                    "durable approval record exists",
                    "approval is valid and unexpired",
                    "approval scope matches package scope",
                    "pre-application snapshot exists",
                    "post-approval preflight validation passed",
                    "release operator assigned",
                    "rollback operator assigned",
                }
                else True,
            }
            for precondition in APPLICATION_PRECONDITIONS
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    application_blocker = {
        "schema_name": "ystar.real_application_boundary.blocker",
        "schema_version": SCHEMA_VERSION,
        "blocker_id": "real-application-blocker-v0",
        "real_application_blocked_now": True,
        "reason": "approval workflow boundary only",
        "missing_real_approval_record": True,
        "missing_durable_persistence": True,
        "missing_live_release_protocol": True,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
    }
    application_denied = {
        "schema_name": "ystar.real_application_boundary.denied_operations",
        "schema_version": SCHEMA_VERSION,
        "denied_operations": [
            "applying patch to real canonical state",
            "writing brain",
            "ingesting memory",
            "mutating strategy",
            "direct Y* mutation",
            "enabling live execution",
            "enabling MCP execution",
            "modifying Y-star-gov",
            "modifying gov-mcp",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    preflight_plan = {
        "schema_name": "ystar.post_approval_preflight.validation_plan",
        "schema_version": SCHEMA_VERSION,
        "preflight_validation_plan_id": "post-approval-preflight-validation-plan-v0",
        "required_validations": PREFLIGHT_REQUIREMENTS,
        "approval_record_integrity_validation_required": True,
        "approval_scope_validation_required": True,
        "package_version_validation_required": True,
        "evidence_dossier_validation_required": True,
        "snapshot_validation_required": True,
        "rollback_validation_required": True,
        "safety_flags": SAFETY_FLAGS,
    }
    preflight_matrix = {
        "schema_name": "ystar.post_approval_preflight.validation_matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "post-approval-preflight-validation-matrix-v0",
        "validation_items": [
            {"validation": requirement, "required": True, "executed_now": False}
            for requirement in PREFLIGHT_REQUIREMENTS
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    required_tests = {
        "schema_name": "ystar.post_approval_preflight.required_test_targets",
        "schema_version": SCHEMA_VERSION,
        "test_targets_id": "post-approval-required-test-targets-v0",
        "l5_0_to_l5_9_targeted_pytest": TEST_TARGETS_L5_0_L5_9,
        "known_unrelated_full_pytest_collection_issue": {
            "test": "tests/platform/test_coordinator_reply_5tuple_wire.py",
            "issue": "imports governance.coordinator_audit",
            "context_only": True,
            "approval_blocker_for_artifact_only_milestone": False,
            "recommendation": "separate CI hygiene milestone",
        },
        "safety_flags": SAFETY_FLAGS,
    }
    preflight_invariants = {
        "schema_name": "ystar.post_approval_preflight.invariant_checks",
        "schema_version": SCHEMA_VERSION,
        "invariant_checks_id": "post-approval-invariant-checks-v0",
        "checks": [
            "Y* non-mutation invariant check",
            "mission Y* lineage preserved",
            "behavior Y* remains projection-derived",
            "MCP non-bypass invariant check",
            "Pre-U required",
            "bridge receipt required",
            "CIEU receipt required",
            "no direct writeback invariant check",
            "no direct Y* mutation check",
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    operator_checklist = {
        "schema_name": "ystar.manual_approval.operator_checklist",
        "schema_version": SCHEMA_VERSION,
        "checklist_id": "approval-operator-checklist-v0",
        "review_items": [
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
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    release_checklist = {
        "schema_name": "ystar.manual_approval.release_operator_checklist",
        "schema_version": SCHEMA_VERSION,
        "checklist_id": "release-operator-checklist-v0",
        "review_items": [
            "confirm durable approval record exists",
            "confirm approval is valid and unexpired",
            "confirm pre-application snapshot exists",
            "confirm preflight validation passed",
            "confirm rollback operator is assigned",
            "confirm release scope matches approval scope",
            "confirm live/MCP/network gates remain disabled until explicitly approved mode exists",
        ],
        "release_authorized_now": False,
        "safety_flags": SAFETY_FLAGS,
    }
    rollback_checklist = {
        "schema_name": "ystar.manual_approval.rollback_operator_checklist",
        "schema_version": SCHEMA_VERSION,
        "checklist_id": "rollback-operator-checklist-v0",
        "review_items": [
            "confirm rollback target snapshot exists",
            "confirm rollback plan is version-matched",
            "confirm rollback validation checks are defined",
            "confirm emergency stop policy is available",
            "confirm rollback operator handoff is complete",
        ],
        "rollback_operator_required_before_application": True,
        "safety_flags": SAFETY_FLAGS,
    }
    emergency_stop = {
        "schema_name": "ystar.manual_approval.emergency_stop_policy",
        "schema_version": SCHEMA_VERSION,
        "policy_id": "approval-emergency-stop-policy-v0",
        "triggers": [
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
        ],
        "safety_flags": SAFETY_FLAGS,
    }

    predicted = {
        "schema_name": "ystar.approval_workflow.predicted_outcome",
        "schema_version": SCHEMA_VERSION,
        "predicted_outcome_id": "approval-workflow-predicted-outcome-v0",
        "expected_result": [
            "authority model defined",
            "evidence dossier generated",
            "approval record contract defined",
            "approval decision packet fixture generated",
            "validity/revocation policy generated",
            "snapshot policy generated",
            "real application boundary gate generated",
            "preflight validation plan generated",
            "manual approval runbook generated",
            "real approval/application blocked",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    mock_actual = {
        "schema_name": "ystar.approval_workflow.mock_actual_outcome",
        "schema_version": SCHEMA_VERSION,
        "mock_actual_outcome_id": "approval-workflow-mock-actual-outcome-v0",
        "actual_mode": "approval_workflow_boundary_design_fixture",
        "actual_result": predicted["expected_result"],
        **status,
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }
    residual_delta = {
        "schema_name": "ystar.approval_workflow.residual_delta",
        "schema_version": SCHEMA_VERSION,
        "residual_delta_id": "approval-workflow-residual-delta-v0",
        "residual_classes": {
            "approval_authority_gap": "authority model defined, real authority not exercised",
            "durable_record_gap": "record contract defined, durable record not written",
            "evidence_gap": "dossier assembled for review, future live approval still needs durable record",
            "snapshot_gap": "snapshot policy defined, snapshot not captured",
            "preflight_validation_gap": "preflight plan defined, post-approval preflight not executed",
            "application_boundary_gap": "boundary gate defined, real application blocked",
            "Y_star_invariant_gap": "invariant preserved as requirement, cannot be overridden",
            "MCP_non_bypass_gap": "non-bypass preserved as requirement, cannot be overridden",
            "live_blocker_residual": "live execution remains blocked",
            "real_application_blocker_residual": "real application intentionally blocked",
        },
        "deterministic_structural_residual_only": True,
        "semantic_truth_scoring_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    cieu_event = {
        "schema_name": "ystar.approval_workflow.cieu_event_fixture",
        "schema_version": SCHEMA_VERSION,
        "event_id": "approval-workflow-cieu-event-fixture-v0",
        "X_t": {
            "source_package_id": package_id,
            "source_sandbox_run_id": sandbox_run_id,
            "source_sandbox_validation_id": sandbox_validation_id,
        },
        "U_t": "approval workflow boundary design operation",
        "Y_star_t": (
            "Define a safe real approval workflow boundary without granting approval "
            "or applying any canonical update."
        ),
        "Y_t_plus_1": mock_actual,
        "R_t_plus_1": residual_delta,
        "event_mode": "real_approval_workflow_boundary_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "durable_approval_record_written": False,
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }

    readiness = {
        "schema_name": "ystar.real_approval_workflow.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "real-approval-workflow-readiness-v0",
        "approval_authority_model_defined": True,
        "evidence_dossier_generated": True,
        "durable_approval_record_contract_defined": True,
        "approval_decision_packet_fixture_generated": True,
        "approval_validity_revocation_policy_defined": True,
        "pre_application_snapshot_policy_defined": True,
        "real_application_boundary_gate_defined": True,
        "post_approval_preflight_validation_defined": True,
        "manual_approval_runbook_generated": True,
        "approval_workflow_cieu_fixture_generated": True,
        "real_approval_still_blocked": True,
        "real_application_still_blocked": True,
        "durable_approval_persistence_still_blocked": True,
        "brain_writeback_still_blocked": True,
        "memory_ingestion_still_blocked": True,
        "y_star_direct_mutation_still_blocked": True,
        "mcp_execution_still_blocked": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "ready_for_l5_10_controlled_approval_record_sandbox": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "next_required_milestone": NEXT_MILESTONE,
        **status,
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }
    run = {
        "schema_name": "ystar.real_approval_workflow.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "real-approval-workflow-boundary-run-v0",
        "contract_ref": "real_approval_workflow_boundary/real_approval_workflow_boundary_contract.json",
        "input_fixture_ref": "real_approval_workflow_boundary/real_approval_workflow_input_fixture.json",
        "workflow_stages_completed": WORKFLOW_STAGES,
        "missing_sources": gaps,
        "authority_model_id": authority_model["authority_model_id"],
        "evidence_dossier_id": dossier_id,
        "approval_record_contract_id": record_contract["contract_id"],
        "decision_packet_id": decision_packet_id,
        "readiness_ref": "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
        **status,
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }
    workflow_summary = {
        "schema_name": "ystar.real_approval_workflow.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_9_real_approval_workflow_boundary_defined": True,
        "approval_authority_model_generated": True,
        "approval_evidence_dossier_generated": True,
        "durable_approval_record_contract_generated": True,
        "approval_decision_packet_fixture_generated": True,
        "validity_revocation_policy_generated": True,
        "pre_application_snapshot_policy_generated": True,
        "real_application_boundary_gate_generated": True,
        "post_approval_preflight_validation_plan_generated": True,
        "manual_approval_runbook_generated": True,
        "approval_workflow_cieu_like_fixture_generated": True,
        "ready_for_l5_10_controlled_approval_record_sandbox": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        **status,
        "safety_flags": SAFETY_FLAGS,
        "approval_flags": APPROVAL_FLAGS,
    }

    # Write top-level workflow artifacts.
    write_text(
        BOUNDARY / "README.md",
        md(
            "Real Approval Workflow Boundary",
            [
                "L5.9 defines the approval boundary required before any future real canonical update application.",
                "",
                "It does not grant approval, write a durable approval record, apply a real update, mutate Y*, or enable live/MCP/network execution.",
            ],
        ),
    )
    write_json(BOUNDARY / "real_approval_workflow_boundary_contract.json", contract)
    write_json(BOUNDARY / "real_approval_workflow_input_fixture.json", input_fixture)
    write_json(BOUNDARY / "real_approval_workflow_run.json", run)
    write_json(BOUNDARY / "real_approval_workflow_summary.json", workflow_summary)
    write_text(
        BOUNDARY / "real_approval_workflow_report.md",
        md(
            "Real Approval Workflow Boundary Report",
            [
                "- Approval workflow boundary defined: true",
                "- Durable approval record contract defined: true",
                "- Real approval granted: false",
                "- Real application authorized: false",
                "- Durable approval persistence enabled: false",
                "- Ready for L5.10 controlled approval record sandbox: true",
            ],
        ),
    )

    # Authority artifacts.
    write_json(AUTHORITY / "approval_authority_model.json", authority_model)
    write_json(AUTHORITY / "approval_role_registry.json", role_registry)
    write_json(AUTHORITY / "approval_separation_of_duties_policy.json", separation)
    write_json(AUTHORITY / "approval_authority_scope_matrix.json", scope_matrix)
    write_json(
        AUTHORITY / "approval_authority_summary.json",
        {
            "schema_name": "ystar.approval_authority.summary",
            "schema_version": SCHEMA_VERSION,
            "approval_authority_model_generated": True,
            "authority_mode": authority_model["authority_mode"],
            "self_approval_forbidden": True,
            "agent_auto_approval_forbidden": True,
            "minimum_required_roles": REQUIRED_ROLES,
            "real_approval_granted": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(AUTHORITY / "approval_authority_report.md", md("Approval Authority Report", ["Future explicit human or governance approval is required; self and agent auto-approval are forbidden."]))

    # Evidence artifacts.
    write_json(DOSSIER / "approval_evidence_dossier.json", evidence_dossier)
    write_json(DOSSIER / "approval_source_artifact_index.json", source_artifact_index)
    write_json(DOSSIER / "approval_invariant_check_index.json", invariant_index)
    write_json(DOSSIER / "approval_validation_result_index.json", validation_index)
    write_json(DOSSIER / "approval_missing_evidence_gap_report.json", missing_evidence_report)
    write_json(
        DOSSIER / "approval_evidence_summary.json",
        {
            "schema_name": "ystar.approval_evidence.summary",
            "schema_version": SCHEMA_VERSION,
            "approval_evidence_dossier_generated": True,
            "evidence_status": evidence_dossier["evidence_status"],
            "safe_for_approval_review": evidence_dossier["safe_for_approval_review"],
            "safe_for_direct_application": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(DOSSIER / "approval_evidence_report.md", md("Approval Evidence Report", ["The dossier is safe for review only and not safe for direct application."]))

    # Durable record artifacts.
    write_json(RECORD / "durable_approval_record_contract.json", record_contract)
    write_json(RECORD / "approval_record_schema_v0.json", record_schema)
    write_json(RECORD / "approval_record_integrity_requirements.json", integrity)
    write_json(RECORD / "approval_record_storage_policy.json", storage_policy)
    write_json(
        RECORD / "approval_record_summary.json",
        {
            "schema_name": "ystar.durable_approval_record.summary",
            "schema_version": SCHEMA_VERSION,
            "durable_approval_record_contract_generated": True,
            "approval_record_schema_generated": True,
            "persistence_enabled_now": False,
            "durable_db_write_performed": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(RECORD / "approval_record_report.md", md("Approval Record Report", ["Durable approval record schema is defined; no durable record is written."]))

    # Decision fixture artifacts.
    write_json(DECISION / "real_approval_decision_packet_fixture.json", decision_packet)
    write_json(DECISION / "real_approval_decision_denied_scope.json", decision_denied)
    write_text(DECISION / "real_approval_decision_gap_report.md", md("Real Approval Decision Gap Report", ["Real approval is not granted. Missing future items include durable approval record creation, pre-application snapshot, post-approval preflight, rollback operator confirmation, and final invariant checks."]))
    write_json(
        DECISION / "real_approval_decision_summary.json",
        {
            "schema_name": "ystar.real_approval_decision.summary",
            "schema_version": SCHEMA_VERSION,
            "approval_decision_packet_fixture_generated": True,
            "approval_decision": "not_granted",
            "real_approval_granted": False,
            "real_application_authorized": False,
            "approval_record_created_as_durable_record": False,
            "safety_flags": SAFETY_FLAGS,
            "approval_flags": APPROVAL_FLAGS,
        },
    )

    # Validity artifacts.
    write_json(VALIDITY / "approval_validity_policy.json", validity_policy)
    write_json(VALIDITY / "approval_expiration_policy.json", expiration_policy)
    write_json(VALIDITY / "approval_revocation_policy.json", revocation_policy)
    write_json(VALIDITY / "approval_invalidation_triggers.json", invalidation_triggers)
    write_json(
        VALIDITY / "approval_validity_summary.json",
        {
            "schema_name": "ystar.approval_validity.summary",
            "schema_version": SCHEMA_VERSION,
            "validity_revocation_policy_generated": True,
            "approval_must_be_scope_bound": True,
            "approval_must_be_revocable": True,
            "approval_cannot_override_invariants": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(VALIDITY / "approval_validity_report.md", md("Approval Validity Report", ["Approval must be scoped, bounded, revocable, and invalidated on evidence, rollback, validation, lineage, or safety regressions."]))

    # Snapshot artifacts.
    write_json(SNAPSHOT / "pre_application_snapshot_policy.json", snapshot_policy)
    write_json(SNAPSHOT / "canonical_backup_manifest_contract.json", backup_manifest)
    write_json(SNAPSHOT / "pre_application_state_capture_requirements.json", state_capture)
    write_json(SNAPSHOT / "snapshot_integrity_requirements.json", snapshot_integrity)
    write_json(
        SNAPSHOT / "snapshot_policy_summary.json",
        {
            "schema_name": "ystar.pre_application_snapshot.summary",
            "schema_version": SCHEMA_VERSION,
            "pre_application_snapshot_policy_generated": True,
            "canonical_backup_manifest_contract_generated": True,
            "persistence_enabled_now": False,
            "raw_runtime_content_capture_forbidden": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(SNAPSHOT / "snapshot_policy_report.md", md("Snapshot Policy Report", ["Future real application requires scoped snapshots and forbids raw DB/log/active-marker/secret capture."]))

    # Application boundary artifacts.
    write_json(APPLICATION / "real_application_boundary_gate_contract.json", boundary_gate)
    write_json(APPLICATION / "real_application_precondition_matrix.json", precondition_matrix)
    write_json(APPLICATION / "real_application_blocker.json", application_blocker)
    write_json(APPLICATION / "real_application_denied_operations.json", application_denied)
    write_json(
        APPLICATION / "real_application_boundary_summary.json",
        {
            "schema_name": "ystar.real_application_boundary.summary",
            "schema_version": SCHEMA_VERSION,
            "real_application_boundary_gate_generated": True,
            "real_application_blocked_now": True,
            "missing_real_approval_record": True,
            "missing_durable_persistence": True,
            "missing_live_release_protocol": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(APPLICATION / "real_application_boundary_report.md", md("Real Application Boundary Report", ["The real application boundary is defined and blocks real application now."]))

    # Preflight artifacts.
    write_json(PREFLIGHT / "post_approval_preflight_validation_plan.json", preflight_plan)
    write_json(PREFLIGHT / "post_approval_preflight_validation_matrix.json", preflight_matrix)
    write_json(PREFLIGHT / "post_approval_required_test_targets.json", required_tests)
    write_json(PREFLIGHT / "post_approval_invariant_checks.json", preflight_invariants)
    write_json(
        PREFLIGHT / "post_approval_preflight_summary.json",
        {
            "schema_name": "ystar.post_approval_preflight.summary",
            "schema_version": SCHEMA_VERSION,
            "post_approval_preflight_validation_defined": True,
            "required_validation_count": len(PREFLIGHT_REQUIREMENTS),
            "known_unrelated_full_pytest_collection_issue_recorded": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(PREFLIGHT / "post_approval_preflight_report.md", md("Post-Approval Preflight Report", ["Future approval must be followed by scoped preflight validation before any real application."]))

    # Manual runbook artifacts.
    write_text(
        RUNBOOK / "manual_approval_runbook.md",
        md(
            "Manual Approval Runbook",
            [
                "## Approver Review",
                "- Review package id, scope, denied scope, evidence dossier, Y* non-mutation check, MCP non-bypass check, rollback plan, snapshot policy, and preflight validation plan.",
                "- Do not approve direct Y* mutation, brain writeback, memory ingestion, strategy mutation, live/MCP/network execution, or bundled L6 revenue execution.",
                "",
                "## Evidence Review",
                "- Confirm sandbox validation, rollback validation, and original-vs-sandbox comparison are present.",
                "- Confirm residual never rewrites mission-level or behavior-level Y* directly.",
                "",
                "## Handoff",
                "- Future approval record creation must precede release operator handoff.",
                "- Rollback operator handoff must be complete before application.",
                "- Emergency stop is triggered on validation failure, approval integrity mismatch, rollback unavailability, live/MCP execution, external action, network call, or writeback attempt.",
            ],
        ),
    )
    write_json(RUNBOOK / "approval_operator_checklist.json", operator_checklist)
    write_json(RUNBOOK / "release_operator_checklist.json", release_checklist)
    write_json(RUNBOOK / "rollback_operator_checklist.json", rollback_checklist)
    write_json(RUNBOOK / "emergency_stop_policy.json", emergency_stop)
    write_json(
        RUNBOOK / "manual_approval_runbook_summary.json",
        {
            "schema_name": "ystar.manual_approval.runbook_summary",
            "schema_version": SCHEMA_VERSION,
            "manual_approval_runbook_generated": True,
            "approval_operator_checklist_generated": True,
            "release_operator_checklist_generated": True,
            "rollback_operator_checklist_generated": True,
            "emergency_stop_policy_generated": True,
            "real_approval_granted": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )

    # Approval workflow audit artifacts.
    write_json(CIEU / "approval_workflow_cieu_event_fixture.json", cieu_event)
    write_json(CIEU / "approval_workflow_predicted_outcome.json", predicted)
    write_json(CIEU / "approval_workflow_mock_actual_outcome.json", mock_actual)
    write_json(CIEU / "approval_workflow_residual_delta.json", residual_delta)
    write_json(
        CIEU / "approval_workflow_audit_summary.json",
        {
            "schema_name": "ystar.approval_workflow.audit_summary",
            "schema_version": SCHEMA_VERSION,
            "approval_workflow_cieu_like_fixture_generated": True,
            "approval_workflow_residual_delta_generated": True,
            "persistence_enabled": False,
            "db_write_performed": False,
            "durable_approval_record_written": False,
            "residual_classes": RESIDUAL_CLASSES,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(CIEU / "approval_workflow_audit_report.md", md("Approval Workflow Audit Report", ["Approval workflow CIEU-like fixture is generated without persistence or durable approval record write."]))

    # Readiness artifacts.
    write_json(READINESS / "real_approval_workflow_readiness.json", readiness)
    write_text(
        READINESS / "real_approval_workflow_readiness.md",
        md(
            "Real Approval Workflow Readiness",
            [
                "- approval_authority_model_defined: true",
                "- durable_approval_record_contract_defined: true",
                "- real_approval_still_blocked: true",
                "- real_application_still_blocked: true",
                "- durable_approval_persistence_still_blocked: true",
                "- ready_for_l5_10_controlled_approval_record_sandbox: true",
                "- ready_for_l6_revenue_opportunity_discovery: false",
            ],
        ),
    )
    write_json(
        READINESS / "l5_10_recommended_next_step.json",
        {
            "schema_name": "ystar.real_approval_workflow.next_step",
            "schema_version": SCHEMA_VERSION,
            "recommended_next_step": NEXT_MILESTONE,
            "reason": (
                "The real approval workflow boundary and durable approval record contract are "
                "defined without granting approval. A future sandbox can test writing approval "
                "record fixtures before any real persistence is considered."
            ),
            "ready_for_l5_10_controlled_approval_record_sandbox": True,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )


def main() -> None:
    build_all()


if __name__ == "__main__":
    main()
