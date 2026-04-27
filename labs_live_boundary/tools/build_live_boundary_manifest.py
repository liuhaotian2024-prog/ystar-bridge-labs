#!/usr/bin/env python3
"""Build the disabled live-boundary harness manifest from curated generated inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "labs_live_boundary" / "generated"
MANIFEST_JSON = GENERATED / "live_boundary_manifest.json"
SUMMARY_JSON = GENERATED / "live_boundary_summary.json"
REPORT_MD = GENERATED / "live_boundary_report.md"
CHECKLIST_JSON = GENERATED / "live_transition_checklist.json"

INPUT_REFS = {
    "live_readiness_report": "labs_live_readiness/generated/live_readiness_report.json",
    "live_readiness_manifest": "labs_live_readiness/generated/live_readiness_manifest.json",
    "labs_runtime_acceptance": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
    "cross_repo_alignment": "cross_repo_alignment/generated/cross_repo_status_manifest.json",
    "multi_role_pre_u_governance": (
        "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json"
    ),
    "console_snapshot": "console_read_model/generated/team_console_snapshot.json",
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


def build_checklist() -> dict[str, Any]:
    entries = [
        ("live-transition-001", "operator approval gate implementation", "defined_disabled"),
        ("live-transition-002", "action sandbox implementation", "defined_disabled"),
        ("live-transition-003", "rollback/abort implementation", "defined_disabled"),
        ("live-transition-004", "CIEU writer implementation", "defined_disabled"),
        ("live-transition-005", "CIEU verification implementation", "not_started"),
        ("live-transition-006", "no-direct-brain-writeback enforcement", "defined_disabled"),
        ("live-transition-007", "memory ingestion approval policy", "defined_disabled"),
        ("live-transition-008", "live hook adapter test fixture", "not_started"),
        ("live-transition-009", "live acceptance test fixture", "not_started"),
    ]
    items = [
        {
            "item_id": item_id,
            "title": title,
            "status": status,
            "allowed_next_step": "design_and_validate_boundary_without_enabling_live_behavior",
            "forbidden_shortcut": "mark_live_ready_or_execute_action",
        }
        for item_id, title, status in entries
    ]
    status_counts: dict[str, int] = {}
    for item in items:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    return {
        "schema_name": "ystar.labs_live_boundary.generated.live_transition_checklist",
        "schema_version": "v0",
        "allowed_statuses": ["not_started", "defined_disabled"],
        "items": items,
        "summary": {
            "items_total": len(items),
            "status_counts": status_counts,
            "ready_or_enabled_items": 0,
        },
        "warning": "Checklist items are not live, accepted, approved, completed, or enabled.",
    }


def build_manifest(inputs: dict[str, dict[str, Any]], checklist: dict[str, Any]) -> dict[str, Any]:
    live_readiness = inputs["live_readiness_report"]
    labs_acceptance = inputs["labs_runtime_acceptance"]
    cross_repo = inputs["cross_repo_alignment"]
    pre_u = inputs["multi_role_pre_u_governance"]
    readiness_overall = live_readiness.get("overall_status", {})
    pre_u_summary = pre_u.get("summary", {})
    return {
        "schema_name": "ystar.labs_live_boundary.generated.live_boundary_manifest",
        "schema_version": "v0",
        "generated_at_policy": "deterministic_no_timestamp",
        "live_boundary_defined": True,
        "operator_approval_gate_defined": True,
        "action_sandbox_contract_defined": True,
        "rollback_policy_defined": True,
        "cieu_writer_boundary_defined": True,
        "no_brain_memory_writeback_rule_defined": True,
        "live_transition_guard_defined": True,
        "live_action_execution_enabled": False,
        "cieu_write_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "candidate_auto_approval_enabled": False,
        "raw_artifact_ingestion_enabled": False,
        "requires_manual_enablement": True,
        "minimal_live_loop_ready": False,
        "blocked_reason": "required_live_gates_defined_but_disabled",
        "depends_on": [
            "live_readiness_report",
            "labs_runtime_acceptance",
            "cross_repo_alignment",
            "multi_role_pre_u_governance",
        ],
        "dependency_status": {
            "dry_run_governance_ready": readiness_overall.get("dry_run_governance_ready") is True,
            "labs_runtime_acceptance_accepted": labs_acceptance.get("accepted") is True,
            "cross_repo_alignment_accepted": cross_repo.get("alignment_status", {}).get("accepted") is True,
            "multi_role_pre_u_governance_ready": (
                pre_u_summary.get("dry_run_only") is True
                and bool(pre_u_summary.get("roles_covered"))
            ),
        },
        "transition_checklist_ref": "labs_live_boundary/generated/live_transition_checklist.json",
        "source_refs": INPUT_REFS,
        "safety_note": (
            "Live boundary harness is defined but disabled. It does not execute actions, "
            "write CIEU, write brain or memory, approve candidates, or ingest raw artifacts."
        ),
        "checklist_summary": checklist["summary"],
    }


def build_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.labs_live_boundary.generated.live_boundary_summary",
        "schema_version": "v0",
        "live_boundary_defined": manifest["live_boundary_defined"],
        "operator_approval_gate_defined": manifest["operator_approval_gate_defined"],
        "action_sandbox_contract_defined": manifest["action_sandbox_contract_defined"],
        "rollback_policy_defined": manifest["rollback_policy_defined"],
        "cieu_writer_boundary_defined": manifest["cieu_writer_boundary_defined"],
        "live_action_execution_enabled": manifest["live_action_execution_enabled"],
        "cieu_write_enabled": manifest["cieu_write_enabled"],
        "brain_writeback_enabled": manifest["brain_writeback_enabled"],
        "memory_ingestion_enabled": manifest["memory_ingestion_enabled"],
        "candidate_auto_approval_enabled": manifest["candidate_auto_approval_enabled"],
        "raw_artifact_ingestion_enabled": manifest["raw_artifact_ingestion_enabled"],
        "requires_manual_enablement": manifest["requires_manual_enablement"],
        "minimal_live_loop_ready": manifest["minimal_live_loop_ready"],
        "blocked_reason": manifest["blocked_reason"],
        "depends_on": manifest["depends_on"],
        "checklist_status_counts": manifest["checklist_summary"]["status_counts"],
        "ready_or_enabled_checklist_items": manifest["checklist_summary"]["ready_or_enabled_items"],
        "generated_manifest": "labs_live_boundary/generated/live_boundary_manifest.json",
        "generated_checklist": "labs_live_boundary/generated/live_transition_checklist.json",
        "warning": manifest["safety_note"],
    }


def render_report(manifest: dict[str, Any], checklist: dict[str, Any]) -> str:
    lines = [
        "# Labs Live Boundary Report",
        "",
        f"live_boundary_defined: {manifest['live_boundary_defined']}",
        f"live_action_execution_enabled: {manifest['live_action_execution_enabled']}",
        f"cieu_write_enabled: {manifest['cieu_write_enabled']}",
        f"brain_writeback_enabled: {manifest['brain_writeback_enabled']}",
        f"memory_ingestion_enabled: {manifest['memory_ingestion_enabled']}",
        f"minimal_live_loop_ready: {manifest['minimal_live_loop_ready']}",
        f"requires_manual_enablement: {manifest['requires_manual_enablement']}",
        f"blocked_reason: {manifest['blocked_reason']}",
        "",
        "## Transition Checklist",
        "",
    ]
    for item in checklist["items"]:
        lines.append(f"- {item['item_id']}: {item['title']} ({item['status']})")
    lines.extend(["", f"Safety note: {manifest['safety_note']}", ""])
    return "\n".join(lines)


def main() -> int:
    inputs = {name: load_json(path) for name, path in INPUT_REFS.items()}
    checklist = build_checklist()
    manifest = build_manifest(inputs, checklist)
    summary = build_summary(manifest)

    GENERATED.mkdir(parents=True, exist_ok=True)
    write_json(MANIFEST_JSON, manifest)
    write_json(SUMMARY_JSON, summary)
    write_json(CHECKLIST_JSON, checklist)
    with REPORT_MD.open("w", encoding="utf-8") as handle:
        handle.write(render_report(manifest, checklist))

    print("Labs Live Boundary Builder: PASS")
    print(f"live_boundary_defined: {manifest['live_boundary_defined']}")
    print(f"live_action_execution_enabled: {manifest['live_action_execution_enabled']}")
    print(f"minimal_live_loop_ready: {manifest['minimal_live_loop_ready']}")
    print(f"blocked_reason: {manifest['blocked_reason']}")
    print(f"checklist_items: {checklist['summary']['items_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
