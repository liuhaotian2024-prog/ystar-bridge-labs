import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_top_priority_resurrection_set_selects_expected_clusters():
    data = json.loads((ROOT / "operations/external_validation/e71_top_priority_legacy_resurrection_set.json").read_text())
    clusters = [row["cluster_id"] for row in data["selected_clusters"]]
    assert data["selected_cluster_count"] >= 8
    assert clusters[0] == "k9_cieu_hash_chain_spec_cluster"
    assert "e24_ecosystem_commercial_imagination_cluster" in clusters
    assert "e10_e23_commercial_revenue_runtime_cluster" in clusters
    assert "finance_pricing_package_cluster" in clusters
    assert "gov_mcp_provider_promotion_gate_cluster" in clusters
    assert "marketing_launch_skill_marketplace_cluster" in clusters
    assert data["external_action_allowed"] is False

