import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_no_overclaim_validation_passes():
    data = json.loads((ROOT / "operations/external_validation/e71_no_overclaim_validation_result.json").read_text())
    assert data["passed"] is True
    assert data["violations"] == []
    ceo = json.loads((ROOT / "operations/external_validation/e71_ceo_brain_legacy_asset_resurrection_update.json").read_text())
    forbidden = [
        "old_assets_current_truth_claimed",
        "old_pricing_validated_claimed",
        "old_sales_assets_active_pipeline_claimed",
        "launch_assets_publication_approved_claimed",
        "provider_live_execution_enabled_claimed",
        "K9Audit_integration_completed_claimed",
        "customer_validation_claimed",
        "paid_signal_claimed",
        "pricing_validation_claimed",
        "legal_compliance_claimed",
        "owner_approval_claimed",
        "autonomous_revenue_achieved",
    ]
    assert all(ceo[field] is False for field in forbidden)
    assert ceo["external_action_allowed"] is False

