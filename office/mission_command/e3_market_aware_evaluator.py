from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .competitive_intelligence_engine import build_competitive_intelligence
from .market_reality_model import build_market_reality_profile, profile_has_competition
from .opportunity_synthesis_engine import compare_generated_opportunities


def _score(opportunity: Dict[str, Any], profile: Dict[str, Any], live_evidence: bool) -> Dict[str, int]:
    title = str(opportunity.get("title", "")).lower()
    owner_burden = str(opportunity.get("owner_burden", "")).lower()
    buyer_clarity = 4 if opportunity.get("buyer") else 1
    pain_urgency = 4 if any(word in str(opportunity.get("pain", "")).lower() for word in ("urgent", "risk", "blocked", "cannot", "unsafe", "unclear")) else 3
    budget_channel_clarity = 4 if profile.get("budget_channel") else 1
    competitor_state = 4 if profile_has_competition(profile) else 1
    differentiation = 4 if profile.get("differentiation_wedge") else 1
    internal_fit = min(5, 2 + len(opportunity.get("internal_assets", [])) // 2)
    behavior_feasibility = 4 if "repo modification" not in opportunity.get("behavior_capability_required", []) else 2
    owner_burden_score = 4 if owner_burden.startswith("low") else (2 if owner_burden.startswith("medium") else 1)
    channel_access = 2
    proof_strength = min(4, 1 + len(opportunity.get("proof_assets", [])) // 2)
    external_evidence_strength = 4 if live_evidence else 1
    disconfirming_test = 4 if "48h" in str(opportunity.get("first_experiment", "")) else 2
    counterfactual_risk = 2 if "high" in owner_burden else 3
    repeatability = 4 if any(word in title for word in ("support", "package", "audit", "diagnosis", "review")) else 3
    m3_relevance = 4 if "M-3" in str(opportunity.get("m_triangle_alignment", "")) else 2
    score = {
        "buyer_clarity": buyer_clarity,
        "pain_urgency": pain_urgency,
        "budget_channel_clarity": budget_channel_clarity,
        "competitor_state": competitor_state,
        "differentiation_wedge": differentiation,
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
    score["total"] = sum(score.values())
    if not live_evidence:
        # Prevent internal-only hypotheses from masquerading as market-backed winners.
        score["market_backed_cap"] = 42
        score["rank_total"] = min(score["total"], score["market_backed_cap"])
    else:
        score["market_backed_cap"] = 999
        score["rank_total"] = score["total"]
    return score


def evaluate_market_aware_opportunities(repo_root: Path) -> Dict[str, Any]:
    opportunities = compare_generated_opportunities(repo_root)
    intel = build_competitive_intelligence(opportunities, repo_root)
    live_evidence = intel["mode"] == "live_read_only_evidence"
    profiles = {profile["opportunity_id"]: profile for profile in intel["profiles"]}
    rows: List[Dict[str, Any]] = []
    for opportunity in opportunities:
        profile = profiles.get(opportunity["opportunity_id"]) or build_market_reality_profile(opportunity)
        score = _score(opportunity, profile, live_evidence)
        rows.append(
            {
                "opportunity": opportunity,
                "market_reality_profile": profile,
                "score": score,
                "market_backed": live_evidence and bool(profile.get("market_evidence_refs")),
                "ranking_confidence": "low_internal_hypothesis_only" if not live_evidence else "medium_live_read_only",
                "what_would_change_ranking": [
                    "fresh buyer pain language from bounded public research",
                    "pricing/service references from credible public sources",
                    "evidence that buyer has urgent budget channel",
                    "evidence that competitors/substitutes do not already satisfy the need",
                ],
            }
        )
    rows.sort(key=lambda row: int(row["score"]["rank_total"]), reverse=True)
    recommend_research_first = not live_evidence
    default_decision = "tier1_read_only_research_first" if recommend_research_first else rows[0]["opportunity"]["opportunity_id"]
    return {
        "mode": "market_hypothesis_internal_only" if not live_evidence else "market_evidence_backed",
        "recommend_research_first": recommend_research_first,
        "default_decision": default_decision,
        "top_path": rows[0]["opportunity"]["title"],
        "strongest_alternative": rows[1]["opportunity"]["title"],
        "rows": rows,
        "competitive_intelligence": intel,
        "external_action_executed": False,
    }


def render_market_aware_evaluation_markdown(evaluation: Dict[str, Any]) -> str:
    lines = [
        "# E3 Market-Aware Opportunity Evaluation",
        "",
        f"- mode: {evaluation['mode']}",
        f"- default_decision: {evaluation['default_decision']}",
        f"- top_path: {evaluation['top_path']}",
        f"- strongest_alternative: {evaluation['strongest_alternative']}",
        f"- recommend_research_first: {evaluation['recommend_research_first']}",
        "",
        "| Rank | Opportunity | Lens | Rank Total | External Evidence | Competitors/Substitutes | Confidence |",
        "| ---: | --- | --- | ---: | ---: | --- | --- |",
    ]
    for index, row in enumerate(evaluation["rows"], start=1):
        opportunity = row["opportunity"]
        profile = row["market_reality_profile"]
        lines.append(
            f"| {index} | {opportunity['title']} | {opportunity['generated_from_lens']} | {row['score']['rank_total']} | {row['score']['external_evidence_strength']} | {len(profile['direct_competitors'])}/{len(profile['substitutes'])} | {row['ranking_confidence']} |"
        )
    lines.extend(["", "## Top Candidate Details"])
    for row in evaluation["rows"][:5]:
        opportunity = row["opportunity"]
        profile = row["market_reality_profile"]
        lines.extend(
            [
                f"### {opportunity['title']}",
                f"- buyer: {opportunity['buyer']}",
                f"- pain: {opportunity['pain']}",
                f"- budget_channel: {profile['budget_channel']}",
                f"- direct_competitors: {', '.join(profile['direct_competitors'])}",
                f"- substitutes: {', '.join(profile['substitutes'])}",
                f"- no_action_alternative: {profile['no_action_alternative']}",
                f"- diy_alternative: {profile['diy_alternative']}",
                f"- differentiation_wedge: {profile['differentiation_wedge']}",
                f"- why_buyer_might_not_choose_us: {'; '.join(profile['why_buyer_might_not_choose_us'])}",
                f"- external_evidence_strength: {row['score']['external_evidence_strength']}",
                f"- what_would_change_ranking: {'; '.join(row['what_would_change_ranking'])}",
            ]
        )
    return "\n".join(lines)


def render_top_candidates_markdown(evaluation: Dict[str, Any]) -> str:
    lines = [
        "# E3 Top Candidates",
        "",
        "No candidate is market-backed unless live read-only evidence runs. These are internal hypotheses ranked by market-aware structure.",
        "",
    ]
    for index, row in enumerate(evaluation["rows"][:3], start=1):
        opportunity = row["opportunity"]
        lines.extend(
            [
                f"## {index}. {opportunity['title']}",
                f"- opportunity_id: {opportunity['opportunity_id']}",
                f"- generated_from_lens: {opportunity['generated_from_lens']}",
                f"- buyer: {opportunity['buyer']}",
                f"- first_experiment: {opportunity['first_experiment']}",
                f"- kill_condition: {opportunity['kill_condition']}",
                f"- ranking_confidence: {row['ranking_confidence']}",
                f"- market_backed: {row['market_backed']}",
                "",
            ]
        )
    return "\n".join(lines)
