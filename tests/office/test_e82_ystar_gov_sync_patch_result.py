import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e82_sync_patch_result_records_ystar_gov_validator():
    result = _load("operations/external_validation/e82_ystar_gov_sync_patch_result.json")

    assert result["owner_decision_status"] == "APPROVE_YSTARGOV_CEO_COGNITIVE_OS_SYNC_PATCH"
    assert result["validator_status"] == "YstarGov_synced"
    assert result["bypass_status"] == "denied"
    assert result["live_cross_repo_fixture_passed"] is True
    assert result["Y_star_gov_module_path"] == "ystar/governance/ceo_cognitive_os_contract.py"
    assert "validate_ceo_pre_action_packet" in result["exported_symbols"]
    assert result["external_action_executed"] is False


def test_e82_insertion_point_narrowing_is_small_not_broad_surface_patch():
    narrowing = _load("operations/external_validation/e82_ystar_gov_real_insertion_point_narrowing.json")
    selected = {item["candidate_id"] for item in narrowing["selected_patch_targets"]}

    assert "canonical_check_path" in selected
    assert "test_fixture_path" in selected
    assert len(narrowing["minimal_patch_target_set"]) == 4
    assert all(item["selected_for_patch"] is False for item in narrowing["rejected_or_deferred_targets"])

