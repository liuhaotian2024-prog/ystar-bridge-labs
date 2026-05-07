import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_behavior_authorization_denies_external_and_readonly_mutation():
    data = json.loads((ROOT / "operations/external_validation/e71_behavior_authorization_result.json").read_text())
    assert data["passed"] is True
    assert "read_only_cross_repo_inspection" in data["allow"]
    assert "safe_internal_binding" in data["allow"]
    assert "mutating_read_only_repos" in data["deny"]
    assert "internet_package_install" in data["deny"]
    assert "external_skill_install" in data["deny"]
    assert data["read_only_repos_mutated"] is False
    assert data["external_business_execution_authorized"] is False
    assert data["external_action_allowed"] is False

