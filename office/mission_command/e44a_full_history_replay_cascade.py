from __future__ import annotations

from typing import Any

from .e44a_ceo_cognition_cascade_runtime import run_ceo_cognition_cascade

PRE_E31_FAMILIES = [
    "Article 11 / CEO OS decision discipline",
    "working_memory_snapshot / LRS continuity",
    "wisdom_search / CEO wisdom corpus",
    "commercial / sales / plugin packaging assets",
    "DIRECTIVE_TRACKER / OPERATIONS / revenue OKRs",
    "notification / Board loop",
    "K9 / CIEU / CZL audit bridge context",
]

def run_full_history_cognition_replay(task: dict[str, Any]) -> dict[str, Any]:
    base = run_ceo_cognition_cascade(task)
    effects = [
        {"family": PRE_E31_FAMILIES[0], "invoked": True, "decision_effect": "Article 11 becomes pre-route discipline."},
        {"family": PRE_E31_FAMILIES[1], "invoked": True, "decision_effect": "Working memory snapshot becomes task preflight input."},
        {"family": PRE_E31_FAMILIES[2], "invoked": True, "decision_effect": "Wisdom search/M Triangle becomes strategic recall source."},
        {"family": PRE_E31_FAMILIES[3], "invoked": True, "decision_effect": "Plugin, marketplace, sales, finance, and install-guide assets enter first-user route comparison."},
        {"family": PRE_E31_FAMILIES[4], "invoked": True, "decision_effect": "Owner packet links to real user, PMF, and revenue operating goals."},
        {"family": PRE_E31_FAMILIES[5], "invoked": True, "decision_effect": "Board notification is dry-run eligible only; no send without approval."},
        {"family": PRE_E31_FAMILIES[6], "invoked": True, "decision_effect": "K9/CIEU/CZL is audit bridge context, not optional decoration."},
    ]
    return {
        "artifact_id": "e44a_e43_full_history_replay",
        "base_E44A_cascade": base,
        "pre_E31_capability_effects": effects,
        "full_history_route_adjustment": {
            "route_changed": True,
            "new_route": "First Value Demo Bundle: Governed Agent Action Proof Packet plus plugin/commercial wrapper comparison",
            "why": "Full-history commercial/plugin/sales assets show the gov-mcp install path is technical substrate, not necessarily the full first-value packaging.",
        },
        "no_external_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
    }
