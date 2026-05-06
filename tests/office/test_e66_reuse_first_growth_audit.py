import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_reuse_first_audit_blocks_duplicate_model_rebuild():
    data = json.loads((ROOT / "operations/external_validation/e66_reuse_first_growth_audit.json").read_text())
    assert data["passed"] is True
    risks = data["duplicate_capability_risks_checked"]
    assert risks["E65_market_model_rebuilt"] is False
    assert risks["route_scoring_engine_rebuilt"] is False
    assert risks["public_read_adapter_rebuilt"] is False

