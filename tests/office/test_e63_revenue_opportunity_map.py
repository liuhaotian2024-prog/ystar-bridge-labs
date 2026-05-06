from office.mission_command.e63_revenue_opportunity_map import run_revenue_opportunity_map


def test_e63_opportunity_map_uses_clusters_not_people():
    data = run_revenue_opportunity_map()
    assert data["opportunity_cluster_count"] >= 1
    cluster = data["opportunity_clusters"][0]
    assert "buyer_category_clusters" in cluster
    assert cluster["owner_approval_required"] is True
    assert data["no_customer_validation_claimed"] is True
