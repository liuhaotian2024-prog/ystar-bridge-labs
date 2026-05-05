from office.mission_command.e36_new_capability_creation_planner import build_new_capability_creation_planner


def test_new_capability_planner_prevents_build_before_evidence():
    data = build_new_capability_creation_planner()
    assert data["summary"]["new_capabilities_needed"] > 0
    assert data["summary"]["worth_building_before_evidence_count"] == 0
    assert data["anti_extremes"]
    assert any(item["belongs_in"] in {"bridge-labs", "future repo", "external partner", "Y-star-gov", "gov-mcp"} for item in data["capability_items"])
