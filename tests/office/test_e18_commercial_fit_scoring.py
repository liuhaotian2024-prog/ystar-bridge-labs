import json
from pathlib import Path

from office.mission_command.e18_commercial_fit_scoring import score_candidate

ROOT = Path(__file__).resolve().parents[2]


def test_commercial_fit_scores_are_deterministic_and_transparent():
    data = json.loads((ROOT / "operations/external_validation/e18_commercial_fit_scores.json").read_text())
    assert data["scoring_method"] == "deterministic_keyword_and_field_rules_no_llm_judge"
    assert "buyer_pain_fit" in data["score_fields"]
    assert data["scores"][0]["total_score"] >= data["scores"][-1]["total_score"]
    assert data["external_action_executed"] is False


def test_ready_agent_readiness_candidate_scores_high():
    candidate = {
        "action_id": "a",
        "target_id": "t",
        "target_name": "AI Consulting Agency",
        "status": "ready_for_owner_review",
        "evidence_basis": ["src1", "src2"],
        "buyer_pain_hypothesis": "AI agent implementation readiness governance risk",
        "selection_reason": "consulting team",
        "offer": "48h AI Agent Implementation Readiness Review",
        "risk_tier": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
    }
    assert score_candidate(candidate).total_score >= 34
