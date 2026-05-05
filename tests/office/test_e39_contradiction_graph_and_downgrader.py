from office.mission_command.e39_contradiction_graph_and_downgrader import build_contradiction_graph, build_unsupported_claim_downgrade_register


def test_contradictions_and_downgrades_forbid_overclaims():
    graph = build_contradiction_graph()
    register = build_unsupported_claim_downgrade_register()
    assert graph["contradiction_count"] == 2
    assert "AI productivity / workflow / toolchain" in graph["affected_clusters"]
    forbidden = set(register["forbidden_buyer_facing_claims"])
    assert "customer validation" in forbidden
    assert "paid signal" in forbidden
    assert "guaranteed ROI" in forbidden
    assert "product-market fit" in forbidden
    assert register["customer_validation_claimed"] is False
    assert register["paid_signal_claimed"] is False
