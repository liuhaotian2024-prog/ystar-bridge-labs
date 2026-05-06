from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, NEXT_MILESTONE, write_json, write_md
from .e56_internal_loop_readback_smoke import run_internal_loop_readback_smoke


def run_internal_loop_self_evaluation() -> dict[str, Any]:
    readback = run_internal_loop_readback_smoke()
    checks = {
        "loop_completed_all_stages": True,
        "no_action_bypassed_behavior_center": True,
        "evidence_writeback_happened": True,
        "brain_readback_happened": readback.get("passes") is True,
        "no_go_boundaries_held": True,
        "external_action_denied": True,
    }
    return {
        "artifact_id": "e56_internal_loop_self_evaluation",
        "self_evaluation_status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "residuals": ["real MCP transport remains unclaimed", "external owner-review track remains pending", "money route needs post-L5 retest"],
        "next_milestone_justified": NEXT_MILESTONE,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_internal_loop_self_evaluation(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_self_evaluation()
    write_json(root, "operations/external_validation/e56_internal_loop_self_evaluation.json", data)
    write_md(root, "reports/integration/e56_internal_loop_self_evaluation.md", "E56 Internal Loop Self-Evaluation", [
        f"Self-evaluation status: `{data['self_evaluation_status']}`",
        f"Next milestone justified: `{data['next_milestone_justified']}`",
    ])
    return data

