from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, E56_CYCLE_ID, NEXT_MILESTONE, SELECTED_ACTION, cycle_stages, write_json, write_md
from .e56_internal_loop_authorization import run_internal_loop_authorization


def run_internal_loop_dry_run_executor() -> dict[str, Any]:
    auth = run_internal_loop_authorization()
    authorized = auth["selected_action_authorization"]["authorization_status"] in {"dry_run_only", "allow"}
    trace = []
    for index, stage in enumerate(cycle_stages(), start=1):
        trace.append({"order": index, "stage_id": stage["stage_id"], "status": "dry_run_completed", "external_action": False})
    return {
        "artifact_id": "e56_internal_loop_dry_run_result",
        "cycle_id": E56_CYCLE_ID,
        "selected_action": SELECTED_ACTION,
        "execution_mode": "dry_run",
        "executor_status": "passed" if authorized else "blocked",
        "stage_trace": trace,
        "evidence_packet_seed": "operations/external_validation/e56_internal_loop_evidence_packet.json",
        "self_evaluation_seed": "operations/external_validation/e56_internal_loop_self_evaluation.json",
        "next_milestone_proposal_seed": NEXT_MILESTONE,
        "server_started": False,
        "network_used": False,
        "human_contacted": False,
        "published": False,
        "external_config_mutated": False,
        "secrets_used": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_internal_loop_dry_run_result(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_dry_run_executor()
    write_json(root, "operations/external_validation/e56_internal_loop_dry_run_result.json", data)
    write_md(root, "reports/integration/e56_internal_loop_dry_run_result.md", "E56 Internal Loop Dry-Run Result", [
        f"Executor status: `{data['executor_status']}`",
        f"Stages completed: `{len(data['stage_trace'])}`",
        "External action: `false`",
    ])
    return data

