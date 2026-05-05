from office.mission_command.e35_capability_abstraction_recombination_method import build_capability_abstraction_recombination_method


def test_capability_recombination_transfers_beyond_current_assets():
    artifact = build_capability_abstraction_recombination_method()
    assert artifact["abstract_capability_count"] >= 12
    assert artifact["non_governance_transfer_count"] >= 6
    assert artifact["new_capability_requirements_count"] >= 8
    assert artifact["examples_are_probes_not_routes"] is True
