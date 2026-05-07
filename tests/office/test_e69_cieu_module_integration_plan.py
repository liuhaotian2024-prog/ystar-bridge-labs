import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products/governed_business_operations_blueprint_for_agent_teams"


def test_e69_cieu_module_plan_and_product_updates_are_internal_only():
    data = json.loads((ROOT / "operations/external_validation/e69_cieu_module_integration_plan.json").read_text())
    assert data["module_name"] == "CIEU Audit Module"
    assert data["selected_or_top2"] is True
    assert "EU AI Act compliance" in data["does_not_claim"]
    assert (PRODUCT / "cieu_audit_module.json").exists()
    updated = json.loads((PRODUCT / "updated_offer_blueprint_with_cieu_module.json").read_text())
    assert updated["status"] == "draft_only_internal"
    assert updated["EU_AI_Act_compliance_claimed"] is False
    assert updated["external_action_allowed"] is False

