from __future__ import annotations

from typing import Any

from .e44a_ceo_task_preflight_v2 import run_ceo_task_preflight_v2
from .e44a_full_history_replay_cascade import run_full_history_cognition_replay

def run_full_history_preflight_v2(task: dict[str, Any]) -> dict[str, Any]:
    base = run_ceo_task_preflight_v2(task)
    replay = run_full_history_cognition_replay(task)
    return {
        "artifact_id": "e44a_full_history_preflight_v2_result",
        "base_E44A_preflight": base,
        "full_history_replay": replay,
        "required_pre_E31_families_invoked": [item["family"] for item in replay["pre_E31_capability_effects"] if item["invoked"]],
        "valid": len([item for item in replay["pre_E31_capability_effects"] if item["invoked"]]) >= 7,
        "external_action_occurred": False,
    }
