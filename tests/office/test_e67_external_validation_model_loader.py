from office.mission_command.e67_ceo_external_validation_readback import (
    explain_validation_limits,
    get_external_validation_ladder,
    get_non_contact_validation_portfolio,
    get_route_external_validation_score,
    list_owner_gated_validation_next_steps,
)


def test_e67_loader_exposes_validation_overlay_api():
    assert len(get_external_validation_ladder()["levels"]) == 9
    score = get_route_external_validation_score("governed_business_operations_blueprint_for_agent_teams")
    assert score["route_id"] == "governed_business_operations_blueprint_for_agent_teams"
    assert get_non_contact_validation_portfolio()["primary_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert explain_validation_limits("governed_business_operations_blueprint_for_agent_teams")["public_evidence_equals_customer_feedback"] is False
    assert list_owner_gated_validation_next_steps()["requires_owner_approval_before_any_execution"] is True

