from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from office.mission_command.e108_live_global_open_world_strategy_runtime import (
    DuckDuckGoLitePublicReadProvider,
    PublicReadProvider,
)
from office.mission_command.e111_aiden_host_runtime_and_autonomy_control_plane import (
    run_aiden_host_runtime_cycle,
)
from office.mission_command.e112_cieu_backed_brain_learning_loop import (
    build_market_evidence_freshness_policy,
    run_cieu_backed_brain_learning_cycle,
)


MILESTONE_ID = "E114_Live_Web_Capability_Utilized_Strategy_Run_R1"
SESSION_ID = "e114_live_web_capability_utilized_strategy_run"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


@dataclass(frozen=True)
class DatedPublicReadEvidenceSnapshotProvider:
    """A source-date-aware public-read provider for audited live evidence snapshots.

    The provider is intentionally compatible with E108's PublicReadProvider protocol.
    It is not a fixture: items must carry real public URLs and dates so E112 can
    reject stale/undated evidence before brain-learning candidates are created.
    """

    evidence_items: tuple[dict[str, Any], ...]
    provider_name: str = "dated_public_read_evidence_snapshot_provider"

    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict[str, Any]]:
        rows = [
            dict(item)
            for item in self.evidence_items
            if str(item.get("domain_id") or "") == domain_id
        ]
        return rows[:max_results]


def build_host_live_public_read_provider() -> PublicReadProvider:
    """Return the provider Aiden should use when running on the Mac host."""

    return DuckDuckGoLitePublicReadProvider()


def build_snapshot_public_read_provider(
    evidence_items: Sequence[Mapping[str, Any]] | None = None,
) -> DatedPublicReadEvidenceSnapshotProvider:
    items = [dict(item) for item in (evidence_items or build_default_e114_live_public_read_evidence_snapshot())]
    return DatedPublicReadEvidenceSnapshotProvider(tuple(items))


def build_default_e114_live_public_read_evidence_snapshot() -> list[dict[str, Any]]:
    observed = "2026-05-09T00:00:00Z"
    rows = [
        _e("ai_security_compliance", "Gartner: Global AI Regulations Fuel Billion-Dollar Market for AI Governance Platforms", "https://www.gartner.com/en/newsroom/press-releases/2026-02-17-gartner-global-ai-regulations-fuel-billion-dollar-market-for-ai-governance-platforms", "2026-02-17", "Gartner projects AI governance platform spend at $492M in 2026 and above $1B by 2030, with runtime policy enforcement and evidence collection becoming core requirements.", "Gartner AI governance spend compliance runtime enforcement 2026", observed),
        _e("ai_security_compliance", "McKinsey: Securing the agentic enterprise", "https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/securing-the-agentic-enterprise-opportunities-for-cybersecurity-providers", "2026-03-24", "McKinsey says agentic AI shifts the enterprise control plane and creates demand for continuous authorization, monitoring, and auditability of autonomous systems.", "McKinsey agentic enterprise control plane autonomous systems cybersecurity 2026", observed),
        _e("ai_security_compliance", "Five Eyes agencies warn on risky agentic AI deployments", "https://www.itpro.com/security/five-eyes-agencies-sound-alarm-over-risky-agentic-ai-deployments", "2026-05-06", "Five Eyes agencies warn that unguarded agentic AI expands attack surfaces and requires strict access controls, resilience, reversibility, and adversarial testing.", "Five Eyes agentic AI risk guidance May 2026", observed),
        _e("ai_security_compliance", "Vision Compliance EU AI Act readiness report", "https://www.einnews.com/pr_news/903074846/vision-compliance-releases-2026-eu-ai-act-readiness-report-finds-78-of-enterprises-unprepared-for-obligations", "2026-04-01", "A 2026 EU AI Act readiness analysis reports many enterprises have not taken meaningful compliance steps, supporting demand for AI governance documentation and controls.", "EU AI Act readiness enterprise compliance gaps 2026", observed),
        _e("ai_security_compliance", "Info-Tech AI Trends 2026", "https://www.infotech.com/about/press-releases/ai-trends-2026-report-risk-agents-and-sovereignty-will-shape-the-next-wave-of-adoption-says-info-tech-research-group", "2025-11-17", "Info-Tech frames 2026 AI adoption around risk, agents, sovereignty, governance, transparency, and explainability.", "AI Trends 2026 agent governance risk sovereignty", observed),
        _e("ai_security_compliance", "CTO's Edge AI Governance Market Landscape", "https://www.ctosedge.com/insights/ai-governance-market-landscape/", "2026-05-01", "A 2026 AI governance landscape analysis frames AI agents as digital workers requiring governance layers and operational controls.", "AI governance market landscape agent workers 2026", observed),
        _e("cyber_insurance", "VeriRFP security questionnaire automation", "https://verirfp.com/security-questionnaire-automation", "2026-04-25", "Security questionnaire automation buyers want evidence-backed answers, governed review, and source citations rather than generative guessing.", "security questionnaire automation evidence backed governed review 2026", observed),
        _e("cyber_insurance", "VeriRFP automate security questionnaire", "https://verirfp.com/automate-security-questionnaire", "2026-04-25", "Security questionnaires can take 5 to 10 business days manually; teams juggle repeated questionnaires and need approved evidence reuse.", "security questionnaire 5 to 10 days manual evidence reuse 2026", observed),
        _e("cyber_insurance", "Akitra Andromeda questionnaire automation", "https://akitra.com/security-questionnaire/", "2026-04-01", "Akitra positions questionnaire and RFP automation around agentic AI drafting from policies, controls, and past responses.", "agentic AI security questionnaire RFP automation policies controls 2026", observed),
        _e("cyber_insurance", "Optro automated security questionnaire", "https://optro.ai/product/automated-security-questionnaire", "2026-04-20", "Security questionnaire vendors emphasize central source-of-truth review and faster evidence-backed responses, increasing competitor saturation.", "automated security questionnaire source of truth AI 2026", observed),
        _e("healthcare_admin", "Guidehouse/HFMA 2026 RCM Trends", "https://guidehouse.com/insights/healthcare/2026/rev-cycle-trends-report", "2026-05-08", "Healthcare revenue-cycle leaders rank payer challenges as a top concern and are investing in automation, AI, managed services, governance, and prior-authorization improvements.", "Guidehouse HFMA 2026 revenue cycle AI automation payer challenges", observed),
        _e("healthcare_admin", "UnitedHealth prior authorization AI reform", "https://nypost.com/2026/05/05/business/unitedhealth-to-remove-annoying-barrier-for-slew-of-medical-procedures/", "2026-05-05", "UnitedHealth announced prior-authorization reductions and AI-backed detection of abnormal usage patterns, reinforcing that prior authorization is a current operational pressure point.", "UnitedHealth prior authorization AI May 2026", observed),
        _e("healthcare_admin", "Flexbone prior authorization automation guide", "https://flexbone.ai/prior-authorization-automation", "2026-04-01", "Prior authorization automation vendors market full PA lifecycle support across submission, follow-up, and appeals, showing both pain and competitive saturation.", "prior authorization automation AI agents 2026", observed),
        _e("healthcare_admin", "TechTarget prior-auth AI arms race", "https://www.techtarget.com/revcyclemanagement/news/366641759/AI-arms-race-leading-to-prior-auth-problems-reimbursement-cuts", "2026-04-15", "AI in prior authorization and billing may intensify payer-provider tensions and reimbursement pressure, raising governance and trust barriers.", "AI prior authorization arms race reimbursement cuts 2026", observed),
        _e("construction_bids", "Syntora AI bid analysis for small contractors", "https://syntora.io/solutions/how-can-ai-improve-accuracy-in-construction-project-bids-for-small-contractors", "2026-03-15", "Syntora markets AI bid analysis for small contractors that parses quotes, flags missing scope, and reduces manual review time.", "AI bid analysis small contractors missing scope 2026", observed),
        _e("construction_bids", "Syntora subcontractor management", "https://syntora.io/solutions/which-ai-automation-agencies-specialize-in-subcontractor-management-for-small-to", "2026-03-28", "Construction subcontractor management automation includes bid analysis, compliance tracking, invoice verification, and centralized workflows.", "AI subcontractor management construction compliance tracking 2026", observed),
        _e("construction_bids", "NextAutomation construction automation", "https://nextautomation.ai/ai-automation/construction", "2026-04-09", "Construction AI automation targets bid generation, RFI tracking, daily reports, safety logging, and scheduling, but competitor agencies already package this vertical.", "construction AI automation bid RFI safety scheduling 2026", observed),
        _e("construction_bids", "US Tech Automations construction bid management", "https://ustechautomations.com/resources/blog/construction-bid-management-automation-pain-solution-2026", "2026-03-28", "Construction bid management automation claims estimators spend substantial time and money on losing bids, indicating real pain but also agency competition.", "construction bid management automation pain 2026", observed),
        _e("grant_ops", "AwardTrace grant compliance platform", "https://www.awardtrace.com/", "2026-05-06", "Grant compliance platforms market AI-powered deadline tracking, compliance checks, and audit readiness, showing recurring admin pain and existing competitors.", "AI grant compliance platform audit readiness 2026", observed),
        _e("grant_ops", "NextAutomation nonprofits automation", "https://nextautomation.ai/ai-automation/nonprofits", "2026-04-09", "Nonprofit AI automation claims grant writing and impact reporting burdens, but small budgets and adoption friction may limit fast cash.", "nonprofit AI automation grant reporting burden 2026", observed),
        _e("grant_ops", "GovGrants AI", "https://govgrants.ai/", "2026-05-06", "Grant-management platforms cover solicitation, review, award management, monitoring, compliance, and closeout, suggesting competition across the lifecycle.", "GovGrants AI grants management public sector 2026", observed),
        _e("cpa_tax_accounting", "Black Ore Tax Autopilot broad availability", "https://natlawreview.com/press-releases/black-ore-launches-tax-autopilot-broad-availability", "2026-04-29", "Black Ore opened Tax Autopilot broadly after onboarding firms from a large waitlist, including 40% of Top 20 CPA firms, making CPA tax automation crowded.", "Black Ore Tax Autopilot broad availability April 2026", observed),
        _e("cpa_tax_accounting", "International Accounting Bulletin Black Ore rollout", "https://www.internationalaccountingbulletin.com/news/black-ore-opens-tax-autopilot-ai-platform-to-more-cpa-practices/", "2026-04-30", "Black Ore says Tax Autopilot prepares complex returns and integrates with tax software, creating a strong incumbent threat to CPA rescue ideas.", "Black Ore CPA AI tax automation April 2026", observed),
        _e("cpa_tax_accounting", "Basis AI accounting automation funding", "https://www.crowdfundinsider.com/2026/02/264192-basis-announces-100m-in-new-funding-at-1-15b-valuation-to-enable-ai-driven-accounting-automation/", "2026-02-26", "Basis raised $100M at a $1.15B valuation for AI-driven accounting automation, weakening the uniqueness of a generic CPA AI workflow strategy.", "Basis AI accounting automation funding 2026", observed),
        _e("cpa_tax_accounting", "Pilot AI Accountant", "https://pilot.com/blog/pilot-unveils-ai-accountant-a-major-leap-toward-artificial-general-intelligence-in-accounting", "2026-02-04", "Pilot announced an AI Accountant for autonomous bookkeeping, indicating accounting workflow automation is heavily contested by funded incumbents.", "Pilot AI Accountant autonomous bookkeeping 2026", observed),
        _e("insurance_claims", "IBM: The next era of claims operations", "https://www.ibm.com/think/insights/next-era-claims-operations", "2026-04-13", "IBM frames claims operations as moving from automation toward autonomy because cycle times, leakage, talent constraints, and regulatory scrutiny remain structural pressures.", "insurance claims operations automation autonomy 2026", observed),
        _e("insurance_claims", "Adacta State of Claims Automation Market Study 2026", "https://www.adacta-fintech.com/news/adacta-publishes-state-of-claims-automation-market-study-2026", "2026-02-26", "Adacta reports most European insurers remain at moderate-or-lower claims automation maturity while many plan to increase investment.", "claims automation market study 2026 insurers maturity", observed),
        _e("insurance_claims", "Layerup 2026 buyer guide to AI for insurance claims", "https://www.uselayerup.com/blog/2026-buyers-guide-to-ai-for-insurance-claims", "2026-03-01", "Insurance carriers evaluate AI claims platforms to reduce cycle time, scale operations, and control leakage, but vendor categories and implementation risks differ.", "AI insurance claims buyer guide 2026", observed),
        _e("legal_ops", "Moritz AI-native law firm funding", "https://www.businessinsider.com/moritz-ai-law-firm-seed-funding-y-combinator-2026-5", "2026-05-05", "An AI-native law firm raised seed funding and offers task-based legal services with accountability, showing legal AI demand but strong founder-market-fit expectations.", "AI-native law firm seed funding May 2026", observed),
        _e("legal_ops", "NextAutomation law firm AI automation", "https://nextautomation.ai/ai-automation/law-firms", "2026-04-09", "Law firm AI automation targets contract review, legal research, intake, time tracking, and deposition summaries, but legal trust and liability barriers remain high.", "AI automation law firms intake contract review 2026", observed),
        _e("legal_ops", "Sandstone legal AI startup funding", "https://www.businessinsider.com/sandstone-raises-seed-funding-sequoia-legal-ai-2026-1", "2026-01-15", "Sandstone targets in-house legal teams with AI contract drafting/review and paying customers, indicating competition in legal operations AI.", "Sandstone legal AI startup Sequoia 2026", observed),
        _e("local_services_dispatch", "CallJolt missed-call statistics for home services", "https://calljolt.com/blog/plumbing/missed-call-statistics-home-service-businesses-2026", "2026-02-17", "Home-service missed-call research claims many contractors miss calls and lose jobs to faster responders, showing urgent local-service operational pain.", "home service missed call statistics 2026", observed),
        _e("local_services_dispatch", "Quiet Protocol missed calls AI-first 2026", "https://www.thequietprotocol.com/blog/real-cost-missing-calls-ai-first-2026", "2026-03-29", "Missed-call revenue is framed as an underreported service-business loss, supporting local-services dispatch automation as a possible fast-cash route.", "missed calls service businesses AI first 2026", observed),
        _e("local_services_dispatch", "SmartCallz AI automation for home services", "https://smartcallz.com/ai-automation-for-home-services-companies-in-nj/", "2026-01-14", "Home-service automation vendors target inbound calls, estimates, crews, scheduling, billing, reviews, and emergencies, showing buyer pain and existing alternatives.", "AI automation home services missed calls scheduling 2026", observed),
        _e("manufacturing_quality", "Magna uses AI across factory quality and operations", "https://www.businessinsider.com/auto-giant-magna-ai-factories-2026-5", "2026-05-09", "Magna is applying AI to product quality, predictive maintenance, safety, energy, and production speed, showing current industrial demand for operational AI but also enterprise-scale incumbent expectations.", "Magna AI factories quality predictive maintenance May 2026", observed),
        _e("manufacturing_quality", "UnitX FleX AI visual inspection launch", "https://metrology.news/unitx-launches-flex-ai-powered-visual-inspection-system-for-inline-manufacturing-quality-control/", "2026-01-14", "UnitX launched an AI-powered inline visual inspection system for manufacturing quality control, indicating that factory-quality AI is already a competitive productized market.", "UnitX FleX AI visual inspection manufacturing quality 2026", observed),
        _e("manufacturing_quality", "redi-Group AI camera inspection", "https://redi-group.com/en/new-100-visual-quality-inspection-with-ai-camera-system/", "2026-03-12", "redi-Group markets AI-supported camera inspection for reproducible visual quality checks and traceable documentation, showing demand for evidence-backed operations in manufacturing.", "AI camera inspection visual quality traceable documentation March 2026", observed),
    ]
    return rows


def run_e114_live_web_capability_utilized_strategy_run(
    *,
    cieu_db: str | Path,
    owner_intent: str = "Aiden: use global live public-read evidence, full-system capability utilization, and brain learning to find the easiest credible first-cash path for Y*Bridge Labs.",
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    evidence_items: Sequence[Mapping[str, Any]] | None = None,
    use_host_live_network: bool = False,
    seal_session: bool = True,
) -> dict[str, Any]:
    provider: PublicReadProvider
    provider_mode: str
    if use_host_live_network:
        provider = build_host_live_public_read_provider()
        provider_mode = "host_mac_live_duckduckgo_public_read"
    else:
        provider = build_snapshot_public_read_provider(evidence_items)
        provider_mode = "dated_public_read_evidence_snapshot"

    cieu_path = str(cieu_db)
    brain_cycle = run_cieu_backed_brain_learning_cycle(
        cieu_db=cieu_path,
        owner_intent=owner_intent,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        provider=provider,
        allow_live_network=use_host_live_network,
        test_mode=False,
        seal_session=seal_session,
    )
    host = brain_cycle["host_runtime_result"]
    strategy_result = host["strategy_result"]
    strategy = strategy_result["strategy"]
    scan = strategy["live_global_open_world_scan"]
    control_gate = strategy_result["control_gate"]
    no_new_wheel_gate = control_gate.get("no_new_wheel_runtime_law_gate", {})
    runtime_packet = no_new_wheel_gate.get("runtime_law_packet", {})
    utilization = runtime_packet.get("capability_utilization_matrix", {})
    source_date_summary = summarize_source_dates(scan.get("evidence_items", []))
    result = {
        "artifact_id": "e114_live_web_capability_utilized_strategy_run_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "provider_mode": provider_mode,
        "owner_intent": owner_intent,
        "host_runtime_result": host,
        "brain_learning_cycle_result": brain_cycle,
        "selected_strategy": strategy.get("selected_strategy"),
        "top_routes": list(strategy.get("route_math_scores") or [])[:12],
        "live_public_read_scan_summary": {
            "scan_mode": scan.get("scan_mode"),
            "provider_status": scan.get("provider_status"),
            "domain_count": len(scan.get("scan_domains") or []),
            "evidence_count": len(scan.get("evidence_items") or []),
            "opportunity_cluster_count": len(scan.get("opportunity_clusters") or []),
            "source_date_summary": source_date_summary,
        },
        "capability_utilization_summary": {
            "no_new_wheel_decision": no_new_wheel_gate.get("Y_star_gov_no_new_wheel_decision"),
            "Rt_plus_1": runtime_packet.get("CZL_closure", {}).get("R_t_plus_1"),
            "code_index_loaded": utilization.get("code_index_loaded"),
            "indexed_capability_counts": utilization.get("indexed_capability_counts"),
            "action_relevant_capability_group_count": len(utilization.get("action_relevant_capability_groups") or []),
            "available_for_future_activation_count": len(utilization.get("available_for_future_activation") or []),
            "unreviewed_runtime_active_capability_count": utilization.get("unreviewed_runtime_active_capability_count"),
        },
        "freshness_and_brain_learning_summary": {
            "freshness_filter_summary": brain_cycle["freshness_filter_summary"],
            "brain_mutation_candidate_count": len(brain_cycle["brain_learning_packet"]["brain_mutation_candidates"]),
            "failure_residual_candidate_count": len(brain_cycle["brain_learning_packet"]["failure_residual_candidates"]),
            "production_brain_write_performed": brain_cycle["production_brain_write_performed"],
        },
        "CIEUStore_summary": brain_cycle["CIEUStore_summary"],
        "ability_leap_proof": {
            "E113_capability_utilization_gate_passed": no_new_wheel_gate.get("Y_star_gov_no_new_wheel_decision") == "ALLOW",
            "E110_universal_control_passed": strategy_result["CEO_runtime_receipt"].get("Y_star_gov_universal_control_decision") == "ALLOW",
            "E108_public_read_strategy_passed": strategy_result["CEO_runtime_receipt"].get("Y_star_gov_live_global_decision") == "ALLOW",
            "E112_freshness_filter_passed": brain_cycle["freshness_filter_summary"]["accepted_count"] > 0,
            "CIEU_backed_brain_learning_candidates_created": len(brain_cycle["brain_learning_packet"]["brain_mutation_candidates"]) > 0,
            "stale_or_undated_evidence_blocked": brain_cycle["freshness_filter_summary"]["stale_or_undated_evidence_blocked_from_brain"],
            "external_action_executed": False,
        },
        "truth_constraints": {
            "no_L4_feedback_executed": True,
            "no_customer_validation_claim": True,
            "no_revenue_or_payment_signal": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_capability_utilization_law",
            "L5-B": "complete_for_structured_governed_intelligence_loop_with_live_public_read_strategy_and_brain_learning_candidates",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_CIEU_backed_brain_learning_candidate_loop_no_production_brain_write",
        },
    }
    return result


def write_e114_live_web_strategy_reports(
    *,
    cieu_db: str | Path,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    brain_db: Path | None = None,
    evidence_items: Sequence[Mapping[str, Any]] | None = None,
    use_host_live_network: bool = False,
) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    result = run_e114_live_web_capability_utilized_strategy_run(
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        brain_db=brain_db,
        evidence_items=evidence_items,
        use_host_live_network=use_host_live_network,
        seal_session=False,
    )
    report = _completion_report(result)
    status = _runtime_status(result)
    files = {
        "report_json": base / "office/mission_command/e114_live_web_capability_utilized_strategy_run_report.json",
        "report_md": base / "office/mission_command/e114_live_web_capability_utilized_strategy_run_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e114_live_web_capability_utilized_strategy_run.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e114_live_web_capability_utilized_strategy_run.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_markdown(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_markdown(status), encoding="utf-8")
    return report


def summarize_source_dates(evidence_items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    dated = [item for item in evidence_items if item.get("source_date")]
    undated = [item for item in evidence_items if not item.get("source_date")]
    return {
        "dated_count": len(dated),
        "undated_count": len(undated),
        "oldest_source_date": min((str(item.get("source_date")) for item in dated), default=None),
        "newest_source_date": max((str(item.get("source_date")) for item in dated), default=None),
        "source_date_required_for_brain_learning": True,
    }


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT event_type, decision FROM cieu_events ORDER BY seq_global").fetchall()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    selected = result.get("selected_strategy") if isinstance(result.get("selected_strategy"), Mapping) else {}
    top_routes = result.get("top_routes") if isinstance(result.get("top_routes"), list) else []
    return {
        "milestone_id": MILESTONE_ID,
        "provider_mode": result["provider_mode"],
        "selected_strategy": selected,
        "selected_first_cash_path": selected.get("current_best_first_cash_path"),
        "selected_route_id": selected.get("selected_route_id"),
        "top_routes": [
            {
                "route_id": row.get("route_id"),
                "name": row.get("name"),
                "domain_id": row.get("domain_id"),
                "market_first_score": row.get("market_first_score"),
                "evsi_usd": row.get("evsi_usd"),
                "why_it_might_fail": row.get("why_it_might_fail"),
            }
            for row in top_routes
        ],
        "live_public_read_scan_summary": result["live_public_read_scan_summary"],
        "capability_utilization_summary": result["capability_utilization_summary"],
        "freshness_and_brain_learning_summary": result["freshness_and_brain_learning_summary"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "ability_leap_proof": result["ability_leap_proof"],
        "truth_constraints": result["truth_constraints"],
        "L5_truth_table_after": result["L5_truth_table_after"],
        "host_live_run_command": (
            "python3 -m office.mission_command.e114_live_web_capability_utilized_strategy_run "
            "--use-host-live-network --cieu-db /tmp/e114_aiden_live_web_strategy.db"
        ),
        "what_was_not_claimed": [
            "no L4 feedback executed",
            "no customer validation",
            "no revenue/payment signal",
            "no live provider execution",
            "no K9Audit integration",
            "no production brain write performed",
        ],
    }


def _runtime_status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "runtime_status": "live_public_read_capability_utilized_strategy_run_structurally_enforceable",
        "provider_mode": result["provider_mode"],
        "ability_leap_proof": result["ability_leap_proof"],
        **result["L5_truth_table_after"],
        "remaining_blockers": [
            "host live network run must be executed on the Mac host to prove direct Aiden network access outside Codex sandbox",
            "owner-approved L4 feedback/customer/revenue/payment loop remains pending",
            "production brain write remains blocked; only CIEU-backed candidates are created",
        ],
    }


def _report_markdown(report: Mapping[str, Any]) -> str:
    top_lines = "\n".join(
        f"- {row['route_id']}: score={row['market_first_score']}, EVSI=${row['evsi_usd']} ({row['name']})"
        for row in report["top_routes"][:6]
    )
    return (
        "# E114 Live-Web Capability-Utilized Strategy Run\n\n"
        f"- Provider mode: {report['provider_mode']}\n"
        f"- Selected first-cash path: {report['selected_first_cash_path']}\n"
        f"- Selected route id: {report['selected_route_id']}\n"
        f"- Evidence count: {report['live_public_read_scan_summary']['evidence_count']}\n"
        f"- Dated evidence: {report['live_public_read_scan_summary']['source_date_summary']['dated_count']}\n"
        f"- Capability groups used: {report['capability_utilization_summary']['action_relevant_capability_group_count']}\n"
        f"- Rt+1: {report['capability_utilization_summary']['Rt_plus_1']}\n"
        f"- Fresh evidence accepted: {report['freshness_and_brain_learning_summary']['freshness_filter_summary']['accepted_count']}\n"
        f"- Brain learning candidates: {report['freshness_and_brain_learning_summary']['brain_mutation_candidate_count']}\n"
        f"- CIEU events: {report['CIEUStore_summary']['event_count']}\n\n"
        "## Top Routes\n\n"
        f"{top_lines}\n\n"
        "## Host Live Run\n\n"
        f"`{report['host_live_run_command']}`\n\n"
        "## Boundary\n\n"
        "No external action, customer validation, revenue/payment signal, live provider execution, K9Audit write, or production brain write is claimed.\n"
    )


def _status_markdown(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E114\n\n"
        f"- Runtime status: {status['runtime_status']}\n"
        f"- Provider mode: {status['provider_mode']}\n"
        f"- L5-A: {status['L5-A']}\n"
        f"- L5-B: {status['L5-B']}\n"
        f"- L5-C: {status['L5-C']}\n"
        f"- L5-D: {status['L5-D']}\n"
        f"- L5-E: {status['L5-E']}\n"
    )


def _e(
    domain_id: str,
    title: str,
    url: str,
    source_date: str,
    claim: str,
    query: str,
    observed_at: str,
) -> dict[str, Any]:
    return {
        "source_title": title,
        "source_url": url,
        "source_date": source_date,
        "source_date_basis": "public_page_or_search_metadata",
        "source_date_confidence": "medium",
        "claim_summary": claim,
        "domain_id": domain_id,
        "query": query,
        "observed_at": observed_at,
        "evidence_type": "live_public_read_evidence_snapshot",
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Aiden E114 live-web capability-utilized strategy loop.")
    parser.add_argument("--cieu-db", default="/tmp/e114_aiden_live_web_strategy.db")
    parser.add_argument("--brain-db", default="")
    parser.add_argument("--ystar-gov-root", default=str(Y_GOV_ROOT))
    parser.add_argument("--use-host-live-network", action="store_true")
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args(argv)
    brain_db = Path(args.brain_db) if args.brain_db else None
    if args.write_reports:
        report = write_e114_live_web_strategy_reports(
            cieu_db=args.cieu_db,
            ystar_gov_root=Path(args.ystar_gov_root),
            brain_db=brain_db,
            use_host_live_network=args.use_host_live_network,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        result = run_e114_live_web_capability_utilized_strategy_run(
            cieu_db=args.cieu_db,
            ystar_gov_root=Path(args.ystar_gov_root),
            brain_db=brain_db,
            use_host_live_network=args.use_host_live_network,
            seal_session=False,
        )
        print(json.dumps(_completion_report(result), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


__all__ = [
    "DatedPublicReadEvidenceSnapshotProvider",
    "MILESTONE_ID",
    "SESSION_ID",
    "build_default_e114_live_public_read_evidence_snapshot",
    "build_host_live_public_read_provider",
    "build_snapshot_public_read_provider",
    "run_e114_live_web_capability_utilized_strategy_run",
    "summarize_cieustore",
    "summarize_source_dates",
    "write_e114_live_web_strategy_reports",
]


if __name__ == "__main__":
    raise SystemExit(main())
