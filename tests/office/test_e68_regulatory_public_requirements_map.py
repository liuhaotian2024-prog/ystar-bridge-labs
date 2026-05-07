import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_regulatory_map_uses_public_read_evidence_without_compliance_claims():
    receipts = json.loads((ROOT / "operations/external_validation/e68_regulatory_public_requirements_receipts.json").read_text())
    atoms = json.loads((ROOT / "operations/external_validation/e68_regulatory_public_requirements_evidence_atoms.json").read_text())
    assert receipts["receipt_count"] >= 10
    assert atoms["evidence_atom_count"] >= 10
    assert all(row["no_human_identification"] is True for row in receipts["receipts"])
    assert all(atom["no_compliance_claim"] is True for atom in atoms["atoms"])

