import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_cognitive_os_contract_has_mandatory_evidence_backed_stages():
    contract = _load("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json")

    assert contract["contract_id"] == "ceo_cognitive_os_loop_contract_v1"
    assert contract["discovery_evidence_based"] is True
    assert contract["mandatory_stage_count"] >= 10
    assert contract["can_be_enforced_immediately_in_bridge_labs_preflight"] is True
    assert contract["canonical_governance_owner"] == "Y-star-gov"
    assert contract["bridge_labs_role"] == "pre_sync_validator_and_contract_packet_owner"
    assert contract["bypass_allowed"] is False
    assert all(stage["evidence_source_paths"] for stage in contract["mandatory_stages"])


def test_e81_contract_stages_define_pass_fail_and_cieu_fields():
    contract = _load("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json")

    for stage in contract["mandatory_stages"]:
        assert stage["pass_condition"]
        assert stage["fail_condition"]
        assert stage["Y_star_contract_clause"]
        assert stage["CIEU_pre_action_fields"]
        assert stage["CIEU_post_action_fields"]
        assert stage["bypass_allowed"] is False
