import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_no_overclaim_validation_blocks_validation_and_revenue_claims():
    data = json.loads((ROOT / "operations/external_validation/e64_no_overclaim_validation_result.json").read_text())
    assert data["passed"] is True
    update = json.loads((ROOT / "operations/external_validation/e64_ceo_brain_dual_axis_revenue_update.json").read_text())
    for field in [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "autonomous_revenue_achieved",
        "real_client_delivery_claimed",
        "owner_approval_fabricated",
        "pricing_validation_claimed",
        "global_optimality_proven",
    ]:
        assert update[field] is False
