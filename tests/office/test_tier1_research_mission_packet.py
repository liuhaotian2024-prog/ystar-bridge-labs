from office.mission_command.tier1_research_mission_packet import build_tier1_research_mission_packet


def test_tier1_research_packet_has_budget_and_stop_conditions():
    packet = build_tier1_research_mission_packet()
    assert packet["max_search_queries"] == 10
    assert packet["max_pages_read"] == 15
    assert packet["max_domains"] == 8
    assert packet["stop_conditions"]
    assert packet["budget_receipt_format"]["no_contact"] is True


def test_tier1_research_packet_targets_top_paths():
    packet = build_tier1_research_mission_packet()
    text = str(packet)
    assert "Agent Workflow Bottleneck Diagnosis" in text
    assert "Founder AI Workflow Audit" in text
    assert "Coding-Agent Governance Audit" in text


def test_tier1_research_packet_owner_approval_options():
    packet = build_tier1_research_mission_packet()
    assert packet["owner_approval_options"] == ["approve", "reject", "request_revision", "hold"]


def test_tier1_research_packet_no_live_execution():
    packet = build_tier1_research_mission_packet()
    assert packet["live_research_executed"] is False
    assert packet["external_action_executed"] is False


def test_no_external_side_effects():
    packet = build_tier1_research_mission_packet()
    assert packet["no_login"] is True
    assert packet["no_contact"] is True
    assert packet["no_form_submit"] is True
    assert packet["no_payment"] is True
    assert packet["no_publication"] is True
