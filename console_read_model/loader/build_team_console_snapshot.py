#!/usr/bin/env python3
"""Build a static team console snapshot from curated read-model files only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "console_read_model" / "generated"
GENERATOR_VERSION = "v0"

CURATED_SOURCES = [
    "console_read_model/team_brain_read_model.json",
    "console_read_model/agent_cards.json",
    "console_read_model/capability_matrix.json",
    "agent_brains/team_capsule_map.json",
    "agent_brains/Aiden-CEO/brain_profile.json",
    "agent_brains/Ethan-CTO/brain_profile.json",
    "agent_brains/Samantha-Secretary/brain_profile.json",
    "agent_brains/Ethan-CTO/execution_channels.json",
    "runtime_artifact_quarantine/quarantine_index.json",
    "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
    "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
    "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json",
    "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
    "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
    "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
    "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
    "labs_governance_bridge/generated/governance_decision_snapshot.json",
    "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json",
    "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
    "cross_repo_alignment/generated/cross_repo_alignment_summary.json",
    "labs_live_readiness/generated/live_readiness_report.json",
    "labs_live_boundary/generated/live_boundary_summary.json",
    "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json",
    "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
    "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
    "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
    "governed_observation_loop/generated/governed_observation_loop_summary.json",
    "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
    "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
    "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
    "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
    "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json",
    "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
    "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
    "mission_field_projection_contract/projection_contract_summary.json",
    "field_functional_auto_projection_core/field_projection_operator_summary.json",
    "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
    "behavior_y_star_to_pre_u_candidate/pre_u_candidate_summary.json",
    "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
    "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
    "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
    "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
    "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
    "projection_checked_learning_review_queue/projection_learning_review_summary.json",
    "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
    "residual_review_gate/residual_review_summary.json",
    "learning_target_classifier/learning_target_summary.json",
    "projection_policy_update_candidate/projection_policy_update_summary.json",
    "shadow_projection_policy_patch/shadow_patch_summary.json",
    "shadow_reprojection_preview/shadow_reprojection_summary.json",
    "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
    "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
    "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
    "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
    "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
    "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
    "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
    "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
    "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
    "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
    "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
    "mcp_request_intent_projection/mcp_request_intent_summary.json",
    "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
    "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
    "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
    "governed_mcp_call_candidate/governed_mcp_call_summary.json",
    "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
    "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
    "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
    "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
    "canonical_learning_target_registry/canonical_learning_target_summary.json",
    "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
    "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
    "canonical_update_package_candidate/canonical_update_package_summary.json",
    "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
    "rollback_and_audit_lineage/rollback_audit_summary.json",
    "post_promotion_validation_plan/post_promotion_validation_summary.json",
    "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
    "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
    "sandbox_approval_fixture/sandbox_approval_summary.json",
    "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
    "sandbox_patch_application/sandbox_patch_application_summary.json",
    "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
    "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
    "sandbox_rollback_validation/sandbox_rollback_summary.json",
    "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
    "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
    "real_approval_workflow_boundary/real_approval_workflow_summary.json",
    "approval_authority_model/approval_authority_summary.json",
    "approval_evidence_dossier/approval_evidence_summary.json",
    "durable_approval_record_contract/approval_record_summary.json",
    "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
    "approval_validity_revocation_policy/approval_validity_summary.json",
    "pre_application_snapshot_policy/snapshot_policy_summary.json",
    "real_application_boundary_gate/real_application_boundary_summary.json",
    "post_approval_preflight_validation/post_approval_preflight_summary.json",
    "manual_approval_runbook/manual_approval_runbook_summary.json",
    "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
    "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
]

UNSAFE_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "__pycache__",
    "active-agent",
    ".pid",
    "daemon",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/drift_hourly",
]


class BuildError(Exception):
    """Raised when the static snapshot cannot be built safely."""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def assert_safe_source(path: Path) -> None:
    try:
        relative = rel(path)
    except ValueError as exc:
        raise BuildError(f"Refusing path outside repo: {path}") from exc

    lowered = relative.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                raise BuildError(f"Refusing unsafe source: {relative}")
        elif m in lowered:
            raise BuildError(f"Refusing unsafe source: {relative}")


def load_json(relative_path: str, files_read: list[str]) -> Any:
    path = ROOT / relative_path
    assert_safe_source(path)
    if not path.exists():
        raise BuildError(f"Missing curated source: {relative_path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    files_read.append(relative_path)
    return data


def load_optional_json(relative_path: str, files_read: list[str]) -> Any | None:
    path = ROOT / relative_path
    assert_safe_source(path)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    files_read.append(relative_path)
    return data


def write_json(relative_path: str, payload: Any, generated_files: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    generated_files.append(relative_path)


def write_text(relative_path: str, text: str, generated_files: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated_files.append(relative_path)


def build_quarantine_summary(
    quarantine_index: dict[str, Any],
    quarantine_manifest: dict[str, Any],
) -> dict[str, Any]:
    artifacts = quarantine_manifest.get("artifacts", [])
    future_adapter_candidates = sorted(
        {
            artifact.get("future_adapter_candidate")
            for artifact in artifacts
            if artifact.get("future_adapter_candidate")
            and artifact.get("future_adapter_candidate") not in {"none", "none_or_metadata_only"}
        }
    )
    if not future_adapter_candidates:
        future_adapter_candidates = quarantine_index.get("future_adapters", [])

    return {
        "schema_name": "ystar.console_read_model.generated.quarantine_summary",
        "schema_version": "v0",
        "framework_status": quarantine_index.get("framework_status"),
        "current_mining_level": quarantine_index.get("current_mining_level"),
        "artifacts_classified": quarantine_manifest.get("artifacts_classified", 0),
        "unsafe_artifacts_count": quarantine_manifest.get("unsafe_artifacts_count", 0),
        "classes_seen": quarantine_manifest.get("classes_seen", {}),
        "generated_manifest_ref": quarantine_index.get(
            "generated_manifest_ref",
            "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
        ),
        "forbidden_direct_reads": quarantine_index.get("forbidden_direct_reads", []),
        "future_adapter_candidates": future_adapter_candidates,
        "safety_warning": (
            "Console displays only curated path-level quarantine summary. "
            "No artifact contents were read."
        ),
    }


def build_safe_mining_summary(candidate_index: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.safe_mining_summary",
        "schema_version": "v0",
        "candidate_count": candidate_index.get("candidate_count", 0),
        "classes_seen": candidate_index.get("classes_seen", {}),
        "generated_candidate_index": (
            "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"
        ),
        "mining_manifest_ref": "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json",
        "safety_level": candidate_index.get("safety_level", "bounded_markdown_candidate"),
        "ingestion_status": candidate_index.get("ingestion_status", "candidate_only"),
        "allowed_next_step": candidate_index.get("allowed_next_step", "human_review_or_curated_queue"),
        "forbidden_next_step": candidate_index.get("forbidden_next_step", "direct_brain_writeback"),
        "allowed_artifact_classes": candidate_index.get("allowed_artifact_classes", []),
        "bounds": candidate_index.get("bounds", {}),
        "warning": (
            "Safe mining candidates are bounded review assets only. They are not brain memory, "
            "CIEU records, or approved writeback."
        ),
    }


def build_review_queue_summary(review_queue: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.review_queue_summary",
        "schema_version": "v0",
        "review_count": review_queue.get("review_count", 0),
        "statuses": review_queue.get("statuses", {}),
        "ingestion_statuses": review_queue.get("ingestion_statuses", {}),
        "intended_use_summary": review_queue.get("intended_use_summary", {}),
        "generated_queue_path": (
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json"
        ),
        "review_queue_manifest_ref": (
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/review_queue_manifest.json"
        ),
        "default_review_status": review_queue.get("default_review_status", "pending_review"),
        "default_ingestion_status": review_queue.get("default_ingestion_status", "not_ingested"),
        "allowed_review_actions": review_queue.get("allowed_review_actions", []),
        "forbidden_actions": review_queue.get("forbidden_actions", []),
        "warning": (
            "Review queue entries are not brain memory and require explicit approval "
            "before any future CIEU, memory, or capsule use."
        ),
    }


def build_disposition_summary(disposition_index: dict[str, Any]) -> dict[str, Any]:
    summary = disposition_index.get("summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.artifact_disposition_summary",
        "schema_version": "v0",
        "total_artifacts": summary.get("total_artifacts", 0),
        "artifacts_with_disposition": summary.get("artifacts_with_disposition", 0),
        "dispositions": summary.get("dispositions", {}),
        "artifact_classes": summary.get("artifact_classes", {}),
        "safe_mined_to_review_queue": summary.get("safe_mined_to_review_queue", 0),
        "deferred_adapter_counts": summary.get("deferred_adapter_counts", {}),
        "ignored_generated_cache": summary.get("ignored_generated_cache", 0),
        "forbidden_direct_read_count": summary.get("forbidden_direct_read_count", 0),
        "evidence_scoring_status": summary.get("evidence_scoring_status", {}),
        "generated_disposition_index": (
            "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json"
        ),
        "warning": summary.get(
            "warning",
            "Disposition is not ingestion. No brain/memory/CIEU writes are allowed.",
        ),
    }


def build_evidence_review_summary(
    evidence_scores: dict[str, Any],
    decision_stub: dict[str, Any],
    hint_routing: dict[str, Any],
) -> dict[str, Any]:
    summary = evidence_scores.get("summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.evidence_review_summary",
        "schema_version": "v0",
        "candidates_scored": summary.get("candidates_scored", 0),
        "decision_stubs_created": decision_stub.get("decision_stubs_created", 0),
        "routes_created": hint_routing.get("routes_created", 0),
        "reuse_readiness": summary.get("reuse_readiness", {}),
        "confidence": summary.get("confidence", {}),
        "route_counts": hint_routing.get("route_counts", {}),
        "semantic_truth_status": summary.get("semantic_truth_status", {}),
        "automatic_approvals": summary.get("automatic_approvals", 0),
        "brain_writeback_allowed": summary.get("brain_writeback_allowed", 0),
        "memory_ingestion_allowed": summary.get("memory_ingestion_allowed", 0),
        "cieu_write_allowed": summary.get("cieu_write_allowed", 0),
        "generated_evidence_scores": "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
        "generated_review_decisions": "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
        "generated_hint_routing": "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
        "warning": summary.get(
            "warning",
            "Evidence scoring is structural only. It is not truth validation and not memory ingestion.",
        ),
    }


def build_governance_bridge_summary(decision_snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.governance_bridge_summary",
        "schema_version": "v0",
        "latest_bridge_run_id": decision_snapshot.get("bridge_run_id"),
        "source_task_id": decision_snapshot.get("source_task_id"),
        "agent_id": decision_snapshot.get("agent_id"),
        "ystar_gov_cli_path": decision_snapshot.get("ystar_gov_cli_path"),
        "ystar_gov_exit_code": decision_snapshot.get("ystar_gov_exit_code"),
        "ystar_gov_decision": decision_snapshot.get("ystar_gov_decision"),
        "allow_execution": decision_snapshot.get("allow_execution"),
        "require_revision": decision_snapshot.get("require_revision"),
        "deny": decision_snapshot.get("deny"),
        "escalate": decision_snapshot.get("escalate"),
        "dry_run_only": decision_snapshot.get("dry_run_only"),
        "non_execution_confirmation": decision_snapshot.get("non_execution_confirmation"),
        "action_executed": decision_snapshot.get("action_executed"),
        "cieu_written": decision_snapshot.get("cieu_written"),
        "brain_writeback_performed": decision_snapshot.get("brain_writeback_performed"),
        "memory_ingestion_performed": decision_snapshot.get("memory_ingestion_performed"),
        "generated_decision_snapshot": (
            "labs_governance_bridge/generated/governance_decision_snapshot.json"
        ),
        "warning": decision_snapshot.get(
            "warning",
            "Bridge is dry-run only and does not execute actions or write CIEU.",
        ),
    }


def build_pre_u_governance_summary(decision_snapshots: dict[str, Any]) -> dict[str, Any]:
    summary = decision_snapshots.get("summary", {})
    snapshots = decision_snapshots.get("snapshots", [])
    decisions_by_role = {
        snapshot.get("agent_id"): {
            "packet_id": snapshot.get("packet_id"),
            "decision": snapshot.get("ystar_gov_decision"),
            "exit_code": snapshot.get("ystar_gov_exit_code"),
            "allow_execution": snapshot.get("allow_execution"),
            "require_revision": snapshot.get("require_revision"),
            "deny": snapshot.get("deny"),
            "escalate": snapshot.get("escalate"),
        }
        for snapshot in snapshots
    }
    return {
        "schema_name": "ystar.console_read_model.generated.pre_u_governance_summary",
        "schema_version": "v0",
        "packets_generated": summary.get("snapshots_created", 0),
        "roles_covered": summary.get("roles_covered", []),
        "decision_counts": summary.get("decision_counts", {}),
        "decisions_by_role": decisions_by_role,
        "dry_run_only": summary.get("dry_run_only"),
        "action_executed": summary.get("action_executed"),
        "cieu_written": summary.get("cieu_written"),
        "brain_writeback_performed": summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": summary.get("memory_ingestion_performed"),
        "generated_decision_snapshots": (
            "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json"
        ),
        "warning": summary.get(
            "warning",
            "Generated Pre-U governance decisions are dry-run only and are not runtime actions.",
        ),
    }


def build_labs_acceptance_summary(acceptance_report: dict[str, Any] | None) -> dict[str, Any]:
    if not acceptance_report:
        return {
            "schema_name": "ystar.console_read_model.generated.labs_acceptance_summary",
            "schema_version": "v0",
            "accepted": False,
            "checks_passed": 0,
            "checks_total": 0,
            "roles_covered": [],
            "decision_counts": {},
            "action_executed": False,
            "cieu_written": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
            "raw_runtime_artifacts_ingested": False,
            "generated_acceptance_report": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
            "warning": "Labs runtime acceptance report has not been generated yet.",
        }

    checks = acceptance_report.get("checks", [])
    passed = sum(1 for check in checks if check.get("status") == "PASS")
    safety = acceptance_report.get("safety_assertions", {})
    decision_summary = acceptance_report.get("decision_summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.labs_acceptance_summary",
        "schema_version": "v0",
        "accepted": acceptance_report.get("accepted"),
        "checks_passed": passed,
        "checks_total": len(checks),
        "roles_covered": decision_summary.get("roles_covered", []),
        "decision_counts": decision_summary.get("decision_counts", {}),
        "action_executed": safety.get("action_executed"),
        "cieu_written": safety.get("cieu_written"),
        "brain_writeback_performed": safety.get("brain_writeback_performed"),
        "memory_ingestion_performed": safety.get("memory_ingestion_performed"),
        "raw_runtime_artifacts_ingested": safety.get("raw_runtime_artifacts_ingested"),
        "generated_acceptance_report": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
        "warning": acceptance_report.get(
            "safety_note",
            "Labs runtime acceptance is dry-run only.",
        ),
    }


def build_cross_repo_alignment_summary(cross_repo_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not cross_repo_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.cross_repo_alignment_summary",
            "schema_version": "v0",
            "alignment_accepted": False,
            "ystar_company_head": None,
            "ystar_company_head_summary": None,
            "ystar_gov_head": None,
            "ystar_gov_head_summary": None,
            "ystar_gov_endpoint_accepted": False,
            "labs_runtime_accepted": False,
            "roles_covered": [],
            "decision_counts": {},
            "safety_assertions": {},
            "generated_manifest": "cross_repo_alignment/generated/cross_repo_status_manifest.json",
            "warning": "Cross-repo alignment report has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.cross_repo_alignment_summary",
        "schema_version": "v0",
        "alignment_accepted": cross_repo_summary.get("alignment_accepted"),
        "ystar_company_head": cross_repo_summary.get("ystar_company_head"),
        "ystar_company_head_summary": cross_repo_summary.get("ystar_company_head_summary"),
        "ystar_gov_head": cross_repo_summary.get("ystar_gov_head"),
        "ystar_gov_head_summary": cross_repo_summary.get("ystar_gov_head_summary"),
        "ystar_gov_endpoint_accepted": cross_repo_summary.get("ystar_gov_endpoint_accepted"),
        "labs_runtime_accepted": cross_repo_summary.get("labs_runtime_accepted"),
        "roles_covered": cross_repo_summary.get("roles_covered", []),
        "decision_counts": cross_repo_summary.get("decision_counts", {}),
        "safety_assertions": cross_repo_summary.get("safety_assertions", {}),
        "generated_manifest": cross_repo_summary.get(
            "generated_manifest",
            "cross_repo_alignment/generated/cross_repo_status_manifest.json",
        ),
        "warning": cross_repo_summary.get(
            "warning",
            "Cross-repo alignment is dry-run only and does not execute actions or write CIEU.",
        ),
    }


def build_live_readiness_summary(live_readiness_report: dict[str, Any] | None) -> dict[str, Any]:
    if not live_readiness_report:
        return {
            "schema_name": "ystar.console_read_model.generated.live_readiness_summary",
            "schema_version": "v0",
            "dry_run_governance_ready": False,
            "minimal_live_loop_ready": False,
            "minimal_live_loop_status": "not_evaluated",
            "recommended_next_phase": "build_live_readiness_report",
            "live_action_execution_allowed": False,
            "live_cieu_write_allowed": False,
            "live_brain_writeback_allowed": False,
            "live_memory_ingestion_allowed": False,
            "candidate_auto_approval_allowed": False,
            "raw_artifact_ingestion_allowed": False,
            "blockers": [],
            "transition_backlog_items": 0,
            "generated_report": "labs_live_readiness/generated/live_readiness_report.json",
            "generated_transition_backlog": "labs_live_readiness/generated/transition_backlog.json",
            "warning": "Live readiness report has not been generated yet.",
        }

    safety = live_readiness_report.get("safety_booleans", {})
    blockers = live_readiness_report.get("live_execution_blockers", [])
    overall = live_readiness_report.get("overall_status", {})
    transition = live_readiness_report.get("transition_backlog_summary", {})
    return {
        "schema_name": "ystar.console_read_model.generated.live_readiness_summary",
        "schema_version": "v0",
        "dry_run_governance_ready": overall.get("dry_run_governance_ready"),
        "minimal_live_loop_ready": overall.get("minimal_live_loop_ready"),
        "minimal_live_loop_status": overall.get("minimal_live_loop_status"),
        "recommended_next_phase": overall.get("recommended_next_phase"),
        "live_action_execution_allowed": safety.get("live_action_execution_allowed"),
        "live_cieu_write_allowed": safety.get("live_cieu_write_allowed"),
        "live_brain_writeback_allowed": safety.get("live_brain_writeback_allowed"),
        "live_memory_ingestion_allowed": safety.get("live_memory_ingestion_allowed"),
        "candidate_auto_approval_allowed": safety.get("candidate_auto_approval_allowed"),
        "raw_artifact_ingestion_allowed": safety.get("raw_artifact_ingestion_allowed"),
        "blockers": blockers,
        "transition_backlog_items": transition.get("items_total", 0),
        "generated_report": "labs_live_readiness/generated/live_readiness_report.json",
        "generated_transition_backlog": "labs_live_readiness/generated/transition_backlog.json",
        "warning": live_readiness_report.get(
            "warning",
            "Live-readiness gate is not live runtime and keeps action/CIEU/brain/memory writes blocked.",
        ),
    }


def build_live_boundary_summary(live_boundary_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not live_boundary_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.live_boundary_summary",
            "schema_version": "v0",
            "live_boundary_defined": False,
            "operator_approval_gate_defined": False,
            "action_sandbox_contract_defined": False,
            "rollback_policy_defined": False,
            "cieu_writer_boundary_defined": False,
            "live_action_execution_enabled": False,
            "cieu_write_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "candidate_auto_approval_enabled": False,
            "raw_artifact_ingestion_enabled": False,
            "requires_manual_enablement": True,
            "minimal_live_loop_ready": False,
            "blocked_reason": "live_boundary_manifest_not_generated",
            "checklist_status_counts": {},
            "ready_or_enabled_checklist_items": 0,
            "generated_manifest": "labs_live_boundary/generated/live_boundary_manifest.json",
            "generated_checklist": "labs_live_boundary/generated/live_transition_checklist.json",
            "warning": "Live boundary manifest has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.live_boundary_summary",
        "schema_version": "v0",
        "live_boundary_defined": live_boundary_summary.get("live_boundary_defined"),
        "operator_approval_gate_defined": live_boundary_summary.get("operator_approval_gate_defined"),
        "action_sandbox_contract_defined": live_boundary_summary.get("action_sandbox_contract_defined"),
        "rollback_policy_defined": live_boundary_summary.get("rollback_policy_defined"),
        "cieu_writer_boundary_defined": live_boundary_summary.get("cieu_writer_boundary_defined"),
        "live_action_execution_enabled": live_boundary_summary.get("live_action_execution_enabled"),
        "cieu_write_enabled": live_boundary_summary.get("cieu_write_enabled"),
        "brain_writeback_enabled": live_boundary_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": live_boundary_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": live_boundary_summary.get("candidate_auto_approval_enabled"),
        "raw_artifact_ingestion_enabled": live_boundary_summary.get("raw_artifact_ingestion_enabled"),
        "requires_manual_enablement": live_boundary_summary.get("requires_manual_enablement"),
        "minimal_live_loop_ready": live_boundary_summary.get("minimal_live_loop_ready"),
        "blocked_reason": live_boundary_summary.get("blocked_reason"),
        "checklist_status_counts": live_boundary_summary.get("checklist_status_counts", {}),
        "ready_or_enabled_checklist_items": live_boundary_summary.get("ready_or_enabled_checklist_items", 0),
        "generated_manifest": live_boundary_summary.get(
            "generated_manifest",
            "labs_live_boundary/generated/live_boundary_manifest.json",
        ),
        "generated_checklist": live_boundary_summary.get(
            "generated_checklist",
            "labs_live_boundary/generated/live_transition_checklist.json",
        ),
        "warning": live_boundary_summary.get(
            "warning",
            "Live boundary harness is defined but disabled.",
        ),
    }


def build_cieu_boundary_summary(cieu_boundary_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not cieu_boundary_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.cieu_boundary_summary",
            "schema_version": "v0",
            "cieu_runtime_boundary_defined": False,
            "cieu_runtime_event_schema_defined": False,
            "prediction_delta_fixture_defined": False,
            "cieu_writer_policy_defined": False,
            "dry_run_only": True,
            "persistence_enabled": False,
            "live_action_execution_enabled": False,
            "cieu_write_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "candidate_auto_approval_enabled": False,
            "raw_artifact_ingestion_enabled": False,
            "requires_manual_enablement": True,
            "minimal_live_loop_ready": False,
            "blocked_reason": "cieu_runtime_boundary_manifest_not_generated",
            "generated_manifest": "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json",
            "generated_sample_event": "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json",
            "generated_prediction_delta_fixture": (
                "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json"
            ),
            "warning": "CIEU runtime boundary manifest has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.cieu_boundary_summary",
        "schema_version": "v0",
        "cieu_runtime_boundary_defined": cieu_boundary_summary.get("cieu_runtime_boundary_defined"),
        "cieu_runtime_event_schema_defined": cieu_boundary_summary.get("cieu_runtime_event_schema_defined"),
        "prediction_delta_fixture_defined": cieu_boundary_summary.get("prediction_delta_fixture_defined"),
        "cieu_writer_policy_defined": cieu_boundary_summary.get("cieu_writer_policy_defined"),
        "dry_run_only": cieu_boundary_summary.get("dry_run_only"),
        "persistence_enabled": cieu_boundary_summary.get("persistence_enabled"),
        "live_action_execution_enabled": cieu_boundary_summary.get("live_action_execution_enabled"),
        "cieu_write_enabled": cieu_boundary_summary.get("cieu_write_enabled"),
        "brain_writeback_enabled": cieu_boundary_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": cieu_boundary_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": cieu_boundary_summary.get("candidate_auto_approval_enabled"),
        "raw_artifact_ingestion_enabled": cieu_boundary_summary.get("raw_artifact_ingestion_enabled"),
        "requires_manual_enablement": cieu_boundary_summary.get("requires_manual_enablement"),
        "minimal_live_loop_ready": cieu_boundary_summary.get("minimal_live_loop_ready"),
        "blocked_reason": cieu_boundary_summary.get("blocked_reason"),
        "generated_manifest": cieu_boundary_summary.get(
            "generated_manifest",
            "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json",
        ),
        "generated_sample_event": cieu_boundary_summary.get(
            "generated_sample_event",
            "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json",
        ),
        "generated_prediction_delta_fixture": cieu_boundary_summary.get(
            "generated_prediction_delta_fixture",
            "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json",
        ),
        "warning": cieu_boundary_summary.get(
            "warning",
            "CIEU runtime boundary is defined but persistence is disabled.",
        ),
    }


def build_autonomy_inventory_summary(autonomy_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not autonomy_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.autonomy_inventory_summary",
            "schema_version": "v0",
            "company_autonomy_inventory_defined": False,
            "repo_archaeology_completed": False,
            "observation_capability_map_defined": False,
            "resource_sensing_map_defined": False,
            "action_capability_map_defined": False,
            "governed_tool_registry_candidates_defined": False,
            "agent_role_capability_matrix_defined": False,
            "commercial_agent_company_goal_aligned": False,
            "governance_only_runtime": False,
            "live_actions_enabled": False,
            "external_actions_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "cieu_persistence_enabled": False,
            "git_push_enabled": False,
            "daemon_control_enabled": False,
            "email_or_external_communication_enabled": False,
            "requires_manual_enablement": True,
            "next_required_milestone": "L4.2 Company Autonomous Work Cycle Simulator v0",
            "generated_summary": "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
            "warning": "Company autonomy inventory has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.autonomy_inventory_summary",
        "schema_version": "v0",
        "company_autonomy_inventory_defined": autonomy_summary.get("company_autonomy_inventory_defined"),
        "repo_archaeology_completed": autonomy_summary.get("repo_archaeology_completed"),
        "observation_capability_map_defined": autonomy_summary.get("observation_capability_map_defined"),
        "resource_sensing_map_defined": autonomy_summary.get("resource_sensing_map_defined"),
        "action_capability_map_defined": autonomy_summary.get("action_capability_map_defined"),
        "governed_tool_registry_candidates_defined": autonomy_summary.get(
            "governed_tool_registry_candidates_defined"
        ),
        "agent_role_capability_matrix_defined": autonomy_summary.get("agent_role_capability_matrix_defined"),
        "commercial_agent_company_goal_aligned": autonomy_summary.get("commercial_agent_company_goal_aligned"),
        "governance_only_runtime": autonomy_summary.get("governance_only_runtime"),
        "live_actions_enabled": autonomy_summary.get("live_actions_enabled"),
        "external_actions_enabled": autonomy_summary.get("external_actions_enabled"),
        "brain_writeback_enabled": autonomy_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": autonomy_summary.get("memory_ingestion_enabled"),
        "cieu_persistence_enabled": autonomy_summary.get("cieu_persistence_enabled"),
        "git_push_enabled": autonomy_summary.get("git_push_enabled"),
        "daemon_control_enabled": autonomy_summary.get("daemon_control_enabled"),
        "email_or_external_communication_enabled": autonomy_summary.get(
            "email_or_external_communication_enabled"
        ),
        "requires_manual_enablement": autonomy_summary.get("requires_manual_enablement"),
        "next_required_milestone": autonomy_summary.get("next_required_milestone"),
        "generated_summary": "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
        "generated_report": "company_autonomy_inventory/generated/company_autonomy_report.md",
        "warning": "Company autonomy inventory is discovery-only; all live actions remain disabled.",
    }


def build_autonomous_cycle_summary(cycle_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not cycle_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.autonomous_cycle_summary",
            "schema_version": "v0",
            "autonomous_work_cycle_defined": False,
            "mission_bounded_autonomy_defined": False,
            "founder_sets_mission_agent_team_drives": False,
            "step_by_step_human_prompting_required": True,
            "observation_snapshot_defined": False,
            "autonomous_work_backlog_defined": False,
            "selected_work_item_defined": False,
            "role_delegation_defined": False,
            "governed_tool_selection_defined": False,
            "pre_u_packet_simulated": False,
            "governance_decision_simulated": False,
            "action_plan_simulated": False,
            "cieu_event_simulated": False,
            "residual_delta_simulated": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.3 Governed Read-Only Observation Loop v0",
            "generated_summary": "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
            "warning": "Autonomous work cycle simulator has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.autonomous_cycle_summary",
        "schema_version": "v0",
        "autonomous_work_cycle_defined": cycle_summary.get("autonomous_work_cycle_defined"),
        "mission_bounded_autonomy_defined": cycle_summary.get("mission_bounded_autonomy_defined"),
        "founder_sets_mission_agent_team_drives": cycle_summary.get("founder_sets_mission_agent_team_drives"),
        "step_by_step_human_prompting_required": cycle_summary.get("step_by_step_human_prompting_required"),
        "observation_snapshot_defined": cycle_summary.get("observation_snapshot_defined"),
        "autonomous_work_backlog_defined": cycle_summary.get("autonomous_work_backlog_defined"),
        "selected_work_item_defined": cycle_summary.get("selected_work_item_defined"),
        "role_delegation_defined": cycle_summary.get("role_delegation_defined"),
        "governed_tool_selection_defined": cycle_summary.get("governed_tool_selection_defined"),
        "pre_u_packet_simulated": cycle_summary.get("pre_u_packet_simulated"),
        "governance_decision_simulated": cycle_summary.get("governance_decision_simulated"),
        "action_plan_simulated": cycle_summary.get("action_plan_simulated"),
        "cieu_event_simulated": cycle_summary.get("cieu_event_simulated"),
        "residual_delta_simulated": cycle_summary.get("residual_delta_simulated"),
        "next_task_recommendations_defined": cycle_summary.get("next_task_recommendations_defined"),
        "real_action_executed": cycle_summary.get("real_action_executed"),
        "external_action_executed": cycle_summary.get("external_action_executed"),
        "live_action_enabled": cycle_summary.get("live_action_enabled"),
        "git_push_enabled": cycle_summary.get("git_push_enabled"),
        "daemon_control_enabled": cycle_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": cycle_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": cycle_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": cycle_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": cycle_summary.get("email_or_external_communication_enabled"),
        "requires_manual_enablement_for_live": cycle_summary.get("requires_manual_enablement_for_live"),
        "next_required_milestone": cycle_summary.get("next_required_milestone"),
        "generated_summary": "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
        "generated_report": cycle_summary.get(
            "generated_report",
            "company_autonomous_work_cycle/generated/autonomous_work_cycle_report.md",
        ),
        "warning": cycle_summary.get(
            "warning",
            "Autonomous work cycle is simulated only; no real action occurred.",
        ),
    }


def build_legacy_triage_summary(triage_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not triage_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.legacy_triage_summary",
            "schema_version": "v0",
            "legacy_asset_triage_defined": False,
            "assets_scored": 0,
            "absorption_buckets_defined": False,
            "bucket_counts": {},
            "top_absorption_candidates_defined": False,
            "top_absorption_candidate_count": 0,
            "governed_absorption_backlog_defined": False,
            "governed_absorption_backlog_count": 0,
            "blind_absorption_allowed": False,
            "blanket_rewrite_allowed": False,
            "live_actions_enabled": False,
            "next_required_milestone": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
            "generated_summary": "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
            "warning": "Legacy asset triage has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.legacy_triage_summary",
        "schema_version": "v0",
        "legacy_asset_triage_defined": triage_summary.get("legacy_asset_triage_defined"),
        "assets_scored": triage_summary.get("assets_scored"),
        "absorption_buckets_defined": triage_summary.get("absorption_buckets_defined"),
        "bucket_counts": triage_summary.get("bucket_counts", {}),
        "top_absorption_candidates_defined": triage_summary.get("top_absorption_candidates_defined"),
        "top_absorption_candidate_count": triage_summary.get("top_absorption_candidate_count"),
        "governed_absorption_backlog_defined": triage_summary.get("governed_absorption_backlog_defined"),
        "governed_absorption_backlog_count": triage_summary.get("governed_absorption_backlog_count"),
        "blind_absorption_allowed": triage_summary.get("blind_absorption_allowed"),
        "blanket_rewrite_allowed": triage_summary.get("blanket_rewrite_allowed"),
        "live_actions_enabled": triage_summary.get("live_actions_enabled"),
        "external_actions_enabled": triage_summary.get("external_actions_enabled"),
        "brain_writeback_enabled": triage_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": triage_summary.get("memory_ingestion_enabled"),
        "cieu_persistence_enabled": triage_summary.get("cieu_persistence_enabled"),
        "next_required_milestone": triage_summary.get("next_required_milestone"),
        "generated_summary": "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
        "generated_report": "legacy_asset_triage/generated/legacy_asset_triage_report.md",
        "warning": triage_summary.get("warning", "Legacy assets are triaged only; no absorption is executed."),
    }


def build_observation_loop_summary(observation_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not observation_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.observation_loop_summary",
            "schema_version": "v0",
            "governed_observation_loop_defined": False,
            "read_only_observation_loop_defined": False,
            "observation_source_registry_defined": False,
            "observation_tick_generated": False,
            "mission_dashboard_snapshot_defined": False,
            "company_state_digest_defined": False,
            "observation_to_work_item_candidates_defined": False,
            "mission_bounded_autonomy_supported": False,
            "step_by_step_human_prompting_reduced": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "next_required_milestone": "L4.4 First Governed Read-Only Observation Tool Wrapper v0",
            "generated_summary": "governed_observation_loop/generated/governed_observation_loop_summary.json",
            "warning": "Governed observation loop has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.observation_loop_summary",
        "schema_version": "v0",
        "governed_observation_loop_defined": observation_summary.get("governed_observation_loop_defined"),
        "read_only_observation_loop_defined": observation_summary.get("read_only_observation_loop_defined"),
        "observation_source_registry_defined": observation_summary.get("observation_source_registry_defined"),
        "observation_tick_generated": observation_summary.get("observation_tick_generated"),
        "mission_dashboard_snapshot_defined": observation_summary.get("mission_dashboard_snapshot_defined"),
        "company_state_digest_defined": observation_summary.get("company_state_digest_defined"),
        "observation_to_work_item_candidates_defined": observation_summary.get(
            "observation_to_work_item_candidates_defined"
        ),
        "observation_to_work_item_candidate_count": observation_summary.get(
            "observation_to_work_item_candidate_count"
        ),
        "mission_bounded_autonomy_supported": observation_summary.get("mission_bounded_autonomy_supported"),
        "step_by_step_human_prompting_reduced": observation_summary.get("step_by_step_human_prompting_reduced"),
        "real_action_executed": observation_summary.get("real_action_executed"),
        "external_action_executed": observation_summary.get("external_action_executed"),
        "live_action_enabled": observation_summary.get("live_action_enabled"),
        "git_push_enabled": observation_summary.get("git_push_enabled"),
        "daemon_control_enabled": observation_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": observation_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": observation_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": observation_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": observation_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": observation_summary.get("next_required_milestone"),
        "generated_summary": "governed_observation_loop/generated/governed_observation_loop_summary.json",
        "generated_report": "governed_observation_loop/generated/governed_observation_loop_report.md",
        "warning": observation_summary.get("warning", "Observation loop is read-only and executes no actions."),
    }


def build_readonly_tool_summary(tool_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not tool_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.readonly_tool_summary",
            "schema_version": "v0",
            "governed_readonly_observation_tool_defined": False,
            "tool_contract_defined": False,
            "allowed_source_registry_defined": False,
            "sample_invocation_defined": False,
            "sample_result_defined": False,
            "unsafe_invocation_rejected": False,
            "tool_cieu_event_defined": False,
            "local_readonly_dry_run_callable": False,
            "first_governed_tool_wrapper_created": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.5 Governed Tool Invocation Through Pre-U Bridge v0",
            "generated_summary": "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
            "warning": "Governed read-only observation tool has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.readonly_tool_summary",
        "schema_version": "v0",
        "governed_readonly_observation_tool_defined": tool_summary.get(
            "governed_readonly_observation_tool_defined"
        ),
        "tool_contract_defined": tool_summary.get("tool_contract_defined"),
        "allowed_source_registry_defined": tool_summary.get("allowed_source_registry_defined"),
        "sample_invocation_defined": tool_summary.get("sample_invocation_defined"),
        "sample_result_defined": tool_summary.get("sample_result_defined"),
        "unsafe_invocation_rejected": tool_summary.get("unsafe_invocation_rejected"),
        "tool_cieu_event_defined": tool_summary.get("tool_cieu_event_defined"),
        "local_readonly_dry_run_callable": tool_summary.get("local_readonly_dry_run_callable"),
        "mission_bounded_autonomy_supported": tool_summary.get("mission_bounded_autonomy_supported"),
        "step_by_step_human_prompting_reduced": tool_summary.get("step_by_step_human_prompting_reduced"),
        "first_governed_tool_wrapper_created": tool_summary.get("first_governed_tool_wrapper_created"),
        "real_action_executed": tool_summary.get("real_action_executed"),
        "external_action_executed": tool_summary.get("external_action_executed"),
        "live_action_enabled": tool_summary.get("live_action_enabled"),
        "network_enabled": tool_summary.get("network_enabled"),
        "git_push_enabled": tool_summary.get("git_push_enabled"),
        "daemon_control_enabled": tool_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": tool_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": tool_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": tool_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": tool_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": tool_summary.get("next_required_milestone"),
        "generated_summary": "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
        "generated_contract": tool_summary.get(
            "generated_contract",
            "governed_readonly_observation_tool/generated/tool_contract.json",
        ),
        "generated_registry": tool_summary.get(
            "generated_registry",
            "governed_readonly_observation_tool/generated/allowed_source_registry.json",
        ),
        "generated_sample_result": tool_summary.get(
            "generated_sample_result",
            "governed_readonly_observation_tool/generated/sample_tool_result.json",
        ),
        "generated_cieu_event": tool_summary.get(
            "generated_cieu_event",
            "governed_readonly_observation_tool/generated/tool_cieu_event.json",
        ),
        "warning": tool_summary.get(
            "warning",
            "Read-only wrapper is callable locally, but live execution and persistence remain disabled.",
        ),
    }


def build_tool_bridge_summary(bridge_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not bridge_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.tool_bridge_summary",
            "schema_version": "v0",
            "governed_tool_invocation_bridge_defined": False,
            "bridge_contract_defined": False,
            "agent_tool_request_defined": False,
            "pre_u_tool_packet_defined": False,
            "governance_decision_defined": False,
            "bridge_authorization_defined": False,
            "tool_invoked_through_bridge": False,
            "direct_tool_invocation_rejected": False,
            "unsafe_bridge_request_rejected": False,
            "bridge_cieu_event_defined": False,
            "bridge_residual_delta_defined": False,
            "first_governed_tool_invocation_chain_created": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0",
            "generated_summary": "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
            "warning": "Governed tool invocation bridge has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.tool_bridge_summary",
        "schema_version": "v0",
        "governed_tool_invocation_bridge_defined": bridge_summary.get(
            "governed_tool_invocation_bridge_defined"
        ),
        "bridge_contract_defined": bridge_summary.get("bridge_contract_defined"),
        "agent_tool_request_defined": bridge_summary.get("agent_tool_request_defined"),
        "pre_u_tool_packet_defined": bridge_summary.get("pre_u_tool_packet_defined"),
        "governance_decision_defined": bridge_summary.get("governance_decision_defined"),
        "bridge_authorization_defined": bridge_summary.get("bridge_authorization_defined"),
        "tool_invoked_through_bridge": bridge_summary.get("tool_invoked_through_bridge"),
        "direct_tool_invocation_rejected": bridge_summary.get("direct_tool_invocation_rejected"),
        "unsafe_bridge_request_rejected": bridge_summary.get("unsafe_bridge_request_rejected"),
        "bridge_cieu_event_defined": bridge_summary.get("bridge_cieu_event_defined"),
        "bridge_residual_delta_defined": bridge_summary.get("bridge_residual_delta_defined"),
        "mission_bounded_autonomy_supported": bridge_summary.get("mission_bounded_autonomy_supported"),
        "step_by_step_human_prompting_reduced": bridge_summary.get("step_by_step_human_prompting_reduced"),
        "first_governed_tool_invocation_chain_created": bridge_summary.get(
            "first_governed_tool_invocation_chain_created"
        ),
        "real_action_executed": bridge_summary.get("real_action_executed"),
        "external_action_executed": bridge_summary.get("external_action_executed"),
        "live_action_enabled": bridge_summary.get("live_action_enabled"),
        "network_enabled": bridge_summary.get("network_enabled"),
        "git_push_enabled": bridge_summary.get("git_push_enabled"),
        "daemon_control_enabled": bridge_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": bridge_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": bridge_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": bridge_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": bridge_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": bridge_summary.get("next_required_milestone"),
        "generated_summary": "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
        "generated_contract": bridge_summary.get(
            "generated_contract",
            "governed_tool_invocation_bridge/generated/bridge_contract.json",
        ),
        "generated_pre_u_packet": bridge_summary.get(
            "generated_pre_u_packet",
            "governed_tool_invocation_bridge/generated/pre_u_tool_packet.json",
        ),
        "generated_bridged_result": bridge_summary.get(
            "generated_bridged_result",
            "governed_tool_invocation_bridge/generated/bridged_tool_result.json",
        ),
        "generated_cieu_event": bridge_summary.get(
            "generated_cieu_event",
            "governed_tool_invocation_bridge/generated/bridge_cieu_event.json",
        ),
        "warning": bridge_summary.get(
            "warning",
            "Tool invocation is routed through a Pre-U bridge for local read-only dry-run only.",
        ),
    }


def build_work_proposal_summary(work_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not work_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.work_proposal_summary",
            "schema_version": "v0",
            "agent_team_work_proposal_defined": False,
            "mission_context_snapshot_defined": False,
            "agent_team_observation_input_defined": False,
            "autonomous_work_proposals_defined": False,
            "selected_work_proposal_defined": False,
            "role_review_board_defined": False,
            "tool_need_analysis_defined": False,
            "generated_tool_request_defined": False,
            "work_proposal_routed_to_bridge": False,
            "direct_tool_invocation_used": False,
            "bridged_tool_result_ref_defined": False,
            "work_proposal_cieu_event_defined": False,
            "work_proposal_residual_delta_defined": False,
            "agent_team_generated_the_work": False,
            "agent_team_selected_governed_tool": False,
            "pre_u_bridge_required": False,
            "pre_u_bridge_satisfied": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.7 First Mission Dashboard Refresh Loop v0",
            "generated_summary": "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
            "warning": "Agent team work proposal pack has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.work_proposal_summary",
        "schema_version": "v0",
        "agent_team_work_proposal_defined": work_summary.get("agent_team_work_proposal_defined"),
        "mission_context_snapshot_defined": work_summary.get("mission_context_snapshot_defined"),
        "agent_team_observation_input_defined": work_summary.get("agent_team_observation_input_defined"),
        "autonomous_work_proposals_defined": work_summary.get("autonomous_work_proposals_defined"),
        "selected_work_proposal_defined": work_summary.get("selected_work_proposal_defined"),
        "role_review_board_defined": work_summary.get("role_review_board_defined"),
        "tool_need_analysis_defined": work_summary.get("tool_need_analysis_defined"),
        "generated_tool_request_defined": work_summary.get("generated_tool_request_defined"),
        "work_proposal_routed_to_bridge": work_summary.get("work_proposal_routed_to_bridge"),
        "bridge_runner_used": work_summary.get("bridge_runner_used"),
        "direct_tool_invocation_used": work_summary.get("direct_tool_invocation_used"),
        "bridged_tool_result_ref_defined": work_summary.get("bridged_tool_result_ref_defined"),
        "work_proposal_cieu_event_defined": work_summary.get("work_proposal_cieu_event_defined"),
        "work_proposal_residual_delta_defined": work_summary.get("work_proposal_residual_delta_defined"),
        "next_agent_work_recommendations_defined": work_summary.get("next_agent_work_recommendations_defined"),
        "mission_bounded_autonomy_supported": work_summary.get("mission_bounded_autonomy_supported"),
        "founder_sets_mission_agent_team_drives": work_summary.get("founder_sets_mission_agent_team_drives"),
        "step_by_step_human_prompting_required": work_summary.get("step_by_step_human_prompting_required"),
        "agent_team_generated_the_work": work_summary.get("agent_team_generated_the_work"),
        "agent_team_selected_governed_tool": work_summary.get("agent_team_selected_governed_tool"),
        "pre_u_bridge_required": work_summary.get("pre_u_bridge_required"),
        "pre_u_bridge_satisfied": work_summary.get("pre_u_bridge_satisfied"),
        "real_action_executed": work_summary.get("real_action_executed"),
        "external_action_executed": work_summary.get("external_action_executed"),
        "live_action_enabled": work_summary.get("live_action_enabled"),
        "network_enabled": work_summary.get("network_enabled"),
        "git_push_enabled": work_summary.get("git_push_enabled"),
        "daemon_control_enabled": work_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": work_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": work_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": work_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": work_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": work_summary.get("next_required_milestone"),
        "generated_summary": work_summary.get(
            "generated_summary",
            "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
        ),
        "generated_tool_request": work_summary.get(
            "generated_tool_request",
            "agent_team_work_proposal/generated/generated_tool_request.json",
        ),
        "generated_bridge_trace": work_summary.get(
            "generated_bridge_trace",
            "agent_team_work_proposal/generated/work_proposal_to_bridge_trace.json",
        ),
        "generated_bridged_result_ref": work_summary.get(
            "generated_bridged_result_ref",
            "agent_team_work_proposal/generated/bridged_tool_result_ref.json",
        ),
        "generated_cieu_event": work_summary.get(
            "generated_cieu_event",
            "agent_team_work_proposal/generated/work_proposal_cieu_event.json",
        ),
        "warning": work_summary.get(
            "warning",
            "Agent-team work proposal routes generated work through the governed bridge only.",
        ),
    }


def build_dashboard_refresh_summary(refresh_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not refresh_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.dashboard_refresh_summary",
            "schema_version": "v0",
            "mission_dashboard_refresh_loop_defined": False,
            "refresh_loop_contract_defined": False,
            "previous_dashboard_snapshot_defined": False,
            "current_observation_input_defined": False,
            "refreshed_mission_dashboard_defined": False,
            "company_state_delta_defined": False,
            "refreshed_autonomous_backlog_defined": False,
            "refresh_loop_trace_defined": False,
            "refresh_cieu_event_defined": False,
            "refresh_residual_delta_defined": False,
            "dashboard_refresh_loop_ran": False,
            "scheduler_used": False,
            "daemon_used": False,
            "manual_local_run_only": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.8 Governed Recurring Observation Loop Contract v0",
            "generated_summary": "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
            "warning": "Mission dashboard refresh loop has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.dashboard_refresh_summary",
        "schema_version": "v0",
        "mission_dashboard_refresh_loop_defined": refresh_summary.get(
            "mission_dashboard_refresh_loop_defined"
        ),
        "refresh_loop_contract_defined": refresh_summary.get("refresh_loop_contract_defined"),
        "previous_dashboard_snapshot_defined": refresh_summary.get(
            "previous_dashboard_snapshot_defined"
        ),
        "current_observation_input_defined": refresh_summary.get("current_observation_input_defined"),
        "refreshed_mission_dashboard_defined": refresh_summary.get(
            "refreshed_mission_dashboard_defined"
        ),
        "company_state_delta_defined": refresh_summary.get("company_state_delta_defined"),
        "refreshed_autonomous_backlog_defined": refresh_summary.get(
            "refreshed_autonomous_backlog_defined"
        ),
        "refresh_loop_trace_defined": refresh_summary.get("refresh_loop_trace_defined"),
        "refresh_cieu_event_defined": refresh_summary.get("refresh_cieu_event_defined"),
        "refresh_residual_delta_defined": refresh_summary.get("refresh_residual_delta_defined"),
        "next_loop_recommendations_defined": refresh_summary.get(
            "next_loop_recommendations_defined"
        ),
        "mission_bounded_autonomy_supported": refresh_summary.get(
            "mission_bounded_autonomy_supported"
        ),
        "founder_sets_mission_agent_team_drives": refresh_summary.get(
            "founder_sets_mission_agent_team_drives"
        ),
        "step_by_step_human_prompting_required": refresh_summary.get(
            "step_by_step_human_prompting_required"
        ),
        "dashboard_refresh_loop_ran": refresh_summary.get("dashboard_refresh_loop_ran"),
        "scheduler_used": refresh_summary.get("scheduler_used"),
        "daemon_used": refresh_summary.get("daemon_used"),
        "manual_local_run_only": refresh_summary.get("manual_local_run_only"),
        "real_action_executed": refresh_summary.get("real_action_executed"),
        "external_action_executed": refresh_summary.get("external_action_executed"),
        "live_action_enabled": refresh_summary.get("live_action_enabled"),
        "network_enabled": refresh_summary.get("network_enabled"),
        "git_push_enabled": refresh_summary.get("git_push_enabled"),
        "daemon_control_enabled": refresh_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": refresh_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": refresh_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": refresh_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": refresh_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": refresh_summary.get("next_required_milestone"),
        "generated_summary": refresh_summary.get(
            "generated_summary",
            "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
        ),
        "generated_contract": refresh_summary.get(
            "generated_contract",
            "mission_dashboard_refresh_loop/generated/refresh_loop_contract.json",
        ),
        "generated_refreshed_dashboard": refresh_summary.get(
            "generated_refreshed_dashboard",
            "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
        ),
        "generated_company_state_delta": refresh_summary.get(
            "generated_company_state_delta",
            "mission_dashboard_refresh_loop/generated/company_state_delta.json",
        ),
        "generated_cieu_event": refresh_summary.get(
            "generated_cieu_event",
            "mission_dashboard_refresh_loop/generated/refresh_cieu_event.json",
        ),
        "warning": refresh_summary.get(
            "warning",
            "Mission dashboard refresh loop is manual local dry-run only.",
        ),
    }


def build_recurring_loop_summary(recurring_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not recurring_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.recurring_loop_summary",
            "schema_version": "v0",
            "recurring_observation_loop_contract_defined": False,
            "recurrence_policy_defined": False,
            "recurrence_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "auto_run_enabled": False,
            "manual_local_simulation_only": False,
            "allowed_observation_sources_defined": False,
            "tick_governance_gate_defined": False,
            "simulated_observation_tick_defined": False,
            "simulated_tick_cieu_event_defined": False,
            "simulated_tick_residual_delta_defined": False,
            "stop_abort_conditions_defined": False,
            "escalation_conditions_defined": False,
            "manual_enablement_checklist_defined": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L4.9 Manual Recurring Observation Tick Runner v0",
            "generated_summary": (
                "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json"
            ),
            "warning": "Governed recurring observation loop contract has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.recurring_loop_summary",
        "schema_version": "v0",
        "recurring_observation_loop_contract_defined": recurring_summary.get(
            "recurring_observation_loop_contract_defined"
        ),
        "recurrence_policy_defined": recurring_summary.get("recurrence_policy_defined"),
        "recurrence_enabled": recurring_summary.get("recurrence_enabled"),
        "scheduler_enabled": recurring_summary.get("scheduler_enabled"),
        "daemon_enabled": recurring_summary.get("daemon_enabled"),
        "auto_run_enabled": recurring_summary.get("auto_run_enabled"),
        "manual_local_simulation_only": recurring_summary.get("manual_local_simulation_only"),
        "allowed_observation_sources_defined": recurring_summary.get(
            "allowed_observation_sources_defined"
        ),
        "tick_governance_gate_defined": recurring_summary.get("tick_governance_gate_defined"),
        "simulated_observation_tick_defined": recurring_summary.get(
            "simulated_observation_tick_defined"
        ),
        "simulated_tick_dashboard_delta_defined": recurring_summary.get(
            "simulated_tick_dashboard_delta_defined"
        ),
        "simulated_tick_work_candidates_defined": recurring_summary.get(
            "simulated_tick_work_candidates_defined"
        ),
        "simulated_tick_cieu_event_defined": recurring_summary.get(
            "simulated_tick_cieu_event_defined"
        ),
        "simulated_tick_residual_delta_defined": recurring_summary.get(
            "simulated_tick_residual_delta_defined"
        ),
        "stop_abort_conditions_defined": recurring_summary.get("stop_abort_conditions_defined"),
        "escalation_conditions_defined": recurring_summary.get("escalation_conditions_defined"),
        "manual_enablement_checklist_defined": recurring_summary.get(
            "manual_enablement_checklist_defined"
        ),
        "mission_bounded_autonomy_supported": recurring_summary.get(
            "mission_bounded_autonomy_supported"
        ),
        "founder_sets_mission_agent_team_drives": recurring_summary.get(
            "founder_sets_mission_agent_team_drives"
        ),
        "step_by_step_human_prompting_required": recurring_summary.get(
            "step_by_step_human_prompting_required"
        ),
        "real_action_executed": recurring_summary.get("real_action_executed"),
        "external_action_executed": recurring_summary.get("external_action_executed"),
        "live_action_enabled": recurring_summary.get("live_action_enabled"),
        "network_enabled": recurring_summary.get("network_enabled"),
        "git_push_enabled": recurring_summary.get("git_push_enabled"),
        "daemon_control_enabled": recurring_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": recurring_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": recurring_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": recurring_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": recurring_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": recurring_summary.get("next_required_milestone"),
        "generated_summary": recurring_summary.get(
            "generated_summary",
            "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json",
        ),
        "generated_contract": recurring_summary.get(
            "generated_contract",
            "recurring_observation_loop_contract/generated/recurring_loop_contract.json",
        ),
        "generated_allowed_sources": recurring_summary.get(
            "generated_allowed_sources",
            "recurring_observation_loop_contract/generated/allowed_observation_sources.json",
        ),
        "generated_tick": recurring_summary.get(
            "generated_tick",
            "recurring_observation_loop_contract/generated/simulated_observation_tick_001.json",
        ),
        "generated_cieu_event": recurring_summary.get(
            "generated_cieu_event",
            "recurring_observation_loop_contract/generated/simulated_tick_cieu_event.json",
        ),
        "generated_residual_delta": recurring_summary.get(
            "generated_residual_delta",
            "recurring_observation_loop_contract/generated/simulated_tick_residual_delta.json",
        ),
        "warning": recurring_summary.get(
            "warning",
            "Recurring observation loop contract is disabled for recurrence and simulates one manual local tick only.",
        ),
    }


def build_manual_tick_summary(manual_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not manual_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.manual_tick_summary",
            "schema_version": "v0",
            "manual_recurring_observation_tick_runner_defined": False,
            "manual_tick_runner_contract_defined": False,
            "manual_tick_request_defined": False,
            "manual_tick_preflight_defined": False,
            "manual_tick_source_validation_defined": False,
            "manual_tick_governance_decision_defined": False,
            "manual_tick_result_defined": False,
            "manual_tick_dashboard_delta_defined": False,
            "manual_tick_work_candidates_defined": False,
            "manual_tick_cieu_event_defined": False,
            "manual_tick_residual_delta_defined": False,
            "manual_tick_run_receipt_defined": False,
            "manual_tick_history_index_defined": False,
            "manual_tick_next_recommendations_defined": False,
            "manual_trigger_required": False,
            "one_tick_per_invocation": False,
            "total_recorded_ticks": 0,
            "recurrence_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "auto_run_enabled": False,
            "manual_local_run_only": False,
            "real_action_executed": False,
            "external_action_executed": False,
            "live_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L5.0 Review-Gated Learning Candidate Queue v0",
            "generated_summary": (
                "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json"
            ),
            "warning": "Manual recurring observation tick runner has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.manual_tick_summary",
        "schema_version": "v0",
        "manual_recurring_observation_tick_runner_defined": manual_summary.get(
            "manual_recurring_observation_tick_runner_defined"
        ),
        "manual_tick_runner_contract_defined": manual_summary.get(
            "manual_tick_runner_contract_defined"
        ),
        "manual_tick_request_defined": manual_summary.get("manual_tick_request_defined"),
        "manual_tick_preflight_defined": manual_summary.get("manual_tick_preflight_defined"),
        "manual_tick_source_validation_defined": manual_summary.get(
            "manual_tick_source_validation_defined"
        ),
        "manual_tick_governance_decision_defined": manual_summary.get(
            "manual_tick_governance_decision_defined"
        ),
        "manual_tick_result_defined": manual_summary.get("manual_tick_result_defined"),
        "manual_tick_dashboard_delta_defined": manual_summary.get(
            "manual_tick_dashboard_delta_defined"
        ),
        "manual_tick_work_candidates_defined": manual_summary.get(
            "manual_tick_work_candidates_defined"
        ),
        "manual_tick_cieu_event_defined": manual_summary.get("manual_tick_cieu_event_defined"),
        "manual_tick_residual_delta_defined": manual_summary.get(
            "manual_tick_residual_delta_defined"
        ),
        "manual_tick_run_receipt_defined": manual_summary.get("manual_tick_run_receipt_defined"),
        "manual_tick_history_index_defined": manual_summary.get(
            "manual_tick_history_index_defined"
        ),
        "manual_tick_next_recommendations_defined": manual_summary.get(
            "manual_tick_next_recommendations_defined"
        ),
        "manual_trigger_required": manual_summary.get("manual_trigger_required"),
        "one_tick_per_invocation": manual_summary.get("one_tick_per_invocation"),
        "total_recorded_ticks": manual_summary.get("total_recorded_ticks"),
        "mission_bounded_autonomy_supported": manual_summary.get(
            "mission_bounded_autonomy_supported"
        ),
        "founder_sets_mission_agent_team_drives": manual_summary.get(
            "founder_sets_mission_agent_team_drives"
        ),
        "step_by_step_human_prompting_required": manual_summary.get(
            "step_by_step_human_prompting_required"
        ),
        "recurrence_enabled": manual_summary.get("recurrence_enabled"),
        "scheduler_enabled": manual_summary.get("scheduler_enabled"),
        "daemon_enabled": manual_summary.get("daemon_enabled"),
        "auto_run_enabled": manual_summary.get("auto_run_enabled"),
        "manual_local_run_only": manual_summary.get("manual_local_run_only"),
        "real_action_executed": manual_summary.get("real_action_executed"),
        "external_action_executed": manual_summary.get("external_action_executed"),
        "live_action_enabled": manual_summary.get("live_action_enabled"),
        "network_enabled": manual_summary.get("network_enabled"),
        "git_push_enabled": manual_summary.get("git_push_enabled"),
        "daemon_control_enabled": manual_summary.get("daemon_control_enabled"),
        "cieu_persistence_enabled": manual_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": manual_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": manual_summary.get("memory_ingestion_enabled"),
        "email_or_external_communication_enabled": manual_summary.get(
            "email_or_external_communication_enabled"
        ),
        "next_required_milestone": manual_summary.get("next_required_milestone"),
        "generated_summary": manual_summary.get(
            "generated_summary",
            "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
        ),
        "generated_contract": manual_summary.get(
            "generated_contract",
            "manual_recurring_observation_tick_runner/generated/manual_tick_runner_contract.json",
        ),
        "generated_request": manual_summary.get(
            "generated_request",
            "manual_recurring_observation_tick_runner/generated/manual_tick_request.json",
        ),
        "generated_result": manual_summary.get(
            "generated_result",
            "manual_recurring_observation_tick_runner/generated/manual_tick_result.json",
        ),
        "generated_receipt": manual_summary.get(
            "generated_receipt",
            "manual_recurring_observation_tick_runner/generated/manual_tick_run_receipt.json",
        ),
        "generated_history": manual_summary.get(
            "generated_history",
            "manual_recurring_observation_tick_runner/generated/manual_tick_history_index.json",
        ),
        "generated_cieu_event": manual_summary.get(
            "generated_cieu_event",
            "manual_recurring_observation_tick_runner/generated/manual_tick_cieu_event.json",
        ),
        "generated_residual_delta": manual_summary.get(
            "generated_residual_delta",
            "manual_recurring_observation_tick_runner/generated/manual_tick_residual_delta.json",
        ),
        "warning": manual_summary.get(
            "warning",
            "Manual tick runner executes exactly one local dry-run tick and does not enable recurrence.",
        ),
    }


def build_field_functional_summary(field_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not field_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.field_functional_summary",
            "schema_version": "v0",
            "field_functional_archaeology_defined": False,
            "repos_scanned": 0,
            "assets_scanned": 0,
            "field_functional_assets_found": 0,
            "reuse_candidates_count": 0,
            "wrap_candidates_count": 0,
            "rewrite_candidates_count": 0,
            "concept_reference_count": 0,
            "do_not_absorb_count": 0,
            "old_field_functional_work_found": False,
            "mission_projection_merge_plan_defined": False,
            "ready_for_L5_projection_harness": False,
            "live_action_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L5.1 Mission Field Functional Projection Harness v0",
            "generated_summary": (
                "field_functional_archaeology/generated/field_functional_archaeology_summary.json"
            ),
            "warning": "Field functional archaeology has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.field_functional_summary",
        "schema_version": "v0",
        "field_functional_archaeology_defined": field_summary.get(
            "field_functional_archaeology_defined"
        ),
        "repos_scanned": field_summary.get("repos_scanned"),
        "assets_scanned": field_summary.get("assets_scanned"),
        "field_functional_assets_found": field_summary.get("field_functional_assets_found"),
        "reuse_candidates_count": field_summary.get("reuse_candidates_count"),
        "wrap_candidates_count": field_summary.get("wrap_candidates_count"),
        "rewrite_candidates_count": field_summary.get("rewrite_candidates_count"),
        "concept_reference_count": field_summary.get("concept_reference_count"),
        "do_not_absorb_count": field_summary.get("do_not_absorb_count"),
        "old_field_functional_work_found": field_summary.get("old_field_functional_work_found"),
        "mission_projection_merge_plan_defined": field_summary.get(
            "mission_projection_merge_plan_defined"
        ),
        "ready_for_L5_projection_harness": field_summary.get("ready_for_L5_projection_harness"),
        "live_action_enabled": field_summary.get("live_action_enabled"),
        "external_action_enabled": field_summary.get("external_action_enabled"),
        "network_enabled": field_summary.get("network_enabled"),
        "cieu_persistence_enabled": field_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": field_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": field_summary.get("memory_ingestion_enabled"),
        "next_required_milestone": field_summary.get("next_required_milestone"),
        "generated_summary": field_summary.get(
            "generated_summary",
            "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
        ),
        "generated_inventory": field_summary.get(
            "generated_inventory",
            "field_functional_archaeology/generated/field_functional_asset_inventory.json",
        ),
        "generated_merge_plan": field_summary.get(
            "generated_merge_plan",
            "field_functional_archaeology/generated/mission_projection_merge_plan.json",
        ),
        "warning": field_summary.get(
            "warning",
            "Field functional archaeology produces a merge plan only and enables no live action.",
        ),
    }


def build_mission_projection_summary(projection_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not projection_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.mission_projection_summary",
            "schema_version": "v0",
            "mission_field_projection_harness_defined": False,
            "l5_1_projection_contract_defined": False,
            "layered_projection_trace_generated": False,
            "pre_u_adapter_candidate_generated": False,
            "residual_delta_fixture_generated": False,
            "action_layer_projection_only": True,
            "action_field_execution_implemented": False,
            "ready_for_L5_2_field_functional_auto_projection_core": False,
            "deep_xt_model_is_not_l5_2_main_milestone": True,
            "live_execution_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "candidate_auto_approval_enabled": False,
            "next_required_milestone": "L5.2 Field Functional Auto-Projection Core v0",
            "generated_summary": "mission_field_projection_contract/projection_contract_summary.json",
            "warning": "Mission field projection harness has not been generated yet.",
        }
    return {
        "schema_name": "ystar.console_read_model.generated.mission_projection_summary",
        "schema_version": "v0",
        "mission_field_projection_harness_defined": projection_summary.get(
            "mission_field_projection_harness_defined"
        ),
        "l5_1_projection_contract_defined": projection_summary.get(
            "l5_1_projection_contract_defined"
        ),
        "layered_projection_trace_generated": projection_summary.get(
            "layered_projection_trace_generated"
        ),
        "pre_u_adapter_candidate_generated": projection_summary.get(
            "pre_u_adapter_candidate_generated"
        ),
        "residual_delta_fixture_generated": projection_summary.get(
            "residual_delta_fixture_generated"
        ),
        "projection_layers": projection_summary.get("projection_layers", []),
        "action_layer_projection_only": projection_summary.get("action_layer_projection_only"),
        "action_field_execution_implemented": projection_summary.get(
            "action_field_execution_implemented"
        ),
        "ready_for_L5_2_field_functional_auto_projection_core": projection_summary.get(
            "ready_for_L5_2_field_functional_auto_projection_core"
        ),
        "deep_xt_model_is_not_l5_2_main_milestone": projection_summary.get(
            "deep_xt_model_is_not_l5_2_main_milestone", True
        ),
        "live_execution_enabled": projection_summary.get("live_execution_enabled"),
        "external_action_enabled": projection_summary.get("external_action_enabled"),
        "network_enabled": projection_summary.get("network_enabled"),
        "scheduler_enabled": projection_summary.get("scheduler_enabled"),
        "daemon_enabled": projection_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": projection_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": projection_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": projection_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": projection_summary.get(
            "candidate_auto_approval_enabled"
        ),
        "next_required_milestone": projection_summary.get("next_required_milestone"),
        "generated_summary": "mission_field_projection_contract/projection_contract_summary.json",
        "generated_contract": projection_summary.get("generated_contract"),
        "generated_trace": projection_summary.get("generated_trace"),
        "generated_pre_u_candidate": projection_summary.get("generated_pre_u_candidate"),
        "generated_residual_delta": projection_summary.get("generated_residual_delta"),
        "warning": projection_summary.get(
            "warning",
            "Mission projection harness is dry-run only and does not execute action-field semantics.",
        ),
    }


def build_field_projection_summary(
    operator_summary: dict[str, Any] | None,
    projection_summary: dict[str, Any] | None,
    pre_u_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.field_projection_summary",
            "schema_version": "v0",
            "field_functional_auto_projection_core_defined": False,
            "mission_level_y_star_input_defined": False,
            "mission_to_behavior_projection_generated": False,
            "behavior_level_y_star_candidate_generated": False,
            "pre_u_packet_candidate_from_behavior_y_star_generated": False,
            "residual_delta_loop_fixture_generated": False,
            "learning_candidate_stub_generated_but_not_approved": False,
            "ready_for_l5_3_projection_checked_autonomous_cycle": False,
            "live_execution_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "behavior_execution_enabled": False,
            "next_required_milestone": "L5.3 Projection-Checked Autonomous Work Cycle v0",
            "warning": "Field functional auto-projection core has not been generated yet.",
        }
    operator_summary = operator_summary or {}
    projection_summary = projection_summary or {}
    pre_u_summary = pre_u_summary or {}
    residual_summary = residual_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.field_projection_summary",
        "schema_version": "v0",
        "field_functional_auto_projection_core_defined": operator_summary.get(
            "field_functional_auto_projection_core_defined"
        ),
        "projection_operator_defined": readiness_summary.get("projection_operator_defined"),
        "mission_level_y_star_input_defined": readiness_summary.get("mission_y_star_defined"),
        "mission_to_behavior_projection_generated": readiness_summary.get(
            "mission_to_behavior_trace_generated"
        ),
        "projection_layers": projection_summary.get("projection_layers", []),
        "behavior_level_y_star_candidate_generated": readiness_summary.get(
            "behavior_level_y_star_candidate_generated"
        ),
        "pre_u_packet_candidate_from_behavior_y_star_generated": readiness_summary.get(
            "pre_u_packet_candidate_generated"
        ),
        "residual_delta_loop_fixture_generated": readiness_summary.get(
            "residual_delta_fixture_generated"
        ),
        "learning_candidate_stub_generated_but_not_approved": residual_summary.get(
            "learning_candidate_stub_generated_but_not_approved"
        ),
        "live_execution_still_blocked": readiness_summary.get("live_execution_still_blocked"),
        "writeback_still_blocked": readiness_summary.get("writeback_still_blocked"),
        "external_action_still_blocked": readiness_summary.get("external_action_still_blocked"),
        "ready_for_l5_3_projection_checked_autonomous_cycle": readiness_summary.get(
            "ready_for_l5_3_projection_checked_autonomous_cycle"
        ),
        "l6_revenue_opportunity_discovery_enabled": operator_summary.get(
            "l6_revenue_opportunity_discovery_enabled"
        ),
        "dry_run_only": pre_u_summary.get("dry_run_only"),
        "pre_u_production_ready": pre_u_summary.get("production_ready"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_operator_summary": "field_functional_auto_projection_core/field_projection_operator_summary.json",
        "generated_projection_summary": "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
        "generated_behavior_candidate": "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
        "generated_pre_u_candidate": "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json",
        "generated_residual_loop_summary": "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
        "generated_readiness": "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
        "warning": (
            "L5.2 is a dry-run field projection core. It does not execute behavior, "
            "discover revenue opportunities, or write learning to memory."
        ),
    }


def build_projection_cycle_summary(
    cycle_summary: dict[str, Any] | None,
    work_summary: dict[str, Any] | None,
    pre_u_summary: dict[str, Any] | None,
    result_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    learning_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.projection_cycle_summary",
            "schema_version": "v0",
            "projection_checked_autonomous_work_cycle_defined": False,
            "behavior_y_star_consumed_by_cycle": False,
            "work_proposal_checked_against_behavior_y_star": False,
            "pre_u_packet_candidate_generated": False,
            "dry_run_gate_decision_generated": False,
            "dry_run_result_generated": False,
            "cieu_like_event_fixture_generated": False,
            "residual_delta_generated": False,
            "learning_review_candidate_generated_but_not_approved": False,
            "ready_for_l5_4_review_gated_learning_loop": False,
            "live_execution_enabled": False,
            "behavior_execution_enabled": False,
            "external_action_enabled": False,
            "network_enabled": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
            "next_required_milestone": "L5.4 Review-Gated Learning Loop v0",
            "warning": "Projection-checked autonomous work cycle has not been generated yet.",
        }
    cycle_summary = cycle_summary or {}
    work_summary = work_summary or {}
    pre_u_summary = pre_u_summary or {}
    result_summary = result_summary or {}
    residual_summary = residual_summary or {}
    learning_summary = learning_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.projection_cycle_summary",
        "schema_version": "v0",
        "projection_checked_autonomous_work_cycle_defined": cycle_summary.get(
            "projection_checked_autonomous_work_cycle_defined"
        ),
        "behavior_y_star_consumed_by_cycle": readiness_summary.get(
            "behavior_y_star_consumed_by_cycle"
        ),
        "work_proposal_checked_against_behavior_y_star": readiness_summary.get(
            "work_proposal_checked_against_behavior_y_star"
        ),
        "pre_u_packet_candidate_generated": readiness_summary.get(
            "pre_u_packet_candidate_generated"
        ),
        "dry_run_gate_decision_generated": readiness_summary.get(
            "dry_run_gate_decision_generated"
        ),
        "dry_run_result_generated": readiness_summary.get("dry_run_result_generated"),
        "cieu_like_event_fixture_generated": readiness_summary.get(
            "cieu_like_event_fixture_generated"
        ),
        "residual_delta_generated": readiness_summary.get("residual_delta_generated"),
        "learning_review_candidate_generated_but_not_approved": learning_summary.get(
            "projection_checked_learning_candidate_generated"
        )
        and learning_summary.get("approved") is False,
        "projection_gate_decision": work_summary.get("projection_gate_decision"),
        "cycle_pre_u_gate_decision": pre_u_summary.get("cycle_pre_u_gate_decision"),
        "dry_run_only": pre_u_summary.get("dry_run_only"),
        "pre_u_production_ready": pre_u_summary.get("production_ready"),
        "real_execution_performed": result_summary.get("real_execution_performed"),
        "event_mode": residual_summary.get("event_mode"),
        "db_write_performed": residual_summary.get("db_write_performed"),
        "live_execution_still_blocked": readiness_summary.get("live_execution_still_blocked"),
        "writeback_still_blocked": readiness_summary.get("writeback_still_blocked"),
        "external_action_still_blocked": readiness_summary.get("external_action_still_blocked"),
        "ready_for_l5_4_review_gated_learning_loop": readiness_summary.get(
            "ready_for_l5_4_review_gated_learning_loop"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_cycle_summary": "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
        "generated_work_summary": "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
        "generated_pre_u_summary": "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
        "generated_result_summary": "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
        "generated_residual_summary": "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
        "generated_learning_summary": "projection_checked_learning_review_queue/projection_learning_review_summary.json",
        "generated_readiness": "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
        "warning": (
            "L5.3 is a projection-checked dry-run cycle. It consumes behavior-level Y* "
            "as a gate but does not execute behavior or apply learning."
        ),
    }


def build_shadow_learning_cycle_summary(
    loop_summary: dict[str, Any] | None,
    review_summary: dict[str, Any] | None,
    target_summary: dict[str, Any] | None,
    update_summary: dict[str, Any] | None,
    patch_summary: dict[str, Any] | None,
    reprojection_summary: dict[str, Any] | None,
    shadow_cycle_summary: dict[str, Any] | None,
    shadow_residual_summary: dict[str, Any] | None,
    effect_summary: dict[str, Any] | None,
    integrated_cieu_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.shadow_learning_cycle_summary",
            "schema_version": "v0",
            "integrated_review_gated_shadow_learning_cycle_defined": False,
            "l5_3_residual_consumed": False,
            "review_gate_decision_generated": False,
            "learning_target_classification_generated": False,
            "projection_policy_update_candidate_generated": False,
            "shadow_projection_policy_patch_generated": False,
            "shadow_behavior_y_star_preview_generated": False,
            "shadow_updated_projection_cycle_generated": False,
            "original_vs_shadow_cycle_comparison_generated": False,
            "integrated_cieu_like_fixture_generated": False,
            "ready_for_controlled_canonical_learning_design": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Integrated shadow learning cycle has not been generated yet.",
        }
    loop_summary = loop_summary or {}
    review_summary = review_summary or {}
    target_summary = target_summary or {}
    update_summary = update_summary or {}
    patch_summary = patch_summary or {}
    reprojection_summary = reprojection_summary or {}
    shadow_cycle_summary = shadow_cycle_summary or {}
    shadow_residual_summary = shadow_residual_summary or {}
    effect_summary = effect_summary or {}
    integrated_cieu_summary = integrated_cieu_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.shadow_learning_cycle_summary",
        "schema_version": "v0",
        "integrated_review_gated_shadow_learning_cycle_defined": loop_summary.get(
            "integrated_review_gated_shadow_learning_cycle_defined"
        ),
        "l5_3_residual_consumed": readiness_summary.get("l5_3_residual_consumed"),
        "deterministic_review_gate_decision_generated": readiness_summary.get(
            "review_gate_decision_generated"
        ),
        "review_gate_decision": review_summary.get("decision"),
        "learning_target_classification_generated": readiness_summary.get(
            "learning_target_classified"
        ),
        "projection_policy_update_candidate_generated": readiness_summary.get(
            "projection_policy_update_candidate_generated"
        ),
        "shadow_projection_policy_patch_generated": readiness_summary.get(
            "shadow_projection_policy_patch_generated"
        ),
        "shadow_behavior_y_star_preview_generated": readiness_summary.get(
            "shadow_behavior_y_star_preview_generated"
        ),
        "shadow_updated_projection_cycle_generated": readiness_summary.get(
            "shadow_updated_projection_cycle_generated"
        ),
        "shadow_cycle_cieu_fixture_generated": readiness_summary.get(
            "shadow_cycle_cieu_fixture_generated"
        ),
        "original_vs_shadow_cycle_comparison_generated": readiness_summary.get(
            "original_vs_shadow_cycle_comparison_generated"
        ),
        "integrated_cieu_like_fixture_generated": readiness_summary.get(
            "integrated_learning_cycle_cieu_fixture_generated"
        ),
        "candidate_approved": loop_summary.get("candidate_approved"),
        "candidate_applied": loop_summary.get("candidate_applied"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "previous_residual_influenced_shadow_projection": readiness_summary.get(
            "previous_residual_influenced_shadow_projection"
        ),
        "shadow_learning_effect_class": effect_summary.get("effect_class"),
        "ready_for_controlled_canonical_learning_design": readiness_summary.get(
            "ready_for_controlled_canonical_learning_design"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "shadow_patch_live_application_enabled": readiness_summary.get(
            "shadow_patch_live_application_enabled"
        ),
        "shadow_patch_preview_only": patch_summary.get("preview_only"),
        "shadow_cycle_real_execution_performed": shadow_cycle_summary.get("real_execution_performed"),
        "shadow_cycle_db_write_performed": shadow_residual_summary.get("db_write_performed"),
        "integrated_cieu_db_write_performed": integrated_cieu_summary.get("db_write_performed"),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_loop_summary": "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
        "generated_review_summary": "residual_review_gate/residual_review_summary.json",
        "generated_target_summary": "learning_target_classifier/learning_target_summary.json",
        "generated_update_summary": "projection_policy_update_candidate/projection_policy_update_summary.json",
        "generated_shadow_patch_summary": "shadow_projection_policy_patch/shadow_patch_summary.json",
        "generated_reprojection_summary": "shadow_reprojection_preview/shadow_reprojection_summary.json",
        "generated_shadow_cycle_summary": "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
        "generated_shadow_residual_summary": "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
        "generated_integrated_cieu_summary": "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
        "generated_readiness": "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
        "warning": (
            "L5.4 is shadow-only. Residuals influence a preview Y* and shadow cycle, "
            "but no canonical policy, brain, memory, CIEU store, or live system is changed."
        ),
    }


def build_cross_repo_governance_summary(
    proof_summary: dict[str, Any] | None,
    y_star_gov_summary: dict[str, Any] | None,
    alignment_summary: dict[str, Any] | None,
    gov_mcp_summary: dict[str, Any] | None,
    governed_mcp_summary: dict[str, Any] | None,
    non_bypass_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.cross_repo_governance_summary",
            "schema_version": "v0",
            "cross_repo_governance_contract_proof_defined": False,
            "y_star_gov_surfaces_inventoried_read_only": False,
            "gov_mcp_surfaces_inventoried_read_only": False,
            "ready_for_l5_6_governed_mcp_dry_run_adapter": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Cross-repo governance contract proof has not been generated yet.",
        }
    proof_summary = proof_summary or {}
    y_star_gov_summary = y_star_gov_summary or {}
    alignment_summary = alignment_summary or {}
    gov_mcp_summary = gov_mcp_summary or {}
    governed_mcp_summary = governed_mcp_summary or {}
    non_bypass_summary = non_bypass_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.cross_repo_governance_summary",
        "schema_version": "v0",
        "cross_repo_governance_contract_proof_defined": proof_summary.get(
            "cross_repo_governance_contract_proof_defined"
        ),
        "y_star_gov_surfaces_inventoried_read_only": proof_summary.get(
            "y_star_gov_surfaces_inventoried_read_only"
        ),
        "gov_mcp_surfaces_inventoried_read_only": proof_summary.get(
            "gov_mcp_surfaces_inventoried_read_only"
        ),
        "y_star_gov_repo_present": proof_summary.get("y_star_gov_repo_present"),
        "gov_mcp_repo_present": proof_summary.get("gov_mcp_repo_present"),
        "y_star_gov_scanned_files_count": proof_summary.get("y_star_gov_scanned_files_count"),
        "gov_mcp_scanned_files_count": proof_summary.get("gov_mcp_scanned_files_count"),
        "behavior_y_star_mapped_to_governance_contract": readiness_summary.get(
            "behavior_y_star_mapped_to_governance_contract"
        ),
        "pre_u_candidates_mapped_to_validator_expectations": readiness_summary.get(
            "pre_u_candidates_mapped_to_validator_expectations"
        ),
        "cieu_fixtures_mapped_to_prediction_delta_expectations": readiness_summary.get(
            "cieu_fixtures_mapped_to_prediction_delta_expectations"
        ),
        "gov_mcp_boundary_mapped": readiness_summary.get("gov_mcp_boundary_mapped"),
        "non_bypass_invariants_defined": readiness_summary.get("non_bypass_invariants_defined"),
        "bypass_risks_identified": readiness_summary.get("bypass_risks_identified"),
        "labs_kernel_responsibility_boundary_defined": readiness_summary.get(
            "labs_kernel_responsibility_boundary_defined"
        ),
        "ystar_company_is_not_canonical_governance_kernel": alignment_summary.get(
            "ystar_company_is_not_canonical_governance_kernel"
        ),
        "no_non_ystar_company_repo_modified": proof_summary.get("non_ystar_company_repo_modified") is False,
        "no_mcp_server_or_tool_executed": proof_summary.get("mcp_server_or_tool_executed") is False,
        "mcp_non_bypass_invariants_defined": governed_mcp_summary.get(
            "mcp_non_bypass_invariants_defined"
        ),
        "required_gate_sequence_defined": non_bypass_summary.get("required_gate_sequence_defined"),
        "ready_for_l5_6_governed_mcp_dry_run_adapter": readiness_summary.get(
            "ready_for_l5_6_governed_mcp_dry_run_adapter"
        ),
        "ready_for_controlled_canonical_learning_design": readiness_summary.get(
            "ready_for_controlled_canonical_learning_design"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "y_star_gov_modification_enabled": readiness_summary.get("y_star_gov_modification_enabled"),
        "gov_mcp_modification_enabled": readiness_summary.get("gov_mcp_modification_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_contract_summary": "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
        "generated_y_star_gov_surface_summary": "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
        "generated_alignment_summary": "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
        "generated_gov_mcp_surface_summary": "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
        "generated_governed_mcp_interface_summary": "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
        "generated_non_bypass_summary": "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
        "generated_readiness": "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
        "warning": (
            "L5.5 is a read-only boundary proof. ystar-company is not a governance kernel, "
            "Y-star-gov and gov-mcp were not modified, and MCP tools were not executed."
        ),
    }


def build_governed_mcp_adapter_summary(
    adapter_summary: dict[str, Any] | None,
    intent_summary: dict[str, Any] | None,
    pre_u_summary: dict[str, Any] | None,
    decision_summary: dict[str, Any] | None,
    bridge_summary: dict[str, Any] | None,
    call_summary: dict[str, Any] | None,
    receipt_summary: dict[str, Any] | None,
    residual_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.governed_mcp_adapter_summary",
            "schema_version": "v0",
            "l5_6_governed_mcp_dry_run_adapter_defined": False,
            "ready_for_l5_7_controlled_canonical_learning_design": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Governed MCP dry-run adapter has not been generated yet.",
        }
    adapter_summary = adapter_summary or {}
    intent_summary = intent_summary or {}
    pre_u_summary = pre_u_summary or {}
    decision_summary = decision_summary or {}
    bridge_summary = bridge_summary or {}
    call_summary = call_summary or {}
    receipt_summary = receipt_summary or {}
    residual_summary = residual_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.governed_mcp_adapter_summary",
        "schema_version": "v0",
        "l5_6_governed_mcp_dry_run_adapter_defined": adapter_summary.get(
            "l5_6_governed_mcp_dry_run_adapter_defined"
        ),
        "behavior_y_star_loaded": readiness_summary.get("behavior_y_star_loaded"),
        "mcp_request_intent_generated": intent_summary.get("mcp_request_intent_generated"),
        "mcp_pre_u_packet_candidate_generated": pre_u_summary.get(
            "mcp_pre_u_packet_candidate_generated"
        ),
        "dry_run_governance_decision_envelope_generated": decision_summary.get(
            "governance_decision_envelope_generated"
        ),
        "bridge_authorization_receipt_generated": bridge_summary.get("bridge_receipt_generated"),
        "governed_mcp_call_candidate_generated": call_summary.get(
            "governed_mcp_call_candidate_generated"
        ),
        "real_mcp_execution_blocked": readiness_summary.get("real_mcp_execution_blocked"),
        "mcp_dry_run_receipt_generated": receipt_summary.get("mcp_dry_run_receipt_generated"),
        "mcp_cieu_like_event_generated": receipt_summary.get("mcp_cieu_event_fixture_generated"),
        "mcp_residual_delta_generated": residual_summary.get("mcp_residual_delta_generated"),
        "review_only_mcp_learning_candidate_generated": residual_summary.get(
            "mcp_learning_candidate_generated"
        ),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "mcp_server_not_started": readiness_summary.get("mcp_server_not_started"),
        "mcp_tool_not_executed": readiness_summary.get("mcp_tool_not_executed"),
        "mcp_resource_not_mutated": readiness_summary.get("mcp_resource_not_mutated"),
        "ready_for_l5_7_controlled_canonical_learning_design": readiness_summary.get(
            "ready_for_l5_7_controlled_canonical_learning_design"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "y_star_gov_modification_enabled": readiness_summary.get("y_star_gov_modification_enabled"),
        "gov_mcp_modification_enabled": readiness_summary.get("gov_mcp_modification_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "mcp_resource_mutation_enabled": readiness_summary.get("mcp_resource_mutation_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_adapter_summary": "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
        "generated_intent_summary": "mcp_request_intent_projection/mcp_request_intent_summary.json",
        "generated_pre_u_summary": "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
        "generated_decision_summary": "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
        "generated_bridge_summary": "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
        "generated_call_summary": "governed_mcp_call_candidate/governed_mcp_call_summary.json",
        "generated_receipt_summary": "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
        "generated_residual_summary": "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
        "generated_readiness": "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
        "warning": (
            "L5.6 proves a governed MCP dry-run adapter boundary only. gov-mcp was not run, "
            "MCP tools/resources were not executed or mutated, and Y-star-gov/gov-mcp remain unmodified."
        ),
    }


def build_controlled_canonical_learning_summary(
    design_summary: dict[str, Any] | None,
    invariant_summary: dict[str, Any] | None,
    target_summary: dict[str, Any] | None,
    evidence_summary: dict[str, Any] | None,
    gate_summary: dict[str, Any] | None,
    package_summary: dict[str, Any] | None,
    patch_summary: dict[str, Any] | None,
    rollback_summary: dict[str, Any] | None,
    validation_summary: dict[str, Any] | None,
    promotion_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.controlled_canonical_learning_summary",
            "schema_version": "v0",
            "l5_7_controlled_canonical_learning_design_defined": False,
            "ready_for_l5_8_approved_canonical_update_sandbox": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Controlled canonical learning design has not been generated yet.",
        }
    design_summary = design_summary or {}
    invariant_summary = invariant_summary or {}
    target_summary = target_summary or {}
    evidence_summary = evidence_summary or {}
    gate_summary = gate_summary or {}
    package_summary = package_summary or {}
    patch_summary = patch_summary or {}
    rollback_summary = rollback_summary or {}
    validation_summary = validation_summary or {}
    promotion_summary = promotion_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.controlled_canonical_learning_summary",
        "schema_version": "v0",
        "l5_7_controlled_canonical_learning_design_defined": design_summary.get(
            "l5_7_controlled_canonical_learning_design_defined"
        ),
        "y_star_non_mutation_invariant_defined": invariant_summary.get(
            "y_star_non_mutation_invariant_defined"
        ),
        "canonical_learning_target_registry_generated": target_summary.get(
            "canonical_learning_target_registry_generated"
        ),
        "promotion_evidence_bundle_generated": evidence_summary.get(
            "promotion_evidence_bundle_generated"
        ),
        "promotion_eligibility_gate_generated": gate_summary.get(
            "promotion_eligibility_gate_generated"
        ),
        "canonical_update_package_candidate_generated": package_summary.get(
            "canonical_update_package_candidate_generated"
        ),
        "versioned_patch_plan_generated": patch_summary.get("versioned_patch_plan_generated"),
        "rollback_audit_plan_generated": rollback_summary.get("rollback_plan_generated")
        and rollback_summary.get("audit_lineage_record_generated"),
        "post_promotion_validation_plan_generated": validation_summary.get(
            "post_promotion_validation_plan_generated"
        ),
        "dry_run_promotion_fixture_generated": promotion_summary.get(
            "dry_run_promotion_fixture_generated"
        ),
        "candidate_approved": readiness_summary.get("candidate_approved"),
        "candidate_applied": readiness_summary.get("candidate_applied"),
        "canonical_policy_mutation_performed": readiness_summary.get(
            "canonical_policy_mutation_performed"
        ),
        "canonical_update_application_performed": readiness_summary.get(
            "canonical_update_application_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "strategy_mutation_performed": readiness_summary.get("strategy_mutation_performed"),
        "y_star_direct_mutation_performed": readiness_summary.get(
            "y_star_direct_mutation_performed"
        ),
        "actual_canonical_application_blocked": readiness_summary.get(
            "actual_canonical_application_blocked"
        ),
        "candidate_approval_blocked": readiness_summary.get("candidate_approval_blocked"),
        "brain_writeback_blocked": readiness_summary.get("brain_writeback_blocked"),
        "memory_ingestion_blocked": readiness_summary.get("memory_ingestion_blocked"),
        "y_star_direct_mutation_blocked": readiness_summary.get("y_star_direct_mutation_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "ready_for_l5_8_approved_canonical_update_sandbox": readiness_summary.get(
            "ready_for_l5_8_approved_canonical_update_sandbox"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "canonical_policy_mutation_enabled": readiness_summary.get(
            "canonical_policy_mutation_enabled"
        ),
        "canonical_update_application_enabled": readiness_summary.get(
            "canonical_update_application_enabled"
        ),
        "y_star_direct_mutation_enabled": readiness_summary.get(
            "y_star_direct_mutation_enabled"
        ),
        "y_star_gov_modification_enabled": readiness_summary.get("y_star_gov_modification_enabled"),
        "gov_mcp_modification_enabled": readiness_summary.get("gov_mcp_modification_enabled"),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_design_summary": "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
        "generated_invariant_summary": "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
        "generated_target_summary": "canonical_learning_target_registry/canonical_learning_target_summary.json",
        "generated_evidence_summary": "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
        "generated_gate_summary": "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
        "generated_package_summary": "canonical_update_package_candidate/canonical_update_package_summary.json",
        "generated_patch_summary": "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
        "generated_rollback_summary": "rollback_and_audit_lineage/rollback_audit_summary.json",
        "generated_validation_summary": "post_promotion_validation_plan/post_promotion_validation_summary.json",
        "generated_promotion_summary": "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
        "generated_readiness": "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
        "warning": (
            "L5.7 defines controlled canonical learning promotion architecture only. "
            "Candidates remain unapproved and unapplied; canonical policy, brain, memory, "
            "strategy, Y*, Y-star-gov, and gov-mcp remain unmodified."
        ),
    }


def build_approved_sandbox_update_summary(
    sandbox_summary: dict[str, Any] | None,
    approval_summary: dict[str, Any] | None,
    baseline_summary: dict[str, Any] | None,
    patch_summary: dict[str, Any] | None,
    validation_summary: dict[str, Any] | None,
    reprojection_summary: dict[str, Any] | None,
    cieu_summary: dict[str, Any] | None,
    rollback_summary: dict[str, Any] | None,
    effect_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.approved_sandbox_update_summary",
            "schema_version": "v0",
            "l5_8_approved_canonical_update_sandbox_defined": False,
            "ready_for_l5_9_real_approval_workflow_boundary": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Approved canonical update sandbox has not been generated yet.",
        }
    sandbox_summary = sandbox_summary or {}
    approval_summary = approval_summary or {}
    baseline_summary = baseline_summary or {}
    patch_summary = patch_summary or {}
    validation_summary = validation_summary or {}
    reprojection_summary = reprojection_summary or {}
    cieu_summary = cieu_summary or {}
    rollback_summary = rollback_summary or {}
    effect_summary = effect_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.approved_sandbox_update_summary",
        "schema_version": "v0",
        "l5_8_approved_canonical_update_sandbox_defined": sandbox_summary.get(
            "l5_8_approved_canonical_update_sandbox_defined"
        ),
        "sandbox_approval_fixture_generated": approval_summary.get(
            "sandbox_approval_fixture_generated"
        ),
        "sandbox_application_approved": approval_summary.get("sandbox_application_approved"),
        "real_application_approved": approval_summary.get("real_application_approved"),
        "candidate_real_approved": approval_summary.get("candidate_real_approved"),
        "sandbox_baseline_generated": baseline_summary.get(
            "sandbox_canonical_baseline_generated"
        ),
        "sandbox_patch_applied": patch_summary.get("sandbox_patch_applied"),
        "real_canonical_state_unchanged": readiness_summary.get(
            "real_canonical_state_unchanged"
        ),
        "y_star_non_mutation_invariant_preserved": readiness_summary.get(
            "y_star_non_mutation_invariant_preserved"
        ),
        "sandbox_post_update_validation_generated": validation_summary.get(
            "sandbox_post_update_validation_generated"
        ),
        "sandbox_post_update_validation_passed": validation_summary.get(
            "sandbox_post_update_validation_passed"
        ),
        "sandbox_behavior_y_star_reprojection_generated": reprojection_summary.get(
            "sandbox_behavior_y_star_reprojection_generated"
        ),
        "sandbox_governed_mcp_preview_generated": reprojection_summary.get(
            "sandbox_governed_mcp_preview_generated"
        ),
        "sandbox_update_cieu_like_fixture_generated": cieu_summary.get(
            "sandbox_update_cieu_like_fixture_generated"
        ),
        "sandbox_update_residual_delta_generated": cieu_summary.get(
            "sandbox_update_residual_delta_generated"
        ),
        "sandbox_rollback_validation_generated": rollback_summary.get(
            "sandbox_rollback_performed"
        ),
        "rollback_restored_baseline": rollback_summary.get("rollback_restored_baseline"),
        "original_vs_sandbox_vs_rollback_comparison_generated": readiness_summary.get(
            "original_sandbox_rollback_comparison_generated"
        ),
        "sandbox_update_effect_class": effect_summary.get("effect_class"),
        "previous_residual_influenced_sandbox_projection": effect_summary.get(
            "previous_residual_influenced_sandbox_projection"
        ),
        "real_candidate_approved": readiness_summary.get("real_candidate_approved"),
        "real_candidate_applied": readiness_summary.get("real_candidate_applied"),
        "real_canonical_policy_mutation_performed": readiness_summary.get(
            "real_canonical_policy_mutation_performed"
        ),
        "real_canonical_update_application_performed": readiness_summary.get(
            "real_canonical_update_application_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "strategy_mutation_performed": readiness_summary.get("strategy_mutation_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_9_real_approval_workflow_boundary": readiness_summary.get(
            "ready_for_l5_9_real_approval_workflow_boundary"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_sandbox_summary": "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
        "generated_approval_summary": "sandbox_approval_fixture/sandbox_approval_summary.json",
        "generated_baseline_summary": "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
        "generated_patch_summary": "sandbox_patch_application/sandbox_patch_application_summary.json",
        "generated_validation_summary": "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
        "generated_reprojection_summary": "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
        "generated_cieu_summary": "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
        "generated_rollback_summary": "sandbox_rollback_validation/sandbox_rollback_summary.json",
        "generated_effect_summary": "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
        "generated_readiness": "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
        "warning": (
            "L5.8 is sandbox-only. Sandbox approval and patch application are generated "
            "artifacts only; real candidate approval, real canonical mutation, writeback, "
            "direct Y* mutation, MCP execution, and live execution remain blocked."
        ),
    }


def build_real_approval_workflow_summary(
    workflow_summary: dict[str, Any] | None,
    authority_summary: dict[str, Any] | None,
    evidence_summary: dict[str, Any] | None,
    record_summary: dict[str, Any] | None,
    decision_summary: dict[str, Any] | None,
    validity_summary: dict[str, Any] | None,
    snapshot_summary: dict[str, Any] | None,
    boundary_summary: dict[str, Any] | None,
    preflight_summary: dict[str, Any] | None,
    runbook_summary: dict[str, Any] | None,
    audit_summary: dict[str, Any] | None,
    readiness_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    if not readiness_summary:
        return {
            "schema_name": "ystar.console_read_model.generated.real_approval_workflow_summary",
            "schema_version": "v0",
            "l5_9_real_approval_workflow_boundary_defined": False,
            "ready_for_l5_10_controlled_approval_record_sandbox": False,
            "ready_for_l6_revenue_opportunity_discovery": False,
            "warning": "Real approval workflow boundary has not been generated yet.",
        }
    workflow_summary = workflow_summary or {}
    authority_summary = authority_summary or {}
    evidence_summary = evidence_summary or {}
    record_summary = record_summary or {}
    decision_summary = decision_summary or {}
    validity_summary = validity_summary or {}
    snapshot_summary = snapshot_summary or {}
    boundary_summary = boundary_summary or {}
    preflight_summary = preflight_summary or {}
    runbook_summary = runbook_summary or {}
    audit_summary = audit_summary or {}
    return {
        "schema_name": "ystar.console_read_model.generated.real_approval_workflow_summary",
        "schema_version": "v0",
        "l5_9_real_approval_workflow_boundary_defined": workflow_summary.get(
            "l5_9_real_approval_workflow_boundary_defined"
        ),
        "approval_authority_model_generated": authority_summary.get(
            "approval_authority_model_generated"
        ),
        "approval_evidence_dossier_generated": evidence_summary.get(
            "approval_evidence_dossier_generated"
        ),
        "durable_approval_record_contract_generated": record_summary.get(
            "durable_approval_record_contract_generated"
        ),
        "approval_decision_packet_fixture_generated": decision_summary.get(
            "approval_decision_packet_fixture_generated"
        ),
        "validity_revocation_policy_generated": validity_summary.get(
            "validity_revocation_policy_generated"
        ),
        "pre_application_snapshot_policy_generated": snapshot_summary.get(
            "pre_application_snapshot_policy_generated"
        ),
        "real_application_boundary_gate_generated": boundary_summary.get(
            "real_application_boundary_gate_generated"
        ),
        "post_approval_preflight_validation_plan_generated": preflight_summary.get(
            "post_approval_preflight_validation_defined"
        ),
        "manual_approval_runbook_generated": runbook_summary.get(
            "manual_approval_runbook_generated"
        ),
        "approval_workflow_cieu_like_fixture_generated": audit_summary.get(
            "approval_workflow_cieu_like_fixture_generated"
        ),
        "real_approval_granted": readiness_summary.get("real_approval_granted"),
        "real_application_authorized": readiness_summary.get("real_application_authorized"),
        "approval_record_created_as_durable_record": readiness_summary.get(
            "approval_record_created_as_durable_record"
        ),
        "durable_approval_record_written": readiness_summary.get(
            "durable_approval_record_written"
        ),
        "durable_db_write_performed": readiness_summary.get("durable_db_write_performed"),
        "real_canonical_policy_mutation_performed": readiness_summary.get(
            "real_canonical_policy_mutation_performed"
        ),
        "real_canonical_update_application_performed": readiness_summary.get(
            "real_canonical_update_application_performed"
        ),
        "brain_writeback_performed": readiness_summary.get("brain_writeback_performed"),
        "memory_ingestion_performed": readiness_summary.get("memory_ingestion_performed"),
        "strategy_mutation_performed": readiness_summary.get("strategy_mutation_performed"),
        "direct_y_star_mutation_performed": readiness_summary.get(
            "direct_y_star_mutation_performed"
        ),
        "real_approval_still_blocked": readiness_summary.get("real_approval_still_blocked"),
        "real_application_still_blocked": readiness_summary.get(
            "real_application_still_blocked"
        ),
        "durable_approval_persistence_still_blocked": readiness_summary.get(
            "durable_approval_persistence_still_blocked"
        ),
        "brain_writeback_still_blocked": readiness_summary.get("brain_writeback_still_blocked"),
        "memory_ingestion_still_blocked": readiness_summary.get(
            "memory_ingestion_still_blocked"
        ),
        "y_star_direct_mutation_still_blocked": readiness_summary.get(
            "y_star_direct_mutation_still_blocked"
        ),
        "mcp_execution_still_blocked": readiness_summary.get("mcp_execution_still_blocked"),
        "y_star_gov_unmodified": readiness_summary.get("y_star_gov_unmodified"),
        "gov_mcp_unmodified": readiness_summary.get("gov_mcp_unmodified"),
        "live_execution_enabled": readiness_summary.get("live_execution_enabled"),
        "behavior_execution_enabled": readiness_summary.get("behavior_execution_enabled"),
        "external_action_enabled": readiness_summary.get("external_action_enabled"),
        "network_enabled": readiness_summary.get("network_enabled"),
        "scheduler_enabled": readiness_summary.get("scheduler_enabled"),
        "daemon_enabled": readiness_summary.get("daemon_enabled"),
        "mcp_server_execution_enabled": readiness_summary.get("mcp_server_execution_enabled"),
        "mcp_tool_execution_enabled": readiness_summary.get("mcp_tool_execution_enabled"),
        "cieu_persistence_enabled": readiness_summary.get("cieu_persistence_enabled"),
        "durable_approval_persistence_enabled": readiness_summary.get(
            "durable_approval_persistence_enabled"
        ),
        "brain_writeback_enabled": readiness_summary.get("brain_writeback_enabled"),
        "memory_ingestion_enabled": readiness_summary.get("memory_ingestion_enabled"),
        "strategy_mutation_enabled": readiness_summary.get("strategy_mutation_enabled"),
        "candidate_auto_approval_enabled": readiness_summary.get("candidate_auto_approval_enabled"),
        "real_candidate_approval_enabled": readiness_summary.get(
            "real_candidate_approval_enabled"
        ),
        "real_canonical_policy_mutation_enabled": readiness_summary.get(
            "real_canonical_policy_mutation_enabled"
        ),
        "real_canonical_update_application_enabled": readiness_summary.get(
            "real_canonical_update_application_enabled"
        ),
        "real_y_star_direct_mutation_enabled": readiness_summary.get(
            "real_y_star_direct_mutation_enabled"
        ),
        "semantic_truth_scoring_enabled": readiness_summary.get("semantic_truth_scoring_enabled"),
        "raw_runtime_artifact_reading_enabled": readiness_summary.get(
            "raw_runtime_artifact_reading_enabled"
        ),
        "revenue_opportunity_discovery_enabled": readiness_summary.get(
            "revenue_opportunity_discovery_enabled"
        ),
        "ready_for_l5_10_controlled_approval_record_sandbox": readiness_summary.get(
            "ready_for_l5_10_controlled_approval_record_sandbox"
        ),
        "ready_for_l6_revenue_opportunity_discovery": readiness_summary.get(
            "ready_for_l6_revenue_opportunity_discovery"
        ),
        "next_required_milestone": readiness_summary.get("next_required_milestone"),
        "generated_workflow_summary": "real_approval_workflow_boundary/real_approval_workflow_summary.json",
        "generated_authority_summary": "approval_authority_model/approval_authority_summary.json",
        "generated_evidence_summary": "approval_evidence_dossier/approval_evidence_summary.json",
        "generated_record_summary": "durable_approval_record_contract/approval_record_summary.json",
        "generated_decision_summary": "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
        "generated_validity_summary": "approval_validity_revocation_policy/approval_validity_summary.json",
        "generated_snapshot_summary": "pre_application_snapshot_policy/snapshot_policy_summary.json",
        "generated_boundary_summary": "real_application_boundary_gate/real_application_boundary_summary.json",
        "generated_preflight_summary": "post_approval_preflight_validation/post_approval_preflight_summary.json",
        "generated_runbook_summary": "manual_approval_runbook/manual_approval_runbook_summary.json",
        "generated_audit_summary": "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
        "generated_readiness": "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
        "warning": (
            "L5.9 defines the real approval workflow boundary only. No real approval is "
            "granted, no durable approval record is written, and no real canonical update "
            "application is authorized."
        ),
    }


def build() -> tuple[list[str], list[str], list[str], list[str]]:
    files_read: list[str] = []
    generated_files: list[str] = []
    warnings: list[str] = []

    team_model = load_json("console_read_model/team_brain_read_model.json", files_read)
    agent_cards = load_json("console_read_model/agent_cards.json", files_read)
    capability_matrix = load_json("console_read_model/capability_matrix.json", files_read)
    team_capsules = load_json("agent_brains/team_capsule_map.json", files_read)
    quarantine_index = load_json("runtime_artifact_quarantine/quarantine_index.json", files_read)
    quarantine_manifest = load_json(
        "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
        files_read,
    )
    safe_mining_candidates = load_json(
        "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
        files_read,
    )
    review_queue = load_json(
        "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json",
        files_read,
    )
    disposition_index = load_json(
        "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
        files_read,
    )
    evidence_scores = load_json(
        "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
        files_read,
    )
    decision_stub = load_json(
        "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
        files_read,
    )
    hint_routing = load_json(
        "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
        files_read,
    )
    governance_decision_snapshot = load_json(
        "labs_governance_bridge/generated/governance_decision_snapshot.json",
        files_read,
    )
    pre_u_governance_decisions = load_json(
        "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json",
        files_read,
    )
    labs_acceptance_report = load_optional_json(
        "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
        files_read,
    )
    cross_repo_generated_summary = load_optional_json(
        "cross_repo_alignment/generated/cross_repo_alignment_summary.json",
        files_read,
    )
    live_readiness_report = load_optional_json(
        "labs_live_readiness/generated/live_readiness_report.json",
        files_read,
    )
    live_boundary_generated_summary = load_optional_json(
        "labs_live_boundary/generated/live_boundary_summary.json",
        files_read,
    )
    cieu_boundary_generated_summary = load_optional_json(
        "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json",
        files_read,
    )
    autonomy_generated_summary = load_optional_json(
        "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
        files_read,
    )
    autonomous_cycle_generated_summary = load_optional_json(
        "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
        files_read,
    )
    legacy_triage_generated_summary = load_optional_json(
        "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
        files_read,
    )
    observation_loop_generated_summary = load_optional_json(
        "governed_observation_loop/generated/governed_observation_loop_summary.json",
        files_read,
    )
    readonly_tool_generated_summary = load_optional_json(
        "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
        files_read,
    )
    tool_bridge_generated_summary = load_optional_json(
        "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
        files_read,
    )
    work_proposal_generated_summary = load_optional_json(
        "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
        files_read,
    )
    dashboard_refresh_generated_summary = load_optional_json(
        "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
        files_read,
    )
    recurring_loop_generated_summary = load_optional_json(
        "recurring_observation_loop_contract/generated/recurring_loop_readiness_summary.json",
        files_read,
    )
    manual_tick_generated_summary = load_optional_json(
        "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
        files_read,
    )
    field_functional_generated_summary = load_optional_json(
        "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
        files_read,
    )
    mission_projection_generated_summary = load_optional_json(
        "mission_field_projection_contract/projection_contract_summary.json",
        files_read,
    )
    field_projection_operator_summary = load_optional_json(
        "field_functional_auto_projection_core/field_projection_operator_summary.json",
        files_read,
    )
    field_projection_generated_summary = load_optional_json(
        "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
        files_read,
    )
    field_projection_pre_u_summary = load_optional_json(
        "behavior_y_star_to_pre_u_candidate/pre_u_candidate_summary.json",
        files_read,
    )
    field_projection_residual_summary = load_optional_json(
        "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
        files_read,
    )
    field_projection_readiness_summary = load_optional_json(
        "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
        files_read,
    )
    projection_cycle_generated_summary = load_optional_json(
        "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
        files_read,
    )
    projection_cycle_work_summary = load_optional_json(
        "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
        files_read,
    )
    projection_cycle_pre_u_summary = load_optional_json(
        "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
        files_read,
    )
    projection_cycle_result_summary = load_optional_json(
        "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
        files_read,
    )
    projection_cycle_residual_summary = load_optional_json(
        "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
        files_read,
    )
    projection_cycle_learning_summary = load_optional_json(
        "projection_checked_learning_review_queue/projection_learning_review_summary.json",
        files_read,
    )
    projection_cycle_readiness_summary = load_optional_json(
        "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
        files_read,
    )
    shadow_learning_loop_summary = load_optional_json(
        "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
        files_read,
    )
    shadow_learning_review_summary = load_optional_json(
        "residual_review_gate/residual_review_summary.json",
        files_read,
    )
    shadow_learning_target_summary = load_optional_json(
        "learning_target_classifier/learning_target_summary.json",
        files_read,
    )
    shadow_learning_update_summary = load_optional_json(
        "projection_policy_update_candidate/projection_policy_update_summary.json",
        files_read,
    )
    shadow_learning_patch_summary = load_optional_json(
        "shadow_projection_policy_patch/shadow_patch_summary.json",
        files_read,
    )
    shadow_learning_reprojection_summary = load_optional_json(
        "shadow_reprojection_preview/shadow_reprojection_summary.json",
        files_read,
    )
    shadow_learning_shadow_cycle_summary = load_optional_json(
        "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
        files_read,
    )
    shadow_learning_shadow_residual_summary = load_optional_json(
        "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
        files_read,
    )
    shadow_learning_effect_summary = load_optional_json(
        "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json",
        files_read,
    )
    shadow_learning_integrated_cieu_summary = load_optional_json(
        "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
        files_read,
    )
    shadow_learning_readiness_summary = load_optional_json(
        "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
        files_read,
    )
    cross_repo_governance_proof_summary = load_optional_json(
        "cross_repo_governance_contract_proof/cross_repo_contract_proof_summary.json",
        files_read,
    )
    cross_repo_governance_y_star_gov_summary = load_optional_json(
        "y_star_gov_contract_surface_inventory/y_star_gov_surface_summary.json",
        files_read,
    )
    cross_repo_governance_alignment_summary = load_optional_json(
        "ystar_company_to_y_star_gov_alignment/ystar_company_to_y_star_gov_alignment_summary.json",
        files_read,
    )
    cross_repo_governance_gov_mcp_summary = load_optional_json(
        "gov_mcp_boundary_inventory/gov_mcp_surface_summary.json",
        files_read,
    )
    cross_repo_governance_interface_summary = load_optional_json(
        "governed_mcp_interface_contract/governed_mcp_interface_summary.json",
        files_read,
    )
    cross_repo_governance_non_bypass_summary = load_optional_json(
        "cross_repo_non_bypass_proof/cross_repo_non_bypass_summary.json",
        files_read,
    )
    cross_repo_governance_readiness_summary = load_optional_json(
        "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json",
        files_read,
    )
    governed_mcp_adapter_generated_summary = load_optional_json(
        "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
        files_read,
    )
    governed_mcp_adapter_intent_summary = load_optional_json(
        "mcp_request_intent_projection/mcp_request_intent_summary.json",
        files_read,
    )
    governed_mcp_adapter_pre_u_summary = load_optional_json(
        "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
        files_read,
    )
    governed_mcp_adapter_decision_summary = load_optional_json(
        "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
        files_read,
    )
    governed_mcp_adapter_bridge_summary = load_optional_json(
        "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
        files_read,
    )
    governed_mcp_adapter_call_summary = load_optional_json(
        "governed_mcp_call_candidate/governed_mcp_call_summary.json",
        files_read,
    )
    governed_mcp_adapter_receipt_summary = load_optional_json(
        "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
        files_read,
    )
    governed_mcp_adapter_residual_summary = load_optional_json(
        "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
        files_read,
    )
    governed_mcp_adapter_readiness_summary = load_optional_json(
        "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
        files_read,
    )
    controlled_canonical_learning_design_summary = load_optional_json(
        "controlled_canonical_learning_design/controlled_canonical_learning_summary.json",
        files_read,
    )
    controlled_canonical_learning_invariant_summary = load_optional_json(
        "y_star_non_mutation_invariant/y_star_non_mutation_summary.json",
        files_read,
    )
    controlled_canonical_learning_target_summary = load_optional_json(
        "canonical_learning_target_registry/canonical_learning_target_summary.json",
        files_read,
    )
    controlled_canonical_learning_evidence_summary = load_optional_json(
        "canonical_promotion_evidence_bundle/evidence_bundle_summary.json",
        files_read,
    )
    controlled_canonical_learning_gate_summary = load_optional_json(
        "canonical_promotion_eligibility_gate/canonical_promotion_gate_summary.json",
        files_read,
    )
    controlled_canonical_learning_package_summary = load_optional_json(
        "canonical_update_package_candidate/canonical_update_package_summary.json",
        files_read,
    )
    controlled_canonical_learning_patch_summary = load_optional_json(
        "versioned_canonical_patch_plan/versioned_patch_plan_summary.json",
        files_read,
    )
    controlled_canonical_learning_rollback_summary = load_optional_json(
        "rollback_and_audit_lineage/rollback_audit_summary.json",
        files_read,
    )
    controlled_canonical_learning_validation_summary = load_optional_json(
        "post_promotion_validation_plan/post_promotion_validation_summary.json",
        files_read,
    )
    controlled_canonical_learning_promotion_summary = load_optional_json(
        "dry_run_promotion_decision_fixture/dry_run_promotion_summary.json",
        files_read,
    )
    controlled_canonical_learning_readiness_summary = load_optional_json(
        "controlled_canonical_learning_readiness/controlled_canonical_learning_readiness.json",
        files_read,
    )
    approved_sandbox_update_sandbox_summary = load_optional_json(
        "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
        files_read,
    )
    approved_sandbox_update_approval_summary = load_optional_json(
        "sandbox_approval_fixture/sandbox_approval_summary.json",
        files_read,
    )
    approved_sandbox_update_baseline_summary = load_optional_json(
        "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
        files_read,
    )
    approved_sandbox_update_patch_summary = load_optional_json(
        "sandbox_patch_application/sandbox_patch_application_summary.json",
        files_read,
    )
    approved_sandbox_update_validation_summary = load_optional_json(
        "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
        files_read,
    )
    approved_sandbox_update_reprojection_summary = load_optional_json(
        "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
        files_read,
    )
    approved_sandbox_update_cieu_summary = load_optional_json(
        "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
        files_read,
    )
    approved_sandbox_update_rollback_summary = load_optional_json(
        "sandbox_rollback_validation/sandbox_rollback_summary.json",
        files_read,
    )
    approved_sandbox_update_effect_summary = load_optional_json(
        "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
        files_read,
    )
    approved_sandbox_update_readiness_summary = load_optional_json(
        "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
        files_read,
    )
    real_approval_workflow_generated_summary = load_optional_json(
        "real_approval_workflow_boundary/real_approval_workflow_summary.json",
        files_read,
    )
    real_approval_workflow_authority_summary = load_optional_json(
        "approval_authority_model/approval_authority_summary.json",
        files_read,
    )
    real_approval_workflow_evidence_summary = load_optional_json(
        "approval_evidence_dossier/approval_evidence_summary.json",
        files_read,
    )
    real_approval_workflow_record_summary = load_optional_json(
        "durable_approval_record_contract/approval_record_summary.json",
        files_read,
    )
    real_approval_workflow_decision_summary = load_optional_json(
        "real_approval_decision_packet_fixture/real_approval_decision_summary.json",
        files_read,
    )
    real_approval_workflow_validity_summary = load_optional_json(
        "approval_validity_revocation_policy/approval_validity_summary.json",
        files_read,
    )
    real_approval_workflow_snapshot_summary = load_optional_json(
        "pre_application_snapshot_policy/snapshot_policy_summary.json",
        files_read,
    )
    real_approval_workflow_boundary_summary = load_optional_json(
        "real_application_boundary_gate/real_application_boundary_summary.json",
        files_read,
    )
    real_approval_workflow_preflight_summary = load_optional_json(
        "post_approval_preflight_validation/post_approval_preflight_summary.json",
        files_read,
    )
    real_approval_workflow_runbook_summary = load_optional_json(
        "manual_approval_runbook/manual_approval_runbook_summary.json",
        files_read,
    )
    real_approval_workflow_audit_summary = load_optional_json(
        "approval_workflow_cieu_audit_fixture/approval_workflow_audit_summary.json",
        files_read,
    )
    real_approval_workflow_readiness_summary = load_optional_json(
        "real_approval_workflow_readiness/real_approval_workflow_readiness.json",
        files_read,
    )
    quarantine_summary = build_quarantine_summary(quarantine_index, quarantine_manifest)
    safe_mining_summary = build_safe_mining_summary(safe_mining_candidates)
    review_queue_summary = build_review_queue_summary(review_queue)
    disposition_summary = build_disposition_summary(disposition_index)
    evidence_review_summary = build_evidence_review_summary(evidence_scores, decision_stub, hint_routing)
    governance_bridge_summary = build_governance_bridge_summary(governance_decision_snapshot)
    pre_u_governance_summary = build_pre_u_governance_summary(pre_u_governance_decisions)
    labs_acceptance_summary = build_labs_acceptance_summary(labs_acceptance_report)
    cross_repo_alignment_summary = build_cross_repo_alignment_summary(cross_repo_generated_summary)
    live_readiness_summary = build_live_readiness_summary(live_readiness_report)
    live_boundary_summary = build_live_boundary_summary(live_boundary_generated_summary)
    cieu_boundary_summary = build_cieu_boundary_summary(cieu_boundary_generated_summary)
    autonomy_inventory_summary = build_autonomy_inventory_summary(autonomy_generated_summary)
    autonomous_cycle_summary = build_autonomous_cycle_summary(autonomous_cycle_generated_summary)
    legacy_triage_summary = build_legacy_triage_summary(legacy_triage_generated_summary)
    observation_loop_summary = build_observation_loop_summary(observation_loop_generated_summary)
    readonly_tool_summary = build_readonly_tool_summary(readonly_tool_generated_summary)
    tool_bridge_summary = build_tool_bridge_summary(tool_bridge_generated_summary)
    work_proposal_summary = build_work_proposal_summary(work_proposal_generated_summary)
    dashboard_refresh_summary = build_dashboard_refresh_summary(dashboard_refresh_generated_summary)
    recurring_loop_summary = build_recurring_loop_summary(recurring_loop_generated_summary)
    manual_tick_summary = build_manual_tick_summary(manual_tick_generated_summary)
    field_functional_summary = build_field_functional_summary(field_functional_generated_summary)
    mission_projection_summary = build_mission_projection_summary(
        mission_projection_generated_summary
    )
    field_projection_summary = build_field_projection_summary(
        field_projection_operator_summary,
        field_projection_generated_summary,
        field_projection_pre_u_summary,
        field_projection_residual_summary,
        field_projection_readiness_summary,
    )
    projection_cycle_summary = build_projection_cycle_summary(
        projection_cycle_generated_summary,
        projection_cycle_work_summary,
        projection_cycle_pre_u_summary,
        projection_cycle_result_summary,
        projection_cycle_residual_summary,
        projection_cycle_learning_summary,
        projection_cycle_readiness_summary,
    )
    shadow_learning_cycle_summary = build_shadow_learning_cycle_summary(
        shadow_learning_loop_summary,
        shadow_learning_review_summary,
        shadow_learning_target_summary,
        shadow_learning_update_summary,
        shadow_learning_patch_summary,
        shadow_learning_reprojection_summary,
        shadow_learning_shadow_cycle_summary,
        shadow_learning_shadow_residual_summary,
        shadow_learning_effect_summary,
        shadow_learning_integrated_cieu_summary,
        shadow_learning_readiness_summary,
    )
    cross_repo_governance_summary = build_cross_repo_governance_summary(
        cross_repo_governance_proof_summary,
        cross_repo_governance_y_star_gov_summary,
        cross_repo_governance_alignment_summary,
        cross_repo_governance_gov_mcp_summary,
        cross_repo_governance_interface_summary,
        cross_repo_governance_non_bypass_summary,
        cross_repo_governance_readiness_summary,
    )
    governed_mcp_adapter_summary = build_governed_mcp_adapter_summary(
        governed_mcp_adapter_generated_summary,
        governed_mcp_adapter_intent_summary,
        governed_mcp_adapter_pre_u_summary,
        governed_mcp_adapter_decision_summary,
        governed_mcp_adapter_bridge_summary,
        governed_mcp_adapter_call_summary,
        governed_mcp_adapter_receipt_summary,
        governed_mcp_adapter_residual_summary,
        governed_mcp_adapter_readiness_summary,
    )
    controlled_canonical_learning_summary = build_controlled_canonical_learning_summary(
        controlled_canonical_learning_design_summary,
        controlled_canonical_learning_invariant_summary,
        controlled_canonical_learning_target_summary,
        controlled_canonical_learning_evidence_summary,
        controlled_canonical_learning_gate_summary,
        controlled_canonical_learning_package_summary,
        controlled_canonical_learning_patch_summary,
        controlled_canonical_learning_rollback_summary,
        controlled_canonical_learning_validation_summary,
        controlled_canonical_learning_promotion_summary,
        controlled_canonical_learning_readiness_summary,
    )
    approved_sandbox_update_summary = build_approved_sandbox_update_summary(
        approved_sandbox_update_sandbox_summary,
        approved_sandbox_update_approval_summary,
        approved_sandbox_update_baseline_summary,
        approved_sandbox_update_patch_summary,
        approved_sandbox_update_validation_summary,
        approved_sandbox_update_reprojection_summary,
        approved_sandbox_update_cieu_summary,
        approved_sandbox_update_rollback_summary,
        approved_sandbox_update_effect_summary,
        approved_sandbox_update_readiness_summary,
    )
    real_approval_workflow_summary = build_real_approval_workflow_summary(
        real_approval_workflow_generated_summary,
        real_approval_workflow_authority_summary,
        real_approval_workflow_evidence_summary,
        real_approval_workflow_record_summary,
        real_approval_workflow_decision_summary,
        real_approval_workflow_validity_summary,
        real_approval_workflow_snapshot_summary,
        real_approval_workflow_boundary_summary,
        real_approval_workflow_preflight_summary,
        real_approval_workflow_runbook_summary,
        real_approval_workflow_audit_summary,
        real_approval_workflow_readiness_summary,
    )

    profiles = {
        "Aiden-CEO": load_json("agent_brains/Aiden-CEO/brain_profile.json", files_read),
        "Ethan-CTO": load_json("agent_brains/Ethan-CTO/brain_profile.json", files_read),
        "Samantha-Secretary": load_json("agent_brains/Samantha-Secretary/brain_profile.json", files_read),
    }

    ethan_execution = None
    ethan_execution_path = ROOT / "agent_brains/Ethan-CTO/execution_channels.json"
    if ethan_execution_path.exists():
        ethan_execution = load_json("agent_brains/Ethan-CTO/execution_channels.json", files_read)
    else:
        warnings.append("Ethan execution channel map not present.")

    cards_by_id = {card["card_id"]: card for card in agent_cards.get("cards", [])}
    agents = []
    for agent in team_model.get("agents", []):
        agent_id = agent["agent_id"]
        profile = profiles.get(agent_id, {})
        card = cards_by_id.get(agent_id, {})
        agents.append(
            {
                "agent_id": agent_id,
                "canonical_name": agent.get("canonical_name") or profile.get("canonical_name"),
                "role_type": agent.get("role_type") or profile.get("role_type"),
                "capsule_path": agent.get("capsule_path"),
                "readiness_level": agent.get("readiness_level"),
                "focus": agent.get("focus"),
                "card_status": card.get("status"),
                "capabilities": card.get("capabilities", []),
                "limitations": card.get("limitations", []),
                "next_actions": card.get("next_actions", []),
                "has_pre_u_packet": agent.get("has_pre_u_packet", False),
                "has_chain_review": agent.get("has_chain_review", False),
                "has_execution_channels": agent.get("has_execution_channels", False),
            }
        )

    if ethan_execution:
        warnings.append("Ethan execution channels are present as reference-only boundaries, not runtime launchers.")

    readiness = team_model.get("readiness", {})
    governance_summary = {
        "principle": "labs thinks; Y-star-gov judges; hook enforces; CIEU records and teaches; brain learns",
        "pre_u_packet_validator_spec": team_model.get("governance_interfaces", {}).get("pre_u_packet_validator_spec"),
        "boundary_docs": team_model.get("governance_interfaces", {}).get("boundary_docs"),
        "hook_role": team_model.get("governance_interfaces", {}).get("hook_role"),
        "cieu_role": team_model.get("governance_interfaces", {}).get("cieu_role"),
    }

    open_gaps = [
        "Static console loader exists; no frontend UI yet." if gap == "No static console loader." else gap
        for gap in team_model.get("open_gaps", [])
    ]
    if "Snapshot-only CLI exists; no interactive UI or live refresh yet." not in open_gaps:
        open_gaps.append("Snapshot-only CLI exists; no interactive UI or live refresh yet.")
    if "Runtime artifact quarantine is visible as a path-only summary; full artifact mining is not implemented." not in open_gaps:
        open_gaps.append("Runtime artifact quarantine is visible as a path-only summary; full artifact mining is not implemented.")
    if "Safe mining v0 produces candidate-only Markdown report snippets; no brain or CIEU ingestion exists." not in open_gaps:
        open_gaps.append("Safe mining v0 produces candidate-only Markdown report snippets; no brain or CIEU ingestion exists.")
    if "Candidate review queue exists, but no approval workflow or ingestion path exists." not in open_gaps:
        open_gaps.append("Candidate review queue exists, but no approval workflow or ingestion path exists.")
    if "Backlog disposition index exists, but evidence scoring and adapter extraction are not implemented." not in open_gaps:
        open_gaps.append("Backlog disposition index exists, but evidence scoring and adapter extraction are not implemented.")
    if "Evidence review pack exists, but semantic truth validation and decision application are not implemented." not in open_gaps:
        open_gaps.append("Evidence review pack exists, but semantic truth validation and decision application are not implemented.")
    if "Labs-Gov bridge exists as a dry-run snapshot only; no real hook integration exists." not in open_gaps:
        open_gaps.append("Labs-Gov bridge exists as a dry-run snapshot only; no real hook integration exists.")
    if "Pre-U generator exists for dry-run governance only; no runtime packet execution exists." not in open_gaps:
        open_gaps.append("Pre-U generator exists for dry-run governance only; no runtime packet execution exists.")
    if "Labs runtime acceptance exists for dry-run checks only; no real runtime execution is accepted." not in open_gaps:
        open_gaps.append("Labs runtime acceptance exists for dry-run checks only; no real runtime execution is accepted.")
    if "Cross-repo alignment exists for dry-run compatibility only; no CI or real hook enforcement exists." not in open_gaps:
        open_gaps.append("Cross-repo alignment exists for dry-run compatibility only; no CI or real hook enforcement exists.")
    if "Live readiness gate exists, but minimal live loop remains blocked until required gates exist." not in open_gaps:
        open_gaps.append("Live readiness gate exists, but minimal live loop remains blocked until required gates exist.")
    if "Live boundary harness exists as defined-disabled contracts only; no live execution is enabled." not in open_gaps:
        open_gaps.append("Live boundary harness exists as defined-disabled contracts only; no live execution is enabled.")
    if "CIEU runtime boundary exists as disabled event fixtures only; no CIEU persistence is enabled." not in open_gaps:
        open_gaps.append("CIEU runtime boundary exists as disabled event fixtures only; no CIEU persistence is enabled.")
    if "Company autonomy inventory exists, but governed action registry candidates are not live-enabled." not in open_gaps:
        open_gaps.append("Company autonomy inventory exists, but governed action registry candidates are not live-enabled.")
    if "Autonomous work cycle exists as a simulator only; no real action execution is implemented." not in open_gaps:
        open_gaps.append("Autonomous work cycle exists as a simulator only; no real action execution is implemented.")
    if "Legacy asset triage exists, but no absorption or wrapper application workflow exists." not in open_gaps:
        open_gaps.append("Legacy asset triage exists, but no absorption or wrapper application workflow exists.")
    if "Governed observation loop exists as one read-only tick; recurring wrapper execution is not implemented." not in open_gaps:
        open_gaps.append("Governed observation loop exists as one read-only tick; recurring wrapper execution is not implemented.")
    if "Governed read-only observation tool exists for local dry-run calls only; all invocations remain bridge-gated." not in open_gaps:
        open_gaps.append("Governed read-only observation tool exists for local dry-run calls only; all invocations remain bridge-gated.")
    if "Governed tool invocation bridge exists for local dry-run only; agent work proposal routing remains dry-run only." not in open_gaps:
        open_gaps.append("Governed tool invocation bridge exists for local dry-run only; agent work proposal routing remains dry-run only.")
    if "Agent-team work proposal routing feeds a manual dashboard refresh only; recurrence is not implemented yet." not in open_gaps:
        open_gaps.append("Agent-team work proposal routing feeds a manual dashboard refresh only; recurrence is not implemented yet.")
    if "Mission dashboard refresh loop exists as manual local dry-run only; governed recurrence is not implemented yet." not in open_gaps:
        open_gaps.append("Mission dashboard refresh loop exists as manual local dry-run only; governed recurrence is not implemented yet.")
    if "Recurring observation loop contract exists but recurrence, scheduler, daemon, and auto-run remain disabled." not in open_gaps:
        open_gaps.append("Recurring observation loop contract exists but recurrence, scheduler, daemon, and auto-run remain disabled.")
    if "Manual recurring observation tick runner exists for one-shot local ticks only; no scheduler, daemon, or recurrence is enabled." not in open_gaps:
        open_gaps.append("Manual recurring observation tick runner exists for one-shot local ticks only; no scheduler, daemon, or recurrence is enabled.")
    if "Field functional archaeology exists as a merge plan only; L5 projection harness is not implemented yet." not in open_gaps:
        open_gaps.append("Field functional archaeology exists as a merge plan only; L5 projection harness is not implemented yet.")
    if "Field functional auto-projection core exists as a dry-run projection core only; behavior execution remains disabled." not in open_gaps:
        open_gaps.append("Field functional auto-projection core exists as a dry-run projection core only; behavior execution remains disabled.")
    if "Integrated review-gated shadow learning cycle exists as shadow-only artifacts; controlled canonical learning is not implemented yet." not in open_gaps:
        open_gaps.append("Integrated review-gated shadow learning cycle exists as shadow-only artifacts; controlled canonical learning is not implemented yet.")
    if "Cross-repo governance contract proof exists as read-only boundary alignment; governed MCP dry-run adapter is implemented as dry-run only." not in open_gaps:
        open_gaps.append("Cross-repo governance contract proof exists as read-only boundary alignment; governed MCP dry-run adapter is implemented as dry-run only.")
    if "Controlled canonical learning design exists as a promotion dry-run only; approved canonical update sandbox now remains sandbox-only." not in open_gaps:
        open_gaps.append("Controlled canonical learning design exists as a promotion dry-run only; approved canonical update sandbox now remains sandbox-only.")
    if "Approved canonical update sandbox exists as generated sandbox-only artifacts; real approval workflow boundary is defined but no durable approval record sandbox exists yet." not in open_gaps:
        open_gaps.append("Approved canonical update sandbox exists as generated sandbox-only artifacts; real approval workflow boundary is defined but no durable approval record sandbox exists yet.")

    snapshot = {
        "schema_name": "ystar.console_read_model.generated.team_console_snapshot",
        "schema_version": "v0",
        "generated_by": "console_read_model/loader/build_team_console_snapshot.py",
        "source_files": files_read,
        "agents": agents,
        "capabilities": capability_matrix,
        "readiness": readiness,
        "governance_summary": governance_summary,
        "data_safety": team_model.get("data_safety", {}),
        "quarantine_summary": quarantine_summary,
        "safe_mining_summary": safe_mining_summary,
        "review_queue_summary": review_queue_summary,
        "artifact_disposition_summary": disposition_summary,
        "evidence_review_summary": evidence_review_summary,
        "governance_bridge_summary": governance_bridge_summary,
        "pre_u_governance_summary": pre_u_governance_summary,
        "labs_acceptance_summary": labs_acceptance_summary,
        "cross_repo_alignment_summary": cross_repo_alignment_summary,
        "live_readiness_summary": live_readiness_summary,
        "live_boundary_summary": live_boundary_summary,
        "cieu_boundary_summary": cieu_boundary_summary,
        "autonomy_inventory_summary": autonomy_inventory_summary,
        "autonomous_cycle_summary": autonomous_cycle_summary,
        "legacy_triage_summary": legacy_triage_summary,
        "observation_loop_summary": observation_loop_summary,
        "readonly_tool_summary": readonly_tool_summary,
        "tool_bridge_summary": tool_bridge_summary,
        "work_proposal_summary": work_proposal_summary,
        "dashboard_refresh_summary": dashboard_refresh_summary,
        "recurring_loop_summary": recurring_loop_summary,
        "manual_tick_summary": manual_tick_summary,
        "field_functional_summary": field_functional_summary,
        "mission_projection_summary": mission_projection_summary,
        "field_projection_summary": field_projection_summary,
        "projection_cycle_summary": projection_cycle_summary,
        "shadow_learning_cycle_summary": shadow_learning_cycle_summary,
        "cross_repo_governance_summary": cross_repo_governance_summary,
        "governed_mcp_adapter_summary": governed_mcp_adapter_summary,
        "controlled_canonical_learning_summary": controlled_canonical_learning_summary,
        "approved_sandbox_update_summary": approved_sandbox_update_summary,
        "real_approval_workflow_summary": real_approval_workflow_summary,
        "open_gaps": open_gaps,
        "warnings": warnings,
    }

    compiled_cards = {
        "schema_name": "ystar.console_read_model.generated.agent_cards_compiled",
        "schema_version": "v0",
        "source_files": [
            "console_read_model/agent_cards.json",
            "agent_brains/team_capsule_map.json",
        ],
        "cards": [
            {
                **card,
                "capsule_map_entry": next(
                    (entry for entry in team_capsules.get("agents", []) if entry.get("agent_id") == card.get("card_id")),
                    None,
                ),
            }
            for card in agent_cards.get("cards", [])
        ],
    }

    readiness_summary = {
        "schema_name": "ystar.console_read_model.generated.readiness_summary",
        "schema_version": "v0",
        "ready_now": [
            "reference docs",
            "team read model",
            "capsule schema",
            "Aiden capsule chain",
            "Ethan/Samantha base capsules",
            "Y-star-gov validator interface spec",
            "static read-model validation utility",
            "static snapshot generator",
            "snapshot-only team console CLI",
            "path-only runtime artifact quarantine summary",
            "bounded Markdown safe-mining candidate index",
            "candidate review queue summary",
            "runtime artifact backlog disposition summary",
            "structural evidence review summary",
            "dry-run Labs-Gov alignment bridge snapshot",
            "multi-role dry-run Pre-U governance summary",
            "dry-run labs runtime governance acceptance summary",
            "dry-run cross-repo governance alignment summary",
            "live-readiness gate summary that keeps live execution blocked",
            "disabled live-boundary harness summary",
            "disabled CIEU runtime event boundary summary",
            "company autonomy inventory summary",
            "mission-bounded autonomous work cycle simulator summary",
            "legacy asset triage summary",
            "governed read-only observation loop summary",
            "first governed read-only observation tool wrapper summary",
            "governed tool invocation bridge summary",
            "agent-team work proposal to governed tool invocation summary",
            "mission dashboard refresh loop summary",
            "governed recurring observation loop contract summary",
            "manual recurring observation tick runner summary",
            "field functional archaeology and merge plan summary",
            "mission field functional projection harness summary",
            "field functional auto-projection core summary",
            "projection-checked autonomous work cycle summary",
            "review-gated shadow learning cycle summary",
            "cross-repo governance contract proof summary",
            "governed MCP dry-run adapter summary",
            "controlled canonical learning design summary",
        ],
        "not_ready": [
            "runtime generator",
            "hook enforcement",
            "validator implementation",
            "CIEU delta schema",
            "brain writeback integration validation",
            "DB-safe query adapter",
            "frontend console",
            "live team-state refresh",
            "CI wiring for validator/generator",
            "CLI integration packaging",
            "semantic validation against live runtime",
            "full runtime artifact mining or curation adapters",
            "brain/CIEU ingestion from safe-mining candidates",
            "review approval workflow for candidate queue entries",
            "evidence scoring for disposition records",
            "DB/log/marker metadata adapters",
            "semantic truth validation for evidence records",
            "review decision application workflow",
            "real hook integration for Labs-Gov bridge",
            "runtime Pre-U packet execution",
            "real runtime acceptance beyond dry-run checks",
            "real cross-repo hook enforcement beyond dry-run alignment",
            "minimal live governed loop",
            "enabled live-boundary harness",
            "enabled CIEU runtime event persistence",
            "approved governed action registry",
            "approved canonical update sandbox",
            "L6 revenue opportunity discovery",
        ],
        "recommended_next_steps": [
            "wire static validator and loader into CI",
            "build a frontend that reads generated snapshots only",
            "create Y-star-gov validator skeleton",
            "define CIEU prediction-delta schema",
            "add Ethan/Samantha Pre-U packet variants",
            "design safe adapters for quarantine-to-CIEU review",
            "add human review queue for safe-mining candidates",
            "define signed review decisions for candidate queue entries",
            "create evidence scoring schema for disposition records",
            "define manual decision application for evidence review stubs",
            "connect bridge decisions to future Pre-U/CIEU dry-run examples without executing actions",
            "define a reviewed path from Pre-U dry-run snapshots to future CIEU prediction-delta examples",
            "define real hook enforcement handoff after dry-run acceptance remains stable",
            "define CI handoff after cross-repo dry-run alignment remains stable",
            "build live boundary harness before any runtime execution",
            "implement live boundary gates without enabling runtime execution",
            "define CIEU runtime event writer verification without enabling persistence",
            "simulate a company autonomous work cycle without enabling live actions",
            "build L4.4 first governed read-only observation tool wrapper",
            "route the governed read-only observation tool through the Pre-U bridge",
            "build L4.6 agent team work proposal to governed tool invocation",
            "define L4.8 governed recurring observation loop contract",
            "build L5.0 review-gated learning candidate queue",
            "build L5.1 mission field functional projection harness from archaeology merge plan",
            "build L5.8 approved canonical update sandbox from L5.7 promotion design",
        ],
        "blockers": [
            "no DB-safe adapter",
            "no live validator implementation",
            "no hook enforcement",
            "no semantic runtime truth guarantee",
            "no real Labs-Gov hook enforcement path",
            "no runtime Pre-U execution path",
            "no real action/CIEU/brain write path from acceptance reports",
            "no real cross-repo hook enforcement path",
            "no live boundary harness or operator approval gate",
            "live boundary gates are defined but disabled",
            "CIEU runtime event boundary is defined but persistence is disabled",
            "governed action registry candidates are mapped but disabled",
            "autonomous cycle is simulated only and cannot execute real work",
            "legacy assets are triaged but not absorbed",
            "observation loop is read-only and not recurring",
            "recurring observation loop contract is defined but not enabled",
            "approved canonical update sandbox is not implemented yet",
            "L6 revenue opportunity discovery remains blocked until canonical learning controls exist",
        ],
        "safety_boundaries": [
            "no DB reads",
            "no log reads",
            "no daemon/runtime state reads",
            "no hook/governance execution",
            "curated read-model files only",
            "quarantine summary is path-level only",
            "safe-mining candidates are bounded Markdown snippets only",
            "review queue entries are pending and not ingested",
            "disposition records are routing metadata, not ingestion",
            "evidence scoring is structural only and does not approve ingestion",
            "Labs-Gov bridge is dry-run only and does not execute actions",
            "generated Pre-U packets are dry-run only and not runtime actions",
            "labs runtime acceptance is dry-run only and not runtime execution",
            "cross-repo alignment is dry-run only and not CI or hook execution",
            "live-readiness gate forbids action/CIEU/brain/memory writes",
            "live-boundary harness is disabled and requires manual enablement",
            "CIEU runtime event boundary is disabled and forbids persistence",
            "company autonomy inventory is discovery-only and live actions remain disabled",
            "autonomous work cycle is simulated only and performs no external action",
            "legacy asset triage is classification-only and does not absorb assets",
            "governed observation loop reads generated summaries only and executes no actions",
            "governed read-only observation tool reads allowed generated summaries only and executes no actions",
            "governed tool invocation bridge requires Pre-U/decision/authorization before local tool calls",
            "agent-team work proposal routing starts from generated observations and remains local read-only dry-run only",
            "mission dashboard refresh loop is manual local dry-run only and uses generated/read-model evidence only",
            "recurring observation loop contract simulates one manual local tick and does not enable recurrence",
            "manual recurring observation tick runner executes one manual local tick only and does not enable recurrence",
            "field functional archaeology is merge-plan-only and does not execute old code or absorb runtime assets",
            "field functional auto-projection core is dry-run only and does not execute behavior",
            "projection-checked autonomous work cycle is dry-run only and does not execute behavior",
            "review-gated shadow learning cycle previews policy changes only and does not mutate canonical policy",
            "cross-repo governance proof keeps ystar-company as labs/runtime and not a governance kernel",
            "governed MCP dry-run adapter blocks real MCP server/tool/resource execution and mutation",
            "controlled canonical learning design creates promotion packages only and blocks approval, application, writeback, and direct Y* mutation",
        ],
    }

    manifest = {
        "schema_name": "ystar.console_read_model.generated.generation_manifest",
        "schema_version": "v0",
        "generated_files": [
            "console_read_model/generated/README.md",
            "console_read_model/generated/team_console_snapshot.json",
            "console_read_model/generated/team_console_snapshot.md",
            "console_read_model/generated/agent_cards_compiled.json",
            "console_read_model/generated/readiness_summary.json",
            "console_read_model/generated/quarantine_summary.json",
            "console_read_model/generated/safe_mining_summary.json",
            "console_read_model/generated/review_queue_summary.json",
            "console_read_model/generated/artifact_disposition_summary.json",
            "console_read_model/generated/evidence_review_summary.json",
            "console_read_model/generated/governance_bridge_summary.json",
            "console_read_model/generated/pre_u_governance_summary.json",
            "console_read_model/generated/labs_acceptance_summary.json",
            "console_read_model/generated/cross_repo_alignment_summary.json",
            "console_read_model/generated/live_readiness_summary.json",
            "console_read_model/generated/live_boundary_summary.json",
            "console_read_model/generated/cieu_boundary_summary.json",
            "console_read_model/generated/autonomy_inventory_summary.json",
            "console_read_model/generated/autonomous_cycle_summary.json",
            "console_read_model/generated/legacy_triage_summary.json",
            "console_read_model/generated/observation_loop_summary.json",
            "console_read_model/generated/readonly_tool_summary.json",
            "console_read_model/generated/tool_bridge_summary.json",
            "console_read_model/generated/work_proposal_summary.json",
            "console_read_model/generated/dashboard_refresh_summary.json",
            "console_read_model/generated/recurring_loop_summary.json",
            "console_read_model/generated/manual_tick_summary.json",
            "console_read_model/generated/field_functional_summary.json",
            "console_read_model/generated/mission_projection_summary.json",
            "console_read_model/generated/field_projection_summary.json",
            "console_read_model/generated/projection_cycle_summary.json",
            "console_read_model/generated/shadow_learning_cycle_summary.json",
            "console_read_model/generated/cross_repo_governance_summary.json",
            "console_read_model/generated/governed_mcp_adapter_summary.json",
            "console_read_model/generated/controlled_canonical_learning_summary.json",
            "console_read_model/generated/approved_sandbox_update_summary.json",
            "console_read_model/generated/real_approval_workflow_summary.json",
            "console_read_model/generated/generation_manifest.json",
        ],
        "source_files": files_read,
        "unsafe_sources_not_read": [
            "*.db",
            "*.db-wal",
            "*.db-shm",
            "scripts/.logs/*",
            "active-agent markers",
            "daemon pid/state files",
            "__pycache__",
            "raw runtime report directories",
        ],
        "generator_version": GENERATOR_VERSION,
        "validation_recommendation": "Run console_read_model/validation/validate_team_read_model.py after generation.",
        "generated_at_policy": "static_snapshot_no_runtime_clock_required",
    }

    snapshot_md = render_snapshot_markdown(snapshot, readiness_summary)

    write_text(
        "console_read_model/generated/README.md",
        "# Generated Console Snapshots\n\n"
        "These files are derived artifacts from curated read-model inputs only.\n"
        "They do not contain DB contents, raw logs, daemon state, active-agent state,\n"
        "or live runtime observations.\n\n"
        "`quarantine_summary.json` is derived from the runtime artifact quarantine\n"
        "path-only manifest. It summarizes classes/counts only and does not include\n"
        "artifact contents.\n\n"
        "`safe_mining_summary.json` is derived from bounded Markdown report candidate\n"
        "indexes. It summarizes candidate counts/classes only; candidates remain\n"
        "review assets, not brain memory.\n\n"
        "`review_queue_summary.json` is derived from generated review queue files.\n"
        "It summarizes pending review state only; entries are not approved or ingested.\n\n"
        "`artifact_disposition_summary.json` is derived from generated backlog\n"
        "disposition indexes. It summarizes routing/disposition only; it is not ingestion.\n\n"
        "`evidence_review_summary.json` is derived from generated evidence review\n"
        "indexes. It summarizes structural readiness only; it is not approval.\n\n"
        "`governance_bridge_summary.json` is derived from the generated Labs-Gov\n"
        "dry-run decision snapshot. It is not hook execution or CIEU writeback.\n\n"
        "`pre_u_governance_summary.json` is derived from generated multi-role\n"
        "Pre-U dry-run decisions. It is not runtime packet execution.\n\n"
        "`labs_acceptance_summary.json` is derived from the generated labs runtime\n"
        "acceptance report. It is dry-run acceptance only, not runtime execution.\n\n"
        "`cross_repo_alignment_summary.json` is derived from the generated cross-repo\n"
        "alignment manifest. It is dry-run compatibility only, not CI or hook execution.\n\n"
        "`live_readiness_summary.json` is derived from the generated live-readiness\n"
        "report. It identifies blockers and keeps live execution disabled.\n\n"
        "`live_boundary_summary.json` is derived from the generated live-boundary\n"
        "manifest. It confirms boundary definitions remain disabled.\n\n"
        "`cieu_boundary_summary.json` is derived from the generated CIEU runtime\n"
        "boundary manifest. It confirms event fixtures are dry-run only and persistence is disabled.\n\n"
        "`autonomy_inventory_summary.json` is derived from the generated company\n"
        "autonomy inventory. It confirms capability maps and tool candidates exist while live actions remain disabled.\n\n"
        "`autonomous_cycle_summary.json` is derived from the mission-bounded\n"
        "autonomous work cycle simulator. It confirms a full simulated company cycle exists while real actions remain disabled.\n\n"
        "`legacy_triage_summary.json` is derived from generated legacy asset\n"
        "triage outputs. It classifies assets before absorption and enables no actions.\n\n"
        "`observation_loop_summary.json` is derived from generated governed\n"
        "observation loop outputs. It summarizes a read-only tick from safe generated sources.\n\n"
        "`readonly_tool_summary.json` is derived from generated governed read-only\n"
        "observation tool outputs. It confirms the first local read-only wrapper is callable while live action remains disabled.\n\n"
        "`tool_bridge_summary.json` is derived from generated governed tool\n"
        "invocation bridge outputs. It confirms the read-only tool is called only after Pre-U packet, decision, and bridge authorization.\n\n"
        "`work_proposal_summary.json` is derived from generated agent-team work\n"
        "proposal outputs. It confirms mission/observation evidence produced a governed tool request routed through the L4.5 bridge.\n\n"
        "`dashboard_refresh_summary.json` is derived from generated mission dashboard\n"
        "refresh loop outputs. It confirms a manual local refresh loop produced a refreshed dashboard without scheduler or daemon use.\n\n"
        "`recurring_loop_summary.json` is derived from generated recurring observation\n"
        "loop contract outputs. It confirms recurrence is defined but disabled and only one manual local simulated tick exists.\n\n"
        "`manual_tick_summary.json` is derived from generated manual recurring\n"
        "observation tick runner outputs. It confirms one manual local tick ran with a receipt while scheduler, daemon, and recurrence stay disabled.\n\n"
        "`field_functional_summary.json` is derived from generated field\n"
        "functional archaeology outputs. It confirms old field-functional work was searched and mapped into a merge plan without executing old code.\n\n"
        "`mission_projection_summary.json` is derived from the L5.1 mission field\n"
        "projection harness. It confirms layered Y* projection, a Pre-U packet candidate, and a residual fixture exist while action execution remains disabled.\n\n"
        "`field_projection_summary.json` is derived from the L5.2 field functional\n"
        "auto-projection core. It confirms mission-to-behavior Y* projection, a behavior-level Pre-U candidate, and a residual loop fixture exist while behavior execution remains disabled.\n\n"
        "`projection_cycle_summary.json` is derived from the L5.3 projection-checked\n"
        "autonomous work cycle. It confirms behavior-level Y* is consumed as a gate before dry-run work proposal, Pre-U candidate, residual, and review-only learning artifacts.\n\n"
        "`shadow_learning_cycle_summary.json` is derived from the L5.4 integrated\n"
        "review-gated shadow learning cycle. It confirms an L5.3 residual can influence a shadow behavior-level Y* preview and shadow cycle without canonical policy mutation or writeback.\n\n"
        "`cross_repo_governance_summary.json` is derived from the L5.5 cross-repo\n"
        "governance contract proof. It confirms ystar-company remains labs/runtime, Y-star-gov remains the intended governance kernel, and gov-mcp remains a governed interface boundary.\n\n"
        "`governed_mcp_adapter_summary.json` is derived from the L5.6 governed MCP\n"
        "dry-run adapter proof. It confirms a future MCP call candidate is downstream of behavior-level Y*, Pre-U, governance expectation, bridge receipt, CIEU-like receipt, residual delta, and review-only learning gates while real MCP execution remains blocked.\n\n"
        "`controlled_canonical_learning_summary.json` is derived from the L5.7 controlled\n"
        "canonical learning design. It confirms review-only and shadow candidates can become non-applied canonical update package candidates while approval, application, writeback, strategy mutation, and direct Y* mutation remain blocked.\n\n"
        "`approved_sandbox_update_summary.json` is derived from the L5.8 approved\n"
        "canonical update sandbox. It confirms sandbox approval/application, sandbox reprojection, MCP preview, CIEU-like residual, and rollback validation exist while real approval, real canonical mutation, writeback, direct Y* mutation, MCP execution, and live execution remain blocked.\n\n"
        "`real_approval_workflow_summary.json` is derived from the L5.9 real approval\n"
        "workflow boundary. It confirms authority, evidence, durable approval record contract, validity/revocation, snapshot, real application gate, preflight, runbook, and audit fixture exist while real approval, durable approval persistence, and real application remain blocked.\n\n"
        "`console_read_model/cli/team_console.py` consumes these generated files as its\n"
        "only data source.\n",
        generated_files,
    )
    write_json("console_read_model/generated/team_console_snapshot.json", snapshot, generated_files)
    write_text("console_read_model/generated/team_console_snapshot.md", snapshot_md, generated_files)
    write_json("console_read_model/generated/agent_cards_compiled.json", compiled_cards, generated_files)
    write_json("console_read_model/generated/readiness_summary.json", readiness_summary, generated_files)
    write_json("console_read_model/generated/quarantine_summary.json", quarantine_summary, generated_files)
    write_json("console_read_model/generated/safe_mining_summary.json", safe_mining_summary, generated_files)
    write_json("console_read_model/generated/review_queue_summary.json", review_queue_summary, generated_files)
    write_json("console_read_model/generated/artifact_disposition_summary.json", disposition_summary, generated_files)
    write_json("console_read_model/generated/evidence_review_summary.json", evidence_review_summary, generated_files)
    write_json("console_read_model/generated/governance_bridge_summary.json", governance_bridge_summary, generated_files)
    write_json("console_read_model/generated/pre_u_governance_summary.json", pre_u_governance_summary, generated_files)
    write_json("console_read_model/generated/labs_acceptance_summary.json", labs_acceptance_summary, generated_files)
    write_json("console_read_model/generated/cross_repo_alignment_summary.json", cross_repo_alignment_summary, generated_files)
    write_json("console_read_model/generated/live_readiness_summary.json", live_readiness_summary, generated_files)
    write_json("console_read_model/generated/live_boundary_summary.json", live_boundary_summary, generated_files)
    write_json("console_read_model/generated/cieu_boundary_summary.json", cieu_boundary_summary, generated_files)
    write_json("console_read_model/generated/autonomy_inventory_summary.json", autonomy_inventory_summary, generated_files)
    write_json("console_read_model/generated/autonomous_cycle_summary.json", autonomous_cycle_summary, generated_files)
    write_json("console_read_model/generated/legacy_triage_summary.json", legacy_triage_summary, generated_files)
    write_json("console_read_model/generated/observation_loop_summary.json", observation_loop_summary, generated_files)
    write_json("console_read_model/generated/readonly_tool_summary.json", readonly_tool_summary, generated_files)
    write_json("console_read_model/generated/tool_bridge_summary.json", tool_bridge_summary, generated_files)
    write_json("console_read_model/generated/work_proposal_summary.json", work_proposal_summary, generated_files)
    write_json("console_read_model/generated/dashboard_refresh_summary.json", dashboard_refresh_summary, generated_files)
    write_json("console_read_model/generated/recurring_loop_summary.json", recurring_loop_summary, generated_files)
    write_json("console_read_model/generated/manual_tick_summary.json", manual_tick_summary, generated_files)
    write_json("console_read_model/generated/field_functional_summary.json", field_functional_summary, generated_files)
    write_json("console_read_model/generated/mission_projection_summary.json", mission_projection_summary, generated_files)
    write_json("console_read_model/generated/field_projection_summary.json", field_projection_summary, generated_files)
    write_json("console_read_model/generated/projection_cycle_summary.json", projection_cycle_summary, generated_files)
    write_json("console_read_model/generated/shadow_learning_cycle_summary.json", shadow_learning_cycle_summary, generated_files)
    write_json("console_read_model/generated/cross_repo_governance_summary.json", cross_repo_governance_summary, generated_files)
    write_json("console_read_model/generated/governed_mcp_adapter_summary.json", governed_mcp_adapter_summary, generated_files)
    write_json("console_read_model/generated/controlled_canonical_learning_summary.json", controlled_canonical_learning_summary, generated_files)
    write_json("console_read_model/generated/approved_sandbox_update_summary.json", approved_sandbox_update_summary, generated_files)
    write_json("console_read_model/generated/real_approval_workflow_summary.json", real_approval_workflow_summary, generated_files)
    write_json("console_read_model/generated/generation_manifest.json", manifest, generated_files)

    return files_read, generated_files, [agent["agent_id"] for agent in agents], warnings


def render_snapshot_markdown(snapshot: dict[str, Any], readiness: dict[str, Any]) -> str:
    lines = [
        "# Team Brain Console Snapshot",
        "",
        "This snapshot is generated from curated read-model files only.",
        "",
        "## Agents",
        "",
    ]
    for agent in snapshot["agents"]:
        lines.extend(
            [
                f"### {agent['agent_id']}",
                "",
                f"- Name: {agent['canonical_name']}",
                f"- Role type: {agent['role_type']}",
                f"- Readiness: {agent['readiness_level']}",
                f"- Focus: {agent['focus']}",
                f"- Pre-U packet: {agent['has_pre_u_packet']}",
                f"- Execution channels: {agent['has_execution_channels']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Capability Matrix Summary",
            "",
            "See `capability_matrix.json` and generated snapshot JSON for the full matrix.",
            "",
            "## Readiness Summary",
            "",
            "Ready now:",
        ]
    )
    lines.extend([f"- {item}" for item in readiness["ready_now"]])
    lines.extend(["", "Not ready:"])
    lines.extend([f"- {item}" for item in readiness["not_ready"]])
    quarantine = snapshot.get("quarantine_summary", {})
    safe_mining = snapshot.get("safe_mining_summary", {})
    review_queue = snapshot.get("review_queue_summary", {})
    disposition = snapshot.get("artifact_disposition_summary", {})
    evidence_review = snapshot.get("evidence_review_summary", {})
    governance_bridge = snapshot.get("governance_bridge_summary", {})
    pre_u_governance = snapshot.get("pre_u_governance_summary", {})
    labs_acceptance = snapshot.get("labs_acceptance_summary", {})
    cross_repo = snapshot.get("cross_repo_alignment_summary", {})
    live_readiness = snapshot.get("live_readiness_summary", {})
    live_boundary = snapshot.get("live_boundary_summary", {})
    cieu_boundary = snapshot.get("cieu_boundary_summary", {})
    autonomy_inventory = snapshot.get("autonomy_inventory_summary", {})
    autonomous_cycle = snapshot.get("autonomous_cycle_summary", {})
    legacy_triage = snapshot.get("legacy_triage_summary", {})
    observation_loop = snapshot.get("observation_loop_summary", {})
    readonly_tool = snapshot.get("readonly_tool_summary", {})
    tool_bridge = snapshot.get("tool_bridge_summary", {})
    work_proposal = snapshot.get("work_proposal_summary", {})
    dashboard_refresh = snapshot.get("dashboard_refresh_summary", {})
    recurring_loop = snapshot.get("recurring_loop_summary", {})
    manual_tick = snapshot.get("manual_tick_summary", {})
    field_functional = snapshot.get("field_functional_summary", {})
    mission_projection = snapshot.get("mission_projection_summary", {})
    field_projection = snapshot.get("field_projection_summary", {})
    projection_cycle = snapshot.get("projection_cycle_summary", {})
    shadow_learning_cycle = snapshot.get("shadow_learning_cycle_summary", {})
    cross_repo_governance = snapshot.get("cross_repo_governance_summary", {})
    governed_mcp_adapter = snapshot.get("governed_mcp_adapter_summary", {})
    controlled_canonical_learning = snapshot.get("controlled_canonical_learning_summary", {})
    approved_sandbox_update = snapshot.get("approved_sandbox_update_summary", {})
    real_approval_workflow = snapshot.get("real_approval_workflow_summary", {})
    lines.extend(
        [
            "",
            "## Runtime Artifact Quarantine Summary",
            "",
            f"- Framework status: {quarantine.get('framework_status')}",
            f"- Current mining level: {quarantine.get('current_mining_level')}",
            f"- Artifacts classified: {quarantine.get('artifacts_classified')}",
            f"- Unsafe artifacts count: {quarantine.get('unsafe_artifacts_count')}",
            "- Classes seen:",
        ]
    )
    for class_name, count in sorted(quarantine.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(
        [
            f"- Generated manifest ref: {quarantine.get('generated_manifest_ref')}",
            f"- Warning: {quarantine.get('safety_warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Runtime Artifact Safe Mining Candidates",
            "",
            f"- Candidate count: {safe_mining.get('candidate_count')}",
            f"- Safety level: {safe_mining.get('safety_level')}",
            f"- Ingestion status: {safe_mining.get('ingestion_status')}",
            f"- Generated candidate index: {safe_mining.get('generated_candidate_index')}",
            "- Classes seen:",
        ]
    )
    for class_name, count in sorted(safe_mining.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(
        [
            f"- Warning: {safe_mining.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Runtime Artifact Candidate Review Queue",
            "",
            f"- Review count: {review_queue.get('review_count')}",
            f"- Default review status: {review_queue.get('default_review_status')}",
            f"- Default ingestion status: {review_queue.get('default_ingestion_status')}",
            f"- Generated queue path: {review_queue.get('generated_queue_path')}",
            "- Statuses:",
        ]
    )
    for status, count in sorted(review_queue.get("statuses", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append("- Intended use summary:")
    for use, count in sorted(review_queue.get("intended_use_summary", {}).items()):
        lines.append(f"  - {use}: {count}")
    lines.append(f"- Warning: {review_queue.get('warning')}")
    lines.extend(
        [
            "",
            "## Runtime Artifact Backlog Disposition",
            "",
            f"- Total artifacts: {disposition.get('total_artifacts')}",
            f"- Artifacts with disposition: {disposition.get('artifacts_with_disposition')}",
            f"- Safe-mined to review queue: {disposition.get('safe_mined_to_review_queue')}",
            f"- Forbidden direct read count: {disposition.get('forbidden_direct_read_count')}",
            f"- Generated disposition index: {disposition.get('generated_disposition_index')}",
            "- Dispositions:",
        ]
    )
    for disposition_name, count in sorted(disposition.get("dispositions", {}).items()):
        lines.append(f"  - {disposition_name}: {count}")
    lines.append("- Evidence scoring status:")
    for status, count in sorted(disposition.get("evidence_scoring_status", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append(f"- Warning: {disposition.get('warning')}")
    lines.extend(
        [
            "",
            "## Runtime Artifact Evidence Review",
            "",
            f"- Candidates scored: {evidence_review.get('candidates_scored')}",
            f"- Decision stubs created: {evidence_review.get('decision_stubs_created')}",
            f"- Routes created: {evidence_review.get('routes_created')}",
            f"- Automatic approvals: {evidence_review.get('automatic_approvals')}",
            "- Reuse readiness:",
        ]
    )
    for readiness_name, count in sorted(evidence_review.get("reuse_readiness", {}).items()):
        lines.append(f"  - {readiness_name}: {count}")
    lines.append("- Route counts:")
    for route, count in sorted(evidence_review.get("route_counts", {}).items()):
        lines.append(f"  - {route}: {count}")
    lines.append("- Semantic truth status:")
    for status, count in sorted(evidence_review.get("semantic_truth_status", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append(f"- Warning: {evidence_review.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs-Gov Alignment Bridge",
            "",
            f"- Bridge run id: {governance_bridge.get('latest_bridge_run_id')}",
            f"- Source task id: {governance_bridge.get('source_task_id')}",
            f"- Agent id: {governance_bridge.get('agent_id')}",
            f"- Y-star-gov decision: {governance_bridge.get('ystar_gov_decision')}",
            f"- Y-star-gov exit code: {governance_bridge.get('ystar_gov_exit_code')}",
            f"- allow_execution: {governance_bridge.get('allow_execution')}",
            f"- require_revision: {governance_bridge.get('require_revision')}",
            f"- deny: {governance_bridge.get('deny')}",
            f"- escalate: {governance_bridge.get('escalate')}",
            f"- dry_run_only: {governance_bridge.get('dry_run_only')}",
            f"- action_executed: {governance_bridge.get('action_executed')}",
            f"- cieu_written: {governance_bridge.get('cieu_written')}",
            f"- brain_writeback_performed: {governance_bridge.get('brain_writeback_performed')}",
            f"- Warning: {governance_bridge.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Labs Pre-U Governance Dry Run",
            "",
            f"- Packets generated: {pre_u_governance.get('packets_generated')}",
            f"- Roles covered: {', '.join(pre_u_governance.get('roles_covered', []))}",
            "- Decision counts:",
        ]
    )
    for decision, count in sorted(pre_u_governance.get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.append("- Decisions by role:")
    for agent_id, decision in sorted(pre_u_governance.get("decisions_by_role", {}).items()):
        lines.append(f"  - {agent_id}: {decision.get('decision')} (exit {decision.get('exit_code')})")
    lines.extend(
        [
            f"- dry_run_only: {pre_u_governance.get('dry_run_only')}",
            f"- action_executed: {pre_u_governance.get('action_executed')}",
            f"- cieu_written: {pre_u_governance.get('cieu_written')}",
            f"- brain_writeback_performed: {pre_u_governance.get('brain_writeback_performed')}",
            f"- Warning: {pre_u_governance.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Labs Runtime Governance Acceptance",
            "",
            f"- accepted: {labs_acceptance.get('accepted')}",
            f"- checks_passed: {labs_acceptance.get('checks_passed')}",
            f"- checks_total: {labs_acceptance.get('checks_total')}",
            f"- roles_covered: {', '.join(labs_acceptance.get('roles_covered', []))}",
            "- decision_counts:",
        ]
    )
    for decision, count in sorted(labs_acceptance.get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.extend(
        [
            f"- action_executed: {labs_acceptance.get('action_executed')}",
            f"- cieu_written: {labs_acceptance.get('cieu_written')}",
            f"- brain_writeback_performed: {labs_acceptance.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {labs_acceptance.get('memory_ingestion_performed')}",
            f"- raw_runtime_artifacts_ingested: {labs_acceptance.get('raw_runtime_artifacts_ingested')}",
            f"- Warning: {labs_acceptance.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Cross-Repo Governance Alignment",
            "",
            f"- alignment_accepted: {cross_repo.get('alignment_accepted')}",
            f"- ystar-company HEAD: {cross_repo.get('ystar_company_head_summary')}",
            f"- Y-star-gov HEAD: {cross_repo.get('ystar_gov_head_summary')}",
            f"- Y-star-gov endpoint accepted: {cross_repo.get('ystar_gov_endpoint_accepted')}",
            f"- labs runtime accepted: {cross_repo.get('labs_runtime_accepted')}",
            f"- roles_covered: {', '.join(cross_repo.get('roles_covered', []))}",
            "- decision_counts:",
        ]
    )
    for decision, count in sorted(cross_repo.get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.append("- safety_assertions:")
    for key, value in sorted(cross_repo.get("safety_assertions", {}).items()):
        lines.append(f"  - {key}: {value}")
    lines.append(f"- Warning: {cross_repo.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs Live Readiness",
            "",
            f"- dry_run_governance_ready: {live_readiness.get('dry_run_governance_ready')}",
            f"- minimal_live_loop_ready: {live_readiness.get('minimal_live_loop_ready')}",
            f"- minimal_live_loop_status: {live_readiness.get('minimal_live_loop_status')}",
            f"- recommended_next_phase: {live_readiness.get('recommended_next_phase')}",
            f"- live_action_execution_allowed: {live_readiness.get('live_action_execution_allowed')}",
            f"- live_cieu_write_allowed: {live_readiness.get('live_cieu_write_allowed')}",
            f"- live_brain_writeback_allowed: {live_readiness.get('live_brain_writeback_allowed')}",
            f"- live_memory_ingestion_allowed: {live_readiness.get('live_memory_ingestion_allowed')}",
            f"- transition_backlog_items: {live_readiness.get('transition_backlog_items')}",
            "- blockers:",
        ]
    )
    for blocker in live_readiness.get("blockers", []):
        lines.append(f"  - {blocker}")
    lines.append(f"- Warning: {live_readiness.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs Live Boundary",
            "",
            f"- live_boundary_defined: {live_boundary.get('live_boundary_defined')}",
            f"- operator_approval_gate_defined: {live_boundary.get('operator_approval_gate_defined')}",
            f"- action_sandbox_contract_defined: {live_boundary.get('action_sandbox_contract_defined')}",
            f"- rollback_policy_defined: {live_boundary.get('rollback_policy_defined')}",
            f"- cieu_writer_boundary_defined: {live_boundary.get('cieu_writer_boundary_defined')}",
            f"- live_action_execution_enabled: {live_boundary.get('live_action_execution_enabled')}",
            f"- cieu_write_enabled: {live_boundary.get('cieu_write_enabled')}",
            f"- brain_writeback_enabled: {live_boundary.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {live_boundary.get('memory_ingestion_enabled')}",
            f"- minimal_live_loop_ready: {live_boundary.get('minimal_live_loop_ready')}",
            f"- requires_manual_enablement: {live_boundary.get('requires_manual_enablement')}",
            f"- blocked_reason: {live_boundary.get('blocked_reason')}",
            "- checklist_status_counts:",
        ]
    )
    for status, count in sorted(live_boundary.get("checklist_status_counts", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append(f"- Warning: {live_boundary.get('warning')}")
    lines.extend(
        [
            "",
            "## Labs CIEU Runtime Boundary",
            "",
            f"- cieu_runtime_boundary_defined: {cieu_boundary.get('cieu_runtime_boundary_defined')}",
            f"- cieu_runtime_event_schema_defined: {cieu_boundary.get('cieu_runtime_event_schema_defined')}",
            f"- prediction_delta_fixture_defined: {cieu_boundary.get('prediction_delta_fixture_defined')}",
            f"- cieu_writer_policy_defined: {cieu_boundary.get('cieu_writer_policy_defined')}",
            f"- dry_run_only: {cieu_boundary.get('dry_run_only')}",
            f"- persistence_enabled: {cieu_boundary.get('persistence_enabled')}",
            f"- live_action_execution_enabled: {cieu_boundary.get('live_action_execution_enabled')}",
            f"- cieu_write_enabled: {cieu_boundary.get('cieu_write_enabled')}",
            f"- brain_writeback_enabled: {cieu_boundary.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {cieu_boundary.get('memory_ingestion_enabled')}",
            f"- minimal_live_loop_ready: {cieu_boundary.get('minimal_live_loop_ready')}",
            f"- requires_manual_enablement: {cieu_boundary.get('requires_manual_enablement')}",
            f"- blocked_reason: {cieu_boundary.get('blocked_reason')}",
            f"- generated_sample_event: {cieu_boundary.get('generated_sample_event')}",
            f"- generated_prediction_delta_fixture: {cieu_boundary.get('generated_prediction_delta_fixture')}",
            f"- Warning: {cieu_boundary.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Company Autonomy Inventory",
            "",
            f"- repo_archaeology_completed: {autonomy_inventory.get('repo_archaeology_completed')}",
            f"- observation_capability_map_defined: {autonomy_inventory.get('observation_capability_map_defined')}",
            f"- resource_sensing_map_defined: {autonomy_inventory.get('resource_sensing_map_defined')}",
            f"- action_capability_map_defined: {autonomy_inventory.get('action_capability_map_defined')}",
            f"- governed_tool_registry_candidates_defined: {autonomy_inventory.get('governed_tool_registry_candidates_defined')}",
            f"- agent_role_capability_matrix_defined: {autonomy_inventory.get('agent_role_capability_matrix_defined')}",
            f"- commercial_agent_company_goal_aligned: {autonomy_inventory.get('commercial_agent_company_goal_aligned')}",
            f"- governance_only_runtime: {autonomy_inventory.get('governance_only_runtime')}",
            f"- live_actions_enabled: {autonomy_inventory.get('live_actions_enabled')}",
            f"- external_actions_enabled: {autonomy_inventory.get('external_actions_enabled')}",
            f"- brain_writeback_enabled: {autonomy_inventory.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {autonomy_inventory.get('memory_ingestion_enabled')}",
            f"- cieu_persistence_enabled: {autonomy_inventory.get('cieu_persistence_enabled')}",
            f"- next_required_milestone: {autonomy_inventory.get('next_required_milestone')}",
            f"- Warning: {autonomy_inventory.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Company Autonomous Work Cycle",
            "",
            f"- mission_bounded_autonomy_defined: {autonomous_cycle.get('mission_bounded_autonomy_defined')}",
            f"- founder_sets_mission_agent_team_drives: {autonomous_cycle.get('founder_sets_mission_agent_team_drives')}",
            f"- step_by_step_human_prompting_required: {autonomous_cycle.get('step_by_step_human_prompting_required')}",
            f"- observation_snapshot_defined: {autonomous_cycle.get('observation_snapshot_defined')}",
            f"- autonomous_work_backlog_defined: {autonomous_cycle.get('autonomous_work_backlog_defined')}",
            f"- selected_work_item_defined: {autonomous_cycle.get('selected_work_item_defined')}",
            f"- role_delegation_defined: {autonomous_cycle.get('role_delegation_defined')}",
            f"- governed_tool_selection_defined: {autonomous_cycle.get('governed_tool_selection_defined')}",
            f"- pre_u_packet_simulated: {autonomous_cycle.get('pre_u_packet_simulated')}",
            f"- governance_decision_simulated: {autonomous_cycle.get('governance_decision_simulated')}",
            f"- action_plan_simulated: {autonomous_cycle.get('action_plan_simulated')}",
            f"- cieu_event_simulated: {autonomous_cycle.get('cieu_event_simulated')}",
            f"- residual_delta_simulated: {autonomous_cycle.get('residual_delta_simulated')}",
            f"- real_action_executed: {autonomous_cycle.get('real_action_executed')}",
            f"- external_action_executed: {autonomous_cycle.get('external_action_executed')}",
            f"- live_action_enabled: {autonomous_cycle.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {autonomous_cycle.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {autonomous_cycle.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {autonomous_cycle.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {autonomous_cycle.get('next_required_milestone')}",
            f"- Warning: {autonomous_cycle.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Legacy Asset Triage",
            "",
            f"- assets_scored: {legacy_triage.get('assets_scored')}",
            f"- absorption_buckets_defined: {legacy_triage.get('absorption_buckets_defined')}",
            f"- top_absorption_candidates_defined: {legacy_triage.get('top_absorption_candidates_defined')}",
            f"- governed_absorption_backlog_defined: {legacy_triage.get('governed_absorption_backlog_defined')}",
            f"- blind_absorption_allowed: {legacy_triage.get('blind_absorption_allowed')}",
            f"- blanket_rewrite_allowed: {legacy_triage.get('blanket_rewrite_allowed')}",
            f"- live_actions_enabled: {legacy_triage.get('live_actions_enabled')}",
            f"- next_required_milestone: {legacy_triage.get('next_required_milestone')}",
            "- bucket_counts:",
        ]
    )
    for bucket, count in sorted(legacy_triage.get("bucket_counts", {}).items()):
        lines.append(f"  - {bucket}: {count}")
    lines.append(f"- Warning: {legacy_triage.get('warning')}")
    lines.extend(
        [
            "",
            "## Governed Observation Loop",
            "",
            f"- read_only_observation_loop_defined: {observation_loop.get('read_only_observation_loop_defined')}",
            f"- observation_source_registry_defined: {observation_loop.get('observation_source_registry_defined')}",
            f"- observation_tick_generated: {observation_loop.get('observation_tick_generated')}",
            f"- mission_dashboard_snapshot_defined: {observation_loop.get('mission_dashboard_snapshot_defined')}",
            f"- company_state_digest_defined: {observation_loop.get('company_state_digest_defined')}",
            f"- observation_to_work_item_candidates_defined: {observation_loop.get('observation_to_work_item_candidates_defined')}",
            f"- mission_bounded_autonomy_supported: {observation_loop.get('mission_bounded_autonomy_supported')}",
            f"- step_by_step_human_prompting_reduced: {observation_loop.get('step_by_step_human_prompting_reduced')}",
            f"- real_action_executed: {observation_loop.get('real_action_executed')}",
            f"- external_action_executed: {observation_loop.get('external_action_executed')}",
            f"- live_action_enabled: {observation_loop.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {observation_loop.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {observation_loop.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {observation_loop.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {observation_loop.get('next_required_milestone')}",
            f"- Warning: {observation_loop.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed Read-Only Observation Tool",
            "",
            f"- tool_contract_defined: {readonly_tool.get('tool_contract_defined')}",
            f"- allowed_source_registry_defined: {readonly_tool.get('allowed_source_registry_defined')}",
            f"- sample_invocation_defined: {readonly_tool.get('sample_invocation_defined')}",
            f"- sample_result_defined: {readonly_tool.get('sample_result_defined')}",
            f"- unsafe_invocation_rejected: {readonly_tool.get('unsafe_invocation_rejected')}",
            f"- local_readonly_dry_run_callable: {readonly_tool.get('local_readonly_dry_run_callable')}",
            f"- first_governed_tool_wrapper_created: {readonly_tool.get('first_governed_tool_wrapper_created')}",
            f"- real_action_executed: {readonly_tool.get('real_action_executed')}",
            f"- external_action_executed: {readonly_tool.get('external_action_executed')}",
            f"- live_action_enabled: {readonly_tool.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {readonly_tool.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {readonly_tool.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {readonly_tool.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {readonly_tool.get('next_required_milestone')}",
            f"- Warning: {readonly_tool.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed Tool Invocation Bridge",
            "",
            f"- bridge_contract_defined: {tool_bridge.get('bridge_contract_defined')}",
            f"- agent_tool_request_defined: {tool_bridge.get('agent_tool_request_defined')}",
            f"- pre_u_tool_packet_defined: {tool_bridge.get('pre_u_tool_packet_defined')}",
            f"- governance_decision_defined: {tool_bridge.get('governance_decision_defined')}",
            f"- bridge_authorization_defined: {tool_bridge.get('bridge_authorization_defined')}",
            f"- tool_invoked_through_bridge: {tool_bridge.get('tool_invoked_through_bridge')}",
            f"- direct_tool_invocation_rejected: {tool_bridge.get('direct_tool_invocation_rejected')}",
            f"- unsafe_bridge_request_rejected: {tool_bridge.get('unsafe_bridge_request_rejected')}",
            f"- bridge_cieu_event_defined: {tool_bridge.get('bridge_cieu_event_defined')}",
            f"- bridge_residual_delta_defined: {tool_bridge.get('bridge_residual_delta_defined')}",
            f"- first_governed_tool_invocation_chain_created: {tool_bridge.get('first_governed_tool_invocation_chain_created')}",
            f"- real_action_executed: {tool_bridge.get('real_action_executed')}",
            f"- external_action_executed: {tool_bridge.get('external_action_executed')}",
            f"- live_action_enabled: {tool_bridge.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {tool_bridge.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {tool_bridge.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {tool_bridge.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {tool_bridge.get('next_required_milestone')}",
            f"- Warning: {tool_bridge.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Agent Team Work Proposal",
            "",
            f"- mission_context_snapshot_defined: {work_proposal.get('mission_context_snapshot_defined')}",
            f"- agent_team_observation_input_defined: {work_proposal.get('agent_team_observation_input_defined')}",
            f"- autonomous_work_proposals_defined: {work_proposal.get('autonomous_work_proposals_defined')}",
            f"- selected_work_proposal_defined: {work_proposal.get('selected_work_proposal_defined')}",
            f"- role_review_board_defined: {work_proposal.get('role_review_board_defined')}",
            f"- tool_need_analysis_defined: {work_proposal.get('tool_need_analysis_defined')}",
            f"- generated_tool_request_defined: {work_proposal.get('generated_tool_request_defined')}",
            f"- work_proposal_routed_to_bridge: {work_proposal.get('work_proposal_routed_to_bridge')}",
            f"- direct_tool_invocation_used: {work_proposal.get('direct_tool_invocation_used')}",
            f"- bridged_tool_result_ref_defined: {work_proposal.get('bridged_tool_result_ref_defined')}",
            f"- work_proposal_cieu_event_defined: {work_proposal.get('work_proposal_cieu_event_defined')}",
            f"- work_proposal_residual_delta_defined: {work_proposal.get('work_proposal_residual_delta_defined')}",
            f"- agent_team_generated_the_work: {work_proposal.get('agent_team_generated_the_work')}",
            f"- agent_team_selected_governed_tool: {work_proposal.get('agent_team_selected_governed_tool')}",
            f"- pre_u_bridge_required: {work_proposal.get('pre_u_bridge_required')}",
            f"- pre_u_bridge_satisfied: {work_proposal.get('pre_u_bridge_satisfied')}",
            f"- real_action_executed: {work_proposal.get('real_action_executed')}",
            f"- external_action_executed: {work_proposal.get('external_action_executed')}",
            f"- live_action_enabled: {work_proposal.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {work_proposal.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {work_proposal.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {work_proposal.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {work_proposal.get('next_required_milestone')}",
            f"- Warning: {work_proposal.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Mission Dashboard Refresh Loop",
            "",
            f"- refresh_loop_contract_defined: {dashboard_refresh.get('refresh_loop_contract_defined')}",
            f"- previous_dashboard_snapshot_defined: {dashboard_refresh.get('previous_dashboard_snapshot_defined')}",
            f"- current_observation_input_defined: {dashboard_refresh.get('current_observation_input_defined')}",
            f"- refreshed_mission_dashboard_defined: {dashboard_refresh.get('refreshed_mission_dashboard_defined')}",
            f"- company_state_delta_defined: {dashboard_refresh.get('company_state_delta_defined')}",
            f"- refreshed_autonomous_backlog_defined: {dashboard_refresh.get('refreshed_autonomous_backlog_defined')}",
            f"- refresh_loop_trace_defined: {dashboard_refresh.get('refresh_loop_trace_defined')}",
            f"- refresh_cieu_event_defined: {dashboard_refresh.get('refresh_cieu_event_defined')}",
            f"- refresh_residual_delta_defined: {dashboard_refresh.get('refresh_residual_delta_defined')}",
            f"- dashboard_refresh_loop_ran: {dashboard_refresh.get('dashboard_refresh_loop_ran')}",
            f"- scheduler_used: {dashboard_refresh.get('scheduler_used')}",
            f"- daemon_used: {dashboard_refresh.get('daemon_used')}",
            f"- manual_local_run_only: {dashboard_refresh.get('manual_local_run_only')}",
            f"- real_action_executed: {dashboard_refresh.get('real_action_executed')}",
            f"- external_action_executed: {dashboard_refresh.get('external_action_executed')}",
            f"- live_action_enabled: {dashboard_refresh.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {dashboard_refresh.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {dashboard_refresh.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {dashboard_refresh.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {dashboard_refresh.get('next_required_milestone')}",
            f"- Warning: {dashboard_refresh.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed Recurring Observation Loop Contract",
            "",
            f"- recurring_observation_loop_contract_defined: {recurring_loop.get('recurring_observation_loop_contract_defined')}",
            f"- recurrence_policy_defined: {recurring_loop.get('recurrence_policy_defined')}",
            f"- recurrence_enabled: {recurring_loop.get('recurrence_enabled')}",
            f"- scheduler_enabled: {recurring_loop.get('scheduler_enabled')}",
            f"- daemon_enabled: {recurring_loop.get('daemon_enabled')}",
            f"- auto_run_enabled: {recurring_loop.get('auto_run_enabled')}",
            f"- manual_local_simulation_only: {recurring_loop.get('manual_local_simulation_only')}",
            f"- allowed_observation_sources_defined: {recurring_loop.get('allowed_observation_sources_defined')}",
            f"- tick_governance_gate_defined: {recurring_loop.get('tick_governance_gate_defined')}",
            f"- simulated_observation_tick_defined: {recurring_loop.get('simulated_observation_tick_defined')}",
            f"- simulated_tick_cieu_event_defined: {recurring_loop.get('simulated_tick_cieu_event_defined')}",
            f"- simulated_tick_residual_delta_defined: {recurring_loop.get('simulated_tick_residual_delta_defined')}",
            f"- stop_abort_conditions_defined: {recurring_loop.get('stop_abort_conditions_defined')}",
            f"- escalation_conditions_defined: {recurring_loop.get('escalation_conditions_defined')}",
            f"- manual_enablement_checklist_defined: {recurring_loop.get('manual_enablement_checklist_defined')}",
            f"- real_action_executed: {recurring_loop.get('real_action_executed')}",
            f"- external_action_executed: {recurring_loop.get('external_action_executed')}",
            f"- live_action_enabled: {recurring_loop.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {recurring_loop.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {recurring_loop.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {recurring_loop.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {recurring_loop.get('next_required_milestone')}",
            f"- Warning: {recurring_loop.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Manual Recurring Observation Tick Runner",
            "",
            f"- manual_tick_runner_contract_defined: {manual_tick.get('manual_tick_runner_contract_defined')}",
            f"- manual_tick_request_defined: {manual_tick.get('manual_tick_request_defined')}",
            f"- manual_tick_preflight_defined: {manual_tick.get('manual_tick_preflight_defined')}",
            f"- manual_tick_source_validation_defined: {manual_tick.get('manual_tick_source_validation_defined')}",
            f"- manual_tick_governance_decision_defined: {manual_tick.get('manual_tick_governance_decision_defined')}",
            f"- manual_tick_result_defined: {manual_tick.get('manual_tick_result_defined')}",
            f"- manual_tick_dashboard_delta_defined: {manual_tick.get('manual_tick_dashboard_delta_defined')}",
            f"- manual_tick_work_candidates_defined: {manual_tick.get('manual_tick_work_candidates_defined')}",
            f"- manual_tick_cieu_event_defined: {manual_tick.get('manual_tick_cieu_event_defined')}",
            f"- manual_tick_residual_delta_defined: {manual_tick.get('manual_tick_residual_delta_defined')}",
            f"- manual_tick_run_receipt_defined: {manual_tick.get('manual_tick_run_receipt_defined')}",
            f"- manual_tick_history_index_defined: {manual_tick.get('manual_tick_history_index_defined')}",
            f"- manual_trigger_required: {manual_tick.get('manual_trigger_required')}",
            f"- one_tick_per_invocation: {manual_tick.get('one_tick_per_invocation')}",
            f"- total_recorded_ticks: {manual_tick.get('total_recorded_ticks')}",
            f"- recurrence_enabled: {manual_tick.get('recurrence_enabled')}",
            f"- scheduler_enabled: {manual_tick.get('scheduler_enabled')}",
            f"- daemon_enabled: {manual_tick.get('daemon_enabled')}",
            f"- auto_run_enabled: {manual_tick.get('auto_run_enabled')}",
            f"- manual_local_run_only: {manual_tick.get('manual_local_run_only')}",
            f"- real_action_executed: {manual_tick.get('real_action_executed')}",
            f"- external_action_executed: {manual_tick.get('external_action_executed')}",
            f"- live_action_enabled: {manual_tick.get('live_action_enabled')}",
            f"- cieu_persistence_enabled: {manual_tick.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {manual_tick.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {manual_tick.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {manual_tick.get('next_required_milestone')}",
            f"- Warning: {manual_tick.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Field Functional Archaeology",
            "",
            f"- field_functional_archaeology_defined: {field_functional.get('field_functional_archaeology_defined')}",
            f"- repos_scanned: {field_functional.get('repos_scanned')}",
            f"- assets_scanned: {field_functional.get('assets_scanned')}",
            f"- field_functional_assets_found: {field_functional.get('field_functional_assets_found')}",
            f"- reuse_candidates_count: {field_functional.get('reuse_candidates_count')}",
            f"- wrap_candidates_count: {field_functional.get('wrap_candidates_count')}",
            f"- rewrite_candidates_count: {field_functional.get('rewrite_candidates_count')}",
            f"- concept_reference_count: {field_functional.get('concept_reference_count')}",
            f"- do_not_absorb_count: {field_functional.get('do_not_absorb_count')}",
            f"- mission_projection_merge_plan_defined: {field_functional.get('mission_projection_merge_plan_defined')}",
            f"- ready_for_L5_projection_harness: {field_functional.get('ready_for_L5_projection_harness')}",
            f"- live_action_enabled: {field_functional.get('live_action_enabled')}",
            f"- external_action_enabled: {field_functional.get('external_action_enabled')}",
            f"- cieu_persistence_enabled: {field_functional.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {field_functional.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {field_functional.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {field_functional.get('next_required_milestone')}",
            f"- Warning: {field_functional.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Mission Field Projection Harness",
            "",
            f"- mission_field_projection_harness_defined: {mission_projection.get('mission_field_projection_harness_defined')}",
            f"- l5_1_projection_contract_defined: {mission_projection.get('l5_1_projection_contract_defined')}",
            f"- layered_projection_trace_generated: {mission_projection.get('layered_projection_trace_generated')}",
            f"- pre_u_adapter_candidate_generated: {mission_projection.get('pre_u_adapter_candidate_generated')}",
            f"- residual_delta_fixture_generated: {mission_projection.get('residual_delta_fixture_generated')}",
            f"- action_layer_projection_only: {mission_projection.get('action_layer_projection_only')}",
            f"- action_field_execution_implemented: {mission_projection.get('action_field_execution_implemented')}",
            f"- ready_for_L5_2_field_functional_auto_projection_core: {mission_projection.get('ready_for_L5_2_field_functional_auto_projection_core')}",
            f"- deep_xt_model_is_not_l5_2_main_milestone: {mission_projection.get('deep_xt_model_is_not_l5_2_main_milestone')}",
            f"- live_execution_enabled: {mission_projection.get('live_execution_enabled')}",
            f"- external_action_enabled: {mission_projection.get('external_action_enabled')}",
            f"- network_enabled: {mission_projection.get('network_enabled')}",
            f"- scheduler_enabled: {mission_projection.get('scheduler_enabled')}",
            f"- daemon_enabled: {mission_projection.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {mission_projection.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {mission_projection.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {mission_projection.get('memory_ingestion_enabled')}",
            f"- next_required_milestone: {mission_projection.get('next_required_milestone')}",
            f"- Warning: {mission_projection.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Field Functional Auto-Projection Core",
            "",
            f"- field_functional_auto_projection_core_defined: {field_projection.get('field_functional_auto_projection_core_defined')}",
            f"- mission_level_y_star_input_defined: {field_projection.get('mission_level_y_star_input_defined')}",
            f"- mission_to_behavior_projection_generated: {field_projection.get('mission_to_behavior_projection_generated')}",
            f"- projection_layers: {', '.join(field_projection.get('projection_layers', []))}",
            f"- behavior_level_y_star_candidate_generated: {field_projection.get('behavior_level_y_star_candidate_generated')}",
            f"- pre_u_packet_candidate_from_behavior_y_star_generated: {field_projection.get('pre_u_packet_candidate_from_behavior_y_star_generated')}",
            f"- residual_delta_loop_fixture_generated: {field_projection.get('residual_delta_loop_fixture_generated')}",
            f"- learning_candidate_stub_generated_but_not_approved: {field_projection.get('learning_candidate_stub_generated_but_not_approved')}",
            f"- live_execution_enabled: {field_projection.get('live_execution_enabled')}",
            f"- external_action_enabled: {field_projection.get('external_action_enabled')}",
            f"- network_enabled: {field_projection.get('network_enabled')}",
            f"- scheduler_enabled: {field_projection.get('scheduler_enabled')}",
            f"- daemon_enabled: {field_projection.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {field_projection.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {field_projection.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {field_projection.get('memory_ingestion_enabled')}",
            f"- behavior_execution_enabled: {field_projection.get('behavior_execution_enabled')}",
            f"- l6_revenue_opportunity_discovery_enabled: {field_projection.get('l6_revenue_opportunity_discovery_enabled')}",
            f"- ready_for_l5_3_projection_checked_autonomous_cycle: {field_projection.get('ready_for_l5_3_projection_checked_autonomous_cycle')}",
            f"- next_required_milestone: {field_projection.get('next_required_milestone')}",
            f"- Warning: {field_projection.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Projection-Checked Autonomous Work Cycle",
            "",
            f"- projection_checked_autonomous_work_cycle_defined: {projection_cycle.get('projection_checked_autonomous_work_cycle_defined')}",
            f"- behavior_y_star_consumed_by_cycle: {projection_cycle.get('behavior_y_star_consumed_by_cycle')}",
            f"- work_proposal_checked_against_behavior_y_star: {projection_cycle.get('work_proposal_checked_against_behavior_y_star')}",
            f"- pre_u_packet_candidate_generated: {projection_cycle.get('pre_u_packet_candidate_generated')}",
            f"- dry_run_gate_decision_generated: {projection_cycle.get('dry_run_gate_decision_generated')}",
            f"- dry_run_result_generated: {projection_cycle.get('dry_run_result_generated')}",
            f"- cieu_like_event_fixture_generated: {projection_cycle.get('cieu_like_event_fixture_generated')}",
            f"- residual_delta_generated: {projection_cycle.get('residual_delta_generated')}",
            f"- learning_review_candidate_generated_but_not_approved: {projection_cycle.get('learning_review_candidate_generated_but_not_approved')}",
            f"- live_execution_enabled: {projection_cycle.get('live_execution_enabled')}",
            f"- external_action_enabled: {projection_cycle.get('external_action_enabled')}",
            f"- network_enabled: {projection_cycle.get('network_enabled')}",
            f"- scheduler_enabled: {projection_cycle.get('scheduler_enabled')}",
            f"- daemon_enabled: {projection_cycle.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {projection_cycle.get('cieu_persistence_enabled')}",
            f"- brain_writeback_enabled: {projection_cycle.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {projection_cycle.get('memory_ingestion_enabled')}",
            f"- behavior_execution_enabled: {projection_cycle.get('behavior_execution_enabled')}",
            f"- ready_for_l5_4_review_gated_learning_loop: {projection_cycle.get('ready_for_l5_4_review_gated_learning_loop')}",
            f"- next_required_milestone: {projection_cycle.get('next_required_milestone')}",
            f"- Warning: {projection_cycle.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Integrated Review-Gated Shadow Learning Cycle",
            "",
            f"- integrated_review_gated_shadow_learning_cycle_defined: {shadow_learning_cycle.get('integrated_review_gated_shadow_learning_cycle_defined')}",
            f"- l5_3_residual_consumed: {shadow_learning_cycle.get('l5_3_residual_consumed')}",
            f"- deterministic_review_gate_decision_generated: {shadow_learning_cycle.get('deterministic_review_gate_decision_generated')}",
            f"- review_gate_decision: {shadow_learning_cycle.get('review_gate_decision')}",
            f"- learning_target_classification_generated: {shadow_learning_cycle.get('learning_target_classification_generated')}",
            f"- projection_policy_update_candidate_generated: {shadow_learning_cycle.get('projection_policy_update_candidate_generated')}",
            f"- shadow_projection_policy_patch_generated: {shadow_learning_cycle.get('shadow_projection_policy_patch_generated')}",
            f"- shadow_behavior_y_star_preview_generated: {shadow_learning_cycle.get('shadow_behavior_y_star_preview_generated')}",
            f"- shadow_updated_projection_cycle_generated: {shadow_learning_cycle.get('shadow_updated_projection_cycle_generated')}",
            f"- original_vs_shadow_cycle_comparison_generated: {shadow_learning_cycle.get('original_vs_shadow_cycle_comparison_generated')}",
            f"- integrated_cieu_like_fixture_generated: {shadow_learning_cycle.get('integrated_cieu_like_fixture_generated')}",
            f"- candidate_approved: {shadow_learning_cycle.get('candidate_approved')}",
            f"- candidate_applied: {shadow_learning_cycle.get('candidate_applied')}",
            f"- canonical_policy_mutation_enabled: {shadow_learning_cycle.get('canonical_policy_mutation_enabled')}",
            f"- brain_writeback_enabled: {shadow_learning_cycle.get('brain_writeback_enabled')}",
            f"- memory_ingestion_enabled: {shadow_learning_cycle.get('memory_ingestion_enabled')}",
            f"- live_execution_enabled: {shadow_learning_cycle.get('live_execution_enabled')}",
            f"- behavior_execution_enabled: {shadow_learning_cycle.get('behavior_execution_enabled')}",
            f"- external_action_enabled: {shadow_learning_cycle.get('external_action_enabled')}",
            f"- network_enabled: {shadow_learning_cycle.get('network_enabled')}",
            f"- scheduler_enabled: {shadow_learning_cycle.get('scheduler_enabled')}",
            f"- daemon_enabled: {shadow_learning_cycle.get('daemon_enabled')}",
            f"- cieu_persistence_enabled: {shadow_learning_cycle.get('cieu_persistence_enabled')}",
            f"- previous_residual_influenced_shadow_projection: {shadow_learning_cycle.get('previous_residual_influenced_shadow_projection')}",
            f"- ready_for_controlled_canonical_learning_design: {shadow_learning_cycle.get('ready_for_controlled_canonical_learning_design')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {shadow_learning_cycle.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {shadow_learning_cycle.get('next_required_milestone')}",
            f"- Warning: {shadow_learning_cycle.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Cross-Repo Governance Contract Proof",
            "",
            f"- cross_repo_governance_contract_proof_defined: {cross_repo_governance.get('cross_repo_governance_contract_proof_defined')}",
            f"- y_star_gov_surfaces_inventoried_read_only: {cross_repo_governance.get('y_star_gov_surfaces_inventoried_read_only')}",
            f"- gov_mcp_surfaces_inventoried_read_only: {cross_repo_governance.get('gov_mcp_surfaces_inventoried_read_only')}",
            f"- behavior_y_star_mapped_to_governance_contract: {cross_repo_governance.get('behavior_y_star_mapped_to_governance_contract')}",
            f"- pre_u_candidates_mapped_to_validator_expectations: {cross_repo_governance.get('pre_u_candidates_mapped_to_validator_expectations')}",
            f"- cieu_fixtures_mapped_to_prediction_delta_expectations: {cross_repo_governance.get('cieu_fixtures_mapped_to_prediction_delta_expectations')}",
            f"- gov_mcp_boundary_mapped: {cross_repo_governance.get('gov_mcp_boundary_mapped')}",
            f"- non_bypass_invariants_defined: {cross_repo_governance.get('non_bypass_invariants_defined')}",
            f"- bypass_risks_identified: {cross_repo_governance.get('bypass_risks_identified')}",
            f"- no_non_ystar_company_repo_modified: {cross_repo_governance.get('no_non_ystar_company_repo_modified')}",
            f"- no_mcp_server_or_tool_executed: {cross_repo_governance.get('no_mcp_server_or_tool_executed')}",
            f"- ready_for_l5_6_governed_mcp_dry_run_adapter: {cross_repo_governance.get('ready_for_l5_6_governed_mcp_dry_run_adapter')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {cross_repo_governance.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {cross_repo_governance.get('next_required_milestone')}",
            f"- Warning: {cross_repo_governance.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governed MCP Dry-Run Adapter",
            "",
            f"- l5_6_governed_mcp_dry_run_adapter_defined: {governed_mcp_adapter.get('l5_6_governed_mcp_dry_run_adapter_defined')}",
            f"- behavior_y_star_loaded: {governed_mcp_adapter.get('behavior_y_star_loaded')}",
            f"- mcp_request_intent_generated: {governed_mcp_adapter.get('mcp_request_intent_generated')}",
            f"- mcp_pre_u_packet_candidate_generated: {governed_mcp_adapter.get('mcp_pre_u_packet_candidate_generated')}",
            f"- dry_run_governance_decision_envelope_generated: {governed_mcp_adapter.get('dry_run_governance_decision_envelope_generated')}",
            f"- bridge_authorization_receipt_generated: {governed_mcp_adapter.get('bridge_authorization_receipt_generated')}",
            f"- governed_mcp_call_candidate_generated: {governed_mcp_adapter.get('governed_mcp_call_candidate_generated')}",
            f"- real_mcp_execution_blocked: {governed_mcp_adapter.get('real_mcp_execution_blocked')}",
            f"- mcp_dry_run_receipt_generated: {governed_mcp_adapter.get('mcp_dry_run_receipt_generated')}",
            f"- mcp_cieu_like_event_generated: {governed_mcp_adapter.get('mcp_cieu_like_event_generated')}",
            f"- mcp_residual_delta_generated: {governed_mcp_adapter.get('mcp_residual_delta_generated')}",
            f"- review_only_mcp_learning_candidate_generated: {governed_mcp_adapter.get('review_only_mcp_learning_candidate_generated')}",
            f"- y_star_gov_unmodified: {governed_mcp_adapter.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {governed_mcp_adapter.get('gov_mcp_unmodified')}",
            f"- mcp_server_not_started: {governed_mcp_adapter.get('mcp_server_not_started')}",
            f"- mcp_tool_not_executed: {governed_mcp_adapter.get('mcp_tool_not_executed')}",
            f"- mcp_resource_not_mutated: {governed_mcp_adapter.get('mcp_resource_not_mutated')}",
            f"- ready_for_l5_7_controlled_canonical_learning_design: {governed_mcp_adapter.get('ready_for_l5_7_controlled_canonical_learning_design')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {governed_mcp_adapter.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {governed_mcp_adapter.get('next_required_milestone')}",
            f"- Warning: {governed_mcp_adapter.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Controlled Canonical Learning Design",
            "",
            f"- l5_7_controlled_canonical_learning_design_defined: {controlled_canonical_learning.get('l5_7_controlled_canonical_learning_design_defined')}",
            f"- y_star_non_mutation_invariant_defined: {controlled_canonical_learning.get('y_star_non_mutation_invariant_defined')}",
            f"- canonical_learning_target_registry_generated: {controlled_canonical_learning.get('canonical_learning_target_registry_generated')}",
            f"- promotion_evidence_bundle_generated: {controlled_canonical_learning.get('promotion_evidence_bundle_generated')}",
            f"- promotion_eligibility_gate_generated: {controlled_canonical_learning.get('promotion_eligibility_gate_generated')}",
            f"- canonical_update_package_candidate_generated: {controlled_canonical_learning.get('canonical_update_package_candidate_generated')}",
            f"- versioned_patch_plan_generated: {controlled_canonical_learning.get('versioned_patch_plan_generated')}",
            f"- rollback_audit_plan_generated: {controlled_canonical_learning.get('rollback_audit_plan_generated')}",
            f"- post_promotion_validation_plan_generated: {controlled_canonical_learning.get('post_promotion_validation_plan_generated')}",
            f"- dry_run_promotion_fixture_generated: {controlled_canonical_learning.get('dry_run_promotion_fixture_generated')}",
            f"- candidate_approved: {controlled_canonical_learning.get('candidate_approved')}",
            f"- candidate_applied: {controlled_canonical_learning.get('candidate_applied')}",
            f"- canonical_policy_mutation_performed: {controlled_canonical_learning.get('canonical_policy_mutation_performed')}",
            f"- canonical_update_application_performed: {controlled_canonical_learning.get('canonical_update_application_performed')}",
            f"- brain_writeback_performed: {controlled_canonical_learning.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {controlled_canonical_learning.get('memory_ingestion_performed')}",
            f"- strategy_mutation_performed: {controlled_canonical_learning.get('strategy_mutation_performed')}",
            f"- y_star_direct_mutation_performed: {controlled_canonical_learning.get('y_star_direct_mutation_performed')}",
            f"- y_star_gov_unmodified: {controlled_canonical_learning.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {controlled_canonical_learning.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_8_approved_canonical_update_sandbox: {controlled_canonical_learning.get('ready_for_l5_8_approved_canonical_update_sandbox')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {controlled_canonical_learning.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {controlled_canonical_learning.get('next_required_milestone')}",
            f"- Warning: {controlled_canonical_learning.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Approved Canonical Update Sandbox",
            "",
            f"- l5_8_approved_canonical_update_sandbox_defined: {approved_sandbox_update.get('l5_8_approved_canonical_update_sandbox_defined')}",
            f"- sandbox_approval_fixture_generated: {approved_sandbox_update.get('sandbox_approval_fixture_generated')}",
            f"- sandbox_baseline_generated: {approved_sandbox_update.get('sandbox_baseline_generated')}",
            f"- sandbox_patch_applied: {approved_sandbox_update.get('sandbox_patch_applied')}",
            f"- real_canonical_state_unchanged: {approved_sandbox_update.get('real_canonical_state_unchanged')}",
            f"- y_star_non_mutation_invariant_preserved: {approved_sandbox_update.get('y_star_non_mutation_invariant_preserved')}",
            f"- sandbox_post_update_validation_generated: {approved_sandbox_update.get('sandbox_post_update_validation_generated')}",
            f"- sandbox_behavior_y_star_reprojection_generated: {approved_sandbox_update.get('sandbox_behavior_y_star_reprojection_generated')}",
            f"- sandbox_governed_mcp_preview_generated: {approved_sandbox_update.get('sandbox_governed_mcp_preview_generated')}",
            f"- sandbox_update_cieu_like_fixture_generated: {approved_sandbox_update.get('sandbox_update_cieu_like_fixture_generated')}",
            f"- sandbox_rollback_validation_generated: {approved_sandbox_update.get('sandbox_rollback_validation_generated')}",
            f"- original_vs_sandbox_vs_rollback_comparison_generated: {approved_sandbox_update.get('original_vs_sandbox_vs_rollback_comparison_generated')}",
            f"- real_candidate_approved: {approved_sandbox_update.get('real_candidate_approved')}",
            f"- real_candidate_applied: {approved_sandbox_update.get('real_candidate_applied')}",
            f"- real_canonical_policy_mutation_performed: {approved_sandbox_update.get('real_canonical_policy_mutation_performed')}",
            f"- real_canonical_update_application_performed: {approved_sandbox_update.get('real_canonical_update_application_performed')}",
            f"- brain_writeback_performed: {approved_sandbox_update.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {approved_sandbox_update.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {approved_sandbox_update.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {approved_sandbox_update.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {approved_sandbox_update.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_9_real_approval_workflow_boundary: {approved_sandbox_update.get('ready_for_l5_9_real_approval_workflow_boundary')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {approved_sandbox_update.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {approved_sandbox_update.get('next_required_milestone')}",
            f"- Warning: {approved_sandbox_update.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Real Approval Workflow Boundary",
            "",
            f"- l5_9_real_approval_workflow_boundary_defined: {real_approval_workflow.get('l5_9_real_approval_workflow_boundary_defined')}",
            f"- approval_authority_model_generated: {real_approval_workflow.get('approval_authority_model_generated')}",
            f"- approval_evidence_dossier_generated: {real_approval_workflow.get('approval_evidence_dossier_generated')}",
            f"- durable_approval_record_contract_generated: {real_approval_workflow.get('durable_approval_record_contract_generated')}",
            f"- approval_decision_packet_fixture_generated: {real_approval_workflow.get('approval_decision_packet_fixture_generated')}",
            f"- validity_revocation_policy_generated: {real_approval_workflow.get('validity_revocation_policy_generated')}",
            f"- pre_application_snapshot_policy_generated: {real_approval_workflow.get('pre_application_snapshot_policy_generated')}",
            f"- real_application_boundary_gate_generated: {real_approval_workflow.get('real_application_boundary_gate_generated')}",
            f"- post_approval_preflight_validation_plan_generated: {real_approval_workflow.get('post_approval_preflight_validation_plan_generated')}",
            f"- manual_approval_runbook_generated: {real_approval_workflow.get('manual_approval_runbook_generated')}",
            f"- approval_workflow_cieu_like_fixture_generated: {real_approval_workflow.get('approval_workflow_cieu_like_fixture_generated')}",
            f"- real_approval_granted: {real_approval_workflow.get('real_approval_granted')}",
            f"- real_application_authorized: {real_approval_workflow.get('real_application_authorized')}",
            f"- durable_approval_record_written: {real_approval_workflow.get('durable_approval_record_written')}",
            f"- real_canonical_policy_mutation_performed: {real_approval_workflow.get('real_canonical_policy_mutation_performed')}",
            f"- real_canonical_update_application_performed: {real_approval_workflow.get('real_canonical_update_application_performed')}",
            f"- brain_writeback_performed: {real_approval_workflow.get('brain_writeback_performed')}",
            f"- memory_ingestion_performed: {real_approval_workflow.get('memory_ingestion_performed')}",
            f"- direct_y_star_mutation_performed: {real_approval_workflow.get('direct_y_star_mutation_performed')}",
            f"- y_star_gov_unmodified: {real_approval_workflow.get('y_star_gov_unmodified')}",
            f"- gov_mcp_unmodified: {real_approval_workflow.get('gov_mcp_unmodified')}",
            f"- ready_for_l5_10_controlled_approval_record_sandbox: {real_approval_workflow.get('ready_for_l5_10_controlled_approval_record_sandbox')}",
            f"- ready_for_l6_revenue_opportunity_discovery: {real_approval_workflow.get('ready_for_l6_revenue_opportunity_discovery')}",
            f"- next_required_milestone: {real_approval_workflow.get('next_required_milestone')}",
            f"- Warning: {real_approval_workflow.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governance Boundary",
            "",
            snapshot["governance_summary"]["principle"],
            "",
            "## Data Safety Boundary",
            "",
            "Console reads curated read-model files only. It must not read DBs, logs, active-agent markers, daemon state, or raw runtime state directly.",
            "",
            "## Next Recommended Steps",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in readiness["recommended_next_steps"]])
    lines.extend(["", "## Warnings / Gaps", ""])
    for item in snapshot["warnings"] + snapshot["open_gaps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def print_report(status: str, files_read: list[str], generated_files: list[str], agents: list[str], warnings: list[str]) -> None:
    print(f"Team Console Snapshot Loader: {status}")
    print(f"Files read: {len(files_read)}")
    print(f"Files generated: {len(generated_files)}")
    print(f"Agents included: {', '.join(agents)}")
    print(f"Warnings: {len(warnings)}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    print("\nFiles read:")
    for item in files_read:
        print(f"- {item}")
    print("\nFiles generated:")
    for item in generated_files:
        print(f"- {item}")


def main() -> int:
    try:
        files_read, generated_files, agents, warnings = build()
    except Exception as exc:
        print(f"Team Console Snapshot Loader: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report("PASS", files_read, generated_files, agents, warnings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
