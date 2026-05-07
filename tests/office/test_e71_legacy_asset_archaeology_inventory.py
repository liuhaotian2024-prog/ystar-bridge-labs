import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "operations/external_validation" / name).read_text())


def test_e71_archaeology_inventory_recovers_required_legacy_sources():
    data = load_artifact("e71_legacy_asset_archaeology_inventory.json")
    assert data["asset_count"] >= 60
    assert data["cluster_count"] >= 10
    assert data["E62_repository_archaeology_asset_count"] == 240
    clusters = {row["cluster_id"] for row in data["clusters"]}
    assert "e24_ecosystem_commercial_imagination_cluster" in clusters
    assert "e10_e23_commercial_revenue_runtime_cluster" in clusters
    assert "k9_cieu_hash_chain_spec_cluster" in clusters
    assert "gov_mcp_provider_promotion_gate_cluster" in clusters
    assert data["read_only_repos_mutated"] is False
    assert data["external_action_allowed"] is False

