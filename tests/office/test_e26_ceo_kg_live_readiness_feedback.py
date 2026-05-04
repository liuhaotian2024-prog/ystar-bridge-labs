import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def rows(rel): return [json.loads(line) for line in (ROOT/rel).read_text().splitlines() if line.strip()]
def test_e26_ceo_kg_feedback_is_internal_readiness_only():
    d=json.loads((ROOT/"operations/knowledge_graph/e26_ceo_kg_live_readiness_feedback.json").read_text())
    assert d["kg_delta_node_count"]==len(rows("operations/knowledge_graph/e26_ceo_kg_nodes_delta.jsonl"))>=10
    assert d["kg_delta_edge_count"]==len(rows("operations/knowledge_graph/e26_ceo_kg_edges_delta.jsonl"))>=11
    assert d["customer_feedback_claimed"] is False
    assert d["market_validation_claimed"] is False
