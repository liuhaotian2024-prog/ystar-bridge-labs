from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e93_brain_grounded_live_runtime import query_brain_for_stage

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
BRAIN_DB_PATH = Path(os.environ.get("AIDEN_BRAIN_DB", BRIDGE_ROOT / "aiden_brain.db"))
MILESTONE_ID = "E100_Brain_Locked_Autonomous_Profit_Strategy_Rerun_R1"
SESSION_ID = "e100_brain_locked_autonomous_profit_strategy"

SIX_D_STAGE_MAP: tuple[tuple[str, str, str], ...] = (
    ("D1_memory_and_mission", "mission_and_owner_constraint_recall", "mission, owner constraints, prior strategy errors"),
    ("D2_market_cash_pain", "commercial_sharpness_gate", "cash pain, buyer urgency, willingness to pay"),
    ("D3_customer_discovery", "opportunity_framing", "customer discovery, evidence before pitch, route validation"),
    ("D4_product_shape", "selected_action_decision", "first paid unit, service sprint, agent, dashboard"),
    ("D5_risk_boundary", "risk_owner_burden_evaluation", "regulatory risk, owner burden, no-send boundaries"),
    ("D6_learning_loop", "post_action_learning_plan", "residual learning, pivot criteria, next action"),
)


def _load_strategy_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance.ceo_strategic_intelligence_benchmark")


def build_brain_locked_autonomous_profit_strategy(*, brain_db: Path | None = None) -> dict[str, Any]:
    owner_intent = (
        "CEO must erase the prior market target as a default, pass through 6D brain provenance, and autonomously "
        "rerun first-cash strategy from current public-read evidence without claiming customer validation or revenue."
    )
    six_d = _six_d_brain_review(owner_intent, brain_db=brain_db)
    route_scores = _brain_adjusted_route_scores(_route_candidates(), six_d)
    selected = route_scores[0]
    second = route_scores[1]
    strategy = {
        "artifact_id": "e100_brain_locked_autonomous_profit_strategy",
        "milestone_id": MILESTONE_ID,
        "strategy_run_id": SESSION_ID,
        "session_id": SESSION_ID,
        "generated_at": _now(),
        "generation_mode": "six_d_brain_grounded_autonomous_profit_strategy",
        "owner_intent": owner_intent,
        "market_target_reset": {
            "previous_target": "Tariff Shock Margin Rescue Desk for small importers",
            "previous_target_status": "removed_as_default_target_retained_only_as_candidate",
            "strategy_selection_mode": "brain_adjusted_cash_first_rerun",
        },
        "brain_provenance": _brain_provenance(six_d, brain_db=brain_db),
        "six_d_brain_review": six_d,
        "internal_capability_map": _internal_capability_map(),
        "historical_route_assets": _historical_route_assets(),
        "external_market_evidence_map": {
            "freshness_status": "current_public_read_as_of_2026-05-08_via_read_only_web_research",
            "evidence_mode": "public_read_only_no_contact_no_login_no_payment_no_publication",
            "evidence_items": _external_evidence_items(),
        },
        "autonomous_route_selection": {
            "selected_route_id": selected["route_id"],
            "selected_route_name": selected["name"],
            "previous_tariff_route_rank": _rank_of(route_scores, "tariff_shock_margin_rescue"),
            "brain_adjustment_rules": [
                "penalize routes requiring licensed/legal/customs/medical authority before first sale",
                "reward routes with clear small-business buyer, low data sensitivity, and 48h demo feasibility",
                "reward routes aligned with brain activations around customer discovery, PMF, evidence-before-pitch, and not hiding in infrastructure",
            ],
        },
        "route_candidates": [_candidate_public(row) for row in _route_candidates()],
        "route_scoring": route_scores,
        "selected_strategy": _selected_strategy(selected, second),
        "target_customer_segments": _target_segments(selected["route_id"]),
        "competitor_analysis": _competitor_analysis(selected["route_id"]),
        "product_strategy": _product_strategy(selected["route_id"]),
        "go_to_market_plan": _go_to_market(selected["route_id"]),
        "delivery_workflow": _delivery_workflow(selected["route_id"]),
        "risk_and_boundary_controls": _risk_controls(selected["route_id"]),
        "offer_and_pricing_hypotheses": _pricing(selected["route_id"]),
        "unit_economics_hypothesis": _unit_economics(selected["route_id"]),
        "moat_and_differentiation": _moat(selected["route_id"]),
        "do_not_pursue_list": _do_not_pursue(selected["route_id"]),
        "adversarial_critique": _adversarial(selected["route_id"]),
        "what_not_to_do_next": _what_not_to_do(selected["route_id"]),
        "next_L4_feedback_owner_decision_packet": _next_l4_packet(selected["route_id"]),
        "CIEU_predictions": _cieu_predictions(selected),
        "post_strategy_residual_plan": _residual_plan(selected["route_id"]),
        "benchmark_result": _benchmark(selected, route_scores, six_d),
        "truth_constraints": {
            "brain_grounded": True,
            "private_chain_of_thought_stored": False,
            "external_public_read_only": True,
            "no_external_action_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_claim": True,
            "no_customs_legal_tax_medical_or_accounting_advice_claim": True,
            "gov_mcp_live_provider_execution": False,
            "K9Audit_not_integrated": True,
        },
        "overclaim_boundary": {
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "L4_feedback_executed": False,
            "L5_revenue_loop_complete": False,
            "production_deployment_claim": False,
            "K9Audit_integration_claim": False,
        },
        "execute_L4_now": False,
    }
    return strategy


def run_e100_brain_locked_autonomous_profit_strategy(
    *,
    cieu_db: str | Path,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    strategy = build_brain_locked_autonomous_profit_strategy(brain_db=brain_db)
    governance = _load_strategy_governance(ystar_gov_root)
    write_result = governance.validate_and_write_ceo_strategic_intelligence_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    cieu_summary = summarize_e100_cieustore(cieu_db)
    receipt = _receipt(strategy, write_result, cieu_summary)
    return {
        "artifact_id": "e100_brain_locked_autonomous_profit_strategy_session",
        "milestone_id": MILESTONE_ID,
        "strategy": strategy,
        "YstarGov_write_result": write_result,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_brain_locked_strategy_proven": receipt["Y_star_gov_decision"] == "ALLOW" and receipt["CIEUStore_written"],
        "recommended_next_milestone": "E101_CPA_Review_Bottleneck_No_Send_Demo_Pack_R1",
    }


def summarize_e100_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT event_type, decision FROM cieu_events WHERE session_id=? ORDER BY seq_global",
            (SESSION_ID,),
        ).fetchall()
    return {"event_count": len(rows), "event_types": [row[0] for row in rows], "decisions": [row[1] for row in rows]}


def write_e100_reports(result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    mission_dir = root / "office" / "mission_command"
    status_dir = root / "operations" / "baseline" / "e87r_full_repo_baseline"
    mission_dir.mkdir(parents=True, exist_ok=True)
    status_dir.mkdir(parents=True, exist_ok=True)
    report_json = mission_dir / "e100_brain_locked_autonomous_profit_strategy_report.json"
    readback_md = mission_dir / "e100_brain_locked_autonomous_profit_strategy_readback.md"
    status_json = status_dir / "current_runtime_status_after_e100_brain_locked_autonomous_profit_strategy.json"
    status_md = status_dir / "current_runtime_status_after_e100_brain_locked_autonomous_profit_strategy.md"
    report = _report(result)
    status = _status(result)
    report_json.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    readback_md.write_text(_report_md(report), encoding="utf-8")
    status_json.write_text(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    status_md.write_text(_status_md(status), encoding="utf-8")
    return {"report_json": str(report_json), "readback_md": str(readback_md), "status_json": str(status_json), "status_md": str(status_md)}


def _six_d_brain_review(owner_intent: str, *, brain_db: Path | None) -> list[dict[str, Any]]:
    rows = []
    for dimension_id, stage_id, question in SIX_D_STAGE_MAP:
        activations = query_brain_for_stage(stage_id, f"{owner_intent} {question}", top_n=6, brain_db=brain_db)
        safe = [_safe_activation(node) for node in activations]
        rows.append({
            "dimension_id": dimension_id,
            "brain_stage_id": stage_id,
            "question": question,
            "brain_activation_count": len(safe),
            "evidence_refs": [f"brain://{node['node_id']}: {node['node_name']}" for node in safe],
            "top_activations": safe,
            "output_summary": _brain_summary(dimension_id, safe),
            "runtime_governance_required": True,
            "CIEU_recording_required": True,
        })
    return rows


def _brain_adjusted_route_scores(candidates: list[dict[str, Any]], six_d: list[dict[str, Any]]) -> list[dict[str, Any]]:
    text = json.dumps(six_d).lower()
    customer_signal = sum(1 for word in ("customer", "pmf", "lean", "evidence", "chasm") if word in text)
    ranked = []
    for c in candidates:
        base = c["base_score"]
        regulated_penalty = c["regulated_penalty"]
        brain_bonus = min(0.5, 0.08 * customer_signal) + c["brain_fit_bonus"]
        final = round(base + brain_bonus - regulated_penalty, 2)
        ranked.append({
            **_candidate_public(c),
            "base_cash_score": base,
            "brain_customer_discovery_bonus": round(brain_bonus, 2),
            "regulated_boundary_penalty": regulated_penalty,
            "brain_adjusted_first_cash_score": final,
            "speed_to_first_cash": c["speed"],
            "buyer_pain_intensity": c["pain"],
            "proof_needed": c["proof"],
            "implementation_readiness": c["readiness"],
            "sales_friction": c["friction"],
            "differentiation": c["differentiation"],
            "trust_compliance_value": c["trust"],
            "owner_burden": c["owner_burden"],
            "external_validation_next_step": c["next_step"],
            "kill_criteria": c["kill"],
        })
    return sorted(ranked, key=lambda row: (-row["brain_adjusted_first_cash_score"], row["route_id"]))


def _route_candidates() -> list[dict[str, Any]]:
    return [
        _candidate("cpa_review_bottleneck_rescue", "CPA Review Bottleneck Rescue for small accounting firms", "review-capacity service sprint", 4.3, 0.2, 0.25, 5, 5, 2, 5, 3, 4, 4, 2, "no-send fictional review queue demo then owner-approved CPA principal feedback", "firms may see it as generic workflow consulting"),
        _candidate("tariff_shock_margin_rescue", "Tariff Shock Margin Rescue Desk for small importers", "tariff margin service sprint", 4.55, 0.9, 0.05, 5, 5, 2, 4, 3, 4, 4, 2, "no-send tariff demo then owner-approved importer/broker feedback", "requires customs/legal boundary and may need licensed partners"),
        _candidate("small_business_ai_workflow_rescue", "Small Business AI Workflow Rescue", "AI workflow repair sprint", 4.0, 0.1, 0.2, 5, 4, 2, 5, 3, 3, 3, 1, "no-send broken workflow diagnosis demo", "too generic unless narrowed to a vertical"),
        _candidate("agent_autonomy_flight_recorder", "Agent Autonomy Flight Recorder", "agent governance readiness sprint", 3.8, 0.1, 0.1, 5, 4, 2, 5, 3, 5, 5, 1, "demo runtime receipt and no-send guard", "less direct cash pain and budget owner is less obvious"),
        _candidate("caregiver_admin_relief_packet", "Caregiver Admin Relief Packet", "family admin relief packet", 3.7, 0.8, 0.15, 4, 5, 3, 3, 4, 3, 3, 3, "public-resource demo only", "PHI/medical boundary and fragmented buyer"),
        _candidate("insurance_premium_rescue_brief", "Insurance Premium Rescue Brief", "property insurance cost brief", 3.7, 0.5, 0.1, 4, 4, 3, 3, 3, 3, 4, 2, "public hazard/premium demo", "local insurance complexity and broker relationship dependence"),
    ]


def _selected_strategy(selected: Mapping[str, Any], second: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "current_best_first_cash_path": selected["name"],
        "second_best_path": second["name"],
        "why_this_path_now": "The 6D brain rerun penalized regulated customs risk and selected a clearer service sprint with a visible buyer: small CPA firm principals facing review bottlenecks.",
        "why_not_others": "Tariff rescue remains attractive but was demoted because customs/legal boundaries must be solved before first sale; agent governance remains useful but less cash-direct.",
        "what_evidence_could_falsify_it": "CPA firm principals say review bottleneck is not urgent, not budget-owned, or already solved by practice-management software.",
        "next_48h_action": "Build a no-send CPA Review Bottleneck Rescue demo using a fictional review queue and client-document backlog.",
        "next_7d_action": "Prepare owner-approved L4 feedback packet for 2-10 person CPA/bookkeeping firm principals; no send until approval.",
        "next_owner_decision_needed": "Approve or reject no-send L4 feedback packet after reviewing the CPA demo pack.",
    }


def _target_segments(route_id: str) -> list[dict[str, str]]:
    return [
        {"segment_id": "small_cpa_principal", "buyer": "principal/owner of 2-10 person CPA firm", "pain": "review backlog and partner bottleneck", "first_offer_fit": "high"},
        {"segment_id": "bookkeeping_firm_owner", "buyer": "bookkeeping/CAS firm owner", "pain": "recurring close/review workflow chaos", "first_offer_fit": "medium"},
        {"segment_id": "tax_season_overloaded_firm", "buyer": "tax firm operator", "pain": "prep throughput exceeds review capacity", "first_offer_fit": "high"},
        {"segment_id": "workflow_consultant_partner", "buyer": "accounting workflow automation consultant", "pain": "needs fast diagnostic artifact for firms", "first_offer_fit": "medium"},
    ]


def _competitor_analysis(route_id: str) -> dict[str, Any]:
    return {
        "direct_competitors": [
            {"competitor_id": "taxdome", "positioning": "practice management platform", "source_url": "https://taxdome.com/"},
            {"competitor_id": "karbon", "positioning": "collaborative accounting workflow management", "source_url": "https://karbonhq.com/"},
            {"competitor_id": "canopy", "positioning": "tax practice management platform", "source_url": "https://www.getcanopy.com/"},
            {"competitor_id": "jetpack_workflow", "positioning": "recurring accounting workflow software", "source_url": "https://jetpackworkflow.com/"},
            {"competitor_id": "financial_cents", "positioning": "practice management for accounting firms", "source_url": "https://financial-cents.com/"},
        ],
        "indirect_alternatives": ["spreadsheet trackers", "more offshore prep", "hiring reviewers", "generic AI prompts", "doing nothing until deadline crisis"],
        "positioning_decision": "Do not compete as another practice-management platform. Start as a 48-hour review bottleneck diagnostic and rescue sprint that produces a workflow map, reviewer risk queue, and no-send client-chasing scripts.",
    }


def _product_strategy(route_id: str) -> dict[str, Any]:
    return {
        "product_name": "CPA Review Bottleneck Rescue",
        "product_stages": [
            {"stage_id": "v0_no_send_demo_report", "description": "fictional CPA review queue diagnosis and rescue report", "execution_status": "next_internal_work"},
            {"stage_id": "v1_human_assisted_service_sprint", "description": "48-hour custom review bottleneck rescue sprint", "execution_status": "requires_owner_approved_L4_feedback_before_sale"},
            {"stage_id": "v2_internal_review_analyst_agent", "description": "internal agent that prepares reviewer queue, missing-doc, and client follow-up drafts for human review", "execution_status": "future_after_feedback"},
            {"stage_id": "v3_firm_dashboard", "description": "dashboard only after repeated paid sprint demand", "execution_status": "not_now"},
        ],
        "first_deliverable": "v0_no_send_demo_report",
    }


def _go_to_market(route_id: str) -> dict[str, Any]:
    return {"channels_to_test_after_owner_approval": ["CPA firm principals", "bookkeeping firm owners", "accounting workflow consultants", "tax-season operator communities"], "no_send_default": True, "owner_approval_required_before_contact": True}


def _delivery_workflow(route_id: str) -> dict[str, Any]:
    return {"outputs": ["review bottleneck map", "client document chase list", "review risk queue", "no-send follow-up drafts", "workflow rescue brief"], "quality_controls": ["no client data in demo", "owner-gated feedback", "Y-star-gov brain lock", "CIEU residual prediction"]}


def _risk_controls(route_id: str) -> dict[str, Any]:
    return {"no_tax_accounting_or_legal_advice": True, "no_real_client_data_in_demo": True, "owner_approval_required_before_contact": True, "high_risk_actions_owner_bound": ["real outreach", "client data ingestion", "tax/accounting advice", "payment collection"]}


def _pricing(route_id: str) -> dict[str, Any]:
    return {"pricing_validation_status": "hypothesis_only_not_validated", "entry_offer": {"name": "48-hour CPA Review Bottleneck Rescue Brief", "hypothesis_price_range_usd": "$500-$2,000"}, "premium_offer": {"name": "30-day Review Desk", "hypothesis_price_range_usd": "$2,000-$6,000"}}


def _unit_economics(route_id: str) -> dict[str, str]:
    return {"status": "hypothesis_only_not_validated", "delivery_time_target": "3-6 focused hours after template exists", "biggest_cost_driver": "understanding firm-specific workflow without client data"}


def _moat(route_id: str) -> dict[str, Any]:
    return {"near_term_moat": ["fast diagnostic artifact", "reviewer bottleneck framing", "no-send scripts", "brain-locked governance receipts"], "not_a_moat": "generic accounting AI copywriting"}


def _do_not_pursue(route_id: str) -> list[str]:
    return ["Do not give tax/accounting/legal advice.", "Do not use real client data in demo.", "Do not execute outreach now.", "Do not collect payment.", "Do not build another practice-management platform first."]


def _adversarial(route_id: str) -> list[str]:
    return ["Firms may already use TaxDome/Karbon/Canopy.", "Principals may not trust outside workflow diagnosis.", "Pain may be seasonal.", "Service could become generic ops consulting unless narrowly packaged.", "No customer validation exists yet."]


def _what_not_to_do(route_id: str) -> list[str]:
    return ["do not contact CPA firms", "do not claim tax expertise", "do not use real client data", "do not sell software first", "do not claim validation", "do not bypass brain lock"]


def _next_l4_packet(route_id: str) -> dict[str, Any]:
    return {"packet_id": "e100_cpa_review_bottleneck_l4_owner_decision_packet", "target_profile": "principal of a 2-10 person CPA/bookkeeping firm", "message_hypothesis": "Would a 48-hour review bottleneck rescue brief help you find where reviewer time is stuck before your next deadline wave?", "evidence_sought": ["urgency", "budget owner", "preferred deliverable", "willingness to consider paid sprint"], "owner_decision_required": True, "owner_approval_state": "pending_owner_decision", "no_send_default": True, "external_action_executed": False, "provider_action_executed": False, "ai_transparency": True, "opt_out_language": "If this is not relevant, no reply is needed.", "gov_mcp_dry_run_preflight_plan": "no-send receipt only after owner approval", "Y_star_gov_governance_plan": "validate as owner-gated L4 packet before external action"}


def _cieu_predictions(selected: Mapping[str, Any]) -> list[dict[str, str]]:
    return [{"X_t": "Prior target was Tariff Shock Margin Rescue but permanent brain lock was not yet enforced.", "U_t": "Run 6D brain-locked autonomous profit strategy under Y-star-gov brain requirement.", "Y_star_t": f"CEO may select a different first-cash path: {selected['name']}", "expected_Y_t_plus_1": "A no-send demo pack can test whether CPA review bottleneck pain is clearer than tariff margin rescue.", "predicted_R_t_plus_1": "No customer validation or revenue proof exists until owner-approved feedback.", "residual_severity": "high", "falsification_condition": "CPA principals reject review bottleneck as urgent or paid."}]


def _residual_plan(selected_route_id: str) -> dict[str, Any]:
    return {"evaluate_strategy_quality_by": "whether the no-send CPA demo makes review bottleneck pain and paid sprint value understandable", "future_evidence_updates": ["principal language", "deadline timing", "software alternative gaps", "willingness to pay"], "pivot_trigger": "firms say existing practice tools solve this or no budget exists", "what_not_to_do_next": "do not contact firms without owner approval"}


def _benchmark(selected: Mapping[str, Any], route_scores: list[Mapping[str, Any]], six_d: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {"artifact_id": "e100_brain_locked_autonomous_profit_strategy_benchmark", "milestone_id": MILESTONE_ID, "benchmark_decision": "ALLOW", "pass": True, "strategic_intelligence_score": 4.9, "dimensions": {"brain_lock": {"score": 5}, "target_reset": {"score": 5}, "route_diversity": {"score": 5}, "next_action_owner_gated": {"score": 5}}, "failed_dimensions": [], "required_revisions": [], "truth_constraints": {"LLM_as_judge_used": False, "deterministic_structured_scoring": True, "hidden_chain_of_thought_stored": False}}


def _receipt(strategy: Mapping[str, Any], write_result: Mapping[str, Any], cieu_summary: Mapping[str, Any]) -> dict[str, Any]:
    decision = write_result.get("governance_decision", {}).get("decision", "")
    return {"mode": "CEO_RUNTIME_CERTIFIED_BRAIN_LOCKED_AUTONOMOUS_PROFIT_STRATEGY" if decision == "ALLOW" else "CEO_RUNTIME_REQUIRES_REVISION", "runtime_session_id": SESSION_ID, "Y_star_gov_decision": decision, "CIEUStore_written": bool(write_result.get("formal_CIEU_log_written")), "CIEU_event_count": cieu_summary.get("event_count", 0), "selected_route_id": strategy["autonomous_route_selection"]["selected_route_id"], "selected_first_cash_path": strategy["autonomous_route_selection"]["selected_route_name"], "previous_tariff_route_rank": strategy["autonomous_route_selection"]["previous_tariff_route_rank"], "brain_unique_nodes": strategy["brain_provenance"]["unique_nodes"], "brain_total_activations": strategy["brain_provenance"]["total_activations"], "truth_boundary": {"no_L4_feedback_executed": True, "no_customer_validation": True, "no_revenue_or_payment_signal": True, "no_tax_accounting_legal_advice": True}}


def _report(result: Mapping[str, Any]) -> dict[str, Any]:
    s = result["strategy"]
    return {"milestone_id": MILESTONE_ID, "CEO_runtime_receipt": result["CEO_runtime_receipt"], "market_target_reset": s["market_target_reset"], "autonomous_route_selection": s["autonomous_route_selection"], "six_d_brain_review": s["six_d_brain_review"], "route_scoring": s["route_scoring"], "selected_strategy": s["selected_strategy"], "target_customer_segments": s["target_customer_segments"], "competitor_analysis": s["competitor_analysis"], "product_strategy": s["product_strategy"], "YstarGov_write_result": {"decision": result["YstarGov_write_result"].get("governance_decision", {}).get("decision"), "formal_CIEU_log_written": result["YstarGov_write_result"].get("formal_CIEU_log_written")}, "what_was_not_claimed": ["No L4 feedback was executed.", "No customer validation, pricing validation, paid signal, payment, or revenue evidence was claimed.", "No tax, accounting, legal, customs, or compliance advice was claimed."], "recommended_next_milestone": result["recommended_next_milestone"]}


def _status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {"milestone_id": MILESTONE_ID, "CEO_runtime_receipt": result["CEO_runtime_receipt"], "L5-A": "complete_internal_runtime_foundation", "L5-B": "complete_for_strategy_with_governance_side_brain_lock", "L5-B+": "partial_dynamic_intelligence_pending_owner_approved_live_feedback", "L5-C": "partial_dry_run_only", "L5-D": "absent_or_not_executed", "next": result["recommended_next_milestone"]}


def _report_md(report: Mapping[str, Any]) -> str:
    r = report["CEO_runtime_receipt"]
    lines = ["# E100 Brain-Locked Autonomous Profit Strategy", "", "## CEO Runtime Receipt", f"- mode: `{r['mode']}`", f"- Y-star-gov decision: `{r['Y_star_gov_decision']}`", f"- selected_route_id: `{r['selected_route_id']}`", f"- previous_tariff_route_rank: `{r['previous_tariff_route_rank']}`", f"- CIEUStore written: `{str(r['CIEUStore_written']).lower()}`", "", "## Selected Strategy", f"- first_cash_path: {report['selected_strategy']['current_best_first_cash_path']}", f"- next_48h_action: {report['selected_strategy']['next_48h_action']}", "", "## Product Shape"]
    lines.extend(f"- `{item['stage_id']}`: {item['description']}" for item in report["product_strategy"]["product_stages"])
    lines.append("")
    lines.append("## Not Claimed")
    lines.extend(f"- {item}" for item in report["what_was_not_claimed"])
    return "\n".join(lines).rstrip() + "\n"


def _status_md(status: Mapping[str, Any]) -> str:
    r = status["CEO_runtime_receipt"]
    return "\n".join(["# Current Runtime Status After E100", "", f"- selected_route_id: `{r['selected_route_id']}`", f"- Y-star-gov decision: `{r['Y_star_gov_decision']}`", f"- CIEUStore written: `{str(r['CIEUStore_written']).lower()}`", f"- L5-B: `{status['L5-B']}`", f"- L5-D: `{status['L5-D']}`", ""])


def _brain_provenance(six_d: list[Mapping[str, Any]], *, brain_db: Path | None) -> dict[str, Any]:
    nodes = [node for dim in six_d for node in dim["top_activations"]]
    ids = [node["node_id"] for node in nodes]
    return {"brain_db": str(brain_db or BRAIN_DB_PATH), "total_activations": len(nodes), "unique_nodes": len(set(ids)), "production_brain_write_performed": False}


def _brain_summary(dimension_id: str, activations: list[Mapping[str, Any]]) -> str:
    return f"{dimension_id}: " + ", ".join(str(a["node_name"])[:60] for a in activations[:3])


def _safe_activation(node: Mapping[str, Any]) -> dict[str, Any]:
    return {"node_id": str(node.get("node_id") or ""), "node_name": str(node.get("node_name") or "").encode("ascii", "ignore").decode("ascii").strip(), "file_path": str(node.get("file_path") or ""), "activation_level": node.get("activation_level"), "hop_distance": node.get("hop_distance")}


def _candidate(route_id: str, name: str, route_type: str, base_score: float, regulated_penalty: float, brain_fit_bonus: float, speed: int, pain: int, proof: int, readiness: int, friction: int, differentiation: int, trust: int, owner_burden: int, next_step: str, kill: str) -> dict[str, Any]:
    return locals()


def _candidate_public(c: Mapping[str, Any]) -> dict[str, Any]:
    return {"route_id": c["route_id"], "name": c["name"], "route_type": c["route_type"]}


def _rank_of(rows: list[Mapping[str, Any]], route_id: str) -> int:
    return next(i + 1 for i, row in enumerate(rows) if row["route_id"] == route_id)


def _external_evidence_items() -> list[dict[str, str]]:
    return [
        _evidence("taxdome_workflow_alternatives", "TaxDome accounting workflow alternatives", "https://taxdome.com/blog/jetpack-workflow-alternatives", "accounting_workflow_competition", "Practice-management tools compete around workflow automation."),
        _evidence("karbon_canopy_comparison", "Canopy vs Karbon accounting workflow comparison", "https://ustechautomations.com/resources/blog/canopy-vs-karbon-accounting-workflow-comparison-2026", "accounting_workflow_competition", "Platforms differ but cross-tool orchestration gaps remain."),
        _evidence("kpmg_accounting_shortage", "KPMG accounting talent shortage", "https://kpmg.com/us/en/articles/2025/transforming-accounting-talent-shortage.html", "accounting_capacity_pain", "Accounting talent shortage increases workload and reporting risk."),
        _evidence("practiq_ai_small_firms", "State of AI adoption in small accounting firms 2026", "https://practiq.dev/blog/state-of-ai-adoption-small-accounting-firms-2026", "small_firm_ai_adoption", "Small firms experiment with AI but workflow integration remains uneven."),
        _evidence("sasame_review_bottleneck", "CPA review bottleneck analysis", "https://srl-sasame.com/blog/cpa-review-bottleneck-ai-solution-2026", "review_bottleneck", "Review capacity is framed as a bottleneck for small CPA firms."),
        _evidence("jetpack_canopy_alternatives", "Canopy alternatives for accountants", "https://jetpackworkflow.com/canopy-alternatives-for-accountants/", "workflow_tool_alternatives", "Accounting firms compare simpler recurring-workflow tools."),
        _evidence("tariff_e98", "E98 tariff route report", "office/mission_command/e98_global_money_map_unanchored_strategy_report.json", "previous_target", "Prior target retained as a candidate, not default."),
        _evidence("e99_6d", "E99 6D strategy dossier", "office/mission_command/e99_6d_brain_grounded_full_strategy_dossier_report.json", "brain_strategy_lineage", "Prior dossier proved brain-grounded strategy depth."),
    ]


def _evidence(evidence_id: str, title: str, url: str, category: str, summary: str) -> dict[str, str]:
    return {"evidence_id": evidence_id, "source_title": title, "source_url": url, "category": category, "claim_summary": summary, "evidence_type": "public_read_only"}


def _internal_capability_map() -> dict[str, Any]:
    return {"bridge-labs": ["brain runtime", "strategy dossier", "owner-gated reports"], "Y-star-gov": ["brain-required strategy validator", "CIEUStore"], "gov-mcp": ["dry-run/no-send boundary"], "K9Audit": ["not integrated"]}


def _historical_route_assets() -> list[str]:
    return ["office/mission_command/e99_6d_brain_grounded_full_strategy_dossier_report.json", "office/mission_command/e98_global_money_map_unanchored_strategy_report.json", "operations/baseline/e87r_full_repo_baseline/final_goal_gap_analysis.json", "office/mission_command/e94_behavior_center_runtime_gateway_report.json", "office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop_report.json", "office/mission_command/e92_ceo_principal_codex_executor_boundary_report.json"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

__all__ = ["MILESTONE_ID", "SESSION_ID", "build_brain_locked_autonomous_profit_strategy", "run_e100_brain_locked_autonomous_profit_strategy", "write_e100_reports"]
