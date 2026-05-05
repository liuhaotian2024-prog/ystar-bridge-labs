from office.mission_command.e44a_ceo_capability_activation_registry import build_ceo_capability_activation_registry

def test_registry_contains_required_cognition_capabilities():
    registry = build_ceo_capability_activation_registry()
    ids = {item["capability_id"] for item in registry["capabilities"]}
    for expected in ["strategic_imagination", "innovation", "six_dimensional_cognition", "cross_domain_opportunity_field", "customer_empathy_review", "demand_budget_reality_screen", "opportunity_evidence_ladder", "evidence_intelligence_claim_graph", "contradiction_awareness", "frontier_capability_import", "task_resource_router", "reuse_first_no_rebuild_gate", "execution_boundary_alignment", "governance_boundary_alignment", "first_user_value_path"]:
        assert expected in ids
    assert registry["no_second_ceo_brain_created"] is True
    assert registry["no_second_ceo_kg_created"] is True
    assert all(item["maturity"] != "parked" or item["reason_if_parked"] for item in registry["capabilities"])
