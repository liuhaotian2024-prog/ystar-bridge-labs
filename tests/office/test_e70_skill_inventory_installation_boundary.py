import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_skill_inventory_installation_boundary_prevents_install_claims():
    data = json.loads((ROOT / "operations/external_validation/e70_skill_inventory_and_installation_boundary.json").read_text())
    assert data["local_skill_inventory_allowed"] is True
    assert data["external_skill_installation_executed"] is False
    assert data["internet_package_install_attempted"] is False
    assert data["external_skill_package_install_prohibited_without_owner_approval"] is True
    assert data["all_skill_installation_proposals_require_behavior_authorization_and_owner_gate"] is True
