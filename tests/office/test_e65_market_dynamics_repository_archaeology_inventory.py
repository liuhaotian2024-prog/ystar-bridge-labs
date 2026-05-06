import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_archaeology_reuses_existing_market_assets():
    data = json.loads((ROOT / "operations/external_validation/e65_market_dynamics_repository_archaeology_inventory.json").read_text())
    assert data["asset_count"] > 0
    assert data["reusable_market_analysis_assets"]
    assert data["reusable_public_read_assets"]
    assert data["reusable_dual_axis_assets"]
    assert data["reusable_evidence_atom_assets"]
    assert data["new_layer_truly_required"]
