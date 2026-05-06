import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e46b_artifacts_and_closure_exist():
    contract = json.loads((ROOT / "operations/external_validation/e46b_canonical_runtime_spine_contract.json").read_text())
    rerun = json.loads((ROOT / "operations/external_validation/e46b_first_value_demo_canonical_spine_rerun.json").read_text())
    owner = json.loads((ROOT / "operations/external_validation/e46b_consolidated_owner_decision_packet.json").read_text())
    closure = json.loads((ROOT / "operations/external_validation/e46b_czl_closure.json").read_text())
    assert len(contract["stages"]) == 14
    assert rerun["canonical_spine_route"]["next_recommended_milestone"] == owner["recommended_next_milestone"]
    assert closure["no_external_action"] is True
    for key in ["no_customer_contact", "no_expert_contact", "no_human_identification", "no_scraping", "no_send", "no_publish", "no_login", "no_provider_API_execution", "no_internet_install", "no_payment", "no_secret_use"]:
        assert closure[key] is True
