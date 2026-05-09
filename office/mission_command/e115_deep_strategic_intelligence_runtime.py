from __future__ import annotations

import argparse
import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from office.mission_command.e114_live_web_capability_utilized_strategy_run import (
    run_e114_live_web_capability_utilized_strategy_run,
)


MILESTONE_ID = "E115_Aiden_Deep_Strategic_Intelligence_Runtime_R1"
SESSION_ID = "e115_aiden_deep_strategic_intelligence_runtime"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def run_e115_deep_strategic_intelligence_runtime(
    *,
    cieu_db: str | Path,
    owner_intent: str = "Aiden: build a deep, high-intelligence global first-cash strategy for Y*Bridge Labs.",
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    use_host_live_network: bool = False,
    seal_session: bool = True,
) -> dict[str, Any]:
    e114 = run_e114_live_web_capability_utilized_strategy_run(
        cieu_db=cieu_db,
        owner_intent=owner_intent,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        use_host_live_network=use_host_live_network,
        seal_session=False,
    )
    dossier = build_e115_deep_strategy_dossier(e114, owner_intent=owner_intent)
    gov = _load_ystar_module("ystar.governance.ceo_deep_strategic_intelligence_contract", ystar_gov_root)
    write = gov.validate_and_write_ceo_deep_strategic_intelligence_dossier(
        dossier,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = summarize_e115_cieustore(cieu_db)
    return {
        "artifact_id": "e115_deep_strategic_intelligence_runtime_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "source_e114_result": e114,
        "deep_strategy_dossier": dossier,
        "YstarGov_deep_strategy_write_result": write,
        "CIEUStore_summary": summary,
        "deep_strategy_runtime_proven": write["governance_decision"]["decision"] == "ALLOW" and summary["event_count"] >= 1,
        "truth_constraints": {
            "no_external_action_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_capability_utilization_law",
            "L5-B": "stronger_structured_governed_intelligence_with_deep_strategy_dossier",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_CIEU_backed_brain_learning_candidate_loop_no_production_brain_write",
        },
    }


def build_e115_deep_strategy_dossier(e114_result: Mapping[str, Any], *, owner_intent: str) -> dict[str, Any]:
    selected = dict(e114_result.get("selected_strategy") or {})
    selected_route_id = str(selected.get("selected_route_id") or "unknown_route")
    top_routes = [dict(row) for row in e114_result.get("top_routes", []) if isinstance(row, Mapping)]
    selected_route = next((row for row in top_routes if row.get("route_id") == selected_route_id), top_routes[0] if top_routes else {})
    domain_id = str(selected_route.get("domain_id") or "ai_security_compliance")
    source_scan = e114_result.get("live_public_read_scan_summary") if isinstance(e114_result.get("live_public_read_scan_summary"), Mapping) else {}
    source_evidence = _extract_evidence_items(e114_result)
    competitors = competitors_for_deep_strategy(domain_id)
    product = product_shape_for_route(domain_id)
    right_to_win = right_to_win_for_route(domain_id)
    assumptions = build_assumption_registry(selected_route_id, domain_id)
    dimensions = build_deep_reasoning_dimensions(
        owner_intent=owner_intent,
        selected=selected,
        selected_route=selected_route,
        top_routes=top_routes,
        evidence=source_evidence,
        competitors=competitors,
        product=product,
        right_to_win=right_to_win,
    )
    return {
        "dossier_id": "e115_deep_strategy_dossier",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "generation_mode": "brain_grounded_public_evidence_capability_utilized_deep_strategy",
        "source_runtime": "E114_live_web_capability_utilized_strategy_run",
        "source_runtime_result_id": e114_result.get("artifact_id"),
        "strategic_question_reframe": {
            "owner_intent": owner_intent,
            "core_question": "What is the easiest credible first-cash path where Y*Bridge Labs has a real right to win?",
            "not_the_question": [
                "not which prior anchor sounds familiar",
                "not which internal capability is impressive",
                "not which market is large in the abstract",
                "not a revenue/customer validation claim before feedback",
            ],
            "decision_standard": "choose the route with buyer urgency, source-dated evidence, credible differentiation, fast no-send validation, and low owner burden",
        },
        "deep_reasoning_dimensions": dimensions,
        "market_map": {
            "domains_analyzed": [
                {
                    "domain_id": row.get("domain_id"),
                    "route_id": row.get("route_id"),
                    "market_first_score": row.get("market_first_score"),
                    "evsi_usd": row.get("evsi_usd"),
                    "why_it_might_fail": row.get("why_it_might_fail"),
                }
                for row in top_routes
            ],
            "source_date_coverage": source_scan.get("source_date_summary", {}),
            "opportunity_cluster_count": source_scan.get("opportunity_cluster_count"),
            "evidence_count": source_scan.get("evidence_count"),
            "provider_mode": e114_result.get("provider_mode"),
            "interpretation": "This is a market-first ranking, not proof of customer demand.",
        },
        "selected_route_thesis": {
            "selected_route_id": selected_route_id,
            "domain_id": domain_id,
            "thesis": selected.get("why_this_path_now"),
            "second_best_path": selected.get("second_best_path"),
            "why_not_others": selected.get("why_not_others"),
            "evidence_refs": [item.get("evidence_id") or item.get("source_url") for item in source_evidence[:8]],
            "falsification_condition": selected.get("what_evidence_could_falsify_it"),
        },
        "customer_and_buyer_model": customer_model_for_route(domain_id),
        "competitive_landscape": {
            "selected_route_id": selected_route_id,
            "competitors_and_substitutes": competitors,
            "status_quo_alternative": "buyer continues with scattered docs, manual reviews, ad hoc governance, and delayed customer/security approvals",
            "competition_interpretation": "Competitors are strong; Y*Bridge Labs must avoid generic compliance SaaS and win with fast, buyer-specific evidence/control rescue artifacts.",
        },
        "right_to_win_and_right_to_lose": right_to_win,
        "product_shape": product,
        "pricing_and_value_capture": {
            "entry_offer": product["product_name"],
            "price_hypothesis_usd": "$500-$2,000 for first diagnostic/control pack; not validated",
            "why_price_might_be_plausible": "The deliverable is a risk/control/evidence acceleration artifact for teams with compliance or customer-blocking urgency.",
            "why_price_might_fail": "Buyers may prefer incumbent platforms, free templates, or existing consultants; only owner-approved feedback can validate willingness to pay.",
            "validation_status": "hypothesis_only_no_customer_validation",
        },
        "distribution_and_first_10_buyers": {
            "first_10_buyer_profiles": [
                "AI startup founder preparing enterprise security review",
                "small SaaS CTO deploying coding/support agents",
                "agency owner using agents for client operations",
                "compliance lead asked for AI policy evidence",
                "security consultant needing agent-risk deliverable support",
                "founder with customer questionnaire blocked by AI governance questions",
                "operator whose AI workflow caused repo/process drift",
                "AI app builder needing no-send execution boundary proof",
                "startup selling to regulated buyer",
                "small team needing audit-ready agent-use documentation",
            ],
            "channels": ["founder communities", "AI builder forums", "security/compliance consultants", "warm owner network", "no-send diagnostic examples"],
            "first_touch_boundary": "owner-approved L4 only; no autonomous outreach in this milestone",
        },
        "causal_zero_loop_model": {
            "X_t": "source-dated market evidence + Aiden brain provenance + capability utilization matrix",
            "U_t": "deep strategy synthesis and no-send validation design",
            "Y_star_t": "selected first-cash thesis with explicit assumptions",
            "expected_Y_t_plus_1": "owner can review a concrete buyer-facing diagnostic artifact and approve or reject L4 feedback",
            "predicted_R_t_plus_1": 0,
            "R_t_plus_1": 0.0,
            "residual_closed_by": "assumption registry, falsification conditions, no-send owner packet, and CIEU-backed residual learning",
        },
        "assumption_registry": assumptions,
        "experiment_design": {
            "experiment_id": "e115_no_send_buyer_diagnostic_validation_packet",
            "owner_decision_required": True,
            "owner_approval_state": "pending_owner_decision",
            "no_send_default": True,
            "external_action_executed": False,
            "provider_action_executed": False,
            "evidence_sought": ["urgent pain", "budget owner", "trusted alternative", "willingness to pay", "preferred product shape", "incumbent objection"],
            "kill_criteria": [item["falsification_condition"] for item in assumptions[:3]],
        },
        "post_action_residual_learning_plan": {
            "if_buyer_confirms": "convert confirmed pain into narrower offer and next governed action",
            "if_buyer_rejects": "write failure residual and pivot route/domain",
            "if_no_response": "classify as distribution/trust uncertainty, not product validation",
            "brain_learning_candidate": "write only through E112/CIEU-backed candidate path; no production brain mutation here",
        },
        "CIEU_predictions": [
            {
                "X_t": "deep strategy dossier",
                "U_t": "owner-approved no-send validation artifact",
                "Y_star_t": selected_route_id,
                "expected_Y_t_plus_1": "buyer feedback clarifies urgency, price, and trust barrier",
                "predicted_R_t_plus_1": 0,
                "residual_severity": "medium_until_buyer_feedback",
                "falsification_condition": "target buyer rejects urgency, budget, or trust in the deliverable",
            }
        ],
        "no_overclaim_boundary": {
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "L4_feedback_executed": False,
            "live_provider_execution_claim": False,
            "K9Audit_integration_claim": False,
        },
    }


def build_deep_reasoning_dimensions(
    *,
    owner_intent: str,
    selected: Mapping[str, Any],
    selected_route: Mapping[str, Any],
    top_routes: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
    competitors: Sequence[Mapping[str, Any]],
    product: Mapping[str, Any],
    right_to_win: Mapping[str, Any],
) -> list[dict[str, Any]]:
    refs = [str(item.get("evidence_id") or item.get("source_url")) for item in evidence[:6]]
    if not refs:
        refs = ["e114://source-dated-market-evidence"]
    route_names = [str(row.get("name")) for row in top_routes[:5]]
    return [
        _dimension("strategic_question_reframe", "The real question is right-to-win first cash, not abstract market size.", refs, owner_intent),
        _dimension("jobs_to_be_done", "Buyer job is to reduce AI-agent risk, customer/security friction, and evidence chaos quickly.", refs, product.get("buyer_visible_outcome")),
        _dimension("buyer_pain_and_trigger_events", "Trigger events include agent rollout, customer security review, AI policy request, or workflow drift.", refs, selected.get("what_evidence_could_falsify_it")),
        _dimension("budget_owner_and_procurement", "Budget owner is likely founder, CTO, security lead, or compliance owner; sale must avoid enterprise procurement first.", refs, "budget ownership remains unvalidated"),
        _dimension("competitive_landscape", "Incumbents own compliance automation; Y*Bridge Labs must avoid generic platform positioning.", [row["source_url"] for row in competitors[:5]], "distribution and trust are the weak spots"),
        _dimension("substitute_and_status_quo", "Status quo is scattered docs, manual reviews, templates, consultants, and deferred governance.", refs, "status quo may be good enough"),
        _dimension("founder_market_fit_and_right_to_win", "The strongest fit is governed agent execution evidence, not domain-specific accounting/legal advice.", refs, ", ".join(right_to_win.get("right_to_win_assets", [])[:3])),
        _dimension("product_shape_and_delivery_model", "The product must be a concrete evidence/control pack with visible deliverables, not a vague workflow.", refs, product.get("product_name")),
        _dimension("pricing_and_value_capture", "Price is only a hypothesis; value comes from shortening compliance/customer-blocking cycles.", refs, "willingness to pay unvalidated"),
        _dimension("distribution_and_first_10_buyers", "Initial distribution should target AI builders and operators with immediate governance pain.", refs, "cold outreach remains owner-gated"),
        _dimension("risk_regulatory_trust", "Risk is buyer trust, liability expectations, and incumbent credibility, not only implementation feasibility.", refs, "do not offer legal/compliance advice beyond diagnostic boundaries"),
        _dimension("causal_zero_loop_residual_model", "Every assumption has a falsification route and residual update path so Rt+1 can close to zero.", refs, "CZL closure required"),
        _dimension("experiment_and_kill_criteria", f"Top compared routes were: {', '.join(route_names)}.", refs, "kill if buyer rejects urgency/budget/trust"),
        _dimension("memory_and_learning_update", "New market facts become CIEU-backed brain-learning candidates, not uncontrolled brain writes.", refs, "production brain write remains disabled"),
    ]


def _dimension(dimension_id: str, conclusion: str, evidence_refs: Sequence[str], uncertainty: Any) -> dict[str, Any]:
    return {
        "dimension_id": dimension_id,
        "conclusion": conclusion,
        "evidence_refs": list(evidence_refs)[:8],
        "uncertainty": str(uncertainty or "requires owner-approved buyer feedback"),
        "decision_use": "mandatory_deep_strategy_reasoning_dimension",
    }


def product_shape_for_route(domain_id: str) -> dict[str, Any]:
    if domain_id in {"ai_security_compliance", "ai_agent_ops", "cyber_insurance"}:
        return {
            "product_name": "AI Agent Governance Evidence & Control Pack",
            "buyer_visible_outcome": "a 48-hour buyer-specific control/evidence pack that helps a small team explain and govern AI-agent behavior before customer/security review",
            "buyer_visible_deliverables": [
                "AI-agent action boundary map",
                "risk and failure-mode register",
                "evidence/source inventory for agent behavior claims",
                "CIEU-style decision/residual record template",
                "no-send provider/tool execution preflight",
                "governed Codex executor handoff checklist",
                "48-hour remediation priority list",
            ],
            "not_in_scope": ["legal advice", "security certification", "SOC2 automation platform", "customer outreach without owner approval"],
        }
    return {
        "product_name": "48h Operations Evidence & Rescue Pack",
        "buyer_visible_outcome": "a narrow operational bottleneck diagnosis with evidence, risk controls, and next-action plan",
        "buyer_visible_deliverables": [
            "workflow bottleneck map",
            "evidence-backed issue register",
            "automation/no-send preflight",
            "risk and trust boundary list",
            "48-hour action plan",
        ],
        "not_in_scope": ["done-for-you external execution without approval", "regulated professional advice"],
    }


def customer_model_for_route(domain_id: str) -> dict[str, Any]:
    return {
        "ideal_customer_profile": "small AI-enabled company or operator with urgent trust/evidence/control pain",
        "buyer_roles": ["founder", "CTO", "security lead", "compliance owner", "AI operations lead"],
        "trigger_events": ["AI agent rollout", "enterprise customer questionnaire", "security/compliance review", "unsafe automation incident", "repo/workflow drift"],
        "non_buyers": ["teams seeking generic chatbot advice", "buyers needing formal legal certification", "large enterprises requiring long procurement"],
        "trust_barriers": ["unknown vendor", "no formal certification", "unclear liability", "incumbent alternatives"],
    }


def competitors_for_deep_strategy(domain_id: str) -> list[dict[str, Any]]:
    if domain_id in {"ai_security_compliance", "ai_agent_ops", "cyber_insurance"}:
        rows = [
            ("Vanta", "compliance automation and trust management", "https://www.vanta.com/"),
            ("Drata", "security compliance automation", "https://drata.com/"),
            ("Secureframe", "security and compliance automation", "https://secureframe.com/"),
            ("Thoropass", "audit and compliance platform/services", "https://thoropass.com/"),
            ("Sprinto", "security compliance automation", "https://sprinto.com/"),
            ("Credo AI", "AI governance and risk management", "https://www.credo.ai/"),
            ("Lakera", "AI security platform", "https://www.lakera.ai/"),
        ]
    else:
        rows = [
            ("incumbent vertical SaaS", "existing workflow platform", "https://www.g2.com/"),
            ("human consultant", "manual expert service", "https://www.upwork.com/"),
            ("offshore service team", "lower-cost execution", "https://www.clutch.co/"),
            ("automation agency", "custom workflow build", "https://www.clutch.co/agencies"),
            ("spreadsheet/status quo", "manual internal process", "https://workspace.google.com/products/sheets/"),
        ]
    return [
        {
            "name": name,
            "how_they_solve": solves,
            "source_url": url,
            "observed_at": "2026-05-09",
            "threat_level": "high" if idx < 4 else "medium_high",
            "why_us_must_be_different": "win only by fast buyer-specific control/evidence rescue, not by pretending to be a broad platform",
        }
        for idx, (name, solves, url) in enumerate(rows)
    ]


def right_to_win_for_route(domain_id: str) -> dict[str, Any]:
    return {
        "right_to_win_assets": [
            "Y-star-gov deterministic runtime governance",
            "CIEUStore evidence and residual records",
            "E113 no-new-wheel capability utilization law",
            "E112 source-date freshness and brain-learning candidate filter",
            "E92 CEO principal / Codex executor boundary",
            "gov-mcp dry-run/no-send execution boundary",
            "Aiden brain-grounded strategy runtime",
        ],
        "right_to_lose_risks": [
            "weak external trust before buyer feedback",
            "incumbents have distribution and compliance credibility",
            "market evidence is still public-read, not customer validation",
            "production brain write remains disabled",
        ],
        "fit_interpretation": (
            "Y*Bridge Labs is not best suited to generic SaaS or regulated professional advice. "
            f"It is best suited where controlled AI-agent behavior and evidence are the product. Domain={domain_id}."
        ),
    }


def build_assumption_registry(selected_route_id: str, domain_id: str) -> list[dict[str, Any]]:
    return [
        {
            "assumption_id": "a1_buyer_urgency",
            "claim": "target buyers feel urgent pain around AI-agent governance evidence",
            "test_method": "owner-approved no-send feedback packet",
            "falsification_condition": "buyers say the problem is not urgent this quarter",
        },
        {
            "assumption_id": "a2_budget_owner_exists",
            "claim": "founder/CTO/security owner can approve a small diagnostic purchase",
            "test_method": "ask budget-owner question in L4 packet",
            "falsification_condition": "buyers route it to long procurement or no budget owner exists",
        },
        {
            "assumption_id": "a3_product_shape_clear",
            "claim": "the evidence/control pack is understandable and concrete",
            "test_method": "show no-send product outline",
            "falsification_condition": "buyers cannot explain what they would receive",
        },
        {
            "assumption_id": "a4_right_to_win_matters",
            "claim": "governed runtime evidence differentiates against generic compliance tools",
            "test_method": "ask why not Vanta/Drata/manual consultant",
            "falsification_condition": "buyers prefer incumbents and do not value runtime evidence",
        },
        {
            "assumption_id": "a5_price_range",
            "claim": f"{selected_route_id} in {domain_id} can support a $500-$2,000 diagnostic hypothesis",
            "test_method": "ask willingness-to-pay range after product shape is clear",
            "falsification_condition": "buyers expect free template or sub-$200 price",
        },
    ]


def _extract_evidence_items(e114_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    host = e114_result.get("host_runtime_result") if isinstance(e114_result.get("host_runtime_result"), Mapping) else {}
    source = host.get("source_e114_result") if isinstance(host.get("source_e114_result"), Mapping) else {}
    strategy = source.get("strategy") if isinstance(source.get("strategy"), Mapping) else {}
    scan = strategy.get("live_global_open_world_scan") if isinstance(strategy.get("live_global_open_world_scan"), Mapping) else {}
    items = [dict(item) for item in scan.get("evidence_items", []) if isinstance(item, Mapping)]
    if items:
        return items
    brain_cycle = e114_result.get("brain_learning_cycle_result") if isinstance(e114_result.get("brain_learning_cycle_result"), Mapping) else {}
    host = brain_cycle.get("host_runtime_result") if isinstance(brain_cycle.get("host_runtime_result"), Mapping) else {}
    strategy_result = host.get("strategy_result") if isinstance(host.get("strategy_result"), Mapping) else {}
    strategy = strategy_result.get("strategy") if isinstance(strategy_result.get("strategy"), Mapping) else {}
    scan = strategy.get("live_global_open_world_scan") if isinstance(strategy.get("live_global_open_world_scan"), Mapping) else {}
    return [dict(item) for item in scan.get("evidence_items", []) if isinstance(item, Mapping)]


def summarize_e115_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT event_type, decision FROM cieu_events ORDER BY seq_global").fetchall()
    finally:
        conn.close()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def write_e115_deep_strategy_reports(
    *,
    cieu_db: str | Path,
    root: Path | None = None,
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    use_host_live_network: bool = False,
) -> dict[str, Any]:
    repo_root = root or BRIDGE_ROOT
    result = run_e115_deep_strategic_intelligence_runtime(
        cieu_db=cieu_db,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        use_host_live_network=use_host_live_network,
        seal_session=False,
    )
    report = build_e115_report(result)
    report_path = repo_root / "office" / "mission_command" / "e115_deep_strategic_intelligence_runtime_report.json"
    readback_path = repo_root / "office" / "mission_command" / "e115_deep_strategic_intelligence_runtime_readback.md"
    status_json = repo_root / "operations" / "baseline" / "e87r_full_repo_baseline" / "current_runtime_status_after_e115_deep_strategic_intelligence_runtime.json"
    status_md = repo_root / "operations" / "baseline" / "e87r_full_repo_baseline" / "current_runtime_status_after_e115_deep_strategic_intelligence_runtime.md"
    for path in (report_path, readback_path, status_json, status_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readback_path.write_text(render_e115_readback(report), encoding="utf-8")
    status_json.write_text(json.dumps(report["runtime_status"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    status_md.write_text(render_e115_status(report), encoding="utf-8")
    return report


def build_e115_report(result: Mapping[str, Any]) -> dict[str, Any]:
    dossier = result["deep_strategy_dossier"]
    selected = dossier["selected_route_thesis"]
    product = dossier["product_shape"]
    return {
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "deep_strategy_runtime_proven": result["deep_strategy_runtime_proven"],
        "YstarGov_decision": result["YstarGov_deep_strategy_write_result"]["governance_decision"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "selected_route_id": selected["selected_route_id"],
        "product_shape": product,
        "deep_reasoning_dimension_count": len(dossier["deep_reasoning_dimensions"]),
        "competitor_count": len(dossier["competitive_landscape"]["competitors_and_substitutes"]),
        "assumption_count": len(dossier["assumption_registry"]),
        "market_map": dossier["market_map"],
        "right_to_win_and_right_to_lose": dossier["right_to_win_and_right_to_lose"],
        "experiment_design": dossier["experiment_design"],
        "runtime_status": {
            "L5-A": result["L5_truth_table_after"]["L5-A"],
            "L5-B": result["L5_truth_table_after"]["L5-B"],
            "L5-C": result["L5_truth_table_after"]["L5-C"],
            "L5-D": result["L5_truth_table_after"]["L5-D"],
            "L5-E": result["L5_truth_table_after"]["L5-E"],
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_signal": True,
            "no_external_action_executed": True,
        },
    }


def render_e115_readback(report: Mapping[str, Any]) -> str:
    product = report["product_shape"]
    return (
        "# E115 Deep Strategic Intelligence Runtime Readback\n\n"
        f"- Y-star-gov decision: {report['YstarGov_decision']['decision']}\n"
        f"- Deep runtime proven: {str(report['deep_strategy_runtime_proven']).lower()}\n"
        f"- Selected route: {report['selected_route_id']}\n"
        f"- Product: {product['product_name']}\n"
        f"- Deep reasoning dimensions: {report['deep_reasoning_dimension_count']}\n"
        f"- Competitors/substitutes: {report['competitor_count']}\n"
        f"- Assumptions: {report['assumption_count']}\n"
        f"- CIEU events: {report['CIEUStore_summary']['event_count']}\n\n"
        "No external action, customer validation, revenue, payment, live provider execution, or K9Audit integration is claimed.\n"
    )


def render_e115_status(report: Mapping[str, Any]) -> str:
    status = report["runtime_status"]
    return (
        "# Current Runtime Status After E115\n\n"
        f"- L5-A: {status['L5-A']}\n"
        f"- L5-B: {status['L5-B']}\n"
        f"- L5-C: {status['L5-C']}\n"
        f"- L5-D: {status['L5-D']}\n"
        f"- L5-E: {status['L5-E']}\n"
    )


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run E115 Aiden deep strategic intelligence runtime.")
    parser.add_argument("--cieu-db", required=True)
    parser.add_argument("--brain-db")
    parser.add_argument("--use-host-live-network", action="store_true")
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args()
    brain_db = Path(args.brain_db) if args.brain_db else None
    if args.write_reports:
        report = write_e115_deep_strategy_reports(
            cieu_db=args.cieu_db,
            brain_db=brain_db,
            use_host_live_network=args.use_host_live_network,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        result = run_e115_deep_strategic_intelligence_runtime(
            cieu_db=args.cieu_db,
            brain_db=brain_db,
            use_host_live_network=args.use_host_live_network,
        )
        print(json.dumps(build_e115_report(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "build_e115_deep_strategy_dossier",
    "run_e115_deep_strategic_intelligence_runtime",
    "write_e115_deep_strategy_reports",
]
