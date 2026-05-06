import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_ybridge_unique_matrix_answers_defensibility_axis():
    data = json.loads((ROOT / "operations/external_validation/e64_ybridge_unique_path_matrix.json").read_text())
    assert data["best_YBridge_unique_path"] == "governed_business_operations_blueprint_for_agent_teams"
    first = data["matrix"][0]
    assert first["fast_cash_not_dominant"] is True
    assert first["YBridge_unique_score"] >= 82
