import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_validation_atoms_map_to_ev_levels_without_overclaim():
    data = json.loads((ROOT / "operations/external_validation/e67_external_validation_evidence_atoms.json").read_text())
    assert data["evidence_atom_count"] >= 24
    assert data["mapped_to_E65_signal_taxonomy_where_possible"] is True
    for atom in data["atoms"]:
        assert atom["EV_level"].startswith("EV")
        assert atom["no_customer_validation_claimed"] is True
        assert atom["no_paid_signal_claimed"] is True
        assert atom["no_pricing_validation_claimed"] is True

