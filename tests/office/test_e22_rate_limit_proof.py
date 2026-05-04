import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_rate_limit_proof_allows_selected_batch_and_blocks_excess():
    data = load("operations/external_validation/e22_rate_limit_proof.json")
    assert data["selected_batch_fits_quota"] is True
    assert data["selected_count"] == 5
    assert data["excess_hypothetical_result"] == "blocked_by_rate_limit"
    assert data["production_claims_excess_sends"] is False
