from __future__ import annotations

from pathlib import Path

from .e72_cieu_hash_chain_context import (
    BRIDGE_ROOT,
    build_e72_state_for_brain,
    build_readback_smoke,
    build_cieu_hash_chain_context,
    build_product_binding,
    build_generated_codex_job_proposal,
    load_e71_promoted_k9_cieu_assets,
    map_k9_cieu_to_bridge_labs_audit_module,
    write_json,
)


def load_e72_cieu_audit_module_state_for_brain(root: Path | None = None) -> dict:
    return build_e72_state_for_brain(root or BRIDGE_ROOT)


def get_cieu_hash_chain_context(root: Path | None = None) -> dict:
    return build_cieu_hash_chain_context(root or BRIDGE_ROOT)


def get_cieu_audit_module_product_binding(root: Path | None = None) -> dict:
    return build_product_binding(root or BRIDGE_ROOT)


def get_e72_generated_codex_job_proposal(root: Path | None = None) -> dict:
    return build_generated_codex_job_proposal(root or BRIDGE_ROOT)


def explain_e72_cieu_audit_module_limits(root: Path | None = None) -> dict:
    state = load_e72_cieu_audit_module_state_for_brain(root or BRIDGE_ROOT)
    return {
        "production_ready": False,
        "K9Audit_code_mutated": False,
        "hash_chain_context_imported": state["K9_CIEU_hash_chain_context_bound"],
        "production_hash_chain_enabled": False,
        "live_ledger_written": False,
        "full_audit_verification_completed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "compliance_legal_claimed": False,
        "external_action_allowed": False,
        "forbidden_claims": state.get("forbidden_claims", []),
    }


def run_e72_cieu_audit_module_readback_smoke(root: Path | None = None) -> dict:
    return build_readback_smoke(root or BRIDGE_ROOT)


def write_e72_cieu_audit_module_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e72_cieu_audit_module_readback_smoke(base)
    write_json(base, "operations/external_validation/e72_cieu_audit_module_readback_smoke_result.json", result)
    return result


__all__ = [
    "load_e72_cieu_audit_module_state_for_brain",
    "get_cieu_hash_chain_context",
    "get_cieu_audit_module_product_binding",
    "get_e72_generated_codex_job_proposal",
    "explain_e72_cieu_audit_module_limits",
    "run_e72_cieu_audit_module_readback_smoke",
    "write_e72_cieu_audit_module_readback_smoke",
    "load_e71_promoted_k9_cieu_assets",
    "map_k9_cieu_to_bridge_labs_audit_module",
]
