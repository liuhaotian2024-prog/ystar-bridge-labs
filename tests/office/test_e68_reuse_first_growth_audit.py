import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_reuse_first_audit_blocks_duplicate_rebuilds():
    data = json.loads((ROOT / "operations/external_validation/e68_reuse_first_growth_audit.json").read_text())
    assert data["passed"] is True
    risks = data["duplicate_capability_risks_checked"]
    assert risks["CIEU_schema_rebuilt"] is False
    assert risks["E65_market_model_rebuilt"] is False
    assert risks["E67_validation_overlay_rebuilt"] is False
    assert risks["K9Audit_ledger_concepts_rebuilt"] is False

