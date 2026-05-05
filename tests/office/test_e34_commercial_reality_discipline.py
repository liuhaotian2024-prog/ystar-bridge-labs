from office.mission_command.e34_commercial_reality_discipline import build_commercial_reality_discipline


def test_commercial_reality_discipline_separates_imagination_from_readiness():
    artifact = build_commercial_reality_discipline()
    assert artifact["opportunity_tests_count"] >= 20
    assert "imagination_quality" in artifact["separation"]
    assert "evidence_strength" in artifact["separation"]
    assert "commercial_readiness" in artifact["separation"]
    assert artifact["owner_burden_reduction_exists"] is True
    assert "No buyer interview" in artifact["biggest_credibility_gap"]
