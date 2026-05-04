import json
from pathlib import Path

from office.mission_command.e21_provider_capability_sync import build_provider_capability_sync

ROOT = Path(__file__).resolve().parents[2]


def test_provider_capability_sync_reports_disabled_live_scaffold():
    data = json.loads((ROOT / "operations/external_validation/e21_provider_capability_sync.json").read_text())
    assert data["no_send_available"] is True
    assert data["dry_run_available"] is True
    assert data["live_scaffold_available"] is True
    assert data["live_provider_enabled"] is False
    assert data["capability_status"] == "live_provider_scaffolded_but_disabled"
    assert data["external_action_executed"] is False


def test_provider_capability_sync_does_not_recast_provider_gap_as_owner_manual():
    sync = build_provider_capability_sync({
        "provider_id": "x",
        "provider_mode": "live_disabled",
        "no_send_available": True,
        "dry_run_available": True,
        "live_scaffold_available": True,
        "live_provider_enabled": False,
        "live_execution_blocked_reason": "live_provider_scaffolded_but_disabled",
        "dry_run_and_live_receipts_distinct": True,
    })
    assert "live-capability blocker" in sync["policy_note"]
