import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_reuse_first_growth_audit_passes_without_duplicate_models():
    data = json.loads((ROOT / "operations/external_validation/e70_self_bootstrap_reuse_first_growth_audit.json").read_text())
    assert data["passed"] is True
    assert any("E69" in asset for asset in data["reused_assets"])
    assert any("does not rebuild E65" in risk for risk in data["duplicate_capability_risks_checked"])
    assert "office/mission_command/e70_ceo_capability_growth_model.py" in data["thin_wrappers_added"]
