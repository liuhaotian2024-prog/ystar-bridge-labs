import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_bypass_fixtures_allow_valid_and_deny_invalid_packets():
    fixtures = _load("operations/external_validation/e81_cognitive_os_enforcement_fixture_results.json")

    assert fixtures["valid_packet_allowed"] is True
    assert fixtures["invalid_packets_denied"] is True
    assert fixtures["fixture_count"] >= 8


def test_e81_bypass_fixtures_cover_required_failure_modes():
    fixtures = _load("operations/external_validation/e81_cognitive_os_enforcement_fixture_results.json")
    by_id = {item["fixture_id"]: item for item in fixtures["results"]}

    for fixture_id in [
        "invalid_recent_memory_only",
        "invalid_no_counterfactual",
        "invalid_no_pre_action_cieu_prediction",
        "invalid_no_adversarial_critique",
        "invalid_construction_without_no_new_wheel",
        "invalid_L4_without_owner_approval",
        "invalid_unverified_runtime_active_capability",
        "invalid_forbidden_customer_paid_compliance_claim",
    ]:
        assert by_id[fixture_id]["decision"] == "DENY"
        assert by_id[fixture_id]["CIEU_style_validation_record"]
