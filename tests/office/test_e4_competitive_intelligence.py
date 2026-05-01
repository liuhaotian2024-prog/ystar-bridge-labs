from pathlib import Path

from office.mission_command.competitive_intelligence_engine import build_competitive_intelligence
from office.mission_command.market_reality_model import build_market_reality_profile
from office.mission_command.opportunity_synthesis_engine import compare_generated_opportunities


ROOT = Path(__file__).resolve().parents[2]


def _source(opportunity_id):
    return {
        "source_id": "src_live_001",
        "url_or_public_identifier": "https://example.com/ai-governance",
        "domain": "example.com",
        "source_category": "public docs",
        "retrieved_at": "2026-05-01T00:00:00Z",
        "evidence_type": "live_public_read_only",
        "relevant_opportunity_ids": [opportunity_id],
        "summary": "Public source indicates demand for AI governance.",
        "buyer_pain_signal": "Teams need safer coding agents.",
        "pricing_signal": "$1500 advisory",
        "competitor_signal": "AI governance consultant",
        "substitute_signal": "internal policy checklist",
        "budget_signal": "security/platform budget",
        "confidence": "test",
        "limitations": ["unit test fixture"],
    }


def test_market_profile_refs_sources_when_live_evidence_exists():
    opportunity = {"opportunity_id": "opp_budget_governance_audit", "title": "Coding-Agent Governance Audit"}
    profile = build_market_reality_profile(opportunity, source_evidence=[_source("opp_budget_governance_audit")])
    assert profile["evidence_mode"] == "live_public_read_only_evidence"
    assert profile["market_evidence_refs"] == ["src_live_001"]
    assert "$1500 advisory" in profile["pricing_references"]


def test_market_profile_internal_only_when_no_sources():
    opportunity = {"opportunity_id": "opp_budget_governance_audit", "title": "Coding-Agent Governance Audit"}
    profile = build_market_reality_profile(opportunity)
    assert profile["evidence_mode"] == "internal_hypothesis_only"
    assert profile["market_evidence_refs"] == []


def test_competitive_intelligence_uses_source_evidence():
    opportunities = compare_generated_opportunities(ROOT)
    intel = build_competitive_intelligence(opportunities, ROOT, source_evidence=[_source("opp_budget_governance_audit")])
    assert intel["mode"] == "live_public_read_only_evidence"
    assert intel["live_research_executed"] is True
    assert intel["source_evidence_count"] == 1
