import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_behavior_authorization_blocks_external_install_and_execution():
    data = json.loads((ROOT / "operations/external_validation/e70_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert "internal_self_improvement_candidate_generation" in data["allow"]
    assert "external_skill_installation" in data["deny"]
    assert "internet_package_install" in data["deny"]
    assert data["external_business_execution_authorized"] is False
    assert data["external_skill_installation_authorized"] is False
