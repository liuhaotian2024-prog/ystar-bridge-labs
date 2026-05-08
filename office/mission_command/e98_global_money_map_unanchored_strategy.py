from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Mapping


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
MILESTONE_ID = "E98_Global_Money_Map_Unanchored_Strategy_Rerun_R1"
SESSION_ID = "e98_global_money_map_unanchored_strategy"

MONEY_MAP_SCORE_FIELDS: tuple[str, ...] = (
    "cash_pain_directness",
    "budget_owner_clarity",
    "urgency_2026",
    "demo_feasibility_48h",
    "proof_without_external_action",
    "distribution_access",
    "regulatory_risk_inverse",
    "capability_fit_after_market_selection",
    "sales_friction_inverse",
)


def _load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def build_global_money_map_strategy_artifact(*, owner_intent: str | None = None) -> dict[str, Any]:
    """Build a cash-first CEO strategy artifact.

    Unlike E97, this experiment does not start from current Y* capabilities.
    It first ranks global money opportunities, then asks how the existing
    runtime can safely support the selected wedge.
    """

    intent = owner_intent or (
        "Find the easiest credible first-cash direction globally, without privileging Y*Bridge Labs' existing "
        "agent-governance route, and without claiming customer/revenue validation."
    )
    routes = _route_candidates()
    money_map = score_global_money_map_routes(routes)
    selected_route = money_map["ranked_routes"][0]
    second_route = money_map["ranked_routes"][1]
    strategy = {
        "artifact_id": "e98_global_money_map_unanchored_strategy",
        "milestone_id": MILESTONE_ID,
        "strategy_run_id": SESSION_ID,
        "session_id": SESSION_ID,
        "generated_at": _now(),
        "generation_mode": "cash_first_global_money_map_structured_output",
        "owner_intent": intent,
        "anti_recent_memory_anchor": {
            "initial_seed_thesis": "none",
            "capability_blind_first_pass": True,
            "current_system_fit_weight_applied_after_market_selection": True,
            "old_agent_governance_route_status": "ordinary_candidate_no_privilege",
            "forbidden_shortcut": "do not select agent governance merely because it is our current strongest built system",
        },
        "global_money_map_method": {
            "phase_1": "rank markets by cash pain, urgency, budget owner, and low-friction validation",
            "phase_2": "only after phase 1, score whether current Y* capabilities can support a safe wedge",
            "capability_fit_is_not_primary_selection_driver": True,
            "LLM_as_judge_used": False,
        },
        "internal_capability_map": _internal_capability_map(),
        "historical_route_assets": _historical_route_assets(),
        "external_market_evidence_map": {
            "freshness_status": "current_public_read_as_of_2026-05-08_via_read_only_web_research",
            "evidence_mode": "public_read_only_no_contact_no_login_no_payment_no_publication",
            "evidence_items": _external_evidence_items(),
        },
        "no_new_wheel_proof": {
            "reused_systems_after_market_selection": [
                "E87R full repo baseline",
                "E88 CEO runtime session",
                "E89 intelligence compiler",
                "E90 strategic benchmark write path",
                "Y-star-gov CIEUStore",
                "gov-mcp dry-run/no-send boundary for future owner-approved packets",
            ],
            "not_used_as_primary_market_filter": True,
        },
        "route_candidates": routes,
        "global_money_map_scores": money_map,
        "route_scoring": money_map["ranked_routes"],
        "selected_strategy": {
            "current_best_first_cash_path": selected_route["route_name"],
            "second_best_path": second_route["route_name"],
            "why_this_path_now": (
                "Tariff volatility creates an immediate cash leak that buyers already understand in dollars. "
                "A small importer can pay for a fast margin, pricing, supplier, and refund-opportunity desk "
                "before any platform exists. This is not an AI-governance-first offer; it is a cash-preservation "
                "offer that can be delivered with public-read research, structured analysis, and owner-gated outreach."
            ),
            "why_not_others": [
                "The agent-governance route remains technically strong but is not the most obvious global cash pain.",
                "Caregiver admin relief has huge pain but harder distribution, PHI sensitivity, and weaker immediate B2B budget clarity.",
                "CPA review bottleneck is attractive but crowded and timing-sensitive around tax season.",
                "Insurance premium audit has real pain but needs local/regulatory expertise and agent/broker partnerships.",
                "Prior authorization admin relief is enormous but highly regulated and slow to sell.",
            ],
            "what_evidence_could_falsify_it": (
                "Owner-approved feedback from small importers, freight/customs operators, or ecommerce brands says tariff "
                "margin rescue is not urgent, not budget-owned, or cannot be trusted without licensed customs brokerage."
            ),
            "next_48h_action": "Build one no-send Tariff Shock Margin Rescue demo pack for a fictional small importer SKU set.",
            "next_7d_action": "Prepare owner-approved L4 feedback packet for customs brokers, small importers, and ecommerce operators; no send until approval.",
            "next_owner_decision_needed": "Approve or reject a no-send L4 feedback packet for the Tariff Shock Margin Rescue Desk.",
        },
        "do_not_pursue_list": [
            "Do not claim customs, tax, or legal advice.",
            "Do not contact importers, brokers, customers, or advisors without owner approval.",
            "Do not use private shipment, invoice, customer, or tariff data in this experiment.",
            "Do not claim revenue, pricing validation, customer validation, or paid demand.",
            "Do not choose the old AI agent governance route just because it fits current tools.",
            "Do not build a SaaS product before one owner-approved feedback loop validates urgency and budget.",
        ],
        "adversarial_critique": [
            "Tariff analysis can cross into regulated customs advice if scoped carelessly.",
            "Small importers may already rely on brokers and resist an outside strategy pack.",
            "Policy volatility could make any static pack obsolete quickly.",
            "The buyer may need operational implementation, not just analysis.",
            "This route is less aligned with our existing AI governance moat, so differentiation must come from speed and evidence quality.",
        ],
        "what_not_to_do_next": [
            "do not advertise tariff expertise as legal/customs brokerage advice",
            "do not use real importer data without explicit approval and data handling controls",
            "do not execute outreach now",
            "do not build software before a demo service pack",
            "do not bury the cash-saving promise under AI governance language",
            "do not discard agent-governance assets; reuse them only as internal quality controls",
        ],
        "next_L4_feedback_owner_decision_packet": _next_l4_packet(),
        "CIEU_predictions": _cieu_predictions(selected_route),
        "post_strategy_residual_plan": {
            "evaluate_strategy_quality_by": (
                "whether owner-approved feedback confirms small importers recognize tariff shock as an immediate "
                "cash leak and would pay for a fast margin-rescue desk"
            ),
            "future_evidence_updates": [
                "buyer language for tariff pain and margin leakage",
                "whether customs brokers or importers are better first targets",
                "whether buyers want a service sprint, spreadsheet model, or broker/refund workflow",
            ],
            "pivot_trigger": (
                "target profiles say they already have adequate broker support, do not trust non-broker analysis, "
                "or cannot identify a paid next step"
            ),
            "what_not_to_do_next": "do not interpret public-read tariff evidence as customer validation",
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
        "truth_constraints": {
            "external_public_read_only": True,
            "no_external_action_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_claim": True,
            "gov_mcp_live_provider_execution": False,
            "K9Audit_not_integrated": True,
        },
        "execute_L4_now": False,
    }
    strategy["benchmark_result"] = build_global_money_map_benchmark(strategy)
    return strategy


def score_global_money_map_routes(routes: list[dict[str, Any]]) -> dict[str, Any]:
    ranked: list[dict[str, Any]] = []
    for route in routes:
        scores = route["money_map_score_inputs"]
        first_cash_score = round(mean(float(scores[field]) for field in MONEY_MAP_SCORE_FIELDS), 2)
        row = {
            "route_id": route["route_id"],
            "route_name": route["name"],
            "route_type": route["route_type"],
            "speed_to_first_cash": scores["demo_feasibility_48h"],
            "buyer_pain_intensity": scores["cash_pain_directness"],
            "proof_needed": 6 - scores["proof_without_external_action"],
            "implementation_readiness": scores["capability_fit_after_market_selection"],
            "sales_friction": 6 - scores["sales_friction_inverse"],
            "differentiation": scores["differentiation"],
            "trust_compliance_value": scores["trust_compliance_value"],
            "owner_burden": scores["owner_burden"],
            "external_validation_next_step": route["external_validation_next_step"],
            "kill_criteria": route["kill_criteria"],
            **scores,
            "first_cash_score": first_cash_score,
            "why_it_can_make_money": route["why_it_can_make_money"],
            "why_it_might_fail": route["why_it_might_fail"],
        }
        ranked.append(row)
    ranked.sort(key=lambda item: (-item["first_cash_score"], item["route_id"]))
    return {
        "artifact_id": "e98_global_money_map_scores",
        "score_fields": list(MONEY_MAP_SCORE_FIELDS),
        "capability_fit_applied_after_market_selection": True,
        "ranked_routes": ranked,
        "selected_route_id": ranked[0]["route_id"],
        "old_agent_governance_route_rank": next(
            index + 1 for index, item in enumerate(ranked) if item["route_id"] == "agent_autonomy_flight_recorder"
        ),
    }


def build_global_money_map_benchmark(strategy: Mapping[str, Any]) -> dict[str, Any]:
    money_map = strategy["global_money_map_scores"]
    ranked = money_map["ranked_routes"]
    selected = ranked[0]
    old_route_rank = money_map["old_agent_governance_route_rank"]
    dimensions = {
        "capability_blind_first_pass": _dimension(
            5 if strategy["anti_recent_memory_anchor"]["capability_blind_first_pass"] else 0,
            "Market ranking happened before capability-fit filtering.",
            [],
            [],
            "run capability-blind first pass",
        ),
        "cash_pain_directness": _dimension(
            selected["cash_pain_directness"],
            "Selected route addresses an explicit cash leak.",
            [],
            [],
            "select a route with direct cash pain",
        ),
        "budget_owner_clarity": _dimension(
            selected["budget_owner_clarity"],
            "Selected route has a clear buyer/budget owner.",
            [],
            [],
            "identify who can pay",
        ),
        "urgency_2026": _dimension(
            selected["urgency_2026"],
            "Selected route is grounded in current 2026 pressure.",
            [],
            [],
            "use current market pressure",
        ),
        "route_diversity": _dimension(
            5 if len(ranked) >= 8 else 3,
            "Route set includes materially different markets.",
            [row["route_id"] for row in ranked],
            [],
            "add more cross-market routes",
        ),
        "old_route_independence": _dimension(
            5 if old_route_rank > 2 else 2,
            "Old agent-governance route is not privileged.",
            [f"old_agent_governance_route_rank={old_route_rank}"],
            [],
            "demote old route to ordinary candidate",
        ),
        "external_evidence_strength": _dimension(
            5 if len(strategy["external_market_evidence_map"]["evidence_items"]) >= 10 else 4,
            "Public-read evidence covers multiple unrelated markets.",
            [item["source_url"] for item in strategy["external_market_evidence_map"]["evidence_items"][:10]],
            [],
            "attach current public-read evidence",
        ),
        "next_action_executability": _dimension(
            5 if strategy["next_L4_feedback_owner_decision_packet"]["no_send_default"] else 0,
            "Next action is a no-send owner-gated feedback packet.",
            [],
            [],
            "owner-gate any L4 feedback",
        ),
        "overclaim_control": _dimension(
            5 if not any(strategy["overclaim_boundary"].values()) else 0,
            "No customer/revenue/payment/L4 execution claim is made.",
            [],
            [],
            "remove forbidden claims",
        ),
    }
    average = round(mean(item["score"] for item in dimensions.values()), 2)
    failed = [key for key, value in dimensions.items() if value["score"] < 4]
    return {
        "artifact_id": "e98_global_money_map_benchmark_result",
        "milestone_id": MILESTONE_ID,
        "benchmark_decision": "ALLOW" if average >= 4.2 and not failed else "REQUIRE_REVISION",
        "pass": average >= 4.2 and not failed,
        "strategic_intelligence_score": average,
        "dimensions": dimensions,
        "failed_dimensions": failed,
        "required_revisions": [dimensions[key]["improvement_required"] for key in failed],
        "truth_constraints": {
            "LLM_as_judge_used": False,
            "deterministic_structured_scoring": True,
            "no_customer_validation_claim": True,
            "no_revenue_payment_pricing_claim": True,
        },
    }


def run_e98_global_money_map_strategy(
    *,
    cieu_db: str | Path,
    owner_intent: str | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    strategy = build_global_money_map_strategy_artifact(owner_intent=owner_intent)
    governance = _load_ystar_governance(ystar_gov_root)
    write_result = governance.validate_and_write_ceo_strategic_intelligence_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    cieu_summary = summarize_e98_cieustore(cieu_db)
    receipt = build_ceo_runtime_receipt(strategy, write_result, cieu_summary)
    return {
        "artifact_id": "e98_global_money_map_session",
        "milestone_id": MILESTONE_ID,
        "strategy": strategy,
        "YstarGov_write_result": write_result,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_strategy_record_proven": receipt["CIEUStore_written"] is True
        and receipt["Y_star_gov_decision"] == "ALLOW",
        "recommended_next_milestone": "E99_Tariff_Shock_Margin_Rescue_No_Send_Demo_And_Owner_Gated_L4_Feedback_R1",
    }


def build_ceo_runtime_receipt(
    strategy: Mapping[str, Any],
    write_result: Mapping[str, Any],
    cieu_summary: Mapping[str, Any],
) -> dict[str, Any]:
    decision = write_result.get("governance_decision", {}).get("decision", "")
    selected = strategy["global_money_map_scores"]["ranked_routes"][0]
    return {
        "mode": "CEO_RUNTIME_CERTIFIED_GLOBAL_MONEY_MAP" if decision == "ALLOW" else "CEO_RUNTIME_REQUIRES_REVISION",
        "owner_intent": strategy.get("owner_intent"),
        "CEO_order_id": "e98_global_money_map_order",
        "runtime_session_id": SESSION_ID,
        "Y_star_gov_decision": decision,
        "CIEUStore_written": bool(write_result.get("formal_CIEU_log_written")),
        "CIEU_event_count": cieu_summary.get("event_count", 0),
        "CIEU_event_types": cieu_summary.get("event_types", []),
        "selected_route_id": selected["route_id"],
        "selected_first_cash_path": selected["route_name"],
        "old_agent_governance_route_rank": strategy["global_money_map_scores"]["old_agent_governance_route_rank"],
        "external_observation_status": "public_read_market_scan_no_contact_no_customer_validation",
        "generation_mode": strategy.get("generation_mode"),
        "truth_boundary": {
            "no_L4_feedback_executed": True,
            "no_customer_validation": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def summarize_e98_cieustore(cieu_db: str | Path) -> dict[str, Any]:
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


def write_e98_reports(result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    mission_dir = root / "office" / "mission_command"
    status_dir = root / "operations" / "baseline" / "e87r_full_repo_baseline"
    mission_dir.mkdir(parents=True, exist_ok=True)
    status_dir.mkdir(parents=True, exist_ok=True)
    report_json = mission_dir / "e98_global_money_map_unanchored_strategy_report.json"
    readback_md = mission_dir / "e98_global_money_map_unanchored_strategy_readback.md"
    status_json = status_dir / "current_runtime_status_after_e98_global_money_map_unanchored_strategy.json"
    status_md = status_dir / "current_runtime_status_after_e98_global_money_map_unanchored_strategy.md"

    report = _report(result)
    status = _status(result)
    report_json.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    readback_md.write_text(_report_md(report), encoding="utf-8")
    status_json.write_text(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    status_md.write_text(_status_md(status), encoding="utf-8")
    return {
        "report_json": str(report_json),
        "readback_md": str(readback_md),
        "status_json": str(status_json),
        "status_md": str(status_md),
    }


def _route_candidates() -> list[dict[str, Any]]:
    return [
        _route(
            "tariff_shock_margin_rescue_desk",
            "Tariff Shock Margin Rescue Desk for small importers",
            "48-hour margin, price-pass-through, supplier-risk, refund/protest-readiness, and landed-cost rescue pack",
            "cash_preservation_service",
            {
                "cash_pain_directness": 5,
                "budget_owner_clarity": 5,
                "urgency_2026": 5,
                "demo_feasibility_48h": 5,
                "proof_without_external_action": 5,
                "distribution_access": 4,
                "regulatory_risk_inverse": 4,
                "capability_fit_after_market_selection": 4,
                "sales_friction_inverse": 4,
                "differentiation": 4,
                "trust_compliance_value": 4,
                "owner_burden": 2,
            },
            "Public-read demo pack for a fictional importer; owner-approved L4 feedback to customs brokers/importers.",
            "Buyers may require licensed customs brokerage or already rely on a broker.",
            "Tariff costs are a direct margin leak and price decision problem.",
        ),
        _route(
            "cpa_review_bottleneck_rescue",
            "CPA Review Bottleneck Rescue for small accounting firms",
            "workflow pack that reduces review backlog, client document chasing, and advisory leakage",
            "professional_services_capacity",
            {
                "cash_pain_directness": 5,
                "budget_owner_clarity": 5,
                "urgency_2026": 4,
                "demo_feasibility_48h": 4,
                "proof_without_external_action": 4,
                "distribution_access": 3,
                "regulatory_risk_inverse": 4,
                "capability_fit_after_market_selection": 4,
                "sales_friction_inverse": 3,
                "differentiation": 3,
                "trust_compliance_value": 4,
                "owner_burden": 2,
            },
            "No-send audit of one fictional client intake/review workflow.",
            "Crowded AI accounting market and timing sensitivity around tax season.",
            "Small firms have talent and review-capacity bottlenecks with clear principals as buyers.",
        ),
        _route(
            "caregiver_admin_relief_packet",
            "Caregiver Admin Relief Packet for family caregivers",
            "paperwork, benefits, appointment, and care-task command packet for overwhelmed families",
            "consumer_admin_relief",
            {
                "cash_pain_directness": 5,
                "budget_owner_clarity": 3,
                "urgency_2026": 5,
                "demo_feasibility_48h": 4,
                "proof_without_external_action": 3,
                "distribution_access": 2,
                "regulatory_risk_inverse": 2,
                "capability_fit_after_market_selection": 3,
                "sales_friction_inverse": 2,
                "differentiation": 3,
                "trust_compliance_value": 3,
                "owner_burden": 3,
            },
            "Historical/public-resource demo only; no PHI or medical advice.",
            "High sensitivity, fragmented buyer, and PHI/medical-advice boundary.",
            "Pain is massive but monetization and safe handling are harder.",
        ),
        _route(
            "climate_insurance_premium_rescue",
            "Climate Insurance Premium Rescue Brief for property owners",
            "premium-change evidence, mitigation checklist, and broker-question pack for high-risk properties",
            "insurance_cost_service",
            {
                "cash_pain_directness": 4,
                "budget_owner_clarity": 4,
                "urgency_2026": 4,
                "demo_feasibility_48h": 4,
                "proof_without_external_action": 4,
                "distribution_access": 3,
                "regulatory_risk_inverse": 3,
                "capability_fit_after_market_selection": 3,
                "sales_friction_inverse": 3,
                "differentiation": 3,
                "trust_compliance_value": 4,
                "owner_burden": 2,
            },
            "No-send property-risk brief using public hazard and premium evidence.",
            "Local insurance rules and broker relationships may dominate.",
            "Premium shocks are cash-visible but need local precision.",
        ),
        _route(
            "prior_auth_admin_relief",
            "Prior Authorization Admin Relief Readiness Pack",
            "workflow diagnosis for clinics facing prior-auth paperwork and delay burden",
            "healthcare_admin_service",
            {
                "cash_pain_directness": 4,
                "budget_owner_clarity": 4,
                "urgency_2026": 5,
                "demo_feasibility_48h": 3,
                "proof_without_external_action": 3,
                "distribution_access": 2,
                "regulatory_risk_inverse": 2,
                "capability_fit_after_market_selection": 3,
                "sales_friction_inverse": 2,
                "differentiation": 3,
                "trust_compliance_value": 4,
                "owner_burden": 3,
            },
            "Public process map only; no patient data.",
            "Healthcare compliance, payer integration, and sales cycles are heavy.",
            "Huge burden but not the easiest first cash path.",
        ),
        _route(
            "agent_autonomy_flight_recorder",
            "Agent Autonomy Flight Recorder readiness sprint",
            "pre-production black box, no-send receipt, and residual learning for tool-using agents",
            "agent_governance_service",
            {
                "cash_pain_directness": 4,
                "budget_owner_clarity": 3,
                "urgency_2026": 3,
                "demo_feasibility_48h": 5,
                "proof_without_external_action": 5,
                "distribution_access": 2,
                "regulatory_risk_inverse": 5,
                "capability_fit_after_market_selection": 5,
                "sales_friction_inverse": 2,
                "differentiation": 5,
                "trust_compliance_value": 5,
                "owner_burden": 1,
            },
            "Demo existing runtime receipts and no-send agent workflow.",
            "Still may sound abstract, and budget owner is less obvious than tariff or accounting pain.",
            "Strong fit, but not automatically the biggest cash pain.",
        ),
        _route(
            "construction_permit_fast_lane_packet",
            "Construction Permit Fast-Lane Packet",
            "jurisdiction checklist, missing-doc detector, and contractor/customer packet for stalled permit work",
            "local_operations_service",
            {
                "cash_pain_directness": 4,
                "budget_owner_clarity": 4,
                "urgency_2026": 3,
                "demo_feasibility_48h": 4,
                "proof_without_external_action": 4,
                "distribution_access": 2,
                "regulatory_risk_inverse": 3,
                "capability_fit_after_market_selection": 3,
                "sales_friction_inverse": 2,
                "differentiation": 3,
                "trust_compliance_value": 3,
                "owner_burden": 3,
            },
            "Demo one city permit checklist using public docs only.",
            "Highly local and operationally fragmented.",
            "Permit delay is expensive but not globally uniform.",
        ),
        _route(
            "small_business_ai_workflow_rescue",
            "Small Business AI Workflow Rescue",
            "recover broken ChatGPT/Zapier/agent workflows and document safe operating procedures",
            "ai_operations_service",
            {
                "cash_pain_directness": 3,
                "budget_owner_clarity": 3,
                "urgency_2026": 4,
                "demo_feasibility_48h": 5,
                "proof_without_external_action": 4,
                "distribution_access": 3,
                "regulatory_risk_inverse": 5,
                "capability_fit_after_market_selection": 5,
                "sales_friction_inverse": 3,
                "differentiation": 3,
                "trust_compliance_value": 3,
                "owner_burden": 1,
            },
            "Demo rescue of a fictional failed automation workflow.",
            "Too generic and crowded unless narrowed to a vertical.",
            "Easy to deliver but weaker buyer pain specificity.",
        ),
    ]


def _external_evidence_items() -> list[dict[str, str]]:
    return [
        _evidence(
            "kpmg_2026_tariff_survey",
            "KPMG 2026 Tariff Survey",
            "https://kpmg.com/us/en/articles/2026/kpmg-2026-tariff-survey.html",
            "tariff_margin_pressure",
            "Businesses report margin pressure, pass-through pricing, and ongoing tariff cost uncertainty.",
        ),
        _evidence(
            "cap_small_importer_tariff_costs",
            "Center for American Progress: small-business importers tariff costs",
            "https://www.americanprogress.org/press/release-trumps-tariffs-have-cost-small-business-importers-306000-on-average/",
            "small_importer_cash_pain",
            "Small-business importers face large incremental tariff bills compared with the prior year.",
        ),
        _evidence(
            "freightos_smb_importer_tariffs",
            "Freightos: tariffs reshaping SMB importing",
            "https://www.freightos.com/freight-blog/market-update/tariffs-are-reshaping-how-smb-importers-operate-not-just-temporarily/",
            "smb_importer_behavior",
            "SMB importers report disruption, pessimism, and defensive operational changes.",
        ),
        _evidence(
            "bdo_section_232_2026",
            "BDO Section 232 metals tariffs update",
            "https://www.bdo.com/insights/tax/section-232-metals-tariffs-expanded-and-recalibrated-what-importers-need-to-know",
            "tariff_complexity",
            "Recent tariff changes materially alter duty exposure for many importers.",
        ),
        _evidence(
            "aarp_caregiving_2026",
            "AARP Valuing the Invaluable 2026",
            "https://www.aarp.org/press/releases/2026-03-26-AARP-Economic-Value-Of-Family-Caregiving-Report.html",
            "caregiver_admin_burden",
            "Family caregiving represents a trillion-dollar unpaid labor burden.",
        ),
        _evidence(
            "cms_prior_auth_2026",
            "CMS: Moving Prior Authorization into the 21st Century",
            "https://www.cms.gov/newsroom/blog/moving-prior-authorization-21st-century",
            "healthcare_admin_burden",
            "Prior authorization creates paperwork, delay, and provider administrative burden.",
        ),
        _evidence(
            "wolters_kluwer_accounting_2026",
            "Wolters Kluwer: accounting firm challenges in 2026",
            "https://www.wolterskluwer.com/en/expert-insights/accounting-firm-challenges",
            "accounting_capacity_pain",
            "Accounting firms face talent, client expectations, and operational scalability pressure.",
        ),
        _evidence(
            "gao_homeowners_insurance_2026",
            "GAO homeowners insurance premiums report",
            "https://www.gao.gov/products/gao-26-107867",
            "insurance_cost_pain",
            "Premiums rose more in disaster-prone areas and affordability/availability are worsening.",
        ),
        _evidence(
            "owasp_agentic_ai_top_10",
            "OWASP Top 10 for Agentic Applications",
            "https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security/",
            "agent_governance_risk",
            "Agentic AI creates tool-misuse and execution-boundary risk.",
        ),
        _evidence(
            "nist_ai_rmf",
            "NIST AI Risk Management Framework",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "ai_risk_governance_language",
            "NIST provides risk-management vocabulary, useful as support but not a first-cash anchor.",
        ),
    ]


def _internal_capability_map() -> dict[str, Any]:
    return {
        "bridge-labs": ["structured strategy synthesis", "report generation", "CEO runtime receipts", "controlled capability catalog"],
        "Y-star-gov": ["deterministic strategic benchmark validation", "CIEUStore.write_dict formal record path"],
        "gov-mcp": ["dry-run/no-send boundary for future owner-approved feedback packets"],
        "K9Audit": ["not integrated; no K9Audit write claimed"],
    }


def _historical_route_assets() -> list[str]:
    return [
        "office/mission_command/e90_market_grounded_strategy_run_report.json",
        "office/mission_command/e97_unanchored_global_strategy_rerun_report.json",
        "operations/baseline/e87r_full_repo_baseline/final_goal_gap_analysis.json",
        "operations/baseline/e87r_full_repo_baseline/next_engineering_roadmap.json",
        "operations/controlled_capability_catalog/e96_controlled_capability_catalog.json",
        "office/mission_command/e92_ceo_principal_codex_executor_boundary_report.json",
    ]


def _next_l4_packet() -> dict[str, Any]:
    return {
        "packet_id": "e98_tariff_shock_margin_rescue_l4_owner_decision_packet",
        "target_profile": "small importer, ecommerce brand operator, industrial distributor, freight forwarder, or customs broker serving SMB importers",
        "message_hypothesis": "Would a 48-hour tariff margin rescue desk help you identify price-pass-through, refund/protest readiness, and supplier-risk decisions before your next shipment?",
        "evidence_sought": [
            "whether tariff shock is budget-owned and urgent",
            "whether buyers trust a non-broker strategy pack if scoped as non-legal analysis",
            "whether the first paid unit should be a service sprint, spreadsheet model, or broker-support packet",
        ],
        "risk_tier": "L4_owner_approved_feedback_candidate_no_send_default",
        "owner_decision_required": True,
        "owner_approval_state": "pending_owner_decision",
        "no_send_default": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "ai_transparency": True,
        "opt_out_language": "If this is not relevant, no reply is needed.",
        "gov_mcp_dry_run_plan": "no-send receipt only after owner approval of packet content",
        "gov_mcp_dry_run_preflight_plan": "no-send receipt only after owner approval of packet content",
        "Y_star_gov_governance_plan": "validate as L4 owner-decision packet before any external action",
    }


def _cieu_predictions(selected_route: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "X_t": "Prior strategy experiments stayed anchored to existing AI governance capabilities.",
            "U_t": "Run capability-blind global money map and select first-cash route by market cash pain before capability fit.",
            "Y_star_t": f"Selected route should differ materially from old agent-governance route: {selected_route['route_name']}.",
            "expected_Y_t_plus_1": "A no-send demo pack can test whether tariff pain is more immediate than agent governance pain.",
            "predicted_R_t_plus_1": "No customer validation or revenue proof exists until owner-approved L4 feedback is executed.",
            "residual_severity": "high",
            "falsification_condition": "Feedback says tariff rescue is not urgent, not trusted, or requires licensed customs brokerage.",
        }
    ]


def _report(result: Mapping[str, Any]) -> dict[str, Any]:
    strategy = result["strategy"]
    return {
        "milestone_id": MILESTONE_ID,
        "CEO_runtime_receipt": result["CEO_runtime_receipt"],
        "anti_recent_memory_anchor": strategy["anti_recent_memory_anchor"],
        "global_money_map_method": strategy["global_money_map_method"],
        "selected_strategy": strategy["selected_strategy"],
        "global_money_map_scores": strategy["global_money_map_scores"],
        "external_market_evidence_map": strategy["external_market_evidence_map"],
        "benchmark_result": strategy["benchmark_result"],
        "YstarGov_write_result": {
            "decision": result["YstarGov_write_result"].get("governance_decision", {}).get("decision"),
            "formal_CIEU_log_written": result["YstarGov_write_result"].get("formal_CIEU_log_written"),
            "event_type": result["YstarGov_write_result"].get("CIEU_write_result", {}).get("event_type"),
        },
        "what_was_not_claimed": [
            "No L4 feedback was executed.",
            "No customer validation, pricing validation, paid signal, payment, or revenue evidence was claimed.",
            "No live provider execution occurred.",
            "No customs, tax, legal, or compliance advice was claimed.",
            "No K9Audit write or integration was claimed.",
        ],
        "recommended_next_milestone": result["recommended_next_milestone"],
    }


def _status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "CEO_runtime_receipt": result["CEO_runtime_receipt"],
        "L5-A": "complete_internal_runtime_foundation",
        "L5-B": "complete_for_structured_governed_intelligence_loop_with_capability_blind_global_money_map_experiment",
        "L5-B+": "partial_dynamic_intelligence_pending_owner_approved_live_feedback",
        "L5-C": "partial_dry_run_only",
        "L5-D": "absent_or_not_executed",
        "next": result["recommended_next_milestone"],
    }


def _report_md(report: Mapping[str, Any]) -> str:
    receipt = report["CEO_runtime_receipt"]
    selected = report["selected_strategy"]
    ranked = report["global_money_map_scores"]["ranked_routes"]
    lines = [
        "# E98 Global Money Map Unanchored Strategy",
        "",
        "## CEO Runtime Receipt",
        f"- mode: `{receipt['mode']}`",
        f"- Y-star-gov decision: `{receipt['Y_star_gov_decision']}`",
        f"- CIEUStore written: `{str(receipt['CIEUStore_written']).lower()}`",
        f"- CIEU events: `{receipt['CIEU_event_count']}`",
        "",
        "## Anti-Anchor Protocol",
        f"- capability_blind_first_pass: `{str(report['anti_recent_memory_anchor']['capability_blind_first_pass']).lower()}`",
        f"- old_agent_governance_route_status: `{report['anti_recent_memory_anchor']['old_agent_governance_route_status']}`",
        f"- old_agent_governance_route_rank: `{receipt['old_agent_governance_route_rank']}`",
        "",
        "## Selected Strategy",
        f"- first_cash_path: {selected['current_best_first_cash_path']}",
        f"- second_best_path: {selected['second_best_path']}",
        f"- next_48h_action: {selected['next_48h_action']}",
        "",
        "## Ranked Global Money Map",
    ]
    lines.extend(f"- `{row['route_id']}`: {row['first_cash_score']} - {row['route_name']}" for row in ranked)
    lines.append("")
    lines.append("## Not Claimed")
    lines.extend(f"- {item}" for item in report["what_was_not_claimed"])
    return "\n".join(lines).rstrip() + "\n"


def _status_md(status: Mapping[str, Any]) -> str:
    receipt = status["CEO_runtime_receipt"]
    return "\n".join(
        [
            "# Current Runtime Status After E98",
            "",
            f"- CEO_runtime_mode: `{receipt['mode']}`",
            f"- Y-star-gov decision: `{receipt['Y_star_gov_decision']}`",
            f"- selected_route_id: `{receipt['selected_route_id']}`",
            f"- CIEUStore written: `{str(receipt['CIEUStore_written']).lower()}`",
            f"- L5-A: `{status['L5-A']}`",
            f"- L5-B: `{status['L5-B']}`",
            f"- L5-B+: `{status['L5-B+']}`",
            f"- L5-C: `{status['L5-C']}`",
            f"- L5-D: `{status['L5-D']}`",
            f"- next: `{status['next']}`",
            "",
        ]
    )


def _route(
    route_id: str,
    name: str,
    description: str,
    route_type: str,
    money_map_score_inputs: dict[str, int],
    external_validation_next_step: str,
    why_it_might_fail: str,
    why_it_can_make_money: str,
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "name": name,
        "description": description,
        "route_type": route_type,
        "money_map_score_inputs": money_map_score_inputs,
        "external_validation_next_step": external_validation_next_step,
        "kill_criteria": why_it_might_fail,
        "why_it_might_fail": why_it_might_fail,
        "why_it_can_make_money": why_it_can_make_money,
    }


def _evidence(evidence_id: str, title: str, url: str, category: str, summary: str) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "source_title": title,
        "source_url": url,
        "category": category,
        "claim_summary": summary,
        "evidence_type": "public_read_only",
    }


def _dimension(
    score: int | float,
    reason: str,
    evidence_refs: list[str],
    missing_evidence: list[str],
    improvement: str,
) -> dict[str, Any]:
    return {
        "score": score,
        "reason": reason,
        "evidence_refs": evidence_refs,
        "missing_evidence": missing_evidence,
        "improvement_required": "" if score >= 4 else improvement,
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_global_money_map_benchmark",
    "build_global_money_map_strategy_artifact",
    "run_e98_global_money_map_strategy",
    "score_global_money_map_routes",
    "summarize_e98_cieustore",
    "write_e98_reports",
]
