#!/usr/bin/env python3
"""Build L6.16 CEO command brief and internal strategy memo artifacts.

The builder consumes the local L6.13-L6.15 evidence/review boundary and turns it
into owner-facing planning artifacts. It does not perform external observation,
ask for URLs, or write core state.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.16"
MILESTONE_NAME = "CEO Command Brief & Evidence-Backed Internal Strategy Memo Sprint"
MODE = "ceo_command_brief_internal_strategy_memo"
RUN_ID = "l6_16_ceo_command_brief_internal_strategy_memo_run_001"
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
    "L6.15",
]

REVIEW_STATUS_READY = "human_review_ready_with_bounded_conflict"
BLOCKED_STATUS = "ceo_brief_blocked_missing_review_artifacts"

FORBIDDEN_ACTIONS = [
    "login",
    "account_creation",
    "payment",
    "checkout",
    "form_submission",
    "posting",
    "commenting",
    "messaging",
    "email_customer_outreach",
    "publication",
    "grant_rfp_bounty_submission",
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
    "new_external_search_authorized_by_default": False,
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
    "core_writeback_authorized": False,
    "artifact_refinement_candidate_generation_authorized": True,
    "artifact_refinement_application_authorized": False,
}

REQUIRED_INPUTS = {
    "l6_13_report": "real_mission_evidence_report/mission_evidence_report.json",
    "l6_14_report": "real_mission_evidence_report/l6_14_updated_mission_evidence_report.json",
    "human_review_packet_json": "human_review_packet/l6_15_human_review_packet.json",
    "human_review_packet_md": "human_review_packet/l6_15_human_review_packet.md",
    "evidence_usability": "evidence_usability_assessment/evidence_usability_assessment.json",
    "bounded_conflict": "bounded_conflict_interpretation/bounded_conflict_interpretation_packet.json",
    "planning_matrix": "planning_eligibility_matrix/planning_eligibility_matrix.json",
    "planning_candidates": "governed_planning_candidates/governed_planning_candidates.json",
    "decision_boundary": "decision_boundary_packet/decision_boundary_packet.json",
    "residual_risk_register": "residual_risk_register/residual_risk_register.json",
    "l6_15_summary": "l6_15_read_model/l6_15_read_model_summary.json",
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


def load_text(path: str, default: str = "") -> str:
    target = ROOT / path
    if not target.exists():
        return default
    return target.read_text(encoding="utf-8")


def load_inputs() -> dict[str, Any]:
    missing = [path for path in REQUIRED_INPUTS.values() if not (ROOT / path).exists()]
    data: dict[str, Any] = {
        "missing": missing,
        "paths": REQUIRED_INPUTS,
        "human_review_packet_md": load_text(REQUIRED_INPUTS["human_review_packet_md"]),
    }
    for key, path in REQUIRED_INPUTS.items():
        if path.endswith(".json"):
            data[key] = load_json(path, {})
    return data


def listify(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def count_planning_items(planning_matrix: dict[str, Any], status: str | None = None) -> int:
    matrix = planning_matrix.get("matrix", [])
    if status is None:
        return len(matrix)
    return sum(1 for item in matrix if item.get("allowed_or_blocked") == status)


def build_capability_inventory(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "capabilities": [
            {
                "capability_id": "self_governance_baseline",
                "current_status": "operational_reference_boundary",
                "evidence_commit_or_artifact": "L5/L6 governance artifacts and L6.15 decision boundary",
                "what_it_can_do": "Keep planning, observation, and writeback separated by explicit gates.",
                "what_it_cannot_do": "Authorize external action or core memory updates by itself.",
                "next_upgrade": "Durable human approval records for specific action classes.",
            },
            {
                "capability_id": "external_observation_boundary",
                "current_status": "operational",
                "evidence_commit_or_artifact": "L6.2-L6.4 boundary and preflight artifacts",
                "what_it_can_do": "Define public read-only observation and no-action constraints.",
                "what_it_cannot_do": "Bypass search/page-read backend preflight.",
                "next_upgrade": "Add richer source policies for new mission domains.",
            },
            {
                "capability_id": "controlled_search",
                "current_status": "operational_with_configured_backend",
                "evidence_commit_or_artifact": "2120094e and ca21363d",
                "what_it_can_do": "Run budgeted provider-backed search under explicit environment configuration.",
                "what_it_cannot_do": "Treat search snippets as evidence or run unbounded searches.",
                "next_upgrade": "Provider rate-limit and duplicate-result handling.",
            },
            {
                "capability_id": "controlled_public_page_read",
                "current_status": "operational_with_resilience",
                "evidence_commit_or_artifact": "ca21363d",
                "what_it_can_do": "Read public HTTP/HTTPS pages by GET and turn blocked pages into structured residuals.",
                "what_it_cannot_do": "Login, submit forms, execute JavaScript, or access private/internal networks.",
                "next_upgrade": "Better HTML/PDF extraction and domain-specific readability heuristics.",
            },
            {
                "capability_id": "bounded_crawl",
                "current_status": "operational_limited_depth",
                "evidence_commit_or_artifact": "L6.13/L6.14 run reports",
                "what_it_can_do": "Use depth <= 1 and budgeted pages/domains for evidence discovery.",
                "what_it_cannot_do": "High-volume crawling, scraping loops, or access-control bypass.",
                "next_upgrade": "Explicit domain allow/deny policy and canonical URL de-duplication.",
            },
            {
                "capability_id": "evidence_packet_generation",
                "current_status": "operational",
                "evidence_commit_or_artifact": "real_evidence_packets and second_pass_evidence_packets",
                "what_it_can_do": "Create bounded evidence packets from page-read content.",
                "what_it_cannot_do": "Promote one source into settled truth without review.",
                "next_upgrade": "Improve excerpt quality and structured claim extraction.",
            },
            {
                "capability_id": "source_quality_matrix",
                "current_status": "operational_basic",
                "evidence_commit_or_artifact": "real_source_quality_matrix and source_quality_update_matrix",
                "what_it_can_do": "Classify source quality labels and limitations.",
                "what_it_cannot_do": "Replace human source judgment or guarantee truth.",
                "next_upgrade": "Add stronger provenance and freshness parsing.",
            },
            {
                "capability_id": "conflict_corroboration_matrix",
                "current_status": "operational",
                "evidence_commit_or_artifact": "corroboration_conflict_update",
                "what_it_can_do": "Represent supported, conflicted, unresolved, and insufficient evidence states.",
                "what_it_cannot_do": "Resolve policy or market truth without sufficient reviewed evidence.",
                "next_upgrade": "Add third-pass conflict-specific query executor.",
            },
            {
                "capability_id": "second_pass_observation",
                "current_status": "completed",
                "evidence_commit_or_artifact": "2fc6fd82",
                "what_it_can_do": "Target unresolved conflicts with a second controlled observation pass.",
                "what_it_cannot_do": "Authorize external action from bounded conflict alone.",
                "next_upgrade": "Optional third pass focused on primary sources.",
            },
            {
                "capability_id": "bounded_conflict_decision",
                "current_status": "human_review_ready",
                "evidence_commit_or_artifact": "conflict_resolution_decision_packet",
                "what_it_can_do": "Bound uncertainty enough to support caveated internal planning.",
                "what_it_cannot_do": "Declare unresolved claims settled.",
                "next_upgrade": "Human adjudication and optional additional observation.",
            },
            {
                "capability_id": "human_review_packet",
                "current_status": inputs.get("l6_15_summary", {}).get(
                    "l6_15_review_status", REVIEW_STATUS_READY
                ),
                "evidence_commit_or_artifact": "47b78c53 / human_review_packet",
                "what_it_can_do": "Translate evidence state into reviewable planning boundaries.",
                "what_it_cannot_do": "Grant external-use approval.",
                "next_upgrade": "Human approval workflow with recorded decisions.",
            },
            {
                "capability_id": "planning_eligibility_matrix",
                "current_status": "operational",
                "evidence_commit_or_artifact": "planning_eligibility_matrix",
                "what_it_can_do": "Separate safe internal planning from blocked external and core-writeback actions.",
                "what_it_cannot_do": "Execute blocked actions.",
                "next_upgrade": "Attach approval IDs to future action proposals.",
            },
            {
                "capability_id": "governed_planning_candidates",
                "current_status": "operational_review_only",
                "evidence_commit_or_artifact": "governed_planning_candidates",
                "what_it_can_do": "Propose internal planning steps with caveats and forbidden scopes.",
                "what_it_cannot_do": "Send messages, publish, pay, or write memory.",
                "next_upgrade": "Convert selected candidate into a review-gated work order.",
            },
            {
                "capability_id": "read_model_console_visibility",
                "current_status": "extended_in_l6_16",
                "evidence_commit_or_artifact": "console_read_model/generated/l6_16_ceo_command_brief_internal_strategy_memo_summary.json",
                "what_it_can_do": "Expose owner-facing brief/memo status in the local console.",
                "what_it_cannot_do": "Act outside the repository or modify core state.",
                "next_upgrade": "Add one-command owner dashboard refresh flow.",
            },
        ],
    }


def build_planning_candidate_selection(candidates: dict[str, Any]) -> dict[str, Any]:
    source_candidates = listify(candidates.get("candidates"))
    selected: list[dict[str, Any]] = []
    for candidate in source_candidates:
        cid = candidate.get("candidate_id")
        if cid == "l6_15_candidate_internal_strategy_memo":
            status = "primary_recommended"
            reason = "Matches L6.15 next safe step and stays internal with bounded-conflict caveats."
        elif cid in {"l6_15_candidate_third_pass_observation", "l6_15_candidate_market_hypothesis_table"}:
            status = "secondary_candidate"
            reason = "Useful follow-up after owner review, but not required before this memo."
        elif cid == "l6_15_candidate_technical_gap_analysis":
            status = "deferred_candidate"
            reason = "Helpful once the internal strategy direction is selected."
        else:
            status = "deferred_candidate"
            reason = "Internal draft material only; external sharing remains blocked."
        selected.append(
            {
                "candidate_id": cid,
                "selected_status": status,
                "reason": reason,
                "evidence_basis": candidate.get("evidence_basis", []),
                "caveat": candidate.get("conflict_caveat"),
                "risk": candidate.get("risk"),
                "recommended_next_step": candidate.get("next_safe_step"),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "candidates_considered": len(selected),
        "primary_selected_planning_candidate": "l6_15_candidate_internal_strategy_memo",
        "selection": selected,
    }


def build_evidence_to_strategy_trace(
    review_packet: dict[str, Any],
    usability: dict[str, Any],
    selection: dict[str, Any],
) -> dict[str, Any]:
    candidate_ids = [item.get("candidate_id") for item in selection.get("selection", [])]
    assessments = usability.get("assessments", [])
    trace_items: list[dict[str, Any]] = []
    for idx, assessment in enumerate(assessments, start=1):
        eligibility = assessment.get("planning_eligibility")
        trace_items.append(
            {
                "trace_id": f"l6_16_trace_{idx:03d}",
                "evidence_packet_ids": assessment.get("evidence_packet_ids", []),
                "claim_id": assessment.get("claim_id"),
                "conflict_status": assessment.get("conflict_status"),
                "caveat": assessment.get("limitation"),
                "planning_candidate_ids": candidate_ids[:3],
                "strategy_memo_section": "Strategic interpretation" if idx == 1 else "Risks and mitigations",
                "allowed_use": "internal planning with caveats"
                if eligibility in {"usable_with_caveat", "usable_for_planning"}
                else "internal human review context only",
                "forbidden_use": [
                    "settled truth",
                    "external publication",
                    "customer outreach",
                    "investor claims without human review",
                    "core writeback",
                ],
            }
        )
    if not trace_items:
        trace_items.append(
            {
                "trace_id": "l6_16_trace_001",
                "evidence_packet_ids": review_packet.get("evidence_packet_ids", []),
                "claim_id": "l6_15_review_boundary",
                "conflict_status": "bounded_conflict",
                "caveat": "Use only as a decision boundary until human review.",
                "planning_candidate_ids": candidate_ids[:3],
                "strategy_memo_section": "Executive summary",
                "allowed_use": "internal planning context",
                "forbidden_use": [
                    "settled truth",
                    "external publication",
                    "customer outreach",
                    "core writeback",
                ],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "trace_items": trace_items,
    }


def build_decision_options_matrix() -> dict[str, Any]:
    options = [
        ("continue_internal_strategy_only", True, False, "highest"),
        ("run_third_pass_observation", True, True, "medium"),
        ("create_market_hypothesis_table", True, False, "medium"),
        ("create_technical_gap_analysis", True, False, "medium"),
        ("create_policy_or_funding_landscape_map", True, False, "medium"),
        ("prepare_human_review_session", True, False, "high"),
        ("prepare_external_material_draft_for_review_only", True, True, "low"),
        ("block_external_action_until_approval", True, False, "highest"),
    ]
    matrix = []
    descriptions = {
        "continue_internal_strategy_only": "Keep work internal and caveated while turning evidence into owner decisions.",
        "run_third_pass_observation": "Run another read-only pass only for remaining high-value uncertainties.",
        "create_market_hypothesis_table": "Separate supported, caveated, and unsupported market hypotheses.",
        "create_technical_gap_analysis": "Translate observed evidence into internal technical gaps.",
        "create_policy_or_funding_landscape_map": "Map policy/funding landscape for review without submissions.",
        "prepare_human_review_session": "Prepare a concise human decision session around bounded conflicts.",
        "prepare_external_material_draft_for_review_only": "Draft material that cannot be sent until approval.",
        "block_external_action_until_approval": "Preserve the no-action boundary until a future explicit gate.",
    }
    for priority, (option_id, allowed_now, approval, recommended_priority) in enumerate(options, start=1):
        matrix.append(
            {
                "option_id": option_id,
                "description": descriptions[option_id],
                "evidence_required": "L6.13-L6.15 reviewed evidence boundary",
                "current_evidence_status": "bounded conflict; caveated internal use only",
                "allowed_now": allowed_now,
                "requires_human_approval": approval,
                "risks": [
                    "Overclaiming if caveats are removed.",
                    "External action remains forbidden without future approval.",
                ],
                "expected_value": "Increase owner decision clarity without creating downstream side effects.",
                "recommended_priority": recommended_priority,
                "display_order": priority,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "decision_options": matrix,
    }


def build_30_60_90_plan() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "plan": {
            "30_days": [
                "Stabilize the real observation loop and keep backend configuration outside the repo.",
                "Improve evidence extraction quality for public pages that are noisy or partially blocked.",
                "Create an owner command brief flow from L6.16 artifacts.",
                "Run targeted third-pass observations only where a review packet names a specific gap.",
                "Use this internal strategy memo as the caveated planning baseline.",
            ],
            "60_days": [
                "Build a repeatable mission work-order system for evidence-backed questions.",
                "Improve the source quality classifier and freshness parser.",
                "Add PDF or richer HTML extraction if source gaps require it.",
                "Build a human approval gate workflow for reviewed planning moves.",
                "Start governed planning experiments that remain internal and review-only.",
            ],
            "90_days": [
                "Prepare external-facing materials only after human review.",
                "Define safe publication and outreach protocols behind explicit approval gates.",
                "Consider governed MCP/live behavior only after explicit gates.",
                "Consider review-gated memory or brain writeback only after durable approval records.",
            ],
        },
        "external_actions_authorized_in_l6_16": False,
        "core_writeback_authorized_in_l6_16": False,
    }


def build_no_action_receipt(generated_at: str) -> dict[str, Any]:
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "generated_at_utc": generated_at,
        "new_external_search_performed": False,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
    }
    for action in FORBIDDEN_ACTIONS:
        receipt[f"{action}_occurred"] = False
    return receipt


def build_payloads(inputs: dict[str, Any], generated_at: str) -> dict[str, Any]:
    l6_15_summary = inputs.get("l6_15_summary", {})
    review_packet = inputs.get("human_review_packet_json", {})
    usability = inputs.get("evidence_usability", {})
    bounded_conflict = inputs.get("bounded_conflict", {})
    planning_matrix = inputs.get("planning_matrix", {})
    candidates = inputs.get("planning_candidates", {})
    decision_boundary = inputs.get("decision_boundary", {})
    risk_register = inputs.get("residual_risk_register", {})

    missing = inputs.get("missing", [])
    blocked = bool(missing)
    review_status = BLOCKED_STATUS if blocked else l6_15_summary.get("l6_15_review_status", REVIEW_STATUS_READY)
    evidence_packets_considered = int(l6_15_summary.get("evidence_packets_considered", 0))
    caveated_claims = int(l6_15_summary.get("caveated_claims", 0))
    human_review_required_claims = int(l6_15_summary.get("human_review_required_claims", 0))
    bounded_conflicts_count = int(l6_15_summary.get("bounded_conflicts", 0))
    next_safe_step = l6_15_summary.get(
        "next_recommended_safe_step",
        "draft internal strategy memo with bounded-conflict caveats",
    )
    selection = build_planning_candidate_selection(candidates)
    trace = build_evidence_to_strategy_trace(review_packet, usability, selection)
    capability_inventory = build_capability_inventory(inputs)
    decision_options = build_decision_options_matrix()
    day_plan = build_30_60_90_plan()
    no_action_receipt = build_no_action_receipt(generated_at)

    command_brief = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "run_id": RUN_ID,
        "review_status": review_status,
        "selected_work_order_id": SELECTED_WORK_ORDER_ID,
        "what_do_i_own_now": [
            "A governed CEO-agent evidence loop that can search, read public pages, produce evidence packets, bound conflicts, and expose a review boundary.",
            "A human-review-ready internal planning boundary from L6.15.",
            "A CEO command brief, capability inventory, and internal strategy memo generated in L6.16.",
        ],
        "what_can_ceo_agent_do_today": [
            "Run controlled public read-only observation when explicitly configured.",
            "Create evidence packets from page-read content, not snippets.",
            "Classify source quality, conflicts, planning eligibility, and no-action receipts.",
            "Draft internal planning material with caveats.",
        ],
        "real_external_observation_succeeded": True,
        "evidence_collected": {
            "packets_considered": evidence_packets_considered,
            "evidence_packet_ids": review_packet.get("evidence_packet_ids", []),
            "caveated_claims": caveated_claims,
            "human_review_required_claims": human_review_required_claims,
        },
        "bounded_or_conflicted": {
            "bounded_conflicts": bounded_conflicts_count,
            "conflicted_claims": review_packet.get("conflicted_claims", []),
            "why_bounded": review_packet.get("why_conflict_is_bounded"),
        },
        "usable_for_internal_planning": decision_boundary.get("usable_for_internal_planning", []),
        "not_settled_truth": decision_boundary.get("what_system_cannot_conclude", []),
        "external_actions_still_blocked": decision_boundary.get("actions_remain_forbidden", []),
        "core_writebacks_still_blocked": [
            "CIEU DB write",
            "brain/memory writeback",
            "canonical strategy mutation",
            "direct Y* mutation",
        ],
        "next_safe_step": next_safe_step,
        "shortest_path_to_more_autonomy": [
            "Use the internal memo as a review baseline.",
            "Run a targeted third-pass read-only observation only for named evidence gaps.",
            "Create explicit human approval gates before any external action or core writeback.",
        ],
        "what_should_not_be_built_next": [
            "Another backend activation layer.",
            "A seed URL/manual URL request path.",
            "External outreach, publication, payment, or writeback automation before approval gates.",
        ],
        "blockers": missing,
        "no_action_summary": "No new external search, external action, or core writeback occurred in L6.16.",
    }

    strategy_memo = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "run_id": RUN_ID,
        "classification": "internal_strategy_memo_generated" if not blocked else BLOCKED_STATUS,
        "internal_use_notice": (
            "Internal use only. Not for publication. Not for customer outreach. "
            "Not for investor claims without human review."
        ),
        "executive_summary": (
            "The CEO agent has moved from abstract governance to real controlled observation and "
            "human-review-ready planning. The responsible planning direction is internal strategy "
            "work with explicit bounded-conflict caveats."
        ),
        "current_system_state": command_brief["what_do_i_own_now"],
        "evidence_base": command_brief["evidence_collected"],
        "bounded_conflict_caveats": bounded_conflict.get("bounded_conflicts", []),
        "strategic_interpretation": [
            "The system can support internal hypothesis formation and strategy drafting.",
            "The conflict state is bounded, not settled; caveats must stay attached to any planning output.",
            "The highest-value next move is owner review plus optional targeted observation for specific gaps.",
        ],
        "safe_planning_now": [
            "Draft internal strategy memo with bounded-conflict caveats.",
            "Create market hypothesis table for internal review.",
            "Create technical gap analysis scoped to observed evidence.",
            "Prepare a human review session.",
        ],
        "requires_more_observation": review_packet.get("requires_another_observation_pass", []),
        "requires_human_approval": review_packet.get("requires_human_review", []),
        "remains_blocked": command_brief["external_actions_still_blocked"],
        "recommended_internal_planning_direction": (
            "Continue internal strategy only: use evidence as caveated planning input, "
            "not as public claims or permanent memory."
        ),
        "recommended_next_sprint": "Targeted third-pass observation or owner review workflow, depending on human priority.",
        "risks_and_mitigations": [
            {
                "risk": "Bounded conflict is accidentally treated as settled truth.",
                "mitigation": "Keep caveats in every strategy artifact and require human review before external use.",
            },
            {
                "risk": "Evidence extraction quality varies across public pages.",
                "mitigation": "Improve extraction and run targeted observation only for named gaps.",
            },
            {
                "risk": "Planning material drifts into outreach or publication.",
                "mitigation": "Keep external actions blocked until a future approval gate is created.",
            },
        ],
    }

    caveat_table = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "bounded_conflicts": bounded_conflict.get("bounded_conflicts", []),
        "caveats": [
            {
                "caveat_id": "l6_16_caveat_bounded_conflict_001",
                "linked_conflict_id": conflict.get("conflict_id"),
                "planning_effect": "Permits internal planning, blocks external claims.",
                "must_remain_attached_to": [
                    "CEO command brief",
                    "internal strategy memo",
                    "future external material drafts",
                ],
            }
            for conflict in bounded_conflict.get("bounded_conflicts", [])
        ],
    }

    read_model_summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "run_id": RUN_ID,
        "selected_work_order_id": SELECTED_WORK_ORDER_ID,
        "l6_15_review_status": review_status,
        "command_brief_generated": not blocked,
        "strategy_memo_generated": not blocked,
        "owner_guide_generated": True,
        "capability_inventory_generated": True,
        "evidence_to_strategy_trace_generated": True,
        "planning_candidates_considered": selection["candidates_considered"],
        "primary_selected_planning_candidate": selection["primary_selected_planning_candidate"],
        "decision_options_generated": len(decision_options["decision_options"]),
        "next_30_60_90_day_plan_generated": True,
        "evidence_packets_considered": evidence_packets_considered,
        "bounded_conflicts": bounded_conflicts_count,
        "caveated_claims": caveated_claims,
        "human_review_required_claims": human_review_required_claims,
        "next_safe_step": next_safe_step,
        "blocked_external_actions": l6_15_summary.get("blocked_external_actions", 1),
        "blocked_core_writebacks": l6_15_summary.get("blocked_core_writebacks", 1),
        "blockers": missing,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
    }
    read_model_summary.update(SAFETY_FLAGS)

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_16_ceo_command_brief_internal_strategy_memo_complete": not blocked,
        "review_status": review_status,
        "next_step": next_safe_step,
        "ready_for_owner_review": not blocked,
        "ready_for_external_action": False,
        "ready_for_core_writeback": False,
        "blockers": missing,
    }

    blockers = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "blocked": blocked,
        "blocked_reason": BLOCKED_STATUS if blocked else None,
        "missing_artifacts": missing,
        "ask_user_for_url_required": False,
    }

    residual_delta = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "residuals": [
            "Bounded conflict remains not-settled truth.",
            "External actions remain blocked until explicit human approval.",
            "Core writeback remains blocked until durable approval records exist.",
            "Additional observation should be targeted, not broad.",
        ],
    }

    meta_learning = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "eligible_for_direct_strategy_mutation": False,
        "approved": False,
        "applied": False,
    }

    cieu_fixture = {
        "schema_version": SCHEMA_VERSION,
        "event_mode": "l6_16_ceo_command_brief_internal_strategy_memo_fixture",
        "X_t": "L6.15 human-review-ready bounded conflict state",
        "U_t": "Generate owner-facing command brief and internal strategy memo without new external action.",
        "Y_star_t": (
            "Convert reviewed evidence into internal planning artifacts while preserving no-publication, "
            "no-outreach, no-payment, no-MCP, no-core-writeback, no-canonical-mutation, "
            "and no-direct-Y* mutation constraints."
        ),
        "Y_t_plus_1": "CEO command brief, strategy memo, capability inventory, decision options, and owner guide generated.",
        "R_t_plus_1": residual_delta["residuals"],
    }

    return {
        "command_brief": command_brief,
        "capability_inventory": capability_inventory,
        "evidence_to_strategy_trace": trace,
        "strategy_memo": strategy_memo,
        "planning_candidate_selection": selection,
        "bounded_conflict_caveat_table": caveat_table,
        "decision_options_matrix": decision_options,
        "next_30_60_90_day_plan": day_plan,
        "no_action_receipt": no_action_receipt,
        "read_model_summary": read_model_summary,
        "readiness": readiness,
        "blockers": blockers,
        "strategic_residual_delta": residual_delta,
        "meta_learning_update_candidate": meta_learning,
        "cieu_like_fixture": cieu_fixture,
    }


def md_list(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def render_command_brief(brief: dict[str, Any]) -> str:
    lines = [
        "# L6.16 CEO Command Brief",
        "",
        "This is the short owner-facing answer: the CEO agent can now do controlled public read-only observation, but it still cannot act externally or write core memory.",
        "",
        "## What do I own now?",
        *md_list(brief["what_do_i_own_now"]),
        "",
        "## What can the CEO agent do today?",
        *md_list(brief["what_can_ceo_agent_do_today"]),
        "",
        "## What real observation already succeeded?",
        f"- Real external observation succeeded: {brief['real_external_observation_succeeded']}",
        f"- Evidence packets considered: {brief['evidence_collected']['packets_considered']}",
        f"- Caveated claims: {brief['evidence_collected']['caveated_claims']}",
        f"- Human-review-required claims: {brief['evidence_collected']['human_review_required_claims']}",
        "",
        "## What remains bounded or conflicted?",
        f"- Bounded conflicts: {brief['bounded_or_conflicted']['bounded_conflicts']}",
        f"- Why bounded: {brief['bounded_or_conflicted']['why_bounded']}",
        "",
        "## What can be used for internal planning?",
        *md_list(brief["usable_for_internal_planning"] or ["Caveated internal analysis only."]),
        "",
        "## What cannot be treated as settled truth?",
        *md_list(brief["not_settled_truth"]),
        "",
        "## What is still blocked?",
        "- External actions: outreach, publication, payment, account creation, forms, posting, messaging, grants/RFPs/bounties, revenue execution, MCP/live behavior.",
        "- Core writebacks: CIEU DB, brain/memory, canonical strategy, direct Y* mutation.",
        "",
        "## Next safe step",
        f"- {brief['next_safe_step']}",
        "",
        "## Shortest path to more autonomy",
        *md_list(brief["shortest_path_to_more_autonomy"]),
        "",
        "## What should not be built next?",
        *md_list(brief["what_should_not_be_built_next"]),
        "",
        "## No-action summary",
        f"- {brief['no_action_summary']}",
        "",
    ]
    return "\n".join(lines)


def render_strategy_memo(memo: dict[str, Any]) -> str:
    lines = [
        "# L6.16 Evidence-Backed Internal Strategy Memo",
        "",
        f"**{memo['internal_use_notice']}**",
        "",
        "## Executive Summary",
        memo["executive_summary"],
        "",
        "## Current System State",
        *md_list(memo["current_system_state"]),
        "",
        "## Evidence Base",
        f"- Evidence packets considered: {memo['evidence_base']['packets_considered']}",
        f"- Caveated claims: {memo['evidence_base']['caveated_claims']}",
        f"- Human-review-required claims: {memo['evidence_base']['human_review_required_claims']}",
        "",
        "## Bounded Conflict Caveats",
        "- The conflict is bounded enough for internal planning, not settled enough for external claims.",
        "- Caveats must travel with any downstream draft.",
        "",
        "## Strategic Interpretation",
        *md_list(memo["strategic_interpretation"]),
        "",
        "## What The System Can Safely Plan Now",
        *md_list(memo["safe_planning_now"]),
        "",
        "## What Requires Human Approval",
        *md_list(memo["requires_human_approval"] or ["Any external use or core writeback."]),
        "",
        "## What Remains Blocked",
        *md_list(memo["remains_blocked"]),
        "",
        "## Recommended Internal Planning Direction",
        memo["recommended_internal_planning_direction"],
        "",
        "## Recommended Next Sprint",
        memo["recommended_next_sprint"],
        "",
        "## Risks And Mitigations",
    ]
    for item in memo["risks_and_mitigations"]:
        lines.append(f"- Risk: {item['risk']} Mitigation: {item['mitigation']}")
    lines.append("")
    return "\n".join(lines)


def render_owner_guide(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# L6.16 Owner Operating Guide",
            "",
            "## How do I run the CEO command brief?",
            "- Use the console command `ceo-command-brief-internal-strategy-memo` from the repo root.",
            "",
            "## How do I run real observation?",
            "- Use the existing L6.13 real observation scripts only when the repo-external controlled observation environment is configured.",
            "- Do not paste API keys into repo files.",
            "",
            "## How do I read the evidence report?",
            "- Start with `ceo_command_brief/l6_16_ceo_command_brief.md` for the owner view.",
            "- Read `internal_strategy_memo/l6_16_internal_strategy_memo.md` for the caveated internal planning direction.",
            "- Use L6.13-L6.15 reports when you need evidence packet details.",
            "",
            "## How do I know what is safe to do next?",
            f"- The next safe step is: {summary['next_safe_step']}.",
            "- Internal analysis is allowed. External action and core writeback remain blocked.",
            "",
            "## What should I not ask the agent to do yet?",
            "- Do not ask it to publish, contact customers, submit grants/RFPs, spend money, execute MCP/live behavior, or write brain/memory/canonical state.",
            "",
            "## Important files",
            "- `ceo_command_brief/l6_16_ceo_command_brief.md`",
            "- `internal_strategy_memo/l6_16_internal_strategy_memo.md`",
            "- `system_capability_inventory/system_capability_inventory.json`",
            "- `decision_options_matrix/decision_options_matrix.json`",
            "- `next_30_60_90_day_plan/next_30_60_90_day_plan.json`",
            "",
            "## One-command workflow",
            "- `python3 console_read_model/cli/team_console.py ceo-command-brief-internal-strategy-memo`",
            "",
        ]
    )


def render_simple_md(title: str, payload: dict[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=False)}\n```\n"


def build() -> list[str]:
    generated: list[str] = []
    generated_at = utc_now()
    inputs = load_inputs()
    payloads = build_payloads(inputs, generated_at)
    summary = payloads["read_model_summary"]

    contract = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "input_milestones": INPUT_MILESTONES,
        "mode": MODE,
        "selected_work_order_id": SELECTED_WORK_ORDER_ID,
        "ceo_command_brief_authorized": True,
        "internal_strategy_memo_authorized": True,
        "new_external_search_authorized_by_default": False,
        "external_action_authorized": False,
        "core_writeback_authorized": False,
        **SAFETY_FLAGS,
    }
    scope = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "allowed_scope": [
            "load existing L6.13-L6.15 local artifacts",
            "generate CEO command brief",
            "generate evidence-backed internal strategy memo",
            "generate planning and owner operating artifacts",
            "update read-model and console visibility",
        ],
        "explicit_non_goals": [
            "new external search by default",
            "external action",
            "core writeback",
            "manual URL request",
        ],
    }

    write_text(
        "l6_ceo_command_brief_internal_strategy_memo/README.md",
        "\n".join(
            [
                "# L6.16 CEO Command Brief & Internal Strategy Memo",
                "",
                "This pack converts the L6.15 human-review decision boundary into owner-facing planning artifacts.",
                "It does not run external search, perform side effects, or write core state.",
                "",
            ]
        ),
        generated,
    )
    write_json("l6_ceo_command_brief_internal_strategy_memo/l6_16_milestone_contract.json", contract, generated)
    write_json("l6_ceo_command_brief_internal_strategy_memo/l6_16_scope.json", scope, generated)
    write_json("l6_ceo_command_brief_internal_strategy_memo/l6_16_safety_flags.json", SAFETY_FLAGS, generated)
    write_json("l6_ceo_command_brief_internal_strategy_memo/l6_16_summary.json", summary, generated)
    write_text(
        "l6_ceo_command_brief_internal_strategy_memo/l6_16_summary.md",
        render_simple_md("L6.16 Summary", summary),
        generated,
    )

    write_json("ceo_command_brief/l6_16_ceo_command_brief.json", payloads["command_brief"], generated)
    write_text("ceo_command_brief/l6_16_ceo_command_brief.md", render_command_brief(payloads["command_brief"]), generated)
    write_json("system_capability_inventory/system_capability_inventory.json", payloads["capability_inventory"], generated)
    write_text(
        "system_capability_inventory/system_capability_inventory.md",
        render_simple_md("System Capability Inventory", payloads["capability_inventory"]),
        generated,
    )
    write_json("evidence_to_strategy_trace/evidence_to_strategy_trace.json", payloads["evidence_to_strategy_trace"], generated)
    write_text(
        "evidence_to_strategy_trace/evidence_to_strategy_trace.md",
        render_simple_md("Evidence To Strategy Trace", payloads["evidence_to_strategy_trace"]),
        generated,
    )
    write_json("internal_strategy_memo/l6_16_internal_strategy_memo.json", payloads["strategy_memo"], generated)
    write_text("internal_strategy_memo/l6_16_internal_strategy_memo.md", render_strategy_memo(payloads["strategy_memo"]), generated)
    write_json("planning_candidate_selection/planning_candidate_selection.json", payloads["planning_candidate_selection"], generated)
    write_text(
        "planning_candidate_selection/planning_candidate_selection.md",
        render_simple_md("Planning Candidate Selection", payloads["planning_candidate_selection"]),
        generated,
    )
    write_json("bounded_conflict_caveat_table/bounded_conflict_caveat_table.json", payloads["bounded_conflict_caveat_table"], generated)
    write_text(
        "bounded_conflict_caveat_table/bounded_conflict_caveat_table.md",
        render_simple_md("Bounded Conflict Caveat Table", payloads["bounded_conflict_caveat_table"]),
        generated,
    )
    write_json("decision_options_matrix/decision_options_matrix.json", payloads["decision_options_matrix"], generated)
    write_text(
        "decision_options_matrix/decision_options_matrix.md",
        render_simple_md("Decision Options Matrix", payloads["decision_options_matrix"]),
        generated,
    )
    write_json("next_30_60_90_day_plan/next_30_60_90_day_plan.json", payloads["next_30_60_90_day_plan"], generated)
    write_text(
        "next_30_60_90_day_plan/next_30_60_90_day_plan.md",
        render_simple_md("Next 30/60/90 Day Plan", payloads["next_30_60_90_day_plan"]),
        generated,
    )
    write_json(
        "owner_operating_guide/l6_16_owner_operating_guide.json",
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "guide_path": "owner_operating_guide/l6_16_owner_operating_guide.md",
            "one_command_workflow": "python3 console_read_model/cli/team_console.py ceo-command-brief-internal-strategy-memo",
            "external_actions_authorized": False,
            "core_writeback_authorized": False,
        },
        generated,
    )
    write_text(
        "owner_operating_guide/l6_16_owner_operating_guide.md",
        render_owner_guide(summary),
        generated,
    )

    write_json("l6_16_no_action_receipts/no_side_effect_receipt.json", payloads["no_action_receipt"], generated)
    write_json(
        "l6_16_no_action_receipts/no_action_receipt_index.json",
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "receipts": ["l6_16_no_action_receipts/no_side_effect_receipt.json"],
        },
        generated,
    )
    write_text(
        "l6_16_no_action_receipts/no_action_receipt_report.md",
        render_simple_md("L6.16 No-Action Receipt", payloads["no_action_receipt"]),
        generated,
    )
    write_json("l6_16_read_model/l6_16_read_model_summary.json", summary, generated)
    write_json("l6_16_read_model/l6_16_readiness_assessment.json", payloads["readiness"], generated)
    write_json("l6_16_read_model/l6_16_blockers.json", payloads["blockers"], generated)
    write_json("l6_16_read_model/l6_16_strategic_residual_delta.json", payloads["strategic_residual_delta"], generated)
    write_json("l6_16_read_model/l6_16_meta_learning_update_candidate.json", payloads["meta_learning_update_candidate"], generated)
    write_json("l6_16_read_model/l6_16_cieu_like_fixture.json", payloads["cieu_like_fixture"], generated)
    write_text("l6_16_read_model/l6_16_report.md", render_simple_md("L6.16 Read Model Report", summary), generated)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "generated_at_utc": generated_at,
        "source_artifacts": REQUIRED_INPUTS,
        "generated_files": generated,
        "no_external_search_performed": True,
        "no_secret_values_serialized": True,
    }
    write_json(
        "l6_ceo_command_brief_internal_strategy_memo/l6_16_generation_manifest.json",
        manifest,
        generated,
    )
    return generated


if __name__ == "__main__":
    for path in build():
        print(path)
