import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_completion_gate_passes_with_truthful_route_status():
    data = json.loads((ROOT / "operations/external_validation/e68_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] in {
        "e68_cieu_route_promising_as_high_defensibility_vertical",
        "e68_cieu_route_deferred_due_to_evidence_or_sales_cycle_risk",
    }
    assert data["legal_compliance_claimed"] is False
    assert data["customer_validation_claimed"] is False
    assert data["recommended_next_milestone"] in {
        "E69_integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution",
        "E69_targeted_non_contact_validation_for_CIEU_high_risk_vertical",
    }

