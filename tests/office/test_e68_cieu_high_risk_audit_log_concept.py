import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_cieu_concept_defines_causal_tuple_and_limits():
    data = json.loads((ROOT / "operations/external_validation/e68_cieu_high_risk_audit_log_concept.json").read_text())
    fields = data["what_CIEU_records"]
    assert set(fields) == {"X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"}
    assert "not EU AI Act compliance proof" in data["does_not_claim"]
    assert data["external_action_allowed"] is False

