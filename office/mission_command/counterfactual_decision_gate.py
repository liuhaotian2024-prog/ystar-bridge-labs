from __future__ import annotations

from typing import Any, Dict, List


def _risk_flags(case: Dict[str, Any]) -> Dict[str, bool]:
    text = " ".join(str(case.get(key, "")) for key in case).lower()
    highest_risk = str(case.get("highest_risk_assumption", "")).lower()
    owner_burden = str(case.get("owner_burden_failure", "")).lower()
    return {
        "buyer_nonexistence_risk": "no buyer" in text or "buyer" in highest_risk,
        "owner_burden_risk": "owner burden risk: medium" in owner_burden or "owner burden risk: high" in owner_burden or "owner-heavy" in highest_risk,
        "capability_failure_risk": "cannot execute" in highest_risk or "delivery" in highest_risk,
        "governance_drag_risk": "governance" in text and "drag" in text,
        "m_triangle_balance": "bypass" not in highest_risk and "unsafe" not in highest_risk,
    }


def _test_quality(case: Dict[str, Any]) -> int:
    test = str(case.get("fastest_disconfirming_test", "")).lower()
    score = 0
    if "48h" in test or "within 48" in test:
        score += 3
    if "if " in test and ("downgrade" in test or "kill" in test):
        score += 2
    if "sample" in test or "question" in test:
        score += 1
    return score


def _opportunity_by_title(opportunities: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {item["title"]: item for item in opportunities}


def evaluate_counterfactual_gate(
    opportunities: List[Dict[str, Any]],
    counterfactual_cases: List[Dict[str, Any]],
    behavior_matrix: List[Dict[str, Any]],
    evidence_status: Dict[str, Any],
) -> Dict[str, Any]:
    by_title = _opportunity_by_title(opportunities)
    scored: List[Dict[str, Any]] = []
    for case in counterfactual_cases:
        title = case["opportunity_title"]
        opportunity = by_title.get(title, {})
        flags = _risk_flags(case)
        owner_burden = str(opportunity.get("owner_burden", "")).lower()
        required = set(opportunity.get("behavior_capability_required", []))
        score = int(opportunity.get("method_score", 0))
        score += _test_quality(case)
        if owner_burden.startswith("low"):
            score += 2
        if "customer contact" in required or "publication" in required:
            score -= 1
        if flags["owner_burden_risk"] and not owner_burden.startswith("low"):
            score -= 2
        if "no buyer" in case["buyer_nonexistence"].lower():
            score -= 1
        if evidence_status.get("external") != "evidence_backed_live_read_only":
            score -= 1
        scored.append(
            {
                "opportunity_id": opportunity.get("opportunity_id"),
                "title": title,
                "gate_score": score,
                "risk_flags": flags,
                "fastest_disconfirming_test_quality": _test_quality(case),
                "highest_risk_assumption": case["highest_risk_assumption"],
                "fastest_disconfirming_test": case["fastest_disconfirming_test"],
            }
        )
    scored.sort(key=lambda item: int(item["gate_score"]), reverse=True)
    return {
        "gate": "counterfactual_decision_gate",
        "ranked": scored,
        "recommended_default_title": scored[0]["title"] if scored else None,
        "external_evidence_gap": evidence_status.get("external") != "evidence_backed_live_read_only",
        "external_action_executed": False,
    }


def maybe_change_default_recommendation(
    default: Dict[str, Any] | None,
    alternatives: List[Dict[str, Any]],
    gate_result: Dict[str, Any],
) -> Dict[str, Any] | None:
    if not default:
        return alternatives[0] if alternatives else None
    recommended_title = gate_result.get("recommended_default_title")
    if recommended_title == default.get("title"):
        return default
    for item in alternatives:
        if item.get("title") == recommended_title:
            return item
    return default


def explain_default_decision(default: Dict[str, Any] | None, gate_result: Dict[str, Any]) -> str:
    if not default:
        return "No default recommendation is available."
    ranked = gate_result.get("ranked", [])
    top = ranked[0] if ranked else {}
    changed = top.get("title") != default.get("title")
    if changed:
        return (
            f"Counterfactual gate changes the default to {top.get('title')} because it has a stronger gate score, "
            f"faster disconfirming test, or lower owner/capability risk."
        )
    return (
        f"Counterfactual gate confirms {default.get('title')} because it has the best gate score among available paths "
        "while preserving approval gates and a fast disconfirming test."
    )
