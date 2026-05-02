from dataclasses import replace

from office.mission_command.e10_autonomous_target_discovery import load_or_run_e10_target_discovery
from office.mission_command.e10_shortest_revenue_path_scorer import rank_e10_shortest_revenue_paths, score_e10_candidate
from office.mission_command.e10_target_candidate_registry import (
    E10ContactChannelStatus,
    build_e10_target_candidate_registry,
)


def _candidates():
    return build_e10_target_candidate_registry(load_or_run_e10_target_discovery()["sources"])


def test_shortest_revenue_path_scores_pain_budget_urgency_reachability():
    scores = rank_e10_shortest_revenue_paths(_candidates())
    top = scores[0]
    assert top.candidate_score > 0
    assert top.reachability >= 1
    assert top.offer_fit >= 1
    assert top.expected_signal_speed >= 1


def test_shortest_revenue_path_penalizes_high_contact_risk():
    base = _candidates()[0]
    reachable = replace(base, contact_channel_status=E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL)
    blocked = replace(base, contact_channel_status=E10ContactChannelStatus.NOT_CONTACTABLE_SAFELY)
    assert score_e10_candidate(reachable).candidate_score > score_e10_candidate(blocked).candidate_score


def test_shortest_revenue_path_penalizes_high_owner_burden():
    base = _candidates()[0]
    low_burden = replace(base, contact_channel_status=E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL)
    high_burden = replace(base, contact_channel_status=E10ContactChannelStatus.PUBLIC_ROLE_ONLY_NO_CONTACT)
    assert score_e10_candidate(low_burden).owner_burden < score_e10_candidate(high_burden).owner_burden
