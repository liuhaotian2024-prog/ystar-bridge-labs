import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_kg_updated_with_public_observation_only():
    data = json.loads((ROOT / "operations/knowledge_graph/e31_ceo_kg_real_world_observation_feedback.json").read_text())
    assert data["kg_delta_nodes"] == 58
    assert data["kg_delta_edges"] == 57
    assert data["public_observation_sources"] == 8
    assert data["customer_feedback_claimed"] is False
    assert data["paid_signal_claimed"] is False
