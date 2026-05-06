from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, NEAREST_ALTERNATIVE, NEXT_MILESTONE, OWNER_STATUS, SELECTED_ACTION, write_json, write_md
from .e56_internal_cycle_scenario_builder import build_internal_cycle_scenario


def _score(candidate: dict[str, Any]) -> dict[str, Any]:
    action_id = candidate["action_id"]
    base = {
        "action_id": action_id,
        "U_intervention": candidate["intent"],
        "predicted_Yt_plus_1": "internal loop proof advances" if action_id == SELECTED_ACTION else "partial progress",
        "predicted_Rt_plus_1": NEXT_MILESTONE if action_id == SELECTED_ACTION else "defer or block",
        "blocker_effect": "closes internal loop proof gap" if action_id == SELECTED_ACTION else "does not close E56 proof gap",
        "governance_risk": "low" if candidate["disposition"] != "deny" else "P0_if_executed",
        "commercial_risk": "low" if action_id == SELECTED_ACTION else "medium",
        "reversibility": "high",
        "evidence_needed": ["queue", "authorization", "dry-run", "KG/CZL/CIEU", "brain readback"],
        "external_action_risk": "none" if candidate["action_type"] != "external_contact" else "blocked",
        "owner_approval_required": candidate["owner_approval_required"],
        "action_authorization_expected": "dry_run_only" if action_id == SELECTED_ACTION else ("deny" if candidate["disposition"] == "deny" else "future_not_executed"),
        "deterministic_score": 90 if action_id == SELECTED_ACTION else (76 if action_id == NEAREST_ALTERNATIVE else (20 if candidate["disposition"] == "deny" else 60)),
    }
    return base


def run_counterfactual_internal_action_selection() -> dict[str, Any]:
    scenario = build_internal_cycle_scenario()
    analyses = [_score(c) for c in scenario["candidate_actions"]]
    return {
        "artifact_id": "e56_counterfactual_internal_action_selection",
        "Xt_current_state": "CEO Brain L5 and Behavior Center L5 are ready; owner review remains pending.",
        "Y_star_target": "prove a complete internal company operating loop without external action",
        "candidate_analyses": analyses,
        "selected_action": SELECTED_ACTION,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "why_selected": "It closes the exact E56 proof gap with reversible internal dry-run evidence.",
        "why_not_alternative": "E57 money-route retest should wait until the internal loop proof is written, read back, and gated.",
        "owner_decision_status": OWNER_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_counterfactual_internal_action_selection(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_counterfactual_internal_action_selection()
    write_json(root, "operations/external_validation/e56_counterfactual_internal_action_selection.json", data)
    write_md(root, "reports/integration/e56_counterfactual_internal_action_selection.md", "E56 Counterfactual Internal Action Selection", [
        f"Selected action: `{data['selected_action']}`",
        f"Nearest alternative: `{data['nearest_alternative']}`",
        data["why_not_alternative"],
    ])
    return data

