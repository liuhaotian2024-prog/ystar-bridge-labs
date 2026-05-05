import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_ceo_kg_frontier_feedback_matches_delta_files_and_claims_no_validation():
    data = json.loads((ROOT / "operations/knowledge_graph/e32_ceo_kg_frontier_mvp_feedback.json").read_text())
    nodes = (ROOT / "operations/knowledge_graph/e32_ceo_kg_nodes_delta.jsonl").read_text().strip().splitlines()
    edges = (ROOT / "operations/knowledge_graph/e32_ceo_kg_edges_delta.jsonl").read_text().strip().splitlines()
    assert data["kg_delta_nodes"] == len(nodes)
    assert data["kg_delta_edges"] == len(edges)
    assert data["selected_mvp"] == "mvp_agent_action_black_box"
    assert data["customer_feedback_claimed"] is False
    assert data["market_validation_claimed"] is False
