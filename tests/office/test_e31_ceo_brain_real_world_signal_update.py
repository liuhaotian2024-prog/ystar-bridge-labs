import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_brain_updates_bottleneck_after_observation():
    data = json.loads((ROOT / "operations/external_validation/e31_ceo_brain_real_world_signal_update.json").read_text())
    assert data["real_world_observation_status"] == "executed"
    assert data["paid_readiness_review_package_status"] == "no_send_feedback_ready"
    assert data["production_live_remains_disabled"] is True
    assert data["next_decision_horizon"] == "E32_owner_reviewed_publication_draft_or_partner_validation_packet"
