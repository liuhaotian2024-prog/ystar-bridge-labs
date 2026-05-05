import json
from pathlib import Path

from office.mission_command.e34_ceo_imagination_to_decision_protocol import build_ceo_imagination_to_decision_protocol


ROOT = Path(__file__).resolve().parents[2]


def read_external(name):
    return json.loads((ROOT / "operations" / "external_validation" / f"{name}.json").read_text())


def test_imagination_protocol_and_closure_guardrails():
    protocol = build_ceo_imagination_to_decision_protocol()
    assert protocol["invariant_checks_count"] == 12
    assert protocol["architecture_core_vs_buyer_wedge_required"] is True
    assert protocol["evidence_vs_imagination_separation_required"] is True
    assert protocol["no_hardcoded_route_menu"] is True
    no_rebuild = read_external("e34_no_rebuild_alignment_gate")
    assert no_rebuild["gate_status"] == "passed"
    assert no_rebuild["parallel_subsystem_created"] is False
    assert no_rebuild["no_product_answer_hardcoded"] is True
    czl = read_external("e34_czl_closure")
    assert czl["customer_contact_occurred"] is False
    assert czl["message_sent"] is False
    assert czl["published_externally"] is False
    assert czl["provider_api_called"] is False
    assert czl["payment_occurred"] is False
    assert czl["customer_validation_claimed"] is False
    assert czl["paid_signal_claimed"] is False
