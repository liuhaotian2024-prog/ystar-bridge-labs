from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

CAPABILITIES = [('strategic_imagination', 'Strategic Imagination', 'E35', ['operations/external_validation/e35_six_dimensional_ceo_cognition_model.json', 'operations/external_validation/e35_superhuman_ceo_cognition_challenge.json'], 'cognition_lens', 'compose_multiple_artifacts', ['imagination', 'strategic_imagination', 'strategy', 'creative']), ('innovation', 'Innovation Lens', 'E35', ['operations/external_validation/e35_capability_abstraction_recombination_method.json', 'operations/external_validation/e35_multi_hop_abstraction_jump_engine.json'], 'cognition_lens', 'compose_multiple_artifacts', ['innovation', 'creative', 'abstraction_recombination']), ('six_dimensional_cognition', 'Six-Dimensional CEO Cognition', 'E35', ['operations/external_validation/e35_six_dimensional_ceo_cognition_model.json', 'operations/external_validation/e35_six_dimensional_opportunity_cognition_protocol.json'], 'cognition_lens', 'read_static_artifact_as_input', ['six_dimensional_cognition', 'ceo_decision', 'strategy']), ('cross_domain_opportunity_field', 'Cross-Domain Opportunity Field', 'E35', ['operations/external_validation/e35_cross_domain_opportunity_field.json'], 'opportunity_generator', 'read_static_artifact_as_input', ['opportunity_generation', 'cross_domain_opportunity', 'market']), ('abstraction_recombination', 'Abstraction/Recombination', 'E35', ['operations/external_validation/e35_capability_abstraction_recombination_method.json'], 'opportunity_generator', 'read_static_artifact_as_input', ['abstraction_recombination', 'innovation']), ('adversarial_board_review', 'Adversarial Board Review', 'E36', ['operations/external_validation/e36_adversarial_ceo_board_review.json'], 'cognition_lens', 'read_static_artifact_as_input', ['adversarial_review', 'contrarian_review']), ('skeptical_cfo_review', 'Skeptical CFO Review', 'E36', ['operations/external_validation/e36_adversarial_ceo_board_review.json'], 'commercial_screen', 'compose_multiple_artifacts', ['skeptical_cfo', 'budget', 'commercial']), ('customer_empathy_review', 'Customer Empathy Review', 'E36', ['operations/external_validation/e36_demand_budget_reality_screen.json', 'operations/external_validation/e36_adversarial_ceo_board_review.json'], 'customer_lens', 'compose_multiple_artifacts', ['product_customer_empathy', 'customer', 'buyer']), ('demand_budget_reality_screen', 'Demand/Budget Reality Screen', 'E36', ['operations/external_validation/e36_demand_budget_reality_screen.json'], 'commercial_screen', 'read_static_artifact_as_input', ['demand_budget_screen', 'budget', 'buyer']), ('opportunity_evidence_ladder', 'Opportunity Evidence Ladder', 'E36', ['operations/external_validation/e36_opportunity_evidence_ladder.json'], 'evidence_lens', 'read_static_artifact_as_input', ['evidence_ladder', 'validation', 'evidence']), ('evidence_intelligence_claim_graph', 'Evidence Intelligence Claim Graph', 'E39', ['operations/external_validation/e39_deep_research_claim_graph.json'], 'evidence_lens', 'read_static_artifact_as_input', ['claim_graph', 'evidence_intelligence']), ('contradiction_awareness', 'Contradiction Awareness', 'E39', ['operations/external_validation/e39_contradiction_graph.json', 'operations/external_validation/e39_unsupported_claim_downgrade_register.json'], 'evidence_lens', 'read_static_artifact_as_input', ['contradiction', 'overclaim']), ('frontier_capability_import', 'Frontier Capability Import', 'E41', ['operations/external_validation/e41_frontier_capability_import_loop.json'], 'cognition_lens', 'read_static_artifact_as_input', ['frontier_capability_import', 'self_upgrade']), ('task_resource_router', 'Task Resource Router', 'E42', ['office/mission_command/e42_task_capability_matcher.py', 'operations/external_validation/e42_task_capability_matcher_model.json'], 'router', 'call_existing_function', ['task_resource_router', 'reuse']), ('reuse_first_no_rebuild_gate', 'Reuse-First No-Rebuild Gate', 'E42', ['office/mission_command/e42_reuse_first_no_rebuild_gate.py'], 'route_selector', 'call_existing_function', ['no_rebuild', 'reuse_first']), ('execution_boundary_alignment', 'Execution Boundary Alignment', 'E36/E43', ['operations/external_validation/e43_minimal_cross_repo_alignment.json'], 'execution_screen', 'read_static_artifact_as_input', ['execution_feasibility', 'gov_mcp', 'mcp']), ('governance_boundary_alignment', 'Governance Boundary Alignment', 'E36/E43', ['operations/external_validation/e43_minimal_cross_repo_alignment.json'], 'governance_boundary', 'read_static_artifact_as_input', ['governance', 'Y-star-gov']), ('first_user_value_path', 'First User Value Path', 'E43', ['operations/external_validation/e43_selected_first_value_path.json', 'office/mission_command/e43_first_value_loop_runner.py'], 'route_selector', 'compose_multiple_artifacts', ['first_user_value_path', 'commercial_wedge', 'execution_feasibility'])]

def build_ceo_capability_activation_registry() -> dict[str, Any]:
    capabilities = []
    for raw in CAPABILITIES:
        cid, display, milestone, paths, cclass, mode, tags = raw
        missing = [path for path in paths if not (REPO_ROOT / path).exists()]
        maturity = "active" if not missing and mode == "call_existing_function" else "partial" if not missing else "static_only"
        capabilities.append({
            "capability_id": cid,
            "display_name": display,
            "source_milestone": milestone,
            "source_paths": paths,
            "capability_class": cclass,
            "activation_mode": mode,
            "callable_entrypoint": {
                "task_resource_router": "office.mission_command.e42_task_capability_matcher.match_task_to_capabilities",
                "reuse_first_no_rebuild_gate": "office.mission_command.e42_reuse_first_no_rebuild_gate.evaluate_reuse_first_gate",
                "first_user_value_path": "office.mission_command.e43_first_value_loop_runner.build_first_value_loop_run_result",
            }.get(cid, ""),
            "required_inputs": ["task_title", "task_description", "owner_constraints"],
            "produced_outputs": ["lens_reasoning", "decision_effect", "route_pressure"],
            "task_triggers": tags,
            "capability_tags": tags,
            "owner_layer": "bridge_labs_ceo_runtime" if "gov_mcp" not in tags and "governance" not in tags else ("gov_mcp_execution_boundary" if "gov_mcp" in tags else "ystar_gov_governance_kernel"),
            "boundary_notes": "Bridge Labs cognition lens or read-only boundary reference; no duplicate kernel/execution layer.",
            "tests_to_run": [f"tests/office/test_{Path(paths[0]).stem}.py"] if (REPO_ROOT / "tests" / "office" / f"test_{Path(paths[0]).stem}.py").exists() else [],
            "maturity": maturity,
            "reason_if_parked": "",
        })
    return {
        "artifact_id": "e44a_ceo_capability_activation_registry",
        "registry_type": "callable_activation_map_not_tag_list",
        "capabilities": capabilities,
        "required_capability_ids_present": {item[0]: True for item in CAPABILITIES},
        "no_second_ceo_brain_created": True,
        "no_second_ceo_kg_created": True,
    }
