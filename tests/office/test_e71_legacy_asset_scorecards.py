import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_scorecards_rank_k9_cieu_and_keep_owner_gated_assets_gated():
    data = json.loads((ROOT / "operations/external_validation/e71_legacy_asset_scorecards.json").read_text())
    rows = data["cluster_scorecards"]
    by_id = {row["cluster_id"]: row for row in rows}
    assert data["top_cluster"] == "k9_cieu_hash_chain_spec_cluster"
    assert by_id["k9_cieu_hash_chain_spec_cluster"]["priority_band"] == "P0_resurrect_now"
    assert by_id["e24_ecosystem_commercial_imagination_cluster"]["priority_band"] == "P0_resurrect_now"
    assert by_id["e10_e23_commercial_revenue_runtime_cluster"]["priority_band"] == "P0_resurrect_now"
    assert by_id["finance_pricing_package_cluster"]["priority_band"] == "P1_bind_as_input"
    assert by_id["gov_mcp_provider_promotion_gate_cluster"]["priority_band"] == "P3_defer_pending_owner_approval"
    assert by_id["marketing_launch_skill_marketplace_cluster"]["priority_band"] == "P3_defer_pending_owner_approval"
    assert by_id["ystar_company_historical_sales_brain_cluster"]["priority_band"] == "Q_quarantine_stale_or_risky"

