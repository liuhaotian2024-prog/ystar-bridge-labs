from office.mission_command.e60_route_candidates_after_external_intelligence import run_route_candidates_after_external_intelligence


def test_e60_route_candidates_deny_outreach_and_publication():
    data = run_route_candidates_after_external_intelligence()
    routes = {item["route_id"]: item for item in data["candidates"]}
    assert data["candidate_count"] == 10
    assert routes["E61_direct_customer_outreach_now"]["decision_candidate"] == "deny"
    assert routes["E61_publish_case_study_now"]["decision_candidate"] == "deny"
    assert routes["E61_live_public_read_adapter_repair_or_host_network_refresh"]["decision_candidate"] == "internal_allowed"
    assert data["external_action_allowed"] is False
