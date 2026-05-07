import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_promoted_and_quarantined_assets_are_separated():
    promoted = json.loads((ROOT / "operations/external_validation/e71_promoted_legacy_assets.json").read_text())
    quarantined = json.loads((ROOT / "operations/external_validation/e71_quarantined_legacy_assets.json").read_text())
    assert promoted["promoted_count"] > 0
    assert promoted["canonical_truth_promoted"] is False
    assert quarantined["quarantined_count"] > 0
    assert any(row["cluster_id"] == "ystar_company_historical_sales_brain_cluster" for row in quarantined["quarantined_assets"])
    assert promoted["external_action_allowed"] is False
    assert quarantined["external_action_allowed"] is False

