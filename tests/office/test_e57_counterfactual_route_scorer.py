from office.mission_command.e57_counterfactual_route_scorer import build_counterfactual_route_matrix


def test_route_scoring_includes_l5_boost_and_missing_evidence_penalties():
    data = build_counterfactual_route_matrix()
    assert data["selected_route"] == "AI_agent_company_runtime_harness_case_study"
    assert data["validation"]["l5_capability_boost_included"] is True
    assert data["validation"]["missing_external_evidence_penalties_included"] is True
    outreach = next(r for r in data["routes"] if r["route_id"] == "direct_customer_outreach_now")
    assert outreach["decision"] == "deny"

