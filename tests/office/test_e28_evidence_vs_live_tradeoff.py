import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_tradeoff_recommends_config_preparation_with_evidence_as_backup():
    d = json.loads((ROOT / "operations/external_validation/e28_evidence_vs_live_tradeoff.json").read_text())
    assert d["recommended_route"] == "proceed_to_secure_production_config_preparation"
    assert d["backup_route"] == "evidence_expansion_first"
    assert d["production_live_config_preparation_recommended"] is True
    assert d["evidence_expansion_recommended"] is True
    assert d["offer_revision_recommended"] is False
    assert d["provider_selection_research_needed"] is False
