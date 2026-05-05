import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(name):
    return json.loads((ROOT / "operations" / "external_validation" / f"{name}.json").read_text())


def test_owner_validation_route_is_prepared_but_not_executed():
    route = read("e33_owner_validation_route")
    assert route["route_status"] == "prepared_not_executed"
    assert route["owner_approval_boundary"]["send_in_e33"] is False
    assert route["owner_approval_boundary"]["contact_in_e33"] is False
    assert route["owner_approval_boundary"]["publication_in_e33"] is False
    assert route["owner_approval_boundary"]["next_milestone_requires_explicit_owner_approval_before_external_outreach"] is True
    assert "short_reviewer_message_draft" in route["prepared_but_unsent_materials"]


def test_czl_closure_flags_and_delivery_shape():
    czl = read("e33_czl_closure")
    assert czl["e33_demo_packet_completed"] is True
    assert czl["no_rebuild_gate_passed"] is True
    assert czl["customer_contact_occurred"] is False
    assert czl["message_sent"] is False
    assert czl["published_externally"] is False
    assert czl["provider_api_called"] is False
    assert czl["production_live_enabled"] is False
    assert czl["production_live_receipt_count"] == 0
    shape = czl["required_delivery_result_shape"]
    assert shape["committed"] is True
    assert shape["pushed"] is True
    assert shape["remote_confirmed"] is True
    assert shape["repository_delivery_rt1"] == 0
