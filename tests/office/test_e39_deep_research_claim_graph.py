from office.mission_command.e39_deep_research_claim_graph import build_deep_research_claim_graph


def test_claim_graph_preserves_evidence_boundaries():
    graph = build_deep_research_claim_graph()
    assert graph["node_count"] > 100
    assert graph["edge_count"] > 150
    assert graph["is_ceo_kg"] is False
    assert "enterprise / professional AI transformation" in graph["main_supported_clusters"]
    edge_types = {edge["type"] for edge in graph["edges"]}
    assert "source_supports_claim" in edge_types
    assert "claim_not_customer_validation" in edge_types
    assert "claim_not_paid_signal" in edge_types
    assert graph["customer_validation_claimed"] is False
    assert graph["paid_signal_claimed"] is False
