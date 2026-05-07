import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_completion_gate_passes_with_completed_or_partial_status():
    data = json.loads((ROOT / "operations/external_validation/e67_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] in {
        "e67_non_contact_external_validation_upgrade_completed",
        "e67_non_contact_validation_partial_with_public_read_blocker",
    }
    assert data["receipts_created"] >= 24
    assert data["EV5_achieved"] is False
    assert data["recommended_next_milestone"] in {
        "E68_owner_decision_packet_for_controlled_external_review_no_execution",
        "E68_targeted_non_contact_validation_refresh",
        "E68_compare_selected_route_vs_fallback_with_owner_decision_no_execution",
    }

