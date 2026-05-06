from office.mission_command.e57_public_readonly_evidence_preflight import run_public_readonly_evidence_preflight


def test_public_readonly_refresh_blocks_without_safe_adapter():
    data = run_public_readonly_evidence_preflight()
    assert data["safe_public_readonly_observation_available"] is False
    assert data["blocker"] == "external_page_read_adapter_unavailable"
    assert data["external_action_allowed"] is False

