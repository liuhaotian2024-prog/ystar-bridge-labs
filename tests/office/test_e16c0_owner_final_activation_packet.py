from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def packet() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16c0_owner_final_activation_packet.json").read_text())


def test_owner_packet_is_request_not_approval() -> None:
    data = packet()
    assert data["status"] == "owner_review_required"
    assert data["owner_activation_present"] is False
    assert data["send_allowed_now"] is False
    assert data["external_action_executed"] is False


def test_owner_packet_keeps_e16c1_blocked_until_required_conditions() -> None:
    required = set(packet()["e16c1_blocked_until"])
    assert "explicit owner activation" in required
    assert "real provider adapter implementation" in required
    assert "provider tests" in required
    assert "safety tests" in required
    assert "bridge delivery closure" in required
