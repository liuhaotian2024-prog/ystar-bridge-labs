import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_raw_file_inventory_uses_tracked_file_graph_first():
    inventory = _load("operations/external_validation/e80_raw_file_inventory.json")
    bridge = inventory["repos"]["bridge-labs"]

    assert inventory["method"] == "git_ls_files_first_raw_inventory_before_capability_interpretation"
    assert inventory["raw_discovery_phase"] is True
    assert inventory["interpretation_started"] is False
    assert bridge["tracked_file_count"] > 10000
    assert len(bridge["tracked_files"]) == bridge["tracked_file_count"]
    assert "office/mission_command" in bridge["counts_by_directory"]
    assert "operations/external_validation" in bridge["counts_by_directory"]
    assert "tests/office" in bridge["counts_by_directory"]
    assert "untracked_files" in bridge


def test_e80_readonly_repo_file_inventory_is_present_without_mutation_claims():
    inventory = _load("operations/external_validation/e80_raw_file_inventory.json")

    for repo in ["K9Audit", "Y-star-gov", "gov-mcp", "ystar-company"]:
        assert inventory["repos"][repo]["available"] is True
        assert inventory["repos"][repo]["tracked_file_count"] > 0
        assert inventory["repos"][repo]["untracked_file_count"] == 0
