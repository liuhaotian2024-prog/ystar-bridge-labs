from pathlib import Path

from office.mission_command.e5_cycle import build_e5_cycle, write_e5_reports


ROOT = Path(__file__).resolve().parents[2]


def test_e5_czl_blocked_full_rt1_nonzero_without_seeds():
    state = build_e5_cycle(ROOT)["strict_czl"]
    assert state["status"] == "BLOCKED_BY_MISSING_PUBLIC_SOURCE_SEEDS"
    assert state["feasible_internal_rt1_score"] == 0
    assert state["full_mission_rt1_score"] > 0


def test_e5_czl_complete_requires_validated_bundle():
    cycle = build_e5_cycle(ROOT)
    assert cycle["bundle"]["validated_live"] is False
    assert cycle["evaluation"]["default_is_market_backed"] is False
    assert cycle["strict_czl"]["full_mission_rt1_score"] > 0


def test_reports_written_and_contain_strict_blocked_status():
    written = write_e5_reports(ROOT)
    report = written["e5_czl_closure_report.md"].read_text(encoding="utf-8")
    assert "BLOCKED_BY_MISSING_PUBLIC_SOURCE_SEEDS" in report
    assert "full_mission_rt1" in report


def test_no_external_sending_customer_contact_email_payment_publication_or_writeback():
    cycle = build_e5_cycle(ROOT)
    text = str(cycle)
    assert cycle["external_action_executed"] is False
    assert "customer contact" in text
    assert "email/message" in text
    assert "payment" in text
    assert "publication" in text
    assert "CIEU" in text
    assert "COO" not in text
    assert cycle["strict_czl"]["status"].startswith("BLOCKED")
