from __future__ import annotations

from statistics import mean
from typing import Any, Mapping


MILESTONE_ID = "E90_CEO_Strategic_Intelligence_Benchmark_And_Market_Grounded_Strategy_Run_R1"

BENCHMARK_DIMENSIONS: tuple[str, ...] = (
    "internal_capability_recall",
    "historical_route_recall",
    "external_market_grounding",
    "buyer_pain_clarity",
    "route_diversity",
    "counterfactual_quality",
    "commercial_sharpness",
    "speed_to_cash_reasoning",
    "evidence_strength",
    "risk_owner_burden_balance",
    "no_new_wheel_compliance",
    "adversarial_depth",
    "what_not_to_do_specificity",
    "prediction_testability",
    "next_action_executability",
    "residual_learning_plan",
)

CRITICAL_DIMENSIONS: tuple[str, ...] = (
    "external_market_grounding",
    "counterfactual_quality",
    "commercial_sharpness",
    "prediction_testability",
    "next_action_executability",
)

FORBIDDEN_CLAIM_FLAGS: tuple[str, ...] = (
    "customer_validation_claim",
    "revenue_claim",
    "payment_claim",
    "paid_signal_claim",
    "pricing_validation_claim",
    "L4_feedback_executed",
    "L5_revenue_loop_complete",
    "production_deployment_claim",
    "K9Audit_integration_claim",
)


def score_ceo_strategic_intelligence(strategy: Mapping[str, Any]) -> dict[str, Any]:
    """Score a structured CEO strategy artifact without LLM-as-judge."""

    dimensions = {
        "internal_capability_recall": _score_internal_capability_recall(strategy),
        "historical_route_recall": _score_historical_route_recall(strategy),
        "external_market_grounding": _score_external_market_grounding(strategy),
        "buyer_pain_clarity": _score_buyer_pain_clarity(strategy),
        "route_diversity": _score_route_diversity(strategy),
        "counterfactual_quality": _score_counterfactual_quality(strategy),
        "commercial_sharpness": _score_commercial_sharpness(strategy),
        "speed_to_cash_reasoning": _score_speed_to_cash_reasoning(strategy),
        "evidence_strength": _score_evidence_strength(strategy),
        "risk_owner_burden_balance": _score_risk_owner_burden_balance(strategy),
        "no_new_wheel_compliance": _score_no_new_wheel_compliance(strategy),
        "adversarial_depth": _score_adversarial_depth(strategy),
        "what_not_to_do_specificity": _score_what_not_to_do_specificity(strategy),
        "prediction_testability": _score_prediction_testability(strategy),
        "next_action_executability": _score_next_action_executability(strategy),
        "residual_learning_plan": _score_residual_learning_plan(strategy),
    }
    average = round(mean(item["score"] for item in dimensions.values()), 2)
    failed_dimensions = [
        dimension
        for dimension, item in dimensions.items()
        if item["score"] < 3 or (dimension in CRITICAL_DIMENSIONS and item["score"] < 4)
    ]
    forbidden_claim = _forbidden_claim(strategy)
    required_revisions = [
        item["improvement_required"]
        for dimension, item in dimensions.items()
        if dimension in failed_dimensions and item["improvement_required"]
    ]
    if forbidden_claim:
        decision = "DENY"
        passed = False
        failed_dimensions.append("overclaim_boundary")
        required_revisions.append(f"remove forbidden claim: {forbidden_claim}")
    elif average < 4.0 or failed_dimensions:
        decision = "REQUIRE_REVISION"
        passed = False
    elif _selected_strategy_requires_owner_execution(strategy):
        decision = "ESCALATE"
        passed = False
        required_revisions.append("route owner-bound L4/L5 action to owner decision packet before execution")
    else:
        decision = "ALLOW"
        passed = True

    return {
        "artifact_id": "e90_ceo_strategic_intelligence_benchmark_result",
        "milestone_id": MILESTONE_ID,
        "dimensions": dimensions,
        "strategic_intelligence_score": average,
        "pass": passed,
        "failed_dimensions": sorted(set(failed_dimensions)),
        "required_revisions": required_revisions,
        "benchmark_decision": decision,
        "pass_threshold": {
            "minimum_average": 4.0,
            "critical_dimension_minimum": 4,
            "hard_rules": [
                "no false customer/revenue/payment/pricing/L4/L5 claims",
                "external evidence must be present and freshness declared",
                "at least five routes",
                "next L4 packet must be no-send and owner-decision gated",
            ],
        },
        "truth_constraints": {
            "LLM_as_judge_used": False,
            "deterministic_structured_scoring": True,
            "no_customer_validation_claim": forbidden_claim != "customer_validation_claim",
            "no_revenue_payment_pricing_claim": forbidden_claim
            not in {"revenue_claim", "payment_claim", "paid_signal_claim", "pricing_validation_claim"},
        },
    }


def _score_internal_capability_recall(strategy: Mapping[str, Any]) -> dict[str, Any]:
    required = ("bridge-labs", "Y-star-gov", "gov-mcp", "K9Audit")
    text = _text(strategy.get("internal_capability_map"))
    missing = [name for name in required if name.lower() not in text]
    return _dimension(
        5 - min(len(missing), 4),
        "Internal capability map references the canonical owner repos and boundaries.",
        evidence_refs=["operations/baseline/e87r_full_repo_baseline/stable_vocabulary_and_owner_map.json"],
        missing_evidence=missing,
        improvement="map each canonical owner repo and its runtime role",
    )


def _score_historical_route_recall(strategy: Mapping[str, Any]) -> dict[str, Any]:
    assets = _as_list(strategy.get("historical_route_assets"))
    return _dimension(
        5 if len(assets) >= 6 else 3 if len(assets) >= 3 else 1,
        "Historical route recall is measured by explicit prior artifact references.",
        evidence_refs=assets[:8],
        missing_evidence=[] if len(assets) >= 6 else ["more historical route artifacts"],
        improvement="include E62-E79 route, offer, public-read, and L4 packet lineage",
    )


def _score_external_market_grounding(strategy: Mapping[str, Any]) -> dict[str, Any]:
    evidence = strategy.get("external_market_evidence_map") if isinstance(strategy.get("external_market_evidence_map"), Mapping) else {}
    items = _as_list(evidence.get("evidence_items")) if isinstance(evidence, Mapping) else []
    freshness = str(evidence.get("freshness_status", "")) if isinstance(evidence, Mapping) else ""
    score = 5 if len(items) >= 8 and "current" in freshness else 4 if len(items) >= 8 else 2 if items else 0
    return _dimension(
        score,
        "Public-read market evidence is present and categorized; it is not customer validation.",
        evidence_refs=[str(item.get("source_url") or item.get("source_path")) for item in items if isinstance(item, Mapping)][:8],
        missing_evidence=[] if score >= 4 else ["at least eight public-read market evidence items"],
        improvement="attach current public-read evidence and declare freshness/status",
    )


def _score_buyer_pain_clarity(strategy: Mapping[str, Any]) -> dict[str, Any]:
    evidence = _text(strategy.get("external_market_evidence_map")) + " " + _text(strategy.get("selected_strategy"))
    keywords = ("governance", "approval", "audit", "risk", "agent", "trust")
    hits = sum(1 for word in keywords if word in evidence)
    return _dimension(min(5, max(1, hits)), "Buyer pain is scored by explicit governance/audit/risk language.", [], [], "make buyer pain concrete")


def _score_route_diversity(strategy: Mapping[str, Any]) -> dict[str, Any]:
    routes = _as_list(strategy.get("route_candidates"))
    route_types = {str(route.get("route_type")) for route in routes if isinstance(route, Mapping)}
    return _dimension(
        5 if len(routes) >= 5 and len(route_types) >= 4 else 3 if len(routes) >= 5 else 1,
        "Route diversity requires at least five materially different routes.",
        [str(route.get("route_id")) for route in routes if isinstance(route, Mapping)][:8],
        [] if len(routes) >= 5 else ["five routes"],
        "add materially different routes",
    )


def _score_counterfactual_quality(strategy: Mapping[str, Any]) -> dict[str, Any]:
    scoring = _as_list(strategy.get("route_scoring"))
    required = (
        "speed_to_first_cash",
        "buyer_pain_intensity",
        "proof_needed",
        "implementation_readiness",
        "sales_friction",
        "differentiation",
        "trust_compliance_value",
        "owner_burden",
        "external_validation_next_step",
        "kill_criteria",
    )
    complete = [
        row for row in scoring if isinstance(row, Mapping) and all(key in row for key in required)
    ]
    return _dimension(
        5 if len(complete) >= 5 else 3 if len(complete) >= 3 else 1,
        "Counterfactual quality is scored by complete route scoring rows.",
        [str(row.get("route_id")) for row in complete[:8]],
        [] if len(complete) >= 5 else ["complete scoring rows for all routes"],
        "score all routes against the required dimensions",
    )


def _score_commercial_sharpness(strategy: Mapping[str, Any]) -> dict[str, Any]:
    scoring = _as_list(strategy.get("route_scoring"))
    has_kill = all(isinstance(row, Mapping) and _present(row.get("kill_criteria")) for row in scoring)
    has_first_cash = _present((strategy.get("selected_strategy") or {}).get("current_best_first_cash_path")) if isinstance(strategy.get("selected_strategy"), Mapping) else False
    score = 5 if has_kill and has_first_cash and len(scoring) >= 5 else 3 if has_first_cash else 1
    return _dimension(score, "Commercial sharpness requires first-cash logic plus kill criteria.", [], [] if score >= 4 else ["kill criteria or first-cash path"], "add sharper first-cash and kill logic")


def _score_speed_to_cash_reasoning(strategy: Mapping[str, Any]) -> dict[str, Any]:
    selected = strategy.get("selected_strategy") if isinstance(strategy.get("selected_strategy"), Mapping) else {}
    text = _text(selected)
    score = 5 if "48h" in text or "48" in text and "7d" in text or "7" in text else 4 if "first-cash" in text or "cash" in text else 2
    return _dimension(score, "Speed-to-cash is scored by explicit 48h/7d and first-cash actions.", [], [] if score >= 4 else ["specific 48h/7d actions"], "make speed-to-cash operational")


def _score_evidence_strength(strategy: Mapping[str, Any]) -> dict[str, Any]:
    internal = _as_list(strategy.get("historical_route_assets"))
    external = _as_list((strategy.get("external_market_evidence_map") or {}).get("evidence_items")) if isinstance(strategy.get("external_market_evidence_map"), Mapping) else []
    count = len(internal) + len(external)
    return _dimension(5 if count >= 16 else 4 if count >= 12 else 2, "Evidence strength combines repo and public-read evidence references.", [], [] if count >= 12 else ["more evidence refs"], "increase evidence coverage")


def _score_risk_owner_burden_balance(strategy: Mapping[str, Any]) -> dict[str, Any]:
    rows = _as_list(strategy.get("route_scoring"))
    has_owner_burden = all(isinstance(row, Mapping) and "owner_burden" in row for row in rows)
    no_send = (strategy.get("next_L4_feedback_owner_decision_packet") or {}).get("no_send_default") is True if isinstance(strategy.get("next_L4_feedback_owner_decision_packet"), Mapping) else False
    return _dimension(5 if has_owner_burden and no_send else 2, "Owner burden and no-send boundary are explicitly modeled.", [], [] if has_owner_burden and no_send else ["owner burden/no-send"], "model owner burden and no-send boundary")


def _score_no_new_wheel_compliance(strategy: Mapping[str, Any]) -> dict[str, Any]:
    text = _text(strategy.get("no_new_wheel_proof"))
    required = ("E87R", "E88", "E89", "Y-star-gov", "CIEUStore", "gov-mcp")
    missing = [item for item in required if item.lower() not in text]
    return _dimension(5 - min(len(missing), 4), "No-new-wheel proof references existing systems.", [], missing, "reference existing runtime/compiler/governance/dry-run systems")


def _score_adversarial_depth(strategy: Mapping[str, Any]) -> dict[str, Any]:
    critique = _as_list(strategy.get("adversarial_critique"))
    return _dimension(5 if len(critique) >= 4 else 3 if len(critique) >= 2 else 1, "Adversarial depth is scored by concrete failure modes.", [], [] if len(critique) >= 4 else ["more failure modes"], "add concrete adversarial critique")


def _score_what_not_to_do_specificity(strategy: Mapping[str, Any]) -> dict[str, Any]:
    items = _as_list(strategy.get("do_not_pursue_list")) + _as_list(strategy.get("what_not_to_do_next"))
    return _dimension(5 if len(items) >= 6 else 3 if len(items) >= 3 else 1, "What-not-to-do specificity is scored by concrete forbidden routes/actions.", [], [] if len(items) >= 6 else ["more explicit no-go actions"], "make constraints specific")


def _score_prediction_testability(strategy: Mapping[str, Any]) -> dict[str, Any]:
    predictions = _as_list(strategy.get("CIEU_predictions"))
    complete = [
        item for item in predictions if isinstance(item, Mapping) and _present(item.get("falsification_condition"))
    ]
    return _dimension(5 if complete else 1, "Prediction testability requires falsification conditions.", [], [] if complete else ["falsification condition"], "add testable CIEU predictions")


def _score_next_action_executability(strategy: Mapping[str, Any]) -> dict[str, Any]:
    packet = strategy.get("next_L4_feedback_owner_decision_packet") if isinstance(strategy.get("next_L4_feedback_owner_decision_packet"), Mapping) else {}
    ok = all(
        [
            packet.get("owner_decision_required") is True,
            packet.get("no_send_default") is True,
            packet.get("ai_transparency") is True,
            _present(packet.get("target_profile")),
            _present(packet.get("evidence_sought")),
            _present(packet.get("gov_mcp_dry_run_preflight_plan")),
            _present(packet.get("Y_star_gov_governance_plan")),
        ]
    )
    return _dimension(5 if ok else 2, "Next action is executable only as owner-gated no-send L4 packet.", [], [] if ok else ["complete owner-gated packet fields"], "complete no-send L4 owner decision packet")


def _score_residual_learning_plan(strategy: Mapping[str, Any]) -> dict[str, Any]:
    plan = strategy.get("post_strategy_residual_plan") if isinstance(strategy.get("post_strategy_residual_plan"), Mapping) else {}
    required = ("evaluate_strategy_quality_by", "future_evidence_updates", "pivot_trigger", "what_not_to_do_next")
    missing = [key for key in required if not _present(plan.get(key))]
    return _dimension(5 - min(len(missing), 4), "Residual plan needs evaluation, update, pivot, and no-go criteria.", [], missing, "complete residual learning plan")


def _dimension(
    score: int,
    reason: str,
    evidence_refs: list[str] | None,
    missing_evidence: list[str] | None,
    improvement: str,
) -> dict[str, Any]:
    bounded = max(0, min(5, score))
    return {
        "score": bounded,
        "evidence_refs": list(evidence_refs or []),
        "reason": reason,
        "missing_evidence": list(missing_evidence or []),
        "improvement_required": "" if bounded >= 4 else improvement,
    }


def _forbidden_claim(strategy: Mapping[str, Any]) -> str:
    checks = strategy.get("overclaim_boundary") or strategy.get("truth_constraints") or {}
    if isinstance(checks, Mapping):
        for field in FORBIDDEN_CLAIM_FLAGS:
            if checks.get(field) is True:
                return field
    text = _text(strategy)
    for phrase in (
        "customer validation complete",
        "revenue achieved",
        "paid signal achieved",
        "payment loop complete",
        "pricing validation complete",
        "l4 feedback executed",
        "l5 revenue loop complete",
    ):
        if phrase in text:
            return phrase
    return ""


def _selected_strategy_requires_owner_execution(strategy: Mapping[str, Any]) -> bool:
    packet = strategy.get("next_L4_feedback_owner_decision_packet")
    if not isinstance(packet, Mapping):
        return False
    return strategy.get("execute_L4_now") is True and packet.get("owner_approval_state") != "approved"


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", {}):
        return []
    return [value]


def _text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items()).lower()
    if isinstance(value, list):
        return " ".join(_text(item) for item in value).lower()
    return str(value or "").lower()


__all__ = [
    "BENCHMARK_DIMENSIONS",
    "MILESTONE_ID",
    "score_ceo_strategic_intelligence",
]
