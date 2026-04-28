#!/usr/bin/env python3
"""Build deterministic L5.1 mission field projection harness artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PACK = ROOT / "mission_field_projection_contract"
TRACE_PACK = ROOT / "layered_y_star_projection_trace"
ADAPTER_PACK = ROOT / "projection_to_pre_u_packet_adapter"
RESIDUAL_PACK = ROOT / "projection_residual_delta_fixture"

INPUT_REFS = {
    "archaeology_summary": "field_functional_archaeology/generated/field_functional_archaeology_summary.json",
    "merge_plan": "field_functional_archaeology/generated/mission_projection_merge_plan.json",
    "concept_map": "field_functional_archaeology/generated/field_functional_concept_map.json",
    "old_to_new_alignment": "field_functional_archaeology/generated/old_to_new_architecture_alignment.json",
    "refreshed_dashboard": "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
    "company_state_digest": "governed_observation_loop/generated/company_state_digest.json",
    "manual_tick_summary": "manual_recurring_observation_tick_runner/generated/manual_tick_runner_readiness_summary.json",
    "console_snapshot": "console_read_model/generated/team_console_snapshot.json",
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
}

LAYER_NAMES = ["mission", "company", "milestone", "session", "task", "action"]


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


def concept_lookup(concept_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {concept.get("concept_id"): concept for concept in concept_map.get("concepts", [])}


def alignment_for(alignment: dict[str, Any], new_layer: str) -> list[dict[str, Any]]:
    return [
        item
        for item in alignment.get("mappings", [])
        if item.get("new_layer") == new_layer
    ]


def evidence_ref(name: str) -> str:
    return INPUT_REFS[name]


def build_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_field_projection_contract.projection_contract",
        "schema_version": "v0",
        "contract_id": "mission_field_projection_contract_v0",
        "contract_name": "Mission Field Functional Projection Contract",
        "supported_projection_layers": LAYER_NAMES,
        "allowed_input_fields": [
            "mission_y_star",
            "xt_observation_summary",
            "agent_role",
            "tool_context",
            "risk_boundary",
            "residual_history_summary",
            "governance_policy_summary",
            "archaeology_evidence_refs",
        ],
        "forbidden_inputs": [
            "raw DB contents",
            "raw WAL/SHM",
            "raw logs",
            "raw active-agent marker contents",
            "unreviewed brain writeback",
            "network results",
            "live hook output",
        ],
        "safety_flags": SAFETY_FLAGS,
        "output_requirements": [
            "layered_y_star_projection",
            "projection_trace",
            "field_source_map",
            "contraction_map",
            "unresolved_gap_map",
            "pre_u_adapter_candidate",
            "residual_delta_fixture_candidate",
        ],
        "structural_confidence_classes": [
            "direct_archaeology_reuse",
            "wrapped_archaeology_asset",
            "deterministic_policy_projection",
            "concept_reference_only",
            "unresolved_gap",
        ],
        "action_field_execution_status": "not_implemented",
        "action_layer_policy": {
            "projection_only": True,
            "live_action_authorized": False,
            "requires_pre_u_validation": True,
            "notes": "L5.0 found weak direct action-field evidence, so action-level Y* is only a contract projection for future Pre-U validation.",
        },
        "requires_y_star_gov_for_future_validation": True,
        "calls_y_star_gov_now": False,
        "uses_generated_read_model_only": True,
        "next_required_milestone": "L5.2 Field Functional Auto-Projection Core v0",
    }


def build_input_fixture(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dashboard = inputs["refreshed_dashboard"]
    digest = inputs["company_state_digest"]
    archaeology_summary = inputs["archaeology_summary"]
    merge_plan = inputs["merge_plan"]
    return {
        "schema_name": "ystar.mission_field_projection_contract.projection_input_fixture",
        "schema_version": "v0",
        "fixture_id": "mission-field-projection-input-001",
        "mission_y_star": {
            "mission_id": dashboard.get("mission_id", "mission-commercial-agent-company-v0"),
            "founder_defined_mission": dashboard.get("mission_summary"),
            "desired_state": "mission-bounded autonomous company advances through governed local dry-run capabilities before live enablement.",
            "non_goals": [
                "no live execution",
                "no external action",
                "no direct memory or brain writeback",
            ],
        },
        "xt_observation_summary": {
            "source_kind": "generated_read_model_summary",
            "current_phase": dashboard.get("current_phase"),
            "company_operating_state": dashboard.get("company_operating_state"),
            "known_capabilities": digest.get("what_the_company_knows_now", []),
            "safe_observations": digest.get("what_it_can_safely_observe", []),
            "blocked_actions": dashboard.get("blocked_actions", digest.get("what_remains_blocked", [])),
        },
        "agent_role": {
            "primary_agent": "Aiden-CEO",
            "supporting_agents": ["Maya-Governance", "Ryan-Platform", "Samantha-Secretary"],
            "role_scope": "select mission-aligned next work only through governed local dry-run channels",
        },
        "tool_context": {
            "candidate_action_context": "prepare a Pre-U packet candidate from action-level projection without invoking a live validator",
            "existing_tool_chain": [
                "governed_readonly_observation_tool_v0",
                "governed_tool_invocation_bridge_v0",
                "manual_recurring_observation_tick_runner_v0",
            ],
        },
        "risk_boundary": {
            **SAFETY_FLAGS,
            "action_field_execution_status": "blocked_future_work",
            "operator_review_required_before_live_use": True,
        },
        "residual_history_summary": {
            "source_kind": "dry_run_generated_residual_summaries",
            "manual_tick_residual_available": inputs["manual_tick_summary"].get(
                "manual_tick_residual_delta_defined"
            ),
            "recurring_execution_enabled": inputs["manual_tick_summary"].get("recurrence_enabled"),
            "direct_learning_allowed": False,
        },
        "governance_policy_summary": {
            "pre_u_required": True,
            "y_star_gov_required_for_future_validation": True,
            "local_projection_harness_may_not_call_live_hooks": True,
            "cieu_event_policy": "fixture_only_no_persistence",
        },
        "archaeology_evidence_refs": {
            "summary": evidence_ref("archaeology_summary"),
            "merge_plan": evidence_ref("merge_plan"),
            "concept_map": evidence_ref("concept_map"),
            "old_to_new_alignment": evidence_ref("old_to_new_alignment"),
            "assets_found": archaeology_summary.get("field_functional_assets_found"),
            "reusable_old_assets_count": len(merge_plan.get("reusable_old_assets", [])),
        },
    }


def build_policy(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_field_projection_contract.projection_policy",
        "schema_version": "v0",
        "policy_id": "mission-field-projection-policy-v0",
        "policy_summary": "Deterministic mission-to-action Y* projection for inspection and future Pre-U adapter work only.",
        "projection_is_not_planning": True,
        "projection_is_not_live_execution": True,
        "semantic_truth_scoring_enabled": False,
        "probabilistic_truth_scoring_enabled": False,
        "allowed_layers": contract["supported_projection_layers"],
        "forbidden_inputs": contract["forbidden_inputs"],
        "required_safety_flags": contract["safety_flags"],
        "action_layer_must_remain_projection_only": True,
        "future_pre_u_validation_required_before_action": True,
    }


def layer(
    name: str,
    parent: str | None,
    projected_y_star: dict[str, Any],
    inherited: list[str],
    narrowed: list[str],
    added: list[str],
    blocked: list[str],
    evidence_refs: list[str],
    source_kind: str,
    confidence_class: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "projection_id": f"projection-layer-{name}-v0",
        "layer_name": name,
        "parent_layer": parent,
        "projected_y_star": projected_y_star,
        "inherited_constraints": inherited,
        "narrowed_constraints": narrowed,
        "added_context_constraints": added,
        "blocked_or_unknown_constraints": blocked,
        "evidence_refs": evidence_refs,
        "source_kind": source_kind,
        "confidence_class": confidence_class,
        "safety_flags": SAFETY_FLAGS,
    }
    if name == "action":
        payload.update(
            {
                "projection_only": True,
                "live_action_authorized": False,
                "requires_pre_u_validation": True,
                "action_field_execution_status": "not_implemented_future_work",
            }
        )
    return payload


def build_layers(input_fixture: dict[str, Any]) -> list[dict[str, Any]]:
    mission = input_fixture["mission_y_star"]
    xt = input_fixture["xt_observation_summary"]
    role = input_fixture["agent_role"]
    policy = input_fixture["governance_policy_summary"]
    common_evidence = [
        evidence_ref("archaeology_summary"),
        evidence_ref("merge_plan"),
        evidence_ref("old_to_new_alignment"),
    ]
    return [
        layer(
            "mission",
            None,
            {
                "Y_star_id": "mission-y-star-v0",
                "statement": mission["founder_defined_mission"],
                "success_shape": mission["desired_state"],
            },
            ["founder mission remains controlling objective"],
            ["commercial AI agent company autonomy is bounded by governance"],
            ["L5.0 field-functional evidence supports mission-field concept preservation"],
            ["deep Xt model remains summary-level until L5.2"],
            [evidence_ref("refreshed_dashboard"), evidence_ref("concept_map")],
            "mission_dashboard_plus_archaeology_concept",
            "concept_reference_only",
        ),
        layer(
            "company",
            "mission",
            {
                "Y_star_id": "company-y-star-v0",
                "statement": "Company advances autonomy by creating deterministic governed harnesses before live operation.",
                "operating_state": xt["company_operating_state"],
            },
            ["founder mission remains controlling objective", "no live execution"],
            ["company scope limited to ystar-company generated/read-model evidence"],
            ["current capability chain includes read-only tool, bridge, manual tick, and field archaeology"],
            ["commercial runtime metrics are not live and cannot be inferred from raw runtime artifacts"],
            common_evidence + [evidence_ref("company_state_digest")],
            "generated_read_model_projection",
            "deterministic_policy_projection",
        ),
        layer(
            "milestone",
            "company",
            {
                "Y_star_id": "milestone-y-star-l5-1-v0",
                "statement": "Produce an inspectable L5.1 projection harness ready to feed L5.2 deep Xt modeling.",
                "target_milestone": "L5.1 Mission Field Functional Projection Harness v0",
            },
            ["company scope limited to generated/read-model evidence"],
            ["milestone output must be JSON-schema-like, deterministic, and validator-friendly"],
            ["L5.0 merge plan becomes source evidence, not live code absorption"],
            ["production Pre-U adapter and live action-field semantics remain unresolved"],
            common_evidence,
            "field_archaeology_merge_plan_projection",
            "wrapped_archaeology_asset",
        ),
        layer(
            "session",
            "milestone",
            {
                "Y_star_id": "session-y-star-l5-1-build-v0",
                "statement": "Within this session, generate contract, trace, Pre-U adapter candidate, and residual fixture without external effects.",
                "agent_role": role["primary_agent"],
            },
            ["milestone output must be deterministic"],
            ["session may only write L5.1 artifacts and read-model summaries"],
            ["role alignment narrows action to Aiden-CEO request with governance support"],
            ["no Y-star-gov import or validator call is authorized in this session"],
            common_evidence,
            "role_scope_policy_projection",
            "concept_reference_only",
        ),
        layer(
            "task",
            "session",
            {
                "Y_star_id": "task-y-star-l5-1-artifact-build-v0",
                "statement": "Create layered projection artifacts plus a dry-run Pre-U packet candidate and residual delta fixture.",
                "acceptance_shape": "all required files exist, parse, and keep safety flags false",
            },
            ["session may only write L5.1 artifacts"],
            ["task is limited to source/docs/schema-like generated outputs and tests"],
            ["contract projection must expose unresolved gaps rather than hiding them"],
            ["direct action-field executor evidence remains weak"],
            common_evidence,
            "deterministic_task_contract_projection",
            "deterministic_policy_projection",
        ),
        layer(
            "action",
            "task",
            {
                "Y_star_id": "action-y-star-pre-u-candidate-v0",
                "statement": "Prepare a future Pre-U packet candidate from the task-level projection; do not authorize or execute action.",
                "candidate_action_context": input_fixture["tool_context"]["candidate_action_context"],
            },
            ["task is limited to source/docs/schema-like generated outputs and tests"],
            ["action may only become a Pre-U-like packet candidate"],
            [policy["cieu_event_policy"], "future Y-star-gov validation remains required"],
            [
                "action-field execution not implemented",
                "production Pre-U adapter not implemented",
                "live hook output forbidden",
            ],
            common_evidence,
            "pre_u_contract_projection_only",
            "unresolved_gap",
        ),
    ]


def build_trace(layers: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.layered_y_star_projection_trace.layered_projection_trace",
        "schema_version": "v0",
        "trace_id": "layered-y-star-projection-trace-001",
        "projection_contract_ref": rel(CONTRACT_PACK / "projection_contract_v0.json"),
        "projection_layers": layers,
        "semantic_truth_scoring_enabled": False,
        "probabilistic_truth_scoring_enabled": False,
        "real_action_executed": False,
        "external_action_executed": False,
        "ready_for_pre_u_adapter_candidate": True,
    }


def build_field_source_map(concepts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    mappings = [
        ("field_alignment", ["mission", "task"], "concept_reference_only"),
        ("mission_field", ["mission", "company"], "concept_reference_only"),
        ("role_field", ["session", "task"], "concept_reference_only"),
        ("observation_field", ["company", "milestone"], "concept_reference_only"),
        ("Y_star_projection", LAYER_NAMES, "wrapped_archaeology_asset"),
        ("contract_projection", ["task", "action"], "wrapped_archaeology_asset"),
        ("residual_feedback", ["action"], "concept_reference_only"),
        ("counterfactual_pre_u", ["action"], "wrapped_archaeology_asset"),
        ("learning_feedback", ["action"], "concept_reference_only"),
        ("action_field", ["action"], "unresolved_gap"),
    ]
    return {
        "schema_name": "ystar.layered_y_star_projection_trace.field_source_map",
        "schema_version": "v0",
        "map_id": "field-source-map-001",
        "field_sources": [
            {
                "field_concept": concept_id,
                "current_status": concepts.get(concept_id, {}).get("current_status", "not_found"),
                "source_assets": concepts.get(concept_id, {}).get("source_assets", []),
                "used_by_layers": layers,
                "confidence_class": confidence,
                "merge_notes": concepts.get(concept_id, {}).get(
                    "merge_notes", "No direct concept evidence found."
                ),
            }
            for concept_id, layers, confidence in mappings
        ],
        "live_enabled": False,
    }


def build_contraction_map(layers: list[dict[str, Any]]) -> dict[str, Any]:
    contractions = []
    for index, current in enumerate(layers):
        if index == 0:
            continue
        parent = layers[index - 1]
        contractions.append(
            {
                "from_layer": parent["layer_name"],
                "to_layer": current["layer_name"],
                "inherited_constraints_count": len(current["inherited_constraints"]),
                "narrowed_constraints": current["narrowed_constraints"],
                "blocked_or_unknown_constraints": current["blocked_or_unknown_constraints"],
                "contraction_rule": "child layer may narrow parent Y* but may not remove disabled safety flags",
            }
        )
    return {
        "schema_name": "ystar.layered_y_star_projection_trace.contraction_map",
        "schema_version": "v0",
        "contraction_map_id": "projection-contraction-map-001",
        "contractions": contractions,
        "safety_flag_invariant": SAFETY_FLAGS,
    }


def build_unresolved_gap_map() -> dict[str, Any]:
    gaps = [
        {
            "gap_id": "gap-action-field-execution",
            "gap_type": "action_field_gap",
            "description": "L5.0 found weak direct action-field evidence; no executor exists.",
            "blocked_until": "future governed action wrapper and Pre-U validator integration",
            "blocks_live_execution": True,
        },
        {
            "gap_id": "gap-deep-xt-model",
            "gap_type": "projection_gap",
            "description": "Xt is still a generated summary, not a deep observation model.",
            "blocked_until": "future deep Xt input-model milestone after auto-projection core",
            "blocks_live_execution": False,
        },
        {
            "gap_id": "gap-pre-u-production-adapter",
            "gap_type": "pre_u_adapter_gap",
            "description": "Adapter candidate mirrors packet concepts but does not call Y-star-gov.",
            "blocked_until": "reviewed Pre-U adapter implementation",
            "blocks_live_execution": True,
        },
        {
            "gap_id": "gap-review-gated-learning",
            "gap_type": "learning_feedback_gap",
            "description": "Residual fixture can enter a future review queue but cannot write memory.",
            "blocked_until": "review-gated learning candidate queue",
            "blocks_live_execution": False,
        },
    ]
    return {
        "schema_name": "ystar.layered_y_star_projection_trace.unresolved_gap_map",
        "schema_version": "v0",
        "gap_map_id": "projection-unresolved-gap-map-001",
        "gaps": gaps,
        "action_field_execution_implemented": False,
        "live_execution_enabled": False,
    }


def build_pre_u_adapter(input_fixture: dict[str, Any], trace: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    action_layer = next(layer for layer in trace["projection_layers"] if layer["layer_name"] == "action")
    packet = {
        "schema_name": "ystar.projection_to_pre_u_packet_adapter.pre_u_packet_candidate",
        "schema_version": "v0",
        "packet_id": "pre-u-packet-candidate-from-projection-001",
        "adapter_status": "candidate_only_not_production_ready",
        "declared_Y_star": action_layer["projected_y_star"],
        "Xt": input_fixture["xt_observation_summary"],
        "candidate_U": {
            "candidate_action_context": action_layer["projected_y_star"]["candidate_action_context"],
            "execution_mode": "dry_run_projection_only",
            "live_action_requested": False,
            "external_action_requested": False,
        },
        "governance_expectations": input_fixture["governance_policy_summary"],
        "trace_refs": [
            rel(TRACE_PACK / "layered_projection_trace.json") + "#projection-layer-action-v0",
            rel(TRACE_PACK / "contraction_map.json"),
            rel(TRACE_PACK / "unresolved_gap_map.json"),
        ],
        "execution_boundary": SAFETY_FLAGS,
        "required_future_validation": [
            "Y-star-gov Pre-U validation",
            "operator review before live enablement",
            "review-gated learning queue before memory changes",
        ],
        "production_ready": False,
        "real_action_executed": False,
        "external_action_executed": False,
    }
    mapping = {
        "schema_name": "ystar.projection_to_pre_u_packet_adapter.pre_u_adapter_mapping",
        "schema_version": "v0",
        "mapping_id": "pre-u-adapter-mapping-001",
        "mappings": [
            {"from": "action_level_y_star", "to": "declared_Y_star", "status": "deterministically_mapped"},
            {"from": "xt_observation_summary", "to": "Xt", "status": "deterministically_mapped"},
            {"from": "candidate_action_context", "to": "candidate_U", "status": "deterministically_mapped"},
            {"from": "governance_policy_summary", "to": "governance_expectations", "status": "deterministically_mapped"},
            {"from": "projection_trace ids", "to": "trace_refs", "status": "deterministically_mapped"},
            {"from": "safety flags", "to": "execution_boundary", "status": "deterministically_mapped"},
        ],
        "not_mapped_to_live_validator": True,
        "calls_y_star_gov_now": False,
    }
    summary = {
        "schema_name": "ystar.projection_to_pre_u_packet_adapter.pre_u_adapter_summary",
        "schema_version": "v0",
        "pre_u_adapter_candidate_generated": True,
        "pre_u_packet_candidate_generated": True,
        "adapter_production_ready": False,
        "y_star_gov_called": False,
        "unfilled_required_fields": [
            "production validator decision",
            "real governed action target",
            "live residual measurement",
        ],
        **SAFETY_FLAGS,
    }
    return packet, mapping, summary


def build_residual_fixture(trace: dict[str, Any], adapter_summary: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    predicted = {
        "schema_name": "ystar.projection_residual_delta_fixture.predicted_outcome",
        "schema_version": "v0",
        "prediction_id": "projection-predicted-outcome-001",
        "derived_from": rel(TRACE_PACK / "layered_projection_trace.json"),
        "predicted_outcome": [
            "six-layer Y* projection can be inspected",
            "action layer can be converted into a Pre-U-like packet candidate",
            "unresolved action-field execution gap remains explicit",
        ],
        "predicted_risk_boundary": SAFETY_FLAGS,
    }
    actual = {
        "schema_name": "ystar.projection_residual_delta_fixture.mock_actual_outcome",
        "schema_version": "v0",
        "actual_id": "projection-mock-actual-outcome-001",
        "synthetic_dry_run_only": True,
        "actual_outcome": [
            "projection artifacts generated",
            "adapter candidate generated without validator call",
            "residual fixture generated without persistence",
        ],
        "real_action_executed": False,
        "external_action_executed": False,
    }
    delta = {
        "schema_name": "ystar.projection_residual_delta_fixture.residual_delta_fixture",
        "schema_version": "v0",
        "delta_id": "projection-residual-delta-fixture-001",
        "predicted_outcome_ref": rel(RESIDUAL_PACK / "projection_predicted_outcome.json"),
        "mock_actual_outcome_ref": rel(RESIDUAL_PACK / "projection_mock_actual_outcome.json"),
        "residual_delta": {
            "projection_gap": ["Xt remains summary-level until L5.2"],
            "pre_u_adapter_gap": adapter_summary["unfilled_required_fields"],
            "action_field_gap": ["no live action-field executor exists"],
            "evidence_gap": ["direct action-field archaeology evidence remains weak"],
            "learning_eligibility": {
                "eligible_for_review_queue": True,
                "eligible_for_direct_brain_writeback": False,
                "eligible_for_direct_memory_ingestion": False,
                "requires_human_or_governance_review": True,
            },
        },
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "cieu_persistence_enabled": False,
    }
    summary = {
        "schema_name": "ystar.projection_residual_delta_fixture.residual_delta_summary",
        "schema_version": "v0",
        "residual_delta_fixture_generated": True,
        "mock_actual_outcome_is_synthetic": True,
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "requires_human_or_governance_review": True,
        **SAFETY_FLAGS,
    }
    return predicted, actual, delta, summary


def build_summary(
    contract: dict[str, Any],
    trace: dict[str, Any],
    adapter_summary: dict[str, Any],
    residual_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_field_projection_contract.projection_contract_summary",
        "schema_version": "v0",
        "mission_field_projection_harness_defined": True,
        "l5_1_projection_contract_defined": True,
        "projection_contract_defined": True,
        "layered_projection_trace_generated": bool(trace.get("projection_layers")),
        "field_source_map_generated": True,
        "contraction_map_generated": True,
        "unresolved_gap_map_generated": True,
        "pre_u_adapter_candidate_generated": adapter_summary["pre_u_adapter_candidate_generated"],
        "residual_delta_fixture_generated": residual_summary["residual_delta_fixture_generated"],
        "projection_layers": contract["supported_projection_layers"],
        "action_layer_projection_only": True,
        "action_field_execution_implemented": False,
        "ready_for_L5_2_field_functional_auto_projection_core": True,
        "deep_xt_model_is_not_l5_2_main_milestone": True,
        "next_required_milestone": "L5.2 Field Functional Auto-Projection Core v0",
        "generated_contract": rel(CONTRACT_PACK / "projection_contract_v0.json"),
        "generated_trace": rel(TRACE_PACK / "layered_projection_trace.json"),
        "generated_pre_u_candidate": rel(ADAPTER_PACK / "pre_u_packet_candidate.json"),
        "generated_residual_delta": rel(RESIDUAL_PACK / "projection_residual_delta_fixture.json"),
        "warning": "L5.1 is a dry-run projection harness; L5.2 should upgrade auto-projection before any future deep Xt expansion.",
        **SAFETY_FLAGS,
    }


def markdown_report(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def build() -> None:
    inputs = {name: load_json(path) for name, path in INPUT_REFS.items()}
    concepts = concept_lookup(inputs["concept_map"])

    contract = build_contract()
    fixture = build_input_fixture(inputs)
    policy = build_policy(contract)
    layers = build_layers(fixture)
    trace = build_trace(layers)
    field_source_map = build_field_source_map(concepts)
    contraction_map = build_contraction_map(layers)
    unresolved_gap_map = build_unresolved_gap_map()
    pre_u_packet, pre_u_mapping, pre_u_summary = build_pre_u_adapter(fixture, trace)
    predicted, actual, residual_delta, residual_summary = build_residual_fixture(trace, pre_u_summary)
    summary = build_summary(contract, trace, pre_u_summary, residual_summary)

    write_text(
        CONTRACT_PACK / "README.md",
        markdown_report(
            "Mission Field Projection Contract",
            [
                "L5.1 defines a deterministic, read-only projection harness for mission-level Y* down to action-level Pre-U preparation.",
                "The harness uses L5.0 archaeology evidence as references only. It does not execute old field-functional code.",
                "Action-level projection is explicitly projection-only and does not authorize live action.",
            ],
        ),
    )
    write_json(CONTRACT_PACK / "projection_contract_v0.json", contract)
    write_json(CONTRACT_PACK / "projection_input_fixture.json", fixture)
    write_json(CONTRACT_PACK / "projection_policy_v0.json", policy)
    write_json(CONTRACT_PACK / "projection_contract_summary.json", summary)
    write_text(
        CONTRACT_PACK / "projection_contract_report.md",
        markdown_report(
            "Projection Contract Report",
            [
                "- Supported layers: " + ", ".join(LAYER_NAMES),
                "- Allowed inputs: " + ", ".join(contract["allowed_input_fields"]),
                "- Forbidden inputs include raw runtime contents, network results, and live hook output.",
                "- All live, persistence, scheduler, daemon, writeback, and approval flags remain false.",
                "- Next milestone: L5.2 Field Functional Auto-Projection Core v0.",
            ],
        ),
    )

    write_json(TRACE_PACK / "layered_projection_trace.json", trace)
    write_text(
        TRACE_PACK / "layered_projection_trace.md",
        markdown_report(
            "Layered Y* Projection Trace",
            [
                "- Mission -> company -> milestone -> session -> task -> action projections were generated deterministically.",
                "- Confidence classes are structural only and do not score semantic truth.",
                "- Action layer is projection-only and requires future Pre-U validation.",
            ],
        ),
    )
    write_json(TRACE_PACK / "field_source_map.json", field_source_map)
    write_json(TRACE_PACK / "contraction_map.json", contraction_map)
    write_json(TRACE_PACK / "unresolved_gap_map.json", unresolved_gap_map)
    write_json(
        TRACE_PACK / "projection_trace_summary.json",
        {
            "schema_name": "ystar.layered_y_star_projection_trace.projection_trace_summary",
            "schema_version": "v0",
            "layered_projection_trace_generated": True,
            "projection_layer_count": len(layers),
            "projection_layers": LAYER_NAMES,
            "action_layer_projection_only": True,
            "semantic_truth_scoring_enabled": False,
            "ready_for_pre_u_adapter_candidate": True,
            **SAFETY_FLAGS,
        },
    )

    write_json(ADAPTER_PACK / "pre_u_packet_candidate.json", pre_u_packet)
    write_json(ADAPTER_PACK / "pre_u_adapter_mapping.json", pre_u_mapping)
    write_text(
        ADAPTER_PACK / "pre_u_adapter_gap_report.md",
        markdown_report(
            "Pre-U Adapter Gap Report",
            [
                "- Adapter status: candidate only, not production-ready.",
                "- Y-star-gov is not imported, modified, or called.",
                "- Missing deterministic production fields: "
                + ", ".join(pre_u_summary["unfilled_required_fields"]),
            ],
        ),
    )
    write_json(ADAPTER_PACK / "pre_u_adapter_summary.json", pre_u_summary)

    write_json(RESIDUAL_PACK / "projection_predicted_outcome.json", predicted)
    write_json(RESIDUAL_PACK / "projection_mock_actual_outcome.json", actual)
    write_json(RESIDUAL_PACK / "projection_residual_delta_fixture.json", residual_delta)
    write_json(RESIDUAL_PACK / "projection_residual_delta_summary.json", residual_summary)
    write_text(
        RESIDUAL_PACK / "projection_residual_delta_report.md",
        markdown_report(
            "Projection Residual Delta Report",
            [
                "- Predicted outcome is derived from the projection trace.",
                "- Actual outcome is synthetic and dry-run only.",
                "- Learning is eligible only for a future review queue, not direct brain or memory ingestion.",
            ],
        ),
    )


def main() -> int:
    build()
    print("Built L5.1 mission field projection harness artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
