from office.mission_command.e10_autonomous_target_discovery import (
    TARGET_SEGMENTS,
    build_e10_target_discovery_request,
    load_or_run_e10_target_discovery,
)


def test_target_discovery_request_has_required_segments():
    request = build_e10_target_discovery_request()
    assert len(request.target_segments_to_explore) >= 8
    assert "AI consultants/agencies needing governance layer" in TARGET_SEGMENTS
    assert "teams hiring for AI ops / LLMOps / AI evaluation / automation" in TARGET_SEGMENTS


def test_target_discovery_request_forbids_contact_and_scraping():
    request = build_e10_target_discovery_request()
    assert "customer_contact" in request.forbidden_actions
    assert "sending_messages" in request.forbidden_actions
    assert "collecting_personal_sensitive_data" in request.forbidden_actions


def test_public_target_discovery_static_fixture_has_receipt_and_sources():
    research = load_or_run_e10_target_discovery()
    assert research["receipt"]["public_target_discovery_ran"] is True
    assert research["receipt"]["external_action_executed"] is False
    assert len(research["sources"]) >= 20
