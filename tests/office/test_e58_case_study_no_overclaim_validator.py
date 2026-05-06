from pathlib import Path

from office.mission_command.e58_case_study_boundary import PRODUCT_DIR, write_case_study_product
from office.mission_command.e58_case_study_no_overclaim_validator import run_case_study_no_overclaim_validation
from office.mission_command.e58_external_intelligence_gap import write_external_intelligence_gap


def test_case_study_no_overclaim_validator_passes_valid_packet():
    data = run_case_study_no_overclaim_validation()
    assert data["passes"] is True
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["real_mcp_transport_claimed"] is False
    assert data["external_intelligence_L5_claimed_complete"] is False


def test_case_study_no_overclaim_validator_rejects_forbidden_claim(tmp_path: Path):
    write_case_study_product(tmp_path)
    write_external_intelligence_gap(tmp_path)
    bad = tmp_path / PRODUCT_DIR / "bad_claim.md"
    bad.write_text("This is customer validated and market proven.\n", encoding="utf-8")
    data = run_case_study_no_overclaim_validation(tmp_path)
    assert data["passes"] is False
    assert data["forbidden_positive_claim_failures"]

