from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _closure() -> str:
    return (REPORTS / "e11_czl_closure_report.md").read_text(encoding="utf-8")


def test_e11_czl_closure_complete_router_ready():
    text = _closure()
    assert "status: complete_global_runtime_coherence_router_ready" in text
    assert "feasible_internal_rt1 = 0" in text
    assert "full_mission_rt1 = 0" in text


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

