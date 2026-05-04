import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_owner_action_model_has_required_choices_and_safe_defaults():
    data = json.loads((ROOT / "operations/external_validation/e19_owner_action_model.json").read_text())
    actions = {item["action"] for item in data["actions"]}
    for action in ["approve_manual_send_for_candidate", "import_feedback", "suppress_candidate", "prepare_provider_adapter_plan", "keep_real_provider_send_blocked"]:
        assert action in actions
    provider = next(item for item in data["actions"] if item["action"] == "prepare_provider_adapter_plan")
    assert "real send" in provider["forbidden_preconditions"]
    assert data["external_action_executed"] is False
