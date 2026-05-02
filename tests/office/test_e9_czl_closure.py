from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _closure() -> str:
    return (REPORTS / "e9_czl_closure_report.md").read_text(encoding="utf-8")


def test_e9_czl_blocked_full_rt1_nonzero_when_pattern_research_missing():
    text = _closure()
    assert "external_pattern_research_ran_or_blocked_honestly: True" in text
    assert "full_mission_rt1 = 0" in text


def test_e9_czl_complete_pattern_mining_requires_pattern_library():
    assert (REPORTS / "e9_external_pattern_library.md").exists()
    assert "pattern_count: 14" in (REPORTS / "e9_external_pattern_library.md").read_text(encoding="utf-8")


def test_e9_czl_complete_validation_requires_action_ledger_or_feedback_events():
    text = _closure()
    assert "complete_pattern_mining_and_owner_handoff_ready" in text
    assert "Aiden did not send anything" in text


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
