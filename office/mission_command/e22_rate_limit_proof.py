from __future__ import annotations

from typing import Any, Dict


def build_rate_limit_proof(selection: Dict[str, Any], *, max_batch_actions: int = 5) -> Dict[str, Any]:
    selected = selection["selected_count"]
    return {
        "artifact_id": "e22_rate_limit_proof",
        "rate_limit_model": {"bucket_id": "e22_autonomous_dry_run_batch", "max_batch_actions": max_batch_actions},
        "selected_batch_fits_quota": selected <= max_batch_actions,
        "selected_count": selected,
        "excess_hypothetical_count": max_batch_actions + 1,
        "excess_hypothetical_result": "blocked_by_rate_limit",
        "production_claims_excess_sends": False,
        "external_action_executed": False,
    }
