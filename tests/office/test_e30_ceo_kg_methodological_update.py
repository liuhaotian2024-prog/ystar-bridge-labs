import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_kg_delta_records_action_space_and_selection_without_truth_promotion():
    feedback = json.loads((ROOT / "operations/knowledge_graph/e30_ceo_kg_methodological_action_selection.json").read_text())
    nodes = (ROOT / "operations/knowledge_graph/e30_ceo_kg_nodes_delta.jsonl").read_text().strip().splitlines()
    edges = (ROOT / "operations/knowledge_graph/e30_ceo_kg_edges_delta.jsonl").read_text().strip().splitlines()
    assert feedback["kg_delta_node_count"] == len(nodes)
    assert feedback["kg_delta_edge_count"] == len(edges)
    assert feedback["selected_route"] == "paid_readiness_review_signal_package"
    assert feedback["customer_feedback_claimed"] is False
    assert feedback["market_validation_claimed"] is False
