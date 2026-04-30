#!/usr/bin/env python3
"""Build deterministic L9 meta-development runtime baseline artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .internal_asset_inventory import build_internal_asset_inventory
from .meta_development_cockpit import build_meta_cockpit
from .money_path_generator import generate_money_paths
from .opportunity_discovery_engine import discover_opportunities
from .opportunity_model import OUT, base_packet, no_action_receipt, write_packet
from .owner_decision_packet import build_owner_decision_packets
from .ranking_engine import build_rankings


def build_manifest(force: bool = False) -> dict[str, Any]:
    assets = build_internal_asset_inventory()
    opportunities = discover_opportunities(force=force)
    money_paths = generate_money_paths(force=force)
    rankings = build_rankings(force=force)
    decisions = build_owner_decision_packets(force=force)
    cockpit = build_meta_cockpit()
    receipt = no_action_receipt()
    write_packet("manifests", "l9_no_action_receipt", receipt)
    manifest = {
        **base_packet("l9_manifest"),
        "manifest_id": "l9_meta_development_manifest",
        "asset_inventory_count": assets["asset_count"],
        "opportunity_count": len(opportunities["opportunities"]),
        "money_path_count": len(money_paths["money_paths"]),
        "ranking_count": len(rankings["rankings"]),
        "owner_decision_packet_count": len(decisions["decision_packets"]),
        "selected_opportunity_count": len(cockpit["selected_opportunities"]),
        "execution_plan_count": len(cockpit["execution_plans"]),
        "l8_bridge_packet_count": len(cockpit["l8_bridge_packets"]),
        "portfolio_residual_count": len(cockpit["portfolio_residuals"]),
        "portfolio_learning_candidate_count": len(cockpit["portfolio_learning_candidates"]),
        "l8_first_cash_path_is_seed_not_only_route": True,
        "grant_rfp_default_path_status": "no",
        "manual_send_only": True,
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
    }
    write_packet("manifests", "l9_meta_development_manifest", manifest)
    _write_summary(manifest, cockpit)
    return manifest


def _write_summary(manifest: dict[str, Any], cockpit: dict[str, Any]) -> None:
    summary = {
        **base_packet("l9_summary"),
        "asset_inventory_count": manifest["asset_inventory_count"],
        "opportunity_count": manifest["opportunity_count"],
        "money_path_count": manifest["money_path_count"],
        "ranking_count": manifest["ranking_count"],
        "owner_decision_packet_count": manifest["owner_decision_packet_count"],
        "top_recommendation": cockpit.get("top_recommendation"),
        "shortest_cash_recommendation": cockpit.get("shortest_cash_recommendation"),
        "l8_first_cash_path_is_seed_not_only_route": True,
        "grant_rfp_path_created_by_default": False,
        "manual_send_only": True,
        "external_side_effects": False,
        "core_writeback": False,
        "local_url": "http://127.0.0.1:8765",
    }
    _write_root_json("l9_summary.json", summary)
    _write_root_text(
        "l9_summary.md",
        f"""
# L9.0 Meta-Development Opportunity & Execution Runtime

L9 builds a local portfolio engine for Y*Bridge Labs:

internal assets -> opportunity discovery -> money path generation -> multi-lens ranking -> owner decision -> manual-send-only execution plan -> L8-style bridge -> feedback/residual/learning.

- Internal assets: {manifest['asset_inventory_count']}
- Opportunities: {manifest['opportunity_count']}
- Money paths: {manifest['money_path_count']}
- Rankings: {manifest['ranking_count']}
- Top balanced recommendation: {json.dumps(cockpit.get('top_recommendation'), ensure_ascii=False)}
- Shortest-cash recommendation: {json.dumps(cockpit.get('shortest_cash_recommendation'), ensure_ascii=False)}

The L8 Founder AI Workflow Audit path remains a seed/benchmark route, not the only route.
No grant/RFP default path is created.
""",
    )
    _write_root_text(
        "README.md",
        """
# L9 Meta-Development Opportunity Runtime

This package provides a deterministic local runtime for discovering, ranking, and preparing multiple commercial money paths for Y*Bridge Labs.

It creates local JSON packets only. It does not send outreach, publish, process payment, create accounts, scrape leads, or write memory/brain/canonical/CIEU state.
""",
    )


def _write_root_json(name: str, payload: dict[str, Any]) -> None:
    path = OUT / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_root_text(name: str, text: str) -> None:
    path = OUT / name
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    manifest = build_manifest(force=False)
    print(f"l9_opportunities: {manifest['opportunity_count']}")
    print(f"l9_money_paths: {manifest['money_path_count']}")
    print(f"l9_rankings: {manifest['ranking_count']}")
    print(f"next_command: {manifest['next_one_command_action']}")


if __name__ == "__main__":
    main()
