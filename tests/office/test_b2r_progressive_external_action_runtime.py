from __future__ import annotations

import json
from pathlib import Path

from office.mission_command.b2r_account_governance import evaluate_account_creation
from office.mission_command.b2r_authenticated_session_policy import evaluate_authenticated_session
from office.mission_command.b2r_capability_domains import (
    build_capability_domains,
    evaluate_capability_action,
    public_evidence_is_validation_feedback,
)
from office.mission_command.b2r_c1_entry_gate import build_c1_entry_gate, evaluate_c1_entry
from office.mission_command.b2r_czl_closure import build_b2r_czl_closure
from office.mission_command.b2r_external_validation_messaging import (
    evaluate_external_validation_message,
    should_stop_for_feedback_event,
)
from office.mission_command.b2r_form_governance import evaluate_form_draft, evaluate_form_submission
from office.mission_command.b2r_gov_mcp_execution_contract import (
    build_gov_mcp_execution_contract,
    validate_gov_mcp_execution_contract,
)
from office.mission_command.b2r_owner_constitutional_envelope import build_owner_constitutional_envelope_request
from office.mission_command.b2r_progressive_unlock import (
    build_progressive_unlock_matrix,
    owner_required_for_every_micro_action,
)
from office.mission_command.b2r_publication_governance import (
    evaluate_governed_publication,
    evaluate_publication_draft,
)
from office.mission_command.b2r_y_gov_action_packet import build_action_packet, validate_action_packet


ROOT = Path(__file__).resolve().parents[2]


def readonly_envelope() -> dict:
    return {
        "credential_vault_ref": "vault://ystar/test",
        "account_identity": "company_test_account",
        "allowed_accounts": ["company_test_account"],
        "session_scope": "read_only",
        "session_duration_minutes": 15,
    }


def low_risk_submit_envelope() -> dict:
    return {
        "form_url": "https://example.com/contact",
        "form_category": "low_risk_submit",
        "approved_envelope_id": "env_1",
        "y_gov_validation_ref": "Y-star-gov::pre_u",
        "gov_mcp_contract_ref": "gov-mcp::execute_or_deny",
        "message_hash": "abc123",
    }


def governed_publication_envelope() -> dict:
    return {
        "channel_allowlist": ["company_blog"],
        "message_hash": "abc123",
        "claim_boundary_passed": True,
        "frequency_cap": "1/day",
        "frequency_ok": True,
        "takedown_plan": "remove_or_update_within_24h",
        "approved_envelope_id": "env_pub",
    }


def account_envelope() -> dict:
    return {
        "account_category": "vendor_trial_account",
        "identity_binding": "Y*Bridge Labs test identity",
        "no_payment": True,
        "no_contract": True,
        "no_kyc": True,
        "approved_vendor_envelope": "vendor_env",
    }


def message_envelope() -> dict:
    return {
        "approved_envelope_id": "env_msg",
        "approved_target_class": "ai_consultant_agency",
        "target_class": "ai_consultant_agency",
        "draft_family": "ai_transparent_validation",
        "max_sends": 3,
        "approved_max_sends": 3,
        "ai_transparency": True,
        "opt_out_language": True,
        "suppression_check": True,
    }


def test_a1_b1_outputs_exist_for_b2r_entry() -> None:
    assert (ROOT / "reports/cross_repo/a1_y_star_gov_full_evidence_chain.md").exists()
    assert (ROOT / "reports/cross_repo/a1_canonical_ownership_map.json").exists()
    assert (ROOT / "reports/cross_repo/a1_backflow_p0_p1_p2_plan.md").exists()
    assert (ROOT / "operations/external_validation/e14_owner_decision_console.md").exists()


def test_login_is_not_globally_hard_blocked() -> None:
    domains = {domain.domain_id: domain for domain in build_capability_domains()}
    assert "authenticated_readonly_observation" in domains
    assert "login_readonly" in domains["authenticated_readonly_observation"].allowed_actions


def test_authenticated_readonly_can_be_allowed_with_valid_envelope() -> None:
    decision = evaluate_authenticated_session(readonly_envelope())
    assert decision.allowed is True
    assert decision.owner_hard_approval_required is False


def test_missing_credentials_deny_safely() -> None:
    envelope = readonly_envelope()
    envelope["credential_vault_ref"] = ""
    decision = evaluate_authenticated_session(envelope)
    assert decision.allowed is False
    assert "missing_credential_vault_ref" in decision.reason_codes or "credential_missing" in decision.reason_codes


def test_authenticated_draft_creation_can_be_allowed() -> None:
    decision = evaluate_capability_action(
        "authenticated_draft_creation",
        {
            "credential_vault_ref": "vault://x",
            "account_identity": "acct",
            "draft_mode": True,
            "no_submit": True,
            "draft_storage_ref": "draft://1",
        },
    )
    assert decision.allowed is True


def test_form_draft_is_allowed() -> None:
    decision = evaluate_form_draft(
        {
            "form_url": "https://example.com",
            "form_category": "draft_only",
            "draft_only": True,
            "no_submit": True,
            "field_manifest": {"name": "Y*Bridge"},
        }
    )
    assert decision.allowed is True


def test_low_risk_form_submit_can_be_allowed_under_envelope() -> None:
    assert evaluate_form_submission(low_risk_submit_envelope()).allowed is True


def test_financial_legal_regulated_form_submit_is_hard_gated() -> None:
    envelope = low_risk_submit_envelope()
    envelope["form_category"] = "financial_submit"
    decision = evaluate_form_submission(envelope)
    assert decision.allowed is False
    assert decision.owner_hard_approval_required is True


def test_publication_draft_is_allowed() -> None:
    decision = evaluate_publication_draft(
        {
            "channel_ref": "company_blog",
            "draft_hash": "abc",
            "publication_mode": "draft_only",
            "claim_boundary_check": "passed",
        }
    )
    assert decision.allowed is True


def test_governed_publication_can_be_allowed_with_channel_claim_frequency_envelope() -> None:
    assert evaluate_governed_publication(governed_publication_envelope()).allowed is True


def test_high_claim_publication_escalates() -> None:
    envelope = governed_publication_envelope()
    envelope["high_claim"] = True
    decision = evaluate_governed_publication(envelope)
    assert decision.escalated is True


def test_low_risk_account_creation_can_be_allowed() -> None:
    assert evaluate_account_creation(account_envelope()).allowed is True


def test_payment_contract_kyc_account_creation_is_hard_gated() -> None:
    envelope = account_envelope()
    envelope["account_category"] = "kyc_account"
    decision = evaluate_account_creation(envelope)
    assert decision.owner_hard_approval_required is True
    assert decision.allowed is False


def test_external_validation_messaging_can_be_allowed_under_strict_envelope() -> None:
    decision = evaluate_external_validation_message(message_envelope())
    assert decision.allowed is True
    assert decision.action_ledger_required is True


def test_opt_out_triggers_suppression_and_stop() -> None:
    assert should_stop_for_feedback_event("opt_out") is True


def test_negative_feedback_triggers_stop_or_escalation() -> None:
    assert should_stop_for_feedback_event("negative_feedback") is True


def test_budget_exceeded_blocks() -> None:
    envelope = message_envelope()
    envelope["max_sends"] = 4
    decision = evaluate_external_validation_message(envelope)
    assert decision.allowed is False
    assert "budget_exceeded" in decision.reason_codes


def test_target_class_mismatch_blocks() -> None:
    envelope = message_envelope()
    envelope["target_class"] = "unapproved_class"
    decision = evaluate_external_validation_message(envelope)
    assert decision.allowed is False
    assert "target_class_mismatch" in decision.reason_codes


def test_action_packet_requires_y_gov_validation_reference() -> None:
    packet = build_action_packet("external_validation_message").to_dict()
    assert validate_action_packet(packet) == []
    packet["y_gov_validation_ref"] = ""
    assert "missing_y_gov_validation_ref" in validate_action_packet(packet)


def test_gov_mcp_execution_contract_exists() -> None:
    contract = build_gov_mcp_execution_contract()
    assert contract.tool_gateway_owner == "gov-mcp"
    assert validate_gov_mcp_execution_contract(contract) == []


def test_public_evidence_is_not_validation_feedback() -> None:
    assert public_evidence_is_validation_feedback() is False
    decision = evaluate_capability_action(
        "feedback_capture",
        {
            "action_id": "act_1",
            "feedback_source": "public_evidence",
            "recorded_by": "system",
            "feedback_summary": "pricing page",
            "limitations": "not customer feedback",
        },
    )
    assert decision.allowed is False


def test_action_ledger_is_required_for_external_action() -> None:
    assert evaluate_external_validation_message(message_envelope()).action_ledger_required is True


def test_cieu_residual_semantics_are_produced() -> None:
    matrix = build_progressive_unlock_matrix()
    assert any("Residual" in domain["cieu_residual_semantics"] for domain in matrix["domains"])


def test_owner_is_not_required_for_every_micro_action() -> None:
    assert owner_required_for_every_micro_action("authenticated_readonly_observation") is False
    assert build_owner_constitutional_envelope_request()["owner_role"] == "constitutional_boundary_setter_not_operator"


def test_owner_is_required_for_payment_legal_customer_system_core_writeback() -> None:
    assert evaluate_capability_action("payment_or_contract_gate", {"owner_explicit_approval_id": "owner_1", "legal_or_financial_review_ref": "ref"}).owner_hard_approval_required is True
    assert owner_required_for_every_micro_action("core_writeback_gate") is True


def test_c1_entry_is_blocked_without_valid_envelope() -> None:
    decision = evaluate_c1_entry("external_validation_message")
    assert decision.ready is False
    assert decision.blocked_reason == "missing_valid_envelope"


def test_c1_entry_is_allowed_as_readiness_only_when_contracts_exist() -> None:
    decision = evaluate_c1_entry("external_validation_message", message_envelope())
    assert decision.ready is True
    assert decision.readiness_only is True
    assert decision.no_live_action_executed is True


def test_no_live_external_action_is_executed_in_this_milestone() -> None:
    closure = build_b2r_czl_closure(repository_delivery_rt1=1)
    assert all(value is False for value in closure["no_external_side_effects"].values())


def test_host_side_delivery_bridge_is_used() -> None:
    request = json.loads(
        (ROOT / "operations/repository_delivery/delivery_requests/ab2_integrated_cross_repo_alignment_b2r_delivery.json").read_text(
            encoding="utf-8"
        )
    )
    assert request["remote_confirmation_required"] is True
    assert "host_delivery_runner.py" in request["safety_boundary"]


def test_b2r_artifacts_exist() -> None:
    for rel in [
        "operations/external_validation/b2r_progressive_capability_unlock_matrix.json",
        "operations/external_validation/b2r_owner_constitutional_envelope.request.json",
        "operations/external_validation/b2r_action_packet_examples.json",
        "operations/external_validation/b2r_escalation_policy.json",
        "operations/external_validation/b2r_c1_governed_action_entry_gate.json",
        "reports/integration/b2r_y_gov_governed_external_action_runtime.md",
        "reports/integration/b2r_cross_repo_integration_plan.md",
        "reports/integration/b2r_c1_entry_gate.md",
        "reports/integration/b2r_czl_closure.md",
    ]:
        assert (ROOT / rel).exists(), rel


def test_c1_gate_blocks_hard_gate_domains() -> None:
    decision = evaluate_c1_entry("payment_or_contract_gate", {"owner_explicit_approval_id": "owner_1"})
    assert decision.ready is False
    assert decision.blocked_reason == "owner_hard_gate_domain"


def test_c1_gate_contains_action_packet_and_contract() -> None:
    gate = build_c1_entry_gate()
    assert gate["action_packet_example"]["y_gov_validation_ref"].startswith("Y-star-gov::")
    assert gate["gov_mcp_execute_or_deny_contract"]["tool_gateway_owner"] == "gov-mcp"
