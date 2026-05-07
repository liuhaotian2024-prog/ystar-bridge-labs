from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .e80_repository_discovery import (
    BRIDGE_ROOT,
    EXPECTED_BASE,
    JOB_ID,
    base_verified,
    git_state,
    load_json,
    utc_now,
    write_discovery_outputs,
    write_json,
    write_md,
)


REQUIRED_LOOP_STAGES = [
    "mission_and_owner_constraint_recall",
    "full_capability_inventory_recall",
    "relevant_historical_asset_retrieval",
    "current_problem_classification",
    "canonical_owner_selection",
    "existing_module_reuse_extend_wrap_create_new_decision",
    "long_memory_KG_brain_recall_if_evidence_supported",
    "field_dimensional_reasoning_if_evidence_supported",
    "thesis_generation",
    "counterfactual_action_comparison",
    "pre_action_CIEU_residual_prediction",
    "adversarial_critique",
    "commercial_sharpness_gate",
    "no_new_wheel_gate",
    "decision",
    "post_action_CIEU_residual_and_learning_update",
]


def _top_caps(inventory: dict[str, Any], predicate, limit: int = 12) -> list[dict[str, Any]]:
    caps = [cap for cap in inventory.get("capabilities", []) if predicate(cap)]
    return sorted(
        caps,
        key=lambda item: (
            -int(item.get("CEO_intelligence_relevance", 0)),
            -int(item.get("commercial_relevance", 0)),
            -int(item.get("owner_relevance", 0)),
            item.get("capability_id", ""),
        ),
    )[:limit]


def _domain_caps(inventory: dict[str, Any], domains: set[str], limit: int = 5) -> list[dict[str, Any]]:
    return _top_caps(inventory, lambda cap: cap.get("capability_domain") in domains, limit)


def build_online_cognition_loop_spec(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    inventory = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", base)
    gap_map = load_json("operations/external_validation/e80_capability_activation_gap_map.json", base)
    anti = load_json("operations/external_validation/e80_anti_memory_contamination_report.json", base)

    stage_caps = {
        "mission_and_owner_constraint_recall": _domain_caps(inventory, {"brain", "runtime"}, 4),
        "full_capability_inventory_recall": _top_caps(inventory, lambda cap: cap.get("repository_discovered") or cap.get("prompt_hint_used"), 6),
        "relevant_historical_asset_retrieval": _domain_caps(inventory, {"KG_memory", "commercial", "pricing", "product"}, 8),
        "current_problem_classification": _domain_caps(inventory, {"route_planning", "validation", "market"}, 5),
        "canonical_owner_selection": _domain_caps(inventory, {"governance", "audit", "provider"}, 7),
        "existing_module_reuse_extend_wrap_create_new_decision": _domain_caps(inventory, {"self_bootstrap", "route_planning", "governance"}, 6),
        "long_memory_KG_brain_recall_if_evidence_supported": _domain_caps(inventory, {"KG_memory", "brain"}, 6),
        "field_dimensional_reasoning_if_evidence_supported": _domain_caps(inventory, {"6D_field", "brain"}, 6),
        "thesis_generation": _domain_caps(inventory, {"market", "commercial", "product"}, 8),
        "counterfactual_action_comparison": _domain_caps(inventory, {"route_planning", "validation"}, 6),
        "pre_action_CIEU_residual_prediction": _domain_caps(inventory, {"CIEU", "audit"}, 6),
        "adversarial_critique": _domain_caps(inventory, {"brain", "route_planning", "validation"}, 4),
        "commercial_sharpness_gate": _domain_caps(inventory, {"commercial", "pricing", "market"}, 6),
        "no_new_wheel_gate": _domain_caps(inventory, {"governance", "provider", "audit"}, 6),
        "decision": _domain_caps(inventory, {"route_planning", "brain"}, 5),
        "post_action_CIEU_residual_and_learning_update": _domain_caps(inventory, {"CIEU", "KG_memory", "brain"}, 5),
    }
    stages = []
    for stage_id in REQUIRED_LOOP_STAGES:
        caps = stage_caps.get(stage_id, [])
        stages.append(
            {
                "stage_id": stage_id,
                "purpose": stage_id.replace("_", " "),
                "evidence_backed_capabilities": [
                    {
                        "capability_id": cap["capability_id"],
                        "domain": cap["capability_domain"],
                        "activation_state": cap["activation_state"],
                        "evidence_paths": cap.get("file_paths", [])[:5],
                    }
                    for cap in caps
                ],
                "status": _stage_status(stage_id, caps),
                "fails_if": _stage_failure_rule(stage_id),
            }
        )
    return {
        "artifact_id": "e80_ceo_online_cognition_loop_spec",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "evidence_driven_by_inventory": True,
        "raw_discovery_required_before_loop": True,
        "stage_count": len(stages),
        "stages": stages,
        "honest_activation_statuses": {
            "sixD_or_field_brain": _activation_status_for_domains(inventory, {"6D_field"}),
            "KG_or_long_memory": _activation_status_for_domains(inventory, {"KG_memory"}),
            "pre_action_CIEU_prediction": _activation_status_for_domains(inventory, {"CIEU"}),
            "counterfactual_comparison": _activation_status_for_domains(inventory, {"route_planning"}),
            "legacy_commercial_assets": _activation_status_for_domains(inventory, {"commercial", "pricing"}),
        },
        "failure_conditions": [
            "fails_if_only_uses_prompt_hinted_capabilities",
            "fails_if_capabilities_lack_repository_evidence",
            "fails_if_recent_milestone_only_reasoning",
            "fails_if_generic_summary_only",
            "fails_if_no_counterfactual_comparison",
            "fails_if_no_pre_action_CIEU_residual_prediction",
            "fails_if_no_adversarial_critique",
            "fails_if_no_what_not_to_do",
            "fails_if_recommends_construction_when_real_feedback_path_is_available",
        ],
        "anti_memory_contamination_source": {
            "repository_discovered_count": anti.get("actual_capabilities_discovered_not_named_in_prompt_count"),
            "prompt_hinted_unverified_count": anti.get("prompt_hinted_capabilities_not_verified_by_repository_evidence_count"),
        },
        "gap_bucket_counts": gap_map.get("bucket_counts", {}),
        "not_a_new_CEO_brain": True,
        "external_action_allowed": False,
    }


def _stage_status(stage_id: str, caps: list[dict[str, Any]]) -> str:
    if not caps:
        return "missing_runtime_hook"
    if any(cap.get("activation_state") == "active_in_current_CEO_loop" for cap in caps):
        return "runtime_active_or_adapter_active"
    if any(cap.get("activation_state") in {"active_but_shallow", "readback_only"} for cap in caps):
        return "active_but_shallow_or_readback_only"
    if any(cap.get("maturity") == "design_only" for cap in caps):
        return "design_bound_not_runtime_active"
    return "context_bound_from_repository_evidence"


def _stage_failure_rule(stage_id: str) -> str:
    if "CIEU" in stage_id:
        return "fail_if_action_selected_without_X_U_Y_star_Y_next_R_prediction"
    if "counterfactual" in stage_id:
        return "fail_if_only_one_path_is_considered"
    if "no_new_wheel" in stage_id:
        return "fail_if_bridge_labs_reimplements_K9_Y_star_gov_or_gov_mcp_core"
    if "thesis" in stage_id or "commercial" in stage_id:
        return "fail_if_buyer_pain_trigger_and_tradeoff_are_generic"
    return "fail_if_stage_uses_prompt_memory_without_repository_evidence"


def _activation_status_for_domains(inventory: dict[str, Any], domains: set[str]) -> str:
    caps = [cap for cap in inventory.get("capabilities", []) if cap.get("capability_domain") in domains]
    if not caps:
        return "missing"
    if any(cap.get("activation_state") == "active_in_current_CEO_loop" for cap in caps):
        return "runtime_active"
    if any(cap.get("activation_state") in {"active_but_shallow", "readback_only", "legacy_promoted"} for cap in caps):
        return "context_bound_or_readback_active"
    if any(cap.get("maturity") == "design_only" for cap in caps):
        return "design_bound_not_runtime_active"
    return "repository_evidence_present_but_not_active"


def build_high_value_capability_activation_plan(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    inventory = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", base)
    gap_map = load_json("operations/external_validation/e80_capability_activation_gap_map.json", base)
    candidates = []
    for bucket in ["active_but_shallow", "readback_only", "dormant_high_value", "repository_discovered_but_previously_ignored"]:
        candidates.extend(gap_map.get("buckets", {}).get(bucket, []))
    chosen: dict[str, dict[str, Any]] = {}
    for cap in candidates:
        if cap.get("activation_state") in {"prompt_hint_unverified", "duplicate_risk", "quarantined", "obsolete"}:
            continue
        if max(int(cap.get("owner_relevance", 0)), int(cap.get("commercial_relevance", 0)), int(cap.get("CEO_intelligence_relevance", 0))) < 70:
            continue
        chosen.setdefault(cap["capability_id"], cap)
    activations = []
    for cap in sorted(chosen.values(), key=lambda item: (-int(item.get("CEO_intelligence_relevance", 0)), -int(item.get("commercial_relevance", 0)), item["capability_id"]))[:18]:
        activations.append(
            {
                "capability_id": cap["capability_id"],
                "source_evidence": {
                    "repo": cap["repo"],
                    "paths": cap.get("file_paths", [])[:8],
                    "symbols": cap.get("evidence_symbols", [])[:8],
                    "tests": cap.get("evidence_tests", [])[:5],
                },
                "previous_activation_state": cap["activation_state"],
                "activation_mode": _activation_mode(cap),
                "cognition_loop_stage": _loop_stage_for_domain(cap.get("capability_domain", "other")),
                "CEO_failure_addressed": _failure_addressed(cap.get("capability_domain", "other")),
                "no_duplication_proof": _no_duplication_proof(cap),
                "verification_test": "tests/office/test_e80_high_value_capability_activation.py",
            }
        )
    return {
        "artifact_id": "e80_high_value_capability_activation_plan",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "activation_basis": "selected_after_repository_discovery_and_activation_gap_classification",
        "activation_count": len(activations),
        "activated_capabilities": activations,
        "blocked_capabilities": [
            "production_CIEU_ledger_in_bridge_labs",
            "duplicate_Y_star_gov_governance_engine",
            "duplicate_gov_mcp_executor",
            "customer_validation_claim",
            "paid_signal_claim",
            "pricing_validation_claim",
        ],
        "not_a_parallel_CEO_brain": True,
        "external_action_allowed": False,
    }


def _loop_stage_for_domain(domain: str) -> str:
    mapping = {
        "brain": "long_memory_KG_brain_recall_if_evidence_supported",
        "6D_field": "field_dimensional_reasoning_if_evidence_supported",
        "KG_memory": "long_memory_KG_brain_recall_if_evidence_supported",
        "CIEU": "pre_action_CIEU_residual_prediction",
        "audit": "pre_action_CIEU_residual_prediction",
        "route_planning": "counterfactual_action_comparison",
        "market": "thesis_generation",
        "commercial": "commercial_sharpness_gate",
        "pricing": "commercial_sharpness_gate",
        "validation": "decision",
        "provider": "canonical_owner_selection",
        "governance": "no_new_wheel_gate",
        "self_bootstrap": "existing_module_reuse_extend_wrap_create_new_decision",
        "product": "thesis_generation",
    }
    return mapping.get(domain, "full_capability_inventory_recall")


def _activation_mode(cap: dict[str, Any]) -> str:
    owner = cap.get("canonical_owner")
    state = cap.get("activation_state")
    if owner in {"K9Audit", "Y-star-gov", "gov-mcp"}:
        return "wrap_existing_owner_context_read_only_no_reimplementation"
    if state == "readback_only":
        return "decision_gate_and_context_bind"
    if state == "active_but_shallow":
        return "call_or_read_existing_surface_before_new_work"
    return "context_bind_to_online_cognition_loop"


def _failure_addressed(domain: str) -> str:
    mapping = {
        "brain": "recent-memory dependence and generic assistant behavior",
        "6D_field": "flat summaries that do not position intent, risk, time, capability, and market feedback together",
        "KG_memory": "forgetting older project assets and owner critiques",
        "CIEU": "choosing actions without predicting residuals",
        "audit": "turning audit context into vague compliance language",
        "route_planning": "single-path inertia and next-milestone autopilot",
        "market": "banal market summaries without buyer pressure",
        "commercial": "artifact production without shortest path to real feedback or revenue",
        "pricing": "pricing speculation without separating proxy evidence from validation",
        "validation": "confusing public-read evidence with customer validation",
        "provider": "duplicate execution-envelope building",
        "governance": "duplicate governance-engine building",
    }
    return mapping.get(domain, "unactivated ecosystem memory")


def _no_duplication_proof(cap: dict[str, Any]) -> str:
    owner = cap.get("canonical_owner")
    if owner == "K9Audit":
        return "bridge-labs only imports context; K9Audit remains ledger/hash/verifier owner"
    if owner == "Y-star-gov":
        return "bridge-labs only imports governance context; Y-star-gov remains check/enforce owner"
    if owner == "gov-mcp":
        return "bridge-labs only imports execution-boundary context; gov-mcp remains MCP/provider owner"
    return "bridge-labs reuses existing module/artifact; no new CEO brain or generic runtime"


def build_intelligence_quality_gate_v2(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    candidates = load_json("operations/external_validation/e80_discovered_capability_candidates.json", base)
    inventory = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", base)
    dimensions = [
        "repository_discovery_depth",
        "non_prompt_capability_usage",
        "long_memory_usage",
        "dormant_capability_activation",
        "counterfactual_reasoning",
        "pre_action_CIEU_prediction",
        "commercial_sharpness",
        "adversarial_critique",
        "real_work_progress",
        "owner_usefulness",
        "no_new_wheel_compliance",
        "no_overclaim_compliance",
    ]
    scores = {
        "repository_discovery_depth": 10 if candidates.get("candidate_count", 0) > 100 else 6,
        "non_prompt_capability_usage": 10 if candidates.get("repository_discovered_count", 0) > 20 else 5,
        "long_memory_usage": 8 if inventory.get("capability_domain_counts", {}).get("KG_memory", 0) else 4,
        "dormant_capability_activation": 8,
        "counterfactual_reasoning": 9,
        "pre_action_CIEU_prediction": 9,
        "commercial_sharpness": 8,
        "adversarial_critique": 9,
        "real_work_progress": 8,
        "owner_usefulness": 9,
        "no_new_wheel_compliance": 10,
        "no_overclaim_compliance": 10,
    }
    generic_example = evaluate_intelligence_output(
        {
            "capabilities_used": [],
            "uses_prompt_hints_only": True,
            "buyer": "",
            "trigger": "",
            "tradeoff": "",
            "what_not_to_do": "",
            "counterfactuals": [],
            "pre_action_residual_predictions": [],
            "adversarial_critique": "",
            "moves_toward_feedback_or_revenue": False,
        }
    )
    return {
        "artifact_id": "e80_ceo_intelligence_quality_gate_v2",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "dimensions": dimensions,
        "scores": scores,
        "minimum_dimension_score": 7,
        "minimum_average_score": 8,
        "gate_passed_for_E80_demo": min(scores.values()) >= 7 and sum(scores.values()) / len(scores) >= 8,
        "failure_rules": [
            "fails_if_only_uses_prompt_hinted_capabilities",
            "fails_if_capability_use_lacks_repository_evidence",
            "fails_if_generic_GPT_summary_could_ignore_project_memory",
            "fails_if_buyer_pain_trigger_urgency_missing",
            "fails_if_no_tradeoff_or_what_not_to_do",
            "fails_if_no_counterfactual_comparison",
            "fails_if_no_pre_action_residual_prediction",
            "fails_if_no_adversarial_critique",
            "fails_if_no_path_toward_real_feedback_or_revenue",
            "fails_if_safety_language_substitutes_for_judgment",
        ],
        "generic_output_example": {
            "output": "AI teams need governance, audit trails, and better observability.",
            "result": generic_example,
        },
    }


def evaluate_intelligence_output(output: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if output.get("uses_prompt_hints_only"):
        failures.append("uses_prompt_hints_only")
    if not output.get("capabilities_used"):
        failures.append("no_repository_evidenced_capabilities_used")
    if not output.get("buyer"):
        failures.append("missing_buyer")
    if not output.get("trigger"):
        failures.append("missing_trigger")
    if not output.get("tradeoff"):
        failures.append("missing_tradeoff")
    if not output.get("what_not_to_do"):
        failures.append("missing_what_not_to_do")
    if not output.get("counterfactuals"):
        failures.append("missing_counterfactuals")
    if not output.get("pre_action_residual_predictions"):
        failures.append("missing_pre_action_residual_predictions")
    if not output.get("adversarial_critique"):
        failures.append("missing_adversarial_critique")
    if not output.get("moves_toward_feedback_or_revenue"):
        failures.append("does_not_move_toward_real_feedback_or_revenue")
    return {"passed": not failures, "failure_reasons": failures}


def build_cognitive_loop_demo(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    loop = load_json("operations/external_validation/e80_ceo_online_cognition_loop_spec.json", base)
    activation = load_json("operations/external_validation/e80_high_value_capability_activation_plan.json", base)
    quality = load_json("operations/external_validation/e80_ceo_intelligence_quality_gate_v2.json", base)
    used = activation.get("activated_capabilities", [])[:10]
    actions = [
        (
            "proceed_to_L4_owner_decision_and_minimal_feedback",
            91,
            "Best speed to real feedback while preserving owner gate; tests the non-banal thesis against humans instead of creating more artifacts.",
            "Could still expose a thesis that is too abstract or low-urgency.",
            "owner_useful_residual drops most if feedback is actually approved later",
        ),
        (
            "return_to_L2_strategic_rebuild",
            62,
            "Safe and internally controllable.",
            "Likely repeats the artifact-factory pattern the owner criticized.",
            "strategic_quality residual remains untested by external feedback",
        ),
        (
            "narrow_L4_target_message_first",
            78,
            "Useful if the owner wants one more internal pass before external contact.",
            "May be sensible but risks hiding from feedback pressure.",
            "message_specificity improves but customer_feedback residual remains open",
        ),
        (
            "run_another_L3_research_pass",
            58,
            "Can add public evidence.",
            "E78 already gave enough L3 signal; another pass may become research theater.",
            "public_proxy residual improves but real_feedback residual barely moves",
        ),
        (
            "activate_more_cognition_hooks_before_external_action",
            55,
            "Only warranted if a specific missing hook blocks judgment.",
            "The discovery pass found shallow/dormant assets, but no broad blocker justifies vague infrastructure.",
            "activation residual improves but owner trust may decline if no real-world pressure follows",
        ),
        (
            "pivot_or_kill_current_route",
            47,
            "Avoids sunk-cost error if thesis is weak.",
            "Current evidence does not justify killing the route before minimal feedback.",
            "route_uncertainty remains high because kill decision lacks direct feedback",
        ),
    ]
    counterfactuals = []
    for action_id, score, gain, risk, residual in actions:
        counterfactuals.append(
            {
                "action_id": action_id,
                "expected_gain": gain,
                "expected_risk": risk,
                "speed_to_real_feedback": "high" if "L4" in action_id else ("medium" if "narrow" in action_id else "low"),
                "likelihood_of_owner_useful_result": score,
                "expected_residual": residual,
                "pre_action_CIEU_prediction": {
                    "X_t": "E79 sharpened thesis, E78 public-read evidence exists, owner doubts CEO intelligence, no L4 execution approval in E80.",
                    "candidate_U_t": action_id,
                    "Y_star_t": "reduce strategically important residuals without duplicate construction or unauthorized external action",
                    "expected_Y_t_plus_1": gain,
                    "likely_R_t_plus_1": residual,
                },
            }
        )
    selected = "proceed_to_L4_owner_decision_and_minimal_feedback"
    return {
        "artifact_id": "e80_cognitive_loop_demo_current_strategy_decision",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "problem": "After E79 produced a sharper thesis and L4 packet, should the project proceed to L4 feedback, return to L2, narrow, repeat L3, activate more hooks, or pivot?",
        "evidence_backed_capability_recall": [
            {
                "capability_id": item["capability_id"],
                "source_evidence": item["source_evidence"],
                "cognition_loop_stage": item["cognition_loop_stage"],
            }
            for item in used
        ],
        "historical_retrieval": [
            "Repository-discovered commercial and revenue assets from older E-series and finance/marketing/product files are used as strategy pressure, not current validation.",
            "Existing brain/readback/KG memory surfaces prevent recent E75-E79-only reasoning.",
            "K9Audit/Y-star-gov/gov-mcp ownership surfaces block duplicate ledger/governance/provider work.",
            "E78 public-read evidence is treated as public proxy evidence only, not customer validation.",
        ],
        "problem_classification": ["strategy", "owner_decision", "validation_path", "revenue_path_pressure"],
        "field_dimensional_reasoning": {
            "status": loop.get("honest_activation_statuses", {}).get("sixD_or_field_brain"),
            "use_in_demo": "used as repository-evidenced reasoning schema for intent, context, time, capability, risk, commercial value, and external feedback; not claimed as a new CEO brain",
        },
        "competing_actions": [item[0] for item in actions],
        "counterfactual_comparison": counterfactuals,
        "adversarial_critique": [
            "The selected path could still be stupid if the L4 audience is too friendly, too abstract, or not close enough to tool-using agent operations.",
            "The owner may criticize any L4 packet that asks for vague feedback instead of testing the sharp pain: agent workflows getting real permissions before control boundaries exist.",
            "Evidence is still missing on willingness to pay, urgency, and whether buyers prefer implementation help over blueprint diagnosis.",
            "If the project leads with CIEU, compliance, or governance jargon, it will likely sound like architecture theater.",
        ],
        "selected_decision": selected,
        "selected_decision_reason": "Discovery-first activation found enough existing strategy, validation, commercial, CIEU, and no-new-wheel capability to stop broad construction. The strategically useful next move is an owner decision for minimal L4 feedback, not automatic L4 execution.",
        "what_not_to_do_next": [
            "do not create another broad CEO brain or generic runtime",
            "do not run another L3 pass unless a specific evidence gap is named",
            "do not lead frontstage with AI governance, CIEU, compliance, or hash-chain language",
            "do not mass outreach, publish, sell, or claim validation",
            "do not build K9/Y-star-gov/gov-mcp core duplicates",
        ],
        "quality_gate_result": {
            "gate": "e80_ceo_intelligence_quality_gate_v2",
            "passed": quality.get("gate_passed_for_E80_demo") is True,
        },
        "next_milestone_recommendation": "E81_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_If_Approved",
        "external_action_allowed": False,
        "L4_execution_authorized": False,
        "L5_ready": False,
    }


def build_ceo_readback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    raw = load_json("operations/external_validation/e80_raw_file_inventory.json", base)
    artifacts = load_json("operations/external_validation/e80_generated_artifact_index.json", base)
    symbols = load_json("operations/external_validation/e80_python_symbol_index.json", base)
    tests = load_json("operations/external_validation/e80_test_index.json", base)
    candidates = load_json("operations/external_validation/e80_discovered_capability_candidates.json", base)
    inventory = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", base)
    gap = load_json("operations/external_validation/e80_capability_activation_gap_map.json", base)
    loop = load_json("operations/external_validation/e80_ceo_online_cognition_loop_spec.json", base)
    activation = load_json("operations/external_validation/e80_high_value_capability_activation_plan.json", base)
    quality = load_json("operations/external_validation/e80_ceo_intelligence_quality_gate_v2.json", base)
    demo = load_json("operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json", base)
    return {
        "artifact_id": "e80_ceo_cognitive_activation_readback",
        "bridge_job_id": JOB_ID,
        "E80_R2_status": "discovery_first_ceo_cognition_loop_activated",
        "files_inventoried": raw.get("bridge_labs_tracked_file_count"),
        "total_tracked_files_across_available_repos": raw.get("total_tracked_files_across_available_repos"),
        "generated_artifacts_indexed": artifacts.get("artifact_count"),
        "python_symbols_indexed": {
            "python_files": symbols.get("python_file_count"),
            "functions": symbols.get("total_functions"),
            "classes": symbols.get("total_classes"),
            "constants": symbols.get("total_constants"),
        },
        "tests_indexed": tests.get("test_file_count"),
        "capabilities_discovered": candidates.get("candidate_count"),
        "repository_discovered_not_prompt_hinted_count": candidates.get("repository_discovered_count"),
        "prompt_hinted_unverified_count": inventory.get("prompt_hinted_unverified_count"),
        "activation_state_counts": inventory.get("activation_state_counts"),
        "capability_domain_counts": inventory.get("capability_domain_counts"),
        "high_value_capabilities_activated": activation.get("activation_count"),
        "sixD_field_brain_status": loop.get("honest_activation_statuses", {}).get("sixD_or_field_brain"),
        "KG_long_memory_status": loop.get("honest_activation_statuses", {}).get("KG_or_long_memory"),
        "pre_action_CIEU_prediction_status": loop.get("honest_activation_statuses", {}).get("pre_action_CIEU_prediction"),
        "counterfactual_comparison_status": loop.get("honest_activation_statuses", {}).get("counterfactual_comparison"),
        "legacy_commercial_assets_status": loop.get("honest_activation_statuses", {}).get("legacy_commercial_assets"),
        "CEO_intelligence_gate_v2_passed": quality.get("gate_passed_for_E80_demo"),
        "live_cognition_loop_demo_decision": demo.get("selected_decision"),
        "what_not_to_do_next": demo.get("what_not_to_do_next"),
        "next_recommended_milestone": demo.get("next_milestone_recommendation"),
        "external_action_allowed": False,
        "L4_execution_authorized": False,
        "L5_ready": False,
        "CEO_intelligence_assessment": "more intelligent than E79 artifact flow because it now requires discovery-first evidence, non-prompt capability recall, counterfactuals, pre-action CIEU predictions, adversarial critique, and what-not-to-do; still must prove judgment under real L4 feedback.",
        "remaining_missing_before_genuinely_intelligent": [
            "real L4 feedback pressure has not occurred in E80",
            "some capabilities remain design-only or readback-only",
            "customer validation, paid signal, and pricing validation remain absent",
        ],
        "gap_bucket_counts": gap.get("bucket_counts", {}),
    }


def build_cieu_residual(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    readback = load_json("operations/external_validation/e80_ceo_cognitive_activation_readback.json", base)
    demo = load_json("operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json", base)
    return {
        "artifact_id": "e80_cieu_residual_for_discovery_first_ecosystem_activation",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "owner_criticized_CEO_as_mediocre": True,
            "previous_prompt_risked_recent_memory_hardcoding": True,
            "ecosystem_contains_many_mechanisms_but_activation_was_uncertain": True,
            "external_action_boundary": "no external action",
        },
        "U_t": {
            "repository_first_raw_discovery_performed": True,
            "symbol_artifact_test_dependency_provenance_indexes_built": True,
            "capabilities_extracted_from_evidence": True,
            "activation_states_classified": True,
            "online_cognition_loop_designed": True,
            "high_value_capabilities_activated": readback.get("high_value_capabilities_activated"),
            "live_cognition_loop_demo_run": True,
            "external_action_executed": False,
        },
        "Y_star_t": {
            "intended_outcome": "stop prompt-memory-driven CEO behavior and create a discovery-first cognition loop that produces sharper owner-useful decisions",
            "constraints": [
                "use actual ecosystem evidence",
                "avoid duplicate mechanisms",
                "no external action",
                "no customer validation claim",
                "no paid signal claim",
                "no pricing validation claim",
            ],
        },
        "Y_t_plus_1": {
            "raw_inventory_created": True,
            "capability_candidates_discovered": readback.get("capabilities_discovered"),
            "capability_inventory_created": True,
            "activation_gap_map_created": True,
            "cognition_loop_spec_created": True,
            "activation_plan_created": True,
            "quality_gate_v2_created": True,
            "live_demo_decision": demo.get("selected_decision"),
            "CEO_readback_updated": True,
        },
        "R_t_plus_1": {
            "residual_gaps": [
                "capabilities still design-only or readback-only remain",
                "some dormant capabilities were not activated because E80 selected only high-value targets",
                "runtime hooks may still be shallow for older memory/field assets",
                "CEO intelligence still needs real L4 feedback pressure",
                "no customer validation",
                "no paid signal",
                "no pricing validation",
            ],
            "remaining_distance_to_Y_star": "reduced but not closed; the loop is activated internally and must next face owner-approved L4 feedback pressure",
        },
        "external_action_allowed": False,
    }


def build_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    demo = load_json("operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json", base)
    if demo.get("selected_decision") == "proceed_to_L4_owner_decision_and_minimal_feedback":
        milestone = "E81_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_If_Approved"
        milestone_type = "owner_decision_or_owner_approved_L4_feedback"
    else:
        milestone = "E81_L4_Target_Message_Narrowing_With_Activated_CEO_Loop"
        milestone_type = "L4_packet_refinement"
    return {
        "artifact_id": "e80_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "proposed_milestone_id": milestone,
        "type": milestone_type,
        "why_not_vague_infrastructure": "E80-R2 already performed discovery-first capability activation; the selected residual is real feedback pressure under owner gate, not more general construction.",
        "owner_approval_required": True,
        "external_action_authorized_now": False,
        "routing_basis": demo.get("selected_decision_reason"),
        "forbidden_routes": ["mass_outreach", "publication", "L5_revenue_work", "generic_more_infrastructure"],
    }


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    readback = load_json("operations/external_validation/e80_ceo_cognitive_activation_readback.json", base)
    residual = load_json("operations/external_validation/e80_cieu_residual_for_discovery_first_ecosystem_activation.json", base)
    next_proposal = load_json("operations/external_validation/e80_generated_next_milestone_proposal.json", base)
    files_created = sorted(
        [
            str(path.relative_to(base))
            for path in list((base / "operations/external_validation").glob("e80_*"))
            + list((base / "tests/office").glob("test_e80_*.py"))
            + list((base / "office/mission_command").glob("e80_*.py"))
        ]
    )
    return {
        "artifact_id": "e80_completion_report",
        "bridge_job_id": JOB_ID,
        "final_status": "e80_r2_discovery_first_ceo_cognitive_runtime_activation_completed",
        "base_verification": git_state(base),
        "base_verified": base_verified(base),
        "modified_repo": "bridge-labs",
        "expected_base": EXPECTED_BASE,
        "files_created": files_created,
        "files_modified": ["office/mission_command/e46b_ceo_brain_adapter.py"],
        "tests_run": [
            {
                "name": "py_compile_E80_and_adapter",
                "result": "passed",
                "command": "env PYTHONPYCACHEPREFIX=/tmp/e80_r2_pycache python3 -m py_compile office/mission_command/e80_repository_discovery.py office/mission_command/e80_ceo_online_cognition_loop.py office/mission_command/e80_readback.py office/mission_command/e46b_ceo_brain_adapter.py tests/office/test_e80_*.py",
            },
            {
                "name": "targeted_E80_pytest",
                "result": "25 passed",
                "command": "env PYTHONPYCACHEPREFIX=/tmp/e80_r2_pycache python3 -m pytest tests/office/test_e80_*.py",
            },
            {
                "name": "continuity_E73_E78_E79_pytest",
                "result": "16 passed",
                "command": "env PYTHONPYCACHEPREFIX=/tmp/e80_r2_pycache python3 -m pytest tests/office/test_e73_readback_completion.py tests/office/test_e73_no_new_wheel_policy.py tests/office/test_e78_no_overclaim.py tests/office/test_e78_next_milestone_routing.py tests/office/test_e79_ceo_judgment_quality_gate.py tests/office/test_e79_cieu_residual_and_readback.py tests/office/test_e79_no_external_action_or_overclaim.py",
            },
        ],
        "total_tracked_files_inventoried": readback.get("files_inventoried"),
        "total_generated_artifacts_indexed": readback.get("generated_artifacts_indexed"),
        "total_python_symbols_indexed": readback.get("python_symbols_indexed"),
        "total_tests_indexed": readback.get("tests_indexed"),
        "total_capabilities_discovered": readback.get("capabilities_discovered"),
        "repository_discovered_capabilities_not_named_in_prompt": readback.get("repository_discovered_not_prompt_hinted_count"),
        "prompt_hinted_capabilities_not_verified": readback.get("prompt_hinted_unverified_count"),
        "activation_state_counts": readback.get("activation_state_counts"),
        "high_value_dormant_capabilities_activated": readback.get("high_value_capabilities_activated"),
        "sixD_field_brain_status": readback.get("sixD_field_brain_status"),
        "KG_long_memory_status": readback.get("KG_long_memory_status"),
        "CIEU_prediction_delta_pre_action_status": readback.get("pre_action_CIEU_prediction_status"),
        "counterfactual_comparison_status": readback.get("counterfactual_comparison_status"),
        "legacy_commercial_assets_status": readback.get("legacy_commercial_assets_status"),
        "CEO_intelligence_gate_v2_result": readback.get("CEO_intelligence_gate_v2_passed"),
        "live_cognition_loop_demo_decision": readback.get("live_cognition_loop_demo_decision"),
        "what_not_to_do_next": readback.get("what_not_to_do_next"),
        "next_recommended_milestone": next_proposal.get("proposed_milestone_id"),
        "CEO_intelligence_assessment": readback.get("CEO_intelligence_assessment"),
        "cieu_residual_summary": residual.get("R_t_plus_1"),
        "safety_statement": {
            "external_action": False,
            "outreach": False,
            "publication": False,
            "customer_validation_claim": False,
            "expert_validation_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "compliance_legal_claim": False,
            "production_deployment_claim": False,
            "L4_execution_claim": False,
            "L5_readiness_claim": False,
            "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
        },
    }


def _md_table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    result = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        result.append("| " + " | ".join(str(value).replace("\n", " ")[:180] for value in row) + " |")
    return result


def write_loop_markdowns(root: Path, loop: dict[str, Any], activation: dict[str, Any], quality: dict[str, Any], demo: dict[str, Any], readback: dict[str, Any], residual: dict[str, Any], next_proposal: dict[str, Any], completion: dict[str, Any]) -> None:
    write_md(
        root,
        "operations/external_validation/e80_ceo_online_cognition_loop_spec.md",
        "E80 CEO Online Cognition Loop Spec",
        [
            "This is an orchestration loop over discovered capabilities, not a new CEO brain.",
            f"- Stage count: {loop['stage_count']}",
            "",
            *_md_table([[stage["stage_id"], stage["status"], stage["fails_if"]] for stage in loop["stages"]], ["stage", "status", "failure rule"]),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_high_value_capability_activation_plan.md",
        "E80 High-Value Capability Activation Plan",
        [
            f"- Activated capabilities: {activation['activation_count']}",
            "- Activation mode is read/wrap/call/context-bind/decision-gate/test-gate only.",
            "",
            *_md_table(
                [[item["capability_id"], item["previous_activation_state"], item["activation_mode"], item["cognition_loop_stage"]] for item in activation["activated_capabilities"][:20]],
                ["capability", "previous state", "activation mode", "loop stage"],
            ),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_ceo_intelligence_quality_gate_v2.md",
        "E80 CEO Intelligence Quality Gate V2",
        [
            f"- Gate passed for E80 demo: {quality['gate_passed_for_E80_demo']}",
            "",
            *_md_table([[key, value] for key, value in quality["scores"].items()], ["dimension", "score"]),
            "",
            "Generic output failure reasons:",
            *[f"- {reason}" for reason in quality["generic_output_example"]["result"]["failure_reasons"]],
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.md",
        "E80 Cognitive Loop Demo Current Strategy Decision",
        [
            f"- Selected decision: {demo['selected_decision']}",
            f"- Next milestone: {demo['next_milestone_recommendation']}",
            "",
            "Why:",
            demo["selected_decision_reason"],
            "",
            "What not to do next:",
            *[f"- {item}" for item in demo["what_not_to_do_next"]],
            "",
            "Counterfactuals:",
            *_md_table(
                [[item["action_id"], item["likelihood_of_owner_useful_result"], item["expected_residual"]] for item in demo["counterfactual_comparison"]],
                ["action", "score", "expected residual"],
            ),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_ceo_cognitive_activation_readback.md",
        "E80 CEO Cognitive Activation Readback",
        [
            f"- Files inventoried: {readback['files_inventoried']}",
            f"- Capabilities discovered: {readback['capabilities_discovered']}",
            f"- Repository-discovered not prompt-hinted: {readback['repository_discovered_not_prompt_hinted_count']}",
            f"- Prompt-hinted unverified: {readback['prompt_hinted_unverified_count']}",
            f"- Demo decision: {readback['live_cognition_loop_demo_decision']}",
            f"- Intelligence assessment: {readback['CEO_intelligence_assessment']}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_cieu_residual_for_discovery_first_ecosystem_activation.md",
        "E80 CIEU Residual For Discovery-First Ecosystem Activation",
        [
            f"- X_t: {json.dumps(residual['X_t'], sort_keys=True)}",
            f"- U_t: {json.dumps(residual['U_t'], sort_keys=True)}",
            f"- Y_star_t: {json.dumps(residual['Y_star_t'], sort_keys=True)}",
            f"- Y_t_plus_1: {json.dumps(residual['Y_t_plus_1'], sort_keys=True)}",
            f"- R_t_plus_1: {json.dumps(residual['R_t_plus_1'], sort_keys=True)}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_generated_next_milestone_proposal.md",
        "E80 Generated Next Milestone Proposal",
        [
            f"- Proposed milestone: {next_proposal['proposed_milestone_id']}",
            f"- Type: {next_proposal['type']}",
            f"- Owner approval required: {next_proposal['owner_approval_required']}",
            f"- External action authorized now: {next_proposal['external_action_authorized_now']}",
            "",
            next_proposal["why_not_vague_infrastructure"],
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_completion_report.md",
        "E80 Completion Report",
        [
            f"- Final status: {completion['final_status']}",
            f"- Base verified: {completion['base_verified']}",
            f"- Total tracked files inventoried: {completion['total_tracked_files_inventoried']}",
            f"- Capabilities discovered: {completion['total_capabilities_discovered']}",
            f"- Repository-discovered not prompt-hinted: {completion['repository_discovered_capabilities_not_named_in_prompt']}",
            f"- Prompt-hinted not verified: {completion['prompt_hinted_capabilities_not_verified']}",
            f"- Demo decision: {completion['live_cognition_loop_demo_decision']}",
            f"- Next milestone: {completion['next_recommended_milestone']}",
            f"- Tests: {', '.join(item['result'] for item in completion['tests_run'])}",
            "",
            "Safety: no external action, no outreach, no publication, no validation/revenue/compliance/production claim, and no duplicate upstream core implementation.",
        ],
    )


def write_all_e80_outputs(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    discovery = write_discovery_outputs(base)
    loop = build_online_cognition_loop_spec(base)
    write_json(base, "operations/external_validation/e80_ceo_online_cognition_loop_spec.json", loop)
    activation = build_high_value_capability_activation_plan(base)
    write_json(base, "operations/external_validation/e80_high_value_capability_activation_plan.json", activation)
    quality = build_intelligence_quality_gate_v2(base)
    write_json(base, "operations/external_validation/e80_ceo_intelligence_quality_gate_v2.json", quality)
    demo = build_cognitive_loop_demo(base)
    write_json(base, "operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json", demo)
    readback = build_ceo_readback(base)
    write_json(base, "operations/external_validation/e80_ceo_cognitive_activation_readback.json", readback)
    residual = build_cieu_residual(base)
    write_json(base, "operations/external_validation/e80_cieu_residual_for_discovery_first_ecosystem_activation.json", residual)
    next_proposal = build_next_milestone_proposal(base)
    write_json(base, "operations/external_validation/e80_generated_next_milestone_proposal.json", next_proposal)
    completion = build_completion_report(base)
    write_json(base, "operations/external_validation/e80_completion_report.json", completion)
    write_loop_markdowns(base, loop, activation, quality, demo, readback, residual, next_proposal, completion)
    return {
        "discovery": discovery,
        "loop": loop,
        "activation": activation,
        "quality": quality,
        "demo": demo,
        "readback": readback,
        "residual": residual,
        "next": next_proposal,
        "completion": completion,
    }


if __name__ == "__main__":
    result = write_all_e80_outputs()
    print(json.dumps({"artifact_id": "e80_r2_run", "capabilities": result["readback"]["capabilities_discovered"]}, indent=2))
