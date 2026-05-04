from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e16c0_czl_closure_records_no_external_action_and_rt0() -> None:
    text = (ROOT / "reports/integration/e16c0_czl_closure.md").read_text()
    assert "Y*: E16C0 revised one-action send-gated pilot dry-run only." in text
    assert "Rt+1: 0" in text
    assert "external_action_executed: false" in text
    assert "dry_run_receipt_id:" in text
