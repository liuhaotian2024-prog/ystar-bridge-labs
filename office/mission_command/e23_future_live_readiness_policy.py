from __future__ import annotations

from typing import Any, Dict


def build_future_live_readiness_policy() -> Dict[str, Any]:
    return {"artifact_id":"e23_future_live_readiness_policy","future_live_readiness_milestone_must_include":["evidence sufficiency gate","suppression registry check","compliance registry check","provider live capability check","live tests","dry-run receipt history","idempotency persistence check","rate-limit budget","kill switch","audit receipt proof","owner approval only when required by risk tier","ecosystem alignment proof","explicit live/no-live decision"],"owner_manual_send_is_default":False,"live_without_live_ready_provider_allowed":False,"external_action_executed":False}

def render_future_live_readiness_policy(policy: Dict[str, Any]) -> str:
    lines=["# E23 Future Live-Readiness Policy","",f"- owner_manual_send_is_default: {str(policy['owner_manual_send_is_default']).lower()}",f"- live_without_live_ready_provider_allowed: {str(policy['live_without_live_ready_provider_allowed']).lower()}","- external_action_executed: false","","## Required"]
    lines.extend(f"- {item}" for item in policy["future_live_readiness_milestone_must_include"])
    return "\n".join(lines).rstrip()+"\n"
