from office.mission_command.e73_ceo_real_work_readiness import load_ceo_real_work_readiness_gate


def test_e73_ceo_real_work_readiness_gate_returns_concrete_level_decisions():
    gate = load_ceo_real_work_readiness_gate()
    levels = gate["level_decisions"]

    assert gate["highest_ready_level"] == "L2_internal_autonomous_work_ready"
    assert levels["L2_internal_autonomous_work_ready"]["readiness_decision"] == "ready"
    assert levels["L3_controlled_read_only_external_research_ready"]["readiness_decision"] == "conditionally_ready"
    assert levels["L4_owner_approved_external_action_ready"]["readiness_decision"] == "not_ready"
    assert levels["L5_revenue_work_ready"]["readiness_decision"] == "not_ready"
    assert levels["L3_controlled_read_only_external_research_ready"]["missing_evidence"]
    assert levels["L4_owner_approved_external_action_ready"]["missing_evidence"]
    assert levels["L5_revenue_work_ready"]["missing_evidence"]
    assert gate["external_action_allowed"] is False


def test_e73_l2_readiness_allows_internal_real_work_only():
    gate = load_ceo_real_work_readiness_gate()
    l2 = gate["level_decisions"]["L2_internal_autonomous_work_ready"]

    assert l2["readiness_decision"] == "ready"
    assert "real internal research" in l2["allowed_action_class"]
    assert "network" in l2["forbidden_action_class"]
    assert "outreach" in l2["forbidden_action_class"]
    assert "publication" in l2["forbidden_action_class"]
    assert l2["next_smallest_closure"] == "E74_CEO_L2_Internal_Autonomous_Work_Pilot"
