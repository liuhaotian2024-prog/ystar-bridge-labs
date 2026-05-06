import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_completion_gate_passes_with_dual_axis_selection():
    data = json.loads((ROOT / "operations/external_validation/e64_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] in {
        "e64_dual_axis_retest_completed_runtime_harness_survived",
        "e64_dual_axis_retest_partial_with_public_read_blocker",
    }
    assert data["selected_final_first_cash_path"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["runtime_harness_blueprint_created"] is True
    assert data["recommended_next_milestone"] == "E65_draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution"
