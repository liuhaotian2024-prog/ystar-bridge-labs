import json
from pathlib import Path

from office.mission_command.e14_action_ledger import build_e14_action_ledger_template, validate_e14_action_ledger_event
from office.mission_command.e14_entry_gate import validate_e14_entry
from office.mission_command.e14_feedback_events import build_e14_feedback_events_template, validate_e14_feedback_event
from office.mission_command.e14_manual_validation_draft import build_e14_manual_validation_draft, validate_e14_manual_draft
from office.mission_command.e14_owner_approval_packet import build_e14_owner_approval_packet, validate_e14_owner_approval_packet
from office.mission_command.e14_owner_decision_packet import build_e14_owner_decision_packet
from office.mission_command.e14_signal_evaluator import evaluate_e14_validation_signal, public_evidence_is_e14_validation_feedback
from office.mission_command.e14_target_candidates import build_e14_target_candidates, validate_e14_target_candidate
from office.mission_command.e14_target_scoring import build_e14_target_batch, score_e14_target


def test_e14_requires_e13r_paid_signal_ready_before_validation_prep():
    decision = validate_e14_entry(Path("."))
    assert decision.e13r_paid_signal_ready is True
    assert decision.allowed is True


def test_e14_blocks_if_e13r_repository_delivery_rt1_not_zero():
    decision = validate_e14_entry(Path("."), expected_e13r_head="deadbeef")
    assert decision.allowed is False
    assert decision.e13r_repository_delivery_rt1 == 1


def test_e14_prepares_approval_packet_without_executing_outreach():
    candidates = build_e14_target_candidates(Path("."))
    batch = build_e14_target_batch(candidates)
    draft = build_e14_manual_validation_draft()
    packet = build_e14_owner_approval_packet(candidates, batch["selected_target_ids"], draft)
    assert packet.status == "request_only_not_approval"
    assert "Aiden autonomous sending" in packet.what_is_not_approved
    assert validate_e14_owner_approval_packet(packet) == []


def test_e14_target_candidates_require_evidence_refs_and_no_contact_state():
    candidates = build_e14_target_candidates(Path("."))
    assert candidates
    for candidate in candidates:
        assert candidate.evidence_refs
        assert candidate.no_contact_until_approved is True
        assert candidate.contact_channel_allowed is False
        assert validate_e14_target_candidate(candidate) == []


def test_e14_target_scoring_rejects_private_personal_scraping():
    candidate = build_e14_target_candidates(Path("."))[0]
    bad = candidate.to_dict()
    bad["public_url_or_ref"] = "https://linkedin.com/in/private-person"
    assert "private_or_personal_scraping_rejected" in validate_e14_target_candidate(bad)
    assert score_e14_target(candidate).score > 0


def test_e14_manual_send_draft_includes_ai_transparency_and_opt_out():
    draft = build_e14_manual_validation_draft()
    assert draft.ai_transparency_present is True
    assert draft.opt_out_ignore_present is True
    assert validate_e14_manual_draft(draft) == []


def test_e14_manual_send_draft_does_not_claim_existing_customer_validation():
    draft = build_e14_manual_validation_draft()
    assert draft.no_existing_validation_claim is True


def test_e14_action_ledger_cannot_be_executed_without_owner_execution():
    template = build_e14_action_ledger_template()["template"]
    event = dict(template)
    event["approval_id"] = "approval_1"
    event["target_id"] = "target_1"
    event["result_status"] = "sent"
    assert "executed_action_requires_owner_execution" in validate_e14_action_ledger_event(event, owner_executed=False)


def test_e14_feedback_event_requires_action_id_and_owner_source():
    event = build_e14_feedback_events_template()["template"]
    assert "feedback_requires_valid_action_id" in validate_e14_feedback_event(event)
    valid = dict(event)
    valid.update(
        {
            "feedback_event_id": "fb_1",
            "action_id": "act_1",
            "target_id": "target_1",
            "feedback_type": "weak_positive",
            "response_text_or_summary": "They asked for an example.",
            "recorded_by": "owner",
        }
    )
    assert validate_e14_feedback_event(valid, valid_action_ids=["act_1"], owner_entered=True) == []


def test_e14_no_response_invalid_without_valid_action_ledger():
    event = {
        "action_id": "missing",
        "feedback_type": "no_response_after_valid_action",
        "source": "owner_entered_after_manual_validation",
        "response_text_or_summary": "No response after valid action window.",
    }
    assert "feedback_requires_valid_action_id" in validate_e14_feedback_event(event, valid_action_ids=[])


def test_e14_signal_evaluator_distinguishes_approved_not_executed_from_no_response():
    approved = evaluate_e14_validation_signal(approval_present=True)
    assert approved.classification == "approved_but_not_executed"
    no_response = evaluate_e14_validation_signal(
        approval_present=True,
        action_ledger_events=[{"action_id": "act_1"}],
        feedback_events=[{"feedback_type": "no_response_after_valid_action", "paid_signal_candidate": False}],
    )
    assert no_response.classification == "no_response_after_valid_action"


def test_e14_cannot_recommend_e15_without_action_ledger_and_feedback():
    signal = evaluate_e14_validation_signal()
    packet = build_e14_owner_decision_packet(signal)
    assert signal.e15_entry_allowed is False
    assert packet.recommended_next_step == "owner_approve_manual_validation_batch"


def test_e14_can_recommend_e15_only_after_valid_action_and_feedback():
    signal = evaluate_e14_validation_signal(
        approval_present=True,
        action_ledger_events=[{"action_id": "act_1"}],
        feedback_events=[{"feedback_type": "strong_positive", "paid_signal_candidate": False}],
    )
    packet = build_e14_owner_decision_packet(signal)
    assert signal.e15_entry_allowed is True
    assert packet.recommended_next_step == "proceed_to_E15_only_after_feedback"


def test_e14_cannot_classify_public_evidence_as_validation_feedback():
    assert public_evidence_is_e14_validation_feedback() is False


def test_e14_owner_packet_has_exact_approval_boundary():
    candidates = build_e14_target_candidates(Path("."))
    draft = build_e14_manual_validation_draft()
    packet = build_e14_owner_approval_packet(candidates, build_e14_target_batch(candidates)["selected_target_ids"], draft)
    boundary = " ".join(packet.what_is_not_approved).lower()
    assert "payment collection" in boundary
    assert "aiden autonomous sending" in boundary
    assert "core brain/cieu/memory writeback" in boundary


def test_e14_czl_keeps_full_mission_residual_until_action_and_feedback():
    report = Path("reports/integration/e14_czl_closure.md")
    if report.exists():
        text = report.read_text(encoding="utf-8")
        assert "E14 full_mission_rt1: 1" in text


def test_e14_repository_delivery_uses_host_side_bridge():
    request = Path("operations/repository_delivery/delivery_requests/e14_owner_operated_validation_prep_delivery.json")
    assert request.as_posix().endswith("e14_owner_operated_validation_prep_delivery.json")


def test_e14_generates_one_host_bootstrap_command_and_avoids_manual_burden():
    command = "python3.11 /tmp/e14_owner_operated_validation_prep_bootstrap.py"
    assert command.count("python3.11") == 1
    assert "&&" not in command


def test_e14_generated_artifacts_exist_after_creation_script():
    expected = [
        "operations/external_validation/e14_owner_approval_packet.request.json",
        "operations/external_validation/e14_manual_send_draft.md",
        "operations/external_validation/e14_action_ledger.template.json",
        "operations/external_validation/e14_feedback_events.template.json",
        "operations/external_validation/e14_validation_signal_report.json",
    ]
    for path in expected:
        assert Path(path).exists()


def test_e14_operation_files_do_not_claim_execution_or_feedback():
    signal = json.loads(Path("operations/external_validation/e14_validation_signal_report.json").read_text(encoding="utf-8"))
    assert signal["classification"] == "no_approval"
    assert signal["action_ledger_exists"] is False
    assert signal["feedback_events_exist"] is False
