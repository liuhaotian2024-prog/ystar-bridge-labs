from office.mission_command.action_authorization_router import ActionAuthorizationRequest, authorize_external_action


def _valid_request(**overrides):
    payload = {
        "action_id": "act_1",
        "action_type": "send_validation_message",
        "risk_tier": "Tier 2",
        "target_lifecycle_state": "preflighted_action_target",
        "owner_approval_present": True,
        "manifest_valid": True,
        "channel_approved": True,
        "draft_hash_valid": True,
        "y_star_gov_decision": "owner_approval_required_and_present",
        "gov_mcp_gateway_available": True,
        "gov_mcp_preflight_passed": True,
        "execution_provider_available": True,
        "no_forbidden_side_effects": True,
    }
    payload.update(overrides)
    return ActionAuthorizationRequest(**payload)


def test_action_authorization_router_references_y_star_gov_decision_if_router_implemented():
    decision = authorize_external_action(_valid_request(y_star_gov_decision="missing"))
    assert decision.allowed is False
    assert decision.y_star_gov_reference_required is True
    assert "Y_star_gov" in decision.blocked_reason


def test_action_authorization_router_references_gov_mcp_gateway_when_available_if_router_implemented():
    decision = authorize_external_action(_valid_request(gov_mcp_gateway_available=False))
    assert decision.allowed is False
    assert decision.gov_mcp_gateway_reference_required is True
    assert "gov_mcp_gateway_available" in decision.blocked_reason


def test_e10_or_e11_paths_cannot_bypass_routers_for_target_contact():
    decision = authorize_external_action(_valid_request(target_lifecycle_state="proposed_target_seed"))
    assert decision.allowed is False
    assert decision.blocked_reason == "target_must_pass_canonical_lifecycle_preflight"

