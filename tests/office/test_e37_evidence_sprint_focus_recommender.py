from office.mission_command.e37_evidence_sprint_focus_recommender import build_evidence_sprint_focus_recommendation


def test_focus_recommendation_is_not_final_product_selection():
    data = build_evidence_sprint_focus_recommendation()
    assert data["final_product_selected"] is False
    assert data["primary_evidence_sprint_clusters"]
    assert data["reason_not_final_product_selection"]
    assert data["reason_not_customer_validation"]
    assert data["reason_not_paid_signal"]
    assert data["taxonomy_repair_changed_ranking"] is True
