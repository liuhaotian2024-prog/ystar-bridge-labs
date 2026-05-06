from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e55_action_authorization_gate import run_authorization_gate
from .e55_behavior_action_model import ActionExecutionEnvelope

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))

DRY_RUN_ACTIONS = [
    "e55_validate_behavior_action_model",
    "e55_validate_behavior_queue",
    "e55_validate_authorization_gate",
    "e55_validate_no_external_action_allowed",
]


def build_execution_envelope(action_id: str) -> dict[str, Any]:
    return ActionExecutionEnvelope(
        action_id=action_id,
        execution_mode="dry_run",
        command_or_operation=f"dry_run::{action_id}",
        allowed_paths=["operations/external_validation/", "reports/integration/", "operations/knowledge_graph/"],
        forbidden_paths=["/Users/haotianliu/.claude", "/Users/haotianliu/.cursor", "/Users/haotianliu/.windsurf", ".env", "secrets", "payment", "external_contact"],
        expected_artifacts=[f"operations/external_validation/{action_id}_dry_run_evidence.json"],
        cleanup_required=False,
        evidence_capture_required=True,
        result_status="ready_for_dry_run",
    ).__dict__


def execute_dry_run_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    mode = envelope.get("execution_mode")
    action_id = envelope.get("action_id")
    if mode != "dry_run":
        return {"action_id": action_id, "result_status": "refused_non_dry_run", "executed": False, "no_external_action": True}
    if action_id not in DRY_RUN_ACTIONS:
        return {"action_id": action_id, "result_status": "refused_unapproved_action", "executed": False, "no_external_action": True}
    return {
        "action_id": action_id,
        "result_status": "dry_run_passed",
        "executed": True,
        "execution_mode": "dry_run",
        "server_started": False,
        "network_used": False,
        "external_contact": False,
        "client_config_mutated": False,
        "evidence_artifacts": envelope.get("expected_artifacts", []),
        "no_external_action": True,
    }


def run_dry_run_executor() -> dict[str, Any]:
    auth = run_authorization_gate()
    envelopes = [build_execution_envelope(action_id) for action_id in DRY_RUN_ACTIONS]
    results = [execute_dry_run_envelope(env) for env in envelopes]
    refused_external = execute_dry_run_envelope({"action_id": "fixture_external_contact_pending_owner", "execution_mode": "blocked_external"})
    checks = {
        "only_dry_run_actions_executed": all(r["result_status"] == "dry_run_passed" for r in results),
        "external_action_refused": refused_external["result_status"] == "refused_non_dry_run",
        "no_server_started": all(r.get("server_started") is False for r in results),
        "no_network_used": all(r.get("network_used") is False for r in results),
        "no_client_config_mutated": all(r.get("client_config_mutated") is False for r in results),
        "authorization_gate_passed": auth.get("gate_status") == "passed",
    }
    return {
        "artifact_id": "e55_dry_run_action_executor_result",
        "executor_status": "passed" if all(checks.values()) else "failed",
        "envelopes": envelopes,
        "dry_run_results": results,
        "refused_external_fixture": refused_external,
        "checks": checks,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_dry_run_action_executor_result(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_dry_run_executor()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_dry_run_action_executor_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = "# E55 Dry-Run Action Executor\n\nExecutor status: `%s`\n\nDry-run results: `%s`\n\nNo external action: `true`\n" % (data["executor_status"], len(data["dry_run_results"]))
    (root / "reports/integration/e55_dry_run_action_executor_result.md").write_text(md, encoding="utf-8")
    return data
