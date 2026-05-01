from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _closure() -> str:
    return (REPORTS / "e7_czl_closure_report.md").read_text(encoding="utf-8")


def test_e7_czl_complete_requires_all_artifacts():
    required = [
        "e7_implementation_inspection.md",
        "e7_evidence_quality_calibration.md",
        "e7_cleaned_evidence_table.md",
        "e7_validation_ready_offer_packet.md",
        "e7_validation_protocol.md",
        "e7_outreach_draft.md",
        "e7_landing_page_draft.md",
        "e7_demo_call_script.md",
        "e7_validation_survey_or_question_set.md",
        "e7_owner_decision_packet.md",
        "e7_czl_closure_report.md",
    ]
    for name in required:
        assert (REPORTS / name).exists(), name
    assert "status: complete" in _closure()


def test_e7_czl_full_rt1_zero_only_when_all_internal_validation_readiness_artifacts_exist():
    text = _closure()
    assert "feasible_internal_rt1: 0" in text
    assert "full_mission_rt1: 0" in text
    assert "validation_ready_offer_packet_created: True" in text
    assert "owner_decision_packet_created: True" in text


def test_no_external_sending_customer_contact_email_payment_publication_account_form():
    text = _closure()
    assert "external sending: false" in text
    assert "customer contact: false" in text
    assert "email/message: false" in text
    assert "payment: false" in text
    assert "publication: false" in text
    assert "account creation: false" in text
    assert "form submission: false" in text


def test_no_core_db_writeback_obligation_auto_registration_cieu_or_coo():
    text = _closure()
    assert "core DB/brain/memory/CIEU writeback: false" in text
    assert "obligation auto-registration: false" in text
    assert "COO invented: false" in text
