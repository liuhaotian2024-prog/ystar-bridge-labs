from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e90_ceo_strategic_intelligence_benchmark import (
    score_ceo_strategic_intelligence,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
MILESTONE_ID = "E97_CEO_Runtime_Certified_Unanchored_Global_Strategy_Rerun_R1"
SESSION_ID = "e97_unanchored_global_strategy_rerun"


def _load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def build_unanchored_global_strategy_artifact(*, owner_intent: str | None = None) -> dict[str, Any]:
    """Build a zero-thesis CEO strategy artifact.

    This intentionally does not call E90's default strategy scope. The prior
    route is included only as a competitor so it has to win on evidence.
    """

    intent = owner_intent or (
        "Reopen global market strategy from zero, ignore recent route inertia, and find the easiest credible "
        "cash path from current Y*Bridge Labs capabilities without claiming customer/revenue validation."
    )
    routes = _route_candidates()
    strategy = {
        "artifact_id": "e97_unanchored_global_strategy_rerun",
        "milestone_id": MILESTONE_ID,
        "strategy_run_id": "e97_unanchored_global_strategy_rerun",
        "session_id": SESSION_ID,
        "generated_at": _now(),
        "generation_mode": "unanchored_runtime_structured_output",
        "owner_intent": intent,
        "anti_recent_memory_anchor": {
            "initial_seed_thesis": "none",
            "old_E90_route_status": "competitor_only_not_default",
            "old_thesis_forced_to_compete": True,
            "forbidden_shortcut": "do not start from Governed Business Operations Blueprint or CIEU Audit Module",
        },
        "internal_capability_map": _internal_capability_map(),
        "historical_route_assets": _historical_route_assets(),
        "external_market_evidence_map": {
            "freshness_status": "current_public_read_as_of_2026-05-08_via_read_only_web_research",
            "evidence_mode": "public_read_only_no_contact_no_login_no_payment_no_publication",
            "evidence_items": _external_evidence_items(),
        },
        "no_new_wheel_proof": {
            "reused_systems": [
                "E87R full repo baseline",
                "E88 CEO runtime session",
                "E89 CEO intelligence compiler",
                "Y-star-gov strategic benchmark validator",
                "Y-star-gov CIEUStore",
                "gov-mcp dry-run/no-send boundary",
            ],
            "not_rebuilt": [
                "no new behavior center",
                "no new governance engine",
                "no new CIEU ledger",
                "no new provider executor",
            ],
        },
        "route_candidates": routes,
        "route_scoring": _route_scoring(),
        "selected_strategy": {
            "current_best_first_cash_path": "Agent Autonomy Flight Recorder readiness sprint for teams moving AI agents from pilot to production",
            "second_best_path": "AI agent incident simulation and red-team drill for internal tool-using agents",
            "why_this_path_now": (
                "It turns our strongest existing capability into an urgent buyer job: before an AI agent gets "
                "tool access, prove its action boundaries, receipts, no-send controls, and residual learning. "
                "It can be sold as a short readiness sprint before SaaS exists."
            ),
            "why_not_others": [
                "The old CIEU audit module route is technically strong but too abstract as a first buyer promise.",
                "A broad AI CEO operating system is strategically large but too hard to explain before trust is earned.",
                "K9Audit productization should wait until a tested bridge exists.",
                "Generic public-read market intelligence is easier to copy and less tied to our governance moat.",
                "Payment/revenue automation is high risk and not appropriate before L4 feedback.",
            ],
            "what_evidence_could_falsify_it": (
                "Owner-approved conversations or public-read follow-up show agent teams do not feel acute pain "
                "around tool access, auditability, or pre-production agent risk, or will not pay for readiness proof."
            ),
            "next_48h_action": "Package one no-send Agent Autonomy Flight Recorder demo report using an example tool-using agent workflow.",
            "next_7d_action": "Run owner-approved L4 feedback on the demo report with three target profiles; no send until approval.",
            "next_owner_decision_needed": "Approve or reject one no-send L4 feedback packet for the readiness sprint offer.",
        },
        "do_not_pursue_list": [
            "Do not pitch a broad AI CEO OS as the first offer.",
            "Do not sell K9Audit integration as active.",
            "Do not claim customer validation, pricing validation, paid demand, or compliance certification.",
            "Do not execute outreach, publication, payment, login, or production deployment in this run.",
            "Do not let static evidence maps replace live public-read observation in future non-test strategy runs.",
        ],
        "adversarial_critique": [
            "The flight-recorder phrase may still sound like security theater unless the demo shows before/after action receipts.",
            "Small teams may agree with the risk but lack budget unless the sprint is packaged as production-readiness acceleration.",
            "Security buyers may ask for integrations and certifications we do not yet have; the offer must stay scoped to readiness proof.",
            "The old CIEU audit route could be technically superior but commercially weaker because buyers do not know that vocabulary.",
            "A no-send demo may not prove willingness to pay; the next L4 feedback must test urgency and budget owner language.",
        ],
        "what_not_to_do_next": [
            "do not build SaaS before one readiness sprint offer is tested",
            "do not claim legal compliance certification",
            "do not run live outreach without owner approval",
            "do not pitch broad AI CEO OS first",
            "do not sell K9Audit as integrated",
            "do not accept static evidence as live market learning",
        ],
        "next_L4_feedback_owner_decision_packet": _next_l4_packet(),
        "CIEU_predictions": _cieu_predictions(),
        "post_strategy_residual_plan": {
            "evaluate_strategy_quality_by": "whether owner-approved L4 feedback recognizes agent autonomy risk as urgent and budget-relevant",
            "future_evidence_updates": [
                "language buyers use for agent tool-access risk",
                "whether readiness sprint feels like security/compliance/ops budget",
                "which workflow demo triggers strongest recognition",
            ],
            "pivot_trigger": "target profiles call it interesting but not urgent, or prefer implementation help over readiness/audit proof",
            "what_not_to_do_next": "do not build a platform before testing whether readiness sprint language earns attention",
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
    strategy["benchmark_result"] = score_ceo_strategic_intelligence(strategy)
    return strategy


def run_e97_unanchored_global_strategy_rerun(
    *,
    cieu_db: str | Path,
    owner_intent: str | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    strategy = build_unanchored_global_strategy_artifact(owner_intent=owner_intent)
    governance = _load_ystar_governance(ystar_gov_root)
    write_result = governance.validate_and_write_ceo_strategic_intelligence_strategy(
        strategy,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    cieu_summary = summarize_e97_cieustore(cieu_db)
    receipt = build_ceo_runtime_receipt(strategy, write_result, cieu_summary)
    return {
        "artifact_id": "e97_unanchored_global_strategy_session",
        "milestone_id": MILESTONE_ID,
        "strategy": strategy,
        "YstarGov_write_result": write_result,
        "CEO_runtime_receipt": receipt,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_strategy_record_proven": receipt["CIEUStore_written"] is True
        and receipt["Y_star_gov_decision"] == "ALLOW",
        "recommended_next_milestone": "E98_Agent_Autonomy_Flight_Recorder_No_Send_Demo_And_L4_Feedback_Packet_R1",
    }


def build_ceo_runtime_receipt(
    strategy: Mapping[str, Any],
    write_result: Mapping[str, Any],
    cieu_summary: Mapping[str, Any],
) -> dict[str, Any]:
    decision = write_result.get("governance_decision", {}).get("decision", "")
    return {
        "mode": "CEO_RUNTIME_CERTIFIED_STRATEGY_RECORD" if decision == "ALLOW" else "CEO_RUNTIME_REQUIRES_REVISION",
        "owner_intent": strategy.get("owner_intent"),
        "CEO_order_id": "e97_unanchored_global_strategy_order",
        "runtime_session_id": SESSION_ID,
        "Y_star_gov_decision": decision,
        "CIEUStore_written": bool(write_result.get("formal_CIEU_log_written")),
        "CIEU_event_count": cieu_summary.get("event_count", 0),
        "CIEU_event_types": cieu_summary.get("event_types", []),
        "doctrines_invoked": [
            "external_observation_public_read_evidence",
            "market_dynamics_and_buyer_pain",
            "counterfactual_candidate_selection",
            "commercial_sharpness_gate",
            "cieu_prediction_residual_learning",
            "Y-star-gov strategic benchmark validator",
        ],
        "external_observation_status": "live_public_read_by_codex_web_tool_recorded_as_public_read_evidence_not_customer_validation",
        "generation_mode": strategy.get("generation_mode"),
        "Codex_role": "public_read_collector_and_structured_report_writer_not_strategy_owner",
        "truth_boundary": {
            "no_L4_feedback_executed": True,
            "no_customer_validation": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def summarize_e97_cieustore(cieu_db: str | Path) -> dict[str, Any]:
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


def write_e97_reports(result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    mission_dir = root / "office" / "mission_command"
    status_dir = root / "operations" / "baseline" / "e87r_full_repo_baseline"
    mission_dir.mkdir(parents=True, exist_ok=True)
    status_dir.mkdir(parents=True, exist_ok=True)
    report_json = mission_dir / "e97_unanchored_global_strategy_rerun_report.json"
    readback_md = mission_dir / "e97_unanchored_global_strategy_rerun_readback.md"
    status_json = status_dir / "current_runtime_status_after_e97_unanchored_global_strategy_rerun.json"
    status_md = status_dir / "current_runtime_status_after_e97_unanchored_global_strategy_rerun.md"

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


def _external_evidence_items() -> list[dict[str, Any]]:
    return [
        _evidence(
            "mckinsey_agentic_security",
            "McKinsey: Deploying agentic AI with safety and security",
            "https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/deploying-agentic-ai-with-safety-and-security-a-playbook-for-technology-leaders",
            "agentic_ai_risk_governance",
            "Agentic systems shift from interaction to transaction and need updated AI policy, IAM, oversight, and controls.",
        ),
        _evidence(
            "mckinsey_trust_agents",
            "McKinsey: Trust in the age of agents",
            "https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/trust-in-the-age-of-agents",
            "accountability_for_agent_action",
            "Agency is a transfer of decision rights; leaders need auditable scope, inventory, ownership, and accountability.",
        ),
        _evidence(
            "ibm_ai_oversight_gap",
            "IBM Cost of a Data Breach 2025",
            "https://www.ibm.com/reports/data-breach",
            "shadow_ai_and_access_controls",
            "IBM reports an AI oversight gap around governance policies, AI access controls, and incidents.",
        ),
        _evidence(
            "infosys_hfs_scaling_gap",
            "Infosys-HFS Agentic AI scaling report",
            "https://www.infosys.com/newsroom/features/2026/enterprises-scaled-agentic-ai.html",
            "agentic_ai_scaling_gap",
            "Only a minority of enterprises have scaled agentic AI; governance, data readiness, and ownership gaps block scale.",
        ),
        _evidence(
            "infosys_responsible_ai_gap",
            "Infosys Responsible Enterprise AI in the Agentic Era",
            "https://www.infosys.com/newsroom/press-releases/2025/responsible-enterprise-ai-agentic.html",
            "responsible_ai_controls_gap",
            "Enterprise leaders expect heightened risks from agentic AI while only a small share meet strong RAI controls.",
        ),
        _evidence(
            "eu_ai_act_timeline",
            "EU AI Act implementation timeline",
            "https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act",
            "regulatory_timing",
            "AI Act obligations and enforcement phases create demand for transparency, governance, and readiness evidence.",
        ),
        _evidence(
            "nist_ai_rmf",
            "NIST AI Risk Management Framework",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "risk_management_language",
            "NIST AI RMF provides cross-sector vocabulary for trustworthy AI risk management and governance.",
        ),
        _evidence(
            "owasp_agentic_top_10",
            "OWASP Top 10 for Agentic Applications",
            "https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security/",
            "agentic_security_threat_model",
            "OWASP separates agentic application risks such as tool misuse, identity abuse, supply-chain issues, and unexpected code execution.",
        ),
        _evidence(
            "owasp_agentic_skills",
            "OWASP Agentic Skills Top 10",
            "https://owasp.org/www-project-agentic-skills-top-10/",
            "agent_skill_execution_layer_risk",
            "Agentic skills define what tools actually do, making the execution layer a security target.",
        ),
    ]


def _route_candidates() -> list[dict[str, Any]]:
    return [
        _route("agent_autonomy_flight_recorder", "Agent Autonomy Flight Recorder readiness sprint", "pre-production black box, brake, receipt, and residual learning for tool-using AI agents", "service_sprint"),
        _route("agent_incident_simulation", "AI agent incident simulation and red-team drill", "simulate tool misuse, scope expansion, prompt hijack, and no-send failures before production", "service_sprint"),
        _route("agent_skill_supply_chain_scanner", "Agent skill/tool supply-chain scanner", "scan agent skills, MCP/tool configs, and scripts for ungoverned action surfaces", "developer_security_tool"),
        _route("eu_ai_act_agent_readiness_pack", "EU AI Act agent transparency/logging readiness pack", "prepare deployer-facing transparency, logging, and governance evidence for agent workflows", "compliance_readiness"),
        _route("no_send_outbound_preflight", "No-send outbound agent preflight for sales/support agents", "prove outbound agent messages are transparent, opt-out ready, suppressed, and receipt-backed before send", "provider_tool_dry_run"),
        _route("public_read_market_radar", "Autonomous public-read market radar for founders", "continuous public-read evidence synthesis with no contact or publication", "market_intelligence"),
        _route("codex_executor_boundary_pack", "Codex executor governance pack for AI engineering teams", "force implementation work through CEOImplementationOrder and execution receipts", "engineering_governance"),
        _route("legacy_cieu_audit_module", "Legacy CIEU audit module route", "prior CIEU audit module route retained as a competitor, not default", "legacy_competitor"),
    ]


def _route_scoring() -> list[dict[str, Any]]:
    rows = [
        ("agent_autonomy_flight_recorder", 5, 5, 2, 5, 2, 5, 5, 1, "demo one agent workflow readiness report; then owner-approved L4 feedback", "buyers do not recognize agent autonomy risk as urgent"),
        ("agent_incident_simulation", 4, 5, 2, 4, 3, 4, 5, 2, "package three incident simulations and no-send receipts", "teams prefer generic security review over agent-specific drill"),
        ("agent_skill_supply_chain_scanner", 4, 4, 3, 3, 3, 4, 4, 2, "scan existing scripts/skills and produce quarantine report", "market expects open-source/free scanner"),
        ("eu_ai_act_agent_readiness_pack", 3, 4, 4, 3, 4, 3, 5, 3, "map readiness pack to EU AI Act transparency/logging language", "buyers require formal legal advice or certification"),
        ("no_send_outbound_preflight", 4, 4, 3, 4, 3, 4, 4, 2, "dry-run sales/support agent message workflow with receipts", "buyers want execution not preflight"),
        ("public_read_market_radar", 3, 3, 2, 4, 2, 2, 2, 1, "run public-read radar for one vertical", "too easy to copy and weak governance moat"),
        ("codex_executor_boundary_pack", 3, 3, 2, 5, 3, 4, 3, 1, "package CEOImplementationOrder/CodexExecutionReceipt demo", "too niche outside AI engineering teams"),
        ("legacy_cieu_audit_module", 3, 3, 3, 4, 4, 3, 4, 2, "rename as part of flight recorder rather than standalone product", "too abstract as first buyer promise"),
    ]
    return [
        {
            "route_id": rid,
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
        for rid, speed, pain, proof, readiness, friction, diff, trust, burden, next_step, kill in rows
    ]


def _internal_capability_map() -> dict[str, Any]:
    return {
        "bridge-labs": [
            "CEO behavior center",
            "brain provenance",
            "intelligence compiler",
            "strategy benchmark",
            "controlled capability catalog",
            "CEOImplementationOrder/CodexExecutionReceipt boundary",
        ],
        "Y-star-gov": [
            "deterministic governance validators",
            "CEO Cognitive OS runtime hook",
            "strategic benchmark validator",
            "CIEUStore.write_dict formal record path",
        ],
        "gov-mcp": ["dry-run provider/tool boundary", "no-send receipts", "provider_action_executed=false invariant"],
        "K9Audit": ["separate stronger evidence chain boundary; not integrated in this run"],
    }


def _historical_route_assets() -> list[str]:
    return [
        "operations/baseline/e87r_full_repo_baseline/baseline_summary.json",
        "operations/controlled_capability_catalog/e96_controlled_capability_catalog.json",
        "office/mission_command/e90_market_grounded_strategy_run_report.json",
        "operations/ceo_doctrine_registry/e91_canonical_doctrine_registry_spec.json",
        "office/mission_command/e92_ceo_principal_codex_executor_boundary_report.json",
        "office/mission_command/e96_ceo_controlled_capability_control_plane_report.json",
        "office/mission_command/e94_behavior_center_runtime_gateway_report.json",
    ]


def _next_l4_packet() -> dict[str, Any]:
    return {
        "packet_id": "e97_next_l4_feedback_owner_decision_packet",
        "target_profile": "AI agent builder, AI automation agency, MSP/Copilot implementer, or engineering lead moving agents from pilot to production",
        "message_hypothesis": "Before your AI agent gets tool access, would a black-box action receipt and no-send readiness report reduce production risk?",
        "evidence_sought": [
            "whether the pain is urgent",
            "whether readiness sprint is easier to buy than a platform",
            "which budget owner recognizes the problem",
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


def _cieu_predictions() -> list[dict[str, Any]]:
    return [
        {
            "X_t": "Old E90 route may be anchoring strategy around CIEU audit language.",
            "U_t": "Run unanchored cross-market route competition with public-read evidence and Y-star-gov benchmark write.",
            "Y_star_t": "Select a sharper first-cash wedge if evidence and route scoring beat the old thesis.",
            "expected_Y_t_plus_1": "CEO picks Agent Autonomy Flight Recorder or another route with stronger buyer pain clarity.",
            "predicted_R_t_plus_1": "No customer validation or revenue proof exists until owner-approved L4 feedback.",
            "residual_severity": "medium",
            "falsification_condition": "L4 feedback says agent autonomy readiness is not urgent or budget-owned.",
        }
    ]


def _evidence(evidence_id: str, title: str, url: str, category: str, summary: str) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "source_title": title,
        "source_url": url,
        "category": category,
        "claim_summary": summary,
        "evidence_type": "public_read_only",
    }


def _route(route_id: str, name: str, description: str, route_type: str) -> dict[str, str]:
    return {"route_id": route_id, "name": name, "description": description, "route_type": route_type}


def _report(result: Mapping[str, Any]) -> dict[str, Any]:
    strategy = result["strategy"]
    return {
        "milestone_id": MILESTONE_ID,
        "CEO_runtime_receipt": result["CEO_runtime_receipt"],
        "anti_recent_memory_anchor": strategy["anti_recent_memory_anchor"],
        "selected_strategy": strategy["selected_strategy"],
        "route_candidates": strategy["route_candidates"],
        "route_scoring": strategy["route_scoring"],
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
            "No K9Audit write or integration was claimed.",
        ],
        "recommended_next_milestone": result["recommended_next_milestone"],
    }


def _status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "CEO_runtime_receipt": result["CEO_runtime_receipt"],
        "L5-A": "complete_internal_runtime_foundation",
        "L5-B": "complete_for_structured_governed_intelligence_loop_with_unanchored_strategy_rerun",
        "L5-B+": "partial_dynamic_intelligence_pending_owner_approved_live_feedback",
        "L5-C": "partial_dry_run_only",
        "L5-D": "absent_or_not_executed",
        "next": result["recommended_next_milestone"],
    }


def _report_md(report: Mapping[str, Any]) -> str:
    receipt = report["CEO_runtime_receipt"]
    selected = report["selected_strategy"]
    lines = [
        "# E97 Unanchored Global Strategy Rerun",
        "",
        "## CEO Runtime Receipt",
        f"- mode: `{receipt['mode']}`",
        f"- Y-star-gov decision: `{receipt['Y_star_gov_decision']}`",
        f"- CIEUStore written: `{str(receipt['CIEUStore_written']).lower()}`",
        f"- CIEU events: `{receipt['CIEU_event_count']}`",
        "",
        "## Anti-Recent-Memory Anchor",
        f"- initial_seed_thesis: `{report['anti_recent_memory_anchor']['initial_seed_thesis']}`",
        f"- old_E90_route_status: `{report['anti_recent_memory_anchor']['old_E90_route_status']}`",
        "",
        "## Selected Strategy",
        f"- first_cash_path: {selected['current_best_first_cash_path']}",
        f"- second_best_path: {selected['second_best_path']}",
        f"- next_48h_action: {selected['next_48h_action']}",
        "",
        "## Route Candidates",
    ]
    lines.extend(f"- `{route['route_id']}`: {route['name']}" for route in report["route_candidates"])
    lines.append("")
    lines.append("## Not Claimed")
    lines.extend(f"- {item}" for item in report["what_was_not_claimed"])
    return "\n".join(lines).rstrip() + "\n"


def _status_md(status: Mapping[str, Any]) -> str:
    receipt = status["CEO_runtime_receipt"]
    return "\n".join(
        [
            "# Current Runtime Status After E97",
            "",
            f"- CEO_runtime_mode: `{receipt['mode']}`",
            f"- Y-star-gov decision: `{receipt['Y_star_gov_decision']}`",
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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_ceo_runtime_receipt",
    "build_unanchored_global_strategy_artifact",
    "run_e97_unanchored_global_strategy_rerun",
    "summarize_e97_cieustore",
    "write_e97_reports",
]
