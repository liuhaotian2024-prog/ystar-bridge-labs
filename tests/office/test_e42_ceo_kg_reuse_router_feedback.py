from office.mission_command.e42_ceo_kg_reuse_router_feedback import build_ceo_kg_reuse_router_feedback


def test_ceo_kg_reuse_router_feedback_is_delta_only():
    artifact = build_ceo_kg_reuse_router_feedback()
    assert artifact["node_count"] >= 5
    assert artifact["edge_count"] >= 4
    assert artifact["customer_validation_claimed"] is False
    assert artifact["paid_signal_claimed"] is False
