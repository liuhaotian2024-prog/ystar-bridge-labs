from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .evidence_provenance import EvidenceRunBundle, evidence_bundle_is_market_backing_eligible
from .market_reality_model import build_market_reality_profile
from .opportunity_synthesis_engine import compare_generated_opportunities


def _bundle_dict(bundle: Dict[str, Any] | EvidenceRunBundle | None) -> Dict[str, Any]:
    if bundle is None:
        return {}
    if isinstance(bundle, EvidenceRunBundle):
        return bundle.to_dict()
    return dict(bundle)


def _bundle_sources(bundle: Dict[str, Any] | EvidenceRunBundle | None) -> List[Dict[str, Any]]:
    data = _bundle_dict(bundle)
    if not data or not evidence_bundle_is_market_backing_eligible(data):
        return []
    return list(data.get("sources", []))


def _relevant_sources(opportunity: Dict[str, Any], sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    oid = opportunity["opportunity_id"]
    return [source for source in sources if oid in source.get("relevant_opportunity_ids", [])]


def _independent_domains(sources: List[Dict[str, Any]]) -> int:
    return len({str(source.get("domain", "")) for source in sources if source.get("domain")})


def _row_market_backed(sources: List[Dict[str, Any]]) -> bool:
    if _independent_domains(sources) >= 2:
        return True
    has_pain_pricing = any(source.get("buyer_pain_signal") and source.get("pricing_signal") for source in sources)
    has_competition = any(source.get("competitor_signal") or source.get("substitute_signal") for source in sources)
    return bool(has_pain_pricing and has_competition and _independent_domains(sources) >= 1)


def score_e5_opportunity(opportunity: Dict[str, Any], profile: Dict[str, Any], relevant: List[Dict[str, Any]], bundle_valid: bool) -> Dict[str, int]:
    title = str(opportunity.get("title", "")).lower()
    owner_burden = str(opportunity.get("owner_burden", "")).lower()
    evidence_strength = min(5, len(relevant) * 2) if bundle_valid else 0
    pricing_strength = 4 if any(source.get("pricing_signal") for source in relevant) and bundle_valid else 1
    independence = _independent_domains(relevant) if bundle_valid else 0
    governance_cluster = any(token in title for token in ["mcp", "governance", "coding-agent", "runtime"])
    narrowness_penalty = 3 if governance_cluster and not bundle_valid else 0
    score = {
        "buyer_clarity": 4 if opportunity.get("buyer") else 1,
        "pain_urgency": 5 if any(token in str(opportunity.get("pain", "")).lower() for token in ["risk", "blocked", "unsafe", "cannot", "urgent", "incident"]) else 3,
        "budget_channel_clarity": 4 if profile.get("budget_channel") else 1,
        "competitor_pressure": min(5, 2 + len(profile.get("direct_competitors", [])) // 2),
        "substitutes_no_action_pressure": min(5, 2 + len(profile.get("substitutes", [])) // 2),
        "differentiation_wedge": 4 if profile.get("differentiation_wedge") else 1,
        "trust_gap_severity": 1 if relevant and bundle_valid else 4,
        "pricing_evidence_strength": pricing_strength,
        "buyer_process_clarity": 4 if profile.get("buying_process") else 1,
        "internal_capability_fit": min(5, 2 + len(opportunity.get("internal_assets", [])) // 2),
        "behavior_feasibility": 4 if "repo modification" not in opportunity.get("behavior_capability_required", []) else 2,
        "owner_burden": 4 if owner_burden.startswith("low") else (2 if owner_burden.startswith("medium") else 1),
        "channel_access": 3 if relevant and bundle_valid else 2,
        "proof_strength": min(5, 1 + len(opportunity.get("proof_assets", [])) // 2 + len(relevant)),
        "external_evidence_strength": evidence_strength,
        "source_independence": independence,
        "fastest_disconfirming_test_quality": 4 if "48h" in str(opportunity.get("first_experiment", "")) else 2,
        "counterfactual_risk": 2 if "high" in owner_burden else 3,
        "repeatability": 4 if any(token in title for token in ["support", "package", "audit", "diagnosis", "review"]) else 3,
        "m3_relevance": 4 if "M-3" in str(opportunity.get("m_triangle_alignment", "")) else 2,
        "narrowness_penalty": narrowness_penalty,
    }
    positive = sum(value for key, value in score.items() if key not in {"trust_gap_severity", "narrowness_penalty"})
    score["total"] = positive - score["trust_gap_severity"] - narrowness_penalty
    score["relevant_source_count"] = len(relevant)
    return score


def evaluate_e5_market_evidence(repo_root: Path, evidence_bundle: Dict[str, Any] | EvidenceRunBundle | None = None) -> Dict[str, Any]:
    bundle_data = _bundle_dict(evidence_bundle)
    bundle_valid = evidence_bundle_is_market_backing_eligible(bundle_data)
    sources = _bundle_sources(evidence_bundle)
    opportunities = compare_generated_opportunities(repo_root)
    rows: List[Dict[str, Any]] = []
    for opportunity in opportunities:
        relevant = _relevant_sources(opportunity, sources)
        profile = build_market_reality_profile(opportunity, source_evidence=relevant if bundle_valid else [])
        score = score_e5_opportunity(opportunity, profile, relevant, bundle_valid)
        market_backed = bundle_valid and _row_market_backed(relevant)
        rows.append(
            {
                "opportunity": opportunity,
                "market_reality_profile": profile,
                "score": score,
                "market_backed": market_backed,
                "ranking_confidence": profile["confidence"] if market_backed else "internal_hypothesis_only",
                "evidence_mode": profile["evidence_mode"] if bundle_valid else "internal_hypothesis_only",
                "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
            }
        )
    rows.sort(key=lambda row: int(row["score"]["total"]), reverse=True)
    top = rows[0]
    return {
        "mode": "validated_live_bundle" if bundle_valid else "internal_only_or_blocked",
        "bundle_valid": bundle_valid,
        "default_recommendation": top["opportunity"]["title"] if top["market_backed"] else "obtain_validated_public_evidence_bundle",
        "default_is_market_backed": bool(top["market_backed"]),
        "top_path": top["opportunity"]["title"],
        "strongest_alternative": rows[1]["opportunity"]["title"],
        "rows": rows,
        "external_action_executed": False,
    }


def render_e5_market_evaluation_markdown(evaluation: Dict[str, Any]) -> str:
    lines = [
        "# E5 Market Evidence Opportunity Evaluation",
        "",
        f"- mode: {evaluation['mode']}",
        f"- bundle_valid: {evaluation['bundle_valid']}",
        f"- default_recommendation: {evaluation['default_recommendation']}",
        f"- default_is_market_backed: {evaluation['default_is_market_backed']}",
        f"- top_path: {evaluation['top_path']}",
        f"- strongest_alternative: {evaluation['strongest_alternative']}",
        "",
        "| Rank | Opportunity | Total | Market-backed | Evidence mode | Sources | Independence | Narrowness penalty |",
        "| ---: | --- | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for index, row in enumerate(evaluation["rows"], start=1):
        score = row["score"]
        lines.append(
            f"| {index} | {row['opportunity']['title']} | {score['total']} | {row['market_backed']} | {row['evidence_mode']} | {score['relevant_source_count']} | {score['source_independence']} | {score['narrowness_penalty']} |"
        )
    if not evaluation["default_is_market_backed"]:
        lines.extend(["", "## Blocked / Internal-Only State", "No recommendation is market-backed without a validated EvidenceRunBundle and sufficient independent source support."])
    return "\n".join(lines)


def render_e5_top_candidates_markdown(evaluation: Dict[str, Any]) -> str:
    lines = ["# E5 Top Candidates", ""]
    for index, row in enumerate(evaluation["rows"][:3], start=1):
        opportunity = row["opportunity"]
        lines.extend(
            [
                f"## {index}. {opportunity['title']}",
                f"- opportunity_id: {opportunity['opportunity_id']}",
                f"- lens: {opportunity['generated_from_lens']}",
                f"- market_backed: {row['market_backed']}",
                f"- evidence_mode: {row['evidence_mode']}",
                f"- ranking_confidence: {row['ranking_confidence']}",
                f"- first_experiment: {opportunity['first_experiment']}",
                f"- kill_condition: {opportunity['kill_condition']}",
                "",
            ]
        )
    return "\n".join(lines)
