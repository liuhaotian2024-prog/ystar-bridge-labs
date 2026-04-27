#!/usr/bin/env python3
"""Build the labs live-readiness gate report from curated generated inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "labs_live_readiness" / "generated"
REPORT_JSON = GENERATED / "live_readiness_report.json"
REPORT_MD = GENERATED / "live_readiness_report.md"
BACKLOG_JSON = GENERATED / "transition_backlog.json"
MANIFEST_JSON = GENERATED / "live_readiness_manifest.json"


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


def dry_run_readiness(inputs: dict[str, dict[str, Any]]) -> dict[str, bool]:
    cross = inputs["cross_repo_alignment"]
    labs_acceptance = inputs["labs_acceptance"]
    pre_u = inputs["pre_u_governance"]
    console = inputs["console_snapshot"]
    disposition = inputs["disposition"]
    evidence = inputs["evidence_scores"]
    return {
        "ystar_gov_endpoint_accepted": cross.get("ystar_gov_endpoint_acceptance", {}).get("accepted") is True,
        "labs_runtime_acceptance_accepted": labs_acceptance.get("accepted") is True,
        "cross_repo_alignment_accepted": cross.get("alignment_status", {}).get("accepted") is True,
        "multi_role_pre_u_governance_ready": (
            pre_u.get("summary", {}).get("dry_run_only") is True
            and pre_u.get("summary", {}).get("snapshots_created") == 3
        ),
        "console_read_model_ready": console.get("schema_name") == "ystar.console_read_model.generated.team_console_snapshot",
        "quarantine_disposition_ready": (
            disposition.get("summary", {}).get("total_artifacts")
            == disposition.get("summary", {}).get("artifacts_with_disposition")
        ),
        "evidence_review_ready": evidence.get("summary", {}).get("automatic_approvals") == 0,
    }


def build_transition_backlog() -> dict[str, Any]:
    phases = [
        (
            "live_boundary_harness",
            [
                ("live-boundary-001", "real hook boundary contract", "hook ambiguity can bypass Y-star-gov judgment"),
                ("live-boundary-002", "action sandbox dry-run-to-live switch guard", "dry-run packets could be mistaken for executable actions"),
                ("live-boundary-003", "operator approval gate", "live actions could start without human authorization"),
                ("live-boundary-004", "rollback/abort policy", "failed live actions may not have a controlled stop path"),
            ],
        ),
        (
            "cieu_runtime_event_bridge",
            [
                ("cieu-runtime-001", "CIEU event writer interface", "outcomes cannot be recorded through a governed writer"),
                ("cieu-runtime-002", "prediction_delta runtime event schema", "predicted-vs-actual evidence may be malformed"),
                ("cieu-runtime-003", "CIEU log verification", "records may be unverifiable or incomplete"),
                ("cieu-runtime-004", "no direct brain writeback rule", "runtime evidence could bypass review"),
            ],
        ),
        (
            "memory_brain_writeback_governance",
            [
                ("writeback-gov-001", "review decision application", "candidate hints could be applied without a signed decision"),
                ("writeback-gov-002", "approved hint migration candidate", "weak hints could become canonical memory"),
                ("writeback-gov-003", "schema validation before memory/capsule update", "brain capsules could drift structurally"),
                ("writeback-gov-004", "manual approval requirement", "automation could approve its own memory writes"),
            ],
        ),
        (
            "external_executor_adapter",
            [
                ("executor-adapter-001", "Codex/Claude/OpenClaw adapter boundary", "external execution channels could be overbroad"),
                ("executor-adapter-002", "tool allowlist/denylist", "unsafe tools could be invoked"),
                ("executor-adapter-003", "filesystem scope", "live actions could touch unapproved paths"),
                ("executor-adapter-004", "secret policy", "live tools could access credentials without policy"),
            ],
        ),
        (
            "minimal_live_governed_loop_acceptance",
            [
                ("live-loop-001", "live task fixture", "no deterministic live acceptance input exists"),
                ("live-loop-002", "hook gate enforced", "actions could bypass governance"),
                ("live-loop-003", "action sandbox enforced", "live side effects could exceed scope"),
                ("live-loop-004", "CIEU event recorded", "outcome evidence may not exist"),
                ("live-loop-005", "no brain writeback without review", "learning could bypass evidence-backed deltas"),
            ],
        ),
    ]
    items: list[dict[str, Any]] = []
    for phase, entries in phases:
        for item_id, title, risk in entries:
            items.append(
                {
                    "item_id": item_id,
                    "phase": phase,
                    "title": title,
                    "required_before_live": True,
                    "status": "not_started",
                    "risk_if_missing": risk,
                    "allowed_next_step": "design_and_dry_run_boundary_contract",
                    "forbidden_shortcut": "enable_live_runtime_behavior_before_gate_exists",
                }
            )
    return {
        "schema_name": "ystar.labs_live_readiness.generated.transition_backlog",
        "schema_version": "v0",
        "items": items,
        "summary": {
            "items_total": len(items),
            "required_before_live": sum(1 for item in items if item["required_before_live"]),
            "not_started": sum(1 for item in items if item["status"] == "not_started"),
            "phases": {phase: sum(1 for item in items if item["phase"] == phase) for phase, _ in phases},
        },
    }


def build_report(inputs: dict[str, dict[str, Any]], backlog: dict[str, Any]) -> dict[str, Any]:
    readiness = dry_run_readiness(inputs)
    dry_run_ready = all(readiness.values())
    live_execution_blockers = [
        "no_real_hook_gate",
        "no_action_sandbox",
        "no_CIEU_writer",
        "no_CIEU_prediction_delta_runtime_recording",
        "no_brain_writeback_review_application",
        "no_memory_ingestion_policy_application",
        "no_runtime_rollback_boundary",
        "no_live_operator_approval_gate",
        "no_secret_policy_for_live_tools",
        "dirty_runtime_artifacts_not_canonical",
    ]
    safety_booleans = {
        "live_action_execution_allowed": False,
        "live_cieu_write_allowed": False,
        "live_brain_writeback_allowed": False,
        "live_memory_ingestion_allowed": False,
        "candidate_auto_approval_allowed": False,
        "raw_artifact_ingestion_allowed": False,
    }
    return {
        "schema_name": "ystar.labs_live_readiness.generated.live_readiness_report",
        "schema_version": "v0",
        "generated_at_policy": "deterministic_no_timestamp",
        "dry_run_readiness": readiness,
        "live_execution_blockers": live_execution_blockers,
        "safety_booleans": safety_booleans,
        "overall_status": {
            "dry_run_governance_ready": dry_run_ready,
            "minimal_live_loop_ready": False,
            "minimal_live_loop_status": "blocked_until_required_gates_exist",
            "recommended_next_phase": "build_live_boundary_harness_not_runtime_execution",
        },
        "transition_backlog_summary": backlog["summary"],
        "generated_refs": {
            "transition_backlog": "labs_live_readiness/generated/transition_backlog.json",
            "manifest": "labs_live_readiness/generated/live_readiness_manifest.json",
        },
        "source_refs": {
            "cross_repo_alignment": "cross_repo_alignment/generated/cross_repo_status_manifest.json",
            "labs_runtime_acceptance": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
            "pre_u_governance": "labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json",
            "labs_governance_bridge": "labs_governance_bridge/generated/governance_decision_snapshot.json",
            "disposition": "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
            "evidence_scores": "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
            "review_decision_stub": "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
            "hint_routing": "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
            "console_snapshot": "console_read_model/generated/team_console_snapshot.json",
        },
        "warning": "Dry-run governance ready is not live runtime readiness; live execution remains blocked.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Labs Live Readiness Report",
        "",
        f"dry_run_governance_ready: {report['overall_status']['dry_run_governance_ready']}",
        f"minimal_live_loop_ready: {report['overall_status']['minimal_live_loop_ready']}",
        f"minimal_live_loop_status: {report['overall_status']['minimal_live_loop_status']}",
        f"recommended_next_phase: {report['overall_status']['recommended_next_phase']}",
        "",
        "## Dry-Run Readiness",
        "",
    ]
    for key, value in report["dry_run_readiness"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Live Execution Blockers", ""])
    for blocker in report["live_execution_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Safety Booleans", ""])
    for key, value in report["safety_booleans"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"Warning: {report['warning']}", ""])
    return "\n".join(lines)


def build_manifest(report: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.labs_live_readiness.generated.manifest",
        "schema_version": "v0",
        "generated_files": [
            "labs_live_readiness/generated/live_readiness_report.json",
            "labs_live_readiness/generated/live_readiness_report.md",
            "labs_live_readiness/generated/transition_backlog.json",
            "labs_live_readiness/generated/live_readiness_manifest.json",
        ],
        "source_refs": report["source_refs"],
        "dry_run_governance_ready": report["overall_status"]["dry_run_governance_ready"],
        "minimal_live_loop_ready": report["overall_status"]["minimal_live_loop_ready"],
        "transition_backlog_items": backlog["summary"]["items_total"],
        "generated_at_policy": report["generated_at_policy"],
    }


def main() -> int:
    inputs = {
        "cross_repo_alignment": load_json("cross_repo_alignment/generated/cross_repo_status_manifest.json"),
        "labs_acceptance": load_json("labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json"),
        "pre_u_governance": load_json("labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json"),
        "labs_bridge": load_json("labs_governance_bridge/generated/governance_decision_snapshot.json"),
        "disposition": load_json("runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json"),
        "evidence_scores": load_json("runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json"),
        "review_decisions": load_json("runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json"),
        "hint_routing": load_json("runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json"),
        "console_snapshot": load_json("console_read_model/generated/team_console_snapshot.json"),
    }
    backlog = build_transition_backlog()
    report = build_report(inputs, backlog)
    manifest = build_manifest(report, backlog)

    GENERATED.mkdir(parents=True, exist_ok=True)
    write_json(REPORT_JSON, report)
    with REPORT_MD.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))
    write_json(BACKLOG_JSON, backlog)
    write_json(MANIFEST_JSON, manifest)

    print("Labs Live Readiness Builder: PASS")
    print(f"dry_run_governance_ready: {report['overall_status']['dry_run_governance_ready']}")
    print(f"minimal_live_loop_ready: {report['overall_status']['minimal_live_loop_ready']}")
    print(f"minimal_live_loop_status: {report['overall_status']['minimal_live_loop_status']}")
    print(f"transition_backlog_items: {backlog['summary']['items_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

