from __future__ import annotations

from pathlib import Path

from . import e69_ceo_next_action_planner as planner


def load_e69_next_action_state_for_brain(root: Path | None = None) -> dict:
    return planner.load_e69_next_action_state_for_brain(root or planner.BRIDGE_ROOT)


def get_ceo_candidate_actions(root: Path | None = None) -> dict:
    return planner.get_ceo_candidate_actions(root or planner.BRIDGE_ROOT)


def get_ceo_next_action_scoring(root: Path | None = None) -> dict:
    return planner.get_ceo_next_action_scoring(root or planner.BRIDGE_ROOT)


def get_ceo_selected_next_action(root: Path | None = None) -> dict:
    return planner.get_ceo_selected_next_action(root or planner.BRIDGE_ROOT)


def get_owner_decision_packet(root: Path | None = None) -> dict:
    return planner.get_owner_decision_packet(root or planner.BRIDGE_ROOT)


def explain_next_action_selection(root: Path | None = None) -> dict:
    return planner.explain_next_action_selection(root or planner.BRIDGE_ROOT)


def run_ceo_next_action_planner_readback_smoke(root: Path | None = None) -> dict:
    return planner.build_ceo_next_action_planner_readback_smoke(root or planner.BRIDGE_ROOT)


def write_ceo_next_action_planner_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or planner.BRIDGE_ROOT
    data = run_ceo_next_action_planner_readback_smoke(root)
    planner.write_json(root, "operations/external_validation/e69_ceo_next_action_planner_readback_smoke_result.json", data)
    return data
