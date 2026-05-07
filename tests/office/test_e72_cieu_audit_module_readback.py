from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e72_cieu_audit_module_readback import (
    explain_e72_cieu_audit_module_limits,
    get_cieu_audit_module_product_binding,
    get_e72_generated_codex_job_proposal,
    load_e72_cieu_audit_module_state_for_brain,
    run_e72_cieu_audit_module_readback_smoke,
)


def test_e72_readback_exposes_hash_chain_module_state_to_ceo_brain():
    state = load_e72_cieu_audit_module_state_for_brain()
    assert state["K9_CIEU_hash_chain_context_bound"] is True
    assert state["CIEU_Audit_Module_integrated_into_governed_business_operations_blueprint"] is True
    assert state["production_ready"] is False
    assert state["external_action_allowed"] is False
    assert run_e72_cieu_audit_module_readback_smoke()["passes"] is True

    context = load_ceo_brain_context({"task_title": "e72 readback", "task_description": "CIEU audit module"})
    assert context["current_cieu_audit_module_status"] == "hash_chain_context_bound_internal_no_execution"
    assert context["current_cieu_audit_module_k9_context_bound"] is True
    assert context["current_cieu_audit_module_product_binding_status"] is True
    assert context["current_cieu_audit_module_production_ready"] is False
    assert context["current_cieu_audit_module_next_milestone"] == "E73_CIEU_hash_chain_structural_verifier_bridge_labs_adapter"
    assert context["current_cieu_audit_module_external_action_allowed"] is False


def test_e72_readback_limits_block_production_and_validation_claims():
    limits = explain_e72_cieu_audit_module_limits()
    assert limits["hash_chain_context_imported"] is True
    assert limits["production_hash_chain_enabled"] is False
    assert limits["live_ledger_written"] is False
    assert limits["full_audit_verification_completed"] is False
    assert limits["customer_validation_claimed"] is False
    assert limits["paid_signal_claimed"] is False
    assert limits["compliance_legal_claimed"] is False
    assert limits["external_action_allowed"] is False
    assert get_cieu_audit_module_product_binding()["external_action_allowed"] is False
    assert get_e72_generated_codex_job_proposal()["external_action_allowed"] is False

