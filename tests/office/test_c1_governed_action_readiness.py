from __future__ import annotations

import json
from pathlib import Path

from office.mission_command.c1_action_intent_packet import (
    build_c1_action_intent_examples,
    validate_c1_action_intent_packet,
)
from office.mission_command.c1_action_ledger import build_c1_action_ledger_template, validate_c1_action_ledger_event
from office.mission_command.c1_constitutional_envelope import (
    build_c1_constitutional_envelope_request,
    validate_c1_constitutional_envelope,
)
from office.mission_command.c1_feedback_events import build_c1_feedback_event_template, validate_c1_feedback_event
from office.mission_command.c1_gov_mcp_execution_bridge import (
    build_c1_gov_mcp_execution_contract,
    validate_c1_gov_mcp_execution_contract,
)
from office.mission_command.c1_readiness_report import build_c1_readiness_report
from office.mission_command.c1_signal_evaluator import evaluate_c1_signal
from office.mission_command.c1_y_gov_decision_bridge import evaluate_y_gov_decision


ROOT = Path(__file__).resolve().parents[2]


def test_c1_constitutional_envelope_request_has_required_boundary() -> None:
    envelope = build_c1_constitutional_envelope_request()
    assert validate_c1_constitutional_envelope(envelope) == []
    data = envelope.to_dict()
    assert data["validity_days"] == 7
    assert data["max_total_actions"] == 3
    assert data["max_actions_per_day"] == 1
    assert data["owner_role"] == "constitutional_boundary_setter_not_operator"
    assert data["live_execution_approved"] is False


def test_c1_envelope_hard_gates_payment_contract_legal_customer_system_core_writeback() -> None:
    gates = set(build_c1_constitutional_envelope_request().hard_owner_gates)
    for gate in [
        "payment",
        "contract",
        "legal_obligation",
        "financial_commitment",
        "customer_system_access",
        "core_brain_cieu_memory_writeback",
    ]:
        assert gate in gates


def test_c1_action_intent_examples_include_three_paths() -> None:
    packets = build_c1_action_intent_examples()
    domains = {packet.capability_domain for packet in packets}
    assert {"external_validation_message", "low_risk_form_submission", "publication_draft"} <= domains
    assert all(validate_c1_action_intent_packet(packet) == [] for packet in packets)


def test_c1_action_packets_include_y_gov_and_gov_mcp_expectations() -> None:
    packet = build_c1_action_intent_examples()[0]
    assert "Y*gov" in packet.y_gov_validation_expectation
    assert "gov-mcp" in packet.gov_mcp_execution_expectation
    assert packet.live_execution_in_this_milestone is False


def test_c1_y_gov_decision_allows_readiness_with_valid_envelope() -> None:
    envelope = build_c1_constitutional_envelope_request().to_dict()
    packet = build_c1_action_intent_examples()[0].to_dict()
    decision = evaluate_y_gov_decision(packet, envelope)
    assert decision.allowed is True
    assert decision.executes_action is False


def test_c1_y_gov_decision_denies_without_envelope() -> None:
    packet = build_c1_action_intent_examples()[0].to_dict()
    assert evaluate_y_gov_decision(packet, None).reason_code == "blocked_no_envelope"


def test_c1_y_gov_decision_escalates_hard_gate_packet() -> None:
    envelope = build_c1_constitutional_envelope_request().to_dict()
    packet = build_c1_action_intent_examples()[0].to_dict()
    packet["proposed_u"] = "Make a payment for a vendor."
    decision = evaluate_y_gov_decision(packet, envelope)
    assert decision.escalated is True
    assert decision.reason_code == "owner_hard_gate"


def test_c1_gov_mcp_execution_contract_has_required_fields() -> None:
    contract = build_c1_gov_mcp_execution_contract()
    assert validate_c1_gov_mcp_execution_contract(contract) == []
    assert "allow" in contract.decision_modes
    assert "deny" in contract.decision_modes
    assert "escalate" in contract.decision_modes
    assert contract.no_secret_printing is True
    assert contract.no_credential_disclosure is True


def test_c1_action_ledger_template_and_validation() -> None:
    template = build_c1_action_ledger_template()["template"]
    assert "action_id" in template
    assert "y_gov_decision_id" in template
    assert "gov_mcp_receipt_id" in template
    assert "residual_candidate" in template
    assert validate_c1_action_ledger_event(template)
    valid = dict(template)
    valid.update(
        {
            "action_id": "act_1",
            "y_gov_decision_id": "ygov_1",
            "gov_mcp_receipt_id": "receipt_1",
            "target_id_or_class": "ai_consultant_agency",
            "channel": "governed_adapter",
            "executed_at": "2026-05-03T00:00:00Z",
            "result": "sent",
        }
    )
    assert validate_c1_action_ledger_event(valid) == []


def test_c1_feedback_event_template_and_validation() -> None:
    template = build_c1_feedback_event_template()["template"]
    assert "buyer_pain" in template
    assert "urgency" in template
    assert "budget" in template
    assert "paid_signal_candidate" in template
    assert validate_c1_feedback_event(template)
    valid = dict(template)
    valid.update(
        {
            "feedback_event_id": "fb_1",
            "action_id": "act_1",
            "feedback_source": "reply",
            "feedback_type": "asks_price",
            "recorded_by": "gov-mcp",
            "recorded_at": "2026-05-03T00:00:00Z",
        }
    )
    assert validate_c1_feedback_event(valid) == []


def test_c1_feedback_rejects_public_evidence_as_feedback() -> None:
    valid = {
        "feedback_event_id": "fb_1",
        "action_id": "act_1",
        "feedback_source": "public_evidence",
        "feedback_type": "interested",
        "recorded_by": "system",
        "recorded_at": "2026-05-03T00:00:00Z",
    }
    assert "public_evidence_is_not_validation_feedback" in validate_c1_feedback_event(valid)


def test_c1_signal_evaluator_classifications() -> None:
    assert evaluate_c1_signal(envelope_present=False) == "blocked_no_envelope"
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="deny") == "denied_by_Y_gov"
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="deny") == "denied_by_gov_mcp"
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="allow") == "approved_not_executed"
    assert (
        evaluate_c1_signal(
            envelope_present=True,
            y_gov_decision="allow",
            gov_mcp_decision="allow",
            action_executed=True,
        )
        == "executed_no_feedback_yet"
    )


def test_c1_signal_evaluator_positive_negative_paid_signal() -> None:
    base = {"feedback_source": "reply"}
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="allow", action_executed=True, feedback_event={**base, "feedback_type": "interested"}) == "weak_positive"
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="allow", action_executed=True, feedback_event={**base, "feedback_type": "describes_buyer_pain", "budget": "$1000"}) == "strong_positive"
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="allow", action_executed=True, feedback_event={**base, "feedback_type": "rejects_price"}) == "negative"
    assert evaluate_c1_signal(envelope_present=True, y_gov_decision="allow", gov_mcp_decision="allow", action_executed=True, feedback_event={**base, "feedback_type": "asks_price", "paid_signal_candidate": True}) == "paid_signal_candidate"


def test_c1_readiness_report_names_most_ready_action_and_blocks() -> None:
    report = build_c1_readiness_report()
    assert report["most_ready_low_risk_action"] == "external_validation_message"
    assert report["c1_real_action_cycle_allowed_now"] is False
    assert "payment" in report["still_not_allowed"]


def test_c1_operational_artifacts_exist() -> None:
    for rel in [
        "operations/external_validation/c1_owner_constitutional_envelope.request.json",
        "operations/external_validation/c1_action_intent_examples.json",
        "operations/external_validation/c1_gov_mcp_execution_contract.json",
        "operations/external_validation/c1_action_ledger.template.json",
        "operations/external_validation/c1_feedback_events.template.json",
        "operations/external_validation/c1_signal_evaluator_fixture.json",
        "operations/external_validation/c1_governed_action_readiness_report.json",
        "reports/integration/c1_governed_real_action_entry.md",
        "reports/integration/c1_y_gov_gov_mcp_action_flow.md",
        "reports/integration/c1_czl_closure.md",
    ]:
        assert (ROOT / rel).exists(), rel


def test_c1_delivery_request_uses_host_bridge() -> None:
    request = json.loads(
        (ROOT / "operations/repository_delivery/delivery_requests/ab3_c1_governed_action_readiness_delivery.json").read_text(
            encoding="utf-8"
        )
    )
    assert request["remote_confirmation_required"] is True
    assert "host_delivery_runner.py" in request["safety_boundary"]


def test_c1_does_not_execute_external_action() -> None:
    closure = json.loads(
        (ROOT / "reports/integration/c1_czl_closure.md").read_text(encoding="utf-8").split("```json\n", 1)[1].split("\n```", 1)[0]
    )
    assert all(value is False for value in closure["no_external_side_effects"].values())


def test_c1_owner_is_envelope_approver_not_operator() -> None:
    envelope = build_c1_constitutional_envelope_request()
    assert envelope.owner_role == "constitutional_boundary_setter_not_operator"
    assert envelope.status == "request_only_not_approval"
