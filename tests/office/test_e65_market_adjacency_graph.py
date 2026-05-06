import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_market_adjacency_graph_has_clusters_and_escalation_paths():
    data = json.loads((ROOT / "operations/external_validation/e65_market_adjacency_graph.json").read_text())
    assert data["edge_count"] > 0
    clusters = data["clusters"]
    assert clusters["fast_cash_commodity_cluster"]
    assert clusters["YBridge_unique_strategic_cluster"]
    assert clusters["hybrid_wedge_cluster"]
    assert data["escalation_paths"]
