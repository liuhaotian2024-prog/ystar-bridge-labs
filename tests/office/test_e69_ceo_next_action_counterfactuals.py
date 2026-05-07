import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_counterfactuals_cover_owner_rejection_and_ev4_limits():
    data = json.loads((ROOT / "operations/external_validation/e69_ceo_next_action_counterfactuals.json").read_text())
    questions = [item["question"] for item in data["counterfactuals"]]
    assert len(questions) >= 10
    assert "What if owner does not approve external action?" in questions
    assert "What if public evidence remains only EV4?" in questions
    assert data["external_action_allowed"] is False

