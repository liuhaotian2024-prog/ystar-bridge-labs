import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_candidate_set_is_generated_by_ceo_planner_from_installed_state():
    data = json.loads((ROOT / "operations/external_validation/e69_ceo_next_action_candidate_set.json").read_text())
    assert data["generated_from_installed_capabilities"] is True
    assert data["candidate_count"] >= 10
    ids = {item["candidate_id"] for item in data["candidates"]}
    assert "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution" in ids
    assert "refresh_buyer_understandability_language_from_market_dynamics_no_contact" in ids
    assert all(item["generated_by_CEO_planner"] is True for item in data["candidates"])
    assert all(item["external_action_required"] is False for item in data["candidates"])

