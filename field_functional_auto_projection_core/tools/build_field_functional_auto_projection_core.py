#!/usr/bin/env python3
"""Build deterministic L5.2 field functional auto-projection artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "field_functional_auto_projection_core"
PROJECTION = ROOT / "mission_to_behavior_y_star_projection"
PRE_U = ROOT / "behavior_y_star_to_pre_u_candidate"
RESIDUAL = ROOT / "projection_behavior_residual_loop_fixture"
READINESS = ROOT / "field_projection_cycle_readiness"

INPUT_REFS = {
    "l5_0_summary": "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
    "l5_0_merge_plan": "field_functional_archaeology/generated/mission_projection_merge_plan.json",
    "l5_0_concept_map": "field_functional_archaeology/generated/field_functional_concept_map.json",
    "l5_0_alignment": "field_functional_archaeology/generated/old_to_new_architecture_alignment.json",
    "l5_1_contract": "mission_field_projection_contract/projection_contract_v0.json",
    "l5_1_input_fixture": "mission_field_projection_contract/projection_input_fixture.json",
    "l5_1_summary": "mission_field_projection_contract/projection_contract_summary.json",
    "l5_1_trace": "layered_y_star_projection_trace/layered_projection_trace.json",
    "l5_1_gap_map": "layered_y_star_projection_trace/unresolved_gap_map.json",
    "l5_1_pre_u_candidate": "projection_to_pre_u_packet_adapter/pre_u_packet_candidate.json",
    "l5_1_residual_delta": "projection_residual_delta_fixture/projection_residual_delta_fixture.json",
    "manual_tick_summary": "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
    "refreshed_dashboard": "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "cieu_persistence_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "candidate_auto_approval_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "behavior_execution_enabled": False,
}

LAYERS = ["mission", "company", "milestone", "session", "task", "behavior"]

STRUCTURAL_CONFIDENCE_CLASSES = [
    "direct_contract_inheritance",
    "context_bound_projection",
    "archaeology_supported_projection",
    "l5_1_harness_supported_projection",
    "policy_constrained_projection",
    "unresolved_gap",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(relative_path: str) -> dict[str, Any]:
    if relative_path not in set(INPUT_REFS.values()):
        raise ValueError(f"Refusing non-curated input: {relative_path}")
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing curated input: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def report(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def concept_status(concept_map: dict[str, Any], concept_id: str) -> dict[str, Any]:
    for concept in concept_map.get("concepts", []):
        if concept.get("concept_id") == concept_id:
            return concept
    return {"concept_id": concept_id, "current_status": "not_found", "source_assets": []}


def build_operator_contract() -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "operator_name": "Field Functional Auto-Projection Core",
        "operator_id": "field_functional_auto_projection_core_v0",
        "purpose": (
            "Deterministically project mission-level Y* through company, milestone, "
            "session, task, and behavior layers for dry-run governed preparation."
        ),
        "y_star_definition": (
            "Y* is the declared ideal/normative target state before action/behavior "
            "execution. It is not merely a prompt, not merely a plan, not merely an "
            "output summary, and not actual Y."
        ),
        "projection_layers": LAYERS,
        "input_fields": [
            "mission_y_star",
            "company_context",
            "milestone_context",
            "session_context",
            "task_context",
            "behavior_context",
            "xt_context_field",
            "agent_role_field",
            "tool_context_field",
            "governance_boundary_field",
            "risk_field",
            "residual_history_field",
            "archaeology_evidence_refs",
            "l5_1_projection_contract_refs",
        ],
        "output_fields": [
            "layered_y_star_projection",
            "mission_to_behavior_projection_trace",
            "y_star_inheritance_map",
            "y_star_contraction_map",
            "context_binding_map",
            "unresolved_projection_gap_map",
            "behavior_level_y_star_candidate",
            "pre_u_packet_candidate",
            "projection_residual_delta_fixture",
        ],
        "inheritance_rules": [
            "Every child layer inherits parent Y* obligations unless explicitly narrowed by policy.",
            "Safety constraints are invariant and cannot be removed by lower layers.",
            "Founder mission remains the controlling parent obligation for all layers.",
        ],
        "contraction_rules": [
            "A child layer may narrow scope, owner, acceptance shape, and context binding.",
            "A child layer may not authorize live behavior, external action, network, scheduler, daemon, persistence, or writeback.",
            "Unresolved or weak evidence must be emitted as a gap instead of filled by guesswork.",
        ],
        "context_binding_rules": [
            "Bind only generated/read-model evidence and committed schema/docs.",
            "Bind agent role, tool context, governance boundary, risk, and residual history as constraints.",
            "Treat Xt as a minimal safe context fixture in L5.2, not a full deep observation model.",
        ],
        "forbidden_projection_sources": [
            "raw_db_contents",
            "raw_wal_contents",
            "raw_shm_contents",
            "raw_log_contents",
            "active_agent_marker_contents",
            "unreviewed_brain_writeback",
            "unreviewed_memory_writeback",
            "live_hook_output",
            "network_fetch_result",
            "scheduler_output",
            "daemon_output",
            "raw_external_credentials",
            "raw_secrets",
            "untrusted_runtime_dump",
            "semantic_truth_scoring",
        ],
        "safety_flags": SAFETY_FLAGS,
        "non_goals": [
            "not an LLM planner",
            "not a live executor",
            "not a scheduler",
            "not network-enabled",
            "not revenue opportunity discovery",
            "not brain writeback",
            "not CIEU persistence",
        ],
        "action_alias_policy": {
            "canonical_final_layer": "behavior",
            "action_alias_allowed_only_as_downstream_reference": True,
            "action_or_tool_call_requires_future_pre_u_validation": True,
        },
        "next_required_milestone": "L5.3 Projection-Checked Autonomous Work Cycle v0",
    }


def build_policy(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.field_functional_auto_projection_core.operator_policy",
        "schema_version": "v0",
        "policy_id": "field-projection-operator-policy-v0",
        "deterministic_only": True,
        "llm_planning_enabled": False,
        "mathematical_optimality_claimed": False,
        "semantic_truth_scoring_enabled": False,
        "probabilistic_scoring_enabled": False,
        "projection_layers": contract["projection_layers"],
        "structural_confidence_classes": STRUCTURAL_CONFIDENCE_CLASSES,
        "forbidden_projection_sources": contract["forbidden_projection_sources"],
        "safety_flags": SAFETY_FLAGS,
        "behavior_layer_requires_pre_u_before_execution": True,
        "future_revenue_opportunity_discovery_enabled": False,
    }


def build_mission_input(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fixture = inputs["l5_1_input_fixture"]
    mission = fixture["mission_y_star"]
    return {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.mission_y_star_input",
        "schema_version": "v0",
        "mission_id": mission.get("mission_id", "mission-commercial-agent-company-v0"),
        "declared_mission_y_star": mission["founder_defined_mission"],
        "normative_target_state": (
            "A mission-bounded self-governed AI agent company architecture that can "
            "project Y* down to behavior candidates before any governed execution."
        ),
        "success_constraints": [
            "layered Y* projection exists from mission through behavior",
            "behavior-level Y* can become a Pre-U packet candidate",
            "residual learning remains review-gated",
        ],
        "safety_constraints": [
            "no live behavior execution",
            "no external action",
            "no network",
            "no scheduler or daemon",
            "no brain or memory writeback",
            "no CIEU persistence",
        ],
        "governance_constraints": [
            "Pre-U validation required before any behavior execution",
            "Y-star-gov remains unmodified",
            "operator approval required before future live enablement",
        ],
        "non_goals": [
            "revenue execution",
            "revenue opportunity discovery",
            "raw runtime artifact reading",
            "semantic truth scoring",
        ],
        "evidence_refs": [
            INPUT_REFS["l5_0_summary"],
            INPUT_REFS["l5_0_merge_plan"],
            INPUT_REFS["l5_1_contract"],
            INPUT_REFS["l5_1_trace"],
        ],
    }


def build_context_fixture(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dashboard = inputs["refreshed_dashboard"]
    l5_1_summary = inputs["l5_1_summary"]
    l5_0_summary = inputs["l5_0_summary"]
    return {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.context_field_fixture",
        "schema_version": "v0",
        "context_fixture_id": "field-projection-context-field-001",
        "architecture_stage_context": {
            "current_stage": "L5.2 field functional auto-projection core",
            "prior_chain": [
                "L5.0 field functional archaeology",
                "L5.1 mission field projection harness",
            ],
            "field_functional_assets_found": l5_0_summary.get("field_functional_assets_found"),
        },
        "current_milestone_context": {
            "milestone": "L5.2 Field Functional Auto-Projection Core v0",
            "purpose": "upgrade structural harness into deterministic auto-projection core",
        },
        "agent_role_context": {
            "primary_agent": "Aiden-CEO",
            "supporting_agents": ["Maya-Governance", "Ryan-Platform", "Samantha-Secretary"],
            "role_field": "mission alignment and governance-bounded projection",
        },
        "repo_context_summary": {
            "canonical_repo": "ystar-company",
            "non_company_repos_modified": False,
            "read_model_only": True,
        },
        "validation_context_summary": {
            "l5_1_projection_harness_defined": l5_1_summary.get(
                "mission_field_projection_harness_defined"
            ),
            "l5_1_action_layer_projection_only": l5_1_summary.get("action_layer_projection_only"),
            "l5_1_action_field_execution_implemented": l5_1_summary.get(
                "action_field_execution_implemented"
            ),
        },
        "governance_boundary_context": {
            "pre_u_required_before_behavior_execution": True,
            "y_star_gov_import_or_modification_allowed_now": False,
            "live_hook_output_allowed": False,
            "operator_review_required_for_live": True,
        },
        "tool_context_summary": {
            "pre_u_packet_candidate_supported": True,
            "tool_call_downstream_of_behavior_y_star": True,
            "tool_execution_enabled": False,
        },
        "residual_history_summary": {
            "l5_1_residual_fixture_available": True,
            "residuals_are_dry_run_only": True,
            "direct_learning_allowed": False,
        },
        "blocked_live_capability_summary": {
            "live_execution": "blocked",
            "external_action": "blocked",
            "scheduler": "blocked",
            "daemon": "blocked",
            "network": "blocked",
            "brain_memory_writeback": "blocked",
            "cieu_persistence": "blocked",
        },
        "future_meta_development_context": {
            "next_recommended_milestone": "L5.3 Projection-Checked Autonomous Work Cycle v0",
            "deep_xt_model_is_future_input_enhancement": True,
        },
        "future_revenue_opportunity_context_disabled": {
            "reserved_for_future": True,
            "enabled": False,
            "network_scans_enabled": False,
            "bounty_rfp_grant_market_source_scans_enabled": False,
            "reason": "L5.2 is architecture projection only, not L6 opportunity discovery.",
        },
        "safety_flags": SAFETY_FLAGS,
        "evidence_refs": [
            INPUT_REFS["refreshed_dashboard"],
            INPUT_REFS["l5_1_summary"],
            INPUT_REFS["l5_0_summary"],
        ],
    }


def build_input_fixture(mission_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.field_functional_auto_projection_core.input_fixture",
        "schema_version": "v0",
        "fixture_id": "field-projection-operator-input-001",
        "mission_y_star": mission_input,
        "company_context": context["repo_context_summary"],
        "milestone_context": context["current_milestone_context"],
        "session_context": {
            "session_purpose": "generate deterministic L5.2 field projection artifacts",
            "manual_local_dry_run_only": True,
        },
        "task_context": {
            "task_purpose": "produce mission-to-behavior Y* and downstream dry-run fixtures",
            "testable_artifacts_required": True,
        },
        "behavior_context": {
            "behavior_intent": "prepare a projection-checked autonomous work-cycle candidate",
            "behavior_execution_enabled": False,
        },
        "xt_context_field": {
            "source_kind": "minimal_safe_generated_context_fixture",
            "deep_xt_model_implemented": False,
            "summary": "L5.2 uses bounded generated context only; deep Xt remains future input work.",
        },
        "agent_role_field": context["agent_role_context"],
        "tool_context_field": context["tool_context_summary"],
        "governance_boundary_field": context["governance_boundary_context"],
        "risk_field": context["blocked_live_capability_summary"],
        "residual_history_field": context["residual_history_summary"],
        "archaeology_evidence_refs": [
            INPUT_REFS["l5_0_summary"],
            INPUT_REFS["l5_0_merge_plan"],
            INPUT_REFS["l5_0_concept_map"],
            INPUT_REFS["l5_0_alignment"],
        ],
        "l5_1_projection_contract_refs": [
            INPUT_REFS["l5_1_contract"],
            INPUT_REFS["l5_1_summary"],
            INPUT_REFS["l5_1_trace"],
            INPUT_REFS["l5_1_gap_map"],
        ],
        "safety_flags": SAFETY_FLAGS,
    }


def layer_payload(
    layer_name: str,
    parent_layer: str | None,
    parent_ref: str | None,
    projected_y_star: dict[str, Any],
    inherited: list[str],
    contracted: list[str],
    bound: list[str],
    non_goals: list[str],
    forbidden: list[str],
    validation: list[str],
    gaps: list[str],
    evidence: list[str],
    confidence: str,
) -> dict[str, Any]:
    return {
        "layer_name": layer_name,
        "parent_layer": parent_layer,
        "parent_y_star_ref": parent_ref,
        "projected_y_star": projected_y_star,
        "inherited_obligations": inherited,
        "contracted_obligations": contracted,
        "context_bound_obligations": bound,
        "explicit_non_goals": non_goals,
        "forbidden_behaviors": forbidden,
        "required_validation_before_execution": validation,
        "unresolved_gaps": gaps,
        "evidence_refs": evidence,
        "structural_confidence_class": confidence,
        "safety_flags": SAFETY_FLAGS,
    }


def build_layer_artifacts(
    mission_input: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    base_forbidden = [
        "live behavior execution",
        "external communication",
        "network access",
        "scheduler or daemon activation",
        "brain or memory writeback",
        "CIEU persistence",
        "candidate auto-approval",
    ]
    mission_ref = rel(PROJECTION / "mission_y_star_input.json")
    company = layer_payload(
        "company",
        "mission",
        mission_ref,
        {
            "y_star_id": "company-y-star-field-projection-v0",
            "declared_y_star": "Company should advance field-functional projection capability through governed dry-run artifacts.",
            "normative_target_state": "ystar-company can project mission Y* into behavior Y* without live execution.",
        },
        mission_input["success_constraints"] + mission_input["safety_constraints"],
        ["company scope is limited to ystar-company architecture and generated/read-model evidence"],
        ["repo_context_summary", "governance_boundary_context"],
        mission_input["non_goals"],
        base_forbidden,
        ["static validator", "local safety wrapper", "pytest"],
        ["deep Xt remains future input model"],
        [INPUT_REFS["l5_0_summary"], INPUT_REFS["l5_1_summary"]],
        "archaeology_supported_projection",
    )
    milestone = layer_payload(
        "milestone",
        "company",
        rel(PROJECTION / "mission_to_company_y_star.json"),
        {
            "y_star_id": "milestone-y-star-l5-2-v0",
            "declared_y_star": "L5.2 should define the deterministic auto-projection operator and generate behavior-level Y*.",
            "normative_target_state": "field functional moves from structural harness to deterministic projection core.",
        },
        company["inherited_obligations"] + company["contracted_obligations"],
        ["milestone must end at behavior layer, not action layer"],
        ["current_milestone_context", "L5.1 projection contract refs"],
        ["production Pre-U adapter", "live behavior execution", "L6 revenue discovery"],
        base_forbidden,
        ["L5.2 artifact tests", "read-model integration"],
        ["behavior execution remains future work"],
        [INPUT_REFS["l5_1_contract"], INPUT_REFS["l5_1_trace"]],
        "l5_1_harness_supported_projection",
    )
    session = layer_payload(
        "session",
        "milestone",
        rel(PROJECTION / "company_to_milestone_y_star.json"),
        {
            "y_star_id": "session-y-star-l5-2-build-v0",
            "declared_y_star": "This build session should create deterministic L5.2 artifacts and tests only.",
            "normative_target_state": "session output is inspectable, schema-like, and dry-run safe.",
        },
        milestone["inherited_obligations"] + milestone["contracted_obligations"],
        ["session scope is one local deterministic build, not recurring execution"],
        ["session_context", "agent_role_context"],
        ["daemon use", "scheduler use", "network use"],
        base_forbidden,
        ["py_compile", "JSON validation", "targeted pytest"],
        ["full deep Xt not implemented in this session"],
        [INPUT_REFS["manual_tick_summary"], INPUT_REFS["l5_1_summary"]],
        "context_bound_projection",
    )
    task = layer_payload(
        "task",
        "session",
        rel(PROJECTION / "milestone_to_session_y_star.json"),
        {
            "y_star_id": "task-y-star-l5-2-artifacts-v0",
            "declared_y_star": "Task should emit operator, projection, Pre-U candidate, residual loop, readiness, console, and test artifacts.",
            "normative_target_state": "all L5.2 artifacts exist, parse, and preserve blocked safety boundaries.",
        },
        session["inherited_obligations"] + session["contracted_obligations"],
        ["task completion is measured by deterministic artifacts and validators"],
        ["task_context", "validation_context_summary"],
        ["semantic truth scoring", "probabilistic scoring", "runtime artifact reads"],
        base_forbidden,
        ["new L5.2 tests", "existing L5.0/L5.1 tests"],
        ["production validator integration remains unresolved"],
        [INPUT_REFS["l5_0_merge_plan"], INPUT_REFS["l5_1_gap_map"]],
        "policy_constrained_projection",
    )
    behavior = layer_payload(
        "behavior",
        "task",
        rel(PROJECTION / "session_to_task_y_star.json"),
        {
            "y_star_id": "behavior-y-star-projection-checked-cycle-v0",
            "declared_y_star": "Prepare a projection-checked autonomous work-cycle candidate for future Pre-U validation.",
            "normative_target_state": "behavior candidate is explicit, bounded, and eligible only for Pre-U packet candidate generation.",
        },
        task["inherited_obligations"] + task["contracted_obligations"],
        ["behavior is projection-only and cannot execute directly"],
        ["behavior_context", "governance_boundary_context", "risk_field"],
        ["direct execution", "brain writeback", "memory ingestion", "candidate auto-approval"],
        base_forbidden + ["direct behavior execution"],
        ["future Pre-U validation", "future Y-star-gov decision", "operator review before live enablement"],
        [
            "action/tool execution downstream remains unimplemented",
            "actual Y cannot be measured without execution",
        ],
        [INPUT_REFS["l5_1_pre_u_candidate"], INPUT_REFS["l5_1_residual_delta"]],
        "policy_constrained_projection",
    )
    return {
        "mission_to_company_y_star.json": company,
        "company_to_milestone_y_star.json": milestone,
        "milestone_to_session_y_star.json": session,
        "session_to_task_y_star.json": task,
        "task_to_behavior_y_star.json": behavior,
    }


def build_behavior_candidate(
    mission_input: dict[str, Any],
    behavior_layer: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.behavior_candidate",
        "schema_version": "v0",
        "behavior_y_star_id": "behavior-y-star-projection-checked-cycle-v0",
        "source_mission_y_star_id": mission_input["mission_id"],
        "behavior_intent": "prepare next autonomous work cycle candidate through field-functional projection and Pre-U validation",
        "declared_behavior_y_star": behavior_layer["projected_y_star"]["declared_y_star"],
        "required_pre_u_validation": True,
        "allowed_behavior_boundary": [
            "local dry-run artifact generation",
            "read-model observation",
            "Pre-U packet candidate preparation",
            "review-queue-only learning stub",
        ],
        "forbidden_behavior_boundary": behavior_layer["forbidden_behaviors"],
        "candidate_u_summary": {
            "candidate_u_id": "candidate-u-projection-checked-cycle-v0",
            "candidate_u": "route projected behavior Y* into a dry-run Pre-U packet candidate",
            "execution_mode": "projection_only",
        },
        "expected_y_if_allowed": "A future validator could inspect behavior Y* and approve only governed local dry-run continuation.",
        "expected_residual_if_blocked": "Residual should record missing production Pre-U validation and absent live behavior executor.",
        "execution_status": "projection_only",
        "live_behavior_authorized": False,
        "behavior_execution_enabled": False,
        "eligible_for_pre_u_packet_candidate": True,
        "eligible_for_direct_execution": False,
        "eligible_for_brain_writeback": False,
        "eligible_for_memory_ingestion": False,
        "evidence_refs": behavior_layer["evidence_refs"],
        "unresolved_gaps": behavior_layer["unresolved_gaps"],
        "safety_flags": SAFETY_FLAGS,
    }


def build_maps(layers: dict[str, dict[str, Any]], context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    ordered_files = [
        ("mission", "mission_y_star_input.json"),
        ("company", "mission_to_company_y_star.json"),
        ("milestone", "company_to_milestone_y_star.json"),
        ("session", "milestone_to_session_y_star.json"),
        ("task", "session_to_task_y_star.json"),
        ("behavior", "task_to_behavior_y_star.json"),
    ]
    inheritance = {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.inheritance_map",
        "schema_version": "v0",
        "map_id": "y-star-inheritance-map-l5-2",
        "inheritance_edges": [
            {
                "parent_layer": ordered_files[index - 1][0],
                "child_layer": ordered_files[index][0],
                "parent_ref": rel(PROJECTION / ordered_files[index - 1][1]),
                "child_ref": rel(PROJECTION / ordered_files[index][1]),
                "inherited_obligations": layers[ordered_files[index][1]]["inherited_obligations"]
                if index > 1
                else ["mission success constraints", "mission safety constraints"],
            }
            for index in range(1, len(ordered_files))
        ],
        "safety_flags_inherited_without_relaxation": SAFETY_FLAGS,
    }
    contraction = {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.contraction_map",
        "schema_version": "v0",
        "map_id": "y-star-contraction-map-l5-2",
        "contractions": [
            {
                "layer": layer_name,
                "artifact_ref": rel(PROJECTION / file_name),
                "contracted_obligations": layers[file_name]["contracted_obligations"],
                "contraction_rule": "narrow scope without relaxing safety flags",
            }
            for layer_name, file_name in ordered_files[1:]
        ],
    }
    binding = {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.context_binding_map",
        "schema_version": "v0",
        "map_id": "context-binding-map-l5-2",
        "bindings": [
            {"context_field": key, "bound_to_projection": True, "source_kind": "generated_fixture"}
            for key in [
                "architecture_stage_context",
                "current_milestone_context",
                "agent_role_context",
                "repo_context_summary",
                "validation_context_summary",
                "governance_boundary_context",
                "tool_context_summary",
                "residual_history_summary",
                "blocked_live_capability_summary",
                "future_meta_development_context",
                "future_revenue_opportunity_context_disabled",
            ]
        ],
        "future_revenue_opportunity_context_enabled": context[
            "future_revenue_opportunity_context_disabled"
        ]["enabled"],
    }
    gaps = {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.unresolved_gap_map",
        "schema_version": "v0",
        "gap_map_id": "unresolved-projection-gap-map-l5-2",
        "gaps": [
            {
                "gap_id": "gap-deep-xt-input-model",
                "gap_type": "context_gap",
                "description": "Xt is still a minimal safe fixture, not a deep observation model.",
                "blocks_l5_2_completion": False,
            },
            {
                "gap_id": "gap-production-pre-u-validation",
                "gap_type": "pre_u_gap",
                "description": "Pre-U packet is candidate-only and not sent to Y-star-gov.",
                "blocks_l5_2_completion": False,
            },
            {
                "gap_id": "gap-behavior-execution",
                "gap_type": "behavior_boundary_gap",
                "description": "Behavior execution is disabled and no live action executor is implemented.",
                "blocks_l5_2_completion": False,
            },
            {
                "gap_id": "gap-review-gated-learning-queue",
                "gap_type": "learning_gap",
                "description": "Learning candidate is a stub only and requires future review workflow.",
                "blocks_l5_2_completion": False,
            },
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    return inheritance, contraction, binding, gaps


def build_trace(layers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    transitions = [
        ("mission", "company", "mission_y_star_input.json", "mission_to_company_y_star.json"),
        ("company", "milestone", "mission_to_company_y_star.json", "company_to_milestone_y_star.json"),
        ("milestone", "session", "company_to_milestone_y_star.json", "milestone_to_session_y_star.json"),
        ("session", "task", "milestone_to_session_y_star.json", "session_to_task_y_star.json"),
        ("task", "behavior", "session_to_task_y_star.json", "task_to_behavior_y_star.json"),
    ]
    return {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.trace",
        "schema_version": "v0",
        "trace_id": "mission-to-behavior-projection-trace-l5-2",
        "projection_layers": LAYERS,
        "transitions": [
            {
                "from_layer": parent,
                "to_layer": child,
                "parent_ref": rel(PROJECTION / parent_file),
                "child_ref": rel(PROJECTION / child_file),
                "derivation_rule": (
                    "inherit parent Y*, contract to child context, bind constraints, "
                    "preserve forbidden boundaries, emit gaps"
                ),
                "structural_confidence_class": layers[child_file]["structural_confidence_class"],
                "evidence_refs": layers[child_file]["evidence_refs"],
            }
            for parent, child, parent_file, child_file in transitions
        ],
        "semantic_truth_scoring_enabled": False,
        "probabilistic_scoring_enabled": False,
        "behavior_execution_enabled": False,
    }


def build_pre_u_candidate(
    behavior_candidate: dict[str, Any],
    context: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    mapping = {
        "schema_name": "ystar.behavior_y_star_to_pre_u_candidate.mapping",
        "schema_version": "v0",
        "mapping_id": "behavior-y-star-to-pre-u-mapping-l5-2",
        "field_mappings": [
            {
                "from": "behavior_level_y_star_candidate.declared_behavior_y_star",
                "to": "declared_Y_star",
                "status": "mapped",
            },
            {"from": "projection_context_field_fixture", "to": "Xt", "status": "mapped"},
            {
                "from": "behavior_level_y_star_candidate.candidate_u_summary",
                "to": "candidate_U",
                "status": "mapped",
            },
            {
                "from": "governance_boundary_context",
                "to": "governance_expectations",
                "status": "mapped",
            },
            {
                "from": "y_star_inheritance_map / contraction_map",
                "to": "projection_trace_refs",
                "status": "mapped",
            },
            {
                "from": "forbidden_behavior_boundary",
                "to": "deny / boundary constraints",
                "status": "mapped",
            },
            {
                "from": "required_pre_u_validation",
                "to": "validation_required",
                "status": "mapped",
            },
            {"from": "safety_flags", "to": "execution_boundary", "status": "mapped"},
        ],
        "y_star_gov_imported": False,
        "y_star_gov_modified": False,
        "live_hooks_called": False,
    }
    packet = {
        "schema_name": "ystar.behavior_y_star_to_pre_u_candidate.packet_candidate",
        "schema_version": "v0",
        "packet_id": "pre-u-candidate-from-behavior-y-star-l5-2",
        "dry_run_only": True,
        "production_ready": False,
        "requires_y_star_gov_validation_before_execution": True,
        "live_execution_authorized": False,
        "external_action_authorized": False,
        "declared_Y_star": behavior_candidate["declared_behavior_y_star"],
        "Xt": context,
        "candidate_U": behavior_candidate["candidate_u_summary"],
        "governance_expectations": context["governance_boundary_context"],
        "projection_trace_refs": [
            rel(PROJECTION / "mission_to_behavior_projection_trace.json"),
            rel(PROJECTION / "y_star_inheritance_map.json"),
            rel(PROJECTION / "y_star_contraction_map.json"),
        ],
        "deny_boundary_constraints": behavior_candidate["forbidden_behavior_boundary"],
        "validation_required": behavior_candidate["required_pre_u_validation"],
        "execution_boundary": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.behavior_y_star_to_pre_u_candidate.summary",
        "schema_version": "v0",
        "behavior_to_pre_u_mapping_defined": True,
        "pre_u_packet_candidate_from_behavior_y_star_generated": True,
        "dry_run_only": True,
        "production_ready": False,
        "requires_y_star_gov_validation_before_execution": True,
        "live_execution_authorized": False,
        "external_action_authorized": False,
        "y_star_gov_imported": False,
        "y_star_gov_modified": False,
        **SAFETY_FLAGS,
    }
    return mapping, packet, summary


def build_residual_loop(
    behavior_candidate: dict[str, Any],
    pre_u_summary: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    expected = {
        "schema_name": "ystar.projection_behavior_residual_loop_fixture.expected_outcome",
        "schema_version": "v0",
        "expected_outcome_id": "projected-behavior-expected-outcome-l5-2",
        "derived_from_behavior_y_star_ref": rel(PROJECTION / "behavior_level_y_star_candidate.json"),
        "expected_behavior_result": "Pre-U packet candidate is generated from behavior Y* and remains blocked from execution.",
        "expected_safety_state": SAFETY_FLAGS,
    }
    actual = {
        "schema_name": "ystar.projection_behavior_residual_loop_fixture.mock_actual_outcome",
        "schema_version": "v0",
        "mock_actual_outcome_id": "mock-behavior-actual-outcome-l5-2",
        "synthetic_dry_run_only": True,
        "real_behavior_executed": False,
        "actual_behavior_result": "No behavior executed; dry-run artifacts were generated for review only.",
        "live_execution_enabled": False,
        "external_action_enabled": False,
    }
    delta = {
        "schema_name": "ystar.projection_behavior_residual_loop_fixture.residual_delta",
        "schema_version": "v0",
        "delta_id": "behavior-projection-residual-delta-l5-2",
        "no_execution_residual": "Actual Y cannot be measured because no behavior execution occurred.",
        "projection_gap": ["behavior Y* is deterministic but not validated by production governance"],
        "context_gap": ["Xt is minimal safe fixture, not deep observation model"],
        "pre_u_gap": ["packet candidate was not sent to Y-star-gov"],
        "behavior_boundary_gap": ["behavior execution remains disabled"],
        "evidence_gap": ["action-field direct execution evidence remains weak from L5.0"],
        "learning_gap": ["learning candidate is stub-only until review queue milestone"],
        "real_behavior_executed": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
    }
    learning = {
        "schema_name": "ystar.projection_behavior_residual_loop_fixture.learning_candidate_stub",
        "schema_version": "v0",
        "learning_candidate_id": "projection-learning-candidate-stub-l5-2",
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "requires_human_or_governance_review": True,
        "learning_target": "projection_policy_only",
        "live_learning_enabled": False,
        "approved": False,
        "evidence_refs": [
            rel(PROJECTION / "behavior_level_y_star_candidate.json"),
            rel(PRE_U / "pre_u_packet_candidate_from_behavior_y_star.json"),
            rel(RESIDUAL / "behavior_projection_residual_delta.json"),
        ],
    }
    summary = {
        "schema_name": "ystar.projection_behavior_residual_loop_fixture.summary",
        "schema_version": "v0",
        "residual_delta_loop_fixture_generated": True,
        "projected_behavior_expected_outcome_generated": True,
        "mock_behavior_actual_outcome_generated": True,
        "behavior_projection_residual_delta_generated": True,
        "projection_learning_candidate_stub_generated": True,
        "learning_candidate_stub_generated_but_not_approved": True,
        "real_behavior_executed": False,
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "pre_u_packet_candidate_generated": pre_u_summary[
            "pre_u_packet_candidate_from_behavior_y_star_generated"
        ],
        **SAFETY_FLAGS,
    }
    return expected, actual, delta, learning, summary


def build_readiness(
    operator_summary: dict[str, Any],
    projection_summary: dict[str, Any],
    pre_u_summary: dict[str, Any],
    residual_summary: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    dry_run_ready = all(
        [
            projection_summary["mission_y_star_defined"],
            operator_summary["projection_operator_defined"],
            projection_summary["mission_to_behavior_trace_generated"],
            projection_summary["behavior_level_y_star_candidate_generated"],
            pre_u_summary["pre_u_packet_candidate_from_behavior_y_star_generated"],
            residual_summary["residual_delta_loop_fixture_generated"],
            residual_summary["projection_learning_candidate_stub_generated"],
            not any(SAFETY_FLAGS.values()),
        ]
    )
    readiness = {
        "schema_name": "ystar.field_projection_cycle_readiness.readiness",
        "schema_version": "v0",
        "mission_y_star_defined": projection_summary["mission_y_star_defined"],
        "projection_operator_defined": operator_summary["projection_operator_defined"],
        "mission_to_behavior_trace_generated": projection_summary[
            "mission_to_behavior_trace_generated"
        ],
        "behavior_level_y_star_candidate_generated": projection_summary[
            "behavior_level_y_star_candidate_generated"
        ],
        "pre_u_packet_candidate_generated": pre_u_summary[
            "pre_u_packet_candidate_from_behavior_y_star_generated"
        ],
        "residual_delta_fixture_generated": residual_summary[
            "residual_delta_loop_fixture_generated"
        ],
        "learning_candidate_stub_generated": residual_summary[
            "projection_learning_candidate_stub_generated"
        ],
        "live_execution_still_blocked": True,
        "writeback_still_blocked": True,
        "external_action_still_blocked": True,
        "ready_for_l5_3_projection_checked_autonomous_cycle": dry_run_ready,
        "next_required_milestone": "L5.3 Projection-Checked Autonomous Work Cycle v0",
        **SAFETY_FLAGS,
    }
    next_step = {
        "schema_name": "ystar.field_projection_cycle_readiness.l5_3_recommended_next_step",
        "schema_version": "v0",
        "recommended_next_step_id": "l5-3-projection-checked-autonomous-work-cycle",
        "title": "L5.3 Projection-Checked Autonomous Work Cycle v0",
        "reason": "L5.2 can project mission Y* to behavior Y* and produce dry-run Pre-U and residual fixtures.",
        "requires_y_star_gov": True,
        "requires_operator_approval": False,
        "live_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "depends_on": [
            rel(CORE / "field_projection_operator_contract.json"),
            rel(PROJECTION / "behavior_level_y_star_candidate.json"),
            rel(PRE_U / "pre_u_packet_candidate_from_behavior_y_star.json"),
            rel(READINESS / "field_projection_cycle_readiness.json"),
        ],
    }
    return readiness, next_step


def build() -> None:
    inputs = {name: load_json(path) for name, path in INPUT_REFS.items()}
    contract = build_operator_contract()
    policy = build_policy(contract)
    mission_input = build_mission_input(inputs)
    context = build_context_fixture(inputs)
    input_fixture = build_input_fixture(mission_input, context)
    layers = build_layer_artifacts(mission_input, context)
    inheritance, contraction, binding, gaps = build_maps(layers, context)
    trace = build_trace(layers)
    behavior_candidate = build_behavior_candidate(mission_input, layers["task_to_behavior_y_star.json"])
    pre_u_mapping, pre_u_packet, pre_u_summary = build_pre_u_candidate(behavior_candidate, context)
    expected, actual, delta, learning, residual_summary = build_residual_loop(
        behavior_candidate, pre_u_summary
    )
    projection_summary = {
        "schema_name": "ystar.mission_to_behavior_y_star_projection.summary",
        "schema_version": "v0",
        "mission_y_star_defined": True,
        "projection_context_field_fixture_defined": True,
        "mission_to_behavior_trace_generated": True,
        "projection_layers": LAYERS,
        "behavior_level_y_star_candidate_generated": True,
        "future_revenue_opportunity_context_disabled": True,
        "semantic_truth_scoring_enabled": False,
        "behavior_execution_enabled": False,
        **SAFETY_FLAGS,
    }
    operator_summary = {
        "schema_name": "ystar.field_functional_auto_projection_core.operator_summary",
        "schema_version": "v0",
        "field_functional_auto_projection_core_defined": True,
        "projection_operator_defined": True,
        "field_projection_operator_contract_defined": True,
        "field_projection_input_fixture_defined": True,
        "field_projection_algorithm_defined": True,
        "projection_layers": LAYERS,
        "behavior_final_layer_used": True,
        "action_layer_canonical": False,
        "l6_revenue_opportunity_discovery_enabled": False,
        "next_required_milestone": "L5.3 Projection-Checked Autonomous Work Cycle v0",
        **SAFETY_FLAGS,
    }
    readiness, next_step = build_readiness(
        operator_summary, projection_summary, pre_u_summary, residual_summary
    )

    write_text(
        CORE / "README.md",
        report(
            "Field Functional Auto-Projection Core",
            [
                "L5.2 upgrades the L5.1 structural harness into a deterministic mission-to-behavior Y* projection core.",
                "Behavior is the canonical final layer. Action/tool execution is downstream and remains blocked until future Pre-U validation.",
                "The core reads only curated generated/read-model JSON and emits dry-run artifacts.",
            ],
        ),
    )
    write_json(CORE / "field_projection_operator_contract.json", contract)
    write_json(CORE / "field_projection_operator_policy.json", policy)
    write_json(CORE / "field_projection_input_fixture.json", input_fixture)
    write_text(
        CORE / "field_projection_algorithm_v0.md",
        report(
            "Field Projection Algorithm v0",
            [
                "For each layer transition:",
                "1. inherit parent Y* obligations",
                "2. identify layer-specific context",
                "3. contract or narrow obligations based on current context",
                "4. bind concrete constraints",
                "5. preserve forbidden boundaries",
                "6. emit unresolved gaps instead of guessing",
                "7. produce child Y*",
                "8. record trace refs and evidence refs",
                "",
                "This algorithm makes no mathematical optimality claim, uses no probabilistic scoring, and performs no semantic truth scoring.",
            ],
        ),
    )
    write_json(CORE / "field_projection_operator_summary.json", operator_summary)
    write_text(
        CORE / "field_projection_operator_report.md",
        report(
            "Field Projection Operator Report",
            [
                "- Projection layers: " + ", ".join(LAYERS),
                "- Final canonical layer: behavior",
                "- Safety flags remain false, including behavior execution.",
                "- L6 revenue opportunity discovery is reserved but disabled.",
            ],
        ),
    )

    write_json(PROJECTION / "mission_y_star_input.json", mission_input)
    write_json(PROJECTION / "projection_context_field_fixture.json", context)
    for file_name, payload in layers.items():
        write_json(PROJECTION / file_name, payload)
    write_json(PROJECTION / "mission_to_behavior_projection_trace.json", trace)
    write_json(PROJECTION / "y_star_inheritance_map.json", inheritance)
    write_json(PROJECTION / "y_star_contraction_map.json", contraction)
    write_json(PROJECTION / "context_binding_map.json", binding)
    write_json(PROJECTION / "unresolved_projection_gap_map.json", gaps)
    write_json(PROJECTION / "behavior_level_y_star_candidate.json", behavior_candidate)
    write_json(PROJECTION / "mission_to_behavior_projection_summary.json", projection_summary)
    write_text(
        PROJECTION / "mission_to_behavior_projection_report.md",
        report(
            "Mission to Behavior Projection Report",
            [
                "- Generated mission, company, milestone, session, task, and behavior Y* artifacts.",
                "- Behavior-level Y* is eligible for Pre-U packet candidate generation only.",
                "- Future revenue opportunity context is present only as disabled future context.",
            ],
        ),
    )

    write_json(PRE_U / "behavior_to_pre_u_mapping.json", pre_u_mapping)
    write_json(PRE_U / "pre_u_packet_candidate_from_behavior_y_star.json", pre_u_packet)
    write_text(
        PRE_U / "pre_u_candidate_gap_report.md",
        report(
            "Pre-U Candidate Gap Report",
            [
                "- Candidate is dry-run only and not production-ready.",
                "- Y-star-gov is not imported, modified, or called.",
                "- Required future gaps: production validator decision, governed behavior executor, live residual measurement.",
            ],
        ),
    )
    write_json(PRE_U / "pre_u_candidate_summary.json", pre_u_summary)

    write_json(RESIDUAL / "projected_behavior_expected_outcome.json", expected)
    write_json(RESIDUAL / "mock_behavior_actual_outcome.json", actual)
    write_json(RESIDUAL / "behavior_projection_residual_delta.json", delta)
    write_json(RESIDUAL / "projection_learning_candidate_stub.json", learning)
    write_json(RESIDUAL / "projection_residual_loop_summary.json", residual_summary)
    write_text(
        RESIDUAL / "projection_residual_loop_report.md",
        report(
            "Projection Behavior Residual Loop Report",
            [
                "- Expected outcome is derived from behavior-level Y*.",
                "- Mock actual outcome is synthetic dry-run only.",
                "- Learning candidate is eligible for review queue only and is not approved.",
            ],
        ),
    )

    write_json(READINESS / "field_projection_cycle_readiness.json", readiness)
    write_text(
        READINESS / "field_projection_cycle_readiness.md",
        report(
            "Field Projection Cycle Readiness",
            [
                f"- Ready for L5.3 projection-checked autonomous cycle: {readiness['ready_for_l5_3_projection_checked_autonomous_cycle']}",
                "- Live execution, writeback, persistence, scheduler, daemon, network, and behavior execution remain blocked.",
                "- Proceed only to a projection-checked autonomous work cycle, not live execution.",
            ],
        ),
    )
    write_json(READINESS / "l5_3_recommended_next_step.json", next_step)


def main() -> int:
    build()
    print("Built L5.2 field functional auto-projection core artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
