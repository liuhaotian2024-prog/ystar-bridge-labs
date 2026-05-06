import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_archaeology_identifies_constrained_and_unique_assets():
    data = json.loads((ROOT / "operations/external_validation/e64_dual_axis_repository_archaeology_inventory.json").read_text())
    assert data["asset_count"] > 0
    assert data["prior_route_artifacts_AI_product_constrained"]
    assert data["prior_route_artifacts_YBridge_unique"]
    assert data["assets_supporting_broader_business_execution"]
    assert "safe_public_page_reader" in " ".join(data["what_must_not_be_rebuilt"])
