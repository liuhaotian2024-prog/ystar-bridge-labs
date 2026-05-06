import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_evidence_quality_model_has_tiers_and_no_overclaim_rules():
    data = json.loads((ROOT / "operations/external_validation/e65_market_evidence_quality_model.json").read_text())
    tiers = {t["tier"] for t in data["tiers"]}
    assert {"T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"}.issubset(tiers)
    assert data["customer_validation_absent_in_E65"] is True
    assert data["paid_signal_absent_in_E65"] is True
