#!/usr/bin/env python3
"""Run labs-side runtime governance acceptance checks in dry-run mode only."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "labs_runtime_acceptance" / "generated"
REPORT_JSON = GENERATED / "labs_runtime_acceptance_report.json"
REPORT_MD = GENERATED / "labs_runtime_acceptance_report.md"
MANIFEST_JSON = GENERATED / "labs_runtime_acceptance_manifest.json"

SAFETY_ASSERTIONS = {
    "action_executed": False,
    "cieu_written": False,
    "brain_writeback_performed": False,
    "memory_ingestion_performed": False,
    "raw_runtime_artifacts_ingested": False,
}


@dataclass(frozen=True)
class AcceptanceCheck:
    label: str
    command: list[str]


ACCEPTANCE_CHECKS = [
    AcceptanceCheck(
        "Build quarantine manifest",
        ["python3", "runtime_artifact_quarantine/tools/build_runtime_artifact_manifest.py"],
    ),
    AcceptanceCheck(
        "Build safe mining candidates",
        ["python3", "runtime_artifact_quarantine/safe_mining/tools/build_markdown_report_candidates.py"],
    ),
    AcceptanceCheck(
        "Build candidate review queue",
        ["python3", "runtime_artifact_quarantine/safe_mining/review_queue/tools/build_candidate_review_queue.py"],
    ),
    AcceptanceCheck(
        "Build backlog disposition",
        ["python3", "runtime_artifact_quarantine/backlog_disposition/tools/build_artifact_disposition_index.py"],
    ),
    AcceptanceCheck(
        "Build evidence review pack",
        ["python3", "runtime_artifact_quarantine/evidence_review/tools/build_evidence_review_pack.py"],
    ),
    AcceptanceCheck(
        "Build multi-role Pre-U packets",
        ["python3", "labs_governance_bridge/pre_u_generator/tools/build_pre_u_packets.py"],
    ),
    AcceptanceCheck(
        "Build hook envelopes",
        ["python3", "labs_governance_bridge/pre_u_generator/tools/build_hook_envelopes_from_packets.py"],
    ),
    AcceptanceCheck(
        "Run multi-role governance dry-run",
        ["python3", "labs_governance_bridge/pre_u_generator/tools/run_pre_u_governance_dry_run.py"],
    ),
    AcceptanceCheck(
        "Build console snapshot",
        ["python3", "console_read_model/loader/build_team_console_snapshot.py"],
    ),
    AcceptanceCheck(
        "Static validator",
        ["python3", "console_read_model/validation/validate_team_read_model.py"],
    ),
    AcceptanceCheck(
        "Local safety wrapper",
        ["python3", "console_read_model/checks/run_local_safety_checks.py"],
    ),
    AcceptanceCheck(
        "Targeted acceptance tests",
        [
            "python3",
            "-m",
            "pytest",
            "tests/runtime_artifact_quarantine/test_markdown_report_candidates.py",
            "tests/runtime_artifact_quarantine/test_candidate_review_queue.py",
            "tests/runtime_artifact_quarantine/test_artifact_disposition_index.py",
            "tests/runtime_artifact_quarantine/test_evidence_review_pack.py",
            "tests/labs_governance_bridge/test_labs_gov_bridge.py",
            "tests/labs_governance_bridge/test_pre_u_generator.py",
            "-q",
        ],
    ),
]


def run_check(check: AcceptanceCheck) -> tuple[bool, str]:
    result = subprocess.run(
        check.command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return result.returncode == 0, output


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {relative_path}")
    return data


def build_decision_summary() -> dict[str, Any]:
    pre_u = load_json("console_read_model/generated/pre_u_governance_summary.json")
    return {
        "roles_covered": pre_u.get("roles_covered", []),
        "decision_counts": pre_u.get("decision_counts", {}),
        "decisions_by_role": pre_u.get("decisions_by_role", {}),
    }


def build_report(accepted: bool, checks: list[dict[str, Any]]) -> dict[str, Any]:
    decision_summary = build_decision_summary()
    return {
        "schema_name": "ystar.labs_runtime_acceptance.generated.report",
        "schema_version": "v0",
        "tool": "labs_runtime_acceptance",
        "accepted": accepted,
        "generated_at_policy": "deterministic_no_timestamp",
        "run_label": "labs_runtime_governance_acceptance_v0",
        "checks": checks,
        "quarantine_summary_ref": "console_read_model/generated/quarantine_summary.json",
        "safe_mining_summary_ref": "console_read_model/generated/safe_mining_summary.json",
        "review_queue_summary_ref": "console_read_model/generated/review_queue_summary.json",
        "disposition_summary_ref": "console_read_model/generated/artifact_disposition_summary.json",
        "evidence_review_summary_ref": "console_read_model/generated/evidence_review_summary.json",
        "pre_u_governance_summary_ref": "console_read_model/generated/pre_u_governance_summary.json",
        "governance_bridge_summary_ref": "console_read_model/generated/governance_bridge_summary.json",
        "console_snapshot_ref": "console_read_model/generated/team_console_snapshot.json",
        "decision_summary": decision_summary,
        "safety_assertions": dict(SAFETY_ASSERTIONS),
        "safety_note": (
            "Dry-run only; no action execution, no CIEU write, no brain/memory mutation, "
            "and no raw runtime artifact ingestion."
        ),
    }


def build_manifest(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.labs_runtime_acceptance.generated.manifest",
        "schema_version": "v0",
        "accepted": report.get("accepted"),
        "generated_reports": [
            "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
            "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.md",
            "labs_runtime_acceptance/generated/labs_runtime_acceptance_manifest.json",
        ],
        "source_summary_refs": [
            report["quarantine_summary_ref"],
            report["safe_mining_summary_ref"],
            report["review_queue_summary_ref"],
            report["disposition_summary_ref"],
            report["evidence_review_summary_ref"],
            report["pre_u_governance_summary_ref"],
            report["governance_bridge_summary_ref"],
            report["console_snapshot_ref"],
        ],
        "checks_count": len(report.get("checks", [])),
        "checks_passed": sum(1 for check in report.get("checks", []) if check.get("status") == "PASS"),
        "generated_at_policy": report.get("generated_at_policy"),
        "safety_assertions": dict(SAFETY_ASSERTIONS),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Labs Runtime Governance Acceptance Report",
        "",
        f"accepted: {report.get('accepted')}",
        f"run_label: {report.get('run_label')}",
        "",
        "## Checks",
        "",
    ]
    for check in report.get("checks", []):
        lines.append(f"- {check['label']}: {check['status']}")
    lines.extend(
        [
            "",
            "## Decision Summary",
            "",
            f"- Roles covered: {', '.join(report.get('decision_summary', {}).get('roles_covered', []))}",
            "- Decision counts:",
        ]
    )
    for decision, count in sorted(report.get("decision_summary", {}).get("decision_counts", {}).items()):
        lines.append(f"  - {decision}: {count}")
    lines.extend(
        [
            "",
            "## Safety Assertions",
            "",
        ]
    )
    for key, value in report.get("safety_assertions", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"Safety note: {report.get('safety_note')}", ""])
    return "\n".join(lines)


def write_outputs(report: dict[str, Any]) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    with REPORT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with REPORT_MD.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))
    manifest = build_manifest(report)
    with MANIFEST_JSON.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def print_failure_output(output: str) -> None:
    if not output:
        return
    print("Output:")
    for line in output.splitlines()[:40]:
        print(f"  {line}")


def main() -> int:
    checks: list[dict[str, Any]] = []
    failures: list[tuple[AcceptanceCheck, str]] = []

    print("Y* Labs Runtime Governance Acceptance")
    print()

    total = len(ACCEPTANCE_CHECKS)
    for index, check in enumerate(ACCEPTANCE_CHECKS, start=1):
        if check.label in {"Static validator", "Local safety wrapper"}:
            interim_report = build_report(False, checks)
            write_outputs(interim_report)

        print(f"[{index}/{total}] {check.label} ... ", end="", flush=True)
        ok, output = run_check(check)
        checks.append(
            {
                "label": check.label,
                "command": check.command,
                "status": "PASS" if ok else "FAIL",
            }
        )
        if ok:
            print("PASS")
            continue

        print("FAIL")
        failures.append((check, output))
        break

    accepted = not failures and len(checks) == len(ACCEPTANCE_CHECKS)
    report = build_report(accepted, checks)
    write_outputs(report)

    print()
    if accepted:
        print("Result: PASS")
        print("Labs governance acceptance: ACCEPTED")
        print(
            "Safety note: dry-run only; no action execution, no CIEU write, "
            "no brain/memory mutation, no raw runtime artifact ingestion."
        )
        return 0

    print("Result: FAIL")
    for check, output in failures:
        print(f"- {check.label}")
        print_failure_output(output)
    return 1


if __name__ == "__main__":
    sys.exit(main())
