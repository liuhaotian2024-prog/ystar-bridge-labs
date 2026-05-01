from pathlib import Path

from office.mission_command.tier1_research_runtime import resolve_tier1_research_capability


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_live_read_only_research_requires_explicit_config_and_budget():
    resolution = resolve_tier1_research_capability(REPO_ROOT)
    assert resolution["budget_requested"]["max_search_queries"] == 10
    assert resolution["live_research_executed"] is False
    if not resolution["live_read_only_available"]:
        assert resolution["mode"] == "blocked_missing_config"
        assert resolution["missing_config_actions"]


def test_fixture_evidence_is_not_counted_as_live_market_evidence():
    resolution = resolve_tier1_research_capability(REPO_ROOT)
    assert resolution["fixture_demo_available"] in {True, False}
    assert resolution["live_research_executed"] is False


def test_missing_live_research_produces_enablement_packet():
    resolution = resolve_tier1_research_capability(REPO_ROOT)
    packet = resolution["enablement_packet"]
    assert packet["recommended_owner_decision"] == "approve_or_revise_tier1_live_read_only_research"
    assert packet["boundary"]["no_contact"] is True
    assert packet["budget_requested"]["max_pages_read"] == 15
