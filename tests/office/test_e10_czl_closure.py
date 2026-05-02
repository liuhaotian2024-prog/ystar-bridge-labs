from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _closure() -> str:
    return (REPORTS / "e10_czl_closure_report.md").read_text(encoding="utf-8")


def test_e10_inspection_report_exists():
    assert (REPORTS / "e10_implementation_inspection.md").exists()


def test_e10_czl_complete_requires_target_candidates_if_research_ran():
    text = _closure()
    assert "autonomous_target_discovery_research_ran_or_blocked_honestly: True" in text
    assert "target_candidate_registry_created: True" in text
    assert "cross_repo_backflow_assessment_created: True" in text
    assert "full_mission_rt1 = 0" in text


def test_e10_czl_blocked_full_rt1_nonzero_if_no_discovery_provider():
    text = _closure()
    assert "status: complete_autonomous_target_discovery_ready" in text
    assert "BLOCKED_BY_MISSING_PUBLIC_TARGET_DISCOVERY_PROVIDER" not in text


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
