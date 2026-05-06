from office.mission_command.e59_external_intelligence_route_impact import run_external_intelligence_route_impact


def test_route_impact_uses_evidence_atom_and_frontier_idea_ids():
    data = run_external_intelligence_route_impact()
    assert data["routes_evaluated"] >= 9
    for impact in data["route_impacts"]:
        assert impact["evidence_atom_ids"]
        assert impact["frontier_idea_ids"]
    assert data["no_customer_validation_from_public_readonly"] is True
    assert data["no_paid_signal_from_public_readonly"] is True
    assert data["recommended_next_milestone"] == "E60_post_external_intelligence_money_route_and_market_entry_readiness_retest"

