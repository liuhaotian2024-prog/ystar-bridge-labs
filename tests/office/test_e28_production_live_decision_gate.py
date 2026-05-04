import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_decision_gate_recommends_secure_config_but_not_live_execution():
    d = json.loads((ROOT / "operations/external_validation/e28_production_live_decision_gate.json").read_text())
    assert d["recommended_route"] == "proceed_to_secure_production_config_preparation"
    assert d["production_live_config_preparation_recommended"] is True
    assert d["evidence_expansion_recommended"] is True
    assert d["offer_revision_recommended"] is False
    assert d["provider_selection_research_needed"] is False
    assert d["canary_execution_allowed"] is False
    assert d["production_live_receipt_count"] == 0
