from office.mission_command.e20_autonomous_execution_eligibility import classify_autonomous_eligibility


def test_provider_missing_is_not_owner_manual_required():
    provider = {"provider_capability_status": "no_send_only", "live_provider_adapter_present": False}
    action = {
        "action_id": "a1",
        "action_type": "external_validation_message",
        "risk_tier": "T2_low_medium_limited_outbound",
        "evidence_sufficient": True,
        "suppression_clear": True,
        "policy_compatible": True,
    }
    result = classify_autonomous_eligibility(action, provider)
    assert result["executor_decision"] == "provider_capability_missing"
    assert result["owner_approval_required"] is False
    assert "policy_allows_autonomous_but_provider_missing" in result["reason_codes"]


def test_no_go_blocks_before_provider_check():
    provider = {"provider_capability_status": "live", "live_provider_adapter_present": True, "provider_tests_present": True}
    result = classify_autonomous_eligibility({"action_id": "x", "action_type": "payment", "evidence_sufficient": True, "suppression_clear": True}, provider)
    assert result["executor_decision"] == "blocked_no_go"
