import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_market_signal_taxonomy_has_dynamic_update_signals():
    data = json.loads((ROOT / "operations/external_validation/e65_market_signal_taxonomy.json").read_text())
    names = {s["signal_type"] for s in data["signals"]}
    assert data["signal_type_count"] == 20
    assert "buyer_pain_signal" in names
    assert "YBridge_uniqueness_signal" in names
    assert "strategic_compounding_signal" in names
    assert all("customer validation" in s["no_overclaim_boundary"] for s in data["signals"])
