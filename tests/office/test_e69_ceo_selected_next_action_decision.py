import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_selected_next_action_is_internal_and_model_selected():
    data = json.loads((ROOT / "operations/external_validation/e69_ceo_selected_next_action_decision.json").read_text())
    assert data["selected_next_action"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
    assert data["selection_made_by_CEO_planning_model"] is True
    assert data["internal_only"] is True
    assert data["advances_CEO_autonomy"] is True
    assert data["next_recommended_milestone"] == "E70_execute_internal_CIEU_module_integration_no_external_action"

