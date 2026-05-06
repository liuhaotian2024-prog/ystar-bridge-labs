from office.mission_command.e59_external_intelligence_architecture import run_external_intelligence_architecture


def test_architecture_distinguishes_observation_from_human_contact():
    data = run_external_intelligence_architecture()
    assert "public_page_read_adapter" in data["components"]
    assert data["external_knowledge_observation_allowed"] is True
    assert data["external_human_interaction_allowed"] is False
    assert data["rules"]["seed_domains_are_not_exhaustive"] is True
    assert data["rules"]["no_contact"] is True

