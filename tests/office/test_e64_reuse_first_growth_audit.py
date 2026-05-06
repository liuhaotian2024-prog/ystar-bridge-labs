import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_reuse_first_audit_blocks_duplicate_capabilities():
    data = json.loads((ROOT / "operations/external_validation/e64_reuse_first_growth_audit.json").read_text())
    assert data["passed"] is True
    assert data["duplicate_capability_created_without_justification"] is False
    assert data["reused_assets"]
    checks = data["duplicate_capability_risks_checked"]
    assert checks["public_read_adapter_rebuilt"] is False
    assert checks["behavior_authorization_gate_rebuilt"] is False
