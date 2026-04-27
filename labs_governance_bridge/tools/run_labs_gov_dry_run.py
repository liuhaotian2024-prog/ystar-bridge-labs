#!/usr/bin/env python3
"""Run the labs-to-Y-star-gov dry-run bridge and snapshot the decision."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs_governance_bridge.tools.build_labs_hook_envelope import (  # noqa: E402
    GENERATED_ENVELOPE,
    build_envelope,
    write_json,
)


YSTAR_GOV_CLI = "/Users/haotianliu/.openclaw/workspace/Y-star-gov/tools/run_hook_contract_dry_run.py"
DECISION_SNAPSHOT = "labs_governance_bridge/generated/governance_decision_snapshot.json"
DECISION_SNAPSHOT_MD = "labs_governance_bridge/generated/governance_decision_snapshot.md"
BRIDGE_RUN_MANIFEST = "labs_governance_bridge/generated/bridge_run_manifest.json"


class BridgeRunError(Exception):
    """Raised when the dry-run bridge cannot produce a safe snapshot."""


def ensure_envelope() -> dict[str, Any]:
    envelope_path = ROOT / GENERATED_ENVELOPE
    if not envelope_path.exists():
        envelope, manifest = build_envelope()
        write_json(GENERATED_ENVELOPE, envelope)
        write_json("labs_governance_bridge/generated/envelope_manifest.json", manifest)
        return envelope
    with envelope_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise BridgeRunError("Generated hook envelope must be a JSON object.")
    return data


def run_ystar_gov_cli() -> tuple[int, dict[str, Any], str]:
    command = [
        "python3",
        YSTAR_GOV_CLI,
        "--input",
        GENERATED_ENVELOPE,
        "--pretty",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.stderr.strip():
        stderr = result.stderr.strip()
    else:
        stderr = ""
    try:
        decision = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise BridgeRunError(f"Y-star-gov CLI did not return JSON: {exc}; stderr={stderr}") from exc
    if not isinstance(decision, dict):
        raise BridgeRunError("Y-star-gov CLI decision must be a JSON object.")
    return result.returncode, decision, stderr


def build_snapshot(envelope: dict[str, Any], exit_code: int, decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.labs_governance_bridge.governance_decision_snapshot",
        "schema_version": "v0",
        "bridge_run_id": "labs-gov-bridge-run-001",
        "source_task_id": envelope.get("task_id"),
        "agent_id": envelope.get("agent_id"),
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
        "generated_from_envelope_ref": GENERATED_ENVELOPE,
        "warning": "Bridge decision snapshot is dry-run only and is not a CIEU record.",
    }


def build_manifest(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.labs_governance_bridge.bridge_run_manifest",
        "schema_version": "v0",
        "generated_files": [
            DECISION_SNAPSHOT,
            DECISION_SNAPSHOT_MD,
            BRIDGE_RUN_MANIFEST,
        ],
        "source_files": [
            GENERATED_ENVELOPE,
        ],
        "ystar_gov_cli_path": YSTAR_GOV_CLI,
        "ystar_gov_exit_code": snapshot.get("ystar_gov_exit_code"),
        "ystar_gov_decision": snapshot.get("ystar_gov_decision"),
        "dry_run_only": True,
        "action_execution_allowed": False,
        "cieu_write_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
    }


def render_markdown(snapshot: dict[str, Any]) -> str:
    lines = [
        "# Labs-Gov Governance Decision Snapshot",
        "",
        f"- Bridge run id: {snapshot.get('bridge_run_id')}",
        f"- Source task id: {snapshot.get('source_task_id')}",
        f"- Agent id: {snapshot.get('agent_id')}",
        f"- Y-star-gov decision: {snapshot.get('ystar_gov_decision')}",
        f"- Y-star-gov exit code: {snapshot.get('ystar_gov_exit_code')}",
        f"- allow_execution: {snapshot.get('allow_execution')}",
        f"- require_revision: {snapshot.get('require_revision')}",
        f"- deny: {snapshot.get('deny')}",
        f"- escalate: {snapshot.get('escalate')}",
        f"- dry_run_only: {snapshot.get('dry_run_only')}",
        f"- action_executed: {snapshot.get('action_executed')}",
        f"- cieu_written: {snapshot.get('cieu_written')}",
        f"- brain_writeback_performed: {snapshot.get('brain_writeback_performed')}",
        f"- memory_ingestion_performed: {snapshot.get('memory_ingestion_performed')}",
        "",
        f"Warning: {snapshot.get('warning')}",
        "",
    ]
    return "\n".join(lines)


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)


def print_report(snapshot: dict[str, Any]) -> None:
    print("Labs-Gov Dry-Run Bridge: PASS")
    print(f"bridge_run_id: {snapshot.get('bridge_run_id')}")
    print(f"source_task_id: {snapshot.get('source_task_id')}")
    print(f"agent_id: {snapshot.get('agent_id')}")
    print(f"ystar_gov_decision: {snapshot.get('ystar_gov_decision')}")
    print(f"ystar_gov_exit_code: {snapshot.get('ystar_gov_exit_code')}")
    print("Generated files:")
    print(f"- {DECISION_SNAPSHOT}")
    print(f"- {DECISION_SNAPSHOT_MD}")
    print(f"- {BRIDGE_RUN_MANIFEST}")
    print("Safety note: dry-run bridge did not execute actions, write CIEU, or mutate brain/memory.")


def main() -> int:
    try:
        envelope = ensure_envelope()
        exit_code, decision, _stderr = run_ystar_gov_cli()
        snapshot = build_snapshot(envelope, exit_code, decision)
        manifest = build_manifest(snapshot)
        write_json(DECISION_SNAPSHOT, snapshot)
        write_text(DECISION_SNAPSHOT_MD, render_markdown(snapshot))
        write_json(BRIDGE_RUN_MANIFEST, manifest)
    except Exception as exc:
        print("Labs-Gov Dry-Run Bridge: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report(snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
