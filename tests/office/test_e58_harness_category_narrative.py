from office.mission_command.e58_harness_category_narrative import build_harness_category_narrative


def test_harness_category_narrative_avoids_market_claims():
    data = build_harness_category_narrative()
    joined = " ".join(data["narrative_points"])
    assert "runtime harness" in joined
    assert "external intelligence L5" in joined
    assert data["category_leadership_claimed"] is False
    assert data["market_validation_claimed"] is False
    assert data["customer_demand_claimed"] is False

