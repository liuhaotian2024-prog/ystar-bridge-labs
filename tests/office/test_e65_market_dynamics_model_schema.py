import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_market_dynamics_schema_is_full_dimensional():
    data = json.loads((ROOT / "operations/external_validation/e65_market_dynamics_model_schema.json").read_text())
    sections = data["schema_sections"]
    for key in [
        "market_domain",
        "value_chain",
        "competitive_landscape",
        "business_model",
        "YBridge_fit",
        "evidence_state",
        "risk_and_constraints",
        "dynamic_update_triggers",
    ]:
        assert key in sections
    assert data["model_name"] == "CEO Market Dynamics Intelligence Model v1"
