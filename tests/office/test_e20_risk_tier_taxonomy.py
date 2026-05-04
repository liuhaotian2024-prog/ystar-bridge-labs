import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_risk_tier_taxonomy_contains_required_tiers_and_no_owner_manual_default():
    data = json.loads((ROOT / "operations/external_validation/e20_risk_tier_taxonomy.json").read_text())
    tiers = {item["tier"] for item in data["tiers"]}
    for tier in [
        "T0_internal_only_no_external_effect",
        "T1_low_risk_reversible_external",
        "T2_low_medium_limited_outbound",
        "T3_medium_risk_requires_strict_limits",
        "T4_high_risk_owner_approval_required",
        "T5_no_go_blocked",
    ]:
        assert tier in tiers
    assert data["owner_manual_send_is_default"] is False
    assert data["external_action_executed"] is False


def test_t2_tier_allows_agent_with_limits_not_owner_required():
    data = json.loads((ROOT / "operations/external_validation/e20_risk_tier_taxonomy.json").read_text())
    t2 = next(item for item in data["tiers"] if item["tier"] == "T2_low_medium_limited_outbound")
    assert t2["allowed_executor"] == "agent_with_limits"
    assert "suppression" in " ".join(t2["required_checks"]).lower()
