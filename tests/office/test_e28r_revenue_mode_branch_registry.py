import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_branch_registry_contains_required_revenue_modes():
    d = json.loads((ROOT / "operations/external_validation/e28r_revenue_mode_branch_registry.json").read_text())
    ids = {b["branch_id"] for b in d["branches"]}
    required = {
        "revenue_mode_shortest_cash_path",
        "revenue_mode_strategic_compounding",
        "revenue_mode_platform_productization",
        "revenue_mode_enterprise_pilot",
        "revenue_mode_partner_channel",
        "revenue_mode_developer_tooling",
        "revenue_mode_governance_infrastructure",
        "revenue_mode_ceo_agent_runtime_product",
        "revenue_mode_service_cashflow",
        "revenue_mode_internal_capability_before_market",
    }
    assert required <= ids
    assert d["branch_count"] == 10
    assert d["production_live_provider_global_default"] is False
    assert d["outbound_global_default"] is False
