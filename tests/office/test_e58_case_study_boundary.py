from office.mission_command.e58_case_study_boundary import build_case_study_boundary, build_case_study_json


def test_case_study_boundary_has_no_overclaim_claims_and_e59_requirement():
    boundary = build_case_study_boundary()
    case_study = build_case_study_json()
    assert boundary["case_study_name"] == "AI Agent Company Runtime Harness Case Study"
    assert "internal_L5_runtime_harness_proof" in boundary["current_proof_level"]
    assert case_study["selected_route_from_E57"] == "AI_agent_company_runtime_harness_case_study"
    assert case_study["E59_required_before_market_contact"] is True
    assert case_study["customer_validation_claimed"] is False
    assert case_study["paid_signal_claimed"] is False
    assert case_study["real_mcp_transport_claimed"] is False
    assert case_study["next_recommended_milestone"] == "E59_external_world_intelligence_L5_convergence"

