import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_offer_variant_matrix_contains_required_variants():
    data = json.loads((ROOT / "operations/external_validation/e18_offer_variant_matrix.json").read_text())
    ids = {item["variant_id"] for item in data["variants"]}
    assert "direct_readiness_review" in ids
    assert "risk_reduction_framing" in ids
    assert "implementation_bottleneck_framing" in ids
    assert "founder_operator_pain_framing" in ids
    assert "lightweight_advisory_framing" in ids
    assert data["lead_offer"] == "48h AI Agent Implementation Readiness Review"
    assert data["external_action_executed"] is False
