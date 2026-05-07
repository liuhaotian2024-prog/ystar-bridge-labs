import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_ceo_external_validation_readback_passes():
    data = json.loads((ROOT / "operations/external_validation/e67_ceo_external_validation_readback_smoke_result.json").read_text())
    assert data["passes"] is True
    observed = data["observed_state"]
    assert observed["external_validation_status"] == "non_contact_external_validation_overlay_integrated"
    assert observed["external_action_allowed"] is False
    assert observed["EV7_achieved"] is False

