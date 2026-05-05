from pathlib import Path
import json

from office.mission_command.e36_evidence_seeking_shortlist_builder import build_evidence_seeking_shortlist


ROOT = Path(__file__).resolve().parents[2]


def test_shortlist_prepares_evidence_routes_without_product_selection():
    data = build_evidence_seeking_shortlist()
    assert data["final_product_selected"] is False
    assert data["customer_contact_in_e36"] is False
    assert data["near_term_evidence_ready_clusters"]
    assert data["high_imagination_clusters"]
    assert data["recommended_next_evidence_route"].startswith("owner-approved")
    closure = json.loads((ROOT / "operations/external_validation/e36_czl_closure.json").read_text())
    assert closure["customer_contact_occurred"] is False
    assert closure["message_sent"] is False
    assert closure["published_externally"] is False
    assert closure["provider_api_called"] is False
    assert closure["payment_occurred"] is False
    assert closure["customer_validation_claimed"] is False
    assert closure["paid_signal_claimed"] is False
