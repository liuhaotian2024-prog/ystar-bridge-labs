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
            "first governed read-only observation tool wrapper",
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
