from pathlib import Path

from office.mission_command.action_authorization_router import ActionAuthorizationRequest, authorize_external_action
from office.mission_command.e12_action_packet import E12ValidationActionPacket
from office.mission_command.e12_execution_gate import (
    DeterministicFakeE12ProviderForTestsOnly,
    DisabledE12ExternalValidationProvider,
    execute_e12_validation,
)
from office.mission_command.e12_validation_approval import E12ApprovalStatus


def _approval(mode="aiden_executes_if_provider_available"):
    return E12ApprovalStatus(
        approval_present=True,
        approval_valid=True,
        approval_path="operations/external_validation/e12_owner_approval.json",
        request_path="operations/external_validation/e12_owner_approval.request.json",
        approval_state="owner_approved",
        approved_batch_id="batch_ai_ops_agency_governance_layer",
        approved_target_ids=["cand_alicelabs_alicelabs"],
        approved_draft_id="e8_ai_disclosed_outreach_draft",
        approved_draft_hash="hash",
        execution_mode=mode,
        max_external_messages=1,
        errors=[],
    )


def _packet():
    return E12ValidationActionPacket(
        action_id="e12_validation_action_001",
        target_id="cand_alicelabs_alicelabs",
        target_label="Alice Labs",
        channel="owner_approved_public_general_channel",
        draft_id="e8_ai_disclosed_outreach_draft",
        draft_hash="hash",
        ai_transparency_statement="I'm Aiden, an AI-assisted CEO/runtime agent.",
        opt_out_language="Please ignore if not useful; no automated follow-up.",
        max_count=1,
        stop_conditions=["opt out"],
        owner_approval_reference="approval",
        target_router_state="preflighted_action_target",
        action_authorization_allowed=True,
        action_authorization_blocked_reason="",
        external_action_expected=True,
        packet_errors=[],
    )


def test_preflighted_target_executable_only_if_action_authorization_passes():
    request = ActionAuthorizationRequest(
        action_id="act",
        action_type="send_validation_message",
        risk_tier="Tier 2",
        target_lifecycle_state="preflighted_action_target",
        owner_approval_present=True,
        manifest_valid=True,
        channel_approved=True,
        draft_hash_valid=True,
        y_star_gov_decision="owner_approval_required_and_present",
        gov_mcp_gateway_available=True,
        gov_mcp_preflight_passed=True,
        execution_provider_available=True,
        no_forbidden_side_effects=True,
    )
    assert authorize_external_action(request).allowed is True


def test_missing_provider_creates_owner_handoff_not_fake_execution(tmp_path: Path):
    result = execute_e12_validation(tmp_path, [_packet()], _approval(), provider=DisabledE12ExternalValidationProvider())
    assert result.execution_status == "blocked_missing_safe_provider"
    assert result.aiden_sent_anything is False
    assert result.handoff_packet_path.endswith("e12_owner_operated_handoff_packet.md")


def test_owner_operated_feedback_path_does_not_claim_aiden_sent(tmp_path: Path):
    result = execute_e12_validation(tmp_path, [_packet()], _approval("owner_operated_handoff"))
    assert result.execution_status == "owner_operated_handoff_ready"
    assert result.aiden_sent_anything is False
    assert result.customer_contact_occurred is False


def test_execution_with_fake_provider_requires_action_ledger_if_sent(tmp_path: Path):
    result = execute_e12_validation(tmp_path, [_packet()], _approval(), provider=DeterministicFakeE12ProviderForTestsOnly())
    assert result.aiden_sent_anything is True
    assert result.action_ledger_path.endswith("e12_external_action_ledger.md")
    assert (tmp_path / "reports/integration/e12_external_action_ledger.md").exists()

