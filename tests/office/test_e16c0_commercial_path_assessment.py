from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def assessment() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16c0_commercial_path_assessment.json").read_text())


def test_commercial_assessment_uses_paid_signal_ready_offer() -> None:
    data = assessment()
    assert data["offer"] == "48h AI Agent Implementation Readiness Review"
    assert data["paid_signal_classification"] == "paid_signal_ready"
    assert data["top_revised_offer_id"] == "ai_agent_implementation_readiness_review"
    assert data["e14_entry_allowed"] is True
    assert data["shortest_cash_path_candidate"] is True


def test_commercial_route_keeps_dry_run_distinct_from_revenue() -> None:
    data = assessment()
    assert data["commercial_route_recommendation"] == "E16B_owner_manual_send_first"
    assert "Dry-run is not revenue" in data["paid_signal_readiness_advancement"]
    assert data["external_action_executed"] is False
