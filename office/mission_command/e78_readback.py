from __future__ import annotations

from pathlib import Path

from .e78_l3_owner_approved_research_pilot import (
    BRIDGE_ROOT,
    build_ceo_readback,
    build_completion_report,
    build_next_milestone_proposal,
    build_post_run_readiness_assessment,
    build_source_receipts,
    load_json,
    write_json,
)


def load_e78_l3_research_state_for_brain(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e78_ceo_readback.json", base) or build_ceo_readback(base)


def get_e78_source_receipts(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e78_l3_source_receipts.json", base) or build_source_receipts(base)


def get_e78_post_run_readiness_assessment(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e78_l3_post_run_readiness_assessment.json", base) or build_post_run_readiness_assessment(base)


def get_e78_next_milestone_proposal(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e78_generated_next_milestone_proposal.json", base) or build_next_milestone_proposal(base)


def run_e78_readback_smoke(root: Path | None = None) -> dict:
    state = load_e78_l3_research_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "L3_executed": state.get("did_execute_L3") is True,
        "owner_approval_explicit": state.get("owner_approval_explicit") is True,
        "source_receipts_present": int(state.get("source_count") or 0) >= 20,
        "L4_packet_prep_only": state.get("L4_owner_decision_packet_preparation_justified") is True and state.get("L4_execution_ready") is False,
        "L5_not_ready": state.get("L5_ready") is False,
        "no_forbidden_claims": not any(
            bool(state.get(key))
            for key in [
                "customer_validation_claimed",
                "expert_validation_claimed",
                "paid_signal_claimed",
                "pricing_validation_claimed",
                "compliance_legal_claimed",
                "production_deployment_claimed",
                "live_ledger_claimed",
                "L4_execution_readiness_claimed",
                "L5_readiness_claimed",
                "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
            ]
        ),
        "no_external_action_after_E78": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e78_readback_smoke_result",
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def write_e78_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e78_readback_smoke(base)
    write_json(base, "operations/external_validation/e78_readback_smoke_result.json", result)
    return result


def get_e78_completion_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e78_completion_report.json", base) or build_completion_report(base)


__all__ = [
    "load_e78_l3_research_state_for_brain",
    "get_e78_source_receipts",
    "get_e78_post_run_readiness_assessment",
    "get_e78_next_milestone_proposal",
    "run_e78_readback_smoke",
    "write_e78_readback_smoke",
    "get_e78_completion_report",
]

