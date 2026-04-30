#!/usr/bin/env python3
"""Cockpit snapshot for the L9 meta-development opportunity runtime."""

from __future__ import annotations

from typing import Any

from .internal_asset_inventory import list_assets
from .l8_action_loop_bridge import list_l8_bridge_packets
from .money_path_model import list_money_paths
from .opportunity_model import base_packet, latest_packet, load_packets, write_packet
from .opportunity_portfolio import list_opportunities
from .owner_decision_packet import list_owner_decision_packets
from .portfolio_learning_candidate import list_portfolio_learning_candidates
from .portfolio_residual import list_portfolio_residuals
from .ranking_engine import list_rankings
from .execution_plan_generator import list_execution_plans
from .opportunity_review_center import list_opportunity_review_decisions


def build_meta_cockpit(snapshot_id: str = "l9_meta_cockpit_latest") -> dict[str, Any]:
    assets = list_assets()
    opportunities = list_opportunities()
    paths = list_money_paths()
    rankings = list_rankings()
    decision_packets = list_owner_decision_packets()
    reviews = list_opportunity_review_decisions()
    selected = [path for path in paths if path.get("status") == "selected_for_execution"]
    plans = list_execution_plans()
    bridge_packets = list_l8_bridge_packets()
    residuals = list_portfolio_residuals()
    learning = list_portfolio_learning_candidates()
    balanced = next((ranking for ranking in rankings if ranking.get("lens") == "balanced"), None)
    shortest = next((ranking for ranking in rankings if ranking.get("lens") == "shortest_cash"), None)
    snapshot = {
        **base_packet("meta_development_cockpit"),
        "cockpit_snapshot_id": snapshot_id,
        "internal_asset_inventory_summary": {
            "count": len(assets),
            "top_assets": [asset["title"] for asset in assets[:5]],
        },
        "opportunity_candidates": opportunities,
        "money_path_candidates": paths,
        "rankings_by_lens": rankings,
        "top_recommendation": (balanced or {}).get("top_recommendation"),
        "shortest_cash_recommendation": (shortest or {}).get("top_recommendation"),
        "evidence_basis_count": len(load_packets("evidence_basis")),
        "owner_decision_packets": decision_packets,
        "opportunity_review_decisions": reviews,
        "selected_opportunities": selected,
        "execution_plans": plans,
        "l8_bridge_packets": bridge_packets,
        "action_loop_readiness": {
            "selected_path_count": len(selected),
            "execution_plan_count": len(plans),
            "l8_bridge_packet_count": len(bridge_packets),
            "manual_send_only": True,
            "owner_approval_required": True,
        },
        "portfolio_residuals": residuals,
        "portfolio_learning_candidates": learning,
        "next_recommended_owner_decision": _next_decision(decision_packets, selected, plans, bridge_packets),
        "grant_rfp_default_path_status": "no",
        "coo_invented": False,
        "external_side_effects": False,
    }
    return write_packet("cockpit_snapshots", snapshot_id, snapshot)


def current_meta_cockpit() -> dict[str, Any]:
    return latest_packet("cockpit_snapshots") or build_meta_cockpit()


def _next_decision(
    decision_packets: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    plans: list[dict[str, Any]],
    bridge_packets: list[dict[str, Any]],
) -> str:
    if not decision_packets:
        return "build owner decision packets for ranked opportunities"
    if not selected:
        return "select, hold, reject, revise, or request evidence for a top opportunity"
    if not plans:
        return "generate a manual-send-only execution plan for the selected opportunity"
    if not bridge_packets:
        return "bridge the selected execution plan into L8-style approval-gated commercial action"
    return "review bridge packet and choose whether to move toward owner-approved manual action"
