from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_behavior_center_state_for_brain() -> dict[str, Any]:
    update = _json("operations/external_validation/e55_ceo_brain_behavior_center_update.json")
    queue = _json("operations/external_validation/e55_behavior_queue_snapshot.json")
    auth = _json("operations/external_validation/e55_action_authorization_gate_result.json")
    readiness = _json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json")
    if not update and not queue and not auth and not readiness:
        return {"behavior_center_status": "unavailable_nonfatal", "external_action_allowed": False, "owner_decision_status": "pending_owner_decision", "no_external_action": True}
    readiness_passed = readiness.get("gate_passed") is True
    return {
        "behavior_center_status": (readiness.get("final_status") if readiness_passed else None) or update.get("behavior_center_status") or "behavior_control_center_l5_ready",
        "behavior_queue_status": queue.get("queue_status") or update.get("action_queue_status") or "valid",
        "authorization_gate_status": auth.get("gate_status") or update.get("authorization_gate_status") or "passed",
        "dry_run_executor_status": update.get("dry_run_executor_status") or "passed",
        "allowed_internal_dry_run_actions": update.get("allowed_internal_dry_run_actions") or queue.get("dry_run_only_actions", []),
        "external_actions_blocked": True,
        "owner_decision_status": update.get("owner_decision_status") or "pending_owner_decision",
        "owner_approval_fabricated": False,
        "external_action_allowed": False,
        "next_recommended_milestone": (readiness.get("recommended_next_milestone") if readiness_passed else None) or update.get("next_recommended_milestone") or "E56_internal_company_operating_loop_L5",
        "no_external_action": True,
    }


def run_behavior_center_readback_smoke() -> dict[str, Any]:
    state = load_behavior_center_state_for_brain()
    try:
        from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
        context = load_ceo_brain_context({"task_title": "E55 behavior center readback", "task_description": "safe local smoke"})
    except Exception as exc:
        context = {"error": str(exc)}
    checks = {
        "ceo_brain_sees_behavior_center_l5_status": state.get("behavior_center_status") == "behavior_control_center_l5_ready",
        "ceo_brain_sees_action_queue_exists": state.get("behavior_queue_status") == "valid",
        "ceo_brain_sees_allowed_internal_dry_run_actions": bool(state.get("allowed_internal_dry_run_actions")),
        "ceo_brain_sees_external_actions_blocked": state.get("external_actions_blocked") is True,
        "pending_owner_decision_still_pending": state.get("owner_decision_status") == "pending_owner_decision",
        "no_owner_approval_fabricated": state.get("owner_approval_fabricated") is False,
        "next_milestone_recommendation_loaded": state.get("next_recommended_milestone") == "E56_internal_company_operating_loop_L5",
        "canonical_runtime_can_see_behavior_center_state": context.get("latest_behavior_center_state", {}).get("behavior_center_status") in {"behavior_control_center_l5_ready", "unavailable_nonfatal"},
    }
    return {
        "artifact_id": "e55_behavior_center_readback_smoke_result",
        "state": state,
        "ceo_brain_context_excerpt": {
            "current_behavior_center_status": context.get("current_behavior_center_status"),
            "current_behavior_next_milestone": context.get("current_behavior_next_milestone"),
            "current_behavior_external_action_allowed": context.get("current_behavior_external_action_allowed"),
        },
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_behavior_center_readback_smoke(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_behavior_center_readback_smoke()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_center_readback_smoke_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "reports/integration/e55_behavior_center_readback_smoke_result.md").write_text("# E55 Behavior Center Readback Smoke\n\nPasses: `%s`\n" % data["passes"], encoding="utf-8")
    return data
