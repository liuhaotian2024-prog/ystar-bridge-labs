import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_completion_gate_passes_for_autonomous_planning_loop():
    data = json.loads((ROOT / "operations/external_validation/e69_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] == "e69_ceo_selected_cieu_module_integration_as_next_action"
    assert data["selected_next_action"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
    assert data["candidate_count"] >= 10
    assert data["external_action_allowed"] is False

