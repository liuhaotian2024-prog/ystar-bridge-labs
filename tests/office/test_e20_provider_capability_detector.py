import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_provider_capability_detects_no_send_dry_run_only():
    data = json.loads((ROOT / "operations/external_validation/e20_provider_capability_detection.json").read_text())
    assert data["no_send_adapter_only"] is True
    assert data["dry_run_adapter_only"] is True
    assert data["live_provider_adapter_present"] is False
    assert data["provider_tests_present"] is True
    assert data["provider_capability_status"] == "no_send_and_dry_run_only_provider_capability_missing_for_live_send"
    assert data["external_action_executed"] is False
