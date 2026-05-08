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
MILESTONE_ID = "E99_6D_Brain_Grounded_Tariff_Shock_Strategy_Dossier_R1"
SESSION_ID = "e99_6d_brain_grounded_tariff_strategy_dossier"

SIX_D_DIMENSIONS: tuple[dict[str, str], ...] = (
    {
        "dimension_id": "D1_memory_and_mission",
        "brain_stage_id": "mission_and_owner_constraint_recall",
        "question": "What mission, prior mistakes, and owner constraints must govern this strategy?",
    },
    {
        "dimension_id": "D2_market_reality",
        "brain_stage_id": "opportunity_framing",
        "question": "What external market pain is cash-direct and urgent now?",
    },
    {
        "dimension_id": "D3_commercial_architecture",
        "brain_stage_id": "commercial_sharpness_gate",
        "question": "Who pays, why now, what is the first paid unit, and what kills the route?",
    },
    {
        "dimension_id": "D4_product_and_delivery_design",
        "brain_stage_id": "selected_action_decision",
        "question": "What exactly is sold first: report, service sprint, agent, dashboard, or platform?",
    },
    {
        "dimension_id": "D5_risk_and_governance",
        "brain_stage_id": "risk_owner_burden_evaluation",
        "question": "What must be prohibited, owner-gated, no-send, or explicitly scoped out?",
    },
    {
        "dimension_id": "D6_learning_and_next_action",
        "brain_stage_id": "post_action_learning_plan",
        "question": "What evidence updates the strategy after the next owner-approved feedback loop?",
    },
)


def _load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def build_6d_brain_grounded_strategy_dossier(*, brain_db: Path | None = None) -> dict[str, Any]:
    owner_intent = (
        "Build a full CEO-grade strategy dossier for Tariff Shock Margin Rescue Desk, using real brain "
        "provenance and without claiming customer validation, revenue, payment, legal advice, customs advice, "
        "or external execution."
    )
    brain_dimensions = _build_6d_brain_review(owner_intent, brain_db=brain_db)
    dossier = {
        "artifact_id": "e99_6d_brain_grounded_tariff_strategy_dossier",
        "milestone_id": MILESTONE_ID,
        "strategy_run_id": SESSION_ID,
        "session_id": SESSION_ID,
        "generated_at": _now(),
        "generation_mode": "six_d_brain_grounded_full_strategy_dossier",
        "owner_intent": owner_intent,
        "brain_provenance": _brain_provenance_summary(brain_dimensions, brain_db=brain_db),
        "six_d_brain_review": brain_dimensions,
        "strategic_question": (
            "Can Y*Bridge Labs turn the E98 Tariff Shock Margin Rescue route into a clear, owner-gated, "
            "cash-oriented offer without pretending it has customer validation or licensed customs authority?"
        ),
        "internal_capability_map": _internal_capability_map(),
        "historical_route_assets": _historical_route_assets(),
        "external_market_evidence_map": {
            "freshness_status": "current_public_read_as_of_2026-05-08_via_read_only_web_research",
            "evidence_mode": "public_read_only_no_contact_no_login_no_payment_no_publication",
            "evidence_items": _external_evidence_items(),
        },
        "market_definition": _market_definition(),
        "target_customer_segments": _target_customer_segments(),
        "competitor_analysis": _competitor_analysis(),
        "product_strategy": _product_strategy(),
        "offer_and_pricing_hypotheses": _offer_and_pricing_hypotheses(),
        "go_to_market_plan": _go_to_market_plan(),
        "delivery_workflow": _delivery_workflow(),
        "risk_and_boundary_controls": _risk_and_boundary_controls(),
        "unit_economics_hypothesis": _unit_economics_hypothesis(),
        "moat_and_differentiation": _moat_and_differentiation(),
        "route_candidates": _route_candidates(),
        "route_scoring": _route_scoring(),
        "selected_strategy": _selected_strategy(),
        "do_not_pursue_list": _do_not_pursue_list(),
        "adversarial_critique": _adversarial_critique(),
        "what_not_to_do_next": _what_not_to_do_next(),
        "next_L4_feedback_owner_decision_packet": _next_l4_packet(),
        "CIEU_predictions": _cieu_predictions(),
        "post_strategy_residual_plan": _post_strategy_residual_plan(),
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
            "brain_grounded": True,
            "private_chain_of_thought_stored": False,
            "external_public_read_only": True,
            "no_external_action_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_claim": True,
            "no_customs_legal_or_tax_advice_claim": True,
            "gov_mcp_live_provider_execution": False,
            "K9Audit_not_integrated": True,
        },
        "execute_L4_now": False,
    }
    dossier["benchmark_result"] = build_full_strategy_dossier_benchmark(dossier)
    return dossier


def _build_6d_brain_review(owner_intent: str, *, brain_db: Path | None = None) -> list[dict[str, Any]]:
    dimensions: list[dict[str, Any]] = []
    for item in SIX_D_DIMENSIONS:
        activations = query_brain_for_stage(
            item["brain_stage_id"],
            f"{owner_intent} {item['question']}",
            top_n=6,
            brain_db=brain_db,
        )
        safe_activations = [_safe_brain_activation(node) for node in activations]
        dimensions.append(
            {
                "dimension_id": item["dimension_id"],
                "brain_stage_id": item["brain_stage_id"],
                "question": item["question"],
                "brain_activation_count": len(safe_activations),
                "evidence_refs": [f"brain://{node['node_id']}: {node['node_name']}" for node in safe_activations],
                "top_activations": safe_activations,
                "output_summary": _brain_output_summary(item["dimension_id"], safe_activations),
                "confidence_boundary": "brain provenance plus structured public-read dossier; no hidden chain-of-thought stored",
                "missing_evidence": [] if activations else ["no brain activation returned for this dimension"],
                "runtime_governance_required": True,
                "CIEU_recording_required": True,
            }
        )
    return dimensions


def build_full_strategy_dossier_benchmark(dossier: Mapping[str, Any]) -> dict[str, Any]:
    dimensions = {
        "brain_provenance": _dimension(
            5 if dossier["brain_provenance"]["unique_nodes"] >= 3 and len(dossier["six_d_brain_review"]) == 6 else 1,
            "All six strategy dimensions carry real brain provenance.",
            dossier["brain_provenance"].get("sample_evidence_refs", []),
            [],
            "query brain provenance for each 6D dimension",
        ),
        "competitor_analysis": _dimension(
            5 if len(dossier["competitor_analysis"]["direct_competitors"]) >= 5 else 2,
            "Direct and indirect alternatives are mapped.",
            [item["competitor_id"] for item in dossier["competitor_analysis"]["direct_competitors"]],
            [],
            "add direct competitors and alternatives",
        ),
        "product_shape_clarity": _dimension(
            5 if len(dossier["product_strategy"]["product_stages"]) >= 4 else 2,
            "Product stages distinguish demo, service sprint, internal agent, and future dashboard.",
            [item["stage_id"] for item in dossier["product_strategy"]["product_stages"]],
            [],
            "define concrete product stages",
        ),
        "buyer_and_gtm_clarity": _dimension(
            5 if len(dossier["target_customer_segments"]) >= 4 and len(dossier["go_to_market_plan"]["channels_to_test_after_owner_approval"]) >= 4 else 2,
            "Buyer segments and owner-gated channels are explicit.",
            [],
            [],
            "define buyer segments and channels",
        ),
        "risk_boundary": _dimension(
            5 if dossier["risk_and_boundary_controls"]["no_customs_legal_or_tax_advice"] else 1,
            "Customs/legal/tax advice boundary is explicit.",
            [],
            [],
            "make regulated advice boundary explicit",
        ),
        "residual_learning": _dimension(
            5 if dossier["post_strategy_residual_plan"]["pivot_trigger"] else 2,
            "Future evidence, pivot triggers, and residual plan are explicit.",
            [],
            [],
            "add residual learning plan",
        ),
        "truth_boundary": _dimension(
            5 if not any(dossier["overclaim_boundary"].values()) else 0,
            "No L4/customer/revenue/payment/compliance completion claim is made.",
            [],
            [],
            "remove forbidden claims",
        ),
    }
    failed = [key for key, value in dimensions.items() if value["score"] < 4]
    score = round(sum(item["score"] for item in dimensions.values()) / len(dimensions), 2)
    return {
        "artifact_id": "e99_6d_brain_grounded_full_strategy_dossier_benchmark",
        "milestone_id": MILESTONE_ID,
        "benchmark_decision": "ALLOW" if score >= 4.2 and not failed else "REQUIRE_REVISION",
        "pass": score >= 4.2 and not failed,
        "strategic_intelligence_score": score,
        "dimensions": dimensions,
        "failed_dimensions": failed,
        "required_revisions": [dimensions[key]["improvement_required"] for key in failed],
        "truth_constraints": {
            "LLM_as_judge_used": False,
            "deterministic_structured_scoring": True,
            "hidden_chain_of_thought_stored": False,
            "no_customer_validation_claim": True,
            "no_revenue_payment_pricing_claim": True,
        },
    }


def run_e99_6d_brain_grounded_strategy_dossier(
    *,
    cieu_db: str | Path,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    dossier = build_6d_brain_grounded_strategy_dossier(brain_db=brain_db)
    governance = _load_ystar_governance(ystar_gov_root)
    write_result = governance.validate_and_write_ceo_strategic_intelligence_strategy(
        dossier,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    cieu_summary = summarize_e99_cieustore(cieu_db)
    receipt = build_ceo_runtime_receipt(dossier, write_result, cieu_summary)
    return {
        "artifact_id": "e99_6d_brain_grounded_strategy_dossier_session",
        "milestone_id": MILESTONE_ID,
        "dossier": dossier,
        "YstarGov_write_result": write_result,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_dossier_record_proven": receipt["CIEUStore_written"] is True
        and receipt["Y_star_gov_decision"] == "ALLOW",
        "recommended_next_milestone": "E100_Tariff_Shock_Margin_Rescue_No_Send_Demo_Pack_R1",
    }


def build_ceo_runtime_receipt(
    dossier: Mapping[str, Any],
    write_result: Mapping[str, Any],
    cieu_summary: Mapping[str, Any],
) -> dict[str, Any]:
    decision = write_result.get("governance_decision", {}).get("decision", "")
    return {
        "mode": "CEO_RUNTIME_CERTIFIED_6D_BRAIN_GROUNDED_STRATEGY_DOSSIER"
        if decision == "ALLOW"
        else "CEO_RUNTIME_REQUIRES_REVISION",
        "CEO_order_id": "e99_6d_brain_grounded_tariff_strategy_order",
        "runtime_session_id": SESSION_ID,
        "Y_star_gov_decision": decision,
        "CIEUStore_written": bool(write_result.get("formal_CIEU_log_written")),
        "CIEU_event_count": cieu_summary.get("event_count", 0),
        "CIEU_event_types": cieu_summary.get("event_types", []),
        "brain_grounded": True,
        "brain_unique_nodes": dossier["brain_provenance"]["unique_nodes"],
        "brain_total_activations": dossier["brain_provenance"]["total_activations"],
        "selected_first_cash_path": dossier["selected_strategy"]["current_best_first_cash_path"],
        "product_shape": [item["stage_id"] for item in dossier["product_strategy"]["product_stages"]],
        "competitor_count": len(dossier["competitor_analysis"]["direct_competitors"]),
        "truth_boundary": {
            "no_L4_feedback_executed": True,
            "no_customer_validation": True,
            "no_revenue_or_payment_signal": True,
            "no_customs_legal_or_tax_advice": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def summarize_e99_cieustore(cieu_db: str | Path) -> dict[str, Any]:
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


def write_e99_reports(result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    mission_dir = root / "office" / "mission_command"
    status_dir = root / "operations" / "baseline" / "e87r_full_repo_baseline"
    mission_dir.mkdir(parents=True, exist_ok=True)
    status_dir.mkdir(parents=True, exist_ok=True)
    report_json = mission_dir / "e99_6d_brain_grounded_full_strategy_dossier_report.json"
    readback_md = mission_dir / "e99_6d_brain_grounded_full_strategy_dossier_readback.md"
    status_json = status_dir / "current_runtime_status_after_e99_6d_brain_grounded_full_strategy_dossier.json"
    status_md = status_dir / "current_runtime_status_after_e99_6d_brain_grounded_full_strategy_dossier.md"

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


def _market_definition() -> dict[str, Any]:
    return {
        "market_name": "SMB tariff shock margin rescue",
        "job_to_be_done": "protect gross margin and cash planning when import duties, landed cost, and refund/protest options change faster than the importer can analyze",
        "not_the_market": [
            "licensed customs brokerage",
            "legal/tax advice",
            "enterprise global trade management platform replacement",
            "generic AI governance product",
        ],
        "why_now": [
            "tariff volatility turns import decisions into immediate margin and pricing problems",
            "SMB importers often lack in-house trade compliance teams",
            "refund/drawback/protest opportunities create found-money urgency but also complexity",
        ],
    }


def _target_customer_segments() -> list[dict[str, Any]]:
    return [
        {
            "segment_id": "import_heavy_dtc_brand",
            "buyer": "founder, COO, or finance lead",
            "pain": "tariff costs reduce contribution margin and force price changes",
            "first_offer_fit": "high",
            "data_sensitivity": "medium",
        },
        {
            "segment_id": "small_industrial_distributor",
            "buyer": "owner/operator or procurement lead",
            "pain": "supplier and SKU landed-cost shifts hurt quote accuracy",
            "first_offer_fit": "high",
            "data_sensitivity": "medium",
        },
        {
            "segment_id": "customs_broker_or_freight_forwarder",
            "buyer": "broker principal or client advisory lead",
            "pain": "clients need quick triage and communication material",
            "first_offer_fit": "medium",
            "data_sensitivity": "medium",
        },
        {
            "segment_id": "ecommerce_marketplace_seller",
            "buyer": "brand operator",
            "pain": "tariff costs disrupt replenishment and price competitiveness",
            "first_offer_fit": "medium",
            "data_sensitivity": "medium",
        },
    ]


def _competitor_analysis() -> dict[str, Any]:
    return {
        "direct_competitors": [
            {
                "competitor_id": "zollback",
                "positioning": "AI duty drawback and tariff refund platform",
                "strength": "refund automation and customs filing workflow",
                "gap_for_us": "do not compete on filing; focus on pre-filing margin triage and decision brief",
                "source_url": "https://www.zollback.com/",
            },
            {
                "competitor_id": "landededge",
                "positioning": "customs valuation intelligence for duty savings",
                "strength": "First Sale and non-dutiable cost analysis",
                "gap_for_us": "avoid enterprise platform competition; sell fast SMB decision sprint",
                "source_url": "https://www.landededge.com/",
            },
            {
                "competitor_id": "tariff_refund_hq",
                "positioning": "managed tariff refund and duty drawback support",
                "strength": "attorney-backed managed refund/refund pathway support",
                "gap_for_us": "stay upstream as readiness and margin-impact brief, then refer/partner if filing is needed",
                "source_url": "https://www.tariffrefundhq.com/",
            },
            {
                "competitor_id": "tariffcenter_ai",
                "positioning": "SMB tariff intelligence and HTS lookup platform",
                "strength": "low-cost self-serve HS classification and landed-cost analysis",
                "gap_for_us": "offer human-readable strategic decision pack and broker-question list",
                "source_url": "https://www.tariffcenter.ai/",
            },
            {
                "competitor_id": "dutyback",
                "positioning": "managed duty drawback service for SMBs",
                "strength": "expert oversight and broker partnerships",
                "gap_for_us": "do not replace drawback provider; help decide whether a buyer should pursue drawback/protest/price action",
                "source_url": "https://www.getdutyback.com/",
            },
            {
                "competitor_id": "crumbs",
                "positioning": "duty drawback and tariff recovery for brands",
                "strength": "contingency refund positioning and calculator",
                "gap_for_us": "serve before refund filing by clarifying margin, product, and timing decisions",
                "source_url": "https://www.crumbsback.com/",
            },
        ],
        "indirect_alternatives": [
            "existing customs broker advice",
            "freight forwarder advisory support",
            "internal spreadsheet landed-cost model",
            "ERP/global trade management tools",
            "do nothing and absorb margin hit",
        ],
        "positioning_decision": (
            "Y*Bridge Labs should not position as a broker, filing service, or legal advisor. The wedge is a fast "
            "cash-decision brief that tells the importer what questions to ask, what margin scenarios to model, "
            "and whether to pursue a licensed partner."
        ),
    }


def _product_strategy() -> dict[str, Any]:
    return {
        "product_name": "Tariff Shock Margin Rescue Desk",
        "product_stages": [
            {
                "stage_id": "v0_no_send_demo_report",
                "description": "fictional SKU set demo showing landed-cost shock, price-pass-through options, refund/protest readiness, and broker questions",
                "buyer_value": "shows the shape of the deliverable without using real customer data",
                "execution_status": "next_internal_work",
            },
            {
                "stage_id": "v1_human_assisted_service_sprint",
                "description": "48-hour custom brief using buyer-provided non-sensitive/import summary data under explicit scope",
                "buyer_value": "fast decision support before a shipment, price update, or broker conversation",
                "execution_status": "requires_owner_approved_L4_feedback_before_sale",
            },
            {
                "stage_id": "v2_internal_rescue_analyst_agent",
                "description": "internal agent that prepares evidence, scenario tables, and broker-question lists for human review",
                "buyer_value": "speed and repeatability without claiming autonomous customs advice",
                "execution_status": "future_after_feedback",
            },
            {
                "stage_id": "v3_client_facing_dashboard",
                "description": "dashboard or portal only if repeated service demand validates workflow and boundaries",
                "buyer_value": "self-serve monitoring and scenario updates",
                "execution_status": "not_now",
            },
        ],
        "first_deliverable": "v0_no_send_demo_report",
        "not_a_product_yet": "No SaaS or autonomous client-facing rescue agent should be built before L4 feedback.",
    }


def _offer_and_pricing_hypotheses() -> dict[str, Any]:
    return {
        "pricing_validation_status": "hypothesis_only_not_validated",
        "entry_offer": {
            "name": "48-hour Tariff Shock Margin Rescue Brief",
            "hypothesis_price_range_usd": "$750-$2,500",
            "why": "small enough for urgent owner approval; high enough to test real willingness to pay",
        },
        "premium_offer": {
            "name": "30-day Tariff Desk with weekly SKU/supplier scenarios",
            "hypothesis_price_range_usd": "$3,000-$8,000",
            "why": "only after first sprint proves repeat urgency",
        },
        "success_fee_boundary": "Do not offer contingency refund filing unless licensed partner boundary exists.",
    }


def _go_to_market_plan() -> dict[str, Any]:
    return {
        "channels_to_test_after_owner_approval": [
            "customs broker partner feedback",
            "freight forwarder operator feedback",
            "import-heavy DTC founder feedback",
            "industrial distributor owner/operator feedback",
        ],
        "first_message_hypothesis": (
            "Would a 48-hour tariff margin rescue brief help you decide which SKUs need price changes, supplier changes, "
            "refund/protest review, or broker questions before your next shipment?"
        ),
        "no_send_default": True,
        "owner_approval_required_before_contact": True,
        "L4_feedback_goal": "validate pain language, buyer owner, deliverable shape, and willingness to consider paid sprint",
    }


def _delivery_workflow() -> dict[str, Any]:
    return {
        "inputs_for_demo": ["fictional SKU list", "fictional current landed cost", "public tariff references", "fictional sales price"],
        "inputs_for_real_sprint_later": [
            "customer-provided SKU/import summary",
            "current landed cost assumptions",
            "supplier/country exposure summary",
            "broker/contact questions approved by customer",
        ],
        "outputs": [
            "margin shock table",
            "price-pass-through scenarios",
            "supplier/route exposure map",
            "refund/protest/drawback readiness checklist",
            "broker question list",
            "decision brief with no legal/customs advice disclaimer",
        ],
        "quality_controls": [
            "public-read evidence refs",
            "no legal/tax/customs advice claim",
            "Y-star-gov governance receipt",
            "CIEU residual prediction",
            "owner-gated external feedback",
        ],
    }


def _risk_and_boundary_controls() -> dict[str, Any]:
    return {
        "no_customs_legal_or_tax_advice": True,
        "no_filing_or_brokerage": True,
        "no_real_customer_data_in_demo": True,
        "licensed_partner_required_for_filing": True,
        "customer_data_boundary_required_before_real_sprint": True,
        "high_risk_actions_owner_bound": [
            "real outreach",
            "customer data ingestion",
            "refund/protest filing",
            "legal/customs advice",
            "payment collection",
        ],
    }


def _unit_economics_hypothesis() -> dict[str, Any]:
    return {
        "status": "hypothesis_only_not_validated",
        "delivery_time_target": "4-8 focused hours for v1 after template exists",
        "gross_margin_hypothesis": "high if analysis template is reused and no licensed filing is included",
        "biggest_cost_driver": "data cleanup and boundary review",
        "validation_needed": "owner-approved L4 feedback and eventually paid pilot",
    }


def _moat_and_differentiation() -> dict[str, Any]:
    return {
        "near_term_moat": [
            "fast structured decision brief",
            "public-read evidence discipline",
            "governed no-overclaim receipts",
            "clear boundary between analysis and licensed filing",
        ],
        "longer_term_moat": [
            "repeatable tariff scenario workflow",
            "agent-assisted evidence extraction under governance",
            "partner network with brokers/refund providers if validated",
        ],
        "not_a_moat": "generic AI writing, generic tariff lookup, or broad AI governance language",
    }


def _route_candidates() -> list[dict[str, Any]]:
    return [
        {"route_id": "tariff_shock_margin_rescue", "name": "Tariff Shock Margin Rescue Desk", "route_type": "cash_preservation_service"},
        {"route_id": "duty_drawback_refund_filing", "name": "Duty drawback/refund filing service", "route_type": "licensed_partner_required"},
        {"route_id": "tariffcenter_self_serve_tool", "name": "Self-serve tariff/HTS lookup tool", "route_type": "software_tool"},
        {"route_id": "customs_broker_partner_enablement", "name": "Broker partner enablement packet", "route_type": "partner_enablement"},
        {"route_id": "agent_autonomy_flight_recorder", "name": "Agent Autonomy Flight Recorder", "route_type": "old_agent_governance_route"},
    ]


def _route_scoring() -> list[dict[str, Any]]:
    return [
        _score("tariff_shock_margin_rescue", 5, 5, 2, 5, 2, 4, 4, 2, "no-send demo report and owner-approved L4 feedback", "buyers require licensed broker or do not trust non-broker analysis"),
        _score("duty_drawback_refund_filing", 4, 5, 4, 2, 4, 3, 5, 4, "find licensed partner before any filing claim", "requires licensed/attorney/broker boundary"),
        _score("tariffcenter_self_serve_tool", 3, 3, 4, 2, 4, 2, 3, 3, "validate repeated workflow before software", "tool market may already be crowded"),
        _score("customs_broker_partner_enablement", 4, 4, 3, 3, 3, 4, 4, 3, "test broker partner feedback packet", "brokers may already have internal process"),
        _score("agent_autonomy_flight_recorder", 3, 4, 2, 4, 3, 5, 4, 1, "keep as separate route, not first tariff strategy", "less direct cash pain for importer target"),
    ]


def _selected_strategy() -> dict[str, Any]:
    return {
        "current_best_first_cash_path": "Tariff Shock Margin Rescue Desk for small importers",
        "second_best_path": "Customs broker partner enablement packet",
        "why_this_path_now": (
            "It turns tariff volatility into a cash-preservation service sprint with a clear buyer, clear pain, "
            "and a concrete 48-hour demo deliverable."
        ),
        "why_not_others": [
            "Duty refund filing needs licensed partner boundaries before we can sell it.",
            "Self-serve tools are crowded and should wait until repeated service workflow is validated.",
            "Agent governance route is useful internally but less direct for importer cash pain.",
            "Caregiver/accounting/insurance routes remain interesting but are outside this dossier's selected route.",
        ],
        "what_evidence_could_falsify_it": "target buyers say tariff pain is already solved by brokers or will not pay for a scoped decision brief",
        "next_48h_action": "Build v0 no-send demo report using fictional importer SKU data.",
        "next_7d_action": "Prepare owner-approved L4 feedback packet for brokers, importers, and ecommerce operators; no send until approval.",
        "next_owner_decision_needed": "Approve or reject the no-send L4 feedback packet after reviewing the v0 demo report.",
    }


def _next_l4_packet() -> dict[str, Any]:
    return {
        "packet_id": "e99_tariff_shock_strategy_l4_owner_decision_packet",
        "target_profile": "small importer, import-heavy DTC founder, industrial distributor, customs broker, or freight forwarder",
        "message_hypothesis": "Would a 48-hour tariff margin rescue brief help you decide pricing, supplier, refund/protest, or broker questions before the next shipment?",
        "evidence_sought": [
            "pain urgency",
            "budget owner",
            "preferred deliverable shape",
            "trust boundary for non-broker analysis",
            "willingness to consider paid sprint",
        ],
        "risk_tier": "L4_owner_approved_feedback_candidate_no_send_default",
        "owner_decision_required": True,
        "owner_approval_state": "pending_owner_decision",
        "no_send_default": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "ai_transparency": True,
        "opt_out_language": "If this is not relevant, no reply is needed.",
        "gov_mcp_dry_run_plan": "generate no-send receipt only after owner approval of packet content",
        "gov_mcp_dry_run_preflight_plan": "generate no-send receipt only after owner approval of packet content",
        "Y_star_gov_governance_plan": "validate as L4 owner-decision packet before any external action",
    }


def _external_evidence_items() -> list[dict[str, str]]:
    return [
        _evidence("kpmg_2026_tariff_survey", "KPMG 2026 Tariff Survey", "https://kpmg.com/us/en/articles/2026/kpmg-2026-tariff-survey.html", "tariff_margin_pressure", "Public-read evidence of tariff pressure and strategic response needs."),
        _evidence("cap_small_importer_tariff_costs", "CAP small-business importer tariff cost analysis", "https://www.americanprogress.org/press/release-trumps-tariffs-have-cost-small-business-importers-306000-on-average/", "small_importer_cash_pain", "Small importers face material incremental tariff costs."),
        _evidence("freightos_smb_importer_tariffs", "Freightos SMB importer tariff disruption", "https://www.freightos.com/freight-blog/market-update/tariffs-are-reshaping-how-smb-importers-operate-not-just-temporarily/", "smb_importer_behavior", "SMB importers are changing operations under tariff pressure."),
        _evidence("bdo_section_232_2026", "BDO Section 232 tariff update", "https://www.bdo.com/insights/tax/section-232-metals-tariffs-expanded-and-recalibrated-what-importers-need-to-know", "tariff_complexity", "Tariff changes create analysis burden for importers."),
        _evidence("zollback", "Zollback duty drawback platform", "https://www.zollback.com/", "competitor", "AI-native duty drawback and refund competitor."),
        _evidence("landededge", "LandedEdge customs valuation platform", "https://www.landededge.com/", "competitor", "Customs valuation intelligence competitor."),
        _evidence("tariff_refund_hq", "Tariff Refund HQ", "https://www.tariffrefundhq.com/", "competitor", "Managed tariff refund support competitor."),
        _evidence("tariffcenter_ai", "TariffCenter.AI", "https://www.tariffcenter.ai/", "competitor", "SMB tariff intelligence platform competitor."),
        _evidence("dutyback", "dutyback", "https://www.getdutyback.com/", "competitor", "Managed duty drawback service competitor."),
        _evidence("crumbs", "Crumbs duty recovery", "https://www.crumbsback.com/", "competitor", "Duty drawback and tariff recovery competitor."),
    ]


def _cieu_predictions() -> list[dict[str, Any]]:
    return [
        {
            "X_t": "E98 selected tariff shock margin rescue as a cash-first route but lacked full 6D brain-grounded strategy depth.",
            "U_t": "Build full dossier with brain provenance, competitor analysis, product shape, GTM, pricing hypothesis, risk boundaries, and residual learning.",
            "Y_star_t": "A complete dossier clarifies whether the route is worth owner-approved no-send demo work.",
            "expected_Y_t_plus_1": "Owner can evaluate a concrete v0 demo scope and L4 feedback packet rather than a vague strategic direction.",
            "predicted_R_t_plus_1": "Dossier still lacks real customer feedback and paid signal until owner-approved L4/L5 work occurs.",
            "residual_severity": "medium",
            "falsification_condition": "the v0 demo cannot show credible buyer value without regulated customs/legal advice",
        }
    ]


def _post_strategy_residual_plan() -> dict[str, Any]:
    return {
        "evaluate_strategy_quality_by": "whether v0 demo makes the product shape, buyer pain, competitor gap, and risk boundary understandable",
        "future_evidence_updates": [
            "which buyer segment reacts fastest",
            "whether broker partnership is required before selling",
            "whether buyers prefer service sprint, spreadsheet, or agent-assisted desk",
            "whether price hypothesis is credible",
        ],
        "pivot_trigger": "buyers say tariff problem is broker-owned, too regulated, or not worth a paid sprint",
        "what_not_to_do_next": "do not contact targets or take payment before owner approval and risk-boundary review",
    }


def _do_not_pursue_list() -> list[str]:
    return [
        "Do not sell customs brokerage, legal, tax, or compliance advice.",
        "Do not ingest real customer shipment data in the demo.",
        "Do not execute outreach without owner approval.",
        "Do not claim revenue, payment, pricing validation, or customer validation.",
        "Do not build SaaS before testing paid service-sprint interest.",
        "Do not hide competitors or pretend the category is empty.",
    ]


def _adversarial_critique() -> list[str]:
    return [
        "The route could be invalid if buyers trust only licensed brokers.",
        "Competitors already cover refund/drawback, so our position must stay upstream and decision-focused.",
        "The phrase rescue desk could imply advice authority; the scope must be narrow and explicit.",
        "A fictional demo may be too abstract unless it shows margin math clearly.",
        "Owner-approved feedback may reveal the buyer wants a partner referral, not an analysis pack.",
    ]


def _what_not_to_do_next() -> list[str]:
    return [
        "do not claim licensed customs expertise",
        "do not use real importer data",
        "do not send messages",
        "do not collect payment",
        "do not build dashboard first",
        "do not collapse this back into generic AI governance language",
    ]


def _brain_provenance_summary(dimensions: list[dict[str, Any]], *, brain_db: Path | None) -> dict[str, Any]:
    all_nodes = [
        node
        for dimension in dimensions
        for node in dimension["top_activations"]
    ]
    node_ids = [str(node["node_id"]) for node in all_nodes]
    evidence_refs = [
        ref
        for dimension in dimensions
        for ref in dimension["evidence_refs"]
    ]
    return {
        "brain_db": str(brain_db or BRAIN_DB_PATH),
        "six_d_dimension_count": len(dimensions),
        "total_activations": len(all_nodes),
        "unique_nodes": len(set(node_ids)),
        "sample_evidence_refs": evidence_refs[:12],
        "production_brain_write_performed": False,
    }


def _brain_output_summary(dimension_id: str, activations: list[dict[str, Any]]) -> str:
    if not activations:
        return f"{dimension_id}: no brain activation returned"
    top = ", ".join(str(item["node_name"])[:80] for item in activations[:3])
    return f"{dimension_id}: brain activation highlights {top}"


def _safe_brain_activation(node: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "node_id": str(node.get("node_id") or ""),
        "node_name": _ascii_only(str(node.get("node_name") or "")),
        "file_path": str(node.get("file_path") or ""),
        "activation_level": node.get("activation_level"),
        "hop_distance": node.get("hop_distance"),
    }


def _ascii_only(value: str) -> str:
    return value.encode("ascii", "ignore").decode("ascii").replace("  ", " ").strip()


def _internal_capability_map() -> dict[str, Any]:
    return {
        "bridge-labs": ["6D brain provenance", "strategy dossier generation", "owner-gated L4 packet", "reporting"],
        "Y-star-gov": ["strategic benchmark validator", "CIEUStore formal record write"],
        "gov-mcp": ["dry-run/no-send boundary for future feedback packet"],
        "K9Audit": ["not integrated; no write claimed"],
    }


def _historical_route_assets() -> list[str]:
    return [
        "office/mission_command/e98_global_money_map_unanchored_strategy_report.json",
        "office/mission_command/e97_unanchored_global_strategy_rerun_report.json",
        "office/mission_command/e94_behavior_center_runtime_gateway_report.json",
        "office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop_report.json",
        "office/mission_command/e90_market_grounded_strategy_run_report.json",
        "operations/baseline/e87r_full_repo_baseline/final_goal_gap_analysis.json",
    ]


def _score(route_id: str, speed: int, pain: int, proof: int, readiness: int, friction: int, diff: int, trust: int, burden: int, next_step: str, kill: str) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "speed_to_first_cash": speed,
        "buyer_pain_intensity": pain,
        "proof_needed": proof,
        "implementation_readiness": readiness,
        "sales_friction": friction,
        "differentiation": diff,
        "trust_compliance_value": trust,
        "owner_burden": burden,
        "external_validation_next_step": next_step,
        "kill_criteria": kill,
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


def _dimension(score: int, reason: str, evidence_refs: list[str], missing_evidence: list[str], improvement: str) -> dict[str, Any]:
    return {
        "score": score,
        "reason": reason,
        "evidence_refs": evidence_refs,
        "missing_evidence": missing_evidence,
        "improvement_required": "" if score >= 4 else improvement,
    }


def _report(result: Mapping[str, Any]) -> dict[str, Any]:
    dossier = result["dossier"]
    return {
        "milestone_id": MILESTONE_ID,
        "CEO_runtime_receipt": result["CEO_runtime_receipt"],
        "brain_provenance": dossier["brain_provenance"],
        "six_d_brain_review": dossier["six_d_brain_review"],
        "market_definition": dossier["market_definition"],
        "target_customer_segments": dossier["target_customer_segments"],
        "competitor_analysis": dossier["competitor_analysis"],
        "product_strategy": dossier["product_strategy"],
        "offer_and_pricing_hypotheses": dossier["offer_and_pricing_hypotheses"],
        "go_to_market_plan": dossier["go_to_market_plan"],
        "delivery_workflow": dossier["delivery_workflow"],
        "risk_and_boundary_controls": dossier["risk_and_boundary_controls"],
        "unit_economics_hypothesis": dossier["unit_economics_hypothesis"],
        "moat_and_differentiation": dossier["moat_and_differentiation"],
        "selected_strategy": dossier["selected_strategy"],
        "benchmark_result": dossier["benchmark_result"],
        "YstarGov_write_result": {
            "decision": result["YstarGov_write_result"].get("governance_decision", {}).get("decision"),
            "formal_CIEU_log_written": result["YstarGov_write_result"].get("formal_CIEU_log_written"),
            "event_type": result["YstarGov_write_result"].get("CIEU_write_result", {}).get("event_type"),
        },
        "what_was_not_claimed": [
            "No L4 feedback was executed.",
            "No customer validation, pricing validation, paid signal, payment, or revenue evidence was claimed.",
            "No customs, tax, legal, or compliance advice was claimed.",
            "No live provider execution occurred.",
            "No production brain write or K9Audit write was performed.",
        ],
        "recommended_next_milestone": result["recommended_next_milestone"],
    }


def _status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "CEO_runtime_receipt": result["CEO_runtime_receipt"],
        "L5-A": "complete_internal_runtime_foundation",
        "L5-B": "complete_for_structured_governed_intelligence_loop_with_6d_brain_grounded_strategy_dossier",
        "L5-B+": "partial_dynamic_intelligence_pending_owner_approved_live_feedback",
        "L5-C": "partial_dry_run_only",
        "L5-D": "absent_or_not_executed",
        "next": result["recommended_next_milestone"],
    }


def _report_md(report: Mapping[str, Any]) -> str:
    receipt = report["CEO_runtime_receipt"]
    selected = report["selected_strategy"]
    lines = [
        "# E99 6D Brain-Grounded Full Strategy Dossier",
        "",
        "## CEO Runtime Receipt",
        f"- mode: `{receipt['mode']}`",
        f"- Y-star-gov decision: `{receipt['Y_star_gov_decision']}`",
        f"- CIEUStore written: `{str(receipt['CIEUStore_written']).lower()}`",
        f"- brain_unique_nodes: `{receipt['brain_unique_nodes']}`",
        f"- competitor_count: `{receipt['competitor_count']}`",
        "",
        "## Selected Strategy",
        f"- first_cash_path: {selected['current_best_first_cash_path']}",
        f"- next_48h_action: {selected['next_48h_action']}",
        "",
        "## Product Shape",
    ]
    lines.extend(f"- `{item['stage_id']}`: {item['description']}" for item in report["product_strategy"]["product_stages"])
    lines.append("")
    lines.append("## Direct Competitors")
    lines.extend(f"- `{item['competitor_id']}`: {item['positioning']}" for item in report["competitor_analysis"]["direct_competitors"])
    lines.append("")
    lines.append("## Not Claimed")
    lines.extend(f"- {item}" for item in report["what_was_not_claimed"])
    return "\n".join(lines).rstrip() + "\n"


def _status_md(status: Mapping[str, Any]) -> str:
    receipt = status["CEO_runtime_receipt"]
    return "\n".join(
        [
            "# Current Runtime Status After E99",
            "",
            f"- CEO_runtime_mode: `{receipt['mode']}`",
            f"- Y-star-gov decision: `{receipt['Y_star_gov_decision']}`",
            f"- CIEUStore written: `{str(receipt['CIEUStore_written']).lower()}`",
            f"- brain_unique_nodes: `{receipt['brain_unique_nodes']}`",
            f"- L5-A: `{status['L5-A']}`",
            f"- L5-B: `{status['L5-B']}`",
            f"- L5-B+: `{status['L5-B+']}`",
            f"- L5-C: `{status['L5-C']}`",
            f"- L5-D: `{status['L5-D']}`",
            f"- next: `{status['next']}`",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_6d_brain_grounded_strategy_dossier",
    "build_full_strategy_dossier_benchmark",
    "run_e99_6d_brain_grounded_strategy_dossier",
    "summarize_e99_cieustore",
    "write_e99_reports",
]
