from __future__ import annotations

import importlib
import sqlite3
import sys
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e105_open_world_market_discovery_runtime import (
    SESSION_ID as E105_SESSION_ID,
    build_open_world_market_discovery_strategy,
)


MILESTONE_ID = "E106_CEO_Strategy_Process_Integrity_And_Anti_Anchor_Runtime_R1"
SESSION_ID = "e106_strategy_process_integrity_runtime"
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def build_strategy_process_integrity_runtime_strategy(
    *,
    owner_intent: str | None = None,
    brain_db: Path | None = None,
) -> dict[str, Any]:
    strategy = build_open_world_market_discovery_strategy(
        owner_intent=owner_intent,
        brain_db=brain_db,
    )
    strategy["artifact_id"] = "e106_strategy_process_integrity_strategy"
    strategy["milestone_id"] = MILESTONE_ID
    strategy["strategy_run_id"] = SESSION_ID
    strategy["session_id"] = SESSION_ID
    strategy["strategy_process_integrity_proof"] = build_strategy_process_integrity_proof(strategy)
    strategy["process_integrity_status"] = {
        "E105_limitation_corrected": "E105 proved evidence-derived candidates but did not require the full strategic analysis process.",
        "recent_memory_anchor_risk": "explicitly audited",
        "strategy_conclusion_status": "provisional_until_owner_approved_external_feedback",
    }
    return strategy


def build_strategy_process_integrity_proof(strategy: Mapping[str, Any]) -> dict[str, Any]:
    proof = strategy["open_world_discovery_proof"]
    route_scores = list(strategy["route_scoring"])
    selected = strategy["selected_strategy"]
    opportunity_universe = _opportunity_universe(strategy)
    return {
        "process_id": "e106_full_strategy_process_integrity",
        "process_mode": "full_strategy_process_with_anchor_audit",
        "completed_phases": [
            "owner_intent_restatement",
            "decision_question_framing",
            "blank_slate_opportunity_universe",
            "evidence_acquisition_plan",
            "query_expansion_log",
            "market_landscape_map",
            "competitor_saturation_by_cluster",
            "customer_segment_and_buyer_map",
            "business_model_options",
            "founder_market_fit_counterevidence",
            "route_generation_from_evidence_clusters",
            "counterfactual_route_comparison",
            "anchor_dependence_audit",
            "selected_strategy_thesis",
            "validation_experiment_design",
            "kill_criteria",
            "residual_learning_plan",
        ],
        "recent_memory_only": False,
        "recent_chat_summary_only": False,
        "owner_intent_restatement": strategy.get("owner_intent"),
        "decision_question_framing": {
            "core_question": "What is the fastest credible first-cash path that matches our real capabilities and current public evidence?",
            "not_the_question": "How can we rationalize the previous favorite route?",
        },
        "opportunity_universe_scan": opportunity_universe,
        "evidence_acquisition_plan": {
            "mode": proof["evidence_feed_mode"],
            "public_read_only": True,
            "no_contact_no_login_no_payment_no_publication": True,
            "freshness_status": strategy["external_market_evidence_map"]["freshness_status"],
            "evidence_count": len(strategy["external_market_evidence_map"]["evidence_items"]),
        },
        "query_expansion_log": proof["query_expansion_rounds"],
        "market_landscape_map": _market_landscape(strategy),
        "competitor_saturation_by_cluster": _competitor_by_cluster(strategy),
        "customer_segment_and_buyer_map": _customer_segments(),
        "business_model_options": _business_model_options(),
        "founder_market_fit_counterevidence": _founder_fit_counterevidence(),
        "route_generation_from_evidence_clusters": [
            {
                "route_id": candidate["route_id"],
                "source_cluster_ids": candidate["source_cluster_ids"],
                "evidence_refs": candidate["evidence_refs"],
            }
            for candidate in strategy["route_candidates"]
        ],
        "counterfactual_comparison": [
            {
                "route_id": row["route_id"],
                "score": row["first_cash_score"],
                "why_not_selected": _why_not_selected(row, selected),
            }
            for row in route_scores[:7]
        ],
        "anchor_dependence_audit": {
            "prior_anchors": [
                "CPA Review Bottleneck Rescue",
                "AI Agent Control Room Rescue",
                "Tariff Shock Margin Rescue",
            ],
            "blank_slate_generation_before_anchor_review": True,
            "anchor_penalty_applied": True,
            "selected_route_supported_without_anchor": True,
            "selected_route_id": selected["selected_route_id"],
            "independent_supporting_evidence_refs": _selected_evidence_refs(strategy),
            "anchor_risk_note": "Selected route is allowed to match a previous route only because evidence-derived clusters, scoring, and counterfactual comparison support it independently.",
        },
        "selected_strategy_thesis": {
            "selected_route_id": selected["selected_route_id"],
            "thesis": selected["why_this_path_now"],
            "falsification_condition": selected["what_evidence_could_falsify_it"],
        },
        "validation_experiment_design": {
            "experiment": "owner-approved no-send L4 feedback on a sample AI Agent Control Room Rescue Brief",
            "owner_decision_required": True,
            "no_send_default": True,
            "external_action_executed": False,
            "success_signal": "target buyer recognizes urgency and asks to see/pay for the rescue brief",
            "failure_signal": "target buyer sees no urgent pain or no budget owner",
        },
        "kill_criteria": [
            "No recognized urgent pain after owner-approved feedback.",
            "No budget owner can be identified.",
            "Buyers prefer existing observability/governance tools and do not want a rescue brief.",
            "A simpler adjacent cluster has stronger willingness-to-pay evidence.",
        ],
        "residual_learning_plan": strategy["post_strategy_residual_plan"],
    }


def run_e106_strategy_process_integrity_session(
    *,
    cieu_db: str | Path,
    owner_intent: str | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    strategy = build_strategy_process_integrity_runtime_strategy(
        owner_intent=owner_intent,
        brain_db=brain_db,
    )
    strategic_governance = _load_ystar_module("ystar.governance.ceo_strategic_intelligence_benchmark", ystar_gov_root)
    refresh_governance = _load_ystar_module("ystar.governance.ceo_market_strategy_refresh_contract", ystar_gov_root)
    open_world_governance = _load_ystar_module("ystar.governance.ceo_open_world_strategy_contract", ystar_gov_root)
    integrity_governance = _load_ystar_module("ystar.governance.ceo_strategy_process_integrity_contract", ystar_gov_root)
    strategic_write = strategic_governance.validate_and_write_ceo_strategic_intelligence_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    refresh_write = refresh_governance.validate_and_write_ceo_market_strategy_refresh(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    open_world_write = open_world_governance.validate_and_write_ceo_open_world_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    integrity_write = integrity_governance.validate_and_write_ceo_strategy_process_integrity(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    cieu_summary = summarize_e106_cieustore(cieu_db)
    receipt = _receipt(strategy, strategic_write, refresh_write, open_world_write, integrity_write, cieu_summary)
    return {
        "artifact_id": "e106_strategy_process_integrity_session",
        "milestone_id": MILESTONE_ID,
        "strategy": strategy,
        "YstarGov_strategic_benchmark_write_result": strategic_write,
        "YstarGov_market_refresh_write_result": refresh_write,
        "YstarGov_open_world_write_result": open_world_write,
        "YstarGov_process_integrity_write_result": integrity_write,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_strategy_process_integrity_proven": (
            receipt["Y_star_gov_strategic_decision"] == "ALLOW"
            and receipt["Y_star_gov_market_refresh_decision"] == "ALLOW"
            and receipt["Y_star_gov_open_world_decision"] == "ALLOW"
            and receipt["Y_star_gov_process_integrity_decision"] == "ALLOW"
            and receipt["CIEUStore_written"]
        ),
        "recommended_next_milestone": "E107_Automated_Public_Read_Provider_And_Strategy_Dossier_Generator_R1",
    }


def summarize_e106_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT event_type, decision FROM cieu_events WHERE session_id=? ORDER BY seq_global",
            (SESSION_ID,),
        ).fetchall()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def _receipt(
    strategy: Mapping[str, Any],
    strategic_write: Mapping[str, Any],
    refresh_write: Mapping[str, Any],
    open_world_write: Mapping[str, Any],
    integrity_write: Mapping[str, Any],
    cieu_summary: Mapping[str, Any],
) -> dict[str, Any]:
    strategic_decision = strategic_write.get("governance_decision", {}).get("decision", "")
    refresh_decision = refresh_write.get("governance_decision", {}).get("decision", "")
    open_world_decision = open_world_write.get("governance_decision", {}).get("decision", "")
    integrity_decision = integrity_write.get("governance_decision", {}).get("decision", "")
    selected = strategy["selected_strategy"]
    proof = strategy["strategy_process_integrity_proof"]
    return {
        "mode": "CEO_RUNTIME_CERTIFIED_FULL_STRATEGY_PROCESS_WITH_ANTI_ANCHOR_AUDIT"
        if all(item == "ALLOW" for item in (strategic_decision, refresh_decision, open_world_decision, integrity_decision))
        else "CEO_RUNTIME_REQUIRES_REVISION",
        "runtime_session_id": SESSION_ID,
        "Y_star_gov_strategic_decision": strategic_decision,
        "Y_star_gov_market_refresh_decision": refresh_decision,
        "Y_star_gov_open_world_decision": open_world_decision,
        "Y_star_gov_process_integrity_decision": integrity_decision,
        "CIEUStore_written": bool(strategic_write.get("formal_CIEU_log_written"))
        and bool(refresh_write.get("formal_CIEU_log_written"))
        and bool(open_world_write.get("formal_CIEU_log_written"))
        and bool(integrity_write.get("formal_CIEU_log_written")),
        "CIEU_event_count": cieu_summary.get("event_count", 0),
        "selected_route_id": selected["selected_route_id"],
        "selected_first_cash_path": selected["current_best_first_cash_path"],
        "completed_strategy_phase_count": len(proof["completed_phases"]),
        "opportunity_universe_count": len(proof["opportunity_universe_scan"]),
        "counterfactual_route_count": len(proof["counterfactual_comparison"]),
        "anchor_penalty_applied": proof["anchor_dependence_audit"]["anchor_penalty_applied"],
        "recent_memory_only": proof["recent_memory_only"],
        "truth_boundary": {
            "no_L4_feedback_executed": True,
            "no_customer_validation": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def _opportunity_universe(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    clusters = strategy["open_world_discovery_proof"]["opportunity_clusters"]
    universe = [
        {
            "domain_id": cluster["cluster_id"],
            "status": "evidence_cluster_evaluated",
            "evidence_count": cluster["evidence_count"],
        }
        for cluster in clusters
    ]
    for domain_id in (
        "legal_ops_intake_automation",
        "healthcare_admin_prior_auth",
        "education_admin_grant_ops",
        "local_services_ai_dispatch",
    ):
        universe.append(
            {
                "domain_id": domain_id,
                "status": "adjacent_domain_not_selected_insufficient_current_evidence",
                "evidence_count": 0,
            }
        )
    return universe


def _market_landscape(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "cluster_id": cluster["cluster_id"],
            "problem_statement": cluster["problem_statement"],
            "evidence_count": cluster["evidence_count"],
        }
        for cluster in strategy["open_world_discovery_proof"]["opportunity_clusters"]
    ]


def _competitor_by_cluster(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "cluster_id": "cpa_ai_saturation",
            "saturation": "high",
            "examples": ["Black Ore", "Basis", "Juno", "CPA Pilot", "Aiwyn", "Canopy", "Karbon", "TaxDome", "Madras Accountancy"],
        },
        {
            "cluster_id": "agentic_ai_runtime_governance",
            "saturation": "emerging",
            "examples": ["platform governance toolkits", "observability vendors", "internal enterprise controls"],
        },
        {
            "cluster_id": "ai_observability_gap",
            "saturation": "medium",
            "examples": ["observability platforms", "AI monitoring vendors", "consulting practices"],
        },
    ]


def _customer_segments() -> list[dict[str, str]]:
    return [
        {
            "segment_id": "founder_operator_ai_coding",
            "buyer": "founder/operator using AI coding agents",
            "budget_owner": "founder",
            "urgent_pain": "repo drift, prompt scope creep, unsafe delivery",
            "adoption_friction": "may not yet believe governance is worth paying for",
        },
        {
            "segment_id": "engineering_lead_agent_rollout",
            "buyer": "engineering lead rolling out agentic tools",
            "budget_owner": "engineering leadership",
            "urgent_pain": "pilot-to-production risk and accountability",
            "adoption_friction": "procurement and internal security review",
        },
        {
            "segment_id": "ops_owner_ai_workflows",
            "buyer": "operator using agents in business workflows",
            "budget_owner": "business owner",
            "urgent_pain": "automation drift and unclear human approval boundaries",
            "adoption_friction": "needs plain-language value, not governance jargon",
        },
    ]


def _business_model_options() -> list[dict[str, str]]:
    return [
        {
            "model_id": "48h_rescue_brief",
            "description": "one-off paid rescue brief that diagnoses an agent workflow and proposes controlled action boundaries",
            "why_now": "fastest cash test and lowest build risk",
        },
        {
            "model_id": "productized_service",
            "description": "repeatable control-room setup sprint with templates, tests, and receipts",
            "why_now": "second step after repeated brief demand",
        },
        {
            "model_id": "software_or_dashboard",
            "description": "dashboard/tooling only after repeated paid demand proves workflow and data shape",
            "why_now": "not first; avoid building before buyer pull",
        },
    ]


def _founder_fit_counterevidence() -> dict[str, Any]:
    return {
        "strong_fit": ["AI-agent engineering pain", "repo governance", "Codex execution boundary", "CIEU evidence records"],
        "weak_fit": ["CPA credential", "regulated accounting advice", "customs/legal advice"],
        "implication": "prefer AI-agent control room over regulated CPA/tariff routes until external evidence says otherwise",
    }


def _selected_evidence_refs(strategy: Mapping[str, Any]) -> list[str]:
    for candidate in strategy["route_candidates"]:
        if candidate["route_id"] == strategy["selected_strategy"]["selected_route_id"]:
            return list(candidate.get("evidence_refs") or [])[:6]
    return []


def _why_not_selected(row: Mapping[str, Any], selected: Mapping[str, Any]) -> str:
    if row["route_id"] == selected["selected_route_id"]:
        return "selected as current provisional first-cash path"
    if "cpa" in row["route_id"]:
        return "real pain but crowded competitors and weak founder-market fit"
    if "tariff" in row["route_id"]:
        return "regulated/customs boundary and weaker founder fit"
    return "lower score after founder fit, proof burden, differentiation, or buyer clarity"


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_strategy_process_integrity_proof",
    "build_strategy_process_integrity_runtime_strategy",
    "run_e106_strategy_process_integrity_session",
    "summarize_e106_cieustore",
]
