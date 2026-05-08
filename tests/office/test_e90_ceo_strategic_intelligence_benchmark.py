from __future__ import annotations

from office.mission_command.e90_ceo_strategic_intelligence_benchmark import (
    BENCHMARK_DIMENSIONS,
    score_ceo_strategic_intelligence,
)
from office.mission_command.e90_market_grounded_strategy_run import (
    build_market_grounded_strategy_artifact,
)


def test_benchmark_scores_all_required_dimensions():
    strategy = build_market_grounded_strategy_artifact()

    result = score_ceo_strategic_intelligence(strategy)

    assert set(result["dimensions"]) == set(BENCHMARK_DIMENSIONS)
    assert result["strategic_intelligence_score"] >= 4.0
    assert result["pass"] is True
    assert result["benchmark_decision"] == "ALLOW"
    for dimension in result["dimensions"].values():
        assert {"score", "evidence_refs", "reason", "missing_evidence", "improvement_required"} <= set(dimension)


def test_benchmark_fails_shallow_strategy():
    strategy = build_market_grounded_strategy_artifact()
    strategy["external_market_evidence_map"]["evidence_items"] = []
    strategy["route_candidates"] = strategy["route_candidates"][:2]
    strategy["route_scoring"] = strategy["route_scoring"][:1]

    result = score_ceo_strategic_intelligence(strategy)

    assert result["pass"] is False
    assert result["benchmark_decision"] == "REQUIRE_REVISION"
    assert "external_market_grounding" in result["failed_dimensions"]
    assert "route_diversity" in result["failed_dimensions"]


def test_benchmark_denies_false_customer_or_revenue_claim():
    strategy = build_market_grounded_strategy_artifact()
    strategy["overclaim_boundary"]["customer_validation_claim"] = True

    result = score_ceo_strategic_intelligence(strategy)

    assert result["pass"] is False
    assert result["benchmark_decision"] == "DENY"
    assert "overclaim_boundary" in result["failed_dimensions"]
