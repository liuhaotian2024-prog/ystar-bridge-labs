from office.mission_command.e34_non_obvious_opportunity_generator import build_non_obvious_opportunity_spaces


def test_opportunity_generator_creates_broad_non_hardcoded_space():
    artifact = build_non_obvious_opportunity_spaces()
    counts = artifact["counts"]
    assert counts["opportunity_spaces"] >= 20
    assert counts["not_direct_variants"] >= 10
    assert counts["strange_but_plausible"] >= 5
    assert counts["infrastructure_layer"] >= 5
    assert counts["service_first_or_wedge_first"] >= 5
    assert counts["protocol_or_standardization"] >= 3
    assert counts["insurance_liability_underwriting_adjacent"] >= 3
    assert counts["autonomous_company_operation"] >= 3
    assert counts["agent_labor_or_marketplace_trust"] >= 3
    assert artifact["no_final_product_hardcoded"] is True
