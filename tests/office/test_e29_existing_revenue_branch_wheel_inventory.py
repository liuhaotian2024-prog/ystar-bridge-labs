import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_existing_wheel_audit_happened_before_e29_builds():
    data = json.loads((ROOT / "operations/external_validation/e29_existing_revenue_branch_wheel_inventory.json").read_text())
    assert data["audit_completed_before_new_e29_modules"] is True
    assert data["repos_scanned_count"] == 4
    assert data["existing_revenue_branch_wheels_found"] == 25
    assert data["reused_wheels_count"] == 15
    assert data["wrapped_or_extended_wheels_count"] == 5
    assert data["newly_built_wheels_count"] == 4
    assert data["gov_mcp_modification_required"] is False
