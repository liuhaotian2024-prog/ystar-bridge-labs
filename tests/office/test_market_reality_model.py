from office.mission_command.market_reality_model import build_market_reality_profile, profile_has_competition


def test_market_reality_profile_requires_competitors_and_substitutes():
    profile = build_market_reality_profile(
        {
            "opportunity_id": "opp",
            "title": "Coding-Agent Governance Audit",
            "buyer": "Engineering leader",
            "pain": "AI coding-agent control is unclear.",
        }
    )
    assert profile_has_competition(profile)
    assert profile["direct_competitors"]
    assert profile["substitutes"]
    assert profile["no_action_alternative"]
    assert profile["diy_alternative"]
    assert profile["confidence"] == "low_internal_hypothesis_only"
