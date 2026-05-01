from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .competitive_intelligence_engine import build_competitive_intelligence
from .market_reality_model import build_market_reality_profile
from .opportunity_synthesis_engine import compare_generated_opportunities


def _relevant_sources(opportunity: Dict[str, Any], sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    oid = opportunity["opportunity_id"]
    return [source for source in sources if oid in source.get("relevant_opportunity_ids", [])]


def score_e4_opportunity(
    opportunity: Dict[str, Any],
    profile: Dict[str, Any],
    sources: List[Dict[str, Any]],
) -> Dict[str, int]:
    relevant = _relevant_sources(opportunity, sources)
    title = str(opportunity.get("title", "")).lower()
    owner_burden = str(opportunity.get("owner_burden", "")).lower()
    pain_text = " ".join([str(opportunity.get("pain", "")), *(str(s.get("buyer_pain_signal", "")) for s in relevant)]).lower()
    buyer_clarity = 4 if opportunity.get("buyer") else 1
    pain_urgency = 5 if any(word in pain_text for word in ["urgent", "incident", "risk", "blocked", "unsafe", "cannot"]) else 3
    budget_channel_clarity = 4 if profile.get("budget_channel") else 1
    competitor_pressure = min(5, 2 + len(profile.get("direct_competitors", [])) // 2)
    substitutes_pressure = min(5, 2 + len(profile.get("substitutes", [])) // 2)
    differentiation = 4 if profile.get("differentiation_wedge") else 1
    trust_gap_severity = 1 if relevant else 4
    pricing_evidence_strength = 4 if any(source.get("pricing_signal") for source in relevant) else 1
    buyer_process_clarity = 4 if profile.get("buying_process") else 1
    internal_fit = min(5, 2 + len(opportunity.get("internal_assets", [])) // 2)
    behavior_feasibility = 4 if "repo modification" not in opportunity.get("behavior_capability_required", []) else 2
    owner_burden_score = 4 if owner_burden.startswith("low") else (2 if owner_burden.startswith("medium") else 1)
    channel_access = 3 if relevant else 2
    proof_strength = min(5, 1 + len(opportunity.get("proof_assets", [])) // 2 + len(relevant))
    external_evidence_strength = min(5, len(relevant) * 2) if relevant else 0
    disconfirming_test = 4 if "48h" in str(opportunity.get("first_experiment", "")) else 2
    counterfactual_risk = 2 if "high" in owner_burden else 3
    repeatability = 4 if any(word in title for word in ["support", "package", "audit", "diagnosis", "review"]) else 3
    m3_relevance = 4 if "M-3" in str(opportunity.get("m_triangle_alignment", "")) else 2
    raw = {
        "buyer_clarity": buyer_clarity,
        "pain_urgency": pain_urgency,
        "budget_channel_clarity": budget_channel_clarity,
        "competitor_pressure": competitor_pressure,
        "substitutes_no_action_pressure": substitutes_pressure,
        "differentiation_wedge": differentiation,
        "trust_gap_severity": trust_gap_severity,
        "pricing_evidence_strength": pricing_evidence_strength,
        "buyer_process_clarity": buyer_process_clarity,
        "internal_capability_fit": internal_fit,
        "behavior_feasibility": behavior_feasibility,
        "owner_burden": owner_burden_score,
        "channel_access": channel_access,
        "proof_strength": proof_strength,
        "external_evidence_strength": external_evidence_strength,
        "fastest_disconfirming_test_quality": disconfirming_test,
        "counterfactual_risk": counterfactual_risk,
        "repeatability": repeatability,
        "m3_relevance": m3_relevance,
    }
    positive = sum(value for key, value in raw.items() if key != "trust_gap_severity")
    penalty = raw["trust_gap_severity"]
    raw["total"] = positive - penalty
    raw["relevant_source_count"] = len(relevant)
    return raw


def evaluate_e4_market_evidence(
    repo_root: Path,
    source_evidence: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    sources = source_evidence or []
    opportunities = compare_generated_opportunities(repo_root)
    intel = build_competitive_intelligence(opportunities, repo_root, source_evidence=sources)
    profiles = {profile["opportunity_id"]: profile for profile in intel["profiles"]}
    rows: List[Dict[str, Any]] = []
    for opportunity in opportunities:
        profile = profiles.get(opportunity["opportunity_id"]) or build_market_reality_profile(opportunity, source_evidence=sources)
        score = score_e4_opportunity(opportunity, profile, sources)
        rows.append(
            {
                "opportunity": opportunity,
                "market_reality_profile": profile,
                "score": score,
                "market_backed": bool(score["relevant_source_count"] and profile.get("market_evidence_refs")),
                "ranking_confidence": profile["confidence"],
                "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
            }
        )
    rows.sort(key=lambda row: int(row["score"]["total"]), reverse=True)
    live_ran = bool(sources)
    return {
        "mode": "live_public_read_only_evidence" if live_ran else "internal_only_blocked",
        "live_research_executed": live_ran,
        "default_recommendation": rows[0]["opportunity"]["title"] if live_ran else "unblock_tier1_public_research_provider",
        "default_is_market_backed": live_ran and rows[0]["market_backed"],
        "top_path": rows[0]["opportunity"]["title"],
        "strongest_alternative": rows[1]["opportunity"]["title"],
        "rows": rows,
        "competitive_intelligence": intel,
        "external_action_executed": False,
    }


def render_e4_market_evaluation_markdown(evaluation: Dict[str, Any]) -> str:
    lines = [
        "# E4 Market-Backed Opportunity Evaluation",
        "",
        f"- mode: {evaluation['mode']}",
        f"- live_research_executed: {evaluation['live_research_executed']}",
        f"- default_recommendation: {evaluation['default_recommendation']}",
        f"- default_is_market_backed: {evaluation['default_is_market_backed']}",
        f"- top_path: {evaluation['top_path']}",
        f"- strongest_alternative: {evaluation['strongest_alternative']}",
        "",
        "| Rank | Opportunity | Total | Sources | Market-backed | External evidence | Pricing evidence | Trust gap severity |",
        "| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for index, row in enumerate(evaluation["rows"], start=1):
        opportunity = row["opportunity"]
        score = row["score"]
        lines.append(
            f"| {index} | {opportunity['title']} | {score['total']} | {score['relevant_source_count']} | {row['market_backed']} | {score['external_evidence_strength']} | {score['pricing_evidence_strength']} | {score['trust_gap_severity']} |"
        )
    lines.extend(["", "## Top Details"])
    for row in evaluation["rows"][:5]:
        opportunity = row["opportunity"]
        profile = row["market_reality_profile"]
        lines.extend(
            [
                f"### {opportunity['title']}",
                f"- opportunity_id: {opportunity['opportunity_id']}",
                f"- buyer: {opportunity['buyer']}",
                f"- pain: {opportunity['pain']}",
                f"- evidence_mode: {profile['evidence_mode']}",
                f"- market_evidence_refs: {', '.join(profile['market_evidence_refs']) or 'none'}",
                f"- competitors: {', '.join(profile['direct_competitors'])}",
                f"- substitutes: {', '.join(profile['substitutes'])}",
                f"- pricing_references: {', '.join(profile['pricing_references'])}",
                f"- why_buyer_might_not_choose_us: {'; '.join(profile['why_buyer_might_not_choose_us'])}",
            ]
        )
    if not evaluation["live_research_executed"]:
        lines.extend(["", "## Blocked Evidence State", "No opportunity is market-backed. Ranking is internal-only until Tier 1 public research runs."])
    return "\n".join(lines)


def render_e4_top_candidates_markdown(evaluation: Dict[str, Any]) -> str:
    lines = ["# E4 Top Candidates", ""]
    if not evaluation["live_research_executed"]:
        lines.append("Current candidates are internal hypotheses because live public research did not run.")
        lines.append("")
    for index, row in enumerate(evaluation["rows"][:3], start=1):
        opportunity = row["opportunity"]
        lines.extend(
            [
                f"## {index}. {opportunity['title']}",
                f"- opportunity_id: {opportunity['opportunity_id']}",
                f"- lens: {opportunity['generated_from_lens']}",
                f"- market_backed: {row['market_backed']}",
                f"- ranking_confidence: {row['ranking_confidence']}",
                f"- first_experiment: {opportunity['first_experiment']}",
                f"- kill_condition: {opportunity['kill_condition']}",
                "",
            ]
        )
    return "\n".join(lines)
