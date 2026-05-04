import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_live_provider_enablement_plan_keeps_live_disabled():
    data=load("operations/external_validation/e23_live_provider_enablement_plan.json")
    assert data["live_provider_remains_disabled"] is True
    assert "disabled-live scaffold" in data["launch_stages"]
    assert "one-action low-risk live canary" in data["launch_stages"]
    assert data["owner_approval_policy"] == "owner approval only for risk tiers requiring it"
