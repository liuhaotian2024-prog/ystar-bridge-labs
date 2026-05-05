from office.mission_command.e37_opportunity_cluster_normalizer import build_normalized_opportunity_clusters


def test_normalized_clusters_exist_and_are_not_route_choices():
    data = build_normalized_opportunity_clusters()
    assert data["final_product_selected"] is False
    assert "AI productivity / workflow / toolchain" in data["active_clusters"]
    assert "enterprise / professional AI transformation" in data["active_clusters"]
    assert "agent economy / autonomous company" in data["parked_clusters"]
    assert len(data["clusters"]) >= 7
    for cluster in data["clusters"]:
        assert cluster["opportunity_ids"]
        assert cluster["taxonomy_confidence"] == "high"
