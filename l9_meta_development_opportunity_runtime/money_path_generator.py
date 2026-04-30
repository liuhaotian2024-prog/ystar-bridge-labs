#!/usr/bin/env python3
"""Generate flexible money path candidates for discovered opportunities."""

from __future__ import annotations

from typing import Any

from .money_path_model import list_money_paths, save_money_path
from .opportunity_discovery_engine import discover_opportunities
from .opportunity_model import base_packet, now_iso, safe_id


def generate_money_paths(force: bool = False) -> dict[str, Any]:
    discovery = discover_opportunities(force=force)
    existing = list_money_paths()
    if existing and not force:
        return {"ok": True, "money_paths": existing, "created": 0}
    paths = []
    for opp in discovery["opportunities"]:
        paths.append(save_money_path(_path_for_opportunity(opp)))
    return {"ok": True, "money_paths": paths, "created": len(paths)}


def _path_for_opportunity(opp: dict[str, Any]) -> dict[str, Any]:
    short = safe_id(opp["opportunity_id"].removeprefix("opp_"))
    signal_days = int(str(opp["estimated_time_to_signal"]).split()[0])
    cash_days = int(str(opp["estimated_time_to_cash"]).split()[0])
    implementation_cost = int(opp["implementation_cost"])
    strategic = 5 if any(word in opp["title"].lower() for word in ["runtime", "governance", "open-source", "cockpit"]) else 4
    productization = 5 if any(word in opp["title"].lower() for word in ["template", "open-source", "cockpit", "runtime"]) else 3
    fit = max(2, 6 - implementation_cost)
    return {
        **base_packet("money_path_candidate"),
        "money_path_id": f"money_path_{short}",
        "opportunity_id": opp["opportunity_id"],
        "path_title": f"{opp['title']} money path",
        "path_type": _path_type(opp),
        "offer_hypothesis": opp["proposed_value"],
        "target_customer": opp["customer_profile"],
        "first_action": "Create owner-reviewed manual-send action packet and/or no-contact validation plan.",
        "required_assets": opp["internal_asset_match"],
        "missing_assets": _missing_assets(opp),
        "expected_signal": "Owner-approved customer signal, response, or paid pilot interest.",
        "expected_cash_mechanism": opp["revenue_mechanism"],
        "time_to_first_signal": opp["estimated_time_to_signal"],
        "time_to_first_cash": opp["estimated_time_to_cash"],
        "time_to_first_signal_days": signal_days,
        "time_to_first_cash_days": cash_days,
        "execution_difficulty": implementation_cost,
        "strategic_value": strategic,
        "current_capability_fit": fit,
        "productization_potential": productization,
        "owner_load": 2 if signal_days <= 14 else 3,
        "risk_level": implementation_cost + (1 if cash_days > 45 else 0),
        "score_summary": "Score by shortest cash, strategic value, owner load, and capability fit.",
        "status": "candidate",
        "created_at": now_iso(),
        "approval_needs": ["owner approval before contact", "manual-send only", "feedback intake after owner action"],
        "risk_boundary": "No automatic sending, payment, publication, scraping, or permanent writeback.",
        "feedback_plan": "Record owner-entered feedback, build residual, then create review-gated learning candidate.",
    }


def _path_type(opp: dict[str, Any]) -> str:
    title = opp["title"].lower()
    if "open-source" in title or "template" in title:
        return "productized_support_path"
    if "cockpit" in title or "runtime" in title:
        return "setup_and_advisory_path"
    if "audit" in title:
        return "service_audit_path"
    return "diagnostic_service_path"


def _missing_assets(opp: dict[str, Any]) -> list[str]:
    if "Open-Source" in opp["title"]:
        return ["public packaging", "support docs", "proof asset"]
    if "Cockpit" in opp["title"]:
        return ["installation checklist", "demo walkthrough", "setup scope boundary"]
    return ["buyer proof", "manual-send recipient selection", "sample deliverable"]

