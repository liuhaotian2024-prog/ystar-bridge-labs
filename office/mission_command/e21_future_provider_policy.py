from __future__ import annotations

from typing import Any, Dict


def build_future_provider_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e21_future_provider_policy",
        "policy_id": "future_real_send_publication_provider_policy_v1",
        "future_real_send_milestone_must_include": [
            "provider capability manifest",
            "risk-tier eligibility result",
            "dry-run receipt",
            "promotion contract result",
            "rate-limit check",
            "idempotency check",
            "suppression check",
            "audit receipt proof",
            "ecosystem alignment proof",
            "explicit owner approval requirement by risk tier, not by send action alone",
        ],
        "owner_manual_send_is_default": False,
        "live_send_allowed_without_live_ready_provider": False,
        "external_action_executed": False,
    }


def render_future_provider_policy(policy: Dict[str, Any]) -> str:
    lines = [
        "# E21 Future Provider Policy",
        "",
        f"- policy_id: {policy['policy_id']}",
        f"- owner_manual_send_is_default: {str(policy['owner_manual_send_is_default']).lower()}",
        f"- live_send_allowed_without_live_ready_provider: {str(policy['live_send_allowed_without_live_ready_provider']).lower()}",
        "- external_action_executed: false",
        "",
        "## Required In Future Real-Send Milestones",
    ]
    lines.extend(f"- {item}" for item in policy["future_real_send_milestone_must_include"])
    return "\n".join(lines).rstrip() + "\n"
