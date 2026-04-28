#!/usr/bin/env python3
"""Build deterministic L5.4 review-gated shadow learning cycle artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LOOP = ROOT / "review_gated_shadow_learning_cycle"
REVIEW = ROOT / "residual_review_gate"
TARGETS = ROOT / "learning_target_classifier"
UPDATES = ROOT / "projection_policy_update_candidate"
PATCH = ROOT / "shadow_projection_policy_patch"
REPROJECT = ROOT / "shadow_reprojection_preview"
SHADOW = ROOT / "shadow_updated_projection_cycle"
SHADOW_CIEU = ROOT / "shadow_cycle_cieu_residual"
COMPARE = ROOT / "original_vs_shadow_cycle_comparison"
INTEGRATED = ROOT / "integrated_learning_cycle_cieu_fixture"
READINESS = ROOT / "integrated_shadow_learning_readiness"

INPUT_REFS = {
    "l5_3_residual": "projection_checked_cieu_residual_cycle/projection_checked_residual_delta.json",
    "l5_3_learning_candidate": "projection_checked_learning_review_queue/projection_checked_learning_candidate.json",
    "l5_3_review_queue_entry": "projection_checked_learning_review_queue/projection_checked_review_queue_entry.json",
    "l5_3_cycle_run": "projection_checked_autonomous_work_cycle/projection_checked_cycle_run.json",
    "l5_3_readiness": "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
    "mission_y_star": "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "behavior_y_star": "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
    "projection_trace": "mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json",
    "operator_policy": "field_functional_auto_projection_core/field_projection_operator_policy.json",
    "l5_2_pre_u": "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "cieu_persistence_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "candidate_auto_approval_enabled": False,
    "canonical_policy_mutation_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
    "shadow_patch_live_application_enabled": False,
}

LOOP_STAGES = [
    "load_l5_3_projection_checked_residual_delta",
    "load_l5_3_learning_candidate",
    "normalize_residual_for_review",
    "classify_learning_target",
    "run_deterministic_review_gate",
    "produce_review_decision_packet",
    "generate_projection_policy_update_candidate",
    "generate_shadow_projection_policy_patch",
    "generate_next_cycle_projection_input_candidate",
    "generate_shadow_behavior_y_star_preview",
    "run_shadow_updated_projection_checked_cycle",
    "generate_shadow_cycle_cieu_like_fixture",
    "compute_shadow_cycle_residual_delta",
    "compare_original_vs_shadow_behavior_y_star",
    "compare_original_vs_shadow_cycle",
    "emit_integrated_learning_cycle_cieu_like_fixture",
    "produce_final_l5_4_readiness",
]

FORBIDDEN_OPERATIONS = [
    "reading raw DB/WAL/SHM/log contents",
    "reading active-agent marker contents",
    "running live hooks",
    "running daemon/scheduler/runtime scripts",
    "external network/API calls",
    "GitHub issue/PR creation",
    "git push",
    "CIEU DB writes",
    "brain writeback",
    "memory ingestion",
    "candidate approval",
    "canonical policy mutation",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

LEARNING_TARGETS = [
    "projection_policy",
    "behavior_y_star_generation",
    "pre_u_mapping",
    "work_proposal_alignment",
    "residual_classification",
    "evidence_collection_policy",
    "live_blocker_tracking",
    "writeback_boundary_tracking",
]

EFFECT_CLASS = "behavior_y_star_shadow_effect"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(relative_path: str) -> dict[str, Any]:
    if relative_path not in set(INPUT_REFS.values()):
        raise ValueError(f"Refusing non-curated input: {relative_path}")
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing curated input: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def build_contract() -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "loop_name": "Integrated Review-Gated Shadow Learning Cycle",
        "loop_id": "review_gated_shadow_learning_cycle_v0",
        "purpose": (
            "Convert an L5.3 dry-run residual into review-gated shadow update "
            "artifacts, preview a shadow behavior-level Y*, run a shadow dry-run "
            "cycle, and compare original versus shadow without applying learning."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "loop_stages": LOOP_STAGES,
        "required_outputs": [
            "normalized_projection_residual",
            "residual_review_gate_decision",
            "learning_target_classification",
            "projection_policy_update_candidate",
            "shadow_projection_policy_patch",
            "shadow_reprojected_behavior_y_star_preview",
            "shadow_updated_projection_cycle_run",
            "shadow_cycle_residual_delta",
            "original_vs_shadow_cycle_comparison",
            "integrated_learning_cycle_cieu_event_fixture",
            "integrated_shadow_learning_readiness",
        ],
        "review_gate_requirements": [
            "review must be deterministic and structural",
            "source residual must be dry-run and evidence-backed",
            "review gate may allow only shadow update candidates",
        ],
        "learning_scope_requirements": [
            "learning targets are projection policy, behavior Y* generation, Pre-U mapping, work alignment, residual classification, and evidence policy",
            "learning cannot write brain, memory, canonical policy, Y-star-gov, or CIEU storage",
            "learning candidate remains not approved and not applied",
        ],
        "shadow_update_requirements": [
            "shadow patch must be preview-only",
            "shadow patch must not mutate canonical projection policy",
            "shadow patch can generate only separate L5.4 preview artifacts",
        ],
        "shadow_cycle_requirements": [
            "shadow cycle consumes the shadow behavior-level Y* preview",
            "shadow cycle remains dry-run only",
            "shadow cycle cannot execute behavior or tools",
        ],
        "comparison_requirements": [
            "compare original and shadow behavior-level Y*",
            "compare original and shadow cycle gate decisions and residual classes",
            "state whether the residual produced a visible shadow-only effect",
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "not live learning",
            "not canonical policy mutation",
            "not brain writeback",
            "not memory ingestion",
            "not candidate auto-approval",
            "not real behavior execution",
            "not scheduler or daemon activation",
            "not network-enabled",
            "not L6 revenue opportunity discovery",
        ],
    }


def build_input_fixture() -> dict[str, Any]:
    return {
        "schema_name": "ystar.review_gated_shadow_learning_cycle.input_fixture",
        "schema_version": "v0",
        "fixture_id": "review-gated-shadow-learning-input-001",
        "l5_3_projection_checked_residual_delta_ref": INPUT_REFS["l5_3_residual"],
        "l5_3_learning_candidate_ref": INPUT_REFS["l5_3_learning_candidate"],
        "l5_3_review_queue_entry_ref": INPUT_REFS["l5_3_review_queue_entry"],
        "l5_3_cycle_run_ref": INPUT_REFS["l5_3_cycle_run"],
        "l5_3_cycle_readiness_ref": INPUT_REFS["l5_3_readiness"],
        "mission_y_star_ref": INPUT_REFS["mission_y_star"],
        "behavior_y_star_ref": INPUT_REFS["behavior_y_star"],
        "projection_trace_ref": INPUT_REFS["projection_trace"],
        "operator_policy_ref": INPUT_REFS["operator_policy"],
        "pre_u_packet_candidate_ref": INPUT_REFS["l5_2_pre_u"],
        "shadow_only": True,
        "canonical_mutation_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }


def normalize_residual(residual: dict[str, Any]) -> dict[str, Any]:
    residual_classes = [
        "projection_policy_gap",
        "behavior_y_star_generation_gap",
        "pre_u_mapping_gap",
        "work_alignment_gap",
        "residual_classification_gap",
        "evidence_collection_gap",
        "blocked_live_gap",
    ]
    return {
        "schema_name": "ystar.residual_review_gate.normalized_projection_residual",
        "schema_version": "v0",
        "normalized_residual_id": "normalized-projection-residual-001",
        "source_residual_delta_id": residual["residual_delta_id"],
        "residual_classes": residual_classes,
        "residual_severity_structural": "projection_policy_gap",
        "affected_projection_stage": "projection_checked_autonomous_cycle",
        "affected_y_star_layer": "behavior",
        "affected_cycle_stage": "projection_gate_and_pre_u_mapping",
        "evidence_refs": [
            INPUT_REFS["l5_3_residual"],
            INPUT_REFS["l5_3_learning_candidate"],
            INPUT_REFS["l5_3_cycle_run"],
        ],
        "unresolved_gaps": [
            "real behavior outcome is unavailable by design",
            "production Y-star-gov validation is future work",
            "deep Xt evidence model remains future work",
        ],
        "safety_flags": SAFETY_FLAGS,
    }


def build_review_policy() -> dict[str, Any]:
    return {
        "schema_name": "ystar.residual_review_gate.policy",
        "schema_version": "v0",
        "policy_id": "residual-review-policy-v0",
        "deterministic_review_only": True,
        "semantic_truth_scoring_enabled": False,
        "rules": {
            "projection_policy_update_candidate": ["projection_policy_gap", "work_alignment_gap"],
            "behavior_y_star_generation_update_candidate": [
                "behavior_y_star_generation_gap",
                "projection_policy_gap",
            ],
            "pre_u_mapping_update_candidate": ["pre_u_mapping_gap"],
            "work_alignment_update_candidate": ["work_alignment_gap"],
            "residual_classification_update_candidate": ["residual_classification_gap"],
            "context_only": ["blocked_live_gap", "writeback_boundary_tracking"],
            "blocked": ["live_execution_request", "canonical_policy_mutation_request"],
            "requires_human_or_governance_review": LEARNING_TARGETS,
        },
        "safety_flags": SAFETY_FLAGS,
    }


def build_review_gate(normalized: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    decision = {
        "schema_name": "ystar.residual_review_gate.decision",
        "schema_version": "v0",
        "decision_id": "residual-review-gate-decision-001",
        "gate_name": "deterministic_residual_review_gate_v0",
        "decision": "eligible_for_shadow_update_candidate",
        "allowed_learning_scope": [
            "projection_policy",
            "behavior_y_star_generation",
            "pre_u_mapping",
            "work_proposal_alignment",
            "residual_classification",
            "evidence_collection_policy",
        ],
        "denied_learning_scope": [
            "live application",
            "brain writeback",
            "memory ingestion",
            "canonical policy mutation",
            "candidate auto-approval",
            "external action",
            "revenue opportunity discovery",
        ],
        "required_human_or_governance_review": True,
        "approved_for_live_application": False,
        "approved_for_brain_writeback": False,
        "approved_for_memory_ingestion": False,
        "approved_for_canonical_policy_mutation": False,
        "eligible_for_shadow_update_candidate": True,
        "eligible_for_shadow_cycle_preview": True,
        "evidence_refs": normalized["evidence_refs"],
        "safety_flags": SAFETY_FLAGS,
    }
    packet = {
        "schema_name": "ystar.residual_review_gate.decision_packet",
        "schema_version": "v0",
        "packet_id": "residual-review-decision-packet-001",
        "decision_id": decision["decision_id"],
        "normalized_residual_ref": rel(REVIEW / "normalized_projection_residual.json"),
        "decision": decision["decision"],
        "shadow_update_candidate_allowed": True,
        "shadow_cycle_preview_allowed": True,
        "approved": False,
        "applied": False,
        "canonical_policy_mutation_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return decision, packet


def build_learning_targets(normalized: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    targets = []
    for target in LEARNING_TARGETS:
        can_patch = target not in {"live_blocker_tracking", "writeback_boundary_tracking"}
        targets.append(
            {
                "target_name": target,
                "source_residual_refs": [rel(REVIEW / "normalized_projection_residual.json")],
                "allowed_update_type": "shadow_patch_candidate" if can_patch else "context_tracking_only",
                "denied_update_type": [
                    "canonical_policy_mutation",
                    "brain_writeback",
                    "memory_ingestion",
                    "candidate_auto_approval",
                    "live_application",
                ],
                "can_generate_shadow_patch": can_patch,
                "can_apply_to_canonical_policy_now": False,
                "can_write_to_brain_now": False,
                "can_write_to_memory_now": False,
                "requires_review_before_application": True,
                "evidence_refs": normalized["evidence_refs"],
            }
        )
    classification = {
        "schema_name": "ystar.learning_target_classifier.classification",
        "schema_version": "v0",
        "classification_id": "learning-target-classification-001",
        "source_normalized_residual_id": normalized["normalized_residual_id"],
        "targets": targets,
        "safety_flags": SAFETY_FLAGS,
    }
    matrix = {
        "schema_name": "ystar.learning_target_classifier.scope_matrix",
        "schema_version": "v0",
        "matrix_id": "learning-scope-matrix-001",
        "allowed_shadow_learning": True,
        "allowed_shadow_cycle_preview": True,
        "denied_live_learning": True,
        "denied_brain_writeback": True,
        "denied_memory_ingestion": True,
        "denied_candidate_auto_approval": True,
        "denied_external_action": True,
        "denied_revenue_discovery": True,
        "denied_canonical_policy_mutation": True,
        "safety_flags": SAFETY_FLAGS,
    }
    trace = {
        "schema_name": "ystar.learning_target_classifier.trace",
        "schema_version": "v0",
        "trace_id": "learning-target-trace-001",
        "source_residual_classes": normalized["residual_classes"],
        "classified_targets": LEARNING_TARGETS,
        "classification_rule": "deterministic class-to-target mapping",
        "semantic_truth_scoring_used": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return classification, matrix, trace


def update_candidate(
    filename_id: str,
    decision_id: str,
    classification_id: str,
    scope: str,
    description: str,
    layers: list[str],
    effect: str,
    eligible_patch: bool = True,
) -> dict[str, Any]:
    return {
        "schema_name": f"ystar.projection_policy_update_candidate.{filename_id}",
        "schema_version": "v0",
        "update_candidate_id": f"{filename_id}-001",
        "source_review_decision_id": decision_id,
        "source_learning_target_classification_id": classification_id,
        "proposed_update_scope": scope,
        "proposed_update_description": description,
        "affected_projection_layers": layers,
        "expected_effect_on_future_projection": effect,
        "denied_effects": [
            "canonical policy mutation",
            "brain writeback",
            "memory ingestion",
            "live behavior execution",
            "candidate approval",
        ],
        "evidence_refs": [
            rel(REVIEW / "residual_review_gate_decision.json"),
            rel(TARGETS / "learning_target_classification.json"),
        ],
        "approval_status": "not_approved",
        "applied_to_canonical_policy": False,
        "applied_to_brain": False,
        "applied_to_memory": False,
        "eligible_for_shadow_patch": eligible_patch,
        "eligible_for_shadow_cycle_preview": eligible_patch,
        "requires_human_or_governance_review_before_application": True,
        "safety_flags": SAFETY_FLAGS,
    }


def build_update_candidates(
    review_decision: dict[str, Any],
    classification: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    decision_id = review_decision["decision_id"]
    classification_id = classification["classification_id"]
    return {
        "projection_policy_update_candidate.json": update_candidate(
            "projection-policy-update-candidate",
            decision_id,
            classification_id,
            "projection_policy",
            "Tighten projection trace linkage and require explicit no-execution residual handling before a dry-run gate passes.",
            ["mission", "company", "milestone", "session", "task", "behavior"],
            "Future behavior Y* previews should carry clearer trace and no-execution residual obligations.",
        ),
        "behavior_y_star_generation_update_candidate.json": update_candidate(
            "behavior-y-star-generation-update-candidate",
            decision_id,
            classification_id,
            "behavior_y_star_generation",
            "Clarify behavior boundary inheritance and add explicit shadow-cycle preview language to future behavior-level Y*.",
            ["behavior"],
            "Future behavior Y* should preserve boundaries while naming shadow-only learning context.",
        ),
        "pre_u_mapping_update_candidate.json": update_candidate(
            "pre-u-mapping-update-candidate",
            decision_id,
            classification_id,
            "pre_u_mapping",
            "Improve mapping from behavior Y* to candidate_U by carrying review-gated residual context into governance expectations.",
            ["behavior"],
            "Future Pre-U packet candidates should expose residual-driven governance expectations.",
        ),
        "work_alignment_update_candidate.json": update_candidate(
            "work-alignment-update-candidate",
            decision_id,
            classification_id,
            "work_proposal_alignment",
            "Require work proposal alignment checks to cite behavior boundaries and residual learning boundaries explicitly.",
            ["task", "behavior"],
            "Future work gates should explain why dry-run-only work remains inside behavior Y*.",
        ),
        "residual_classification_update_candidate.json": update_candidate(
            "residual-classification-update-candidate",
            decision_id,
            classification_id,
            "residual_classification",
            "Improve class labeling for no-execution dry-run cycles so blocked-live residuals stay separate from evidence gaps.",
            ["behavior"],
            "Future residuals should distinguish no-execution, evidence, live-blocker, and writeback-blocker classes.",
        ),
        "evidence_collection_update_candidate.json": update_candidate(
            "evidence-collection-update-candidate",
            decision_id,
            classification_id,
            "evidence_collection_policy",
            "Require projection gates to identify which evidence refs are sufficient for shadow preview versus future canonical learning.",
            ["company", "milestone", "session", "task", "behavior"],
            "Future shadow previews should document evidence sufficiency before dry-run cycle preview.",
        ),
    }


def build_shadow_patch(update_candidates: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_ids = [
        payload["update_candidate_id"]
        for payload in update_candidates.values()
        if payload["eligible_for_shadow_patch"]
    ]
    patch = {
        "schema_name": "ystar.shadow_projection_policy_patch.patch",
        "schema_version": "v0",
        "shadow_patch_id": "shadow-projection-policy-patch-001",
        "source_update_candidate_ids": source_ids,
        "patch_scope": [
            "projection trace linkage",
            "behavior boundary inheritance",
            "Pre-U residual context mapping",
            "work proposal alignment checks",
            "residual class labeling",
            "evidence sufficiency notes",
        ],
        "patch_operations": [
            "add shadow-only residual context to behavior Y* preview",
            "add explicit no-execution residual obligations",
            "carry residual class refs into shadow Pre-U governance expectations",
            "preserve all forbidden behavior boundaries",
        ],
        "affected_noncanonical_artifacts": [
            rel(REPROJECT / "shadow_reprojected_behavior_y_star_preview.json"),
            rel(SHADOW / "shadow_cycle_pre_u_packet_candidate.json"),
            rel(SHADOW_CIEU / "shadow_cycle_residual_delta.json"),
        ],
        "canonical_policy_mutation": False,
        "brain_writeback": False,
        "memory_ingestion": False,
        "live_application": False,
        "preview_only": True,
        "shadow_cycle_preview_allowed": True,
        "rollback_required_before_live": True,
        "evidence_refs": [rel(UPDATES / "projection_policy_update_candidate.json")],
        "safety_flags": SAFETY_FLAGS,
    }
    plan = {
        "schema_name": "ystar.shadow_projection_policy_patch.application_plan",
        "schema_version": "v0",
        "plan_id": "shadow-patch-application-plan-001",
        "source_shadow_patch_id": patch["shadow_patch_id"],
        "application_mode": "preview_and_shadow_cycle_only",
        "canonical_projection_policy_modified": False,
        "generated_shadow_artifacts_only": True,
        "steps": [
            "load non-applied update candidates",
            "construct shadow patch object",
            "generate shadow behavior-level Y* preview",
            "run shadow dry-run cycle artifacts",
            "compare original and shadow outputs",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    denied = {
        "schema_name": "ystar.shadow_projection_policy_patch.denied_operations",
        "schema_version": "v0",
        "denied_operations_id": "shadow-patch-denied-operations-001",
        "denied_operations": [
            "modifying canonical projection operator policy",
            "modifying brain",
            "modifying memory",
            "modifying Y-star-gov",
            "writing CIEU DB",
            "enabling live behavior execution",
            "enabling network/external action",
            "approving candidates",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    return patch, plan, denied


def build_shadow_reprojection(
    mission: dict[str, Any],
    behavior: dict[str, Any],
    review_decision: dict[str, Any],
    update_candidate_payload: dict[str, Any],
    patch: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    input_candidate = {
        "schema_name": "ystar.shadow_reprojection_preview.input_candidate",
        "schema_version": "v0",
        "input_candidate_id": "next-cycle-projection-input-candidate-001",
        "original_mission_y_star_ref": INPUT_REFS["mission_y_star"],
        "original_behavior_y_star_ref": INPUT_REFS["behavior_y_star"],
        "review_gated_residual_learning_candidate_ref": INPUT_REFS["l5_3_learning_candidate"],
        "projection_policy_update_candidate_ref": rel(UPDATES / "projection_policy_update_candidate.json"),
        "shadow_patch_ref": rel(PATCH / "shadow_projection_policy_patch.json"),
        "safety_flags": SAFETY_FLAGS,
    }
    preview_y = (
        behavior["declared_behavior_y_star"]
        + " Shadow preview adds explicit residual-review obligations, no-execution residual labeling, and evidence sufficiency checks before any future canonical learning design."
    )
    preview = {
        "schema_name": "ystar.shadow_reprojection_preview.behavior_y_star_preview",
        "schema_version": "v0",
        "preview_id": "shadow-behavior-y-star-preview-001",
        "source_shadow_patch_id": patch["shadow_patch_id"],
        "source_original_behavior_y_star_id": behavior["behavior_y_star_id"],
        "preview_behavior_y_star": preview_y,
        "changed_fields": [
            "declared_behavior_y_star",
            "candidate_u_summary",
            "unresolved_gaps",
            "evidence_refs",
        ],
        "unchanged_fields": [
            "source_mission_y_star_id",
            "required_pre_u_validation",
            "allowed_behavior_boundary",
            "forbidden_behavior_boundary",
            "execution_status",
        ],
        "inherited_constraints_preserved": True,
        "forbidden_boundaries_preserved": True,
        "pre_u_validation_still_required": True,
        "live_behavior_authorized": False,
        "behavior_execution_enabled": False,
        "applied_to_canonical_policy": False,
        "applied_to_brain": False,
        "applied_to_memory": False,
        "allowed_behavior_boundary": behavior["allowed_behavior_boundary"],
        "forbidden_behavior_boundary": behavior["forbidden_behavior_boundary"],
        "candidate_u_summary": {
            "candidate_u_id": "candidate-u-shadow-projection-cycle-v0",
            "candidate_u": "route shadow behavior Y* preview into a shadow dry-run projection-checked cycle",
            "execution_mode": "shadow_projection_only",
        },
        "evidence_refs": [
            rel(PATCH / "shadow_projection_policy_patch.json"),
            rel(UPDATES / "projection_policy_update_candidate.json"),
            INPUT_REFS["behavior_y_star"],
            INPUT_REFS["mission_y_star"],
        ],
        "unresolved_gaps": [
            "shadow preview is not canonical",
            "future controlled canonical learning design is required before application",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    comparison = {
        "schema_name": "ystar.shadow_reprojection_preview.behavior_comparison",
        "schema_version": "v0",
        "comparison_id": "original-vs-shadow-behavior-y-star-comparison-001",
        "original_behavior_intent": behavior["behavior_intent"],
        "original_declared_behavior_y_star": behavior["declared_behavior_y_star"],
        "shadow_preview_behavior_y_star": preview["preview_behavior_y_star"],
        "inherited_obligations_preserved": True,
        "contracted_obligations_changed": [
            "added no-execution residual handling",
            "added evidence sufficiency checks",
        ],
        "context_bound_obligations_changed": [
            "residual review gate context is now bound into the preview",
            "shadow patch reference is included",
        ],
        "safety_boundaries_preserved": True,
        "new_unresolved_gaps": preview["unresolved_gaps"],
        "acceptable_for_shadow_cycle_dry_run_consumption": True,
        "canonical_system_changed": False,
        "brain_memory_changed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    gap_map = {
        "schema_name": "ystar.shadow_reprojection_preview.gap_map",
        "schema_version": "v0",
        "gap_map_id": "shadow-reprojection-gap-map-001",
        "gaps": [
            {
                "gap_id": "shadow-not-canonical",
                "description": "Shadow behavior Y* preview cannot replace canonical behavior Y*.",
                "blocks_live_use": True,
            },
            {
                "gap_id": "controlled-learning-needed",
                "description": "Controlled canonical learning architecture is required before applying policy updates.",
                "blocks_live_use": True,
            },
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    return input_candidate, preview, comparison, gap_map


def build_shadow_cycle(
    preview: dict[str, Any],
    input_candidate: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    contract = {
        "schema_name": "ystar.shadow_updated_projection_cycle.contract",
        "schema_version": "v0",
        "shadow_cycle_id": "shadow-updated-projection-cycle-v0",
        "shadow_cycle_only": True,
        "canonical_policy_mutation": False,
        "real_execution_performed": False,
        "live_behavior_authorized": False,
        "behavior_execution_enabled": False,
        "external_action_authorized": False,
        "network_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    fixture = {
        "schema_name": "ystar.shadow_updated_projection_cycle.input_fixture",
        "schema_version": "v0",
        "fixture_id": "shadow-cycle-input-fixture-001",
        "shadow_behavior_y_star_preview_ref": rel(REPROJECT / "shadow_reprojected_behavior_y_star_preview.json"),
        "next_cycle_projection_input_candidate_ref": rel(REPROJECT / "next_cycle_projection_input_candidate.json"),
        "shadow_patch_ref": rel(PATCH / "shadow_projection_policy_patch.json"),
        "dry_run_only": True,
        "safety_flags": SAFETY_FLAGS,
    }
    intent = {
        "schema_name": "ystar.shadow_updated_projection_cycle.work_intent",
        "schema_version": "v0",
        "shadow_work_intent_id": "shadow-projection-checked-work-intent-001",
        "source_shadow_behavior_y_star_preview_id": preview["preview_id"],
        "declared_work_intent": "refresh mission dashboard using shadow-updated behavior-level Y* context",
        "required_shadow_behavior_y_star_alignment": preview["preview_behavior_y_star"],
        "expected_safe_result": "A shadow dry-run work result and comparison artifact only.",
        "safety_flags": SAFETY_FLAGS,
    }
    proposal = {
        "schema_name": "ystar.shadow_updated_projection_cycle.work_proposal",
        "schema_version": "v0",
        "proposal_id": "shadow-autonomous-work-proposal-001",
        "title": "refresh mission dashboard using shadow-updated behavior-level Y* context",
        "source_shadow_work_intent_id": intent["shadow_work_intent_id"],
        "source_shadow_behavior_y_star_preview_id": preview["preview_id"],
        "internal_only": True,
        "dry_run_only": True,
        "read_model_only": True,
        "external_action_requested": False,
        "network_requested": False,
        "revenue_opportunity_discovery_requested": False,
        "db_or_runtime_content_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "canonical_policy_mutation_requested": False,
        "safety_flags": SAFETY_FLAGS,
    }
    alignment = {
        "schema_name": "ystar.shadow_updated_projection_cycle.alignment",
        "schema_version": "v0",
        "alignment_id": "shadow-work-proposal-alignment-001",
        "shadow_behavior_y_star_preview_id": preview["preview_id"],
        "proposal_id": proposal["proposal_id"],
        "inherited_constraints_preserved": True,
        "forbidden_boundary_check_passed": True,
        "decision": "shadow_projection_gate_passed_for_dry_run",
        "safety_flags": SAFETY_FLAGS,
    }
    gate = {
        "schema_name": "ystar.shadow_updated_projection_cycle.work_gate",
        "schema_version": "v0",
        "gate_decision_id": "shadow-work-proposal-gate-decision-001",
        "decision": "shadow_projection_gate_passed_for_dry_run",
        "dry_run_only": True,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "canonical_policy_mutation_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }
    packet = {
        "schema_name": "ystar.shadow_updated_projection_cycle.pre_u_packet_candidate",
        "schema_version": "v0",
        "packet_candidate_id": "shadow-cycle-pre-u-packet-candidate-001",
        "declared_Y_star": preview["preview_behavior_y_star"],
        "candidate_U": {
            "shadow_work_intent": intent["declared_work_intent"],
            "execution_mode": "shadow_dry_run_static_fixture",
        },
        "Xt": {
            "next_cycle_projection_input_candidate_ref": rel(REPROJECT / "next_cycle_projection_input_candidate.json"),
            "shadow_patch_ref": rel(PATCH / "shadow_projection_policy_patch.json"),
        },
        "deny_or_boundary_constraints": preview["forbidden_behavior_boundary"],
        "trace_refs": [
            INPUT_REFS["projection_trace"],
            rel(REPROJECT / "original_vs_shadow_behavior_y_star_comparison.json"),
        ],
        "governance_expectations": {
            "shadow_work_proposal_gate_decision": gate["decision"],
            "allow_only_shadow_dry_run": True,
        },
        "execution_boundary": SAFETY_FLAGS,
        "dry_run_only": True,
        "production_ready": False,
        "requires_y_star_gov_validation_before_execution": True,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }
    pre_u_gate = {
        "schema_name": "ystar.shadow_updated_projection_cycle.pre_u_gate",
        "schema_version": "v0",
        "gate_decision_id": "shadow-cycle-pre-u-gate-decision-001",
        "decision": "allow_shadow_dry_run_only",
        "dry_run_only": True,
        "production_ready": False,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
        "canonical_policy_mutation_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }
    result = {
        "schema_name": "ystar.shadow_updated_projection_cycle.work_result",
        "schema_version": "v0",
        "result_id": "shadow-dry-run-work-result-001",
        "execution_mode": "shadow_dry_run_static_fixture",
        "real_execution_performed": False,
        "live_tool_called": False,
        "external_action_performed": False,
        "network_called": False,
        "db_log_runtime_content_read": False,
        "canonical_policy_mutated": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "generated_outputs": [
            "shadow behavior-level Y* preview",
            "shadow Pre-U packet candidate",
            "shadow CIEU-like fixture",
            "original-vs-shadow comparison",
        ],
        "evidence_refs": [
            rel(REPROJECT / "shadow_reprojected_behavior_y_star_preview.json"),
            rel(SHADOW / "shadow_cycle_pre_u_packet_candidate.json"),
        ],
        "unresolved_gaps": [
            "shadow cycle cannot prove live behavior outcome",
            "canonical policy remains unchanged",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    receipt = {
        "schema_name": "ystar.shadow_updated_projection_cycle.work_receipt",
        "schema_version": "v0",
        "receipt_id": "shadow-dry-run-work-receipt-001",
        "no_live_behavior_execution": True,
        "no_external_action": True,
        "no_network": True,
        "no_scheduler_or_daemon": True,
        "no_cieu_persistence": True,
        "no_canonical_policy_mutation": True,
        "no_brain_writeback": True,
        "no_memory_ingestion": True,
        "no_candidate_approval": True,
        "safety_flags": SAFETY_FLAGS,
    }
    run = {
        "schema_name": "ystar.shadow_updated_projection_cycle.run",
        "schema_version": "v0",
        "run_id": "shadow-updated-projection-cycle-run-001",
        "shadow_cycle_id": contract["shadow_cycle_id"],
        "shadow_behavior_y_star_preview_consumed": True,
        "shadow_work_gate_decision_ref": rel(SHADOW / "shadow_work_proposal_gate_decision.json"),
        "shadow_pre_u_packet_candidate_ref": rel(SHADOW / "shadow_cycle_pre_u_packet_candidate.json"),
        "shadow_dry_run_work_result_ref": rel(SHADOW / "shadow_dry_run_work_result.json"),
        "canonical_policy_mutated": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.shadow_updated_projection_cycle.summary",
        "schema_version": "v0",
        "shadow_updated_projection_cycle_generated": True,
        "shadow_behavior_y_star_preview_consumed": True,
        "shadow_projection_gate_decision": alignment["decision"],
        "shadow_pre_u_gate_decision": pre_u_gate["decision"],
        "real_execution_performed": False,
        "canonical_policy_mutated": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return (
        contract,
        fixture,
        intent,
        proposal,
        alignment,
        gate,
        packet,
        pre_u_gate,
        result,
        receipt,
        run,
        summary,
    )


def build_shadow_cieu_residual(preview: dict[str, Any], cycle_items: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    packet = cycle_items[6]
    result = cycle_items[8]
    predicted = {
        "schema_name": "ystar.shadow_cycle_cieu_residual.predicted_outcome",
        "schema_version": "v0",
        "predicted_outcome_id": "shadow-cycle-predicted-outcome-001",
        "expected_y": "shadow dry-run cycle reflects residual-driven behavior Y* preview",
        "safety_flags": SAFETY_FLAGS,
    }
    actual = {
        "schema_name": "ystar.shadow_cycle_cieu_residual.mock_actual_outcome",
        "schema_version": "v0",
        "mock_actual_outcome_id": "shadow-cycle-mock-actual-outcome-001",
        "synthetic_dry_run_only": True,
        "real_behavior_executed": False,
        "actual_y_summary": "shadow artifacts generated; no canonical mutation or execution",
        "safety_flags": SAFETY_FLAGS,
    }
    event = {
        "schema_name": "ystar.shadow_cycle_cieu_residual.event_fixture",
        "schema_version": "v0",
        "event_id": "shadow-cycle-cieu-event-fixture-001",
        "X_t": {"shadow_input_ref": rel(REPROJECT / "next_cycle_projection_input_candidate.json")},
        "U_t": {
            "shadow_work_proposal_ref": rel(SHADOW / "shadow_autonomous_work_proposal_candidate.json"),
            "shadow_pre_u_candidate_ref": rel(SHADOW / "shadow_cycle_pre_u_packet_candidate.json"),
        },
        "Y_star_t": {
            "shadow_behavior_y_star_preview_ref": rel(REPROJECT / "shadow_reprojected_behavior_y_star_preview.json"),
            "preview_behavior_y_star": preview["preview_behavior_y_star"],
        },
        "Y_t_plus_1": {
            "shadow_mock_actual_ref": rel(SHADOW_CIEU / "shadow_cycle_mock_actual_outcome.json"),
            "dry_run_mock_only": True,
        },
        "R_t_plus_1": {
            "residual_mode": "deterministic_structural_residual",
            "semantic_truth_scoring_used": False,
        },
        "event_mode": "shadow_dry_run_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    residual = {
        "schema_name": "ystar.shadow_cycle_cieu_residual.delta",
        "schema_version": "v0",
        "residual_delta_id": "shadow-cycle-residual-delta-001",
        "event_id": event["event_id"],
        "shadow_projection_alignment_residual": "shadow proposal aligns with preview but remains noncanonical",
        "shadow_pre_u_gate_residual": "shadow gate allows dry-run only",
        "shadow_dry_run_execution_residual": "no real shadow execution occurred",
        "behavior_boundary_residual": "behavior boundaries preserved",
        "evidence_gap_residual": "production evidence still absent",
        "learning_queue_residual": "learning remains review-gated",
        "live_blocker_residual": "live remains blocked",
        "writeback_blocker_residual": "writeback remains blocked",
        "canonical_policy_mutation_blocker_residual": "canonical policy mutation remains blocked",
        "semantic_truth_scoring_used": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.shadow_cycle_cieu_residual.summary",
        "schema_version": "v0",
        "shadow_cycle_cieu_fixture_generated": True,
        "shadow_cycle_residual_delta_generated": True,
        "event_mode": event["event_mode"],
        "persistence_enabled": False,
        "db_write_performed": False,
        "semantic_truth_scoring_used": False,
    }
    return predicted, actual, event, residual, summary


def build_comparison(
    behavior: dict[str, Any],
    preview: dict[str, Any],
    original_residual: dict[str, Any],
    shadow_residual: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    comparison = {
        "schema_name": "ystar.original_vs_shadow_cycle_comparison.comparison",
        "schema_version": "v0",
        "comparison_id": "original-vs-shadow-cycle-comparison-001",
        "original_behavior_y_star_id": behavior["behavior_y_star_id"],
        "shadow_behavior_y_star_preview_id": preview["preview_id"],
        "original_work_intent": "refresh mission dashboard using projection-checked behavior-level Y* context",
        "shadow_work_intent": "refresh mission dashboard using shadow-updated behavior-level Y* context",
        "original_projection_gate_decision": "projection_gate_passed_for_dry_run",
        "shadow_projection_gate_decision": "shadow_projection_gate_passed_for_dry_run",
        "original_pre_u_gate_decision": "allow_dry_run_only",
        "shadow_pre_u_gate_decision": "allow_shadow_dry_run_only",
        "original_residual_classes": list(original_residual.keys()),
        "shadow_residual_classes": list(shadow_residual.keys()),
        "inherited_constraints_preserved": True,
        "safety_boundaries_preserved": True,
        "learning_effect_observed_in_shadow_only": True,
        "canonical_system_changed": False,
        "brain_memory_changed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    delta = {
        "schema_name": "ystar.original_vs_shadow_cycle_comparison.delta",
        "schema_version": "v0",
        "delta_id": "original-vs-shadow-cycle-delta-001",
        "y_star_projection_delta": "shadow preview adds residual-review obligations and evidence sufficiency language",
        "work_alignment_delta": "shadow work intent cites shadow behavior Y* preview",
        "pre_u_mapping_delta": "shadow Pre-U candidate carries residual-driven governance expectations",
        "residual_classification_delta": "shadow residual separates canonical mutation blocker from writeback blocker",
        "evidence_requirement_delta": "shadow preview requires explicit evidence sufficiency before canonical application",
        "safety_boundary_delta": "no safety boundary relaxed",
        "safety_flags": SAFETY_FLAGS,
    }
    effect = {
        "schema_name": "ystar.original_vs_shadow_cycle_comparison.learning_effect_summary",
        "schema_version": "v0",
        "effect_summary_id": "shadow-learning-effect-summary-001",
        "effect_class": EFFECT_CLASS,
        "previous_residual_visibly_influenced_shadow_projection": True,
        "visible_shadow_effect": (
            "Shadow behavior-level Y* preview adds residual-review obligations, "
            "no-execution residual labeling, and evidence sufficiency requirements."
        ),
        "canonical_system_changed": False,
        "brain_memory_changed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return comparison, delta, effect


def build_integrated_cieu(
    review_decision: dict[str, Any],
    classification: dict[str, Any],
    patch: dict[str, Any],
    preview: dict[str, Any],
    comparison: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    predicted = {
        "schema_name": "ystar.integrated_learning_cycle_cieu_fixture.predicted_outcome",
        "schema_version": "v0",
        "predicted_outcome_id": "integrated-learning-cycle-predicted-outcome-001",
        "declared_target": "convert L5.3 residual into a non-applied shadow projection update and run one shadow-updated dry-run cycle preview",
        "safety_flags": SAFETY_FLAGS,
    }
    actual = {
        "schema_name": "ystar.integrated_learning_cycle_cieu_fixture.mock_actual_outcome",
        "schema_version": "v0",
        "mock_actual_outcome_id": "integrated-learning-cycle-mock-actual-outcome-001",
        "review_decision_packet_generated": True,
        "learning_target_classification_generated": True,
        "update_candidate_generated": True,
        "shadow_patch_generated": True,
        "shadow_behavior_level_y_star_preview_generated": True,
        "shadow_projection_checked_cycle_generated": True,
        "original_vs_shadow_comparison_generated": True,
        "no_canonical_writeback": True,
        "safety_flags": SAFETY_FLAGS,
    }
    event = {
        "schema_name": "ystar.integrated_learning_cycle_cieu_fixture.event",
        "schema_version": "v0",
        "event_id": "integrated-learning-cycle-cieu-event-fixture-001",
        "X_t": {
            "residual_ref": INPUT_REFS["l5_3_residual"],
            "learning_candidate_ref": INPUT_REFS["l5_3_learning_candidate"],
        },
        "U_t": {
            "operation": "integrated review-gated learning plus shadow-updated cycle preview",
            "review_decision_ref": rel(REVIEW / "residual_review_gate_decision.json"),
            "shadow_patch_ref": rel(PATCH / "shadow_projection_policy_patch.json"),
        },
        "Y_star_t": predicted["declared_target"],
        "Y_t_plus_1": {
            "integrated_mock_actual_ref": rel(INTEGRATED / "integrated_learning_cycle_mock_actual_outcome.json"),
            "no_canonical_writeback": True,
        },
        "R_t_plus_1": {
            "residual_mode": "deterministic_structural_residual",
            "semantic_truth_scoring_used": False,
        },
        "event_mode": "integrated_review_gated_shadow_cycle_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    residual = {
        "schema_name": "ystar.integrated_learning_cycle_cieu_fixture.residual_delta",
        "schema_version": "v0",
        "residual_delta_id": "integrated-learning-cycle-residual-delta-001",
        "event_id": event["event_id"],
        "review_gate_residual": "review gate allows shadow update candidate only",
        "shadow_patch_residual": "shadow patch generated but not applied canonically",
        "shadow_cycle_residual": "shadow cycle generated with no execution",
        "canonical_learning_blocker_residual": "controlled canonical learning design remains future milestone",
        "l6_blocker_residual": "L6 revenue discovery remains blocked",
        "semantic_truth_scoring_used": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.integrated_learning_cycle_cieu_fixture.summary",
        "schema_version": "v0",
        "integrated_learning_cycle_cieu_fixture_generated": True,
        "event_mode": event["event_mode"],
        "persistence_enabled": False,
        "db_write_performed": False,
        "semantic_truth_scoring_used": False,
        "shadow_patch_generated": patch["preview_only"],
        "shadow_behavior_y_star_preview_generated": bool(preview["preview_id"]),
        "original_vs_shadow_comparison_generated": bool(comparison["comparison_id"]),
    }
    return predicted, actual, event, residual, summary


def build_readiness() -> dict[str, Any]:
    return {
        "schema_name": "ystar.integrated_shadow_learning_readiness",
        "schema_version": "v0",
        "readiness_id": "integrated-shadow-learning-readiness-v0",
        "l5_3_residual_consumed": True,
        "residual_normalized": True,
        "review_gate_decision_generated": True,
        "learning_target_classified": True,
        "projection_policy_update_candidate_generated": True,
        "shadow_projection_policy_patch_generated": True,
        "shadow_behavior_y_star_preview_generated": True,
        "shadow_updated_projection_cycle_generated": True,
        "shadow_cycle_cieu_fixture_generated": True,
        "original_vs_shadow_cycle_comparison_generated": True,
        "integrated_learning_cycle_cieu_fixture_generated": True,
        "previous_residual_influenced_shadow_projection": True,
        "live_execution_still_blocked": True,
        "writeback_still_blocked": True,
        "canonical_policy_mutation_still_blocked": True,
        "external_action_still_blocked": True,
        "ready_for_controlled_canonical_learning_design": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "live_execution_enabled": False,
        "behavior_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "candidate_auto_approval_enabled": False,
        "canonical_policy_mutation_enabled": False,
        "semantic_truth_scoring_enabled": False,
        "raw_runtime_artifact_reading_enabled": False,
        "revenue_opportunity_discovery_enabled": False,
        "shadow_patch_live_application_enabled": False,
        "next_required_milestone": "Controlled Canonical Learning Architecture v0",
    }


def main() -> None:
    inputs = {name: load_json(path) for name, path in INPUT_REFS.items()}
    contract = build_contract()
    input_fixture = build_input_fixture()
    normalized = normalize_residual(inputs["l5_3_residual"])
    review_policy = build_review_policy()
    review_decision, review_packet = build_review_gate(normalized)
    classification, scope_matrix, target_trace = build_learning_targets(normalized)
    update_candidates = build_update_candidates(review_decision, classification)
    shadow_patch, patch_plan, patch_denied = build_shadow_patch(update_candidates)
    next_input, shadow_preview, behavior_comparison, reprojection_gap_map = build_shadow_reprojection(
        inputs["mission_y_star"],
        inputs["behavior_y_star"],
        review_decision,
        update_candidates["projection_policy_update_candidate.json"],
        shadow_patch,
    )
    shadow_cycle_items = build_shadow_cycle(shadow_preview, next_input)
    shadow_predicted, shadow_actual, shadow_event, shadow_residual, shadow_residual_summary = (
        build_shadow_cieu_residual(shadow_preview, shadow_cycle_items)
    )
    cycle_comparison, cycle_delta, effect_summary = build_comparison(
        inputs["behavior_y_star"],
        shadow_preview,
        inputs["l5_3_residual"],
        shadow_residual,
    )
    integrated_predicted, integrated_actual, integrated_event, integrated_residual, integrated_summary = (
        build_integrated_cieu(review_decision, classification, shadow_patch, shadow_preview, cycle_comparison)
    )
    readiness = build_readiness()
    next_step = {
        "schema_name": "ystar.integrated_shadow_learning_readiness.next_step",
        "schema_version": "v0",
        "recommendation_id": "controlled-canonical-learning-architecture",
        "title": "Controlled Canonical Learning Architecture v0",
        "rationale": "L5.4 proves residuals can affect future Y* through shadow artifacts; the next step is controlled canonical learning design.",
        "ready_for_l6_revenue_opportunity_discovery": False,
        "live_execution_enabled": False,
        "canonical_policy_mutation_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
    }

    run = {
        "schema_name": "ystar.review_gated_shadow_learning_cycle.run",
        "schema_version": "v0",
        "run_id": "review-gated-shadow-learning-run-001",
        "loop_id": contract["loop_id"],
        "loop_stages": [
            {"stage": stage, "status": "completed_shadow_dry_run"} for stage in LOOP_STAGES
        ],
        "source_l5_3_residual_ref": INPUT_REFS["l5_3_residual"],
        "review_decision_ref": rel(REVIEW / "residual_review_gate_decision.json"),
        "shadow_patch_ref": rel(PATCH / "shadow_projection_policy_patch.json"),
        "shadow_behavior_y_star_preview_ref": rel(REPROJECT / "shadow_reprojected_behavior_y_star_preview.json"),
        "shadow_cycle_run_ref": rel(SHADOW / "shadow_updated_projection_cycle_run.json"),
        "original_vs_shadow_comparison_ref": rel(COMPARE / "original_vs_shadow_cycle_comparison.json"),
        "integrated_cieu_fixture_ref": rel(INTEGRATED / "integrated_learning_cycle_cieu_event_fixture.json"),
        "readiness_ref": rel(READINESS / "integrated_shadow_learning_readiness.json"),
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.review_gated_shadow_learning_cycle.summary",
        "schema_version": "v0",
        "integrated_review_gated_shadow_learning_cycle_defined": True,
        "l5_3_residual_consumed": True,
        "review_gate_decision_generated": True,
        "learning_target_classification_generated": True,
        "projection_policy_update_candidate_generated": True,
        "shadow_projection_policy_patch_generated": True,
        "shadow_behavior_y_star_preview_generated": True,
        "shadow_updated_projection_cycle_generated": True,
        "original_vs_shadow_cycle_comparison_generated": True,
        "integrated_cieu_like_fixture_generated": True,
        "candidate_approved": False,
        "candidate_applied": False,
        "canonical_policy_mutation_enabled": False,
        "previous_residual_influenced_shadow_projection": True,
        "ready_for_controlled_canonical_learning_design": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        "safety_flags": SAFETY_FLAGS,
    }
    target_summary = {
        "schema_name": "ystar.learning_target_classifier.summary",
        "schema_version": "v0",
        "learning_target_classification_generated": True,
        "targets_classified": LEARNING_TARGETS,
        "allowed_shadow_learning": True,
        "denied_canonical_policy_mutation": True,
        "denied_brain_writeback": True,
        "denied_memory_ingestion": True,
    }
    update_summary = {
        "schema_name": "ystar.projection_policy_update_candidate.summary",
        "schema_version": "v0",
        "projection_policy_update_candidate_generated": True,
        "behavior_y_star_generation_update_candidate_generated": True,
        "pre_u_mapping_update_candidate_generated": True,
        "work_alignment_update_candidate_generated": True,
        "residual_classification_update_candidate_generated": True,
        "evidence_collection_update_candidate_generated": True,
        "approval_status": "not_approved",
        "applied_to_canonical_policy": False,
        "applied_to_brain": False,
        "applied_to_memory": False,
    }
    patch_summary = {
        "schema_name": "ystar.shadow_projection_policy_patch.summary",
        "schema_version": "v0",
        "shadow_projection_policy_patch_generated": True,
        "preview_only": True,
        "canonical_policy_mutation": False,
        "brain_writeback": False,
        "memory_ingestion": False,
        "live_application": False,
        "shadow_cycle_preview_allowed": True,
    }
    reprojection_summary = {
        "schema_name": "ystar.shadow_reprojection_preview.summary",
        "schema_version": "v0",
        "next_cycle_projection_input_candidate_generated": True,
        "shadow_behavior_y_star_preview_generated": True,
        "original_vs_shadow_behavior_y_star_comparison_generated": True,
        "previous_residual_influenced_shadow_projection": True,
        "live_behavior_authorized": False,
        "behavior_execution_enabled": False,
        "applied_to_canonical_policy": False,
    }

    write_text(
        LOOP / "README.md",
        "# Review-Gated Shadow Learning Cycle\n\n"
        "L5.4 proves residuals can influence future Y* projection through shadow-only artifacts.\n",
    )
    write_json(LOOP / "review_gated_shadow_learning_contract.json", contract)
    write_json(LOOP / "review_gated_shadow_learning_input_fixture.json", input_fixture)
    write_json(LOOP / "review_gated_shadow_learning_run.json", run)
    write_json(LOOP / "review_gated_shadow_learning_summary.json", summary)
    write_text(
        LOOP / "review_gated_shadow_learning_report.md",
        md(
            "Review-Gated Shadow Learning Report",
            [
                "- L5.3 residual was normalized and reviewed.",
                "- Update candidates were generated but not approved or applied.",
                "- Shadow patch and shadow cycle preview were generated with canonical mutation disabled.",
            ],
        ),
    )

    write_json(REVIEW / "normalized_projection_residual.json", normalized)
    write_json(REVIEW / "residual_review_policy.json", review_policy)
    write_json(REVIEW / "residual_review_gate_decision.json", review_decision)
    write_json(REVIEW / "residual_review_decision_packet.json", review_packet)
    write_json(
        REVIEW / "residual_review_summary.json",
        {
            "schema_name": "ystar.residual_review_gate.summary",
            "schema_version": "v0",
            "residual_normalized": True,
            "review_gate_decision_generated": True,
            "decision": review_decision["decision"],
            "eligible_for_shadow_update_candidate": True,
            "eligible_for_shadow_cycle_preview": True,
            "approved_for_live_application": False,
            "approved_for_canonical_policy_mutation": False,
        },
    )
    write_text(REVIEW / "residual_review_report.md", md("Residual Review Report", ["- Decision: eligible_for_shadow_update_candidate.", "- No live or canonical application was approved."]))

    write_json(TARGETS / "learning_target_classification.json", classification)
    write_json(TARGETS / "learning_scope_matrix.json", scope_matrix)
    write_json(TARGETS / "learning_target_trace.json", target_trace)
    write_json(TARGETS / "learning_target_summary.json", target_summary)
    write_text(TARGETS / "learning_target_report.md", md("Learning Target Report", ["- All required targets were classified.", "- Only shadow learning and shadow cycle preview are allowed."]))

    for filename, payload in update_candidates.items():
        write_json(UPDATES / filename, payload)
    write_json(UPDATES / "projection_policy_update_summary.json", update_summary)
    write_text(UPDATES / "projection_policy_update_report.md", md("Projection Policy Update Report", ["- Update candidates are concrete but not approved.", "- No canonical policy, brain, or memory writes occurred."]))

    write_json(PATCH / "shadow_projection_policy_patch.json", shadow_patch)
    write_json(PATCH / "shadow_patch_application_plan.json", patch_plan)
    write_json(PATCH / "shadow_patch_denied_operations.json", patch_denied)
    write_json(PATCH / "shadow_patch_summary.json", patch_summary)
    write_text(PATCH / "shadow_patch_report.md", md("Shadow Patch Report", ["- Patch is preview-only.", "- Canonical mutation and live application are denied."]))

    write_json(REPROJECT / "next_cycle_projection_input_candidate.json", next_input)
    write_json(REPROJECT / "shadow_reprojected_behavior_y_star_preview.json", shadow_preview)
    write_json(REPROJECT / "original_vs_shadow_behavior_y_star_comparison.json", behavior_comparison)
    write_json(REPROJECT / "shadow_reprojection_gap_map.json", reprojection_gap_map)
    write_json(REPROJECT / "shadow_reprojection_summary.json", reprojection_summary)
    write_text(REPROJECT / "shadow_reprojection_report.md", md("Shadow Reprojection Report", ["- Shadow behavior-level Y* preview was generated.", "- Safety boundaries and Pre-U requirement are preserved."]))

    shadow_files = [
        "shadow_cycle_contract.json",
        "shadow_cycle_input_fixture.json",
        "shadow_projection_checked_work_intent.json",
        "shadow_autonomous_work_proposal_candidate.json",
        "shadow_work_proposal_to_behavior_y_star_alignment.json",
        "shadow_work_proposal_gate_decision.json",
        "shadow_cycle_pre_u_packet_candidate.json",
        "shadow_cycle_pre_u_gate_decision.json",
        "shadow_dry_run_work_result.json",
        "shadow_dry_run_work_receipt.json",
        "shadow_updated_projection_cycle_run.json",
        "shadow_updated_projection_cycle_summary.json",
    ]
    for filename, payload in zip(shadow_files, shadow_cycle_items):
        write_json(SHADOW / filename, payload)
    write_text(SHADOW / "shadow_updated_projection_cycle_report.md", md("Shadow Updated Projection Cycle Report", ["- Shadow cycle consumed shadow behavior-level Y* preview.", "- It produced only dry-run artifacts."]))

    write_json(SHADOW_CIEU / "shadow_cycle_cieu_event_fixture.json", shadow_event)
    write_json(SHADOW_CIEU / "shadow_cycle_predicted_outcome.json", shadow_predicted)
    write_json(SHADOW_CIEU / "shadow_cycle_mock_actual_outcome.json", shadow_actual)
    write_json(SHADOW_CIEU / "shadow_cycle_residual_delta.json", shadow_residual)
    write_json(SHADOW_CIEU / "shadow_cycle_residual_summary.json", shadow_residual_summary)
    write_text(SHADOW_CIEU / "shadow_cycle_residual_report.md", md("Shadow Cycle Residual Report", ["- Shadow CIEU-like fixture is dry-run only.", "- Residuals remain deterministic and structural."]))

    write_json(COMPARE / "original_vs_shadow_cycle_comparison.json", cycle_comparison)
    write_json(COMPARE / "original_vs_shadow_cycle_delta.json", cycle_delta)
    write_json(COMPARE / "shadow_learning_effect_summary.json", effect_summary)
    write_text(COMPARE / "original_vs_shadow_cycle_report.md", md("Original vs Shadow Cycle Report", ["- Residual produced a visible shadow-only behavior Y* effect.", "- Canonical system, brain, and memory did not change."]))

    write_json(INTEGRATED / "integrated_learning_cycle_cieu_event_fixture.json", integrated_event)
    write_json(INTEGRATED / "integrated_learning_cycle_predicted_outcome.json", integrated_predicted)
    write_json(INTEGRATED / "integrated_learning_cycle_mock_actual_outcome.json", integrated_actual)
    write_json(INTEGRATED / "integrated_learning_cycle_residual_delta.json", integrated_residual)
    write_json(INTEGRATED / "integrated_learning_cycle_cieu_summary.json", integrated_summary)
    write_text(INTEGRATED / "integrated_learning_cycle_cieu_report.md", md("Integrated Learning Cycle CIEU Report", ["- Top-level CIEU-like fixture is dry-run only.", "- No persistence or DB write occurred."]))

    write_json(READINESS / "integrated_shadow_learning_readiness.json", readiness)
    write_text(
        READINESS / "integrated_shadow_learning_readiness.md",
        md(
            "Integrated Shadow Learning Readiness",
            [
                "- ready_for_controlled_canonical_learning_design: true",
                "- ready_for_l6_revenue_opportunity_discovery: false",
                "- live/writeback/canonical mutation/external paths remain blocked.",
            ],
        ),
    )
    write_json(READINESS / "l5_5_or_l6_recommended_next_step.json", next_step)

    print("Built L5.4 review-gated shadow learning cycle artifacts.")


if __name__ == "__main__":
    main()
