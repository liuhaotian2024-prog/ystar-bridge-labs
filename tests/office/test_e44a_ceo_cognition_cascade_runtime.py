from office.mission_command.e44a_ceo_cognition_cascade_runtime import run_ceo_cognition_cascade

TASK = {
    "task_title": "E43 replay",
    "task_description": "Prepare the fastest credible path toward one real external user successfully installing and understanding Y*gov / gov-mcp / Y*Bridge Labs' agent-company runtime value.",
}

def test_cascade_invokes_prior_capabilities_and_selects_route():
    result = run_ceo_cognition_cascade(TASK)
    ids = set(result["invoked_capability_ids"])
    assert "strategic_imagination" in ids or "six_dimensional_cognition" in ids
    assert "cross_domain_opportunity_field" in ids
    assert "task_resource_router" in ids
    for expected in ["customer_empathy_review", "demand_budget_reality_screen", "opportunity_evidence_ladder", "execution_boundary_alignment"]:
        assert expected in ids
    assert result["route_selection"]["route_improved_from_E43"] is True
    assert result["route_selection"]["user_facing_value_object"] == "Governed Agent Action Proof Packet"
    assert result["no_external_action"] is True
    assert len(result["stages"]) >= 14
