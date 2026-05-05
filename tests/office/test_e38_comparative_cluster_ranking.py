from office.mission_command.e38_comparative_cluster_ranking import build_comparative_cluster_ranking


def test_comparative_ranking_preserves_tradeoffs_and_no_product_selection():
    data = build_comparative_cluster_ranking()
    assert data["evidence_ready_clusters"]
    assert data["expert_review_ready_clusters"]
    assert data["clusters_needing_more_public_research"]
    assert data["parked_clusters"]
    assert data["final_product_selected"] is False
    for row in data["ranking"]:
        assert row["tradeoff"]
