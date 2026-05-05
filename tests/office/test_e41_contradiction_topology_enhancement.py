from office.mission_command.e41_contradiction_topology_enhancement import build_contradiction_topology_enhancement


def test_e41_contradiction_topology_enhancement_contract():
    artifact = build_contradiction_topology_enhancement()
    assert artifact["input_contradictions"] >= 2
    assert "customer validation" in artifact["buyer_facing_claims_forbidden"]
    assert "paid signal" in artifact["buyer_facing_claims_forbidden"]
    assert artifact["method_only_no_external_execution"] is True

