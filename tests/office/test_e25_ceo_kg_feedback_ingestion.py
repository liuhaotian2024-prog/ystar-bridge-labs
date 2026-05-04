import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read_jsonl(rel):
    return [json.loads(line) for line in (ROOT / rel).read_text().splitlines() if line.strip()]

def test_e25_ceo_kg_feedback_ingests_internal_sandbox_evidence_only():
    data = json.loads((ROOT / "operations/knowledge_graph/e25_ceo_kg_feedback_ingestion.json").read_text())
    nodes = read_jsonl("operations/knowledge_graph/e25_ceo_kg_nodes_delta.jsonl")
    edges = read_jsonl("operations/knowledge_graph/e25_ceo_kg_edges_delta.jsonl")
    assert data["kg_delta_node_count"] == len(nodes) >= 7
    assert data["kg_delta_edge_count"] == len(edges) >= 8
    assert any(n["type"] == "SandboxExecution" for n in nodes)
    assert data["customer_or_market_truth_claimed"] is False
