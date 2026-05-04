from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def receipt() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16c0_gov_mcp_no_send_dry_run_receipt.json").read_text())


def test_no_send_receipt_uses_gov_mcp_canonical_semantics() -> None:
    data = receipt()
    assert data["execution_mode"] == "send_gated_dry_run"
    assert data["provider_adapter_mode"] == "local_no_send"
    assert data["no_send_invariant"] is True
    assert data["send_blocked_until_owner_activation"] is True
    assert data["preflight_result"]["allowed_for_dry_run"] is True
    assert data["preflight_result"]["allowed_for_real_send"] is False


def test_no_provider_or_external_action_was_executed() -> None:
    data = receipt()
    assert data["external_action_executed"] is False
    assert data["provider_called"] is False
    assert data["external_provider_called"] is False
    assert data["real_message_sent"] is False
    assert data["network_required"] is False
    assert data["login_required"] is False
    assert data["credential_required"] is False
