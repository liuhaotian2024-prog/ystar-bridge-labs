from office.mission_command.e36_adversarial_ceo_board_review import build_adversarial_ceo_board_review


def test_adversarial_review_is_same_brain_structured_review():
    data = build_adversarial_ceo_board_review()
    assert data["second_ceo_brain_created"] is False
    assert len(data["review_lenses"]) >= 9
    assert data["cluster_reviews"]
    assert data["strongest_pro_findings"]
    assert data["strongest_contra_findings"]
