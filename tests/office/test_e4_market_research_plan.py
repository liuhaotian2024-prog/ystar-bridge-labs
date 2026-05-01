from office.mission_command.e4_market_research_plan import (
    ALLOWED_SOURCE_CATEGORIES,
    E4_OPPORTUNITY_FAMILIES,
    build_e4_market_research_request,
    render_e4_market_research_plan,
)


def test_e4_market_research_plan_covers_required_families():
    request = build_e4_market_research_request()
    assert len(E4_OPPORTUNITY_FAMILIES) >= 8
    assert "Coding-Agent Governance Audit" in E4_OPPORTUNITY_FAMILIES
    assert len(request.query_plan) <= request.budget.max_search_queries
    assert "public GitHub repos/issues/discussions" in ALLOWED_SOURCE_CATEGORIES


def test_e4_market_research_plan_mentions_no_fake_completion():
    text = render_e4_market_research_plan(build_e4_market_research_request())
    assert "No live research may be treated as evidence-backed" in text
    assert "customer_contact" in text
