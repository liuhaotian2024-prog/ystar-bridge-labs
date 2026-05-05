from office.mission_command.e34_institutional_void_mapper import build_institutional_void_mapper


def test_institutional_void_mapper_keeps_voids_before_products():
    artifact = build_institutional_void_mapper()
    assert artifact["institutional_voids_generated"] >= 10
    assert artifact["most_important_void"] == "agent_action_authority"
    assert artifact["no_final_product_selected"] is True
    assert any(void["void_id"] == "agent_liability_allocation" for void in artifact["voids"])
