from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _closure() -> str:
    return (REPORTS / "e8_czl_closure_report.md").read_text(encoding="utf-8")


def test_e8_czl_complete_control_plane_ready_requires_all_control_artifacts():
    required = [
        "e8_risk_control_model.md",
        "e8_ai_transparency_policy.md",
        "e8_external_validation_manifest_request.md",
        "e8_target_seed_request.md",
        "e8_frozen_validation_drafts.md",
        "e8_external_action_preflight.md",
        "e8_execution_gate_report.md",
        "e8_feedback_capture_report.md",
        "e8_validation_signal_evaluation.md",
        "e8_validation_result_summary.md",
        "e8_residual_learning_update.md",
        "e8_owner_decision_packet.md",
        "e8_czl_closure_report.md",
    ]
    for name in required:
        assert (REPORTS / name).exists(), name
    assert "status: complete_control_plane_ready" in _closure()


def test_e8_czl_complete_external_validation_requires_action_ledger():
    text = _closure()
    assert "complete_external_validation_executed" not in text
    assert "external_action_executed: True" not in text


def test_no_unapproved_external_sending_customer_contact_email_publication():
    text = _closure()
    assert "unapproved external sending: false" in text
    assert "unapproved customer contact: false" in text
    assert "unapproved email/message: false" in text
    assert "unapproved publication: false" in text


def test_no_payment_account_form_core_writeback_obligation_cieu_or_coo():
    text = _closure()
    assert "payment: false" in text
    assert "account creation: false" in text
    assert "form submission: false" in text
    assert "core DB/brain/memory/CIEU writeback: false" in text
    assert "obligation auto-registration: false" in text
    assert "COO invented: false" in text
