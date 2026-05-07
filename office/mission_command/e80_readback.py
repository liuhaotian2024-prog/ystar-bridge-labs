from __future__ import annotations

from pathlib import Path

from .e80_ceo_online_cognition_loop import (
    BRIDGE_ROOT,
    build_ceo_readback,
    build_completion_report,
    build_cognitive_loop_demo,
    build_next_milestone_proposal,
    build_online_cognition_loop_spec,
    load_json,
    write_json,
)


def load_e80_cognitive_activation_state_for_brain(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e80_ceo_cognitive_activation_readback.json", base) or build_ceo_readback(base)


def get_e80_cognition_loop_spec(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e80_ceo_online_cognition_loop_spec.json", base) or build_online_cognition_loop_spec(base)


def get_e80_cognitive_loop_demo(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json", base) or build_cognitive_loop_demo(base)


def get_e80_next_milestone_proposal(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e80_generated_next_milestone_proposal.json", base) or build_next_milestone_proposal(base)


def get_e80_completion_report(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e80_completion_report.json", base) or build_completion_report(base)


def run_e80_readback_smoke(root: Path | None = None) -> dict:
    state = load_e80_cognitive_activation_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "discovery_first_status": state.get("E80_R2_status") == "discovery_first_ceo_cognition_loop_activated",
        "files_inventoried": int(state.get("files_inventoried") or 0) > 1000,
        "capabilities_discovered": int(state.get("capabilities_discovered") or 0) > 50,
        "repository_discovered_capabilities_visible": int(state.get("repository_discovered_not_prompt_hinted_count") or 0) > 0,
        "prompt_hinted_unverified_visible": int(state.get("prompt_hinted_unverified_count") or 0) > 0,
        "counterfactual_comparison_active": state.get("counterfactual_comparison_status") in {"runtime_active", "context_bound_or_readback_active", "repository_evidence_present_but_not_active"},
        "pre_action_CIEU_prediction_visible": state.get("pre_action_CIEU_prediction_status") in {"runtime_active", "context_bound_or_readback_active", "repository_evidence_present_but_not_active", "design_bound_not_runtime_active"},
        "demo_decision_present": bool(state.get("live_cognition_loop_demo_decision")),
        "no_external_action": state.get("external_action_allowed") is False,
        "no_L4_execution": state.get("L4_execution_authorized") is False,
        "no_L5_claim": state.get("L5_ready") is False,
    }
    return {
        "artifact_id": "e80_readback_smoke_result",
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def write_e80_readback_smoke(root: Path | None = None) -> dict:
    base = root or BRIDGE_ROOT
    result = run_e80_readback_smoke(base)
    write_json(base, "operations/external_validation/e80_readback_smoke_result.json", result)
    return result


__all__ = [
    "load_e80_cognitive_activation_state_for_brain",
    "get_e80_cognition_loop_spec",
    "get_e80_cognitive_loop_demo",
    "get_e80_next_milestone_proposal",
    "get_e80_completion_report",
    "run_e80_readback_smoke",
    "write_e80_readback_smoke",
]
