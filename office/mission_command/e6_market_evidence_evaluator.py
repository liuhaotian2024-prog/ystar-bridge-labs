from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from .evidence_provenance import EvidenceRunBundle, evidence_bundle_is_market_backing_eligible
from .market_reality_model import build_market_reality_profile
from .opportunity_synthesis_engine import compare_generated_opportunities


GOVERNANCE_CLUSTER = ["mcp", "governance", "coding-agent", "runtime"]


def _bundle_dict(bundle: Dict[str, Any] | EvidenceRunBundle | None) -> Dict[str, Any]:
    if bundle is None:
        return {}
    if isinstance(bundle, EvidenceRunBundle):
        return bundle.to_dict()
    return dict(bundle)


def _valid_sources(bundle: Dict[str, Any] | EvidenceRunBundle | None) -> List[Dict[str, Any]]:
    data = _bundle_dict(bundle)
    if not evidence_bundle_is_market_backing_eligible(data):
        return []
    return list(data.get("sources", []))


def relevant_sources(opportunity: Dict[str, Any], sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    opportunity_id = opportunity["opportunity_id"]
    return [source for source in sources if opportunity_id in source.get("relevant_opportunity_ids", [])]


def source_domains(sources: List[Dict[str, Any]]) -> List[str]:
    return sorted({str(source.get("domain", "")) for source in sources if source.get("domain")})


def evidence_type_diversity(sources: List[Dict[str, Any]]) -> int:
    dimensions = {
        "buyer_pain": any(source.get("buyer_pain_signal") for source in sources),
        "pricing": any(source.get("pricing_signal") for source in sources),
        "competitor": any(source.get("competitor_signal") for source in sources),
        "substitute": any(source.get("substitute_signal") for source in sources),
        "budget": any(source.get("budget_signal") for source in sources),
    }
    return sum(1 for present in dimensions.values() if present)


def opportunity_is_market_backed(sources: List[Dict[str, Any]]) -> bool:
    domains = source_domains(sources)
    if len(domains) >= 2 and any(source.get("buyer_pain_signal") for source in sources):
        return True
    has_pain_or_pricing = any(source.get("buyer_pain_signal") or source.get("pricing_signal") for source in sources)
    has_independent_competition = any(source.get("competitor_signal") or source.get("substitute_signal") or source.get("budget_signal") for source in sources)
    return bool(len(domains) >= 2 and has_pain_or_pricing and has_independent_competition)


def score_e6_opportunity(opportunity: Dict[str, Any], profile: Dict[str, Any], sources: List[Dict[str, Any]], bundle_valid: bool) -> Dict[str, int]:
    title = str(opportunity.get("title", "")).lower()
    owner_burden = str(opportunity.get("owner_burden", "")).lower()
    domain_count = len(source_domains(sources))
    diversity = evidence_type_diversity(sources)
    pricing_sources = [source for source in sources if source.get("pricing_signal")]
    budget_sources = [source for source in sources if source.get("budget_signal")]
    pain_sources = [source for source in sources if source.get("buyer_pain_signal")]
    governance_cluster = any(token in title for token in GOVERNANCE_CLUSTER)
    narrowness_penalty = 2 if governance_cluster and not sources else 0
    score = {
        "buyer_clarity": 5 if opportunity.get("buyer") and pain_sources else (4 if opportunity.get("buyer") else 1),
        "pain_urgency": 5 if pain_sources else (4 if any(token in str(opportunity.get("pain", "")).lower() for token in ["risk", "blocked", "incident", "unsafe"]) else 2),
        "budget_channel_clarity": 5 if budget_sources or pricing_sources else (3 if profile.get("budget_channel") else 1),
        "competitor_pressure": min(5, 2 + len(profile.get("direct_competitors", [])) // 2 + (1 if any(source.get("competitor_signal") for source in sources) else 0)),
        "substitute_no_action_pressure": min(5, 2 + len(profile.get("substitutes", [])) // 2 + (1 if any(source.get("substitute_signal") for source in sources) else 0)),
        "differentiation_wedge": 4 if profile.get("differentiation_wedge") else 1,
        "trust_gap_severity": 1 if domain_count >= 2 and diversity >= 2 else (3 if sources else 5),
        "pricing_evidence_strength": min(5, len(pricing_sources) * 2),
        "buyer_process_clarity": 4 if any(source.get("budget_signal") for source in sources) else 2,
        "internal_capability_fit": min(5, 2 + len(opportunity.get("internal_assets", [])) // 2),
        "behavior_feasibility": 4 if "repo modification" not in opportunity.get("behavior_capability_required", []) else 2,
        "owner_burden": 4 if owner_burden.startswith("low") else (3 if owner_burden.startswith("medium") else 1),
        "channel_access": 3 if sources else 1,
        "proof_strength": min(5, 1 + len(opportunity.get("proof_assets", [])) // 2 + len(sources)),
        "external_evidence_strength": min(5, len(sources) * 2) if bundle_valid else 0,
        "source_independence": domain_count,
        "evidence_type_diversity": diversity,
        "fastest_disconfirming_test_quality": 4 if "48h" in str(opportunity.get("first_experiment", "")) else 2,
        "counterfactual_risk": 2 if "high" in owner_burden else 3,
        "repeatability": 4 if any(token in title for token in ["support", "package", "audit", "diagnosis", "review", "implementation"]) else 3,
        "m3_relevance": 4 if "M-3" in str(opportunity.get("m_triangle_alignment", "")) else 2,
        "narrowness_penalty": narrowness_penalty,
    }
    positive = sum(value for key, value in score.items() if key not in {"trust_gap_severity", "narrowness_penalty"})
    score["total"] = positive - score["trust_gap_severity"] - narrowness_penalty
    score["relevant_source_count"] = len(sources)
    return score


def evaluate_e6_market_evidence(repo_root: Path, evidence_bundle: Dict[str, Any] | EvidenceRunBundle | None = None) -> Dict[str, Any]:
    bundle_data = _bundle_dict(evidence_bundle)
    bundle_valid = evidence_bundle_is_market_backing_eligible(bundle_data)
    all_sources = _valid_sources(evidence_bundle)
    rows: List[Dict[str, Any]] = []
    for opportunity in compare_generated_opportunities(repo_root):
        sources = relevant_sources(opportunity, all_sources)
        profile = build_market_reality_profile(opportunity, source_evidence=sources if bundle_valid else [])
        score = score_e6_opportunity(opportunity, profile, sources, bundle_valid)
        market_backed = bool(bundle_valid and opportunity_is_market_backed(sources))
        rows.append(
            {
                "opportunity": opportunity,
                "market_reality_profile": profile,
                "score": score,
                "source_ids": [source["source_id"] for source in sources],
                "source_domains": source_domains(sources),
                "market_backed": market_backed,
                "evidence_mode": "source_seed_live_public_read_only" if bundle_valid and sources else ("validated_bundle_no_relevant_sources" if bundle_valid else "internal_hypothesis_only"),
                "evidence_status": "market_backed" if market_backed else ("source_observed_but_not_market_backed" if sources else "no_relevant_live_source"),
                "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
            }
        )
    rows.sort(key=lambda row: int(row["score"]["total"]), reverse=True)
    top = rows[0]
    return {
        "mode": "validated_live_bundle" if bundle_valid else "internal_only_or_blocked",
        "bundle_valid": bundle_valid,
        "top_path": top["opportunity"]["title"],
        "top_opportunity_id": top["opportunity"]["opportunity_id"],
        "strongest_alternative": rows[1]["opportunity"]["title"],
        "default_recommendation": top["opportunity"]["title"] if top["market_backed"] else "request_revision_more_public_evidence",
        "default_is_market_backed": bool(top["market_backed"]),
        "evidence_market_backing_eligible": bool(bundle_valid),
        "rows": rows,
        "external_action_executed": False,
    }


def competitive_objection_rows(evaluation: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for row in evaluation["rows"][:limit]:
        profile = row["market_reality_profile"]
        rows.append(
            {
                "opportunity": row["opportunity"]["title"],
                "competitors": profile["direct_competitors"],
                "substitutes": profile["substitutes"],
                "no_action": profile["no_action_alternative"],
                "diy": profile["diy_alternative"],
                "buyer_rejection_reasons": profile["why_buyer_might_not_choose_us"],
                "trust_gap": profile["trust_gap"],
                "evidence_supporting_or_weakening": row["source_ids"] or ["no relevant validated source IDs"],
                "what_would_change_ranking": "More independent source evidence for buyer pain, budget/pricing, and buying process.",
            }
        )
    return rows


def render_e6_market_evaluation_markdown(evaluation: Dict[str, Any]) -> str:
    lines = [
        "# E6 Market Evidence Opportunity Evaluation",
        "",
        f"- mode: {evaluation['mode']}",
        f"- bundle_valid: {evaluation['bundle_valid']}",
        f"- default_recommendation: {evaluation['default_recommendation']}",
        f"- default_is_market_backed: {evaluation['default_is_market_backed']}",
        f"- top_path: {evaluation['top_path']}",
        f"- strongest_alternative: {evaluation['strongest_alternative']}",
        "",
        "| Rank | Opportunity | Total | Status | Sources | Domains | Diversity | Market-backed |",
        "| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for index, row in enumerate(evaluation["rows"], start=1):
        score = row["score"]
        lines.append(
            f"| {index} | {row['opportunity']['title']} | {score['total']} | {row['evidence_status']} | {score['relevant_source_count']} | {score['source_independence']} | {score['evidence_type_diversity']} | {row['market_backed']} |"
        )
    return "\n".join(lines)


def render_e6_top_candidates_markdown(evaluation: Dict[str, Any]) -> str:
    lines = ["# E6 Top Candidates", ""]
    for index, row in enumerate(evaluation["rows"][:5], start=1):
        opportunity = row["opportunity"]
        score = row["score"]
        lines.extend(
            [
                f"## {index}. {opportunity['title']}",
                f"- opportunity_id: {opportunity['opportunity_id']}",
                f"- lens: {opportunity['generated_from_lens']}",
                f"- market_backed: {row['market_backed']}",
                f"- evidence_status: {row['evidence_status']}",
                f"- source_ids: {', '.join(row['source_ids']) or 'none'}",
                f"- domains: {', '.join(row['source_domains']) or 'none'}",
                f"- total_score: {score['total']}",
                f"- first_experiment: {opportunity['first_experiment']}",
                f"- kill_condition: {opportunity['kill_condition']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_competitive_objection_matrix(evaluation: Dict[str, Any]) -> str:
    lines = ["# E6 Competitive Objection Matrix", ""]
    for item in competitive_objection_rows(evaluation):
        lines.extend(
            [
                f"## {item['opportunity']}",
                f"- competitors: {', '.join(item['competitors'])}",
                f"- substitutes: {', '.join(item['substitutes'])}",
                f"- no-action: {item['no_action']}",
                f"- DIY: {item['diy']}",
                f"- trust_gap: {item['trust_gap']}",
                f"- evidence_supporting_or_weakening: {', '.join(item['evidence_supporting_or_weakening'])}",
                f"- what_would_change_ranking: {item['what_would_change_ranking']}",
                "### Buyer Rejection Reasons",
            ]
        )
        lines.extend(f"- {reason}" for reason in item["buyer_rejection_reasons"])
        lines.append("")
    return "\n".join(lines)
