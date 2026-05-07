import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_ladder_distinguishes_non_contact_from_human_and_paid_validation():
    data = json.loads((ROOT / "operations/external_validation/e67_external_validation_ladder.json").read_text())
    levels = {row["EV_level"]: row for row in data["levels"]}
    assert len(levels) == 9
    assert data["external_validation_is_not_only_human_feedback"] is True
    assert "EV4_public_demand_or_behavior_proxy" in data["non_contact_levels_available_now"]
    assert "EV6_owner_approved_human_feedback" in data["customer_validation_levels"]
    assert "EV7_paid_signal" in data["paid_validation_levels"]
    assert levels["EV5_owner_approved_public_experiment"]["achieved_in_E67"] is False

