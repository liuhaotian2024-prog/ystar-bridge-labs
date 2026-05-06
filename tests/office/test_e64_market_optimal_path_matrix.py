import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_market_optimal_matrix_answers_fast_cash_axis():
    data = json.loads((ROOT / "operations/external_validation/e64_market_optimal_path_matrix.json").read_text())
    assert data["best_market_optimal_path"] == "founder_operator_decision_brief_service"
    first = data["matrix"][0]
    assert first["decision"] == "best_market_optimal"
    assert first["strategic_uniqueness_not_dominant"] is True
