import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def test_e25_selects_ceo_kg_sandbox_route_from_current_revenue_path():
    data = load("operations/external_validation/e25_ceo_kg_sandbox_route_selection.json")
    assert data["selected_revenue_path_id"] == "rev_path_readiness_review_ai_consultancies"
    assert data["sandbox_route_candidate"]["provider_mode_required"] == "sandbox_ready"
    assert data["why_not_live_now"]
    assert data["external_action_executed"] is False
