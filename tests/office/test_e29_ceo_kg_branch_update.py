import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_kg_branch_delta_is_working_strategy_evidence_only():
    feedback = json.loads((ROOT / "operations/knowledge_graph/e29_ceo_kg_branch_selection_feedback.json").read_text())
    nodes = (ROOT / "operations/knowledge_graph/e29_ceo_kg_nodes_delta.jsonl").read_text().strip().splitlines()
    edges = (ROOT / "operations/knowledge_graph/e29_ceo_kg_edges_delta.jsonl").read_text().strip().splitlines()
    assert feedback["kg_delta_node_count"] == len(nodes)
    assert feedback["kg_delta_edge_count"] == len(edges)
    assert feedback["customer_feedback_claimed"] is False
    assert feedback["market_validation_claimed"] is False
    assert any(json.loads(line)["relationship"] == "scoped_to" for line in edges)
