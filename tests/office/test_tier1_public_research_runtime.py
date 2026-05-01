from pathlib import Path

from office.mission_command.e4_market_research_plan import build_e4_market_research_request
from office.mission_command.tier1_public_research import (
    DeterministicFakeTier1ResearchProvider,
    DisabledTier1ResearchProvider,
    Tier1ResearchBudget,
    Tier1ResearchReceipt,
    Tier1ResearchRequest,
    Tier1SourceEvidence,
    enforce_budget,
    safety_boundary,
    utc_now,
    validate_receipt,
    validate_request_safety,
    validate_source_evidence,
)


def _request(**budget_overrides):
    return Tier1ResearchRequest(
        mission_id="test",
        allowed_source_categories=["public docs"],
        query_plan=["q1"],
        page_read_plan=["https://example.com/a"],
        budget=Tier1ResearchBudget(**budget_overrides),
        stop_conditions=["stop"],
    )


def _source(oid="opp_budget_governance_audit"):
    return Tier1SourceEvidence(
        source_id="src_test_001",
        url_or_public_identifier="https://example.com/a",
        domain="example.com",
        source_category="public docs",
        retrieved_at=utc_now(),
        evidence_type="live_public_read_only",
        relevant_opportunity_ids=[oid],
        summary="Public source says teams need AI coding governance.",
        buyer_pain_signal="Teams need AI coding governance.",
        pricing_signal="$1000 advisory reference",
        competitor_signal="DevSecOps consultant",
        substitute_signal="internal checklist",
        budget_signal="engineering productivity budget",
        confidence="test",
        limitations=["fixture test only"],
    )


def test_tier1_receipt_cannot_mark_live_true_without_sources():
    now = utc_now()
    receipt = Tier1ResearchReceipt(
        mission_id="m",
        live_research_executed=True,
        provider_name="bad",
        started_at=now,
        completed_at=now,
        queries_used=["q"],
        pages_read=["https://example.com"],
        domains_touched=["example.com"],
        stopped_reason="bad",
        safety_boundary=safety_boundary(),
        external_action_executed=False,
        errors=[],
        source_summary_paths=[],
    )
    errors = validate_receipt(receipt, [])
    assert "live_research_true_without_sources" in errors
    assert "live_research_true_without_source_summary_paths" in errors


def test_tier1_budget_blocks_over_query_limit():
    request = _request(max_search_queries=0)
    assert "budget_exceeded:max_search_queries" in enforce_budget(request)


def test_tier1_budget_blocks_over_page_limit():
    request = _request(max_pages_read=0)
    assert "budget_exceeded:max_pages_read" in enforce_budget(request)


def test_tier1_budget_blocks_over_domain_limit():
    request = Tier1ResearchRequest(
        mission_id="test",
        allowed_source_categories=["public docs"],
        query_plan=[],
        page_read_plan=["https://a.example/x", "https://b.example/y"],
        budget=Tier1ResearchBudget(max_domains=1),
        stop_conditions=["stop"],
    )
    assert "budget_exceeded:max_domains" in enforce_budget(request)


def test_tier1_forbids_login_contact_form_payment_publication():
    request = build_e4_market_research_request()
    text = " ".join(request.forbidden_actions)
    for item in ["login", "customer_contact", "form_submission", "payment", "publication"]:
        assert item in text
    assert not validate_request_safety(request)


def test_provider_unavailable_keeps_live_research_false():
    receipt, sources = DisabledTier1ResearchProvider().run(build_e4_market_research_request())
    assert receipt.live_research_executed is False
    assert sources == []
    assert receipt.external_action_executed is False


def test_source_evidence_requires_public_identifier_domain_category_summary():
    source = _source()
    assert validate_source_evidence(source) == []


def test_fake_provider_live_requires_sources():
    provider = DeterministicFakeTier1ResearchProvider([_source()])
    receipt, sources = provider.run(_request())
    assert receipt.live_research_executed is True
    assert sources
    assert validate_receipt(receipt, sources) == []
