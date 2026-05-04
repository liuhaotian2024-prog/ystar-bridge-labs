import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_kg_feedback_is_internal_readiness_only():
    d = json.loads((ROOT / "operations/knowledge_graph/e27_ceo_kg_live_test_feedback.json").read_text())
    assert d["kg_delta_node_count"] == 9
    assert d["kg_delta_edge_count"] == 10
    assert d["internal_readiness_evidence_only"] is True
    assert d["customer_feedback_claimed"] is False
    assert d["market_validation_claimed"] is False
    assert d["production_live_readiness_promoted"] is False
