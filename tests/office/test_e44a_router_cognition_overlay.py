from office.mission_command.e44a_router_cognition_overlay import route_task_with_cognition_overlay

def test_first_user_task_routes_to_cognition_lenses():
    result = route_task_with_cognition_overlay("Prepare first real user value path for agent company runtime")
    tags = set(result["matched_cognition_tags"])
    for expected in ["first_user_value_path", "product_customer_empathy", "demand_budget_screen", "opportunity_generation", "execution_feasibility"]:
        assert expected in tags
    assert result["external_action_occurred"] is False

def test_innovation_and_business_route_hit_prior_cognition():
    innovation = route_task_with_cognition_overlay("innovation and creative strategic opportunity")
    assert {"innovation", "strategic_imagination"} & set(innovation["matched_cognition_tags"])
    assert any(cap in set(innovation["matched_capability_ids"]) for cap in ["innovation", "strategic_imagination", "six_dimensional_cognition"])
    route = route_task_with_cognition_overlay("business route and commercial wedge")
    assert "commercial_wedge" in set(route["matched_cognition_tags"])
    assert "evidence_ladder" in set(route["matched_cognition_tags"])
