from office.mission_command.e65_ceo_market_dynamics_readback import (
    explain_route_selection,
    get_decision_stability,
    get_market_dynamics_model,
    get_recommended_market_portfolio,
    get_route_evidence,
    list_update_triggers,
    rank_routes_by_profile,
)


def test_e65_loader_api_reads_real_artifacts():
    model = get_market_dynamics_model()
    assert model["universe"]["domain_count"] >= 30
    assert rank_routes_by_profile("balanced_CEO_profile")["rankings"]
    assert get_route_evidence("governed_business_operations_blueprint_for_agent_teams")["evidence_count"] >= 0
    assert get_decision_stability()["fragile_assumptions"]
    assert get_recommended_market_portfolio()["primary_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert explain_route_selection("governed_business_operations_blueprint_for_agent_teams")["selected"] is True
    assert list_update_triggers()["trigger_count"] >= 8
