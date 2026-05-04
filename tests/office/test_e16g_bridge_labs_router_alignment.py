from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16g_bridge_labs_router_alignment.json").read_text())


def test_e16g_alignment_does_not_duplicate_runtime_implementation() -> None:
    data = load()
    assert data["bridge_labs_runtime_changes"].startswith("no core runtime behavior changed")
    assert data["real_e16c0_allowed_now"] is False
    assert any("gov-mcp adapter contract" in rule for rule in data["router_alignment_rules"])


def test_e16g_alignment_keeps_router_and_risk_tier_boundaries() -> None:
    rules = " ".join(load()["router_alignment_rules"])
    assert "action_authorization_router remains" in rules
    assert "E8 risk tiers remain canonical" in rules
    assert "B2R capability levels remain capability maturity" in rules
