from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class CounterfactualCase:
    opportunity_id: str
    opportunity_title: str
    do_nothing: str
    wrong_path: str
    alternative_path: str
    capability_failure: str
    buyer_nonexistence: str
    governance_drag: str
    m_triangle_failure: str
    owner_burden_failure: str
    highest_risk_assumption: str
    fastest_disconfirming_test: str
    recommended_adjustment: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _risk_assumption(opportunity: Dict[str, Any]) -> str:
    title = opportunity["title"].lower()
    if "cockpit" in title or "setup" in title:
        return "buyer may want advice before paying for setup implementation"
    if "template" in title:
        return "existing audience may not yet exist for paid template support"
    if "governance" in title or "readiness" in title:
        return "buyer may agree governance matters but not feel urgent budget pain"
    if "bottleneck" in title:
        return "buyer pain may be real but not yet framed as a paid diagnostic need"
    return "buyer may not recognize enough urgency to pay within 7 days"


def _fastest_test(opportunity: Dict[str, Any]) -> str:
    title = opportunity["title"]
    if "Bottleneck" in title:
        return "Within 48h, draft a one-page bottleneck diagnosis sample and a 5-question buyer pain test; if no crisp paid-pain language emerges, downgrade."
    if "Founder AI Workflow" in title:
        return "Within 48h, create a sample CEO Command Brief and compare it against two other offer samples for buyer clarity and delivery burden."
    if "Template" in title:
        return "Within 48h, package one before/after template-support example; if it needs too much context or no buyer segment is obvious, downgrade."
    return "Within 48h, produce the smallest sample deliverable and identify one owner-approved validation question; if not possible, downgrade."


def build_counterfactual_case(
    opportunity: Dict[str, Any],
    alternatives: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    title = opportunity["title"]
    alternative = next((item for item in alternatives if item.get("opportunity_id") != opportunity.get("opportunity_id")), None)
    alt_title = alternative["title"] if alternative else "the next-best path"
    owner_burden = str(opportunity.get("owner_burden", "unknown"))
    risk = _risk_assumption(opportunity)
    case = CounterfactualCase(
        opportunity_id=opportunity["opportunity_id"],
        opportunity_title=title,
        do_nothing=(
            f"If Labs does not test {title} for 7 days, it preserves optionality but loses a concrete M-3 feedback window; "
            "after 14-30 days the risk becomes more internal-system polish without paid-signal learning."
        ),
        wrong_path=f"If {title} is wrong, the most likely failure is: {risk}.",
        alternative_path=f"{alt_title} may be better if it can produce clearer buyer language, lower owner burden, or faster disconfirmation.",
        capability_failure=(
            "If delivery needs owner-heavy bespoke analysis, the path should be narrowed to a smaller diagnostic or downgraded."
        ),
        buyer_nonexistence=(
            "If no buyer can be described with urgent pain, budget, and reachable validation route, do not proceed to outreach."
        ),
        governance_drag=(
            "If reports, rituals, or old directives consume the 48h experiment window, the path is failing M-3 execution discipline."
        ),
        m_triangle_failure=(
            "If the path boosts M-3 but bypasses M-2 approval gates, it is unsafe; if it boosts M-2 ceremony but produces no value signal, it is drag."
        ),
        owner_burden_failure=(
            f"Owner burden risk: {owner_burden}. If owner becomes the operator, Aiden must shrink the action to a prepared approval decision."
        ),
        highest_risk_assumption=risk,
        fastest_disconfirming_test=_fastest_test(opportunity),
        recommended_adjustment=(
            "Keep as a 48h internal experiment plus optional Tier 1 evidence run; do not advance to external validation without owner approval."
        ),
    )
    return case.to_dict()


def build_counterfactual_matrix(opportunities: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [build_counterfactual_case(item, opportunities, context) for item in opportunities]


def rank_counterfactual_risks(counterfactual_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def score(case: Dict[str, Any]) -> int:
        text = " ".join(str(case.get(field, "")) for field in ("highest_risk_assumption", "owner_burden_failure", "buyer_nonexistence"))
        value = 0
        if "buyer" in text:
            value += 3
        if "budget" in text:
            value += 2
        if "owner" in text:
            value += 2
        if "governance" in text:
            value += 1
        return value

    ranked = [dict(case, risk_score=score(case)) for case in counterfactual_cases]
    return sorted(ranked, key=lambda item: int(item["risk_score"]), reverse=True)


def render_counterfactual_markdown(cases: List[Dict[str, Any]]) -> str:
    lines = ["## Counterfactual Stress Test"]
    for case in cases:
        lines.extend(
            [
                f"### {case['opportunity_title']}",
                f"- Do nothing: {case['do_nothing']}",
                f"- Wrong path: {case['wrong_path']}",
                f"- Alternative path: {case['alternative_path']}",
                f"- Capability failure: {case['capability_failure']}",
                f"- Buyer nonexistence: {case['buyer_nonexistence']}",
                f"- Governance drag: {case['governance_drag']}",
                f"- M Triangle: {case['m_triangle_failure']}",
                f"- Owner burden: {case['owner_burden_failure']}",
                f"- Highest risk assumption: {case['highest_risk_assumption']}",
                f"- Fastest disconfirming test: {case['fastest_disconfirming_test']}",
                f"- Recommended adjustment: {case['recommended_adjustment']}",
            ]
        )
    return "\n".join(lines)
