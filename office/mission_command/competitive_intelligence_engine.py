from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .market_reality_model import build_market_reality_profile
from .tier1_research_runtime import resolve_tier1_research_capability


def build_competitive_intelligence(
    opportunities: List[Dict[str, Any]],
    repo_root: Path,
    external_evidence_packets: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    resolution = resolve_tier1_research_capability(repo_root)
    live_available = bool(resolution["live_read_only_available"] and resolution["live_research_executed"])
    external_packets = external_evidence_packets or []
    live_refs = [packet.get("packet_id", "external_packet") for packet in external_packets if packet.get("evidence_type") == "live_public_read_only"]
    profiles = [build_market_reality_profile(item, live_refs if live_available else []) for item in opportunities]
    competitor_map = {
        profile["opportunity_id"]: {
            "category": profile["category"],
            "direct_competitors": profile["direct_competitors"],
            "substitutes": profile["substitutes"],
            "no_action_alternative": profile["no_action_alternative"],
            "diy_alternative": profile["diy_alternative"],
            "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
            "trust_gap": profile["trust_gap"],
        }
        for profile in profiles
    }
    pricing_reference_map = {
        profile["opportunity_id"]: profile["pricing_references"]
        for profile in profiles
    }
    return {
        "mode": "live_read_only_evidence" if live_available else "internal_hypothesis_only",
        "live_research_executed": False,
        "resolution": resolution,
        "profiles": profiles,
        "competitor_map": competitor_map,
        "pricing_reference_map": pricing_reference_map,
        "buyer_process_notes": {
            profile["opportunity_id"]: profile["buying_process"]
            for profile in profiles
        },
        "differentiation_wedges": {
            profile["opportunity_id"]: profile["differentiation_wedge"]
            for profile in profiles
        },
        "invalidators": {
            profile["opportunity_id"]: [
                "Live public evidence shows no active pain language.",
                "Pricing references suggest buyers expect free templates only.",
                "Existing alternatives solve the problem with lower trust friction.",
                "48h sample cannot produce a concrete decision brief.",
            ]
            for profile in profiles
        },
        "research_plan_if_blocked": resolution["enablement_packet"],
        "external_action_executed": False,
    }


def render_competitive_intelligence_markdown(intel: Dict[str, Any]) -> str:
    lines = [
        "# E3 Competitive Intelligence",
        "",
        f"- mode: {intel['mode']}",
        f"- live_research_executed: {intel['live_research_executed']}",
        f"- external_action_executed: {intel['external_action_executed']}",
        "",
        "## Research Status",
        f"- live_read_only_available: {intel['resolution']['live_read_only_available']}",
        f"- missing_config_actions: {len(intel['resolution']['missing_config_actions'])}",
    ]
    if intel["resolution"]["missing_config_actions"]:
        lines.extend(f"- {item}" for item in intel["resolution"]["missing_config_actions"])
    lines.extend(["", "## Competitor / Alternative Map"])
    for profile in intel["profiles"]:
        lines.extend(
            [
                f"### {profile['opportunity_id']}",
                f"- category: {profile['category']}",
                f"- buyer: {profile['buyer']}",
                f"- budget_channel: {profile['budget_channel']}",
                f"- direct_competitors: {', '.join(profile['direct_competitors'])}",
                f"- substitutes: {', '.join(profile['substitutes'])}",
                f"- no_action_alternative: {profile['no_action_alternative']}",
                f"- diy_alternative: {profile['diy_alternative']}",
                f"- differentiation_wedge: {profile['differentiation_wedge']}",
                f"- trust_gap: {profile['trust_gap']}",
                f"- confidence: {profile['confidence']}",
                f"- missing_evidence: {', '.join(profile['missing_evidence']) or 'none'}",
            ]
        )
    return "\n".join(lines)
