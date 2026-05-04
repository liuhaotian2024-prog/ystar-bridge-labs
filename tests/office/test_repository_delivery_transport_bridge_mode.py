from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_transport import classify_direct_delivery_mode


def test_bridge_mode_is_used_when_direct_push_unavailable_but_bridge_available() -> None:
    facts = {
        "transport_classification": "direct_push_blocked_by_network",
        "host_local_bridge": {"available": True},
    }
    assert classify_direct_delivery_mode(facts) == "host_local_bridge_available"


def test_no_channel_when_neither_direct_nor_bridge_available() -> None:
    facts = {
        "transport_classification": "direct_push_blocked_by_network",
        "host_local_bridge": {"available": False, "root_exists": False},
    }
    assert classify_direct_delivery_mode(facts) == "blocked_no_delivery_channel"

