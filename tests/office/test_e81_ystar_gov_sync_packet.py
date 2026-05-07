import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_ystar_gov_sync_packet_is_ready_but_no_mutation():
    sync = _load("operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.json")
    patch = _load("operations/external_validation/e81_ystar_gov_patch_plan_no_mutation.json")

    assert sync["contract_id"] == "ceo_cognitive_os_loop_contract_v1"
    assert sync["Y_star_gov_mutated_in_E81"] is False
    assert sync["integration_target_candidates_from_YstarGov_inspection"]
    assert "missing pre-action CIEU prediction" in sync["denial_conditions"]
    assert patch["Y_star_gov_mutated"] is False
    assert patch["owner_approval_required_before_patch"] is True


def test_e81_sync_packet_preserves_y_star_gov_canonical_ownership():
    sync = _load("operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.json")

    assert "Y-star-gov remains canonical" in sync["non_duplication_proof"]
    assert "Y-star-gov" in sync["why_bridge_labs_cannot_be_canonical_enforcement_owner"]
    assert "canonical" in sync["why_bridge_labs_cannot_be_canonical_enforcement_owner"]
