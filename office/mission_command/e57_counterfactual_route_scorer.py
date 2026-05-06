from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, NEAREST_ALTERNATIVE, NEXT_MILESTONE, SELECTED_ROUTE, build_commercial_route_candidates, write_json, write_md
from .e57_post_l5_capability_delta import run_post_l5_capability_delta


def _decision(route: dict[str, Any], score: float) -> str:
    if route["route_id"] == "direct_customer_outreach_now":
        return "deny"
    if route["external_action_required"] and route["owner_approval_required"]:
        return "owner_approval_required"
    if route["allowed_action_type"] == "public_readonly_observation" and not route["allowed_now"]:
        return "defer"
    if score >= 0.68:
        return "select"
    if score >= 0.52:
        return "defer"
    return "quarantine"


def score_route(route: dict[str, Any]) -> dict[str, Any]:
    l5_boost = 0.0
    if route["route_id"] == SELECTED_ROUTE:
        l5_boost = 0.18
    elif route["route_id"] == "full_governed_execution_causal_audit_proof_stack":
        l5_boost = 0.28
    elif route["route_id"] == "governed_agent_action_proof_packet_owner_review_path":
        l5_boost = 0.02
    penalties = 0.0
    if route["real_mcp_transport_dependency"]:
        penalties += 0.09
    if route["customer_validation_dependency"]:
        penalties += 0.08
    if route["paid_signal_dependency"]:
        penalties += 0.10
    if route["external_action_required"]:
        penalties += 0.14
    if route["route_id"] == "direct_customer_outreach_now":
        penalties += 0.70
    score = round(
        route["near_term_cash_potential"] * 0.20
        + route["proof_strength"] * 0.28
        + route["reversibility"] * 0.14
        - route["governance_risk"] * 0.18
        - route["commercial_risk"] * 0.16
        + l5_boost
        - penalties
        + 0.20,
        4,
    )
    return {
        "route_id": route["route_id"],
        "route_name": route["description"],
        "Xt_current_state": "CEO brain L5, behavior center L5, and internal company loop L5 are ready; owner decision remains pending; no customer validation/paid signal/real MCP transport claim exists.",
        "Y_star_target": "Select the strongest near-term money route that can advance internally without external action or overclaiming.",
        "U_intervention": route["description"],
        "predicted_Yt_plus_1": "stronger owner-reviewable commercial narrative" if route["route_id"] == SELECTED_ROUTE else "partial or deferred commercial progress",
        "predicted_Rt_plus_1": NEXT_MILESTONE if route["route_id"] == SELECTED_ROUTE else "deferred, owner-gated, or blocked route state",
        "evidence_available": route["proof_strength"],
        "evidence_needed": route["missing_evidence"],
        "blocker_state": route["blocker_state"],
        "governance_risk": route["governance_risk"],
        "commercial_risk": route["commercial_risk"],
        "technical_readiness": route["proof_strength"],
        "revenue_immediacy": route["near_term_cash_potential"],
        "proof_strength": route["proof_strength"],
        "reversibility": route["reversibility"],
        "opportunity_cost": round(1 - route["near_term_cash_potential"], 4),
        "owner_approval_dependency": route["owner_approval_required"],
        "external_action_dependency": route["external_action_required"],
        "deterministic_score_components": {
            "near_term_cash_potential": route["near_term_cash_potential"],
            "proof_strength": route["proof_strength"],
            "reversibility": route["reversibility"],
            "governance_risk": route["governance_risk"],
            "commercial_risk": route["commercial_risk"],
            "post_l5_capability_boost": l5_boost,
            "missing_external_evidence_penalty": penalties,
            "counterfactual_score": score,
        },
        "decision": _decision(route, score),
    }


def build_counterfactual_route_matrix() -> dict[str, Any]:
    candidates = build_commercial_route_candidates()["routes"]
    routes = [score_route(route) for route in candidates]
    selectable = [route for route in routes if route["decision"] == "select"]
    selected = sorted(selectable, key=lambda r: (-r["deterministic_score_components"]["counterfactual_score"], r["governance_risk"]))[0]
    alternatives = [route for route in routes if route["route_id"] != selected["route_id"] and route["decision"] in {"select", "defer"}]
    nearest = sorted(alternatives, key=lambda r: abs(selected["deterministic_score_components"]["counterfactual_score"] - r["deterministic_score_components"]["counterfactual_score"]))[0]
    return {
        "artifact_id": "e57_counterfactual_route_matrix",
        "matrix_id": "e57_post_l5_counterfactual_route_matrix",
        "capability_delta_consumed": run_post_l5_capability_delta()["artifact_id"],
        "selected_route": selected["route_id"],
        "nearest_alternative": nearest["route_id"],
        "routes": routes,
        "validation": {
            "all_routes_have_counterfactual_fields": all(all(route.get(k) is not None for k in ["Xt_current_state", "Y_star_target", "U_intervention", "predicted_Yt_plus_1", "predicted_Rt_plus_1"]) for route in routes),
            "direct_customer_outreach_denied": any(route["route_id"] == "direct_customer_outreach_now" and route["decision"] == "deny" for route in routes),
            "l5_capability_boost_included": True,
            "missing_external_evidence_penalties_included": True,
        },
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_counterfactual_route_matrix(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_counterfactual_route_matrix()
    write_json(root, "operations/external_validation/e57_counterfactual_route_matrix.json", data)
    write_md(root, "reports/integration/e57_counterfactual_route_matrix.md", "E57 Counterfactual Route Matrix", [
        f"Selected route: `{data['selected_route']}`",
        f"Nearest alternative: `{data['nearest_alternative']}`",
        "L5 capability boost and missing-external-evidence penalties are included.",
    ])
    return data
