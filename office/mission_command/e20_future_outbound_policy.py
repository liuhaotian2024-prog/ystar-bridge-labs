from __future__ import annotations

from typing import Any, Dict


def build_future_outbound_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e20_future_outbound_policy",
        "policy": "Future outbound/publication/send milestones must not default to owner manual send.",
        "required_sections": [
            "risk_tier_classification",
            "autonomous_eligibility_decision",
            "provider_capability_status",
            "human_intervention_boundary",
            "no_go_decision_if_applicable",
            "ecosystem_alignment_result",
            "owner_involvement_required_or_optional_statement",
        ],
        "owner_manual_send_default_allowed": False,
        "owner_involvement_default": "optional_for_low_risk_provider_supported_actions_required_for_high_risk_or_policy_gate",
        "external_action_executed": False,
    }


def render_future_outbound_policy(policy: Dict[str, Any]) -> str:
    lines = [
        "# E20 Future Outbound Policy",
        "",
        policy["policy"],
        "",
        f"- owner_manual_send_default_allowed: {str(policy['owner_manual_send_default_allowed']).lower()}",
        f"- owner_involvement_default: {policy['owner_involvement_default']}",
        "- external_action_executed: false",
        "",
        "## Required Sections",
    ]
    lines.extend(f"- {item}" for item in policy["required_sections"])
    return "\n".join(lines).rstrip() + "\n"
