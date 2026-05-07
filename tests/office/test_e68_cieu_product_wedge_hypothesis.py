import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_product_wedge_is_internal_and_not_ordinary_logging():
    data = json.loads((ROOT / "operations/external_validation/e68_cieu_product_wedge_hypothesis.json").read_text())
    assert data["offer_name"] == "Governed Business Operations Blueprint + CIEU Audit Module"
    assert "not just event or trace spans" in data["why_not_ordinary_logging"]
    assert "EU AI Act compliance" in data["what_it_does_not_claim"]
    assert data["external_action_allowed"] is False

