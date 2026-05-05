from office.mission_command.e36_demand_budget_reality_screen import build_demand_budget_reality_screen


def test_demand_budget_screen_exists_without_fabricating_demand():
    data = build_demand_budget_reality_screen()
    assert len(data["entries"]) >= 60
    assert data["strongest_near_term_buyer_patterns"]
    assert data["weakest_commercial_assumptions"]
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert all(entry["demand_fabricated"] is False for entry in data["entries"])
