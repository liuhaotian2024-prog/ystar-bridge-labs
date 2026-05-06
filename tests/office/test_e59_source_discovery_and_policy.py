from office.mission_command.e59_source_discovery_and_policy import run_source_discovery_and_policy


def test_source_domains_are_seed_domains_not_exhaustive_categories():
    data = run_source_discovery_and_policy()
    assert data["methodology_driven_discovery"] is True
    assert data["seed_domains_are_not_exhaustive"] is True
    assert data["max_candidate_sources"] == 60
    assert data["max_page_reads_one_run"] == 30
    assert all(source["human_contact_required"] is False for source in data["candidate_sources"])
    assert any("public academic" in item for item in data["new_source_type_allowed_if"])

