from office.mission_command.e63_public_read_opportunity_discovery_plan import run_public_read_opportunity_discovery_plan


def test_e63_public_read_plan_is_bounded_and_no_contact():
    data = run_public_read_opportunity_discovery_plan()
    assert 1 <= data["planned_source_count"] <= data["max_live_page_reads"]
    assert data["uses_search_provider_api"] is False
    assert data["no_contact_pages"] is True
    assert data["no_human_identification"] is True
    assert all(item["policy_status"] == "allowed" for item in data["planned_sources"])
