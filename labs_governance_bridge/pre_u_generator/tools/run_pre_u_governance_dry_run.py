#!/usr/bin/env python3
"""Run Y-star-gov dry-run judgment for generated multi-role Pre-U envelopes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs_governance_bridge.pre_u_generator.tools.build_hook_envelopes_from_packets import (  # noqa: E402
    ENVELOPE_FILES,
    build_all_envelopes,
)
from labs_governance_bridge.pre_u_generator.tools.build_pre_u_packets import (  # noqa: E402
    ROLE_CONFIG,
    build_all_packets,
)


YSTAR_GOV_CLI = "/Users/haotianliu/.openclaw/workspace/Y-star-gov/tools/run_hook_contract_dry_run.py"
GENERATED_DIR = "labs_governance_bridge/pre_u_generator/generated"
SNAPSHOTS = f"{GENERATED_DIR}/governance_decision_snapshots.json"
SNAPSHOTS_MD = f"{GENERATED_DIR}/governance_decision_snapshots.md"
MANIFEST = f"{GENERATED_DIR}/pre_u_governance_run_manifest.json"


class GovernanceRunError(Exception):
    """Raised when the multi-role governance dry-run cannot complete."""


def load_json(relative_path: str) -> Any:
    with (ROOT / relative_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(relative_path: str, payload: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)


def ensure_inputs() -> None:
    if not all((ROOT / config["packet"]).exists() for config in ROLE_CONFIG.values()):
        build_all_packets()
    if not all((ROOT / path).exists() for path in ENVELOPE_FILES.values()):
        build_all_envelopes()


def call_ystar_gov(envelope_path: str) -> tuple[int, dict[str, Any]]:
    result = subprocess.run(
        ["python3", YSTAR_GOV_CLI, "--input", envelope_path, "--pretty"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        decision = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GovernanceRunError(
            f"Y-star-gov CLI did not return JSON for {envelope_path}: {exc}; stderr={result.stderr.strip()}"
        ) from exc
    if not isinstance(decision, dict):
        raise GovernanceRunError(f"Y-star-gov decision must be object for {envelope_path}")
    return result.returncode, decision


def build_snapshot(agent_id: str, packet: dict[str, Any], envelope_path: str, exit_code: int, decision: dict[str, Any]) -> dict[str, Any]:
    slug = ROLE_CONFIG[agent_id]["slug"]
    return {
        "bridge_run_id": f"preu-governance-{slug}-001",
        "packet_id": packet.get("packet_id"),
        "task_id": packet.get("task_id"),
        "agent_id": agent_id,
        "role": packet.get("role"),
        "ystar_gov_cli_path": YSTAR_GOV_CLI,
        "ystar_gov_exit_code": exit_code,
        "ystar_gov_decision": decision.get("decision"),
        "allow_execution": bool(decision.get("allow_execution")),
        "require_revision": bool(decision.get("require_revision")),
        "deny": bool(decision.get("deny")),
        "escalate": bool(decision.get("escalate")),
        "dry_run_only": True,
        "non_execution_confirmation": True,
        "action_executed": False,
        "cieu_written": False,
        "brain_writeback_performed": False,
        "memory_ingestion_performed": False,
        "decision_envelope": decision,
        "generated_from_packet_ref": ROLE_CONFIG[agent_id]["packet"],
        "generated_from_envelope_ref": envelope_path,
    }


def run_governance() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ensure_inputs()
    snapshots: list[dict[str, Any]] = []
    for agent_id, envelope_path in ENVELOPE_FILES.items():
        packet = load_json(ROLE_CONFIG[agent_id]["packet"])
        exit_code, decision = call_ystar_gov(envelope_path)
        snapshots.append(build_snapshot(agent_id, packet, envelope_path, exit_code, decision))

    decisions: dict[str, int] = {}
    for snapshot in snapshots:
        decision = str(snapshot.get("ystar_gov_decision"))
        decisions[decision] = decisions.get(decision, 0) + 1

    payload = {
        "schema_name": "ystar.labs_governance_bridge.pre_u_governance_decision_snapshots",
        "schema_version": "v0",
        "snapshots": snapshots,
        "summary": {
            "snapshots_created": len(snapshots),
            "roles_covered": [snapshot["agent_id"] for snapshot in snapshots],
            "decision_counts": decisions,
            "dry_run_only": True,
            "action_executed": False,
            "cieu_written": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
            "warning": "Generated Pre-U governance decisions are dry-run only and are not runtime actions.",
        },
    }
    manifest = {
        "schema_name": "ystar.labs_governance_bridge.pre_u_governance_run_manifest",
        "schema_version": "v0",
        "generated_files": [
            SNAPSHOTS,
            SNAPSHOTS_MD,
            MANIFEST,
        ],
        "source_packets": [config["packet"] for config in ROLE_CONFIG.values()],
        "source_envelopes": list(ENVELOPE_FILES.values()),
        "ystar_gov_cli_path": YSTAR_GOV_CLI,
        "snapshots_created": len(snapshots),
        "decision_counts": decisions,
        "dry_run_only": True,
        "action_execution_allowed": False,
        "cieu_write_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
    }
    write_json(SNAPSHOTS, payload)
    write_text(SNAPSHOTS_MD, render_markdown(payload))
    write_json(MANIFEST, manifest)
    return snapshots, manifest


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Pre-U Governance Dry-Run Decisions",
        "",
        f"- Snapshots created: {summary['snapshots_created']}",
        "- Decisions:",
    ]
    for decision, count in sorted(summary["decision_counts"].items()):
        lines.append(f"  - {decision}: {count}")
    lines.extend(["", "## Roles", ""])
    for snapshot in payload["snapshots"]:
        lines.extend(
            [
                f"### {snapshot['agent_id']}",
                "",
                f"- Packet: {snapshot['packet_id']}",
                f"- Decision: {snapshot['ystar_gov_decision']}",
                f"- Exit code: {snapshot['ystar_gov_exit_code']}",
                f"- allow_execution: {snapshot['allow_execution']}",
                f"- dry_run_only: {snapshot['dry_run_only']}",
                f"- action_executed: {snapshot['action_executed']}",
                "",
            ]
        )
    lines.append("Safety: no action, CIEU write, memory ingestion, or brain writeback occurred.")
    lines.append("")
    return "\n".join(lines)


def print_report(snapshots: list[dict[str, Any]]) -> None:
    print("Pre-U Governance Dry-Run Runner: PASS")
    print(f"Decision snapshots: {len(snapshots)}")
    for snapshot in snapshots:
        print(f"- {snapshot['agent_id']}: {snapshot['ystar_gov_decision']} (exit {snapshot['ystar_gov_exit_code']})")
    print("Generated files:")
    print(f"- {SNAPSHOTS}")
    print(f"- {SNAPSHOTS_MD}")
    print(f"- {MANIFEST}")
    print("Safety note: Y-star-gov CLI was called dry-run only; no actions were executed.")


def main() -> int:
    try:
        snapshots, _manifest = run_governance()
    except Exception as exc:
        print("Pre-U Governance Dry-Run Runner: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report(snapshots)
    return 0


if __name__ == "__main__":
    sys.exit(main())
