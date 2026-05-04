from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def guards() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16c0_guard_verification.json").read_text())


def test_required_guards_are_verified() -> None:
    results = guards()["guard_results"]
    for name in [
        "global_kill_switch",
        "batch_kill_switch",
        "target_suppression",
        "do_not_contact",
        "max_actions_per_day",
        "max_actions_per_target",
        "no_followup_without_positive_signal",
        "no_send_if_idempotency_key_missing",
    ]:
        assert results[name] == "pass"


def test_guards_allow_dry_run_but_block_real_send() -> None:
    data = guards()
    assert data["dry_run_allowed"] is True
    assert data["real_send_allowed"] is False
    assert "no_send_if_envelope_not_active" in data["failed_for_real_send"]
    assert "no_send_if_owner_activation_missing" in data["failed_for_real_send"]
    assert data["external_action_executed"] is False
