from __future__ import annotations

from pathlib import Path

from .e76_e77_lineage_decision_and_conditional_l3 import (
    BRIDGE_ROOT,
    build_ceo_readback,
    build_completion_report,
    build_generated_next_milestone_proposal,
    build_owner_decision_record,
    build_prior_public_read_lineage_map,
    build_public_read_lineage_reconciliation,
    build_phase_gate_result,
    load_json,
    write_json,
)


def load_e76_e77_state_for_brain(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_ceo_readback.json", base) or build_ceo_readback(base)


def get_e76_e77_prior_public_read_lineage(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_prior_public_read_lineage_map.json", base) or build_prior_public_read_lineage_map(base)


def get_e76_e77_lineage_reconciliation(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_public_read_lineage_reconciliation.json", base) or build_public_read_lineage_reconciliation(base)


def get_e76_e77_owner_decision_record(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_owner_decision_record.json", base) or build_owner_decision_record(base)


def get_e76_e77_phase_gate_result(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_phase_gate_result.json", base) or build_phase_gate_result(base)


def get_e76_e77_next_milestone_proposal(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_generated_next_milestone_proposal.json", base) or build_generated_next_milestone_proposal(base)


def run_e76_e77_readback_smoke(root: Path | None = None) -> dict:
    state = load_e76_e77_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "phase_A_state_loaded": state.get("prior_public_read_lineage_exists") is True,
        "owner_decision_recorded": state.get("owner_decision_status") in {
            "pending_owner_decision",
            "APPROVE_L3_READ_ONLY_RESEARCH_PILOT",
            "APPROVE_WITH_SCOPE_REDUCTION",
            "REQUEST_MORE_L2_INTERNAL_WORK",
            "REJECT_L3_FOR_NOW",
        },
        "pending_blocks_L3": state.get("owner_decision_status") != "pending_owner_decision" or state.get("did_execute_L3") is False,
        "lineage_correction_available": "Historical public-read" in str(state.get("why_not_first_external_read_only_research", "")),
        "L4_L5_not_ready": state.get("L4_ready") is False and state.get("L5_ready") is False,
        "no_forbidden_claims": not any(
            bool(state.get(key))
            for key in [
                "customer_validation_claimed",
                "paid_signal_claimed",
                "pricing_validation_claimed",
                "compliance_legal_claimed",
                "production_deployment_claimed",
                "live_ledger_claimed",
                "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
            ]
        ),
    }
    return {
        "artifact_id": "e76_e77_readback_smoke_result",
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": bool(state.get("external_action_allowed", False)),
    }


def write_e76_e77_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e76_e77_readback_smoke(base)
    write_json(base, "operations/external_validation/e76_e77_readback_smoke_result.json", result)
    return result


def get_e76_e77_completion_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e76_e77_completion_report.json", base) or build_completion_report(base)


__all__ = [
    "load_e76_e77_state_for_brain",
    "get_e76_e77_prior_public_read_lineage",
    "get_e76_e77_lineage_reconciliation",
    "get_e76_e77_owner_decision_record",
    "get_e76_e77_phase_gate_result",
    "get_e76_e77_next_milestone_proposal",
    "run_e76_e77_readback_smoke",
    "write_e76_e77_readback_smoke",
    "get_e76_e77_completion_report",
]

