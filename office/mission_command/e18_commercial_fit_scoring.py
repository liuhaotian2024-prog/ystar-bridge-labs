from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class E18CommercialFitScore:
    action_id: str
    target_id: str
    target_name: str
    status: str
    buyer_pain_fit: int
    urgency_likelihood: int
    authority_likelihood: int
    budget_relevance: int
    offer_fit: int
    trust_risk_level: int
    manual_send_suitability: int
    shortest_cash_path_relevance: int
    total_score: int
    recommended_message_variant_id: str
    score_reason: str
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _contains(text: str, terms: List[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def score_candidate(candidate: Dict[str, Any]) -> E18CommercialFitScore:
    text = " ".join(
        [
            str(candidate.get("target_name", "")),
            str(candidate.get("buyer_pain_hypothesis", "")),
            str(candidate.get("selection_reason", "")),
            str(candidate.get("offer", "")),
        ]
    )
    evidence_count = len(candidate.get("evidence_basis", []))
    ready = candidate.get("status") == "ready_for_owner_review"
    buyer_pain = 5 if _contains(text, ["readiness", "bottleneck", "governance", "risk"]) and evidence_count >= 2 else 3 if evidence_count else 1
    urgency = 4 if _contains(text, ["implementation", "operational", "safe next"]) else 2
    authority = 4 if _contains(text, ["consult", "agency", "operator", "team"]) else 2
    budget = 4 if _contains(text, ["consult", "agency", "paid", "implementation"]) else 2
    offer_fit = 5 if _contains(text, ["48h", "readiness", "agent"]) else 2
    trust_risk = 5 if str(candidate.get("risk_tier")) == "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION" else 2
    manual = 5 if ready and not candidate.get("missing_fields") else 2
    cash = 5 if ready and buyer_pain >= 4 and offer_fit >= 4 else 2
    total = buyer_pain + urgency + authority + budget + offer_fit + trust_risk + manual + cash
    if _contains(text, ["risk", "governance"]):
        variant = "risk_reduction_framing"
    elif _contains(text, ["bottleneck", "workflow"]):
        variant = "implementation_bottleneck_framing"
    elif _contains(text, ["consult", "agency"]):
        variant = "lightweight_advisory_framing"
    else:
        variant = "direct_readiness_review"
    return E18CommercialFitScore(
        action_id=str(candidate.get("action_id", "")),
        target_id=str(candidate.get("target_id", "")),
        target_name=str(candidate.get("target_name", "")),
        status=str(candidate.get("status", "")),
        buyer_pain_fit=buyer_pain,
        urgency_likelihood=urgency,
        authority_likelihood=authority,
        budget_relevance=budget,
        offer_fit=offer_fit,
        trust_risk_level=trust_risk,
        manual_send_suitability=manual,
        shortest_cash_path_relevance=cash,
        total_score=total,
        recommended_message_variant_id=variant,
        score_reason="Deterministic score from evidence count, offer keywords, risk tier, and owner-manual-send suitability.",
    )


def build_commercial_fit_scores(batch: Dict[str, Any]) -> Dict[str, Any]:
    scores = [score_candidate(item).to_dict() for item in batch.get("candidates", [])]
    scores.sort(key=lambda item: (-item["total_score"], item["target_name"]))
    return {
        "artifact_id": "e18_commercial_fit_scores",
        "batch_id": batch.get("batch_id"),
        "scoring_method": "deterministic_keyword_and_field_rules_no_llm_judge",
        "score_fields": [
            "buyer_pain_fit",
            "urgency_likelihood",
            "authority_likelihood",
            "budget_relevance",
            "offer_fit",
            "trust_risk_level",
            "manual_send_suitability",
            "shortest_cash_path_relevance",
        ],
        "scores": scores,
        "external_action_executed": False,
    }
