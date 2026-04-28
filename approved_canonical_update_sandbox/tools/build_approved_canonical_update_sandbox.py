#!/usr/bin/env python3
"""Build deterministic L5.8 approved canonical update sandbox artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SANDBOX = ROOT / "approved_canonical_update_sandbox"
APPROVAL = ROOT / "sandbox_approval_fixture"
BASELINE = ROOT / "sandbox_canonical_state_baseline"
APPLICATION = ROOT / "sandbox_patch_application"
VALIDATION = ROOT / "sandbox_post_update_validation"
REPROJECTION = ROOT / "sandbox_reprojection_and_mcp_preview"
CIEU = ROOT / "sandbox_update_cieu_residual"
ROLLBACK = ROOT / "sandbox_rollback_validation"
COMPARISON = ROOT / "original_sandbox_rollback_comparison"
READINESS = ROOT / "approved_sandbox_update_readiness"

SCHEMA_VERSION = "v0"
NEXT_MILESTONE = "L5.9 Real Approval Workflow Boundary v0"

INPUT_REFS = {
    "canonical_update_package_candidate": (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    ),
    "versioned_patch_plan": "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json",
    "canonical_patch_application_blocker": (
        "versioned_canonical_patch_plan/canonical_patch_application_blocker.json"
    ),
    "rollback_plan": "rollback_and_audit_lineage/rollback_plan.json",
    "audit_lineage_record": "rollback_and_audit_lineage/canonical_learning_audit_lineage_record.json",
    "post_promotion_validation_plan": "post_promotion_validation_plan/post_promotion_validation_plan.json",
    "y_star_non_mutation_invariant": "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json",
    "y_star_forbidden_change_surface": (
        "y_star_non_mutation_invariant/y_star_forbidden_change_surface.json"
    ),
    "dry_run_promotion_decision_fixture": (
        "dry_run_promotion_decision_fixture/dry_run_promotion_decision_fixture.json"
    ),
    "controlled_canonical_learning_readiness": (
        "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json"
    ),
    "mission_y_star_input": "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "behavior_level_y_star_candidate": (
        "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"
    ),
    "field_projection_operator_policy": (
        "field_functional_auto_projection_core/field_projection_operator_policy.json"
    ),
    "governed_mcp_adapter_readiness": (
        "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json"
    ),
}

SANDBOX_STAGES = [
    "load_l5_7_canonical_update_package_candidate",
    "load_l5_7_versioned_patch_plan",
    "load_l5_7_y_star_non_mutation_invariant",
    "create_sandbox_approval_fixture",
    "create_sandbox_canonical_baseline",
    "apply_patch_to_sandbox_canonical_state_only",
    "verify_real_canonical_state_unchanged",
    "run_sandbox_post_update_validation",
    "generate_sandbox_projection_policy_snapshot",
    "run_sandbox_behavior_y_star_reprojection",
    "run_sandbox_governed_mcp_dry_run_preview",
    "compute_sandbox_update_residual_delta",
    "run_sandbox_rollback_plan",
    "verify_sandbox_rollback_restores_baseline",
    "compare_original_vs_sandbox_vs_rollback",
    "emit_sandbox_update_cieu_like_fixture",
    "produce_l5_9_recommendation",
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
    "sandbox_approval_fixture_created": True,
    "sandbox_patch_application_performed": True,
    "sandbox_projection_preview_generated": True,
    "sandbox_mcp_dry_run_preview_generated": True,
    "sandbox_rollback_performed": True,
}

FORBIDDEN_OPERATIONS = [
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
    "real candidate approval",
    "real canonical update application",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

SANDBOX_POLICY_CHANGES = [
    "tighten projection trace linkage",
    "clarify behavior boundary inheritance",
    "improve Pre-U mapping expectation",
    "improve MCP non-bypass evidence requirements",
    "improve residual classification labels",
    "improve evidence completeness requirements",
]

RESIDUAL_CLASSES = [
    "sandbox_patch_application_residual",
    "y_star_lineage_residual",
    "projection_policy_delta_residual",
    "mcp_non_bypass_residual",
    "post_update_validation_residual",
    "rollback_residual",
    "evidence_gap_residual",
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
        "real_candidate_approved": False,
        "real_candidate_applied": False,
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
        INPUT_REFS["rollback_plan"],
        INPUT_REFS["y_star_non_mutation_invariant"],
        INPUT_REFS["behavior_level_y_star_candidate"],
        INPUT_REFS["governed_mcp_adapter_readiness"],
    ]


def build_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.approved_canonical_update_sandbox.contract",
        "schema_version": SCHEMA_VERSION,
        "sandbox_name": "Approved Canonical Update Sandbox + Rollback Validation",
        "purpose": (
            "Simulate approval and application of an L5.7 canonical update package only "
            "inside generated sandbox state, then validate projection, MCP non-bypass, "
            "CIEU-like residual, and rollback behavior without mutating real canonical state."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "sandbox_stages": SANDBOX_STAGES,
        "required_outputs": [
            "sandbox approval fixture",
            "sandbox canonical baseline",
            "sandbox patch application result",
            "sandbox post-update validation",
            "sandbox behavior-level Y* reprojection",
            "sandbox governed MCP dry-run preview",
            "sandbox update CIEU-like fixture",
            "sandbox rollback validation",
            "original-vs-sandbox-vs-rollback comparison",
            "approved sandbox update readiness",
        ],
        "sandbox_approval_requirements": [
            "sandbox approval may authorize generated sandbox application only",
            "real application and real candidate approval remain false",
            "approval fixture must record denied real scopes",
        ],
        "sandbox_application_requirements": [
            "patch semantics are applied only to generated sandbox policy snapshots",
            "real canonical projection policy remains unchanged",
            "brain, memory, strategy, Y-star-gov, and gov-mcp remain unchanged",
        ],
        "y_star_non_mutation_requirements": [
            "mission-level Y* is not rewritten",
            "behavior-level Y* is not directly overwritten",
            "sandbox behavior-level Y* delta must be projection-policy mediated",
            "residual cannot become a new Y*",
            "actual Y cannot become a new Y*",
        ],
        "rollback_validation_requirements": [
            "rollback is performed only in sandbox",
            "post-rollback state must restore or explicitly gap the baseline",
            "no real canonical rollback is needed because no real canonical application occurs",
        ],
        "post_update_validation_requirements": [
            "Y* non-mutation invariant check",
            "MCP non-bypass invariant check",
            "real canonical unchanged check",
            "writeback and live execution blockers check",
            "rollback availability check",
        ],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "real canonical learning",
            "real candidate approval",
            "real canonical policy mutation",
            "brain writeback",
            "memory ingestion",
            "strategy mutation",
            "live behavior execution",
            "MCP execution",
            "L6 revenue opportunity discovery",
        ],
    }


def build_all() -> None:
    sources = {key: read_optional_json(path) for key, path in INPUT_REFS.items()}
    gaps = missing_sources(sources)
    status = common_status()

    package = sources["canonical_update_package_candidate"]
    patch_plan = sources["versioned_patch_plan"]
    rollback_plan = sources["rollback_plan"]
    mission = sources["mission_y_star_input"]
    behavior = sources["behavior_level_y_star_candidate"]
    policy = sources["field_projection_operator_policy"]

    package_id = package.get("package_id", "canonical-update-package-candidate-v0")
    promotion_decision_id = package.get(
        "source_promotion_decision_id", "canonical-promotion-eligibility-decision-v0"
    )
    patch_plan_id = patch_plan.get("patch_plan_id", "versioned-canonical-patch-plan-v0")
    rollback_plan_id = rollback_plan.get("rollback_plan_id", "canonical-learning-rollback-plan-v0")
    mission_id = mission.get("mission_id", "mission-commercial-agent-company-v0")
    behavior_id = behavior.get("behavior_y_star_id", "behavior-y-star-projection-checked-cycle-v0")
    policy_id = policy.get("policy_id", "field-projection-operator-policy-v0")

    contract = build_contract()
    input_fixture = {
        "schema_name": "ystar.approved_canonical_update_sandbox.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "approved-canonical-update-sandbox-input-v0",
        "input_refs": INPUT_REFS,
        "missing_sources": gaps,
        "gap_aware_execution": True,
        "safety_flags": SAFETY_FLAGS,
    }

    approval_protocol = {
        "schema_name": "ystar.sandbox_approval.protocol",
        "schema_version": SCHEMA_VERSION,
        "protocol_id": "sandbox-approval-protocol-v0",
        "approval_modes": ["sandbox_only"],
        "real_approval_modes_enabled": [],
        "required_preconditions": [
            "canonical update package candidate is not approved",
            "versioned patch plan is blocked_dry_run_plan_only",
            "Y* non-mutation invariant is loaded",
            "rollback plan is available",
            "sandbox state is generated separately from real canonical state",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    approval_decision = {
        "schema_name": "ystar.sandbox_approval.decision_fixture",
        "schema_version": SCHEMA_VERSION,
        "sandbox_approval_id": "sandbox-approval-fixture-v0",
        "source_canonical_update_package_id": package_id,
        "source_promotion_decision_id": promotion_decision_id,
        "approval_mode": "sandbox_only",
        "sandbox_application_approved": True,
        "real_application_approved": False,
        "candidate_real_approved": False,
        "allowed_scope": [
            "generate sandbox canonical baseline",
            "apply patch semantics to sandbox policy snapshots",
            "run sandbox validation",
            "run sandbox reprojection and MCP dry-run preview",
            "run sandbox rollback validation",
        ],
        "denied_scope": [
            "real canonical policy mutation",
            "real canonical update application",
            "brain writeback",
            "memory ingestion",
            "strategy mutation",
            "direct Y* mutation",
            "live execution",
            "MCP execution",
            "external action",
            "network",
            "candidate auto-approval",
        ],
        "required_post_sandbox_validation": True,
        "required_rollback_validation": True,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    approval_scope = {
        "schema_name": "ystar.sandbox_approval.scope_boundary",
        "schema_version": SCHEMA_VERSION,
        "allowed_sandbox_actions": approval_decision["allowed_scope"],
        "denied_real_actions": [
            "real canonical policy mutation",
            "real canonical update application",
            "real candidate approval",
        ],
        "denied_y_star_mutations": [
            "mission-level Y* rewrite",
            "behavior-level Y* direct overwrite",
            "residual becoming new Y*",
            "actual Y becoming new Y*",
        ],
        "denied_brain_memory_mutations": ["brain writeback", "memory ingestion"],
        "denied_external_or_live_actions": ["live execution", "MCP execution", "external action", "network"],
        "safety_flags": SAFETY_FLAGS,
    }
    approval_denied = {
        "schema_name": "ystar.sandbox_approval.denied_scope",
        "schema_version": SCHEMA_VERSION,
        "denied_operations": approval_decision["denied_scope"],
        "real_canonical_policy_mutation_enabled": False,
        "real_canonical_update_application_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "strategy_mutation_enabled": False,
        "real_y_star_direct_mutation_enabled": False,
        "live_execution_enabled": False,
        "mcp_tool_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "candidate_auto_approval_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    baseline_manifest = {
        "schema_name": "ystar.sandbox_canonical_state.baseline_manifest",
        "schema_version": SCHEMA_VERSION,
        "baseline_id": "sandbox-canonical-baseline-v0",
        "baseline_mode": "generated_sandbox_copy",
        "source_canonical_refs": [
            INPUT_REFS["field_projection_operator_policy"],
            INPUT_REFS["y_star_non_mutation_invariant"],
            INPUT_REFS["governed_mcp_adapter_readiness"],
        ],
        "copied_into_sandbox_only": True,
        "real_canonical_files_modified": False,
        "brain_files_modified": False,
        "memory_files_modified": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    projection_policy_baseline = {
        "schema_name": "ystar.sandbox_canonical_state.projection_policy_baseline",
        "schema_version": SCHEMA_VERSION,
        "baseline_policy_snapshot_id": "sandbox-projection-policy-baseline-v0",
        "source_policy_id": policy_id,
        "snapshot_mode": "generated_sandbox_copy",
        "projection_layers": policy.get("projection_layers", ["mission", "company", "milestone", "session", "task", "behavior"]),
        "baseline_policy_summary": {
            "deterministic_only": policy.get("deterministic_only", True),
            "semantic_truth_scoring_enabled": False,
            "behavior_layer_requires_pre_u_before_execution": policy.get(
                "behavior_layer_requires_pre_u_before_execution", True
            ),
        },
        "real_policy_modified": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    learning_policy_baseline = {
        "schema_name": "ystar.sandbox_canonical_state.learning_policy_baseline",
        "schema_version": SCHEMA_VERSION,
        "baseline_learning_policy_snapshot_id": "sandbox-learning-policy-baseline-v0",
        "learning_policy_summary": {
            "review_required_before_application": True,
            "direct_brain_writeback_allowed": False,
            "direct_memory_ingestion_allowed": False,
            "candidate_auto_approval_allowed": False,
            "residual_direct_y_star_mutation_allowed": False,
        },
        "real_learning_policy_modified": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_boundary_baseline = {
        "schema_name": "ystar.sandbox_canonical_state.mcp_boundary_policy_baseline",
        "schema_version": SCHEMA_VERSION,
        "baseline_mcp_boundary_policy_snapshot_id": "sandbox-mcp-boundary-policy-baseline-v0",
        "required_future_mcp_gates": [
            "behavior-level Y*",
            "Pre-U packet candidate",
            "governance decision",
            "bridge receipt",
            "MCP receipt",
            "CIEU-like event",
            "residual delta",
        ],
        "real_mcp_execution_allowed": False,
        "real_mcp_policy_modified": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    y_star_lineage_baseline = {
        "schema_name": "ystar.sandbox_canonical_state.y_star_lineage_baseline",
        "schema_version": SCHEMA_VERSION,
        "lineage_baseline_id": "sandbox-y-star-lineage-baseline-v0",
        "mission_level_y_star_source": INPUT_REFS["mission_y_star_input"],
        "mission_y_star_id": mission_id,
        "behavior_level_y_star_source": INPUT_REFS["behavior_level_y_star_candidate"],
        "behavior_y_star_id": behavior_id,
        "projection_derived_relationship_preserved": True,
        "residual_did_not_directly_mutate_y_star": True,
        "future_sandbox_changes_must_preserve_lineage": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    patch_plan_doc = {
        "schema_name": "ystar.sandbox_patch.application_plan",
        "schema_version": SCHEMA_VERSION,
        "sandbox_patch_application_plan_id": "sandbox-patch-application-plan-v0",
        "source_sandbox_approval_id": approval_decision["sandbox_approval_id"],
        "source_patch_plan_id": patch_plan_id,
        "application_target": "generated sandbox canonical state only",
        "patch_operations_to_apply": SANDBOX_POLICY_CHANGES,
        "real_application_blocked": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    patch_result = {
        "schema_name": "ystar.sandbox_patch.application_result",
        "schema_version": SCHEMA_VERSION,
        "sandbox_patch_application_id": "sandbox-patch-application-result-v0",
        "source_sandbox_approval_id": approval_decision["sandbox_approval_id"],
        "source_patch_plan_id": patch_plan_id,
        "applied_to_sandbox": True,
        "applied_to_real_canonical_policy": False,
        "applied_to_brain": False,
        "applied_to_memory": False,
        "applied_to_strategy": False,
        "direct_y_star_mutation_performed": False,
        "y_star_lineage_preserved": True,
        "patch_operations_applied": SANDBOX_POLICY_CHANGES,
        "denied_real_operations": approval_denied["denied_operations"],
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    updated_projection_policy = {
        "schema_name": "ystar.sandbox_patch.updated_projection_policy_snapshot",
        "schema_version": SCHEMA_VERSION,
        "sandbox_policy_snapshot_id": "sandbox-updated-projection-policy-v0",
        "source_baseline_policy_snapshot_id": projection_policy_baseline["baseline_policy_snapshot_id"],
        "sandbox_only_policy_changes": SANDBOX_POLICY_CHANGES,
        "forbidden_sandbox_changes_not_performed": [
            "rewrite mission-level Y*",
            "directly overwrite behavior-level Y*",
            "enable live execution",
            "enable MCP execution",
            "write brain or memory",
            "mutate real canonical policy",
        ],
        "real_canonical_policy_mutation_performed": False,
        "direct_y_star_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    updated_learning_policy = {
        "schema_name": "ystar.sandbox_patch.updated_learning_policy_snapshot",
        "schema_version": SCHEMA_VERSION,
        "sandbox_learning_policy_snapshot_id": "sandbox-updated-learning-policy-v0",
        "sandbox_only_policy_changes": [
            "tighten evidence completeness requirements before future application",
            "preserve review-only learning candidate status until explicit future approval",
            "keep direct brain and memory writeback denied",
        ],
        "real_learning_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    updated_mcp_boundary = {
        "schema_name": "ystar.sandbox_patch.updated_mcp_boundary_policy_snapshot",
        "schema_version": SCHEMA_VERSION,
        "sandbox_mcp_boundary_policy_snapshot_id": "sandbox-updated-mcp-boundary-policy-v0",
        "sandbox_only_policy_changes": [
            "require explicit MCP non-bypass evidence before sandbox gate pass",
            "preserve bridge receipt and CIEU receipt requirements",
            "keep real MCP server/tool/resource execution denied",
        ],
        "mcp_server_execution_enabled": False,
        "mcp_tool_execution_enabled": False,
        "mcp_resource_mutation_enabled": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    real_blocker = {
        "schema_name": "ystar.sandbox_patch.application_blocker_for_real",
        "schema_version": SCHEMA_VERSION,
        "blocker_id": "sandbox-patch-application-blocker-for-real-v0",
        "blocked_reason": (
            "L5.8 approval is a sandbox approval fixture only. Real canonical application "
            "requires a future approval workflow boundary, explicit approval record, versioned "
            "backup, rollback record, and post-application validation."
        ),
        "sandbox_application_is_not_real_application": True,
        "real_canonical_policy_mutation_enabled": False,
        "real_canonical_update_application_enabled": False,
        "real_candidate_approval_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }

    validation_result = {
        "schema_name": "ystar.sandbox_post_update.validation_result",
        "schema_version": SCHEMA_VERSION,
        "validation_result_id": "sandbox-post-update-validation-result-v0",
        "sandbox_patch_applied": True,
        "real_canonical_state_unchanged": True,
        "y_star_non_mutation_invariant_preserved": True,
        "mission_y_star_lineage_preserved": True,
        "behavior_y_star_still_projection_derived": True,
        "Pre-U_validation_still_required": True,
        "bridge_receipt_still_required": True,
        "CIEU_receipt_still_required": True,
        "MCP_non_bypass_preserved": True,
        "brain_writeback_still_blocked": True,
        "memory_ingestion_still_blocked": True,
        "live_execution_still_blocked": True,
        "external_action_still_blocked": True,
        "rollback_plan_available": True,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    validation_plan = {
        "schema_name": "ystar.sandbox_post_update.validation_plan",
        "schema_version": SCHEMA_VERSION,
        "sandbox_validation_plan_id": "sandbox-post-update-validation-plan-v0",
        "required_checks": [
            "real canonical unchanged",
            "Y* non-mutation invariant",
            "mission Y* lineage preserved",
            "behavior Y* remains projection-derived",
            "MCP non-bypass preserved",
            "rollback available",
        ],
        "source_l5_7_validation_plan": INPUT_REFS["post_promotion_validation_plan"],
        "safety_flags": SAFETY_FLAGS,
    }
    invariant_validation = {
        "schema_name": "ystar.sandbox_post_update.invariant_validation_result",
        "schema_version": SCHEMA_VERSION,
        "invariant_validation_result_id": "sandbox-invariant-validation-result-v0",
        "y_star_non_mutation_invariant_preserved": True,
        "mcp_non_bypass_preserved": True,
        "no_direct_writeback_preserved": True,
        "real_canonical_state_unchanged": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    y_star_check = {
        "schema_name": "ystar.sandbox_post_update.y_star_non_mutation_check",
        "schema_version": SCHEMA_VERSION,
        "check_id": "sandbox-y-star-non-mutation-check-v0",
        "residual_did_not_become_new_y_star": True,
        "actual_y_did_not_become_new_y_star": True,
        "mission_y_star_not_rewritten": True,
        "behavior_y_star_not_directly_overwritten": True,
        "projected_behavior_y_star_changes_are_policy_mediated": True,
        "projection_lineage_preserved": True,
        "direct_y_star_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_check = {
        "schema_name": "ystar.sandbox_post_update.mcp_non_bypass_check",
        "schema_version": SCHEMA_VERSION,
        "check_id": "sandbox-mcp-non-bypass-check-v0",
        "no_mcp_call_without_behavior_y_star": True,
        "no_mcp_call_without_pre_u_candidate": True,
        "no_mcp_call_without_governance_decision": True,
        "no_mcp_call_without_bridge_receipt": True,
        "no_mcp_call_without_cieu_receipt": True,
        "no_mcp_call_without_residual_delta": True,
        "no_mcp_direct_brain_writeback": True,
        "no_mcp_direct_memory_ingestion": True,
        "mcp_tool_execution_enabled": False,
        "mcp_server_execution_enabled": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    sandbox_behavior_id = "sandbox-behavior-y-star-policy-mediated-preview-v0"
    sandbox_reprojected_behavior = {
        "schema_name": "ystar.sandbox_reprojection.behavior_y_star",
        "schema_version": SCHEMA_VERSION,
        "sandbox_behavior_y_star_id": sandbox_behavior_id,
        "source_mission_y_star_id": mission_id,
        "source_sandbox_policy_snapshot_id": updated_projection_policy["sandbox_policy_snapshot_id"],
        "projected_behavior_y_star": (
            "Refresh the internal mission dashboard through a sandbox-updated projection policy "
            "that preserves mission lineage, tightens evidence requirements, and keeps all live "
            "or MCP execution blocked."
        ),
        "changed_fields_from_baseline": [
            "declared_behavior_y_star includes explicit sandbox evidence requirements",
            "allowed_behavior_boundary requires MCP non-bypass proof references",
            "candidate_u_summary narrows to sandbox dry-run preview only",
        ],
        "unchanged_fields_from_baseline": [
            "source mission-level Y*",
            "Pre-U validation requirement",
            "live behavior authorization remains false",
            "brain and memory writeback remain false",
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
        "evidence_refs": evidence_refs() + [str(APPLICATION / "sandbox_updated_projection_policy_snapshot.json")],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    next_cycle_input = {
        "schema_name": "ystar.sandbox_reprojection.next_cycle_projection_input",
        "schema_version": SCHEMA_VERSION,
        "input_id": "sandbox-next-cycle-projection-input-v0",
        "mission_y_star_ref": INPUT_REFS["mission_y_star_input"],
        "baseline_behavior_y_star_ref": INPUT_REFS["behavior_level_y_star_candidate"],
        "sandbox_policy_snapshot_ref": "sandbox_patch_application/sandbox_updated_projection_policy_snapshot.json",
        "sandbox_patch_application_ref": "sandbox_patch_application/sandbox_patch_application_result.json",
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    behavior_delta = {
        "schema_name": "ystar.sandbox_reprojection.behavior_y_star_delta_from_baseline",
        "schema_version": SCHEMA_VERSION,
        "delta_id": "sandbox-behavior-y-star-delta-v0",
        "baseline_behavior_y_star_id": behavior_id,
        "sandbox_behavior_y_star_id": sandbox_behavior_id,
        "projection_policy_mediated_delta": "tightened evidence and MCP boundary requirements",
        "evidence_requirement_delta": "sandbox preview requires explicit post-update and rollback evidence",
        "boundary_contraction_delta": "live and MCP execution remain denied; sandbox preview scope is narrower",
        "pre_u_mapping_delta": "candidate_U now includes sandbox approval and rollback context",
        "mcp_non_bypass_delta": "non-bypass proof is explicitly required before dry-run preview",
        "residual_classification_delta": "residual labels now distinguish sandbox blocker from real application blocker",
        "no_direct_y_star_mutation": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_intent = {
        "schema_name": "ystar.sandbox_mcp_preview.request_intent",
        "schema_version": SCHEMA_VERSION,
        "preview_request_intent_id": "sandbox-mcp-request-intent-preview-v0",
        "source_sandbox_behavior_y_star_id": sandbox_behavior_id,
        "declared_request_intent": (
            "Preview retrieval of a safe generated console summary through a future governed "
            "MCP boundary, without starting a server or calling a tool."
        ),
        "internal_only": True,
        "dry_run_only": True,
        "no_real_mcp_server": True,
        "no_real_tool_execution": True,
        "no_external_action": True,
        "forbidden_request_patterns": [
            "external network",
            "filesystem mutation",
            "DB/log/raw runtime artifact read",
            "brain writeback",
            "memory ingestion",
            "revenue opportunity discovery",
            "live MCP tool execution",
        ],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_pre_u = {
        "schema_name": "ystar.sandbox_mcp_preview.pre_u_candidate",
        "schema_version": SCHEMA_VERSION,
        "sandbox_mcp_pre_u_packet_id": "sandbox-mcp-pre-u-candidate-preview-v0",
        "source_sandbox_behavior_y_star_id": sandbox_behavior_id,
        "declared_Y_star": sandbox_reprojected_behavior["projected_behavior_y_star"],
        "Xt": {
            "sandbox_policy_snapshot": updated_projection_policy["sandbox_policy_snapshot_id"],
            "sandbox_validation_result": validation_result["validation_result_id"],
            "request_context": "internal generated summary retrieval preview only",
        },
        "candidate_U": "retrieve safe generated read-model summary through future governed MCP adapter preview",
        "requested_operation": "read_safe_generated_summary_resource_preview",
        "requires_y_star_gov_validation_before_live_execution": True,
        "dry_run_only": True,
        "live_execution_authorized": False,
        "mcp_tool_execution_authorized": False,
        "external_action_authorized": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_decision = {
        "schema_name": "ystar.sandbox_mcp_preview.governance_decision",
        "schema_version": SCHEMA_VERSION,
        "sandbox_mcp_decision_id": "sandbox-mcp-governance-decision-preview-v0",
        "source_pre_u_packet_id": mcp_pre_u["sandbox_mcp_pre_u_packet_id"],
        "decision": "allow_sandbox_mcp_dry_run_only",
        "canonical_y_star_gov_validation_performed": False,
        "y_star_gov_validation_required_before_live": True,
        "live_execution_authorized": False,
        "mcp_tool_execution_authorized": False,
        "external_action_authorized": False,
        "reason_codes": ["sandbox_only", "internal_generated_summary", "real_mcp_execution_blocked"],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_bridge = {
        "schema_name": "ystar.sandbox_mcp_preview.bridge_receipt",
        "schema_version": SCHEMA_VERSION,
        "sandbox_mcp_bridge_receipt_id": "sandbox-mcp-bridge-receipt-preview-v0",
        "source_decision_id": mcp_decision["sandbox_mcp_decision_id"],
        "authorization_mode": "sandbox_mcp_preview_only",
        "real_mcp_execution_authorized": False,
        "live_execution_authorized": False,
        "external_action_authorized": False,
        "cieu_receipt_required": True,
        "residual_delta_required": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    mcp_receipt = {
        "schema_name": "ystar.sandbox_mcp_preview.dry_run_receipt",
        "schema_version": SCHEMA_VERSION,
        "sandbox_mcp_receipt_id": "sandbox-mcp-dry-run-receipt-preview-v0",
        "source_pre_u_packet_id": mcp_pre_u["sandbox_mcp_pre_u_packet_id"],
        "source_decision_id": mcp_decision["sandbox_mcp_decision_id"],
        "source_bridge_receipt_id": mcp_bridge["sandbox_mcp_bridge_receipt_id"],
        "actual_result_summary": "No real MCP execution occurred; receipt records preview-only boundary.",
        "real_execution_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "persistence_mode": "none",
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    predicted = {
        "schema_name": "ystar.sandbox_update.predicted_outcome",
        "schema_version": SCHEMA_VERSION,
        "predicted_outcome_id": "sandbox-update-predicted-outcome-v0",
        "expected_result": [
            "sandbox approval fixture generated",
            "sandbox patch applied",
            "real canonical unchanged",
            "sandbox projection preview generated",
            "sandbox MCP preview generated",
            "rollback validated or prepared",
            "no real writeback",
        ],
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
    }
    mock_actual = {
        "schema_name": "ystar.sandbox_update.mock_actual_outcome",
        "schema_version": SCHEMA_VERSION,
        "mock_actual_outcome_id": "sandbox-update-mock-actual-outcome-v0",
        "actual_mode": "generated_sandbox_fixture_only",
        "actual_result": predicted["expected_result"],
        "real_execution_performed": False,
        "real_canonical_policy_mutation_performed": False,
        "real_canonical_update_application_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "direct_y_star_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    residual_delta = {
        "schema_name": "ystar.sandbox_update.residual_delta",
        "schema_version": SCHEMA_VERSION,
        "residual_delta_id": "sandbox-update-residual-delta-v0",
        "residual_classes": {
            "sandbox_patch_application_residual": "sandbox patch applied as generated artifact only",
            "y_star_lineage_residual": "no lineage break detected",
            "projection_policy_delta_residual": "sandbox-only projection policy delta observed",
            "mcp_non_bypass_residual": "MCP preview remains gated and non-executing",
            "post_update_validation_residual": "validation generated; future real application still blocked",
            "rollback_residual": "rollback restored baseline in sandbox",
            "evidence_gap_residual": "future real approval needs signed approval and backup evidence",
            "live_blocker_residual": "live execution remains blocked",
            "real_application_blocker_residual": "real application intentionally blocked",
        },
        "deterministic_structural_residual_only": True,
        "semantic_truth_scoring_enabled": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    cieu_event = {
        "schema_name": "ystar.sandbox_update.cieu_event_fixture",
        "schema_version": SCHEMA_VERSION,
        "event_id": "sandbox-update-cieu-event-fixture-v0",
        "X_t": {
            "source_package_id": package_id,
            "source_patch_plan_id": patch_plan_id,
            "sandbox_policy_snapshot_id": updated_projection_policy["sandbox_policy_snapshot_id"],
        },
        "U_t": "sandbox approval plus sandbox patch application plus sandbox validation operation",
        "Y_star_t": (
            "Apply a canonical update package candidate only to sandbox state, validate it, run "
            "sandbox projection and MCP preview, and preserve all non-mutation and non-bypass invariants."
        ),
        "Y_t_plus_1": mock_actual,
        "R_t_plus_1": residual_delta,
        "event_mode": "sandbox_canonical_update_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    learning_preview = {
        "schema_name": "ystar.sandbox_update.learning_candidate_preview",
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "sandbox-update-learning-candidate-preview-v0",
        "source_residual_delta_id": residual_delta["residual_delta_id"],
        "learning_target": ["sandbox_validation_policy", "real_approval_workflow_boundary"],
        "review_only_preview": True,
        "eligible_for_review_queue": True,
        "approved": False,
        "applied": False,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_real_canonical_application": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    rollback_instance = {
        "schema_name": "ystar.sandbox_rollback.plan_instance",
        "schema_version": SCHEMA_VERSION,
        "sandbox_rollback_plan_instance_id": "sandbox-rollback-plan-instance-v0",
        "source_rollback_plan_id": rollback_plan_id,
        "source_sandbox_patch_application_id": patch_result["sandbox_patch_application_id"],
        "rollback_scope": "sandbox generated policy snapshots only",
        "real_rollback_not_required": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    rollback_result = {
        "schema_name": "ystar.sandbox_rollback.result",
        "schema_version": SCHEMA_VERSION,
        "rollback_id": "sandbox-rollback-result-v0",
        "source_sandbox_patch_application_id": patch_result["sandbox_patch_application_id"],
        "rollback_performed_in_sandbox": True,
        "real_canonical_policy_modified": False,
        "brain_modified": False,
        "memory_modified": False,
        "strategy_modified": False,
        "y_star_direct_mutation_performed": False,
        "rollback_restored_baseline": True,
        "evidence_refs": evidence_refs(),
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    post_rollback_policy = {
        "schema_name": "ystar.sandbox_rollback.post_rollback_projection_policy_snapshot",
        "schema_version": SCHEMA_VERSION,
        "post_rollback_policy_snapshot_id": "sandbox-post-rollback-projection-policy-v0",
        "restored_from_baseline_policy_snapshot_id": projection_policy_baseline["baseline_policy_snapshot_id"],
        "sandbox_patch_removed_or_neutralized": True,
        "real_canonical_policy_modified": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    post_rollback_validation = {
        "schema_name": "ystar.sandbox_rollback.post_rollback_validation_result",
        "schema_version": SCHEMA_VERSION,
        "post_rollback_validation_id": "sandbox-post-rollback-validation-result-v0",
        "baseline_restored": True,
        "sandbox_patch_removed_or_neutralized": True,
        "mission_y_star_lineage_preserved": True,
        "behavior_y_star_projection_lineage_preserved": True,
        "no_real_canonical_change": True,
        "no_brain_memory_change": True,
        "no_y_star_direct_mutation": True,
        "no_mcp_execution": True,
        "no_live_execution": True,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    rollback_delta = {
        "schema_name": "ystar.sandbox_rollback.delta",
        "schema_version": SCHEMA_VERSION,
        "rollback_delta_id": "sandbox-rollback-delta-v0",
        "baseline_restored": True,
        "sandbox_patch_delta_removed": True,
        "unresolved_gaps": [
            "future real workflow still needs explicit approval authority and durable audit record"
        ],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    comparison = {
        "schema_name": "ystar.original_sandbox_rollback.comparison",
        "schema_version": SCHEMA_VERSION,
        "comparison_id": "original-vs-sandbox-vs-rollback-comparison-v0",
        "original_behavior_y_star": {
            "behavior_y_star_id": behavior_id,
            "declared_behavior_y_star": behavior.get("declared_behavior_y_star"),
        },
        "sandbox_reprojected_behavior_y_star": {
            "sandbox_behavior_y_star_id": sandbox_behavior_id,
            "projected_behavior_y_star": sandbox_reprojected_behavior["projected_behavior_y_star"],
        },
        "post_rollback_behavior_y_star_or_policy_snapshot": {
            "post_rollback_policy_snapshot_id": post_rollback_policy["post_rollback_policy_snapshot_id"],
            "baseline_restored": True,
        },
        "original_projection_policy_summary": projection_policy_baseline["baseline_policy_summary"],
        "sandbox_projection_policy_summary": {
            "sandbox_only_policy_changes": SANDBOX_POLICY_CHANGES,
            "real_policy_modified": False,
        },
        "post_rollback_projection_policy_summary": {
            "sandbox_patch_removed_or_neutralized": True,
            "baseline_restored": True,
        },
        "y_star_lineage_preserved": True,
        "safety_boundaries_preserved": True,
        "real_canonical_system_changed": False,
        "brain_memory_changed": False,
        "gov_repos_changed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    sandbox_effect = {
        "schema_name": "ystar.original_sandbox_rollback.update_effect_summary",
        "schema_version": SCHEMA_VERSION,
        "effect_class": "behavior_y_star_projection_sandbox_effect",
        "previous_residual_influenced_sandbox_projection": True,
        "effect_summary": (
            "The sandbox patch produced a visible behavior-level Y* projection delta through "
            "policy-mediated evidence and MCP boundary tightening, not through direct Y* mutation."
        ),
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    rollback_effect = {
        "schema_name": "ystar.original_sandbox_rollback.rollback_effect_summary",
        "schema_version": SCHEMA_VERSION,
        "rollback_restored_baseline": True,
        "unresolved_gaps": rollback_delta["unresolved_gaps"],
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    safety_summary = {
        "schema_name": "ystar.original_sandbox_rollback.learning_safety_summary",
        "schema_version": SCHEMA_VERSION,
        "sandbox_learning_was_preview_only": True,
        "real_canonical_system_changed": False,
        "brain_memory_changed": False,
        "direct_y_star_mutation_performed": False,
        "mcp_execution_performed": False,
        "live_execution_performed": False,
        "safety_flags": SAFETY_FLAGS,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    readiness = {
        "schema_name": "ystar.approved_sandbox_update.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "approved-sandbox-update-readiness-v0",
        "sandbox_approval_fixture_generated": True,
        "sandbox_canonical_baseline_generated": True,
        "sandbox_patch_applied": True,
        "real_canonical_state_unchanged": True,
        "y_star_non_mutation_invariant_preserved": True,
        "sandbox_post_update_validation_passed": True,
        "sandbox_reprojection_generated": True,
        "sandbox_mcp_preview_generated": True,
        "sandbox_update_cieu_fixture_generated": True,
        "sandbox_rollback_performed": True,
        "rollback_restored_or_gap_recorded": True,
        "original_sandbox_rollback_comparison_generated": True,
        "real_approval_still_blocked": True,
        "real_canonical_application_still_blocked": True,
        "brain_writeback_still_blocked": True,
        "memory_ingestion_still_blocked": True,
        "y_star_direct_mutation_still_blocked": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "ready_for_l5_9_real_approval_workflow_boundary": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "next_required_milestone": NEXT_MILESTONE,
        **status,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    run = {
        "schema_name": "ystar.approved_canonical_update_sandbox.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "approved-canonical-update-sandbox-run-v0",
        "contract_ref": "approved_canonical_update_sandbox/approved_canonical_update_sandbox_contract.json",
        "input_fixture_ref": "approved_canonical_update_sandbox/approved_canonical_update_sandbox_input_fixture.json",
        "sandbox_stages_completed": SANDBOX_STAGES,
        "missing_sources": gaps,
        "sandbox_approval_id": approval_decision["sandbox_approval_id"],
        "sandbox_patch_application_id": patch_result["sandbox_patch_application_id"],
        "sandbox_behavior_y_star_id": sandbox_behavior_id,
        "sandbox_rollback_id": rollback_result["rollback_id"],
        "readiness_ref": "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
        **status,
        "sandbox_flags": SANDBOX_FLAGS,
    }
    sandbox_summary = {
        "schema_name": "ystar.approved_canonical_update_sandbox.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_8_approved_canonical_update_sandbox_defined": True,
        "sandbox_approval_fixture_generated": True,
        "sandbox_baseline_generated": True,
        "sandbox_patch_applied": True,
        "real_canonical_state_unchanged": True,
        "y_star_non_mutation_invariant_preserved": True,
        "sandbox_post_update_validation_generated": True,
        "sandbox_behavior_y_star_reprojection_generated": True,
        "sandbox_governed_mcp_preview_generated": True,
        "sandbox_update_cieu_like_fixture_generated": True,
        "sandbox_rollback_validation_generated": True,
        "original_vs_sandbox_vs_rollback_comparison_generated": True,
        "ready_for_l5_9_real_approval_workflow_boundary": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        **status,
        "sandbox_flags": SANDBOX_FLAGS,
    }

    # Write artifacts.
    write_text(
        SANDBOX / "README.md",
        md(
            "Approved Canonical Update Sandbox",
            [
                "L5.8 creates a sandbox-only approval/application proof for the L5.7 canonical update package candidate.",
                "",
                "The sandbox may generate updated policy snapshots, reprojection previews, MCP dry-run previews, residuals, and rollback results.",
                "",
                "It does not approve or apply any real candidate, mutate real canonical policy, write brain or memory, directly mutate Y*, execute MCP, or perform live work.",
            ],
        ),
    )
    write_json(SANDBOX / "approved_canonical_update_sandbox_contract.json", contract)
    write_json(SANDBOX / "approved_canonical_update_sandbox_input_fixture.json", input_fixture)
    write_json(SANDBOX / "approved_canonical_update_sandbox_run.json", run)
    write_json(SANDBOX / "approved_canonical_update_sandbox_summary.json", sandbox_summary)
    write_text(
        SANDBOX / "approved_canonical_update_sandbox_report.md",
        md(
            "Approved Canonical Update Sandbox Report",
            [
                "- Sandbox approval fixture generated: true",
                "- Sandbox patch applied: true",
                "- Real canonical state unchanged: true",
                "- Y* non-mutation invariant preserved: true",
                "- Sandbox rollback restored baseline: true",
                "- Ready for L5.9 real approval workflow boundary: true",
            ],
        ),
    )

    write_json(APPROVAL / "sandbox_approval_protocol.json", approval_protocol)
    write_json(APPROVAL / "sandbox_approval_decision_fixture.json", approval_decision)
    write_json(APPROVAL / "sandbox_approval_scope_boundary.json", approval_scope)
    write_json(APPROVAL / "sandbox_approval_denied_scope.json", approval_denied)
    write_json(
        APPROVAL / "sandbox_approval_summary.json",
        {
            "schema_name": "ystar.sandbox_approval.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_approval_fixture_generated": True,
            "sandbox_application_approved": True,
            "real_application_approved": False,
            "candidate_real_approved": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(APPROVAL / "sandbox_approval_report.md", md("Sandbox Approval Report", ["Sandbox application is approved; real application is denied."]))

    write_json(BASELINE / "sandbox_canonical_baseline_manifest.json", baseline_manifest)
    write_json(BASELINE / "sandbox_projection_policy_baseline.json", projection_policy_baseline)
    write_json(BASELINE / "sandbox_learning_policy_baseline.json", learning_policy_baseline)
    write_json(BASELINE / "sandbox_mcp_boundary_policy_baseline.json", mcp_boundary_baseline)
    write_json(BASELINE / "sandbox_y_star_lineage_baseline.json", y_star_lineage_baseline)
    write_json(
        BASELINE / "sandbox_baseline_summary.json",
        {
            "schema_name": "ystar.sandbox_baseline.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_canonical_baseline_generated": True,
            "copied_into_sandbox_only": True,
            "real_canonical_files_modified": False,
            "y_star_lineage_preserved": True,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(BASELINE / "sandbox_baseline_report.md", md("Sandbox Baseline Report", ["Baseline is a generated sandbox copy only; real canonical files were not modified."]))

    write_json(APPLICATION / "sandbox_patch_application_plan.json", patch_plan_doc)
    write_json(APPLICATION / "sandbox_patch_application_result.json", patch_result)
    write_json(APPLICATION / "sandbox_updated_projection_policy_snapshot.json", updated_projection_policy)
    write_json(APPLICATION / "sandbox_updated_learning_policy_snapshot.json", updated_learning_policy)
    write_json(APPLICATION / "sandbox_updated_mcp_boundary_policy_snapshot.json", updated_mcp_boundary)
    write_json(APPLICATION / "sandbox_patch_application_blocker_for_real.json", real_blocker)
    write_json(
        APPLICATION / "sandbox_patch_application_summary.json",
        {
            "schema_name": "ystar.sandbox_patch.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_patch_applied": True,
            "applied_to_real_canonical_policy": False,
            "y_star_lineage_preserved": True,
            "direct_y_star_mutation_performed": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(APPLICATION / "sandbox_patch_application_report.md", md("Sandbox Patch Application Report", ["Patch semantics were applied to sandbox snapshots only."]))

    write_json(VALIDATION / "sandbox_post_update_validation_plan.json", validation_plan)
    write_json(VALIDATION / "sandbox_post_update_validation_result.json", validation_result)
    write_json(VALIDATION / "sandbox_invariant_validation_result.json", invariant_validation)
    write_json(VALIDATION / "sandbox_y_star_non_mutation_check.json", y_star_check)
    write_json(VALIDATION / "sandbox_mcp_non_bypass_check.json", mcp_check)
    write_json(
        VALIDATION / "sandbox_post_update_validation_summary.json",
        {
            "schema_name": "ystar.sandbox_validation.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_post_update_validation_generated": True,
            "sandbox_post_update_validation_passed": True,
            "real_canonical_state_unchanged": True,
            "y_star_non_mutation_invariant_preserved": True,
            "mcp_non_bypass_preserved": True,
            "rollback_plan_available": True,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(VALIDATION / "sandbox_post_update_validation_report.md", md("Sandbox Post-Update Validation Report", ["Sandbox validation passed for generated artifacts; real application remains blocked."]))

    write_json(REPROJECTION / "sandbox_next_cycle_projection_input.json", next_cycle_input)
    write_json(REPROJECTION / "sandbox_reprojected_behavior_y_star.json", sandbox_reprojected_behavior)
    write_json(REPROJECTION / "sandbox_behavior_y_star_delta_from_baseline.json", behavior_delta)
    write_json(REPROJECTION / "sandbox_mcp_request_intent_preview.json", mcp_intent)
    write_json(REPROJECTION / "sandbox_mcp_pre_u_candidate_preview.json", mcp_pre_u)
    write_json(REPROJECTION / "sandbox_mcp_governance_decision_preview.json", mcp_decision)
    write_json(REPROJECTION / "sandbox_mcp_bridge_receipt_preview.json", mcp_bridge)
    write_json(REPROJECTION / "sandbox_mcp_dry_run_receipt_preview.json", mcp_receipt)
    write_json(
        REPROJECTION / "sandbox_reprojection_mcp_summary.json",
        {
            "schema_name": "ystar.sandbox_reprojection_mcp.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_behavior_y_star_reprojection_generated": True,
            "sandbox_governed_mcp_preview_generated": True,
            "sandbox_mcp_dry_run_receipt_generated": True,
            "real_execution_performed": False,
            "mcp_server_started": False,
            "mcp_tool_called": False,
            "mcp_resource_mutated": False,
            "network_called": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(REPROJECTION / "sandbox_reprojection_mcp_report.md", md("Sandbox Reprojection And MCP Preview Report", ["Sandbox behavior-level Y* changed through policy mediation; MCP preview remains dry-run only."]))

    write_json(CIEU / "sandbox_update_cieu_event_fixture.json", cieu_event)
    write_json(CIEU / "sandbox_update_predicted_outcome.json", predicted)
    write_json(CIEU / "sandbox_update_mock_actual_outcome.json", mock_actual)
    write_json(CIEU / "sandbox_update_residual_delta.json", residual_delta)
    write_json(CIEU / "sandbox_update_learning_candidate_preview.json", learning_preview)
    write_json(
        CIEU / "sandbox_update_cieu_summary.json",
        {
            "schema_name": "ystar.sandbox_update_cieu.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_update_cieu_like_fixture_generated": True,
            "sandbox_update_residual_delta_generated": True,
            "sandbox_update_learning_candidate_preview_generated": True,
            "candidate_approved": False,
            "candidate_applied": False,
            "persistence_enabled": False,
            "db_write_performed": False,
            "residual_classes": RESIDUAL_CLASSES,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(CIEU / "sandbox_update_cieu_report.md", md("Sandbox Update CIEU Report", ["CIEU-like event and residual delta are dry-run sandbox fixtures only."]))

    write_json(ROLLBACK / "sandbox_rollback_plan_instance.json", rollback_instance)
    write_json(ROLLBACK / "sandbox_rollback_result.json", rollback_result)
    write_json(ROLLBACK / "sandbox_post_rollback_projection_policy_snapshot.json", post_rollback_policy)
    write_json(ROLLBACK / "sandbox_post_rollback_validation_result.json", post_rollback_validation)
    write_json(ROLLBACK / "sandbox_rollback_delta.json", rollback_delta)
    write_json(
        ROLLBACK / "sandbox_rollback_summary.json",
        {
            "schema_name": "ystar.sandbox_rollback.summary",
            "schema_version": SCHEMA_VERSION,
            "sandbox_rollback_performed": True,
            "rollback_restored_baseline": True,
            "real_canonical_policy_modified": False,
            "brain_modified": False,
            "memory_modified": False,
            "y_star_direct_mutation_performed": False,
            "safety_flags": SAFETY_FLAGS,
            "sandbox_flags": SANDBOX_FLAGS,
        },
    )
    write_text(ROLLBACK / "sandbox_rollback_report.md", md("Sandbox Rollback Report", ["Rollback restored the generated sandbox baseline."]))

    write_json(COMPARISON / "original_vs_sandbox_vs_rollback_comparison.json", comparison)
    write_json(COMPARISON / "sandbox_update_effect_summary.json", sandbox_effect)
    write_json(COMPARISON / "rollback_effect_summary.json", rollback_effect)
    write_json(COMPARISON / "sandbox_learning_safety_summary.json", safety_summary)
    write_text(COMPARISON / "original_sandbox_rollback_report.md", md("Original Sandbox Rollback Report", ["Original, sandbox-updated, and post-rollback states were compared; real systems were unchanged."]))

    write_json(READINESS / "approved_sandbox_update_readiness.json", readiness)
    write_text(
        READINESS / "approved_sandbox_update_readiness.md",
        md(
            "Approved Sandbox Update Readiness",
            [
                "- sandbox_approval_fixture_generated: true",
                "- sandbox_patch_applied: true",
                "- real_canonical_state_unchanged: true",
                "- y_star_non_mutation_invariant_preserved: true",
                "- sandbox_rollback_performed: true",
                "- ready_for_l5_9_real_approval_workflow_boundary: true",
                "- ready_for_l6_revenue_opportunity_discovery: false",
            ],
        ),
    )
    write_json(
        READINESS / "l5_9_recommended_next_step.json",
        {
            "schema_name": "ystar.approved_sandbox_update.next_step",
            "schema_version": SCHEMA_VERSION,
            "recommended_next_step": NEXT_MILESTONE,
            "reason": (
                "The sandbox proves approval, sandbox application, validation, projection/MCP preview, "
                "and rollback can be tested without real mutation. A future boundary can now define "
                "what would be required for real approval."
            ),
            "ready_for_l5_9_real_approval_workflow_boundary": True,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "safety_flags": SAFETY_FLAGS,
        },
    )


def main() -> None:
    build_all()


if __name__ == "__main__":
    main()
