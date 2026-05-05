from office.mission_command.e40_evidence_ready_cluster_selection import build_evidence_ready_cluster_selection


def test_selected_clusters_are_preflight_ready_not_products():
    selection = build_evidence_ready_cluster_selection()
    clusters = {c["cluster"] for c in selection["selected_clusters"]}
    assert clusters == {"enterprise / professional AI transformation", "AI productivity / workflow / toolchain", "governance / trust / audit / legitimacy"}
    assert selection["final_product_selected"] is False
    assert selection["customer_validation_claimed"] is False
    assert selection["paid_signal_claimed"] is False
    assert selection["preserved_high_imagination_watchlist"]
