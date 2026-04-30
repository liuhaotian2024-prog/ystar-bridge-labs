#!/usr/bin/env python3
"""Owner decision packets for top L9 opportunity paths."""

from __future__ import annotations

from typing import Any

from .money_path_model import get_money_path
from .opportunity_model import base_packet, load_packets, now_iso, write_packet
from .opportunity_portfolio import get_opportunity
from .ranking_engine import build_rankings


def build_owner_decision_packets(force: bool = False, top_n: int = 5) -> dict[str, Any]:
    rankings = build_rankings(force=force)["rankings"]
    balanced = next((ranking for ranking in rankings if ranking["lens"] == "balanced"), rankings[0])
    packets = []
    seen: set[str] = set()
    for scored in balanced["ranked_items"][:top_n]:
        money_path_id = scored["money_path_id"]
        if money_path_id in seen:
            continue
        seen.add(money_path_id)
        path = get_money_path(money_path_id)
        opp = get_opportunity(path["opportunity_id"])
        packet_id = f"decision_packet_{money_path_id}"
        packet = {
            **base_packet("owner_decision_packet"),
            "decision_packet_id": packet_id,
            "opportunity_id": opp["opportunity_id"],
            "money_path_id": money_path_id,
            "decision_needed": "Choose whether this path should enter manual-send-only execution planning.",
            "recommended_decision": "select_for_execution" if scored["total_score"] >= balanced["ranked_items"][0]["total_score"] - 2 else "hold",
            "options": ["select_for_execution", "reject", "hold", "request_revision", "request_more_evidence"],
            "evidence_summary": f"{opp['title']} uses assets {', '.join(opp['internal_asset_match'])}.",
            "tradeoffs": [
                f"Cash timing: {path['time_to_first_cash']}",
                f"Owner load: {path['owner_load']}",
                f"Risk penalty: {scored['risk_penalty']}",
            ],
            "owner_risk": "Owner approval and manual action remain required before external contact.",
            "next_action_if_approved": "Generate execution plan and L8 bridge packet.",
            "created_at": now_iso(),
        }
        packets.append(write_packet("owner_decision_packets", packet_id, packet))
    return {"ok": True, "decision_packets": packets, "created": len(packets)}


def list_owner_decision_packets() -> list[dict[str, Any]]:
    return load_packets("owner_decision_packets")

