import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_frontier_world_model_preserves_evidence_boundaries():
    data = json.loads((ROOT / "operations/external_validation/e32_frontier_world_model.json").read_text())
    assert data["primary_world_fracture"] == "agent_action_legitimacy_gap"
    assert "authorized" in data["institutional_void"]
    assert data["evidence_boundaries"]["unsupported_do_not_use"]
