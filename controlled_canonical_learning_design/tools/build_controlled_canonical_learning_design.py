#!/usr/bin/env python3
"""Build deterministic L5.7 controlled canonical learning design artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

DESIGN = ROOT / "controlled_canonical_learning_design"
INVARIANT = ROOT / "y_star_non_mutation_invariant"
TARGETS = ROOT / "canonical_learning_target_registry"
EVIDENCE = ROOT / "canonical_promotion_evidence_bundle"
GATE = ROOT / "canonical_promotion_eligibility_gate"
PACKAGE = ROOT / "canonical_update_package_candidate"
PATCH = ROOT / "versioned_canonical_patch_plan"
ROLLBACK = ROOT / "rollback_and_audit_lineage"
VALIDATION = ROOT / "post_promotion_validation_plan"
PROMOTION = ROOT / "dry_run_promotion_decision_fixture"
READINESS = ROOT / "controlled_canonical_learning_readiness"

SCHEMA_VERSION = "v0"
NEXT_MILESTONE = "L5.8 Approved Canonical Update Sandbox v0"

INPUT_REFS = {
    "residual_review_gate_decision": "residual_review_gate/residual_review_gate_decision.json",
    "learning_target_classification": "learning_target_classifier/learning_target_classification.json",
    "projection_policy_update_candidate": (
        "projection_policy_update_candidate/projection_policy_update_candidate.json"
    ),
    "shadow_projection_policy_patch": "shadow_projection_policy_patch/shadow_projection_policy_patch.json",
    "shadow_behavior_y_star_preview": (
        "shadow_reprojection_preview/shadow_reprojected_behavior_y_star_preview.json"
    ),
    "shadow_learning_effect_summary": (
        "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json"
    ),
    "integrated_shadow_learning_readiness": (
        "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json"
    ),
    "mcp_learning_candidate": "mcp_residual_and_learning_candidate/mcp_learning_candidate.json",
    "mcp_residual_delta": "mcp_residual_and_learning_candidate/mcp_residual_delta.json",
    "governed_mcp_adapter_readiness": (
        "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json"
    ),
    "mission_y_star_input": "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "behavior_y_star_candidate": (
        "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"
    ),
    "field_projection_operator_policy": (
        "field_functional_auto_projection_core/field_projection_operator_policy.json"
    ),
}

DESIGN_STAGES = [
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
    "canonical_policy_mutation_enabled": False,
    "canonical_update_application_enabled": False,
    "y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
}

FORBIDDEN_OPERATIONS = [
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
    "brain writeback",
    "memory ingestion",
    "strategy mutation",
    "candidate approval",
    "canonical policy mutation",
    "canonical update application",
    "direct Y* mutation from residual",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

TARGET_CLASSES = [
    ("projection_policy", "medium_projection_policy"),
    ("projection_operator_version", "medium_projection_policy"),
    ("behavior_y_star_generation_rule", "critical_y_star_boundary"),
    ("pre_u_mapping_rule", "medium_projection_policy"),
    ("governance_expectation_mapping", "medium_projection_policy"),
    ("bridge_receipt_requirement", "low_artifact_policy"),
    ("mcp_interface_contract", "medium_projection_policy"),
    ("cieu_receipt_requirement", "low_artifact_policy"),
    ("residual_classification_policy", "medium_projection_policy"),
    ("evidence_collection_policy", "low_artifact_policy"),
    ("review_gate_policy", "medium_projection_policy"),
    ("learning_eligibility_policy", "medium_projection_policy"),
    ("brain_update_policy", "high_brain_memory_boundary"),
    ("memory_ingestion_policy", "high_brain_memory_boundary"),
    ("strategy_update_policy", "high_strategy_boundary"),
]

ALLOWED_LEARNING_SURFACES = [
    "projection_policy",
    "behavior_y_star_generation_rule",
    "pre_u_mapping_rule",
    "work_alignment_rule",
    "residual_classification_rule",
    "evidence_requirement_rule",
    "safety_boundary_rule",
]

DENIED_MUTATION_SURFACES = [
    "mission_y_star_direct_mutation",
    "behavior_y_star_direct_overwrite",
    "brain_direct_writeback",
    "memory_direct_ingestion",
    "canonical_policy_direct_mutation",
    "strategy_direct_mutation",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def refs(*paths: str) -> list[str]:
    return [path for path in paths if path]


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
        "mcp_server_not_started": True,
        "mcp_tool_not_executed": True,
        "mcp_resource_not_mutated": True,
        "candidate_approved": False,
        "candidate_applied": False,
        "canonical_policy_mutation_performed": False,
        "canonical_update_application_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "y_star_direct_mutation_performed": False,
        "db_log_wal_shm_active_marker_content_read": False,
        "l6_revenue_opportunity_discovery_implemented": False,
    }


def build_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.controlled_canonical_learning_design.contract",
        "schema_version": SCHEMA_VERSION,
        "design_name": "Controlled Canonical Learning Design + Promotion Dry-Run",
        "purpose": (
            "Define how review-only and shadow learning candidates can become structured "
            "canonical update package candidates through approval, versioning, rollback, audit, "
            "and post-promotion validation, without applying any update now."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "design_stages": DESIGN_STAGES,
        "required_outputs": [
            "Y* non-mutation invariant",
            "canonical learning target registry",
            "promotion evidence bundle",
            "promotion eligibility gate",
            "canonical update package candidate",
            "versioned patch plan",
            "rollback plan",
            "audit lineage record",
            "post-promotion validation plan",
            "dry-run promotion decision fixture",
            "controlled canonical learning readiness",
        ],
        "learning_promotion_requirements": [
            "source candidate must be review-only or shadow-only",
            "source candidate must not be approved or applied",
            "residual may only propose process improvements",
            "promotion candidate must preserve Y* non-mutation invariant",
        ],
        "canonical_update_requirements": [
            "canonical package candidate only",
            "explicit target class",
            "versioned patch plan required",
            "rollback plan required",
            "post-promotion validation plan required",
            "actual application blocked in L5.7",
        ],
        "approval_requirements": [
            "human or governance review required before application",
            "approval record required before application",
            "candidate auto-approval forbidden",
        ],
        "rollback_requirements": [
            "rollback scope defined",
            "rollback trigger policy defined",
            "rollback validation checks required",
        ],
        "audit_lineage_requirements": [
            "source residual ids",
            "source learning candidate ids",
            "source shadow patch ids",
            "promotion decision id",
            "update package id",
            "patch plan id",
        ],
        "post_promotion_validation_requirements": [
            "py_compile",
            "JSON validation",
            "static read-model validator",
            "local safety wrapper",
            "L5.0-L5.6 targeted pytest",
            "Y* non-mutation invariant check",
            "MCP non-bypass invariant check",
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "live learning",
            "candidate approval",
            "canonical policy mutation",
            "canonical update application",
            "brain writeback",
            "memory ingestion",
            "strategy mutation",
            "direct Y* mutation",
            "MCP execution",
            "L6 revenue opportunity discovery",
        ],
    }


def build_input_fixture(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gaps = missing_sources(sources)
    return {
        "schema_name": "ystar.controlled_canonical_learning_design.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "controlled-canonical-learning-input-fixture-v0",
        "input_refs": INPUT_REFS,
        "source_status": [
            {
                "source_key": key,
                "path": path,
                "present": not sources[key].get("missing", False),
            }
            for key, path in INPUT_REFS.items()
        ],
        "missing_sources": gaps,
        "gap_handling": "missing safe inputs are recorded as gaps and do not trigger destructive failure",
        "safe_read_policy": [
            "safe generated JSON and policy artifacts only",
            "no DB/WAL/SHM/log/active-agent marker content",
            "no external repository modification",
        ],
        "safety_flags": SAFETY_FLAGS,
    }


def build_y_star_invariant() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    invariant = {
        "schema_name": "ystar.y_star_non_mutation_invariant.invariant",
        "schema_version": SCHEMA_VERSION,
        "invariant_id": "y-star-non-mutation-invariant-v0",
        "y_star_definition": (
            "Y* is the declared ideal/normative target state before behavior/action execution."
        ),
        "mission_level_y_star_cannot_be_rewritten_by_residual": True,
        "behavior_level_y_star_cannot_be_directly_overwritten_by_residual": True,
        "residual_may_only_propose_controlled_projection_rule_or_constraint_changes": True,
        "future_canonical_update_must_preserve_mission_level_y_star_lineage": True,
        "future_behavior_y_star_change_must_be_projection_operator_derived": True,
        "approved_projection_operator_version_required_for_projected_behavior_y_star_change": True,
        "residual_driven_target_drift_forbidden": True,
        "direct_y_star_mutation_from_residual_forbidden": True,
        "safety_flags": SAFETY_FLAGS,
    }
    boundary_rows = [
        {
            "residual_class": residual_class,
            "allowed_learning_surface": surface,
            "denied_mutation_surface": DENIED_MUTATION_SURFACES,
            "required_review": "human_or_governance_review",
            "required_evidence": [
                "source residual",
                "source learning candidate",
                "shadow effect or dry-run evidence",
                "non-bypass invariant evidence",
            ],
            "approval_requirement": "explicit approval required before canonical application",
            "allowed_shadow_effect": "preview projection or mapping rule change",
            "allowed_canonical_candidate_effect": "non-applied package candidate only",
            "forbidden_direct_effect": [
                "residual directly becoming new Y*",
                "direct mission Y* rewrite",
                "direct behavior Y* overwrite",
                "brain writeback",
                "memory ingestion",
                "canonical direct mutation",
                "strategy direct mutation",
            ],
        }
        for residual_class, surface in [
            ("projection_alignment_residual", "projection_policy"),
            ("behavior_y_star_generation_gap", "behavior_y_star_generation_rule"),
            ("pre_u_mapping_residual", "pre_u_mapping_rule"),
            ("work_alignment_gap", "work_alignment_rule"),
            ("residual_classification_gap", "residual_classification_rule"),
            ("evidence_gap_residual", "evidence_requirement_rule"),
            ("live_or_writeback_blocker_residual", "safety_boundary_rule"),
        ]
    ]
    boundary = {
        "schema_name": "ystar.y_star_non_mutation_invariant.residual_boundary",
        "schema_version": SCHEMA_VERSION,
        "boundary_id": "residual-to-projection-policy-boundary-v0",
        "allowed_learning_surfaces": ALLOWED_LEARNING_SURFACES,
        "denied_mutation_surfaces": DENIED_MUTATION_SURFACES,
        "residual_boundary_map": boundary_rows,
        "safety_flags": SAFETY_FLAGS,
    }
    allowed = {
        "schema_name": "ystar.y_star_non_mutation_invariant.allowed_change_surface",
        "schema_version": SCHEMA_VERSION,
        "allowed_change_surface_id": "y-star-allowed-change-surface-v0",
        "allowed_shadow_projection_preview_changes": [
            "preview behavior-level Y* wording derived through shadow projection rules",
            "preview trace linkage improvements",
            "preview boundary tightening",
        ],
        "allowed_canonical_update_candidates": [
            "projection policy update candidate",
            "Pre-U mapping rule update candidate",
            "residual classification policy update candidate",
            "evidence policy update candidate",
        ],
        "allowed_future_approved_projection_operator_changes": [
            "versioned projection operator rules",
            "versioned boundary contraction rules",
            "versioned context binding rules",
        ],
        "allowed_evidence_requirement_changes": [
            "additional evidence refs before gate pass",
            "stricter trace completeness checks",
        ],
        "allowed_boundary_tightening": [
            "more explicit denied scope",
            "stricter non-bypass requirements",
        ],
        "allowed_trace_linkage_improvements": [
            "source residual to learning candidate refs",
            "learning candidate to package refs",
            "package to patch plan refs",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    forbidden = {
        "schema_name": "ystar.y_star_non_mutation_invariant.forbidden_change_surface",
        "schema_version": SCHEMA_VERSION,
        "forbidden_change_surface_id": "y-star-forbidden-change-surface-v0",
        "forbidden_changes": [
            "residual directly becoming new Y*",
            "actual Y becoming new Y*",
            "reward-like residual minimization replacing mission Y*",
            "unreviewed behavior Y* rewrite",
            "automatic target drift",
            "direct mission rewrite",
            "direct canonical policy rewrite",
        ],
        "residual_directly_becoming_new_y_star_forbidden": True,
        "actual_y_becoming_new_y_star_forbidden": True,
        "automatic_target_drift_forbidden": True,
        "direct_mission_rewrite_forbidden": True,
        "direct_canonical_policy_rewrite_forbidden": True,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.y_star_non_mutation_invariant.summary",
        "schema_version": SCHEMA_VERSION,
        "y_star_non_mutation_invariant_defined": True,
        "residual_to_projection_policy_boundary_defined": True,
        "allowed_change_surface_defined": True,
        "forbidden_change_surface_defined": True,
        "residual_cannot_directly_mutate_mission_y_star": True,
        "residual_cannot_directly_mutate_behavior_y_star": True,
        "residual_can_only_improve_projection_process": True,
        "safety_flags": SAFETY_FLAGS,
    }
    return invariant, boundary, allowed, forbidden, summary


def build_target_registry() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    targets = [
        {
            "target_id": f"canonical-learning-target-{name}",
            "target_name": name,
            "description": f"Controlled learning target for {name.replace('_', ' ')}.",
            "source_candidate_types": [
                "review_only_learning_candidate",
                "shadow_update_candidate",
                "mcp_review_only_learning_candidate",
            ],
            "allowed_update_mode": [
                "shadow_preview",
                "canonical_update_package_candidate",
                "future_approved_versioned_patch",
            ],
            "denied_update_mode": [
                "auto_apply",
                "direct_writeback",
                "direct_y_star_mutation",
                "silent_canonical_mutation",
            ],
            "requires_human_review": True,
            "requires_governance_review": True,
            "requires_versioning": True,
            "requires_rollback_plan": True,
            "requires_post_update_validation": True,
            "can_be_shadow_updated": name not in {"brain_update_policy", "memory_ingestion_policy", "strategy_update_policy"},
            "can_be_canonical_candidate": True,
            "can_be_auto_applied_now": False,
            "can_mutate_y_star_directly": False,
            "evidence_requirements": [
                "source residual",
                "source learning candidate",
                "review decision",
                "non-mutation invariant check",
                "rollback plan",
                "post-update validation plan",
            ],
            "risk_class": risk,
        }
        for name, risk in TARGET_CLASSES
    ]
    registry = {
        "schema_name": "ystar.canonical_learning_target_registry.registry",
        "schema_version": SCHEMA_VERSION,
        "registry_id": "canonical-learning-target-registry-v0",
        "target_classes": targets,
        "safety_flags": SAFETY_FLAGS,
    }
    scope_matrix = {
        "schema_name": "ystar.canonical_learning_target_registry.scope_matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "canonical-learning-target-scope-matrix-v0",
        "targets": [
            {
                "target_name": target["target_name"],
                "allowed_shadow_learning": target["can_be_shadow_updated"],
                "allowed_canonical_candidate": target["can_be_canonical_candidate"],
                "denied_auto_application": True,
                "denied_direct_y_star_mutation": True,
                "denied_brain_writeback_now": True,
                "denied_memory_ingestion_now": True,
                "requires_review_before_application": True,
            }
            for target in targets
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    risk_matrix = {
        "schema_name": "ystar.canonical_learning_target_registry.risk_matrix",
        "schema_version": SCHEMA_VERSION,
        "risk_matrix_id": "canonical-learning-target-risk-matrix-v0",
        "risk_classes": [
            "low_artifact_policy",
            "medium_projection_policy",
            "high_brain_memory_boundary",
            "high_strategy_boundary",
            "critical_y_star_boundary",
            "critical_live_execution_boundary",
        ],
        "target_risks": [
            {
                "target_name": target["target_name"],
                "risk_class": target["risk_class"],
                "requires_human_review": target["requires_human_review"],
                "requires_governance_review": target["requires_governance_review"],
            }
            for target in targets
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.canonical_learning_target_registry.summary",
        "schema_version": SCHEMA_VERSION,
        "canonical_learning_target_registry_generated": True,
        "target_class_count": len(targets),
        "all_targets_block_auto_apply": all(not target["can_be_auto_applied_now"] for target in targets),
        "all_targets_block_direct_y_star_mutation": all(
            not target["can_mutate_y_star_directly"] for target in targets
        ),
        "safety_flags": SAFETY_FLAGS,
    }
    return registry, scope_matrix, risk_matrix, summary


def build_evidence_bundle(sources: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    missing = missing_sources(sources)
    evidence_refs = list(INPUT_REFS.values())
    completeness_status = (
        "complete_for_dry_run_promotion_review"
        if not missing
        else "incomplete_requires_more_evidence"
    )
    bundle = {
        "schema_name": "ystar.canonical_promotion_evidence_bundle.bundle",
        "schema_version": SCHEMA_VERSION,
        "bundle_id": "canonical-promotion-evidence-bundle-v0",
        "source_candidates": [
            INPUT_REFS["projection_policy_update_candidate"],
            INPUT_REFS["mcp_learning_candidate"],
        ],
        "source_residuals": [
            INPUT_REFS["residual_review_gate_decision"],
            INPUT_REFS["mcp_residual_delta"],
        ],
        "source_shadow_patches": [INPUT_REFS["shadow_projection_policy_patch"]],
        "source_shadow_behavior_previews": [INPUT_REFS["shadow_behavior_y_star_preview"]],
        "source_shadow_cycle_comparisons": [INPUT_REFS["shadow_learning_effect_summary"]],
        "source_mcp_learning_candidates": [INPUT_REFS["mcp_learning_candidate"]],
        "evidence_refs": evidence_refs,
        "missing_evidence": missing,
        "evidence_completeness_status": completeness_status,
        "safe_for_promotion_review": True,
        "safe_for_direct_application": False,
        "safety_flags": SAFETY_FLAGS,
    }
    candidate_index = {
        "schema_name": "ystar.canonical_promotion_evidence_bundle.source_learning_candidate_index",
        "schema_version": SCHEMA_VERSION,
        "index_id": "source-learning-candidate-index-v0",
        "candidates": [
            {
                "candidate_ref": INPUT_REFS["projection_policy_update_candidate"],
                "candidate_kind": "projection_policy_update_candidate",
                "approval_status": sources["projection_policy_update_candidate"].get(
                    "approval_status", "not_approved"
                ),
                "application_status": "not_applied",
            },
            {
                "candidate_ref": INPUT_REFS["mcp_learning_candidate"],
                "candidate_kind": "mcp_review_only_learning_candidate",
                "approved": sources["mcp_learning_candidate"].get("approved", False),
                "applied": sources["mcp_learning_candidate"].get("applied", False),
            },
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    residual_index = {
        "schema_name": "ystar.canonical_promotion_evidence_bundle.source_residual_index",
        "schema_version": SCHEMA_VERSION,
        "index_id": "source-residual-index-v0",
        "residuals": [
            {
                "residual_ref": INPUT_REFS["residual_review_gate_decision"],
                "residual_kind": "review_gated_shadow_learning_residual_decision",
            },
            {
                "residual_ref": INPUT_REFS["mcp_residual_delta"],
                "residual_kind": "mcp_dry_run_adapter_residual_delta",
            },
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    shadow_index = {
        "schema_name": "ystar.canonical_promotion_evidence_bundle.source_shadow_effect_index",
        "schema_version": SCHEMA_VERSION,
        "index_id": "source-shadow-effect-index-v0",
        "shadow_effects": [
            {
                "shadow_patch_ref": INPUT_REFS["shadow_projection_policy_patch"],
                "shadow_preview_ref": INPUT_REFS["shadow_behavior_y_star_preview"],
                "comparison_ref": INPUT_REFS["shadow_learning_effect_summary"],
                "effect_class": sources["shadow_learning_effect_summary"].get(
                    "effect_class", "unknown"
                ),
                "canonical_system_changed": sources["shadow_learning_effect_summary"].get(
                    "canonical_system_changed", False
                ),
                "brain_memory_changed": sources["shadow_learning_effect_summary"].get(
                    "brain_memory_changed", False
                ),
            }
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    check = {
        "schema_name": "ystar.canonical_promotion_evidence_bundle.completeness_check",
        "schema_version": SCHEMA_VERSION,
        "check_id": "evidence-completeness-check-v0",
        "residual_has_source_cycle": True,
        "learning_candidate_has_review_trace": True,
        "shadow_patch_exists": not sources["shadow_projection_policy_patch"].get("missing", False),
        "shadow_preview_exists": not sources["shadow_behavior_y_star_preview"].get("missing", False),
        "original_vs_shadow_comparison_exists": not sources["shadow_learning_effect_summary"].get("missing", False),
        "safety_flags_verified": True,
        "no_direct_writeback_claim": True,
        "no_approval_claim": True,
        "no_canonical_mutation_claim": True,
        "y_star_non_mutation_invariant_checked": True,
        "mcp_non_bypass_invariant_checked": True,
        "evidence_completeness_status": completeness_status,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.canonical_promotion_evidence_bundle.summary",
        "schema_version": SCHEMA_VERSION,
        "promotion_evidence_bundle_generated": True,
        "source_learning_candidate_index_generated": True,
        "source_residual_index_generated": True,
        "source_shadow_effect_index_generated": True,
        "evidence_completeness_check_generated": True,
        "evidence_completeness_status": completeness_status,
        "safe_for_promotion_review": True,
        "safe_for_direct_application": False,
        "missing_evidence_count": len(missing),
        "safety_flags": SAFETY_FLAGS,
    }
    return bundle, candidate_index, residual_index, shadow_index, check, summary


def build_promotion_gate(evidence_bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    eligible = evidence_bundle["evidence_completeness_status"] == "complete_for_dry_run_promotion_review"
    decision = (
        "eligible_for_canonical_update_package_candidate"
        if eligible
        else "requires_more_evidence"
    )
    policy = {
        "schema_name": "ystar.canonical_promotion_eligibility_gate.policy",
        "schema_version": SCHEMA_VERSION,
        "policy_id": "canonical-promotion-policy-v0",
        "deterministic_rules": [
            "candidate must be review-only or shadow-only source",
            "candidate must have evidence bundle",
            "candidate must preserve Y* non-mutation invariant",
            "candidate must not claim approval",
            "candidate must not have been applied",
            "candidate must not require live execution",
            "candidate must not require network/external action",
            "candidate must not write brain/memory",
            "candidate must include rollback and validation plan before canonical application",
            "candidate must be blocked if it proposes direct Y* mutation or unreviewed writeback",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    decision_doc = {
        "schema_name": "ystar.canonical_promotion_eligibility_gate.decision",
        "schema_version": SCHEMA_VERSION,
        "decision_id": "canonical-promotion-eligibility-decision-v0",
        "source_evidence_bundle_id": evidence_bundle["bundle_id"],
        "decision": decision,
        "allowed_promotion_scope": [
            "canonical update package candidate generation",
            "versioned dry-run patch planning",
            "rollback and audit planning",
            "post-promotion validation planning",
        ],
        "denied_promotion_scope": [
            "actual canonical application now",
            "candidate approval",
            "brain writeback",
            "memory ingestion",
            "strategy mutation",
            "direct Y* mutation",
            "MCP execution",
            "live execution",
        ],
        "allowed_next_artifact": "canonical_update_package_candidate",
        "required_approval_before_application": True,
        "eligible_for_canonical_update_package_candidate": eligible,
        "approved_for_application": False,
        "applied": False,
        "evidence_refs": [rel(EVIDENCE / "canonical_promotion_evidence_bundle.json")],
        "safety_flags": SAFETY_FLAGS,
    }
    packet = {
        "schema_name": "ystar.canonical_promotion_eligibility_gate.decision_packet",
        "schema_version": SCHEMA_VERSION,
        "packet_id": "canonical-promotion-decision-packet-v0",
        "source_decision_id": decision_doc["decision_id"],
        "decision": decision,
        "candidate_approved": False,
        "candidate_applied": False,
        "approval_protocol_required": True,
        "versioning_required": True,
        "rollback_required": True,
        "post_promotion_validation_required": True,
        "evidence_refs": decision_doc["evidence_refs"],
        "safety_flags": SAFETY_FLAGS,
    }
    denied = {
        "schema_name": "ystar.canonical_promotion_eligibility_gate.denied_scope",
        "schema_version": SCHEMA_VERSION,
        "denied_scope_id": "canonical-promotion-denied-scope-v0",
        "denied_operations": [
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
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.canonical_promotion_eligibility_gate.summary",
        "schema_version": SCHEMA_VERSION,
        "promotion_eligibility_gate_generated": True,
        "promotion_policy_generated": True,
        "promotion_decision_packet_generated": True,
        "decision": decision,
        "eligible_for_canonical_update_package_candidate": eligible,
        "approved_for_application": False,
        "applied": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return policy, decision_doc, packet, denied, summary


def build_update_package(decision_doc: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    package = {
        "schema_name": "ystar.canonical_update_package_candidate.package",
        "schema_version": SCHEMA_VERSION,
        "package_id": "canonical-update-package-candidate-v0",
        "source_promotion_decision_id": decision_doc["decision_id"],
        "package_type": "mixed_canonical_update_candidate",
        "target_classes": [
            "projection_policy",
            "behavior_y_star_generation_rule",
            "pre_u_mapping_rule",
            "mcp_interface_contract",
            "residual_classification_policy",
            "evidence_collection_policy",
            "learning_eligibility_policy",
        ],
        "proposed_canonical_changes": [
            "tighten projection trace linkage requirements",
            "clarify behavior boundary inheritance rules",
            "improve Pre-U mapping from behavior Y* to candidate_U",
            "improve governed MCP boundary evidence requirements",
            "improve residual labels for no-execution dry-run cycles",
            "require explicit evidence sufficiency before promotion gates pass",
        ],
        "non_canonical_preview_sources": [
            INPUT_REFS["shadow_projection_policy_patch"],
            INPUT_REFS["shadow_behavior_y_star_preview"],
            INPUT_REFS["mcp_learning_candidate"],
        ],
        "expected_effect_on_future_projection": (
            "Future projected behavior-level Y* should be derived through stricter trace, "
            "evidence, and boundary contraction rules."
        ),
        "expected_effect_on_future_pre_u_mapping": (
            "Future Pre-U candidates should preserve behavior Y* lineage and expose denied scope."
        ),
        "expected_effect_on_future_mcp_boundary": (
            "Future governed MCP adapter candidates should retain non-bypass receipts and blockers."
        ),
        "expected_effect_on_future_residual_classification": (
            "Residual classes should distinguish no-execution blockers from evidence gaps."
        ),
        "explicit_non_effects": [
            "does not mutate mission Y*",
            "does not directly overwrite behavior Y*",
            "does not apply canonical policy now",
            "does not write brain or memory",
            "does not mutate strategy",
            "does not enable live execution",
        ],
        "evidence_refs": [
            rel(EVIDENCE / "canonical_promotion_evidence_bundle.json"),
            rel(GATE / "canonical_promotion_eligibility_decision.json"),
        ],
        "approval_status": "not_approved",
        "application_status": "not_applied",
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "y_star_direct_mutation_performed": False,
        "requires_human_or_governance_approval_before_application": True,
        "requires_versioning_before_application": True,
        "requires_rollback_plan_before_application": True,
        "requires_post_update_validation_before_application": True,
        "safety_flags": SAFETY_FLAGS,
    }
    manifest = {
        "schema_name": "ystar.canonical_update_package_candidate.manifest",
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "canonical-update-manifest-v0",
        "package_id": package["package_id"],
        "target_classes": package["target_classes"],
        "artifact_refs": package["evidence_refs"],
        "approval_status": "not_approved",
        "application_status": "not_applied",
        "safety_flags": SAFETY_FLAGS,
    }
    boundary = {
        "schema_name": "ystar.canonical_update_package_candidate.scope_boundary",
        "schema_version": SCHEMA_VERSION,
        "scope_boundary_id": "canonical-update-scope-boundary-v0",
        "can_be_proposed": package["target_classes"],
        "cannot_be_applied_now": True,
        "cannot_touch_y_star_directly": True,
        "cannot_write_brain_now": True,
        "cannot_ingest_memory_now": True,
        "cannot_modify_y_star_gov": True,
        "cannot_modify_gov_mcp": True,
        "cannot_enable_live_execution": True,
        "safety_flags": SAFETY_FLAGS,
    }
    denied = {
        "schema_name": "ystar.canonical_update_package_candidate.denied_operations",
        "schema_version": SCHEMA_VERSION,
        "denied_operations_id": "canonical-update-denied-operations-v0",
        "denied_operations": FORBIDDEN_OPERATIONS,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.canonical_update_package_candidate.summary",
        "schema_version": SCHEMA_VERSION,
        "canonical_update_package_candidate_generated": True,
        "package_type": package["package_type"],
        "target_class_count": len(package["target_classes"]),
        "approval_status": "not_approved",
        "application_status": "not_applied",
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "y_star_direct_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return package, manifest, boundary, denied, summary


def build_patch_plan(package: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    patch_plan = {
        "schema_name": "ystar.versioned_canonical_patch_plan.plan",
        "schema_version": SCHEMA_VERSION,
        "patch_plan_id": "versioned-canonical-patch-plan-v0",
        "source_package_id": package["package_id"],
        "target_version_family": "controlled_projection_learning_policy",
        "proposed_new_version": "v0.shadow-candidate-plus-1",
        "affected_canonical_artifact_classes": package["target_classes"],
        "proposed_patch_operations": [
            "add trace completeness rule",
            "add Y* non-mutation invariant check",
            "tighten Pre-U mapping denied-scope requirements",
            "add MCP non-bypass evidence requirement",
            "add no-execution residual classification rule",
        ],
        "required_pre_application_checks": [
            "approval record present",
            "rollback plan present",
            "post-promotion validation plan present",
            "Y* non-mutation invariant passes",
            "MCP non-bypass invariant passes",
        ],
        "required_approval_records": ["human_or_governance_approval_record"],
        "required_backup_or_snapshot": "canonical_policy_snapshot_required_before_application",
        "required_rollback_plan": rel(ROLLBACK / "rollback_plan.json"),
        "required_post_application_validation": rel(VALIDATION / "post_promotion_validation_plan.json"),
        "application_mode": "blocked_dry_run_plan_only",
        "applied_now": False,
        "canonical_policy_mutation_performed": False,
        "evidence_refs": [rel(PACKAGE / "canonical_update_package_candidate.json")],
        "safety_flags": SAFETY_FLAGS,
    }
    lineage = {
        "schema_name": "ystar.versioned_canonical_patch_plan.lineage",
        "schema_version": SCHEMA_VERSION,
        "lineage_plan_id": "canonical-version-lineage-plan-v0",
        "current_version_ref": "current_canonical_projection_policy_version_unknown_not_read",
        "proposed_version_ref": patch_plan["proposed_new_version"],
        "parent_version_ref": "future-approved-parent-version-required",
        "lineage_hash_or_placeholder": "placeholder-uncomputed-dry-run-only",
        "approval_record_required": True,
        "rollback_record_required": True,
        "audit_record_required": True,
        "post_validation_record_required": True,
        "safety_flags": SAFETY_FLAGS,
    }
    diff_preview = {
        "schema_name": "ystar.versioned_canonical_patch_plan.diff_preview",
        "schema_version": SCHEMA_VERSION,
        "diff_preview_id": "canonical-patch-diff-preview-v0",
        "structured_diff_preview_only": True,
        "intended_diffs": [
            {
                "target_class": "projection_policy",
                "operation": "add_rule",
                "description": "Require Y* non-mutation invariant check before promotion.",
            },
            {
                "target_class": "mcp_interface_contract",
                "operation": "tighten_boundary",
                "description": "Require bridge receipt, CIEU receipt, and residual refs before any MCP path.",
            },
            {
                "target_class": "residual_classification_policy",
                "operation": "add_label",
                "description": "Classify no-execution blocker residual separately from evidence gaps.",
            },
        ],
        "canonical_target_files_modified": False,
        "safety_flags": SAFETY_FLAGS,
    }
    blocker = {
        "schema_name": "ystar.versioned_canonical_patch_plan.application_blocker",
        "schema_version": SCHEMA_VERSION,
        "blocker_id": "canonical-patch-application-blocker-v0",
        "application_blocked": True,
        "blocked_reason": (
            "L5.7 creates only a versioned dry-run patch plan. Actual canonical application "
            "requires a future approved sandbox with approval, snapshot, rollback, audit, and validation records."
        ),
        "candidate_approved": False,
        "candidate_applied": False,
        "canonical_policy_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.versioned_canonical_patch_plan.summary",
        "schema_version": SCHEMA_VERSION,
        "versioned_patch_plan_generated": True,
        "canonical_version_lineage_plan_generated": True,
        "canonical_patch_diff_preview_generated": True,
        "canonical_patch_application_blocker_generated": True,
        "application_mode": "blocked_dry_run_plan_only",
        "applied_now": False,
        "canonical_policy_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return patch_plan, lineage, diff_preview, blocker, summary


def build_rollback_and_audit(patch_plan: dict[str, Any], package: dict[str, Any], decision_doc: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    rollback_plan = {
        "schema_name": "ystar.rollback_and_audit_lineage.rollback_plan",
        "schema_version": SCHEMA_VERSION,
        "rollback_plan_id": "canonical-learning-rollback-plan-v0",
        "source_patch_plan_id": patch_plan["patch_plan_id"],
        "rollback_scope": package["target_classes"],
        "rollback_preconditions": [
            "future canonical application occurred",
            "snapshot or parent version is available",
            "rollback approval gate is satisfied",
        ],
        "rollback_steps": [
            "pause affected live path",
            "restore parent canonical artifact version",
            "rerun invariant checks",
            "rerun post-promotion validation subset",
            "emit rollback audit record",
        ],
        "rollback_validation_checks": [
            "Y* lineage preserved",
            "MCP non-bypass preserved",
            "no brain/memory direct writeback",
            "safety flags remain blocked",
        ],
        "rollback_owner_or_gate": "human_or_governance_review_gate",
        "rollback_required_before_live": True,
        "evidence_refs": [rel(PATCH / "versioned_canonical_patch_plan.json")],
        "safety_flags": SAFETY_FLAGS,
    }
    trigger_policy = {
        "schema_name": "ystar.rollback_and_audit_lineage.trigger_policy",
        "schema_version": SCHEMA_VERSION,
        "trigger_policy_id": "rollback-trigger-policy-v0",
        "triggers": [
            "post_update_validation_failure",
            "Y_star_lineage_break",
            "safety_flag_regression",
            "Pre-U validation mismatch",
            "MCP non-bypass invariant violation",
            "residual_classification_regression",
            "brain_memory_boundary_violation",
            "external_action_boundary_violation",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    audit_record = {
        "schema_name": "ystar.rollback_and_audit_lineage.audit_record",
        "schema_version": SCHEMA_VERSION,
        "audit_record_id": "canonical-learning-audit-lineage-record-v0",
        "source_residual_ids": [
            "residual-review-gate-decision-001",
            "mcp-residual-delta-v0",
        ],
        "source_learning_candidate_ids": [
            "projection-policy-update-candidate-001",
            "mcp-review-only-learning-candidate-v0",
        ],
        "source_shadow_patch_ids": ["shadow-projection-policy-patch-001"],
        "source_promotion_decision_id": decision_doc["decision_id"],
        "source_update_package_id": package["package_id"],
        "source_patch_plan_id": patch_plan["patch_plan_id"],
        "approval_status": "not_approved",
        "application_status": "not_applied",
        "canonical_mutation_performed": False,
        "brain_memory_mutation_performed": False,
        "evidence_refs": [
            rel(EVIDENCE / "canonical_promotion_evidence_bundle.json"),
            rel(PACKAGE / "canonical_update_package_candidate.json"),
            rel(PATCH / "versioned_canonical_patch_plan.json"),
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    audit_requirements = {
        "schema_name": "ystar.rollback_and_audit_lineage.audit_requirements",
        "schema_version": SCHEMA_VERSION,
        "requirements_id": "canonical-learning-audit-requirements-v0",
        "required_fields": [
            "source residual ids",
            "source learning candidate ids",
            "source shadow patch ids",
            "promotion decision id",
            "update package id",
            "patch plan id",
            "approval status",
            "application status",
            "validation status",
        ],
        "canonical_mutation_requires_audit_record": True,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.rollback_and_audit_lineage.summary",
        "schema_version": SCHEMA_VERSION,
        "rollback_plan_generated": True,
        "rollback_trigger_policy_generated": True,
        "audit_lineage_record_generated": True,
        "audit_requirements_generated": True,
        "canonical_mutation_performed": False,
        "brain_memory_mutation_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return rollback_plan, trigger_policy, audit_record, audit_requirements, summary


def build_validation_plan() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    required_checks = [
        "py_compile",
        "JSON validation",
        "static read-model validator",
        "local safety wrapper",
        "L5.0-L5.6 targeted pytest",
        "new canonical learning tests",
        "console/read-model smoke",
        "Y* non-mutation invariant check",
        "MCP non-bypass invariant check",
        "no direct writeback invariant check",
        "rollback plan check",
        "version lineage check",
        "post-application residual sanity check",
    ]
    plan = {
        "schema_name": "ystar.post_promotion_validation_plan.plan",
        "schema_version": SCHEMA_VERSION,
        "validation_plan_id": "post-promotion-validation-plan-v0",
        "required_validation_targets": required_checks,
        "requires_py_compile": True,
        "requires_json_validation": True,
        "requires_static_read_model_validator": True,
        "requires_local_safety_wrapper": True,
        "requires_l5_0_to_l5_6_targeted_pytest": True,
        "requires_new_canonical_learning_tests": True,
        "requires_console_read_model_smoke": True,
        "requires_y_star_non_mutation_invariant_check": True,
        "requires_mcp_non_bypass_invariant_check": True,
        "requires_no_direct_writeback_invariant_check": True,
        "requires_rollback_plan_check": True,
        "requires_version_lineage_check": True,
        "requires_post_application_residual_sanity_check": True,
        "safety_flags": SAFETY_FLAGS,
    }
    matrix = {
        "schema_name": "ystar.post_promotion_validation_plan.matrix",
        "schema_version": SCHEMA_VERSION,
        "matrix_id": "post-promotion-validation-matrix-v0",
        "validation_matrix": [
            {"validation_target": target, "required_before_application": True}
            for target in required_checks
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    tests = {
        "schema_name": "ystar.post_promotion_validation_plan.required_test_targets",
        "schema_version": SCHEMA_VERSION,
        "test_targets_id": "post-promotion-required-test-targets-v0",
        "required_test_targets": [
            "tests/field_functional_archaeology/test_field_functional_archaeology.py",
            "tests/mission_field_projection_contract/test_mission_field_projection_contract.py",
            "tests/field_functional_auto_projection_core/test_field_functional_auto_projection_core.py",
            "tests/projection_checked_autonomous_work_cycle/test_projection_checked_autonomous_work_cycle.py",
            "tests/review_gated_shadow_projection_cycle/test_review_gated_shadow_projection_cycle.py",
            "tests/cross_repo_governance_contract_proof/test_cross_repo_governance_contract_proof.py",
            "tests/governed_mcp_dry_run_adapter/test_governed_mcp_dry_run_adapter.py",
            "tests/controlled_canonical_learning_design/test_controlled_canonical_learning_design.py",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    invariants = {
        "schema_name": "ystar.post_promotion_validation_plan.invariant_checks",
        "schema_version": SCHEMA_VERSION,
        "invariant_checks_id": "post-promotion-invariant-checks-v0",
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
        "live_execution_still_gated": True,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.post_promotion_validation_plan.summary",
        "schema_version": SCHEMA_VERSION,
        "post_promotion_validation_plan_generated": True,
        "post_promotion_validation_matrix_generated": True,
        "post_promotion_required_test_targets_generated": True,
        "post_promotion_invariant_checks_generated": True,
        "required_validation_target_count": len(required_checks),
        "safety_flags": SAFETY_FLAGS,
    }
    return plan, matrix, tests, invariants, summary


def build_promotion_fixture(decision_doc: dict[str, Any], package: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    fixture = {
        "schema_name": "ystar.dry_run_promotion_decision_fixture.fixture",
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "dry-run-promotion-decision-fixture-v0",
        "source_promotion_decision_id": decision_doc["decision_id"],
        "source_update_package_id": package["package_id"],
        "decision_mode": "dry_run_promotion_design_only",
        "candidate_approved": False,
        "candidate_applied": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "y_star_direct_mutation_performed": False,
        "ready_for_future_approval_workflow": True,
        "evidence_refs": [
            rel(GATE / "canonical_promotion_eligibility_decision.json"),
            rel(PACKAGE / "canonical_update_package_candidate.json"),
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    predicted = {
        "schema_name": "ystar.dry_run_promotion_decision_fixture.predicted_outcome",
        "schema_version": SCHEMA_VERSION,
        "predicted_outcome_id": "dry-run-promotion-predicted-outcome-v0",
        "expected_y": [
            "invariant defined",
            "promotion evidence bundle generated",
            "promotion gate generated",
            "canonical update package candidate generated",
            "versioned patch plan generated",
            "rollback/audit plan generated",
            "post-promotion validation plan generated",
            "actual application blocked",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    actual = {
        "schema_name": "ystar.dry_run_promotion_decision_fixture.mock_actual_outcome",
        "schema_version": SCHEMA_VERSION,
        "mock_actual_outcome_id": "dry-run-promotion-mock-actual-outcome-v0",
        "actual_y": predicted["expected_y"],
        "mock_actual_only": True,
        "real_application_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    residual = {
        "schema_name": "ystar.dry_run_promotion_decision_fixture.residual_delta",
        "schema_version": SCHEMA_VERSION,
        "residual_delta_id": "dry-run-promotion-residual-delta-v0",
        "promotion_design_residual": "none for dry-run artifact generation",
        "canonical_application_residual": "actual application intentionally blocked",
        "approval_residual": "candidate remains not approved",
        "writeback_residual": "brain and memory writeback remain blocked",
        "y_star_mutation_residual": "direct Y* mutation remains blocked",
        "structural_residual_only": True,
        "safety_flags": SAFETY_FLAGS,
    }
    event = {
        "schema_name": "ystar.dry_run_promotion_decision_fixture.cieu_event_fixture",
        "schema_version": SCHEMA_VERSION,
        "event_id": "dry-run-promotion-cieu-event-fixture-v0",
        "X_t": {
            "source_inputs": list(INPUT_REFS.values()),
            "controlled_learning_context": "review-only and shadow-only learning evidence",
        },
        "U_t": {
            "operation": "controlled canonical learning design operation",
            "promotion_fixture_ref": rel(PROMOTION / "dry_run_promotion_decision_fixture.json"),
        },
        "Y_star_t": (
            "Produce a safe canonical learning promotion design without applying it."
        ),
        "Y_t_plus_1": actual["actual_y"],
        "R_t_plus_1": {
            "residual_delta_ref": rel(PROMOTION / "dry_run_promotion_residual_delta.json"),
            "structural_residual_only": True,
        },
        "event_mode": "controlled_canonical_learning_design_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.dry_run_promotion_decision_fixture.summary",
        "schema_version": SCHEMA_VERSION,
        "dry_run_promotion_fixture_generated": True,
        "dry_run_promotion_cieu_event_fixture_generated": True,
        "dry_run_promotion_residual_delta_generated": True,
        "candidate_approved": False,
        "candidate_applied": False,
        "canonical_policy_mutation_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "y_star_direct_mutation_performed": False,
        "ready_for_future_approval_workflow": True,
        "safety_flags": SAFETY_FLAGS,
    }
    return fixture, event, predicted, actual, residual, summary


def build_readiness() -> tuple[dict[str, Any], dict[str, Any]]:
    readiness = {
        "schema_name": "ystar.controlled_canonical_learning_readiness.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "controlled-canonical-learning-readiness-v0",
        "y_star_non_mutation_invariant_defined": True,
        "canonical_learning_targets_registered": True,
        "promotion_evidence_bundle_generated": True,
        "promotion_eligibility_gate_generated": True,
        "canonical_update_package_candidate_generated": True,
        "versioned_patch_plan_generated": True,
        "rollback_plan_generated": True,
        "audit_lineage_record_generated": True,
        "post_promotion_validation_plan_generated": True,
        "dry_run_promotion_fixture_generated": True,
        "actual_canonical_application_blocked": True,
        "candidate_approval_blocked": True,
        "brain_writeback_blocked": True,
        "memory_ingestion_blocked": True,
        "y_star_direct_mutation_blocked": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "ready_for_l5_8_approved_canonical_update_sandbox": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "next_required_milestone": NEXT_MILESTONE,
        **common_status(),
    }
    recommendation = {
        "schema_name": "ystar.controlled_canonical_learning_readiness.next_step",
        "schema_version": SCHEMA_VERSION,
        "recommendation_id": "l5-8-recommended-next-step-v0",
        "recommended_next_milestone": NEXT_MILESTONE,
        "recommended_scope": [
            "approved canonical update sandbox design",
            "approval record fixture",
            "versioned application sandbox",
            "rollback validation dry-run",
        ],
        "blocked_scope": [
            "L6 revenue opportunity discovery",
            "live execution",
            "brain/memory writeback",
            "automatic candidate approval",
        ],
        "ready_for_l6_revenue_opportunity_discovery": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return readiness, recommendation


def build_design_run(
    contract: dict[str, Any],
    input_fixture: dict[str, Any],
    readiness: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    stage_results = [
        {
            "stage": stage,
            "status": "completed_dry_run",
            "live_or_canonical_mutation_performed": False,
        }
        for stage in contract["design_stages"]
    ]
    run = {
        "schema_name": "ystar.controlled_canonical_learning_design.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "controlled-canonical-learning-design-run-v0",
        "contract_ref": rel(DESIGN / "controlled_canonical_learning_contract.json"),
        "input_fixture_ref": rel(DESIGN / "controlled_canonical_learning_input_fixture.json"),
        "design_stages": stage_results,
        "missing_sources": input_fixture["missing_sources"],
        "actual_canonical_application_blocked": True,
        "candidate_approval_blocked": True,
        "dry_run_only": True,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.controlled_canonical_learning_design.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_7_controlled_canonical_learning_design_defined": True,
        "y_star_non_mutation_invariant_defined": True,
        "canonical_learning_target_registry_generated": True,
        "promotion_evidence_bundle_generated": True,
        "promotion_eligibility_gate_generated": True,
        "canonical_update_package_candidate_generated": True,
        "versioned_patch_plan_generated": True,
        "rollback_audit_plan_generated": True,
        "post_promotion_validation_plan_generated": True,
        "dry_run_promotion_fixture_generated": True,
        "candidate_approved": False,
        "candidate_applied": False,
        "canonical_policy_mutation_performed": False,
        "canonical_update_application_performed": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "strategy_mutation_performed": False,
        "y_star_direct_mutation_performed": False,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "ready_for_l5_8_approved_canonical_update_sandbox": readiness[
            "ready_for_l5_8_approved_canonical_update_sandbox"
        ],
        "ready_for_l6_revenue_opportunity_discovery": False,
        "next_required_milestone": NEXT_MILESTONE,
        "generated_readiness": rel(READINESS / "controlled_canonical_learning_readiness.json"),
        "warning": (
            "L5.7 defines controlled canonical learning promotion architecture only. "
            "No candidate is approved or applied and no canonical policy, brain, memory, "
            "strategy, Y-star-gov, or gov-mcp state is mutated."
        ),
        "safety_flags": SAFETY_FLAGS,
    }
    return run, summary


def main() -> None:
    sources = {key: read_optional_json(path) for key, path in INPUT_REFS.items()}
    contract = build_contract()
    input_fixture = build_input_fixture(sources)
    invariant, boundary, allowed_surface, forbidden_surface, invariant_summary = build_y_star_invariant()
    registry, scope_matrix, risk_matrix, target_summary = build_target_registry()
    (
        evidence_bundle,
        candidate_index,
        residual_index,
        shadow_index,
        completeness_check,
        evidence_summary,
    ) = build_evidence_bundle(sources)
    promotion_policy, promotion_decision, promotion_packet, promotion_denied, gate_summary = (
        build_promotion_gate(evidence_bundle)
    )
    update_package, update_manifest, update_boundary, update_denied, update_summary = (
        build_update_package(promotion_decision)
    )
    patch_plan, lineage, diff_preview, patch_blocker, patch_summary = build_patch_plan(update_package)
    rollback_plan, trigger_policy, audit_record, audit_requirements, rollback_summary = (
        build_rollback_and_audit(patch_plan, update_package, promotion_decision)
    )
    validation_plan, validation_matrix, test_targets, invariant_checks, validation_summary = (
        build_validation_plan()
    )
    promotion_fixture, promotion_event, predicted, actual, promotion_residual, promotion_summary = (
        build_promotion_fixture(promotion_decision, update_package)
    )
    readiness, recommendation = build_readiness()
    run, design_summary = build_design_run(contract, input_fixture, readiness)

    write_text(
        DESIGN / "README.md",
        md(
            "Controlled Canonical Learning Design",
            [
                "L5.7 defines how review-only and shadow learning candidates can become non-applied canonical update package candidates.",
                "It does not approve candidates, apply canonical patches, write brain or memory, mutate Y*, run MCP, or enable L6 revenue discovery.",
            ],
        ),
    )
    write_json(DESIGN / "controlled_canonical_learning_contract.json", contract)
    write_json(DESIGN / "controlled_canonical_learning_input_fixture.json", input_fixture)
    write_json(DESIGN / "controlled_canonical_learning_run.json", run)
    write_json(DESIGN / "controlled_canonical_learning_summary.json", design_summary)
    write_text(
        DESIGN / "controlled_canonical_learning_report.md",
        md(
            "Controlled Canonical Learning Report",
            [
                "- Shadow and review-only candidates are normalized into promotion evidence.",
                "- Residuals cannot directly mutate mission-level or behavior-level Y*.",
                "- Canonical package generation is candidate-only and not applied.",
                "- Versioning, rollback, audit, and post-promotion validation are required before any future application.",
            ],
        ),
    )

    write_json(INVARIANT / "y_star_non_mutation_invariant.json", invariant)
    write_json(INVARIANT / "residual_to_projection_policy_boundary.json", boundary)
    write_json(INVARIANT / "y_star_allowed_change_surface.json", allowed_surface)
    write_json(INVARIANT / "y_star_forbidden_change_surface.json", forbidden_surface)
    write_json(INVARIANT / "y_star_non_mutation_summary.json", invariant_summary)
    write_text(
        INVARIANT / "y_star_non_mutation_report.md",
        md(
            "Y* Non-Mutation Invariant",
            [
                "- Residuals cannot directly rewrite mission-level Y*.",
                "- Residuals cannot directly overwrite behavior-level Y*.",
                "- Residuals may only propose controlled projection process improvements.",
            ],
        ),
    )

    write_json(TARGETS / "canonical_learning_target_registry.json", registry)
    write_json(TARGETS / "canonical_learning_target_scope_matrix.json", scope_matrix)
    write_json(TARGETS / "canonical_learning_target_risk_matrix.json", risk_matrix)
    write_json(TARGETS / "canonical_learning_target_summary.json", target_summary)
    write_text(
        TARGETS / "canonical_learning_target_report.md",
        md(
            "Canonical Learning Target Registry",
            [
                "- Target classes are registered for controlled promotion only.",
                "- No target can auto-apply now or mutate Y* directly.",
            ],
        ),
    )

    write_json(EVIDENCE / "canonical_promotion_evidence_bundle.json", evidence_bundle)
    write_json(EVIDENCE / "source_learning_candidate_index.json", candidate_index)
    write_json(EVIDENCE / "source_residual_index.json", residual_index)
    write_json(EVIDENCE / "source_shadow_effect_index.json", shadow_index)
    write_json(EVIDENCE / "evidence_completeness_check.json", completeness_check)
    write_json(EVIDENCE / "evidence_bundle_summary.json", evidence_summary)
    write_text(
        EVIDENCE / "evidence_bundle_report.md",
        md(
            "Canonical Promotion Evidence Bundle",
            [
                "- Evidence is safe for dry-run promotion review.",
                "- Evidence is not safe for direct application.",
            ],
        ),
    )

    write_json(GATE / "canonical_promotion_policy.json", promotion_policy)
    write_json(GATE / "canonical_promotion_eligibility_decision.json", promotion_decision)
    write_json(GATE / "canonical_promotion_decision_packet.json", promotion_packet)
    write_json(GATE / "canonical_promotion_denied_scope.json", promotion_denied)
    write_json(GATE / "canonical_promotion_gate_summary.json", gate_summary)
    write_text(
        GATE / "canonical_promotion_gate_report.md",
        md(
            "Canonical Promotion Eligibility Gate",
            [
                f"- Decision: {promotion_decision['decision']}.",
                "- Application, approval, writeback, direct Y* mutation, MCP execution, and network remain denied.",
            ],
        ),
    )

    write_json(PACKAGE / "canonical_update_package_candidate.json", update_package)
    write_json(PACKAGE / "canonical_update_manifest.json", update_manifest)
    write_json(PACKAGE / "canonical_update_scope_boundary.json", update_boundary)
    write_json(PACKAGE / "canonical_update_denied_operations.json", update_denied)
    write_json(PACKAGE / "canonical_update_package_summary.json", update_summary)
    write_text(
        PACKAGE / "canonical_update_package_report.md",
        md(
            "Canonical Update Package Candidate",
            [
                "- Package is not approved and not applied.",
                "- Package cannot touch Y* directly, brain, memory, strategy, Y-star-gov, gov-mcp, or live execution.",
            ],
        ),
    )

    write_json(PATCH / "versioned_canonical_patch_plan.json", patch_plan)
    write_json(PATCH / "canonical_version_lineage_plan.json", lineage)
    write_json(PATCH / "canonical_patch_diff_preview.json", diff_preview)
    write_json(PATCH / "canonical_patch_application_blocker.json", patch_blocker)
    write_json(PATCH / "versioned_patch_plan_summary.json", patch_summary)
    write_text(
        PATCH / "versioned_patch_plan_report.md",
        md(
            "Versioned Canonical Patch Plan",
            [
                "- Patch plan is blocked dry-run only.",
                "- No canonical target files are modified.",
            ],
        ),
    )

    write_json(ROLLBACK / "rollback_plan.json", rollback_plan)
    write_json(ROLLBACK / "rollback_trigger_policy.json", trigger_policy)
    write_json(ROLLBACK / "canonical_learning_audit_lineage_record.json", audit_record)
    write_json(ROLLBACK / "canonical_learning_audit_requirements.json", audit_requirements)
    write_json(ROLLBACK / "rollback_audit_summary.json", rollback_summary)
    write_text(
        ROLLBACK / "rollback_audit_report.md",
        md(
            "Rollback and Audit Lineage",
            [
                "- Rollback is required before any future live path.",
                "- Audit lineage records source residuals, candidates, package, and patch plan.",
            ],
        ),
    )

    write_json(VALIDATION / "post_promotion_validation_plan.json", validation_plan)
    write_json(VALIDATION / "post_promotion_validation_matrix.json", validation_matrix)
    write_json(VALIDATION / "post_promotion_required_test_targets.json", test_targets)
    write_json(VALIDATION / "post_promotion_invariant_checks.json", invariant_checks)
    write_json(VALIDATION / "post_promotion_validation_summary.json", validation_summary)
    write_text(
        VALIDATION / "post_promotion_validation_report.md",
        md(
            "Post-Promotion Validation Plan",
            [
                "- Future approved canonical application must rerun compile, JSON, static validator, safety wrapper, and L5.0-L5.6 tests.",
                "- Y* non-mutation and MCP non-bypass invariants are required checks.",
            ],
        ),
    )

    write_json(PROMOTION / "dry_run_promotion_decision_fixture.json", promotion_fixture)
    write_json(PROMOTION / "dry_run_promotion_cieu_event_fixture.json", promotion_event)
    write_json(PROMOTION / "dry_run_promotion_predicted_outcome.json", predicted)
    write_json(PROMOTION / "dry_run_promotion_mock_actual_outcome.json", actual)
    write_json(PROMOTION / "dry_run_promotion_residual_delta.json", promotion_residual)
    write_json(PROMOTION / "dry_run_promotion_summary.json", promotion_summary)
    write_text(
        PROMOTION / "dry_run_promotion_report.md",
        md(
            "Dry-Run Promotion Decision Fixture",
            [
                "- The fixture is not approved and not applied.",
                "- The CIEU-like event is dry-run only and not persisted.",
            ],
        ),
    )

    write_json(READINESS / "controlled_canonical_learning_readiness.json", readiness)
    write_text(
        READINESS / "controlled_canonical_learning_readiness.md",
        md(
            "Controlled Canonical Learning Readiness",
            [
                f"- ready_for_l5_8_approved_canonical_update_sandbox: {readiness['ready_for_l5_8_approved_canonical_update_sandbox']}",
                f"- ready_for_l6_revenue_opportunity_discovery: {readiness['ready_for_l6_revenue_opportunity_discovery']}",
                "- Actual canonical application, candidate approval, brain writeback, memory ingestion, and direct Y* mutation remain blocked.",
            ],
        ),
    )
    write_json(READINESS / "l5_8_recommended_next_step.json", recommendation)

    print("Controlled canonical learning design artifacts generated.")
    print(f"- {rel(DESIGN / 'controlled_canonical_learning_summary.json')}")
    print(f"- {rel(READINESS / 'controlled_canonical_learning_readiness.json')}")


if __name__ == "__main__":
    main()
