import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_method_wheel_audit_scans_four_repos_before_building():
    data = json.loads((ROOT / "operations/external_validation/e30_existing_method_wheel_inventory.json").read_text())
    assert data["audit_completed_before_new_e30_modules"] is True
    assert data["repos_scanned_count"] == 4
    assert data["existing_method_wheels_found"] == 27
    assert data["reused_wheels_count"] == 17
    assert data["wrapped_wheels_count"] == 4
    assert data["newly_built_wheels_count"] == 4
    assert data["gov_mcp_modification_required"] is False
