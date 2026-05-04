from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_gov_mcp_outbound_promotion_plan.json").read_text())


def test_e16x_gov_mcp_plan_says_adapter_is_not_confirmed() -> None:
    data = load()
    assert data["gov_mcp_currently_implements_outbound_provider_adapter"] is False
    assert "No canonical live outbound email/message/publication/account/form provider adapter was confirmed by the static scan." in data["current_limitations"]


def test_e16x_gov_mcp_plan_lists_promotion_pr_scope() -> None:
    data = load()
    assert any("outbound preflight" in item for item in data["minimal_gov_mcp_pr_before_real_e16c_send"])
    assert any("no real send" in item for item in data["minimal_gov_mcp_pr_before_real_e16c_send"])
    assert "offer and target selection" in data["bridge_labs_should_continue_to_own"]
