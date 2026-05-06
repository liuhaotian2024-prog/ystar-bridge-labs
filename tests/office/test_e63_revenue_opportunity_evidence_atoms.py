import json
from pathlib import Path


def test_e63_evidence_atoms_do_not_overclaim_public_read_evidence():
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "operations/external_validation/e63_revenue_opportunity_evidence_atoms.json").read_text())
    assert data["no_customer_validation_claimed"] is True
    assert data["no_paid_signal_claimed"] is True
    assert data["no_expert_feedback_claimed"] is True
    for atom in data["atoms"]:
        assert atom["no_customer_validation_claimed"] is True
        assert "public-read evidence only" in atom["limitation"]
