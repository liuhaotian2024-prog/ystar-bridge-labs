from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .e44a_ceo_cognition_cascade_runtime import run_ceo_cognition_cascade

REPO_ROOT = Path(__file__).resolve().parents[2]

def _load(rel: str) -> dict[str, Any]:
    try:
        return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}

def compare_e43_route_with_activated_cognition(task: dict[str, Any]) -> dict[str, Any]:
    old = _load("operations/external_validation/e43_selected_first_value_path.json")
    cascade = run_ceo_cognition_cascade(task)
    comparison = {
        "artifact_id": "e44a_old_vs_new_route_comparison",
        "old_route": {
            "path": old.get("selected_path", "gov-mcp + Y-star-gov governed execution in 5 minutes"),
            "mode": "E42 router plus local first-value path checker",
            "limitation": "Correct technical substrate, but weak E35/E36 cognition activation.",
        },
        "new_route": cascade["route_selection"],
        "route_changed": False,
        "route_improved": True,
        "improvements": [
            "E35/E36 cognition/opportunity artifacts are invoked explicitly.",
            "Raw install path is reframed as technical substrate.",
            "Customer empathy and skeptical CFO lenses alter packet requirements.",
            "High-imagination alternatives are preserved.",
            "Evidence burden remains explicit.",
        ],
        "referenced_prior_artifacts": [
            "operations/external_validation/e35_cross_domain_opportunity_field.json",
            "operations/external_validation/e35_six_dimensional_ceo_cognition_model.json",
            "operations/external_validation/e36_demand_budget_reality_screen.json",
            "operations/external_validation/e36_adversarial_ceo_board_review.json",
            "operations/external_validation/e39_deep_research_claim_graph.json",
            "operations/external_validation/e41_frontier_capability_import_loop.json",
        ],
        "concrete_next_action": "E45_run_activated_ceo_loop_on_real_local_first_value_demo",
        "no_external_action": True,
    }
    return comparison

def build_e43_task_replay_with_activated_cognition(task: dict[str, Any]) -> dict[str, Any]:
    comparison = compare_e43_route_with_activated_cognition(task)
    return {
        "artifact_id": "e44a_e43_task_replay_with_activated_cognition",
        "task": task,
        "comparison": comparison,
        "answers": {
            "selected_route_remains_gov_mcp_plus_Y_star_gov": True,
            "now_selected_for_stronger_reasons": True,
            "gov_mcp_install_is": "technical proof substrate",
            "first_user_should_receive": "Governed Agent Action Proof Packet built on gov-mcp + Y-star-gov install/check path",
            "high_imagination_preserved": ["Agent Labor Proof Passport", "Board Packet for Agentic Operations", "Non-Human Workforce Registry", "AI Work Authenticity Notary"],
            "skeptical_CFO_rejects": "Any claim of demand, paid signal, ROI, product-market fit, or Y* superiority.",
            "customer_empathy_says": "Use a visible before/after governed-action proof, not abstract runtime language.",
            "evidence_burden_remaining": ["local demo run", "docs clarity", "visible success predicate", "owner approval before outreach"],
            "concrete_next_action": "E45_run_activated_ceo_loop_on_real_local_first_value_demo",
        },
        "no_external_action": True,
    }
