import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_portfolio_selection_creates_owner_discussion_agenda():
    data = json.loads((ROOT / "operations/external_validation/e32_portfolio_selection_and_owner_discussion_agenda.json").read_text())
    assert data["recommended_primary_path"] == "path_paid_readiness_review_service"
    assert data["secondary_path"] == "path_partner_validation_packet"
    assert len(data["strategic_reserve_paths"]) >= 3
    assert data["what_owner_should_decide"]
    assert data["customer_feedback_claimed"] is False
