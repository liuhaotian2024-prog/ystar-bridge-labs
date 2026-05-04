import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_learning_agenda_is_method_driven_and_multi_domain():
    data = json.loads((ROOT / "operations/external_validation/e32_ceo_learning_agenda.json").read_text())
    assert data["agenda_is_method_driven"] is True
    assert data["learning_question_count"] >= 12
    assert data["technical_questions"]
    assert data["market_questions"]
    assert data["self_questions"]
    assert data["monetization_questions"]
