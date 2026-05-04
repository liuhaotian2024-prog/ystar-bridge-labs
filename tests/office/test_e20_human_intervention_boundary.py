import json
from pathlib import Path

from office.mission_command.e20_human_intervention_boundary import requires_human_intervention

ROOT = Path(__file__).resolve().parents[2]


def test_human_intervention_boundary_requires_high_risk_not_sending_itself():
    data = json.loads((ROOT / "operations/external_validation/e20_human_intervention_boundary.json").read_text())
    assert "sending" in data["human_not_required_merely_because"]
    assert "payment_or_purchase" in data["human_required_conditions"]
    assert data["external_action_executed"] is False
    assert requires_human_intervention({"risk_tier": "T4_high_risk_owner_approval_required"}) is True
    assert requires_human_intervention({"risk_tier": "T2_low_medium_limited_outbound"}) is False
