from pathlib import Path

from office.mission_command.e4_market_evidence_evaluator import evaluate_e4_market_evidence


ROOT = Path(__file__).resolve().parents[2]


def _source(source_id, opportunity_id):
    return {
        "source_id": source_id,
        "url_or_public_identifier": f"https://example.com/{source_id}",
        "domain": "example.com",
        "source_category": "public docs",
        "retrieved_at": "2026-05-01T00:00:00Z",
        "evidence_type": "live_public_read_only",
        "relevant_opportunity_ids": [opportunity_id],
        "summary": "Public evidence signal.",
        "buyer_pain_signal": "Urgent risk and blocked AI coding-agent adoption.",
        "pricing_signal": "$3000 advisory",
        "competitor_signal": "AI governance consultant",
        "substitute_signal": "internal checklist",
        "budget_signal": "security/platform budget",
        "confidence": "test",
        "limitations": ["unit test fixture"],
    }


def test_evaluator_penalizes_missing_external_evidence():
    evaluation = evaluate_e4_market_evidence(ROOT)
    assert evaluation["live_research_executed"] is False
    assert all(row["score"]["external_evidence_strength"] == 0 for row in evaluation["rows"])


def test_evaluator_can_change_top_path_when_evidence_changes():
    sources = [
        _source("s1", "opp_budget_governance_audit"),
        _source("s2", "opp_budget_governance_audit"),
        _source("s3", "opp_budget_governance_audit"),
    ]
    evaluation = evaluate_e4_market_evidence(ROOT, source_evidence=sources)
    assert evaluation["live_research_executed"] is True
    assert evaluation["top_path"] == "Coding-Agent Governance Audit"
    assert evaluation["default_is_market_backed"] is True


def test_evaluator_does_not_hardcode_agent_workflow_top():
    sources = [
        _source("s1", "opp_regulatory_security_mcp_boundary"),
        _source("s2", "opp_regulatory_security_mcp_boundary"),
        _source("s3", "opp_regulatory_security_mcp_boundary"),
    ]
    evaluation = evaluate_e4_market_evidence(ROOT, source_evidence=sources)
    assert evaluation["top_path"] != "Agent Workflow Bottleneck Diagnosis"


def test_evaluator_records_why_buyer_might_not_choose_us():
    row = evaluate_e4_market_evidence(ROOT)["rows"][0]
    assert row["why_buyer_might_not_choose_us"]
