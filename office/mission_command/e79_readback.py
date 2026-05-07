from __future__ import annotations

from pathlib import Path

from .e79_ceo_strategic_judgment_upgrade import (
    BRIDGE_ROOT,
    build_ceo_readback,
    build_completion_report,
    build_l4_owner_decision_packet,
    build_next_milestone_proposal,
    build_quality_gate,
    load_json,
    write_json,
)


def load_e79_strategic_judgment_state_for_brain(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e79_ceo_readback.json", base) or build_ceo_readback(base)


def get_e79_quality_gate(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e79_ceo_judgment_quality_gate.json", base) or build_quality_gate(base)


def get_e79_l4_owner_decision_packet(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e79_l4_owner_decision_packet_no_external_action.json", base) or build_l4_owner_decision_packet(base)


def get_e79_next_milestone_proposal(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e79_generated_next_milestone_proposal.json", base) or build_next_milestone_proposal(base)


def run_e79_readback_smoke(root: Path | None = None) -> dict:
    state = load_e79_strategic_judgment_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "strategic_judgment_upgraded": state.get("E79_status") == "ceo_strategic_judgment_upgraded_and_l4_packet_prepared",
        "selected_thesis_present": bool(state.get("selected_strategic_thesis")),
        "target_buyer_present": bool(state.get("target_buyer")),
        "trigger_event_present": bool(state.get("trigger_event")),
        "quality_gate_passed": state.get("quality_gate_passed") is True,
        "L4_packet_only": state.get("L4_packet_status") == "owner_reviewable_no_execution" and state.get("L4_execution_authorized") is False,
        "L5_not_claimed": state.get("L5_readiness_claimed") is False,
        "no_forbidden_claims": not any(
            bool(state.get(key))
            for key in [
                "customer_validation_claimed",
                "expert_validation_claimed",
                "paid_signal_claimed",
                "pricing_validation_claimed",
                "compliance_legal_claimed",
                "production_deployment_claimed",
                "L4_execution_claimed",
                "L5_readiness_claimed",
                "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
            ]
        ),
        "no_external_action": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e79_readback_smoke_result",
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def write_e79_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e79_readback_smoke(base)
    write_json(base, "operations/external_validation/e79_readback_smoke_result.json", result)
    return result


def get_e79_completion_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e79_completion_report.json", base) or build_completion_report(base)


__all__ = [
    "load_e79_strategic_judgment_state_for_brain",
    "get_e79_quality_gate",
    "get_e79_l4_owner_decision_packet",
    "get_e79_next_milestone_proposal",
    "run_e79_readback_smoke",
    "write_e79_readback_smoke",
    "get_e79_completion_report",
]
