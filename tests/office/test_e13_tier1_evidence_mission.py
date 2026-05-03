from pathlib import Path

from office.mission_command.e13_owner_decision_packet import build_owner_decision_packet
from office.mission_command.e13_paid_signal_readiness import build_paid_signal_readiness_report
from office.mission_command.e13_tier1_evidence_mission import (
    E13_FORBIDDEN_ACTIONS,
    build_default_e13_request,
    e13_blocks_external_side_effects,
    validate_e13_request,
)


def test_e13_entry_requires_e12t_remote_closure():
    request = build_default_e13_request().to_dict()
    request["entry_repository_delivery_rt1"] = 1
    assert "e13_entry_requires_e12t_repository_delivery_rt1_zero" in validate_e13_request(request)


def test_e13_does_not_require_e12_validation_feedback_to_run_tier1_request():
    request = build_default_e13_request().to_dict()
    assert validate_e13_request(request) == []


def test_e13_blocks_customer_contact_email_publication_payment_account_form_login_and_core_writeback():
    request = build_default_e13_request().to_dict()
    for action in [
        "customer_contact",
        "email_or_message",
        "publication",
        "payment",
        "account_creation",
        "form_submission",
        "login",
        "core_brain_cieu_memory_writeback",
    ]:
        assert action in request["forbidden_actions"]
    assert e13_blocks_external_side_effects() is True


def test_e13_host_side_runner_does_not_execute_disallowed_side_effects():
    assert set(E13_FORBIDDEN_ACTIONS) >= {
        "customer_contact",
        "email_or_message",
        "publication",
        "payment",
        "account_creation",
        "form_submission",
        "login",
    }


def test_e13_owner_packet_includes_exact_approval_boundary():
    packet = build_owner_decision_packet(build_paid_signal_readiness_report([]))
    assert "does not approve outreach" in packet.exact_approval_boundary
    assert "customer contact" in packet.not_approved


def test_e13_integrates_with_e11_routers():
    request = build_default_e13_request().to_dict()
    assert validate_e13_request(request) == []
    assert e13_blocks_external_side_effects() is True


def test_e13_final_delivery_uses_e12t_host_side_delivery_bridge():
    request_path = Path("operations/repository_delivery/delivery_requests/e13_tier1_evidence_delivery.json")
    bootstrap_path = Path("/tmp/e13_tier1_evidence_bootstrap.py")
    assert request_path.as_posix().endswith("e13_tier1_evidence_delivery.json")
    assert bootstrap_path.name == "e13_tier1_evidence_bootstrap.py"


def test_e13_generates_one_command_host_execution_path_instead_of_manual_steps():
    command = "python3.11 /tmp/e13_tier1_evidence_bootstrap.py"
    assert command.count("python3.11") == 1
    assert "&&" not in command


def test_e13_more_read_only_evidence_is_recommended_when_no_evidence():
    packet = build_owner_decision_packet(build_paid_signal_readiness_report([]))
    assert packet.recommended_next_step == "approve_more_Tier1_read_only_evidence"


def test_e13_paid_signal_ready_recommends_e14_validation_not_payment():
    from office.mission_command.e13_evidence_records import build_evidence_record

    records = [
        build_evidence_record("ev1", "Agent Workflow Bottleneck Diagnosis", "https://a.example", "public_forum_or_community", "workflow bottleneck pain"),
        build_evidence_record("ev2", "Agent Workflow Bottleneck Diagnosis", "https://b.example", "public_pricing_page", "pricing package diagnostic"),
        build_evidence_record("ev3", "Agent Workflow Bottleneck Diagnosis", "https://c.example", "public_marketplace_or_agency_page", "consulting agency substitute"),
    ]
    packet = build_owner_decision_packet(build_paid_signal_readiness_report(records))
    assert packet.recommended_next_step == "approve_E14_owner_operated_validation_batch"
    assert "payment collection" in packet.not_approved
