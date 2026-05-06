from office.mission_command.e59_claim_extraction_and_evidence_atomizer import build_evidence_atoms


def test_evidence_atoms_do_not_upgrade_public_observation_to_validation():
    atoms = build_evidence_atoms()
    assert len(atoms) >= 8
    assert all(atom["not_customer_validation"] is True for atom in atoms)
    assert all(atom["not_paid_signal"] is True for atom in atoms)
    assert all(atom["not_expert_feedback"] is True for atom in atoms)
    assert all(atom["confidence_basis"] in {"direct_source", "unverified", "stale_source", "inferred_from_source"} for atom in atoms)

