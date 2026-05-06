import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_prior_constraint_diagnosis_is_honest():
    data = json.loads((ROOT / "operations/external_validation/e64_prior_revenue_path_constraint_diagnosis.json").read_text())
    assert data["E62_E63_candidate_universe_constrained_around_AI_products"] is True
    assert data["non_AI_service_business_paths_underexplored"] is True
    assert data["E63_selected_path_still_valid_candidate"] is True
