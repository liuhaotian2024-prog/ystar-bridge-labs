from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_router_consolidation_plan.json").read_text())


def test_e16x_router_plan_keeps_risk_model_and_upgrades_router() -> None:
    data = load()
    assert data["canonical_now"]["risk_tier_source"] == "office/mission_command/e8_risk_controlled_action_model.py"
    assert data["canonical_now"]["bridge_runtime_router"] == "office/mission_command/action_authorization_router.py"
    answers = " ".join(item["answer"] for item in data["decisions"])
    assert "should understand capability_domain" in answers
    assert "E15D policy" in answers


def test_e16x_router_plan_requires_pre_e16c0_tests() -> None:
    tests = load()["tests_required_before_e16c0"]
    assert any("Level 5 maps to Tier 2" in item for item in tests)
    assert any("owner approval state machine" in item for item in tests)
