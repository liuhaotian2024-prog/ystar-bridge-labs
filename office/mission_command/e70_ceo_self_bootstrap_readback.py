from __future__ import annotations

from pathlib import Path

from . import e70_ceo_self_bootstrap_planner as planner
from .e70_ceo_capability_growth_model import (
    create_owner_gated_skill_installation_packet,
    explain_self_bootstrap_boundaries,
    generate_capability_growth_candidates,
    generate_codex_job_proposal,
    get_capability_gap_registry,
    list_local_skill_candidates,
    load_e70_self_bootstrap_state_for_brain,
    map_goal_to_capability_requirements,
    measure_capability_growth_result,
)


def get_selected_self_bootstrap_action(root: Path | None = None) -> dict:
    return planner.load_json("operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", root) or planner.build_selected_self_bootstrap_decision(root)


def get_generated_codex_job_proposal(root: Path | None = None) -> dict:
    return planner.load_json("operations/external_validation/e70_generated_codex_job_proposal.json", root) or planner.generated_codex_job_proposal(root)


def get_self_bootstrap_use_case_result(root: Path | None = None) -> dict:
    return planner.load_json("operations/external_validation/e70_self_bootstrap_l5_use_case_result.json", root) or planner.build_self_bootstrap_l5_use_case_result(root)


def run_ceo_self_bootstrap_readback_smoke(root: Path | None = None) -> dict:
    return planner.build_ceo_self_bootstrap_readback_smoke(root or planner.BRIDGE_ROOT)


def write_ceo_self_bootstrap_readback_smoke(output_root: Path | None = None) -> dict:
    base = output_root or planner.BRIDGE_ROOT
    result = run_ceo_self_bootstrap_readback_smoke(base)
    planner.write_json(base, "operations/external_validation/e70_ceo_self_bootstrap_readback_smoke_result.json", result)
    return result


__all__ = [
    "load_e70_self_bootstrap_state_for_brain",
    "get_capability_gap_registry",
    "map_goal_to_capability_requirements",
    "generate_capability_growth_candidates",
    "generate_codex_job_proposal",
    "list_local_skill_candidates",
    "create_owner_gated_skill_installation_packet",
    "measure_capability_growth_result",
    "explain_self_bootstrap_boundaries",
    "get_selected_self_bootstrap_action",
    "get_generated_codex_job_proposal",
    "get_self_bootstrap_use_case_result",
    "run_ceo_self_bootstrap_readback_smoke",
    "write_ceo_self_bootstrap_readback_smoke",
]
