#!/usr/bin/env python3
"""Build the disabled CIEU runtime event boundary from curated generated inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "labs_cieu_runtime_boundary" / "generated"
MANIFEST_JSON = GENERATED / "cieu_runtime_boundary_manifest.json"
SUMMARY_JSON = GENERATED / "cieu_runtime_boundary_summary.json"
REPORT_MD = GENERATED / "cieu_runtime_boundary_report.md"
SAMPLE_EVENT_JSON = GENERATED / "sample_cieu_runtime_event.json"
PREDICTION_FIXTURE_JSON = GENERATED / "sample_prediction_delta_fixture.json"

INPUT_REFS = {
    "labs_live_boundary": "labs_live_boundary/generated/live_boundary_manifest.json",
    "live_boundary_summary": "labs_live_boundary/generated/live_boundary_summary.json",
    "live_readiness_report": "labs_live_readiness/generated/live_readiness_report.json",
    "labs_runtime_acceptance": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
    "cross_repo_alignment": "cross_repo_alignment/generated/cross_repo_status_manifest.json",
    "console_snapshot": "console_read_model/generated/team_console_snapshot.json",
}

DISABLED_FLAGS = {
    "dry_run_only": True,
    "persistence_enabled": False,
    "live_action_execution_enabled": False,
    "cieu_write_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "candidate_auto_approval_enabled": False,
    "raw_artifact_ingestion_enabled": False,
}


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {relative_path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def build_sample_event(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    live_boundary = inputs["labs_live_boundary"]
    live_readiness = inputs["live_readiness_report"]
    decision_ref = (
        "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json"
    )
    return {
        "event_id": "cieu-runtime-event-sample-001",
        "event_version": "v0",
        "created_at": "deterministic_no_timestamp",
        "source": {
            "system": "ystar-company",
            "component": "labs_cieu_runtime_boundary",
            "mode": "dry_run_boundary_fixture",
        },
        **DISABLED_FLAGS,
        "Xt": {
            "task_state": "sample_pre_u_governance_dry_run",
            "readiness_ref": "labs_live_readiness/generated/live_readiness_report.json",
        },
        "U": {
            "action_id": "sample-noop-action",
            "action_type": "dry_run_boundary_fixture",
            "action_executed": False,
        },
        "Y_star": "Preserve governance boundaries while preparing future CIEU event recording.",
        "predicted_Y_t1": "A future runtime event can be shaped without persistence.",
        "predicted_R_t1": "Persistence and writeback remain disabled.",
        "actual_Y_t1": "Boundary fixture generated locally only.",
        "actual_R_t1": "No CIEU write, action execution, brain writeback, or memory ingestion occurred.",
        "residual_delta": {
            "status": "structural_fixture_only",
            "semantic_truth_status": "not_evaluated",
            "delta_summary": "No live outcome measured; fixture exists to validate envelope shape.",
        },
        "evidence_refs": [
            "labs_live_boundary/generated/live_boundary_manifest.json",
            "labs_live_readiness/generated/live_readiness_report.json",
        ],
        "governance_decision_ref": decision_ref,
        "live_boundary_ref": "labs_live_boundary/generated/live_boundary_manifest.json",
        "write_policy": {
            "persistence_allowed": False,
            "requires_manual_enablement": True,
            "cieu_writer_boundary": "defined_disabled",
            "brain_writeback_allowed": False,
            "memory_ingestion_allowed": False,
        },
        "validation_status": "boundary_defined_disabled",
        "blocked_reason": "cieu_runtime_boundary_defined_but_persistence_disabled",
        "dependency_status": {
            "live_boundary_defined": live_boundary.get("live_boundary_defined") is True,
            "minimal_live_loop_ready": live_readiness.get("overall_status", {}).get(
                "minimal_live_loop_ready"
            )
            is True,
        },
    }


def build_prediction_fixture(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "prediction_id": "prediction-delta-fixture-001",
        "event_id": event["event_id"],
        "predicted_Y_t1": event["predicted_Y_t1"],
        "actual_Y_t1": event["actual_Y_t1"],
        "predicted_R_t1": event["predicted_R_t1"],
        "actual_R_t1": event["actual_R_t1"],
        "residual_delta": event["residual_delta"],
        "learning_eligibility": False,
        "writeback_policy": {
            "status": "disabled_requires_future_curation",
            "cieu_write_allowed": False,
            "brain_writeback_allowed": False,
            "memory_ingestion_allowed": False,
        },
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "raw_artifact_ingestion_allowed": False,
    }


def build_manifest(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    live_boundary = inputs["labs_live_boundary"]
    live_readiness = inputs["live_readiness_report"]
    labs_acceptance = inputs["labs_runtime_acceptance"]
    cross_repo = inputs["cross_repo_alignment"]
    return {
        "schema_name": "ystar.labs_cieu_runtime_boundary.generated.cieu_runtime_boundary_manifest",
        "schema_version": "v0",
        "generated_at_policy": "deterministic_no_timestamp",
        "cieu_runtime_boundary_defined": True,
        "cieu_runtime_event_schema_defined": True,
        "prediction_delta_fixture_defined": True,
        "cieu_writer_policy_defined": True,
        **DISABLED_FLAGS,
        "requires_manual_enablement": True,
        "minimal_live_loop_ready": False,
        "blocked_reason": "cieu_runtime_boundary_defined_but_persistence_disabled",
        "depends_on": [
            "labs_live_boundary",
            "live_readiness_report",
            "labs_runtime_acceptance",
            "cross_repo_alignment",
        ],
        "dependency_status": {
            "live_boundary_defined": live_boundary.get("live_boundary_defined") is True,
            "live_boundary_cieu_writer_defined": live_boundary.get("cieu_writer_boundary_defined") is True,
            "dry_run_governance_ready": live_readiness.get("overall_status", {}).get(
                "dry_run_governance_ready"
            )
            is True,
            "labs_runtime_acceptance_accepted": labs_acceptance.get("accepted") is True,
            "cross_repo_alignment_accepted": cross_repo.get("alignment_status", {}).get("accepted")
            is True,
        },
        "generated_refs": {
            "summary": "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json",
            "report": "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_report.md",
            "sample_event": "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json",
            "prediction_delta_fixture": (
                "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json"
            ),
        },
        "source_refs": INPUT_REFS,
        "safety_note": (
            "CIEU runtime boundary is defined but persistence is disabled. It does not execute "
            "actions, write CIEU, write brain or memory, approve candidates, or ingest raw artifacts."
        ),
    }


def build_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.labs_cieu_runtime_boundary.generated.cieu_runtime_boundary_summary",
        "schema_version": "v0",
        "cieu_runtime_boundary_defined": manifest["cieu_runtime_boundary_defined"],
        "cieu_runtime_event_schema_defined": manifest["cieu_runtime_event_schema_defined"],
        "prediction_delta_fixture_defined": manifest["prediction_delta_fixture_defined"],
        "cieu_writer_policy_defined": manifest["cieu_writer_policy_defined"],
        "dry_run_only": manifest["dry_run_only"],
        "persistence_enabled": manifest["persistence_enabled"],
        "live_action_execution_enabled": manifest["live_action_execution_enabled"],
        "cieu_write_enabled": manifest["cieu_write_enabled"],
        "brain_writeback_enabled": manifest["brain_writeback_enabled"],
        "memory_ingestion_enabled": manifest["memory_ingestion_enabled"],
        "candidate_auto_approval_enabled": manifest["candidate_auto_approval_enabled"],
        "raw_artifact_ingestion_enabled": manifest["raw_artifact_ingestion_enabled"],
        "requires_manual_enablement": manifest["requires_manual_enablement"],
        "minimal_live_loop_ready": manifest["minimal_live_loop_ready"],
        "blocked_reason": manifest["blocked_reason"],
        "generated_manifest": "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json",
        "generated_sample_event": "labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json",
        "generated_prediction_delta_fixture": (
            "labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json"
        ),
        "warning": manifest["safety_note"],
    }


def render_report(manifest: dict[str, Any], event: dict[str, Any], fixture: dict[str, Any]) -> str:
    lines = [
        "# Labs CIEU Runtime Boundary Report",
        "",
        f"cieu_runtime_boundary_defined: {manifest['cieu_runtime_boundary_defined']}",
        f"dry_run_only: {manifest['dry_run_only']}",
        f"persistence_enabled: {manifest['persistence_enabled']}",
        f"cieu_write_enabled: {manifest['cieu_write_enabled']}",
        f"brain_writeback_enabled: {manifest['brain_writeback_enabled']}",
        f"memory_ingestion_enabled: {manifest['memory_ingestion_enabled']}",
        f"minimal_live_loop_ready: {manifest['minimal_live_loop_ready']}",
        f"requires_manual_enablement: {manifest['requires_manual_enablement']}",
        f"blocked_reason: {manifest['blocked_reason']}",
        "",
        "## Sample Event",
        "",
        f"- event_id: {event['event_id']}",
        f"- validation_status: {event['validation_status']}",
        f"- blocked_reason: {event['blocked_reason']}",
        "",
        "## Prediction Delta Fixture",
        "",
        f"- prediction_id: {fixture['prediction_id']}",
        f"- learning_eligibility: {fixture['learning_eligibility']}",
        f"- curation_required: {fixture['curation_required']}",
        "",
        f"Safety note: {manifest['safety_note']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    inputs = {name: load_json(path) for name, path in INPUT_REFS.items()}
    event = build_sample_event(inputs)
    fixture = build_prediction_fixture(event)
    manifest = build_manifest(inputs)
    summary = build_summary(manifest)

    GENERATED.mkdir(parents=True, exist_ok=True)
    write_json(MANIFEST_JSON, manifest)
    write_json(SUMMARY_JSON, summary)
    write_json(SAMPLE_EVENT_JSON, event)
    write_json(PREDICTION_FIXTURE_JSON, fixture)
    with REPORT_MD.open("w", encoding="utf-8") as handle:
        handle.write(render_report(manifest, event, fixture))

    print("Labs CIEU Runtime Boundary Builder: PASS")
    print(f"cieu_runtime_boundary_defined: {manifest['cieu_runtime_boundary_defined']}")
    print(f"dry_run_only: {manifest['dry_run_only']}")
    print(f"persistence_enabled: {manifest['persistence_enabled']}")
    print(f"cieu_write_enabled: {manifest['cieu_write_enabled']}")
    print(f"blocked_reason: {manifest['blocked_reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
