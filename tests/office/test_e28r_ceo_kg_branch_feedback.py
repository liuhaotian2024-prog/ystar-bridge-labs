import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_kg_delta_has_branch_nodes_and_no_market_truth():
    d = json.loads((ROOT / "operations/knowledge_graph/e28r_ceo_kg_branch_feedback.json").read_text())
    assert d["branch_count"] == 10
    assert d["kg_delta_node_count"] == 60
    assert d["kg_delta_edge_count"] == 52
    assert d["production_live_configuration_global_default"] is False
    assert d["customer_feedback_claimed"] is False
    assert d["market_validation_claimed"] is False
