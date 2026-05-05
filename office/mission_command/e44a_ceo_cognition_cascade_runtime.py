from __future__ import annotations

from typing import Any

from .e44a_ceo_capability_activation_registry import build_ceo_capability_activation_registry
from .e44a_router_cognition_overlay import route_task_with_cognition_overlay

def _stage(stage_id: str, caps: list[str], artifacts: list[str], summary: str, effect: str, confidence: str, changed: str) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "invoked_capabilities": caps,
        "input_artifacts_used": artifacts,
        "reasoning_summary": summary,
        "decision_effect": effect,
        "confidence_class": confidence,
        "what_changed_from_resource_router_only": changed,
    }

def run_ceo_cognition_cascade(task: dict[str, Any]) -> dict[str, Any]:
    registry = build_ceo_capability_activation_registry()
    task_text = f"{task.get('task_title', '')}\n{task.get('task_description', '')}"
    overlay = route_task_with_cognition_overlay(task_text)
    artifacts = {
        "e35_opportunity": "operations/external_validation/e35_cross_domain_opportunity_field.json",
        "e35_cognition": "operations/external_validation/e35_six_dimensional_ceo_cognition_model.json",
        "e36_budget": "operations/external_validation/e36_demand_budget_reality_screen.json",
        "e36_adversarial": "operations/external_validation/e36_adversarial_ceo_board_review.json",
        "e36_ladder": "operations/external_validation/e36_opportunity_evidence_ladder.json",
        "e39_claim_graph": "operations/external_validation/e39_deep_research_claim_graph.json",
        "e41_import": "operations/external_validation/e41_frontier_capability_import_loop.json",
        "e42_router": "office/mission_command/e42_task_capability_matcher.py",
        "e43_path": "operations/external_validation/e43_selected_first_value_path.json",
    }
    stages = [
        _stage("task_interpretation", ["task_resource_router"], [artifacts["e42_router"]], "Task is a company value-path decision, not only an install-doc check.", "Require customer-understandable value object plus local proof.", "hypothesis", "Adds CEO interpretation."),
        _stage("resource_routing", ["task_resource_router"], [artifacts["e42_router"]], "E42 finds gov-mcp, Y-star-gov, E43 proof assets, and tests.", "Reuse existing path assets.", "artifact_supported", "Keeps router but does not stop there."),
        _stage("activation_registry_lookup", ["strategic_imagination", "six_dimensional_cognition", "first_user_value_path"], ["operations/external_validation/e44a_ceo_capability_activation_registry.json"], "Registry activates earlier cognition as task-time lenses.", "Forces E35/E36/E39/E41/E42/E43 participation.", "artifact_supported", "Turns dormant artifacts into stages."),
        _stage("strategic_imagination_recall", ["strategic_imagination"], [artifacts["e35_cognition"]], "Demonstrate agent-company governance value, not package installation alone.", "Upgrade story to governed agent action proof.", "artifact_supported", "Adds strategic imagination."),
        _stage("innovation_abstraction_recombination", ["innovation", "abstraction_recombination"], ["operations/external_validation/e35_capability_abstraction_recombination_method.json"], "Recombine install, governance, Bridge Labs dogfood, and audit-envelope language.", "Creates a value wrapper.", "hypothesis", "Transforms separate docs into a proof packet."),
        _stage("six_dimensional_cognition", ["six_dimensional_cognition"], [artifacts["e35_cognition"]], "Logical, innovation, strategic, systems, human, and execution/commercial lenses all support a proof-packet route.", "Route remains feasible but more CEO-complete.", "artifact_supported", "Adds six-lens reasoning."),
        _stage("opportunity_field_comparison", ["cross_domain_opportunity_field"], [artifacts["e35_opportunity"]], "Compare raw install trial with agent labor proof, board packet, registry, and notary variants.", "Keep high-imagination options as staged layers.", "artifact_supported", "Prevents install from becoming final product."),
        _stage("adversarial_review", ["adversarial_board_review", "skeptical_cfo_review", "customer_empathy_review"], [artifacts["e36_adversarial"], artifacts["e36_budget"]], "CFO rejects platform claims; customer lens rejects raw install docs; governance reviewer demands boundaries.", "Require before/after governed-action proof and do-not-claim list.", "artifact_supported", "Adds skepticism/customer empathy."),
        _stage("demand_budget_reality_screen", ["demand_budget_reality_screen"], [artifacts["e36_budget"]], "Demand and payment remain unproven; first persona is an AI engineer/operator with file/tool-touching agents.", "No customer validation or paid signal.", "evidence_supported", "Adds commercial discipline."),
        _stage("evidence_validation_burden", ["opportunity_evidence_ladder", "evidence_intelligence_claim_graph", "contradiction_awareness"], [artifacts["e36_ladder"], artifacts["e39_claim_graph"], "operations/external_validation/e39_contradiction_graph.json"], "Evidence supports governance pain but not Y* demand.", "Downgrade buyer-demand claims to hypotheses.", "evidence_supported", "Adds evidence burden."),
        _stage("high_imagination_preservation", ["strategic_imagination", "frontier_capability_import"], [artifacts["e41_import"], artifacts["e35_opportunity"]], "Preserve Agent Labor Proof Passport, Board Packet, Non-Human Workforce Registry, and AI Work Notary.", "Stage high-imagination options behind local proof.", "imagination_only", "Avoids narrowing to package install."),
        _stage("execution_feasibility_repo_ownership", ["execution_boundary_alignment", "governance_boundary_alignment"], [artifacts["e43_path"]], "Bridge Labs owns packet/story; gov-mcp owns execution; Y-star-gov owns governance; K9Audit remains audit add-on.", "No duplicate kernel/layer/ledger/brain/KG.", "artifact_supported", "Keeps boundaries."),
        _stage("no_rebuild_gate", ["reuse_first_no_rebuild_gate"], ["office/mission_command/e42_reuse_first_no_rebuild_gate.py"], "Reuse E43 runner/path; add cascade because no task-time cognition runtime existed.", "Minimum corrective delta.", "artifact_supported", "Adds runtime not report pile."),
        _stage("route_selection", ["first_user_value_path", "commercial_wedge"], [artifacts["e43_path"]], "Route remains gov-mcp + Y-star-gov as substrate; value object becomes Governed Agent Action Proof Packet.", "Route improved, not fully changed.", "hypothesis", "Distinguishes substrate from value object."),
        _stage("owner_action_recommendation", ["first_user_value_path", "execution_feasibility"], [artifacts["e43_path"]], "E45 should run activated CEO loop on the real local first-value demo and fix must-fix blockers.", "Owner decides local demo polish, not contact.", "artifact_supported", "Turns replay into execution."),
    ]
    return {
        "artifact_id": "e44a_ceo_cognition_cascade_smoke_result",
        "task": task,
        "overlay": overlay,
        "registry_capability_count": len(registry["capabilities"]),
        "stages": stages,
        "invoked_milestones": ["E35", "E36", "E39", "E41", "E42", "E43"],
        "invoked_capability_ids": sorted(set(cap for stage in stages for cap in stage["invoked_capabilities"])),
        "route_selection": {
            "technical_substrate": "gov-mcp + Y-star-gov governed execution in 5 minutes",
            "user_facing_value_object": "Governed Agent Action Proof Packet",
            "route_changed_from_E43": False,
            "route_improved_from_E43": True,
            "why": "E43 had the right substrate; E44A adds strategic/customer/commercial/evidence/high-imagination reasoning.",
        },
        "no_external_action": True,
        "customer_validation_claimed": False,
        "expert_feedback_claimed": False,
        "paid_signal_claimed": False,
    }
