from office.mission_command.e35_cross_domain_opportunity_field_generator import build_cross_domain_opportunity_field


def test_cross_domain_opportunity_field_has_required_breadth_and_boundaries():
    artifact = build_cross_domain_opportunity_field()
    counts = artifact["counts"]
    assert counts["total_opportunities"] >= 60
    assert counts["human_life_home_health"] >= 12
    assert counts["ai_productivity_workflow"] >= 12
    assert counts["education_creator_family_small_business"] >= 10
    assert counts["enterprise_professional"] >= 10
    assert counts["agent_economy_autonomous_company"] >= 8
    assert counts["hardware_ai_hybrid"] >= 8
    assert counts["strange_but_plausible"] >= 10
    assert counts["requires_new_capability"] >= 10
    assert counts["non_governance_audit_blackbox_preflight"] >= 10
    assert artifact["final_product_selected"] is False
    for opp in artifact["opportunities"]:
        assert opp["six_dimensional_cognition_summary"]
        assert opp["faculty_tension_map"]
        assert opp["evidence_status"] != "customer_validation"
        assert opp["imagination_status"] == "generated_opportunity_not_route"
