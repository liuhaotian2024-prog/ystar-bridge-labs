from __future__ import annotations

from typing import Any, Dict, List


HUMAN_REQUIRED_CONDITIONS = [
    "payment_or_purchase",
    "contract_or_signature",
    "legal_or_financial_commitment",
    "credential_or_account_change",
    "customer_private_data_access",
    "high_volume_outreach",
    "sensitive_public_announcement",
    "regulated_claim",
    "irreversible_publication",
    "ambiguous_high_risk_case",
    "explicit_ygov_or_gov_mcp_owner_gate",
]


def build_human_intervention_boundary() -> Dict[str, Any]:
    return {
        "artifact_id": "e20_human_intervention_boundary",
        "principle": "Human intervention is exceptional risk control, not the default for sending or publishing.",
        "human_required_conditions": HUMAN_REQUIRED_CONDITIONS,
        "human_not_required_merely_because": ["sending", "publishing", "external surface"],
        "autonomous_possible_when": [
            "risk tier is T1 or T2",
            "provider adapter is live and tested",
            "Y*gov/gov-mcp policy permits",
            "rate limit, idempotency, suppression, audit receipt, and rollback/stop path are present",
            "content is bounded, transparent, reversible where applicable, and non-regulated",
        ],
        "owner_manual_only_cases": [
            "owner chooses to manually operate as an override",
            "provider adapter is missing but owner wants a manual business action",
            "policy explicitly requires manual handoff",
        ],
        "external_action_executed": False,
    }


def requires_human_intervention(action: Dict[str, Any]) -> bool:
    if action.get("risk_tier") in {"T4_high_risk_owner_approval_required", "T5_no_go_blocked"}:
        return True
    return any(bool(action.get(condition)) for condition in HUMAN_REQUIRED_CONDITIONS)


def render_human_intervention_boundary(boundary: Dict[str, Any]) -> str:
    lines = [
        "# E20 Human Intervention Boundary",
        "",
        boundary["principle"],
        "",
        "## Human Required Conditions",
    ]
    lines.extend(f"- {item}" for item in boundary["human_required_conditions"])
    lines.extend(["", "## Human Not Required Merely Because"])
    lines.extend(f"- {item}" for item in boundary["human_not_required_merely_because"])
    lines.extend(["", "## Autonomous Possible When"])
    lines.extend(f"- {item}" for item in boundary["autonomous_possible_when"])
    return "\n".join(lines).rstrip() + "\n"
