from office.mission_command.e59_external_observation_archaeology import run_external_observation_archaeology


def test_baseline_capability_archaeology_runs_before_new_assumptions():
    data = run_external_observation_archaeology()
    assert data["mandatory_first_phase_completed"] is True
    assert data["asset_count"] > 0
    assert data["E57_blocker"] == "external_page_read_adapter_unavailable"
    assert data["blocker_classification"] == "missing_or_disconnected_controlled_public_page_read_adapter"
    assert data["seed_domains_not_exhaustive"] is True
    assert data["external_knowledge_observation_not_human_contact"] is True

