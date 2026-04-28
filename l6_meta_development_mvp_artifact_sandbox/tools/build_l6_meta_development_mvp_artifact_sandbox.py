#!/usr/bin/env python3
"""Build deterministic L6.1 MVP artifact sandbox outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SANDBOX = ROOT / "l6_meta_development_mvp_artifact_sandbox"
SELECTOR = ROOT / "l6_mvp_artifact_input_selector"
CONTRACT = ROOT / "mvp_artifact_generation_contract"
TEMPLATES = ROOT / "sandbox_mvp_artifact_templates"
CASES = ROOT / "selected_mvp_artifact_cases"
VALIDATION = ROOT / "mvp_artifact_evidence_validation"
REVIEW = ROOT / "mvp_artifact_review_gate"
BOUNDARY = ROOT / "mvp_artifact_externalization_boundary"
RESIDUAL = ROOT / "l6_mvp_artifact_strategic_residual_loop"
READINESS = ROOT / "l6_mvp_artifact_sandbox_readiness"

SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.1"
MILESTONE_NAME = "Meta-Development MVP Artifact Sandbox v0"
NEXT_MILESTONE = "L6.2 Governed External Observation Boundary v0"
HEADER = "SANDBOX ONLY — NOT FOR PUBLICATION / OUTREACH / PAYMENT / EXTERNAL USE"

INPUT_REFS = {
    "l6_design_readiness": (
        "l6_meta_development_design_readiness/l6_meta_development_design_readiness.json"
    ),
    "generated_value_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "hypothesis_selection_ranking": "redeemability_selection_engine/hypothesis_selection_ranking.json",
    "hypothesis_redeemability_matrix": "redeemability_selection_engine/hypothesis_redeemability_matrix.json",
    "selected_hypothesis_mvp_plans": (
        "minimum_viable_proof_designer/selected_hypothesis_mvp_plans.json"
    ),
    "governed_experiment_portfolio": (
        "governed_meta_development_experiment_portfolio/governed_experiment_portfolio.json"
    ),
    "conversion_physics_schema": "value_conversion_physics/value_conversion_physics_schema.json",
    "conversion_time_horizon_model": "value_conversion_physics/conversion_time_horizon_model.json",
    "strategic_residual_delta": "strategic_residual_meta_learning_loop/strategic_residual_delta.json",
    "meta_learning_update_candidate": (
        "strategic_residual_meta_learning_loop/meta_learning_update_candidate.json"
    ),
    "live_boundary_readiness": "live_boundary_readiness/live_boundary_readiness.json",
    "system_no_go_decision_packet": "system_no_go_decision_packet/system_no_go_decision_packet.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "strategy_mutation_enabled": False,
    "candidate_auto_approval_enabled": False,
    "real_candidate_approval_enabled": False,
    "real_canonical_policy_mutation_enabled": False,
    "real_canonical_update_application_enabled": False,
    "real_release_execution_enabled": False,
    "real_y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
    "revenue_execution_enabled": False,
    "external_market_scan_enabled": False,
    "public_content_publication_enabled": False,
    "payment_enabled": False,
    "external_observation_execution_enabled": False,
    "publication_enabled": False,
    "outreach_enabled": False,
}

L6_1_FLAGS = {
    "l6_1_sandbox_only": True,
    "l6_1_internal_artifact_generation_enabled": True,
    "l6_1_artifact_review_gate_required": True,
    "l6_1_external_execution_enabled": False,
    "l6_1_network_enabled": False,
    "l6_1_publication_enabled": False,
    "l6_1_outreach_enabled": False,
    "l6_1_payment_enabled": False,
    "l6_1_revenue_execution_enabled": False,
}

BLOCKED_AUTHORIZATIONS = {
    "execution_authorized": False,
    "external_observation_authorized": False,
    "external_execution_authorized": False,
    "publication_authorized": False,
    "outreach_authorized": False,
    "payment_authorized": False,
    "network_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
}

SELECTION_VARIABLES = [
    "conversion_path_length",
    "time_to_first_signal",
    "time_to_first_cash_or_commitment",
    "payer_or_recipient_clarity",
    "acceptance_criteria_clarity",
    "evidence_clarity",
    "distribution_friction",
    "execution_complexity",
    "competitive_pressure",
    "advantage_fit",
    "certainty_of_acceptance",
    "stability_of_demand",
    "repeatability",
    "compounding_value",
    "downside_risk",
    "option_value",
    "strategic_stability",
    "learning_value",
    "reversibility",
    "governance_complexity",
    "external_action_dependency",
]

DISALLOWED_FORMS = [
    "published content",
    "sent email/message",
    "submitted grant/RFP/bounty",
    "customer-facing proposal",
    "invoice/payment link",
    "live demo that touches external systems",
    "MCP execution",
    "public release",
    "production claim",
    "legal/compliance certification claim",
    "real customer commitment",
]

ALLOWED_FORMS = [
    "non-public narrative sample",
    "non-public internal diagnostic checklist",
    "non-public governance assurance brief",
    "non-public method/report sample",
    "non-public education artifact sample",
    "non-submitted grant/RFP response skeleton",
    "non-public productization one-pager",
    "non-public internal tool packaging brief",
]

TEMPLATE_NAMES = {
    "narrative_artifact_template.md": "Narrative Artifact Template",
    "governance_assurance_artifact_template.md": "Governance Assurance Artifact Template",
    "methodology_artifact_template.md": "Methodology Artifact Template",
    "tool_assurance_artifact_template.md": "Tool Assurance Artifact Template",
    "grant_or_rfp_skeleton_template.md": "Grant or RFP Skeleton Template",
    "internal_diagnostic_report_template.md": "Internal Diagnostic Report Template",
}


class BuildError(Exception):
    """Raised when safe generated artifacts cannot be built."""


def read_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BuildError(f"Refusing to read outside repo: {relative_path}") from exc
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(relative_path: str, payload: Any, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    generated.append(relative_path)


def write_text(relative_path: str, text: str, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated.append(relative_path)


def with_common(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "safety_flags": SAFETY_FLAGS,
        "l6_1_flags": L6_1_FLAGS,
    }


def physics_for(hypothesis: dict[str, Any]) -> dict[str, str]:
    path_class = hypothesis.get("path_class", "unknown")
    advantage_fit = hypothesis.get("advantage_fit", "unknown")
    return {
        "conversion_path_length": path_class,
        "time_to_first_signal": "seven_day_signal",
        "time_to_first_cash_or_commitment": "unknown",
        "payer_or_recipient_clarity": "medium",
        "acceptance_criteria_clarity": "medium",
        "evidence_clarity": "high",
        "distribution_friction": "low",
        "execution_complexity": "low",
        "competitive_pressure": "unknown",
        "advantage_fit": advantage_fit,
        "certainty_of_acceptance": "medium",
        "stability_of_demand": "unknown",
        "repeatability": "medium",
        "compounding_value": "high",
        "downside_risk": "low_risk",
        "option_value": "high",
        "strategic_stability": "high",
        "learning_value": "high",
        "reversibility": "high",
        "governance_complexity": "medium",
        "external_action_dependency": "blocked_for_l6_1",
    }


def artifact_kind_for(hypothesis_id: str, value_surface: str) -> str:
    if "mcp" in hypothesis_id:
        return "non_public_tool_assurance_checklist"
    if "methodology" in hypothesis_id or value_surface == "methodology_value":
        return "non_public_methodology_artifact"
    if "audit" in hypothesis_id or "governance" in hypothesis_id:
        return "non_public_governance_assurance_brief"
    return "non_public_internal_diagnostic_report"


def select_hypotheses() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    missing: list[str] = []
    ranking = read_json(INPUT_REFS["hypothesis_selection_ranking"])
    hypotheses_doc = read_json(INPUT_REFS["generated_value_hypotheses"])
    mvp_doc = read_json(INPUT_REFS["selected_hypothesis_mvp_plans"])
    experiment_doc = read_json(INPUT_REFS["governed_experiment_portfolio"])

    for name, doc in [
        ("hypothesis_selection_ranking", ranking),
        ("generated_value_hypotheses", hypotheses_doc),
        ("selected_hypothesis_mvp_plans", mvp_doc),
        ("governed_experiment_portfolio", experiment_doc),
    ]:
        if doc is None:
            missing.append(INPUT_REFS[name])

    if missing:
        return [], [], missing

    hypotheses_by_id = {
        item.get("hypothesis_id"): item for item in hypotheses_doc.get("hypotheses", [])
    }
    mvp_by_id = {
        item.get("source_hypothesis_id"): item for item in mvp_doc.get("mvp_plans", [])
    }
    experiment_by_id = {
        item.get("source_hypothesis_id"): item
        for item in experiment_doc.get("experiments", [])
    }

    ranked = [
        item
        for item in ranking.get("selected_candidates", [])
        if item.get("selected_for_sandbox_design") is True
        and item.get("authorized_for_execution") is False
    ]

    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for rank, candidate in enumerate(ranked, start=1):
        hypothesis_id = candidate.get("hypothesis_id")
        hypothesis = hypotheses_by_id.get(hypothesis_id, {})
        mvp_plan = mvp_by_id.get(hypothesis_id, {})
        experiment = experiment_by_id.get(hypothesis_id, {})
        if not hypothesis:
            deferred.append(
                {
                    "source_hypothesis_id": hypothesis_id,
                    "defer_reason": "missing_source_hypothesis",
                    "execution_authorized": False,
                }
            )
            continue
        enriched = {
            "selection_rank": rank,
            "source_hypothesis_id": hypothesis_id,
            "source_l6_0_file": INPUT_REFS["generated_value_hypotheses"],
            "source_assets": hypothesis.get("source_assets", []),
            "conversion_operators": hypothesis.get("conversion_operators", []),
            "value_surface": hypothesis.get("hypothesized_value_surface"),
            "recipient_archetype": hypothesis.get("hypothesized_recipient_archetype"),
            "possible_value_form": hypothesis.get("possible_value_form"),
            "proof_question": mvp_plan.get(
                "proof_question",
                "Can this internal asset become a coherent reviewable proof artifact?",
            ),
            "minimum_artifact_to_generate": mvp_plan.get(
                "minimum_artifact_to_generate", hypothesis.get("possible_value_form")
            ),
            "validation_method": mvp_plan.get(
                "validation_method",
                "local structural review against source trace and non-execution boundary",
            ),
            "expected_internal_signal": mvp_plan.get(
                "expected_signal",
                "internal reviewer can identify value claim, evidence gap, and next governed proof step",
            ),
            "reason_selected": candidate.get("reason_for_selection"),
            "selection_variables": physics_for(hypothesis),
            "governed_experiment_ref": experiment.get("experiment_id"),
            "selected_by_category": False,
            "hardcoded_opportunity_class_used": False,
            "external_execution_authorized": False,
            "artifact_generation_authorized": True,
            "review_required_before_externalization": True,
        }
        if len(selected) < 3:
            selected.append(enriched)
        else:
            deferred.append(
                {
                    "source_hypothesis_id": hypothesis_id,
                    "defer_reason": "limited_l6_1_artifact_batch_size",
                    "selected_by_category": False,
                    "execution_authorized": False,
                    "future_review_possible": True,
                }
            )
    return selected, deferred, missing


def build_template(name: str) -> str:
    return f"""# {TEMPLATE_NAMES[name]}

{HEADER}

This template is an internal conversion shell. It is not a strategy category, not a
fixed opportunity class, and not approved for external use.

- hypothesis_id:
- source_assets:
- value_surface:
- intended_internal_proof:
- recipient_archetype:
- acceptance_criteria:
- evidence_needed:
- claim_boundaries:
- missing_evidence:
- review_gate:
- externalization_status: blocked
"""


def build_case_artifact(case: dict[str, Any]) -> str:
    assets = ", ".join(case["source_assets"])
    operators = ", ".join(case["conversion_operators"])
    criteria = "\n".join(
        f"- {item}" for item in case["acceptance_criteria"]["acceptance_criteria"]
    )
    evidence = "\n".join(f"- {item}" for item in case["evidence_needed"]["evidence_needed"])
    boundaries = "\n".join(f"- {item}" for item in case["claim_boundary"]["claim_boundaries"])
    return f"""# {case['case_id']} Internal MVP Artifact

{HEADER}

Externalization status: blocked.

## Source Trace

- hypothesis_id: {case['source_hypothesis_id']}
- source_assets: {assets}
- conversion_operators: {operators}
- value_surface: {case['value_surface']}
- recipient_archetype: {case['recipient_archetype']}
- possible_value_form: {case['possible_value_form']}

## Proof Question

{case['proof_question']}

## Internal Artifact Body

This artifact tests whether the selected internal asset can be shaped into a
reviewable minimum viable proof without making a market claim or contacting the
world. It should let an internal reviewer see the asset, the proposed value
surface, the evidence boundary, and the missing proof.

Review lens:
- What internal asset is being converted?
- What value surface is hypothesized?
- What evidence is already available inside the L5/L6 artifact chain?
- What claim remains unproven?
- What future approval boundary would be required before external use?

## Acceptance Criteria

{criteria}

## Evidence Needed

{evidence}

## Claim Boundaries

{boundaries}

## Review Gate

This artifact requires human or future governance review before any
externalization. L6.1 does not authorize publication, outreach, payment,
network use, MCP execution, canonical mutation, brain writeback, memory
ingestion, or direct Y* mutation.
"""


def build_cases(selected: list[dict[str, Any]], generated: list[str]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index, item in enumerate(selected, start=1):
        case_id = f"case_{index:03d}"
        artifact_kind = artifact_kind_for(item["source_hypothesis_id"], item["value_surface"])
        acceptance = {
            "case_id": case_id,
            "acceptance_criteria": [
                "sandbox-only header is present",
                "source hypothesis trace is present",
                "source assets and operators are listed",
                "claim boundary is explicit",
                "missing evidence is disclosed",
                "review gate is present",
                "externalization status is blocked",
                "no publication/outreach/payment/revenue/MCP authorization is present",
            ],
            "structural_validation_only": True,
            "semantic_truth_scoring_used": False,
        }
        evidence_needed = {
            "case_id": case_id,
            "evidence_needed": [
                "reviewer confirms source trace matches L6.0 artifacts",
                "reviewer confirms artifact is internally coherent",
                "reviewer identifies any unsupported claims",
                "future external observation boundary if any market signal is desired",
                "future publication/outreach/payment approval before external use",
            ],
            "missing_evidence": [
                "external recipient validation",
                "market demand evidence",
                "payer acceptance evidence",
                "publication performance evidence",
            ],
        }
        claim_boundary = {
            "case_id": case_id,
            "claim_boundaries": [
                "may describe internal artifact lineage",
                "may describe hypothesized value surface",
                "must not claim market demand",
                "must not claim customer acceptance",
                "must not claim compliance certification",
                "must not imply production readiness",
                "must not present as public marketing copy",
            ],
            "forbidden_claims": [
                "proven market need",
                "guaranteed revenue",
                "legal/compliance certification",
                "customer commitment",
                "production safety guarantee",
            ],
        }
        review_packet = {
            "case_id": case_id,
            "review_packet_id": f"review-packet-{case_id}",
            "review_status": "pending_internal_review",
            "review_required_before_externalization": True,
            "approval_required_before_execution": True,
            "review_questions": [
                "Is the source trace complete?",
                "Are unsupported claims clearly blocked?",
                "Is the artifact useful for internal minimum viable proof review?",
                "What evidence gap should be resolved next?",
                "Would any future externalization require a separate milestone?",
            ],
            **BLOCKED_AUTHORIZATIONS,
        }
        receipt = {
            "case_id": case_id,
            "artifact_generated": True,
            "artifact_mode": "sandbox_internal_only",
            "network_used": False,
            "external_observation_executed": False,
            "publication_performed": False,
            "outreach_performed": False,
            "payment_performed": False,
            "revenue_execution_performed": False,
            "mcp_execution_performed": False,
            "live_behavior_executed": False,
            "canonical_update_performed": False,
            "brain_writeback_performed": False,
            "memory_ingestion_performed": False,
            "direct_y_star_mutation_performed": False,
            "externalization_status": "blocked",
        }
        case_contract = with_common(
            {
                "case_id": case_id,
                "source_hypothesis_id": item["source_hypothesis_id"],
                "source_l6_0_artifacts": [
                    INPUT_REFS["generated_value_hypotheses"],
                    INPUT_REFS["hypothesis_selection_ranking"],
                    INPUT_REFS["selected_hypothesis_mvp_plans"],
                    INPUT_REFS["governed_experiment_portfolio"],
                ],
                "source_assets": item["source_assets"],
                "conversion_operators": item["conversion_operators"],
                "value_surface": item["value_surface"],
                "recipient_archetype": item["recipient_archetype"],
                "possible_value_form": item["possible_value_form"],
                "artifact_kind": artifact_kind,
                "proof_question": item["proof_question"],
                "minimum_artifact_to_generate": item["minimum_artifact_to_generate"],
                "validation_method": item["validation_method"],
                "expected_internal_signal": item["expected_internal_signal"],
                **BLOCKED_AUTHORIZATIONS,
                "artifact_generation_authorized": True,
                "review_required_before_externalization": True,
                "approval_required_before_execution": True,
            }
        )
        case = {
            "case_id": case_id,
            "case_contract": case_contract,
            "source_hypothesis_id": item["source_hypothesis_id"],
            "source_assets": item["source_assets"],
            "conversion_operators": item["conversion_operators"],
            "value_surface": item["value_surface"],
            "recipient_archetype": item["recipient_archetype"],
            "possible_value_form": item["possible_value_form"],
            "proof_question": item["proof_question"],
            "acceptance_criteria": acceptance,
            "evidence_needed": evidence_needed,
            "claim_boundary": claim_boundary,
        }
        cases.append(case)

        base = f"selected_mvp_artifact_cases/{case_id}"
        write_json(f"{base}/case_contract.json", case_contract, generated)
        write_json(
            f"{base}/source_hypothesis_trace.json",
            with_common(
                {
                    "case_id": case_id,
                    "source_hypothesis_id": item["source_hypothesis_id"],
                    "source_l6_0_file": item["source_l6_0_file"],
                    "source_assets": item["source_assets"],
                    "conversion_operators": item["conversion_operators"],
                    "value_surface": item["value_surface"],
                    "selection_variables": item["selection_variables"],
                    "selected_by_category": False,
                    "hardcoded_opportunity_class_used": False,
                }
            ),
            generated,
        )
        write_text(f"{base}/generated_artifact.md", build_case_artifact(case), generated)
        write_json(f"{base}/artifact_acceptance_criteria.json", acceptance, generated)
        write_json(f"{base}/artifact_evidence_needed.json", evidence_needed, generated)
        write_json(f"{base}/artifact_claim_boundary.json", claim_boundary, generated)
        write_json(f"{base}/artifact_review_packet.json", review_packet, generated)
        write_json(f"{base}/artifact_non_execution_receipt.json", receipt, generated)
        write_text(
            f"{base}/case_summary.md",
            f"# {case_id} Summary\n\n"
            f"{HEADER}\n\n"
            f"- source_hypothesis_id: {item['source_hypothesis_id']}\n"
            f"- artifact_kind: {artifact_kind}\n"
            "- execution_authorized: false\n"
            "- externalization_status: blocked\n",
            generated,
        )
    return cases


def main() -> int:
    generated: list[str] = []
    selected, deferred, missing = select_hypotheses()
    artifact_generation_authorized = bool(selected) and not missing

    write_text(
        "l6_meta_development_mvp_artifact_sandbox/README.md",
        "# L6.1 Meta-Development MVP Artifact Sandbox\n\n"
        "Internal minimum viable proof artifacts only. No network, publication,\n"
        "outreach, payment, revenue execution, MCP execution, canonical update,\n"
        "brain writeback, memory ingestion, or direct Y* mutation is authorized.\n",
        generated,
    )
    write_json(
        "l6_meta_development_mvp_artifact_sandbox/l6_1_milestone_contract.json",
        with_common(
            {
                "schema_name": "ystar.l6_1.milestone_contract",
                "schema_version": SCHEMA_VERSION,
                "milestone_id": MILESTONE_ID,
                "milestone_name": MILESTONE_NAME,
                "input_milestone": "L6.0",
                "mode": "sandbox_only",
                "design_only": False,
                "artifact_generation_authorized": artifact_generation_authorized,
                "external_execution_authorized": False,
                "publication_authorized": False,
                "outreach_authorized": False,
                "payment_authorized": False,
                "network_authorized": False,
                "revenue_execution_authorized": False,
                "mcp_execution_authorized": False,
                "canonical_update_authorized": False,
                "direct_y_star_mutation_authorized": False,
                "brain_writeback_authorized": False,
                "memory_ingestion_authorized": False,
                "requires_review_before_externalization": True,
                "non_goals": [
                    "revenue opportunity execution",
                    "external observation",
                    "publication",
                    "outreach",
                    "payment",
                    "MCP execution",
                    "canonical strategy mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "l6_meta_development_mvp_artifact_sandbox/l6_1_sandbox_scope.json",
        with_common(
            {
                "scope_id": "l6-1-mvp-artifact-sandbox-scope",
                "allowed_scope": [
                    "read safe L6.0 generated JSON/Markdown artifacts",
                    "select 1-3 structurally ranked hypotheses",
                    "generate internal static MVP proof artifacts",
                    "generate review gates and evidence criteria",
                ],
                "denied_scope": list(DISALLOWED_FORMS)
                + [
                    "network/API call",
                    "customer contact",
                    "external observation execution",
                    "brain/memory writeback",
                    "direct Y* mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "l6_meta_development_mvp_artifact_sandbox/l6_1_safety_flags.json",
        with_common({"all_real_execution_flags_false": all(v is False for v in SAFETY_FLAGS.values())}),
        generated,
    )
    write_text(
        "l6_meta_development_mvp_artifact_sandbox/l6_1_non_execution_boundary.md",
        f"# L6.1 Non-Execution Boundary\n\n{HEADER}\n\n"
        "L6.1 may generate internal artifacts. It may not publish, send, submit,\n"
        "scrape, contact, charge, execute, invoke MCP, mutate canonical strategy,\n"
        "write brain/memory, write CIEU DB, or mutate Y*.\n",
        generated,
    )

    source_map = {
        "schema_name": "ystar.l6_1.input_reference_map",
        "schema_version": SCHEMA_VERSION,
        "input_milestone": "L6.0",
        "input_refs": INPUT_REFS,
        "missing_required_inputs": missing,
        "fail_closed": bool(missing),
        "network_used": False,
        "external_observation_executed": False,
    }
    write_json("l6_mvp_artifact_input_selector/l6_0_input_reference_map.json", source_map, generated)
    write_json(
        "l6_mvp_artifact_input_selector/hypothesis_selection_source_map.json",
        with_common(
            {
                "selection_source_id": "l6-1-hypothesis-selection-source-map",
                "selection_basis": SELECTION_VARIABLES,
                "source_files": [
                    INPUT_REFS["hypothesis_selection_ranking"],
                    INPUT_REFS["generated_value_hypotheses"],
                    INPUT_REFS["selected_hypothesis_mvp_plans"],
                    INPUT_REFS["governed_experiment_portfolio"],
                    INPUT_REFS["conversion_physics_schema"],
                ],
                "hardcoded_opportunity_categories_used": False,
                "selection_by_seed_example_forbidden": True,
            }
        ),
        generated,
    )
    write_json(
        "l6_mvp_artifact_input_selector/selected_hypotheses_for_mvp_artifacts.json",
        with_common(
            {
                "schema_name": "ystar.l6_1.selected_hypotheses_for_mvp_artifacts",
                "schema_version": SCHEMA_VERSION,
                "selected_count": len(selected),
                "selection_status": "selected_for_internal_artifact_generation"
                if selected
                else "fail_closed_no_eligible_source",
                "selected_hypotheses": selected,
                "structural_selection_only": True,
                "selected_by_category": False,
                "hardcoded_opportunity_class_used": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_mvp_artifact_input_selector/rejected_or_deferred_hypotheses_for_l6_1.json",
        with_common({"deferred_hypotheses": deferred, "missing_inputs": missing}),
        generated,
    )
    write_text(
        "l6_mvp_artifact_input_selector/input_selector_report.md",
        "# L6.1 Input Selector Report\n\n"
        "Selected hypotheses are derived from L6.0 structural ranking and MVP proof\n"
        "plans, not from fixed opportunity categories. External execution remains blocked.\n",
        generated,
    )

    write_json(
        "mvp_artifact_generation_contract/mvp_artifact_definition.json",
        with_common(
            {
                "definition_id": "minimum-viable-proof-artifact-v0",
                "mvp_means": "Minimum Viable Proof",
                "mvp_does_not_mean": [
                    "product launch",
                    "real market execution",
                    "publication",
                    "customer outreach",
                    "paid service delivery",
                ],
                "internal_only": True,
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_generation_contract/mvp_artifact_generation_contract.json",
        with_common(
            {
                "contract_id": "l6-1-mvp-artifact-generation-contract",
                "allowed_operation": "generate static internal review artifacts",
                "requires_source_hypothesis_trace": True,
                "requires_claim_boundary": True,
                "requires_non_execution_receipt": True,
                "requires_review_before_externalization": True,
                **BLOCKED_AUTHORIZATIONS,
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_generation_contract/mvp_artifact_allowed_forms.json",
        with_common(
            {
                "allowed_forms": [
                    {
                        "form": form,
                        "example_only": True,
                        "not_exhaustive": True,
                        "not_authorized_for_external_use": True,
                    }
                    for form in ALLOWED_FORMS
                ]
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_generation_contract/mvp_artifact_disallowed_forms.json",
        with_common({"disallowed_forms": DISALLOWED_FORMS}),
        generated,
    )
    write_json(
        "mvp_artifact_generation_contract/mvp_artifact_claim_safety_policy.json",
        with_common(
            {
                "policy_id": "l6-1-claim-safety-policy",
                "allowed_claims": [
                    "internal source trace exists",
                    "hypothesized value surface is design-only",
                    "evidence gaps are identified",
                    "future review is required",
                ],
                "forbidden_claims": [
                    "market demand proven",
                    "customer acceptance proven",
                    "revenue path proven",
                    "compliance certification granted",
                    "production readiness proven",
                ],
                "semantic_truth_scoring_used": False,
            }
        ),
        generated,
    )
    write_text(
        "mvp_artifact_generation_contract/mvp_artifact_generation_report.md",
        "# MVP Artifact Generation Report\n\n"
        "MVP means minimum viable proof. L6.1 artifacts are internal, review-gated,\n"
        "and blocked from external use.\n",
        generated,
    )

    template_registry = {
        "schema_name": "ystar.l6_1.template_registry",
        "schema_version": SCHEMA_VERSION,
        "templates_are_strategy_categories": False,
        "templates": [
            {
                "template_file": filename,
                "template_name": title,
                "example_only": True,
                "not_exhaustive": True,
                "not_authorized_for_external_use": True,
            }
            for filename, title in TEMPLATE_NAMES.items()
        ],
    }
    write_json("sandbox_mvp_artifact_templates/template_registry.json", template_registry, generated)
    for filename in TEMPLATE_NAMES:
        write_text(f"sandbox_mvp_artifact_templates/{filename}", build_template(filename), generated)
    write_text(
        "sandbox_mvp_artifact_templates/template_safety_notes.md",
        f"# Template Safety Notes\n\n{HEADER}\n\n"
        "Templates are reusable internal forms, not fixed strategy classes. They do not\n"
        "authorize externalization.\n",
        generated,
    )

    cases = build_cases(selected, generated)
    write_json(
        "selected_mvp_artifact_cases/selected_case_index.json",
        with_common(
            {
                "schema_name": "ystar.l6_1.selected_case_index",
                "schema_version": SCHEMA_VERSION,
                "case_count": len(cases),
                "cases": [
                    {
                        "case_id": case["case_id"],
                        "source_hypothesis_id": case["source_hypothesis_id"],
                        "generated_artifact": (
                            f"selected_mvp_artifact_cases/{case['case_id']}/generated_artifact.md"
                        ),
                        "externalization_status": "blocked",
                    }
                    for case in cases
                ],
            }
        ),
        generated,
    )

    validation_criteria = [
        "required fields present",
        "source trace exists",
        "claim boundary exists",
        "evidence needed listed",
        "missing evidence disclosed",
        "externalization blocked",
        "safety flags false",
        "review gate present",
        "artifact has sandbox-only header",
        "no publication/outreach/payment authorization",
        "no direct Y* mutation",
        "no canonical update",
        "no brain/memory writeback",
        "no MCP execution",
    ]
    write_json(
        "mvp_artifact_evidence_validation/mvp_artifact_validation_matrix.json",
        with_common(
            {
                "schema_name": "ystar.l6_1.mvp_artifact_validation_matrix",
                "schema_version": SCHEMA_VERSION,
                "validation_mode": "structural_review_only",
                "criteria": validation_criteria,
                "case_results": [
                    {
                        "case_id": case["case_id"],
                        "validation_status": "structurally_ready_for_internal_review",
                        "semantic_truth_scoring_used": False,
                        "market_success_authority_used": False,
                    }
                    for case in cases
                ],
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_evidence_validation/artifact_evidence_registry.json",
        with_common(
            {
                "evidence_registry": [
                    {
                        "case_id": case["case_id"],
                        "source_hypothesis_id": case["source_hypothesis_id"],
                        "evidence_needed": case["evidence_needed"]["evidence_needed"],
                    }
                    for case in cases
                ]
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_evidence_validation/artifact_acceptance_criteria_registry.json",
        with_common(
            {
                "acceptance_criteria_registry": [
                    {
                        "case_id": case["case_id"],
                        "acceptance_criteria": case["acceptance_criteria"]["acceptance_criteria"],
                    }
                    for case in cases
                ]
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_evidence_validation/artifact_signal_model.json",
        with_common(
            {
                "signal_model_id": "l6-1-internal-signal-model",
                "allowed_signals": [
                    "internal reviewer can understand value surface",
                    "internal reviewer can identify evidence gap",
                    "internal reviewer can identify claim boundary",
                    "internal reviewer can recommend next governed boundary",
                ],
                "disallowed_signals": [
                    "market success",
                    "payer acceptance",
                    "publication performance",
                    "customer commitment",
                ],
                "structural_only": True,
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_evidence_validation/artifact_quality_gate.json",
        with_common(
            {
                "quality_gate_id": "l6-1-artifact-quality-gate",
                "gate_status": "internal_review_required",
                "passes_for_internal_review": bool(cases),
                "passes_for_externalization": False,
                "forbidden_authorities": [
                    "automated truth judgment",
                    "semantic authority score",
                    "market success authority score",
                    "model confidence as approval authority",
                ],
            }
        ),
        generated,
    )
    write_text(
        "mvp_artifact_evidence_validation/evidence_validation_report.md",
        "# Evidence Validation Report\n\n"
        "Validation is structural only. It does not use semantic truth scoring,\n"
        "market success scoring, or LLM confidence as authority.\n",
        generated,
    )

    write_json(
        "mvp_artifact_review_gate/review_gate_contract.json",
        with_common(
            {
                "review_gate_id": "l6-1-mvp-artifact-review-gate",
                "l6_1_artifacts_approved_for_external_use": False,
                "externalization_requires_future_milestone": True,
                "future_milestone_requires_explicit_approval_boundary": True,
                "review_required_before_externalization": True,
                **BLOCKED_AUTHORIZATIONS,
            }
        ),
        generated,
    )
    write_text(
        "mvp_artifact_review_gate/reviewer_checklist.md",
        f"# Reviewer Checklist\n\n{HEADER}\n\n"
        "- Confirm source trace exists.\n"
        "- Confirm missing evidence is disclosed.\n"
        "- Confirm claim boundaries block external claims.\n"
        "- Confirm publication, outreach, payment, and revenue execution are blocked.\n",
        generated,
    )
    write_json(
        "mvp_artifact_review_gate/approval_preconditions.json",
        with_common(
            {
                "preconditions": [
                    "future milestone defines externalization boundary",
                    "human/governance review approves scope",
                    "claim review passes",
                    "privacy/IP review passes",
                    "no safety flag regression",
                ],
                "l6_1_approval_granted": False,
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_review_gate/externalization_preflight_checklist.json",
        with_common(
            {
                "checklist": [
                    "publication approval boundary exists",
                    "outreach approval boundary exists",
                    "payment/compliance boundary exists if monetization is proposed",
                    "network/external observation boundary exists",
                    "artifact claims reviewed",
                ],
                "externalization_allowed_now": False,
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_review_gate/claim_review_checklist.json",
        with_common(
            {
                "claim_review_items": [
                    "no market demand claim",
                    "no customer acceptance claim",
                    "no compliance certification claim",
                    "no production readiness claim",
                    "missing evidence disclosed",
                ]
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_review_gate/privacy_ip_review_checklist.json",
        with_common(
            {
                "privacy_ip_review_items": [
                    "no private customer data",
                    "no secrets",
                    "no raw logs",
                    "no DB content",
                    "no unapproved third-party content",
                ],
                "raw_runtime_artifacts_read": False,
            }
        ),
        generated,
    )
    write_text(
        "mvp_artifact_review_gate/review_gate_report.md",
        "# Review Gate Report\n\n"
        "L6.1 artifacts are not approved for external use. Externalization requires a\n"
        "future milestone with an explicit approval boundary.\n",
        generated,
    )

    future_boundaries = [
        "future external observation boundary",
        "future publication approval sandbox",
        "future outreach approval boundary",
        "future payment / monetization compliance boundary",
        "future governed revenue experiment sandbox",
        "future controlled canonical learning release",
    ]
    write_json(
        "mvp_artifact_externalization_boundary/externalization_blocker.json",
        with_common(
            {
                "blocker_id": "l6-1-externalization-blocker",
                "publication_blocked_now": True,
                "outreach_blocked_now": True,
                "payment_blocked_now": True,
                "network_blocked_now": True,
                "external_execution_blocked_now": True,
                "revenue_execution_blocked_now": True,
                "reason": "L6.1 is internal artifact generation only.",
            }
        ),
        generated,
    )
    write_json(
        "mvp_artifact_externalization_boundary/future_boundary_map.json",
        with_common(
            {
                "future_boundaries": [
                    {
                        "boundary": boundary,
                        "authorized_in_l6_1": False,
                        "requires_future_explicit_milestone": True,
                    }
                    for boundary in future_boundaries
                ]
            }
        ),
        generated,
    )
    for name in [
        "non_publication_receipt",
        "non_outreach_receipt",
        "non_payment_receipt",
        "non_network_receipt",
    ]:
        write_json(
            f"mvp_artifact_externalization_boundary/{name}.json",
            with_common(
                {
                    "receipt_id": f"l6-1-{name}",
                    "performed": False,
                    "authorized": False,
                    "blocked_now": True,
                }
            ),
            generated,
        )
    write_text(
        "mvp_artifact_externalization_boundary/externalization_boundary_report.md",
        "# Externalization Boundary Report\n\n"
        "Publication, outreach, payment, network use, and revenue execution are all\n"
        "blocked in L6.1. Future boundaries are named only, not authorized.\n",
        generated,
    )

    residual_classes = [
        "missing evidence",
        "unclear recipient archetype",
        "weak claim boundary",
        "long path to cash",
        "external dependency remains too high",
        "insufficient acceptance criteria",
        "artifact too narrative-heavy",
        "artifact too product-like",
        "artifact not yet reviewable",
    ]
    write_json(
        "l6_mvp_artifact_strategic_residual_loop/l6_1_cieu_like_fixture.json",
        with_common(
            {
                "X_t": {
                    "l6_0_selection_context": INPUT_REFS["hypothesis_selection_ranking"],
                    "l6_1_constraints": "sandbox-only internal artifact generation",
                },
                "U_t": "Generate internal MVP artifacts for selected L6.0 hypotheses.",
                "Y_star_t": (
                    "Generate internal minimum viable proof artifacts that preserve all safety "
                    "boundaries, avoid external execution, publication, outreach, payment, MCP "
                    "execution, canonical mutation, and remain review-gated."
                ),
                "Y_t_plus_1": {
                    "selected_case_count": len(cases),
                    "internal_artifacts_generated": [case["case_id"] for case in cases],
                    "externalization_blocked": True,
                    "review_gate_generated": True,
                },
                "R_t_plus_1": residual_classes,
                "event_mode": "l6_1_mvp_artifact_sandbox_fixture",
                "persistence_enabled": False,
                "db_write_performed": False,
                "l6_execution_enabled": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_mvp_artifact_strategic_residual_loop/l6_1_strategic_residual_delta.json",
        with_common(
            {
                "residual_classes": residual_classes,
                "deterministic_structural_residual_only": True,
            }
        ),
        generated,
    )
    write_json(
        "l6_mvp_artifact_strategic_residual_loop/l6_1_meta_learning_update_candidate.json",
        with_common(
            {
                "candidate_id": "l6-1-mvp-artifact-meta-learning-update-candidate",
                "learning_targets": [
                    "artifact_generation_policy",
                    "claim_boundary_policy",
                    "evidence_validation_policy",
                    "externalization_gate_policy",
                    "strategic_residual_policy",
                ],
                "eligible_for_review_queue": True,
                "eligible_for_direct_brain_writeback": False,
                "eligible_for_direct_memory_ingestion": False,
                "eligible_for_candidate_auto_approval": False,
                "eligible_for_direct_strategy_mutation": False,
                "approved": False,
                "applied": False,
            }
        ),
        generated,
    )
    write_text(
        "l6_mvp_artifact_strategic_residual_loop/l6_1_residual_report.md",
        "# L6.1 Strategic Residual Report\n\n"
        "Residuals are structural review gaps only. They are not persisted to CIEU DB,\n"
        "not written to memory, and not applied as canonical strategy.\n",
        generated,
    )

    readiness = with_common(
        {
            "schema_name": "ystar.l6_1.readiness_assessment",
            "schema_version": SCHEMA_VERSION,
            "l6_1_artifact_sandbox_complete": bool(cases),
            "selected_hypotheses_count": len(selected),
            "generated_case_count": len(cases),
            "artifact_generation_authorized": artifact_generation_authorized,
            "review_gate_generated": True,
            "externalization_boundary_generated": True,
            "strategic_residual_loop_generated": True,
            "ready_for_l6_2_external_observation_boundary_design": bool(cases),
            "ready_for_external_execution": False,
            "ready_for_publication": False,
            "ready_for_outreach": False,
            "ready_for_payment": False,
            "ready_for_revenue_execution": False,
            "ready_for_mcp_execution": False,
            "ready_for_canonical_update": False,
            "ready_for_brain_memory_writeback": False,
            "next_recommended_milestone": NEXT_MILESTONE,
            "warning": (
                "L6.1 generated internal proof artifacts only. Externalization, "
                "network, publication, outreach, payment, revenue, MCP, canonical "
                "mutation, and writeback remain blocked."
            ),
        }
    )
    write_json("l6_mvp_artifact_sandbox_readiness/l6_1_readiness_assessment.json", readiness, generated)
    write_json(
        "l6_mvp_artifact_sandbox_readiness/l6_1_next_milestone_recommendation.json",
        with_common(
            {
                "recommended_next_milestone": NEXT_MILESTONE,
                "do_not_implement_now": True,
                "external_execution_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_mvp_artifact_sandbox_readiness/l6_1_blockers.json",
        with_common(
            {
                "blockers": [
                    "no external observation boundary",
                    "no publication approval boundary",
                    "no outreach approval boundary",
                    "no payment/compliance boundary",
                    "no governed revenue experiment sandbox",
                    "no real MCP execution boundary",
                ],
                "block_external_execution": True,
            }
        ),
        generated,
    )
    write_text(
        "l6_mvp_artifact_sandbox_readiness/l6_1_readiness_report.md",
        "# L6.1 Readiness Report\n\n"
        "L6.1 artifact sandbox is complete if validation passes. The next milestone is\n"
        "L6.2 external observation boundary design. No external execution is allowed.\n",
        generated,
    )

    summary = with_common(
        {
            "schema_name": "ystar.l6_1.summary",
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestone": "L6.0",
            "mode": "sandbox_only",
            "l6_1_mvp_artifact_sandbox_defined": True,
            "selected_hypotheses_count": len(selected),
            "generated_case_count": len(cases),
            "artifact_generation_authorized": artifact_generation_authorized,
            "internal_artifacts_generated": bool(cases),
            "review_gate_generated": True,
            "externalization_boundary_generated": True,
            "strategic_residual_loop_generated": True,
            "ready_for_l6_2_external_observation_boundary_design": bool(cases),
            "ready_for_external_execution": False,
            "ready_for_publication": False,
            "ready_for_outreach": False,
            "ready_for_payment": False,
            "ready_for_revenue_execution": False,
            "ready_for_mcp_execution": False,
            "ready_for_canonical_update": False,
            "ready_for_brain_memory_writeback": False,
            "next_recommended_milestone": NEXT_MILESTONE,
            "generated_files_count": len(generated),
        }
    )
    write_json("l6_meta_development_mvp_artifact_sandbox/l6_1_summary.json", summary, generated)
    write_text(
        "l6_meta_development_mvp_artifact_sandbox/l6_1_summary.md",
        "# L6.1 Summary\n\n"
        f"{HEADER}\n\n"
        f"- selected_hypotheses_count: {len(selected)}\n"
        f"- generated_case_count: {len(cases)}\n"
        "- externalization_status: blocked\n"
        f"- next_recommended_milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    print(f"Built L6.1 MVP artifact sandbox artifacts ({len(generated)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
