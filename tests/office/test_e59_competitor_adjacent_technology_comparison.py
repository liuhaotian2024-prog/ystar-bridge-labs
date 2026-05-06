from office.mission_command.e59_competitor_adjacent_technology_comparison import run_competitor_adjacent_technology_comparison


def test_competitor_adjacent_comparison_compares_categories_without_superiority_overclaim():
    data = run_competitor_adjacent_technology_comparison()
    assert data["comparison_count"] >= 8
    assert data["no_superiority_overclaim"] is True
    assert all(row["uncertain_claims_marked_unverified"] is True for row in data["comparisons"])

