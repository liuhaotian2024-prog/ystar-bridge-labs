from office.mission_command.e73_readback import get_e72_proposal_reclassification, get_no_new_wheel_policy


def test_e73_no_new_wheel_policy_blocks_bridge_labs_production_verifier():
    policy = get_no_new_wheel_policy()
    cieu_rule = policy["domain_rules"]["CIEU_ledger_hash_verification"]

    assert cieu_rule["canonical_owner"] == "K9Audit"
    assert "independent_cryptographic_verifier" in cieu_rule["bridge_labs_blocked"]
    assert "production_hash_chain_ledger" in cieu_rule["bridge_labs_blocked"]
    assert "adapter_contract" in cieu_rule["bridge_labs_allowed"]
    assert policy["new_file_justification_required"]["non_duplication_evidence"] == "required"
    assert policy["external_action_allowed"] is False


def test_e73_reclassifies_e72_structural_verifier_proposal_not_blindly_accepts_it():
    reclassification = get_e72_proposal_reclassification()

    assert reclassification["loaded_E72_proposal_id"] == "E73_CIEU_hash_chain_structural_verifier_bridge_labs_adapter"
    assert reclassification["accepted_as_is"] is False
    assert reclassification["blindly_executed"] is False
    assert reclassification["blocked_as_production_verifier_duplicate"] is True
    assert "CIEU sample packet structural contract" in reclassification["allowed_narrowed_scope"]
    assert "bridge-labs production hash-chain verifier" in reclassification["forbidden_scope"]
    assert reclassification["external_action_allowed"] is False
