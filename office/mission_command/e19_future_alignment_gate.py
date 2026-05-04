from __future__ import annotations

from typing import Any, Dict


def build_future_alignment_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e19_future_milestone_alignment_gate",
        "required_for_future_large_milestones": [
            "ecosystem_alignment_scanner_result",
            "cross_repo_impact_matrix",
            "repo_modification_decision_packet",
            "drift_blocker_register",
            "local_only_or_ecosystem_aligned_closure_statement",
            "validation_coverage_statement",
            "bridge_delivery_closure",
        ],
        "per_milestone_bootstrap_allowed": False,
        "cross_repo_mutation_requires_explicit_future_milestone": True,
        "real_provider_send_requires_explicit_owner_activation": True,
        "external_action_executed": False,
    }


def render_future_alignment_gate(gate: Dict[str, Any]) -> str:
    lines = [
        "# E19 Future Milestone Alignment Gate",
        "",
        f"- per_milestone_bootstrap_allowed: {str(gate['per_milestone_bootstrap_allowed']).lower()}",
        f"- cross_repo_mutation_requires_explicit_future_milestone: {str(gate['cross_repo_mutation_requires_explicit_future_milestone']).lower()}",
        f"- real_provider_send_requires_explicit_owner_activation: {str(gate['real_provider_send_requires_explicit_owner_activation']).lower()}",
        "- external_action_executed: false",
        "",
        "## Required For Future Large Milestones",
    ]
    lines.extend(f"- {item}" for item in gate["required_for_future_large_milestones"])
    return "\n".join(lines).rstrip() + "\n"
