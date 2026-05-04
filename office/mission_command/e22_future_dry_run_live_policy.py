from __future__ import annotations

from typing import Any, Dict


def build_future_dry_run_live_policy() -> Dict[str, Any]:
    return {"artifact_id":"e22_future_dry_run_live_policy","future_autonomous_outbound_milestone_must_include":["dry-run batch selector","provider envelope builder","guard stack replay","dry-run receipt ledger","idempotency proof","suppression proof","rate-limit proof","live promotion blocker report","ecosystem alignment proof","explicit no-external-effect statement until live mode is enabled"],"live_mode_default_enabled":False,"owner_manual_send_is_default":False,"external_action_executed":False}

def render_future_dry_run_live_policy(policy: Dict[str, Any]) -> str:
    lines=["# E22 Future Dry-Run/Live Policy","",f"- live_mode_default_enabled: {str(policy['live_mode_default_enabled']).lower()}",f"- owner_manual_send_is_default: {str(policy['owner_manual_send_is_default']).lower()}","- external_action_executed: false","","## Required"]
    lines.extend(f"- {item}" for item in policy["future_autonomous_outbound_milestone_must_include"])
    return "\n".join(lines).rstrip()+"\n"
