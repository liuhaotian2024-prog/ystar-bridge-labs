import json
from pathlib import Path

from office.mission_command.e35_ceo_methodology_quality_audit import build_ceo_methodology_quality_audit


ROOT = Path(__file__).resolve().parents[2]


def read_external(name):
    return json.loads((ROOT / "operations" / "external_validation" / f"{name}.json").read_text())


def test_methodology_quality_and_closure_flags():
    audit = build_ceo_methodology_quality_audit()
    assert audit["audit_status"] == "passed"
    assert audit["one_brain_integrated"] is True
    assert audit["expanded_beyond_agent_governance_audit_black_box"] is True
    assert audit["prepared_future_route_selection_without_selecting"] is True
    czl = read_external("e35_czl_closure")
    assert czl["second_ceo_brain_created"] is False
    assert czl["customer_contact_occurred"] is False
    assert czl["message_sent"] is False
    assert czl["published_externally"] is False
    assert czl["provider_api_called"] is False
    assert czl["payment_occurred"] is False
    assert czl["customer_validation_claimed"] is False
    assert czl["paid_signal_claimed"] is False
