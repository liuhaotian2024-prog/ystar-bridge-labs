from pathlib import Path

from office.mission_command.opportunity_synthesis_engine import compare_generated_opportunities


ROOT = Path(__file__).resolve().parents[2]


def test_opportunity_expansion_generates_at_least_12():
    opportunities = compare_generated_opportunities(ROOT)
    assert len(opportunities) >= 12


def test_opportunity_expansion_uses_at_least_8_lenses():
    opportunities = compare_generated_opportunities(ROOT)
    lenses = {item["generated_from_lens"] for item in opportunities}
    assert len(lenses) >= 8
    assert "competition gap lens" in lenses
    assert "open-source-to-paid-support lens" in lenses


def test_every_top_opportunity_has_no_action_and_diy_alternative():
    from office.mission_command.market_reality_model import build_market_reality_profile

    for opportunity in compare_generated_opportunities(ROOT)[:5]:
        profile = build_market_reality_profile(opportunity)
        assert profile["no_action_alternative"]
        assert profile["diy_alternative"]
