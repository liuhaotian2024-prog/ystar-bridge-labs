import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_policy_requires_public_observation_before_contact_when_appropriate():
    data = json.loads((ROOT / "operations/external_validation/e31_future_real_world_behavior_policy.json").read_text())
    text = " ".join(data["future_policy"]).lower()
    assert "read-only public observation" in text
    assert "never fake evidence" in text
    assert "never convert public observation into customer feedback" in text
