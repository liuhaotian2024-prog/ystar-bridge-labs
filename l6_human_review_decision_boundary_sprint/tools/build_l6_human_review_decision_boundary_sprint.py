#!/usr/bin/env python3
"""Build L6.15 human review decision-boundary artifacts.

The builder consumes existing L6.13/L6.14 real evidence artifacts and converts
the bounded conflict state into human-review and governed-planning packets. It
does not perform external observation, ask for URLs, or write core state.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.15"
MILESTONE_NAME = "Human Review Packet, Decision Boundary & Governed Planning Sprint"
MODE = "human_review_decision_boundary_sprint"
RUN_ID = "l6_15_human_review_decision_boundary_run_001"
SELECTED_WORK_ORDER_ID = "l6_10x_selected_work_order_001"

INPUT_MILESTONES = [
    "L6.0",
    "L6.1",
    "L6.2",
    "L6.3",
    "L6.4",
    "L6.5",
    "L6.6",
    "L6.7",
    "L6.8",
    "L6.9",
    "L6.10",
    "L6.10R",
    "L6.10T",
    "L6.10U",
    "L6.10V",
    "L6.10W",
    "L6.10X",
    "L6.11",
    "L6.12",
    "L6.13",
    "L6.14",
]

REVIEW_STATUSES = [
    "human_review_ready_with_bounded_conflict",
    "human_review_blocked_missing_evidence_artifacts",
]

FORBIDDEN_ACTIONS = [
    "outreach",
    "publication",
    "payment",
    "checkout",
    "account_creation",
    "grant_rfp_bounty_submission",
    "customer_contact",
    "external_posting",
    "form_submission",
    "login",
    "posting",
    "commenting",
    "messaging",
    "email_customer_outreach",
    "revenue_execution",
    "mcp_execution",
    "live_behavior",
    "cieu_db_write",
    "brain_memory_writeback",
    "canonical_strategy_mutation",
    "direct_y_star_mutation",
    "ask_user_url",
]

SAFETY_FLAGS = {
    "new_external_search_required": False,
    "ask_user_for_url_authorized": False,
    "login_authorized": False,
    "account_creation_authorized": False,
    "payment_authorized": False,
    "checkout_authorized": False,
    "form_submission_authorized": False,
    "posting_authorized": False,
    "commenting_authorized": False,
    "messaging_authorized": False,
    "email_customer_outreach_authorized": False,
    "publication_authorized": False,
    "grant_rfp_bounty_submission_authorized": False,
    "outreach_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "live_behavior_authorized": False,
    "cieu_db_write_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
    "artifact_refinement_candidate_generation_authorized": True,
    "artifact_refinement_application_authorized": False,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: str, payload: dict[str, Any] | list[Any], generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    generated.append(path)


def write_text(path: str, payload: str, generated: list[str]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    generated.append(path)


def load_json(path: str, default: Any) -> Any:
    target = ROOT / path
    if not target.exists():
        return default
    return json.loads(target.read_text(encoding="utf-8"))


def clean_text(value: Any, limit: int = 320) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f-\x9f\ufffd]+", " ", text)
    text = " ".join(text.split())
    if not text:
        return "No clean excerpt available; human review required."
    return text[:limit]


def artifact_present(path: str) -> bool:
    return (ROOT / path).exists()


def load_inputs() -> dict[str, Any]:
    paths = {
        "l6_13_report": "real_mission_evidence_report/mission_evidence_report.json",
        "l6_14_report": "real_mission_evidence_report/l6_14_updated_mission_evidence_report.json",
        "l6_14_summary": "l6_14_read_model/l6_14_read_model_summary.json",
        "decision_packet": "conflict_resolution_decision_packet/conflict_resolution_decision_packet.json",
        "conflict_matrix": "corroboration_conflict_update/corroboration_conflict_update_matrix.json",
        "claim_boundary": "claim_boundary_update/claim_boundary_update_table.json",
        "evidence_index": "second_pass_evidence_packets/second_pass_evidence_packet_index.json",
        "source_quality": "source_quality_update_matrix/source_quality_update_matrix.json",
        "next_action": "next_action_recommendation_packet/next_action_recommendation_packet.json",
    }
    return {
        "paths": paths,
        "missing": [path for path in paths.values() if not artifact_present(path)],
        **{key: load_json(path, {}) for key, path in paths.items()},
    }


def evidence_packets(evidence_index: dict[str, Any]) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for entry in evidence_index.get("packets", []):
        path = entry.get("path")
        if not path:
            continue
        packet = load_json(path, {})
        if packet:
            packets.append(packet)
    return packets


def prior_packet_ids(source_quality: dict[str, Any]) -> list[str]:
    return [
        item.get("evidence_packet_id")
        for item in source_quality.get("sources", [])
        if item.get("evidence_packet_id", "").startswith("l6_13_real")
    ]


def classify_claims(
    claims: list[dict[str, Any]],
    source_quality: dict[str, Any],
) -> list[dict[str, Any]]:
    quality_by_packet = {
        item.get("evidence_packet_id"): item
        for item in source_quality.get("sources", [])
        if item.get("evidence_packet_id")
    }
    assessments: list[dict[str, Any]] = []
    for claim in claims:
        packet_ids = claim.get("new_evidence_packet_ids", [])
        qualities = [quality_by_packet.get(packet_id, {}) for packet_id in packet_ids]
        labels = sorted({q.get("source_quality_label", "unknown") for q in qualities if q})
        has_official = any(label in {"official_primary", "official_secondary", "institutional"} for label in labels)
        boundary = claim.get("post_second_pass_claim_boundary", "")
        conflict_status = claim.get("prior_conflict_status") or "requires_review"
        text = clean_text(claim.get("bounded_claim"), 240)
        noisy = text.startswith("No clean excerpt") or len(re.sub(r"[A-Za-z0-9 .,;:'\"()/-]", "", text)) > 20
        if boundary == "bounded_by_second_pass_evidence" and has_official:
            eligibility = "usable_with_caveat"
            reason = "Official-quality sources exist, but the conflict remains bounded rather than fully resolved."
        elif noisy:
            eligibility = "human_review_required"
            reason = "The extracted text needs human review before it can support planning."
        elif claim.get("review_required", True):
            eligibility = "human_review_required"
            reason = "The claim is review-required and not approved as settled truth."
        else:
            eligibility = "usable_for_planning"
            reason = "Evidence appears structurally usable for internal planning only."
        assessments.append(
            {
                "claim_id": claim.get("claim_id"),
                "evidence_packet_ids": packet_ids,
                "source_quality_summary": labels or ["unknown"],
                "conflict_status": conflict_status,
                "limitation": "Not approved for external claims or core writeback.",
                "planning_eligibility": eligibility,
                "reason": reason,
                "bounded_claim_excerpt": text,
            }
        )
    return assessments


def bounded_conflicts(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for decision in decisions:
        status = decision.get("post_second_pass_status", "still_conflicted_with_reason")
        packets.append(
            {
                "conflict_id": decision.get("conflict_id"),
                "claim_scope": decision.get("claim_boundary_update", "internal planning only"),
                "conflicting_positions": [
                    "Prior evidence suggested useful but unresolved source context.",
                    "Second-pass evidence adds context but does not settle the claim for external use.",
                ],
                "supporting_evidence": decision.get("supporting_sources", []),
                "conflicting_evidence": decision.get("conflicting_sources", []),
                "what_is_bounded": "The conflict is narrowed to a reviewable evidence-quality and source-context question.",
                "what_is_not_resolved": decision.get("residual_reason", "Human review is still required."),
                "why_the_conflict_does_not_block_all_planning": (
                    "Internal analysis can preserve caveats and avoid treating the claim as settled truth."
                ),
                "what_decision_types_it_blocks": [
                    "external publication",
                    "customer outreach",
                    "funding or grant submission",
                    "canonical strategy update",
                    "brain or memory writeback",
                ],
                "what_decision_types_it_permits": [
                    "internal analysis only",
                    "additional read-only observation",
                    "governed strategy draft with caveats",
                    "human review packet preparation",
                ],
                "recommended_human_question": (
                    "Is this bounded evidence sufficient for internal planning, or should a third-pass "
                    "read-only observation target more primary sources?"
                ),
                "post_second_pass_status": status,
            }
        )
    return packets


def planning_matrix() -> list[dict[str, Any]]:
    return [
        {
            "planning_item_id": "l6_15_planning_internal_analysis_only",
            "description": "Summarize evidence and caveats for internal reasoning.",
            "required_evidence_basis": "usable or caveated reviewed evidence",
            "current_evidence_status": "bounded conflict with review-required caveats",
            "allowed_or_blocked": "allowed",
            "reason": "No external side effect or core writeback is required.",
            "required_approval": "none beyond L6.15 review boundary",
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "category": "internal_analysis_only",
        },
        {
            "planning_item_id": "l6_15_planning_additional_read_only_observation",
            "description": "Run a future third-pass read-only observation to improve source quality.",
            "required_evidence_basis": "bounded conflict or human request for stronger source support",
            "current_evidence_status": "eligible as a future governed observation candidate",
            "allowed_or_blocked": "allowed_with_future_scope_gate",
            "reason": "Read-only observation can be separately budgeted and approved.",
            "required_approval": "future observation gate",
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "category": "additional_read_only_observation",
        },
        {
            "planning_item_id": "l6_15_planning_governed_strategy_draft",
            "description": "Draft an internal strategy memo that preserves evidence caveats.",
            "required_evidence_basis": "usable_with_caveat evidence only",
            "current_evidence_status": "eligible for internal draft, not external claims",
            "allowed_or_blocked": "allowed_internal_only",
            "reason": "Internal draft can explicitly mark the conflict as bounded and unresolved.",
            "required_approval": "human review before any external use",
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "category": "governed_strategy_draft",
        },
        {
            "planning_item_id": "l6_15_planning_human_review_required_before_action",
            "description": "Any action that relies on the bounded conflict as settled evidence.",
            "required_evidence_basis": "human-reviewed evidence sufficiency decision",
            "current_evidence_status": "blocked pending human decision",
            "allowed_or_blocked": "blocked_until_human_review",
            "reason": "The system cannot convert bounded conflict into settled truth.",
            "required_approval": "explicit human approval",
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "category": "human_review_required_before_action",
        },
        {
            "planning_item_id": "l6_15_planning_blocked_external_side_effect",
            "description": "Outreach, publication, payment, account creation, posting, or funding submission.",
            "required_evidence_basis": "separate approval gate and external-action authorization",
            "current_evidence_status": "blocked",
            "allowed_or_blocked": "blocked",
            "reason": "L6.15 authorizes review and planning boundaries only.",
            "required_approval": "future explicit external-action approval gate",
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "category": "blocked_external_side_effect",
        },
        {
            "planning_item_id": "l6_15_planning_blocked_core_writeback",
            "description": "CIEU DB, brain/memory, canonical strategy, or direct Y* mutation.",
            "required_evidence_basis": "durable approval record plus writeback gate",
            "current_evidence_status": "blocked",
            "allowed_or_blocked": "blocked",
            "reason": "No core state writeback is authorized in L6.15.",
            "required_approval": "future explicit core-writeback approval gate",
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "category": "blocked_core_writeback",
        },
    ]


def planning_candidates(usable: list[dict[str, Any]], caveated: list[dict[str, Any]]) -> list[dict[str, Any]]:
    basis = [item.get("claim_id") for item in usable + caveated if item.get("claim_id")]
    if not basis:
        basis = ["bounded_conflict_review_packet"]
    common_forbidden = [
        "external sending",
        "publication",
        "outreach",
        "payment",
        "core writeback",
        "canonical mutation",
    ]
    return [
        {
            "candidate_id": "l6_15_candidate_internal_strategy_memo",
            "planning_goal": "Draft internal strategy memo",
            "evidence_basis": basis,
            "conflict_caveat": "Conflict remains bounded and must be disclosed.",
            "allowed_scope": "internal review only",
            "forbidden_scope": common_forbidden,
            "expected_value": "Make the evidence state decision-useful without overclaiming.",
            "risk": "low if caveats are preserved",
            "required_human_approval": "before external use",
            "next_safe_step": "draft internal strategy memo",
        },
        {
            "candidate_id": "l6_15_candidate_third_pass_observation",
            "planning_goal": "Target remaining uncertainty with more read-only evidence",
            "evidence_basis": ["bounded_conflict_interpretation"],
            "conflict_caveat": "Only run under a new budgeted observation gate.",
            "allowed_scope": "future read-only observation proposal",
            "forbidden_scope": common_forbidden,
            "expected_value": "Improve source quality and reduce residual ambiguity.",
            "risk": "low read-only risk if governed",
            "required_human_approval": "future observation scope approval",
            "next_safe_step": "run third-pass read-only observation",
        },
        {
            "candidate_id": "l6_15_candidate_market_hypothesis_table",
            "planning_goal": "Create market hypothesis table",
            "evidence_basis": basis,
            "conflict_caveat": "Use evidence as hypotheses, not settled market truth.",
            "allowed_scope": "internal analysis only",
            "forbidden_scope": common_forbidden,
            "expected_value": "Separate supported, caveated, and unsupported assumptions.",
            "risk": "medium if caveats are dropped",
            "required_human_approval": "before action",
            "next_safe_step": "create market hypothesis table",
        },
        {
            "candidate_id": "l6_15_candidate_technical_gap_analysis",
            "planning_goal": "Create technical gap analysis",
            "evidence_basis": basis,
            "conflict_caveat": "Scope gaps to observed public evidence only.",
            "allowed_scope": "internal technical planning",
            "forbidden_scope": common_forbidden,
            "expected_value": "Map product or evidence gaps without external commitments.",
            "risk": "low",
            "required_human_approval": "before resourcing external execution",
            "next_safe_step": "create technical gap analysis",
        },
        {
            "candidate_id": "l6_15_candidate_internal_investor_narrative_draft",
            "planning_goal": "Create investor narrative draft for internal review only",
            "evidence_basis": basis,
            "conflict_caveat": "Narrative must label bounded evidence and unresolved claims.",
            "allowed_scope": "internal narrative draft",
            "forbidden_scope": common_forbidden + ["publication-ready external claims"],
            "expected_value": "Prepare review material while preventing premature claims.",
            "risk": "medium if shared externally without approval",
            "required_human_approval": "mandatory before external sharing",
            "next_safe_step": "create investor narrative draft for internal review only",
        },
    ]


def approval_gate() -> list[dict[str, Any]]:
    gates = [
        ("third_pass_observation", "new budget, source scope, safety preflight", "low"),
        ("internal_strategy_draft", "human review of caveats", "low"),
        ("external_publication", "reviewed evidence sufficiency and publication approval", "high"),
        ("customer_outreach", "outreach approval and approved claims", "high"),
        ("funding_grant_application", "funding submission approval and reviewed evidence", "high"),
        ("core_memory_brain_writeback", "durable approval record and writeback gate", "critical"),
        ("canonical_strategy_update", "canonical update approval and rollback plan", "critical"),
        ("mcp_live_behavior", "live behavior approval and non-bypass proof", "critical"),
    ]
    return [
        {
            "approval_id": f"l6_15_gate_{action}",
            "action_type": action,
            "evidence_required": evidence,
            "risk_tier": risk,
            "required_human_confirmation": True,
            "default_decision": "blocked_until_approved",
        }
        for action, evidence, risk in gates
    ]


def residual_risks(decisions: list[dict[str, Any]], assessments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks = [
        {
            "risk_id": "l6_15_risk_bounded_conflict_not_settled_truth",
            "source": "conflict_resolution_decision_packet",
            "description": "The conflict is bounded but not fully resolved.",
            "evidence_link": "conflict_resolution_decision_packet/conflict_resolution_decision_packet.json",
            "severity": "medium",
            "mitigation": "Require human review and caveated internal planning.",
            "blocks_planning": False,
            "blocks_external_action": True,
            "blocks_core_writeback": True,
        },
        {
            "risk_id": "l6_15_risk_source_quality_variance",
            "source": "source_quality_update_matrix",
            "description": "Some sources are unknown or require stronger provenance review.",
            "evidence_link": "source_quality_update_matrix/source_quality_update_matrix.json",
            "severity": "medium",
            "mitigation": "Prefer official/primary sources in any third-pass observation.",
            "blocks_planning": False,
            "blocks_external_action": True,
            "blocks_core_writeback": True,
        },
        {
            "risk_id": "l6_15_risk_extracted_text_quality",
            "source": "second_pass_evidence_packets",
            "description": "Some extracted page text is noisy and needs human interpretation.",
            "evidence_link": "second_pass_evidence_packets/second_pass_evidence_packet_index.json",
            "severity": "medium",
            "mitigation": "Do not use noisy excerpts as external claims.",
            "blocks_planning": False,
            "blocks_external_action": True,
            "blocks_core_writeback": True,
        },
    ]
    if not decisions or not assessments:
        risks.append(
            {
                "risk_id": "l6_15_risk_missing_evidence_artifacts",
                "source": "required_inputs",
                "description": "One or more local evidence artifacts are missing.",
                "evidence_link": "l6_15_read_model/l6_15_blockers.json",
                "severity": "high",
                "mitigation": "Regenerate missing local artifacts before review.",
                "blocks_planning": True,
                "blocks_external_action": True,
                "blocks_core_writeback": True,
            }
        )
    return risks


def markdown_review_packet(packet: dict[str, Any]) -> str:
    options = "\n".join(f"- {item}" for item in packet["recommended_decision_options"])
    supported = "\n".join(f"- {item}" for item in packet["supported_claims"]) or "- None"
    conflicted = "\n".join(f"- {item}" for item in packet["conflicted_claims"]) or "- None"
    return f"""# L6.15 Human Review Packet

## Executive Summary
{packet['executive_summary']}

## Run Lineage
- Prior run: {packet['prior_run_lineage']['l6_13_classification']}
- L6.14 status: {packet['prior_run_lineage']['l6_14_conflict_status']}
- Selected work order: {packet['selected_work_order_id']}

## Evidence Collected
- Evidence packets considered: {packet['evidence_packets_considered']}
- Real evidence remains review-only and internal-planning-only.

## Supported Claims
{supported}

## Conflicted Or Caveated Claims
{conflicted}

## Why The Conflict Is Bounded
{packet['why_conflict_is_bounded']}

## Responsible Planning Use
{packet['responsible_planning_use']}

## Must Not Be Used As Settled Truth
{packet['must_not_use_as_settled_truth']}

## Recommended Decision Options
{options}

## No-Side-Effect Summary
No outreach, publication, payment, login, form submission, MCP/live behavior, core writeback, or URL request occurred.
"""


def build() -> list[str]:
    generated: list[str] = []
    inputs = load_inputs()
    now = utc_now()
    l6_14_summary = inputs["l6_14_summary"]
    claim_boundary = inputs["claim_boundary"]
    source_quality = inputs["source_quality"]
    decision_packet = inputs["decision_packet"]
    evidence_index = inputs["evidence_index"]
    next_action = inputs["next_action"]
    packets = evidence_packets(evidence_index)
    prior_ids = prior_packet_ids(source_quality)
    all_packet_ids = sorted(set(prior_ids + [p.get("evidence_packet_id") for p in packets if p.get("evidence_packet_id")]))
    missing = inputs["missing"]
    review_status = (
        "human_review_blocked_missing_evidence_artifacts"
        if missing
        else "human_review_ready_with_bounded_conflict"
    )
    decisions = decision_packet.get("decisions", [])
    claims = claim_boundary.get("claims", [])
    assessments = classify_claims(claims, source_quality)
    usable = [item for item in assessments if item["planning_eligibility"] == "usable_for_planning"]
    caveated = [item for item in assessments if item["planning_eligibility"] == "usable_with_caveat"]
    review_required = [item for item in assessments if item["planning_eligibility"] == "human_review_required"]
    more_observation = [item for item in assessments if item["planning_eligibility"] == "requires_more_observation"]
    not_usable = [item for item in assessments if item["planning_eligibility"] == "not_usable_for_planning"]
    bounded = bounded_conflicts(decisions)
    matrix = planning_matrix()
    candidates = planning_candidates(usable, caveated)
    gates = approval_gate()
    risks = residual_risks(decisions, assessments)
    blocked_external = [item["planning_item_id"] for item in matrix if item["category"] == "blocked_external_side_effect"]
    blocked_core = [item["planning_item_id"] for item in matrix if item["category"] == "blocked_core_writeback"]
    next_safe_step = "draft internal strategy memo with bounded-conflict caveats"
    if review_status != "human_review_ready_with_bounded_conflict":
        next_safe_step = "regenerate missing local evidence artifacts before review"

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "run_id": RUN_ID,
        "selected_work_order_id": SELECTED_WORK_ORDER_ID,
        "prior_classification": l6_14_summary.get("prior_run_classification"),
        "l6_14_conflict_status": l6_14_summary.get("conflict_resolution_status"),
        "l6_14_post_second_pass_classification": l6_14_summary.get("post_second_pass_classification"),
        "l6_15_review_status": review_status,
        "allowed_review_statuses": REVIEW_STATUSES,
        "evidence_packets_considered": len(all_packet_ids),
        "usable_claims": len(usable),
        "caveated_claims": len(caveated),
        "human_review_required_claims": len(review_required),
        "requires_more_observation_claims": len(more_observation),
        "not_usable_claims": len(not_usable),
        "bounded_conflicts": len(bounded),
        "governed_planning_candidates": len(candidates),
        "blocked_external_actions": len(blocked_external),
        "blocked_core_writebacks": len(blocked_core),
        "next_recommended_safe_step": next_safe_step,
        "blockers": ["human_review_blocked_missing_evidence_artifacts"] if missing else [],
        "missing_evidence_artifacts": missing,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        **SAFETY_FLAGS,
        "generated_at_utc": now,
    }

    write_json(
        "l6_human_review_decision_boundary_sprint/l6_15_milestone_contract.json",
        {
            **summary,
            "human_review_packet_authorized": True,
            "decision_boundary_packet_authorized": True,
            "governed_planning_candidate_generation_authorized": True,
            "new_external_observation_authorized_by_default": False,
            "external_action_authorized": False,
            "core_writeback_authorized": False,
        },
        generated,
    )
    write_json("l6_human_review_decision_boundary_sprint/l6_15_scope.json", {"scope": "human_review_and_governed_planning_boundary", "required_inputs": inputs["paths"], "forbidden_actions": FORBIDDEN_ACTIONS}, generated)
    write_json("l6_human_review_decision_boundary_sprint/l6_15_safety_flags.json", SAFETY_FLAGS, generated)
    write_json("l6_human_review_decision_boundary_sprint/l6_15_summary.json", summary, generated)
    write_text("l6_human_review_decision_boundary_sprint/README.md", "# L6.15 Human Review Decision Boundary Sprint\n\nConverts bounded real evidence conflicts into human-review and governed-planning packets without external side effects.\n", generated)
    write_text("l6_human_review_decision_boundary_sprint/l6_15_summary.md", f"# L6.15 Summary\n\nReview status: {review_status}\n\nNext safe step: {next_safe_step}\n", generated)

    usability = {
        "schema_version": SCHEMA_VERSION,
        "review_status": review_status,
        "claim_count": len(assessments),
        "allowed_planning_eligibility": [
            "usable_for_planning",
            "usable_with_caveat",
            "human_review_required",
            "requires_more_observation",
            "not_usable_for_planning",
        ],
        "assessments": assessments,
    }
    write_json("evidence_usability_assessment/evidence_usability_assessment.json", usability, generated)
    write_text("evidence_usability_assessment/evidence_usability_assessment.md", f"# Evidence Usability Assessment\n\nClaims assessed: {len(assessments)}\n\nCaveated claims: {len(caveated)}\n\nHuman-review-required claims: {len(review_required)}\n", generated)

    bounded_packet = {
        "schema_version": SCHEMA_VERSION,
        "bounded_conflict_count": len(bounded),
        "bounded_conflicts": bounded,
    }
    write_json("bounded_conflict_interpretation/bounded_conflict_interpretation_packet.json", bounded_packet, generated)
    write_text("bounded_conflict_interpretation/bounded_conflict_interpretation_report.md", f"# Bounded Conflict Interpretation\n\nBounded conflicts: {len(bounded)}\n", generated)

    write_json("planning_eligibility_matrix/planning_eligibility_matrix.json", {"schema_version": SCHEMA_VERSION, "matrix": matrix}, generated)
    write_text("planning_eligibility_matrix/planning_eligibility_report.md", "# Planning Eligibility Matrix\n\nInternal analysis and caveated strategy drafting are allowed; external actions and core writeback remain blocked.\n", generated)
    write_json("governed_planning_candidates/governed_planning_candidates.json", {"schema_version": SCHEMA_VERSION, "candidates": candidates}, generated)
    write_text("governed_planning_candidates/governed_planning_candidates_report.md", f"# Governed Planning Candidates\n\nCandidates generated: {len(candidates)}\n", generated)

    decision_boundary = {
        "schema_version": SCHEMA_VERSION,
        "what_system_can_conclude": [
            "A real evidence conflict was bounded enough for human review.",
            "Some evidence can support internal planning only with caveats.",
        ],
        "what_system_cannot_conclude": [
            "The bounded conflict is settled truth.",
            "Evidence is approved for external claims or core writeback.",
        ],
        "usable_for_internal_planning": [item["claim_id"] for item in usable + caveated],
        "needs_human_review": [item["claim_id"] for item in review_required],
        "needs_additional_observation": [item["claim_id"] for item in more_observation],
        "actions_remain_forbidden": FORBIDDEN_ACTIONS,
        "required_to_unlock_external_action": "explicit future human approval gate with reviewed claims",
        "required_to_unlock_core_writeback": "durable approval record plus writeback-specific gate",
        "writeback_performed_in_l6_15": False,
    }
    write_json("decision_boundary_packet/decision_boundary_packet.json", decision_boundary, generated)
    write_text("decision_boundary_packet/decision_boundary_packet.md", "# Decision Boundary Packet\n\nL6.15 permits internal planning with caveats and blocks external action/core writeback until future explicit approval.\n", generated)

    review_packet = {
        "schema_version": SCHEMA_VERSION,
        "review_status": review_status,
        "executive_summary": "L6.15 converts the real bounded conflict into human-reviewable planning boundaries.",
        "prior_run_lineage": {
            "l6_13_classification": l6_14_summary.get("prior_run_classification"),
            "l6_14_classification": l6_14_summary.get("post_second_pass_classification"),
            "l6_14_conflict_status": l6_14_summary.get("conflict_resolution_status"),
        },
        "selected_work_order_id": SELECTED_WORK_ORDER_ID,
        "what_was_observed": "L6.13/L6.14 real public read-only evidence packets and conflict-resolution artifacts.",
        "evidence_packets_considered": len(all_packet_ids),
        "evidence_packet_ids": all_packet_ids,
        "supported_claims": [item["claim_id"] for item in usable + caveated],
        "conflicted_claims": [item.get("conflict_id") for item in bounded],
        "why_conflict_is_bounded": "Second-pass evidence narrowed uncertainty into a reviewable caveat, but did not authorize settled truth.",
        "responsible_planning_use": "Use evidence only for internal analysis, caveated strategy drafts, and future read-only observation planning.",
        "must_not_use_as_settled_truth": "Do not use bounded claims for external publication, outreach, funding submissions, or core writeback.",
        "requires_human_review": [item["claim_id"] for item in review_required],
        "requires_another_observation_pass": [item["claim_id"] for item in more_observation],
        "recommended_decision_options": [
            "Approve internal strategy memo with caveats.",
            "Request third-pass read-only observation focused on primary sources.",
            "Reject external use until stronger evidence is reviewed.",
        ],
        "risks": [risk["risk_id"] for risk in risks],
        "no_side_effect_summary": "No external side effects, URL request, or core writeback occurred.",
    }
    write_json("human_review_packet/l6_15_human_review_packet.json", review_packet, generated)
    write_text("human_review_packet/l6_15_human_review_packet.md", markdown_review_packet(review_packet), generated)

    write_json("human_approval_gate/human_approval_gate_spec.json", {"schema_version": SCHEMA_VERSION, "gates": gates}, generated)
    write_text("human_approval_gate/human_approval_gate_report.md", f"# Human Approval Gate\n\nApproval gates defined: {len(gates)}\n\nNo gate was executed.\n", generated)
    write_json("residual_risk_register/residual_risk_register.json", {"schema_version": SCHEMA_VERSION, "risks": risks}, generated)
    write_text("residual_risk_register/residual_risk_register_report.md", f"# Residual Risk Register\n\nRisks registered: {len(risks)}\n", generated)

    no_action_receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": "l6_15_no_action_receipt_001",
        "new_external_search_performed": False,
        "local_artifact_regeneration_performed": False,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        **{f"{action}_occurred": False for action in FORBIDDEN_ACTIONS},
        **SAFETY_FLAGS,
    }
    write_json("l6_15_no_action_receipts/no_side_effect_receipt.json", no_action_receipt, generated)
    write_json("l6_15_no_action_receipts/no_action_receipt_index.json", {"schema_version": SCHEMA_VERSION, "receipts": ["l6_15_no_action_receipts/no_side_effect_receipt.json"]}, generated)
    write_text("l6_15_no_action_receipts/no_action_receipt_report.md", "# L6.15 No-Action Receipt\n\nNo external side effects, ask-user-URL path, or core writeback occurred.\n", generated)

    readiness = {
        **summary,
        "l6_15_human_review_decision_boundary_sprint_complete": review_status == "human_review_ready_with_bounded_conflict",
        "ready_for_governed_planning": review_status == "human_review_ready_with_bounded_conflict",
        "ready_for_external_action": False,
        "ready_for_core_writeback": False,
        "next_step": next_safe_step,
    }
    write_json("l6_15_read_model/l6_15_readiness_assessment.json", readiness, generated)
    write_json("l6_15_read_model/l6_15_blockers.json", {"schema_version": SCHEMA_VERSION, "blockers": summary["blockers"], "missing_evidence_artifacts": missing}, generated)
    write_json("l6_15_read_model/l6_15_next_recommended_safe_step.json", {"schema_version": SCHEMA_VERSION, "next_recommended_safe_step": next_safe_step, "requires_external_side_effects": False, "requires_core_writeback": False}, generated)
    write_json("l6_15_read_model/l6_15_meta_learning_update_candidate.json", {"schema_version": SCHEMA_VERSION, "eligible_for_review_queue": True, "eligible_for_direct_brain_writeback": False, "eligible_for_direct_memory_ingestion": False, "eligible_for_candidate_auto_approval": False, "eligible_for_direct_strategy_mutation": False, "approved": False, "applied": False}, generated)
    write_json("l6_15_read_model/l6_15_strategic_residual_delta.json", {"schema_version": SCHEMA_VERSION, "residuals": [risk["risk_id"] for risk in risks]}, generated)
    cieu = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_15_human_review_decision_boundary_fixture",
        "X_t": "L6.14 real evidence conflict bounded state",
        "U_t": "Generate human-review packet and governed planning boundary without side effects",
        "Y_star_t": "Convert bounded real evidence into human-reviewable planning boundaries while preserving no external action and no core writeback.",
        "Y_t_plus_1": "Human review packet, usability assessment, planning matrix, approval gates, residual risks, and read-model summary generated.",
        "R_t_plus_1": [risk["risk_id"] for risk in risks],
    }
    write_json("l6_15_read_model/l6_15_cieu_like_fixture.json", cieu, generated)
    write_json("l6_15_read_model/l6_15_read_model_summary.json", summary, generated)
    write_text("l6_15_read_model/l6_15_report.md", f"# L6.15 Read Model Report\n\nReview status: {review_status}\n\nNext safe step: {next_safe_step}\n", generated)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "generated_at_utc": now,
        "generated_files": generated,
        "input_paths": inputs["paths"],
        "missing_inputs": missing,
    }
    write_json("l6_human_review_decision_boundary_sprint/l6_15_generation_manifest.json", manifest, generated)
    return generated


if __name__ == "__main__":
    files = build()
    print(f"Generated {len(files)} L6.15 files")
