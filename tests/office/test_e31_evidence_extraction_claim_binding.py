import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_evidence_and_claims_are_bound_not_invented():
    pain = json.loads((ROOT / "operations/external_validation/e31_observed_buyer_pain_evidence.json").read_text())
    claims = json.loads((ROOT / "operations/external_validation/e31_offer_claim_register.json").read_text())
    assert pain["buyer_pain_evidence_count"] == 15
    assert claims["supported_claim_count"] == 8
    assert claims["unsupported_claims_removed_count"] == 4
    assert claims["customer_feedback_claimed"] is False
