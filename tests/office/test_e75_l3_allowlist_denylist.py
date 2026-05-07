import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e75_l3_allowlist_and_denylist_exist_and_remain_no_execution():
    data = json.loads((ROOT / "operations/external_validation/e75_l3_source_allowlist_and_denylist.json").read_text())

    assert data["allowlist_status"] == "proposed_for_owner_approval_not_executed"
    assert len(data["allowed_source_categories"]) >= 8
    assert "private communities" in data["denylisted_source_categories"]
    assert "read public pages" in data["allowed_future_L3_actions"]
    assert "contacting customers" in data["denied_future_L3_actions"]
    assert data["even_if_E76_is_later_approved_E76_remains_read_only_non_contact"] is True
    assert data["owner_approval_required_before_use"] is True
    assert data["external_action_allowed"] is False


def test_e75_packet_scope_budget_is_controlled():
    packet = json.loads((ROOT / "operations/external_validation/e75_l3_owner_decision_packet.json").read_text())
    scope = packet["maximum_scope_and_budget"]

    assert scope["maximum_source_pages"] == 30
    assert scope["maximum_source_categories"] == 6
    assert scope["maximum_search_themes"] == 5
    assert scope["receipts_required_for_every_source"] is True
    assert scope["public_read_only"] is True
