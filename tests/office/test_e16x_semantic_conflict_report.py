from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_semantic_conflict_report.json").read_text())


def test_e16x_semantic_conflicts_include_required_categories() -> None:
    conflict_ids = {item["conflict_id"] for item in load()["conflicts"]}
    assert {
        "risk_tier_vs_capability_level",
        "execution_mode_enum",
        "owner_approval_state_machine",
        "feedback_semantics",
        "gov_mcp_boundary",
    } <= conflict_ids


def test_e16x_conflict_report_blocks_real_e16c0_now() -> None:
    data = load()
    assert data["real_e16c0_should_proceed_now"] is False
    assert data["unresolved_conflict_count"] >= 3
    risk_conflict = next(item for item in data["conflicts"] if item["conflict_id"] == "risk_tier_vs_capability_level")
    assert "TIER_2" in risk_conflict["canonical_resolution"]
