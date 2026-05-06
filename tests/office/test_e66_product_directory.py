import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "products/governed_business_operations_blueprint_for_agent_teams"


def test_e66_product_directory_contains_internal_sample_packet_only():
    assert (PRODUCT / "README.md").exists()
    assert (PRODUCT / "offer_blueprint.json").exists()
    sample = json.loads((PRODUCT / "sample_delivery_packet.json").read_text())
    assert sample["status"] == "draft_only_internal_sample"
    assert sample["no_named_real_customer"] is True
    assert sample["not_market_validation"] is True

