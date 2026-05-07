import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_reuse_first_audit_blocks_model_rebuilds():
    data = json.loads((ROOT / "operations/external_validation/e69_reuse_first_growth_audit.json").read_text())
    assert data["passed"] is True
    risks = data["duplicate_capability_risks_checked"]
    assert risks["E65_market_model_rebuilt"] is False
    assert risks["E67_external_validation_model_rebuilt"] is False
    assert risks["E68_CIEU_route_model_rebuilt"] is False
    assert risks["behavior_authorization_gate_rebuilt"] is False

