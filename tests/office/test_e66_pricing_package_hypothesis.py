import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_pricing_package_hypothesis_is_unvalidated():
    data = json.loads((ROOT / "operations/external_validation/e66_model_driven_pricing_package_hypothesis.json").read_text())
    assert len(data["package_tiers"]) == 3
    assert data["pricing_validation_claimed"] is False
    assert data["owner_approval_required_before_external_presentation"] is True

