import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_reuse_first_audit_does_not_rebuild_e65_or_readers():
    data = json.loads((ROOT / "operations/external_validation/e67_reuse_first_growth_audit.json").read_text())
    assert data["passed"] is True
    risks = data["duplicate_capability_risks_checked"]
    assert risks["E65_market_dynamics_model_rebuilt"] is False
    assert risks["public_read_adapter_rebuilt"] is False
    assert risks["evidence_atomizer_rebuilt"] is False

