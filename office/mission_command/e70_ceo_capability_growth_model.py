from __future__ import annotations

from pathlib import Path

from . import e70_ceo_self_bootstrap_planner as planner


def load_e70_self_bootstrap_state_for_brain(root: Path | None = None) -> dict:
    base = root or planner.BRIDGE_ROOT
    state = planner.load_json("operations/external_validation/e70_ceo_brain_self_bootstrap_update.json", base)
    if not state:
        state = planner.write_kg_czl_cieu(base)
    return state


def get_capability_gap_registry(root: Path | None = None) -> dict:
    return planner.load_json("operations/external_validation/e70_ceo_capability_gap_registry.json", root) or planner.build_capability_gap_registry(root)


def map_goal_to_capability_requirements(goal_id: str, root: Path | None = None) -> dict:
    mapping = planner.load_json("operations/external_validation/e70_goal_to_capability_requirement_map.json", root) or planner.build_goal_to_capability_requirement_map(root)
    matches = [goal for goal in mapping.get("goals", []) if goal.get("goal_id") == goal_id]
    return {"goal_id": goal_id, "matches": matches, "external_action_allowed": False}


def generate_capability_growth_candidates(goal_id: str, root: Path | None = None) -> dict:
    candidates = planner.load_json("operations/external_validation/e70_ceo_self_improvement_candidate_set.json", root) or planner.build_self_improvement_candidate_set(root)
    return {"goal_id": goal_id, **candidates}


def generate_codex_job_proposal(capability_gap_id: str, root: Path | None = None) -> dict:
    proposal = planner.load_json("operations/external_validation/e70_generated_codex_job_proposal.json", root) or planner.generated_codex_job_proposal(root)
    return {"requested_capability_gap_id": capability_gap_id, **proposal}


def list_local_skill_candidates(root: Path | None = None) -> dict:
    return planner.build_skill_inventory_and_installation_boundary(root)


def create_owner_gated_skill_installation_packet(skill_id: str, root: Path | None = None) -> dict:
    return {
        "artifact_id": "e70_owner_gated_skill_installation_packet_preview",
        "skill_id": skill_id,
        "packet_status": "owner_reviewable_no_execution",
        "not_owner_approval": True,
        "installation_executed": False,
        "owner_approval_status": planner.OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def measure_capability_growth_result(action_id: str, root: Path | None = None) -> dict:
    return planner.measure_capability_growth_result(action_id, root)


def explain_self_bootstrap_boundaries(root: Path | None = None) -> dict:
    policy = planner.load_json("operations/external_validation/e70_capability_growth_action_policy.json", root) or planner.build_capability_growth_action_policy(root)
    skill = planner.load_json("operations/external_validation/e70_skill_inventory_and_installation_boundary.json", root) or planner.build_skill_inventory_and_installation_boundary(root)
    return {
        "policy": policy,
        "skill_installation_boundary": skill,
        "CEO_fully_autonomous_external_execution_claimed": False,
        "external_action_allowed": False,
    }
