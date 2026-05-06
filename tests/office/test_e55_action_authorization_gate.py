from office.mission_command.e55_action_authorization_gate import run_authorization_gate

def test_authorization_gate_allows_internal_dry_run_and_denies_unsafe():
    data = run_authorization_gate()
    assert data["gate_status"] == "passed"
    assert "e55_validate_authorization_gate" in data["dry_run_only_actions"]
    for action_id in ["fixture_external_contact_pending_owner", "fixture_publication_pending_owner", "fixture_payment_secret_action", "fixture_customer_validation_claim", "fixture_paid_signal_claim", "fixture_real_mcp_transport_claim", "fixture_ceo_brain_direct_execution", "fixture_missing_evidence_path", "fixture_bypass_canonical_runtime"]:
        assert action_id in data["denied_actions"]
    assert "fixture_unknown_action" in data["quarantined_actions"]
