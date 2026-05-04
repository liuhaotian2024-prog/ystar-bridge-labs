import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_future_policy_blocks_menu_driven_milestones():
    data = json.loads((ROOT / "operations/external_validation/e30_future_methodological_action_policy.json").read_text())
    assert "open action-space generation" in data["required_method_steps"]
    assert "production live configuration is next" in data["must_not_assume"]
    assert data["owner_manual_send_default_allowed"] is False
