#!/usr/bin/env python3
"""Build L7.2 Money Path Intelligence Engine artifacts.

This builder is deterministic and offline-testable. It uses existing L6/L7
artifacts as the evidence base and does not ask for URLs, run outreach, submit
forms, publish, pay, create accounts, or perform core writeback.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L7.2"
MILESTONE_NAME = "Meta-Development Money Path Intelligence Engine with Shortest Cash Realization Path"
RUN_ID = "l7_2_money_path_engine_run_001"
GENERATED_AT = "2026-04-29T00:00:00Z"

POLICY_REFS = {
    "policy_ref": "policy/action_capability_registry.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "secret_scanning_policy_ref": "policy/secret_scanning_policy.json",
}

WEIGHTS = {
    "speed_to_first_cash": 0.20,
    "existing_capability_fit": 0.15,
    "low_trust_barrier": 0.15,
    "clear_buyer": 0.10,
    "clear_pain": 0.10,
    "minimal_new_tooling": 0.10,
    "low_owner_burden": 0.10,
    "repeatability_after_first_sale": 0.05,
    "strategic_compounding_value": 0.05,
}

NO_ACTION_FLAGS = [
    "outreach",
    "email_sent",
    "form_submission",
    "publication",
    "payment",
    "account_creation",
    "customer_contact",
    "grant_rfp_submission",
    "mcp_live_behavior",
    "actual_memory_brain_canonical_cieu_db_writeback",
    "secret_printed_stored_in_repo",
    "y_star_gov_modification",
    "gov_mcp_modification",
    "db_log_wal_shm_active_agent_marker_content_read",
    "ask_user_url",
]


def write_json(path: str, payload: Any) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: str, payload: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")


def load_json(path: str, default: Any) -> Any:
    target = ROOT / path
    if not target.exists():
        return default
    return json.loads(target.read_text(encoding="utf-8"))


def packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "run_id": RUN_ID,
        "packet_type": packet_type,
        "generated_at_utc": GENERATED_AT,
        **POLICY_REFS,
    }


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep] + body)


def simple_md(title: str, sections: list[tuple[str, str]]) -> str:
    chunks = [f"# {title}"]
    for heading, body in sections:
        chunks.append(f"\n## {heading}\n\n{body}")
    return "\n".join(chunks) + "\n"


def artifact_ref(path: str) -> str:
    return path if (ROOT / path).exists() else f"{path} (missing)"


def real_observation_status() -> dict[str, Any]:
    configured = (
        os.environ.get("YSTAR_CONTROLLED_SEARCH_BACKEND") in {"tavily_search_api", "brave_search_api", "serpapi"}
        and os.environ.get("YSTAR_CONTROLLED_PAGE_READ_BACKEND") == "stdlib_public_http"
        and os.environ.get("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK") == "1"
        and os.environ.get("YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK") == "1"
    )
    return {
        "real_external_observation_used": False,
        "real_external_observation_config_detected": configured,
        "limitation": "L7.2 used existing L6/L7 artifacts as evidence; no live external read was required for deterministic money-path reasoning.",
        "secret_values_serialized": False,
    }


def build_external_opportunities() -> list[dict[str, Any]]:
    categories = [
        ("opp_ai_agent_governance", "AI agent governance", "AI teams adopting autonomous agents", "Agents can act faster than governance systems can review.", "medium_high", "high", "medium"),
        ("opp_coding_agent_governance", "AI coding-agent governance", "engineering leaders using Codex/Claude Code/OpenClaw", "Need safe coding-agent autonomy, traceable changes, and approval gates.", "high", "high", "medium"),
        ("opp_audit_evidence_compliance", "AI audit/evidence/compliance tooling", "regulated startups and compliance teams", "Need proof packets and reviewable evidence trails.", "medium", "medium_high", "medium"),
        ("opp_enterprise_observability", "enterprise AI safety/observability", "enterprise AI platform teams", "Need observability and no-action receipts for agent behavior.", "high", "medium", "high"),
        ("opp_governed_workflow_consulting", "governed AI workflow consulting", "founders and SMB operators", "Need someone to set up safe AI workflows quickly.", "medium", "high", "low"),
        ("opp_company_runtime_setup", "AI company runtime setup service", "solo founders building agent teams", "Need an owner cockpit, lanes, and approval workflow without becoming engineers.", "medium_high", "high", "low"),
        ("opp_agent_team_orchestration", "agent-team orchestration", "small technical teams", "Need role separation, handoffs, and lane runners.", "medium", "medium_high", "medium"),
        ("opp_evidence_packet_generation", "compliance evidence packet generation", "AI governance consultants and internal audit teams", "Need repeatable evidence packets with claim boundaries.", "medium", "medium_high", "medium"),
        ("opp_devtool_openclaw_codex", "developer tooling around OpenClaw/Codex/Claude Code workflows", "AI-native developers", "Need scripts, policies, and fixtures that reduce manual coordination.", "medium", "medium", "medium"),
        ("opp_regulated_audit_trails", "regulated workflow audit trails", "health, finance, legal-adjacent operators", "Need audit trails before AI action is trusted.", "high", "medium", "high"),
        ("opp_grant_rfp_support", "grant/funding/RFP tracking and proposal support", "AI governance builders seeking non-dilutive funding", "Need read-only tracking and proposal drafts.", "medium", "medium", "medium"),
        ("opp_cross_border_bridge", "cross-border AI/business bridge opportunities", "Chinese-English founders and US-facing AI teams", "Need bilingual business bridge and agentic execution translation.", "medium_high", "medium_high", "medium"),
        ("opp_startup_ai_governance", "AI governance for small companies/startups", "startups without governance staff", "Need lightweight, credible safety and evidence systems.", "medium", "high", "low"),
        ("opp_internal_automation_service", "internal automation product/service opportunities", "owner-led companies with repeated admin/research work", "Need done-for-you automation before buying a platform.", "medium", "high", "low"),
        ("opp_fast_paid_validation", "fast paid validation opportunities", "founders with urgent research/strategy decisions", "Need a concrete deliverable in days, not a full product.", "high", "high", "low"),
        ("opp_done_for_you_setup", "founder/SMB done-for-you AI workflow setup", "busy owners with low tolerance for tooling complexity", "Need setup, not education.", "high", "high", "low"),
    ]
    evidence = [
        artifact_ref("ceo_command_brief/l6_16_ceo_command_brief.json"),
        artifact_ref("l7_parallel_commercial_autonomy_sprint/l7_1_summary.json"),
        artifact_ref("l7_revenue_opportunity_radar_l7_1/real_read_only_revenue_scan_report.json"),
    ]
    rows = []
    for idx, (cid, desc, segment, pain, competition, wtp, trust) in enumerate(categories, start=1):
        rows.append(
            {
                "category_id": cid,
                "opportunity_description": desc,
                "customer_or_funder_segment": segment,
                "pain_point": pain,
                "evidence_basis": evidence,
                "source_quality": "existing_internal_real_observation_and_strategy_artifacts",
                "competition_intensity": competition,
                "urgency": "high" if idx in {2, 5, 6, 15, 16} else "medium",
                "willingness_to_pay_signal": wtp,
                "trust_barrier": trust,
                "time_to_cash_estimate": "7-30 days" if trust == "low" or cid == "opp_fast_paid_validation" else "30-90 days",
                "uncertainty_level": "medium",
                "next_observation_needed": "read-only buyer pain/source scan and human-reviewed customer discovery script",
            }
        )
    return rows


def build_internal_assets() -> list[dict[str, Any]]:
    specs = [
        ("asset_y_star_cieu", "Y* / CIEU conceptual foundation", "medium", "differentiated governance language and state model", "needs clearer buyer-facing packaging"),
        ("asset_deterministic_governance", "deterministic governance thinking", "high", "trustable boundaries and repeatable tests", "must translate into simple commercial promises"),
        ("asset_y_star_gov_boundary", "Y-star-gov boundary", "medium", "separates company runtime from governance runtime", "external buyers need simpler framing"),
        ("asset_ystar_company_runtime", "ystar-company runtime host", "high", "proves internal agent-company operations", "still owner-machine local"),
        ("asset_real_web_observation", "real controlled web observation", "high", "can gather public evidence under budget", "needs richer extraction and fewer provider failures"),
        ("asset_evidence_pipeline", "evidence packet pipeline", "high", "turns observations into reviewable packets", "needs buyer-facing templates"),
        ("asset_conflict_matrix", "conflict/corroboration matrix", "medium_high", "bounds uncertainty instead of overclaiming", "can feel heavy unless packaged"),
        ("asset_human_review_packet", "human review packet", "high", "clear approval boundary", "needs UI/workflow polish"),
        ("asset_ceo_command_brief", "CEO command brief", "high", "owner-facing decision output", "needs recurring command mode"),
        ("asset_agent_team_runtime", "agent team runtime", "medium_high", "role separation and orchestration", "needs result feedback loop"),
        ("asset_revenue_radar", "revenue radar", "medium", "first opportunity discovery lane", "needs real repeatable market scanning"),
        ("asset_approval_workflow", "human approval workflow", "medium_high", "safe path toward external action", "needs execution receipts after approval"),
        ("asset_writeback_dry_run", "review-gated writeback dry-run", "medium", "learning without unsafe permanence", "needs approval UI"),
        ("asset_owner_cockpit", "owner cockpit", "medium_high", "reduces owner cognitive burden", "needs one-command habit loop"),
        ("asset_policy_registry", "policy registry / staged action policy", "high", "lets discovery and drafting proceed while blocking unsafe execution", "needs broader migration"),
        ("asset_secret_context_policy", "secret scanner contextual policy", "high", "prevents secret leakage without test false positives", "needs integration into all safety checks"),
        ("asset_parallel_orchestrator", "parallel lane orchestrator", "medium_high", "reduces need for multiple manual Codex windows", "needs richer dependency graph"),
        ("asset_tests_validation", "tests/validation maturity", "high", "commercial trust and regression safety", "needs faster validation dashboards"),
        ("asset_codex_implementation_arm", "Codex as implementation arm", "high", "fast tool building and artifact generation", "requires scoped tasks and review"),
        ("asset_owner_mu_speaker", "owner μSpeaker role and system-design narrative", "medium_high", "unique founder narrative around self-governed AI company", "needs buyer-safe storytelling"),
        ("asset_cross_language", "cross-language/cross-cultural advantage", "medium_high", "bridges Chinese/English AI/business contexts", "needs polished bilingual materials"),
        ("asset_constraints", "constraints: limited owner time, English friction, automation need, revenue need", "high", "forces service-before-product and low-burden design", "requires owner burden minimization"),
    ]
    rows = []
    for aid, desc, maturity, relevance, limitation in specs:
        rows.append(
            {
                "asset_id": aid,
                "description": desc,
                "maturity": maturity,
                "evidence_artifact_or_commit": artifact_ref("l7_parallel_commercial_autonomy_sprint/l7_1_summary.json"),
                "commercial_relevance": relevance,
                "differentiation_value": "high" if "governance" in desc.lower() or "evidence" in desc.lower() or "codex" in desc.lower() else "medium",
                "trust_value": "high" if maturity in {"high", "medium_high"} else "medium",
                "current_limitations": limitation,
                "upgrade_needed": "package into buyer-facing deliverable and automate repeatable sprint route",
            }
        )
    return rows


def opportunity_asset_matches(opportunities: list[dict[str, Any]], assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    asset_ids = [asset["asset_id"] for asset in assets]
    selected = {
        "opp_fast_paid_validation": ["asset_ceo_command_brief", "asset_evidence_pipeline", "asset_codex_implementation_arm", "asset_owner_cockpit"],
        "opp_governed_workflow_consulting": ["asset_real_web_observation", "asset_policy_registry", "asset_approval_workflow", "asset_owner_cockpit"],
        "opp_company_runtime_setup": ["asset_agent_team_runtime", "asset_parallel_orchestrator", "asset_owner_cockpit", "asset_tests_validation"],
        "opp_coding_agent_governance": ["asset_deterministic_governance", "asset_secret_context_policy", "asset_policy_registry", "asset_tests_validation"],
        "opp_cross_border_bridge": ["asset_cross_language", "asset_owner_mu_speaker", "asset_ceo_command_brief", "asset_codex_implementation_arm"],
    }
    rows = []
    for idx, opp in enumerate(opportunities, start=1):
        ids = selected.get(opp["category_id"], asset_ids[(idx % 8) : (idx % 8) + 4] or asset_ids[:4])
        cash = "high" if opp["trust_barrier"] == "low" or "fast" in opp["category_id"] else "medium"
        rows.append(
            {
                "opportunity_id": opp["category_id"],
                "asset_ids_used": ids,
                "fit_score": 5 if cash == "high" else 4,
                "why_fit_exists": "Current system already combines controlled observation, evidence trace, command briefs, staged policy, and Codex implementation.",
                "unique_advantage": "Governed agent-company runtime with proof artifacts and approval gates, not just a generic research bot.",
                "weakness": "Trust and market validation remain early; packaging is not yet proven.",
                "trust_gap": opp["trust_barrier"],
                "evidence_gap": "Needs direct buyer interviews or approved outreach after internal review.",
                "capability_gap": "Needs repeatable service delivery workflow and approval execution receipts.",
                "commercial_potential": opp["willingness_to_pay_signal"],
                "cash_realization_potential": cash,
                "recommended_path_candidate": f"path_candidate_from_{opp['category_id']}",
            }
        )
    return rows


def path(
    path_id: str,
    name: str,
    segment: str,
    problem: str,
    offer: str,
    assets: list[str],
    opportunity: str,
    first_revenue: str,
    time: str,
    trust: int,
    complexity: int,
    scale: int,
    evidence: int,
    missing: list[str],
    required_external: list[str],
    why_win: str,
    why_fail: str,
    scores: dict[str, int],
    first_price: str,
    buyer: str,
) -> dict[str, Any]:
    cash_score = round(sum(scores[key] * WEIGHTS[key] for key in WEIGHTS), 2)
    return {
        "path_id": path_id,
        "path_name": name,
        "customer_segment": segment,
        "problem_solved": problem,
        "proposed_offer_or_product": offer,
        "internal_assets_used": assets,
        "external_opportunity_basis": opportunity,
        "first_revenue_mechanism": first_revenue,
        "time_to_first_revenue": time,
        "trust_barrier": trust,
        "delivery_complexity": complexity,
        "scalability": scale,
        "evidence_strength": evidence,
        "missing_capabilities": missing,
        "required_external_actions": required_external,
        "approval_required": bool(required_external),
        "why_this_path_might_win": why_win,
        "why_this_path_might_fail": why_fail,
        "cash_realization_path_length": scores["speed_to_first_cash"],
        "shortest_cash_step": "sell a scoped internal-only service deliverable before building a full product",
        "minimum_new_capabilities_required": missing[:2],
        "human_effort_required": "low_to_medium",
        "trust_barrier_to_first_payment": trust,
        "delivery_time_to_first_paid_result": time,
        "approval_steps_before_cash": len(required_external),
        "external_action_steps_before_cash": len(required_external),
        "first_cash_signal": "paid pilot, paid validation, signed intent, or paid internal strategy sprint",
        "first_possible_paid_offer": offer,
        "first_possible_buyer": buyer,
        "first_possible_price_range": first_price,
        "fastest_validation_method": "owner-reviewed offer one-pager plus approved customer discovery or warm intro",
        "can_generate_cash_before_full_product": True,
        "can_start_as_service": True,
        "can_start_with_existing_tools": len(missing) <= 3,
        "cash_path_blockers": missing,
        "cash_path_score": cash_score,
        "score_inputs": scores,
    }


def commercial_paths() -> list[dict[str, Any]]:
    base_scores_fast = {
        "speed_to_first_cash": 5,
        "existing_capability_fit": 5,
        "low_trust_barrier": 4,
        "clear_buyer": 4,
        "clear_pain": 5,
        "minimal_new_tooling": 5,
        "low_owner_burden": 4,
        "repeatability_after_first_sale": 3,
        "strategic_compounding_value": 4,
    }
    return [
        path("path_001", "Founder AI workflow audit and CEO command brief sprint", "AI startup founders", "Need fast evidence-backed decision help without risky external action.", "Done-for-you governed observation + internal CEO command brief", ["asset_real_web_observation", "asset_evidence_pipeline", "asset_ceo_command_brief"], "opp_fast_paid_validation", "scoped paid internal research sprint", "7-14 days", 4, 2, 3, 4, ["approval-ready outreach draft generator"], ["approved outreach or warm intro"], "Uses current system almost immediately.", "Buyer trust must be earned without case studies.", base_scores_fast, "$500-$1500", "AI startup founder with urgent strategy/research decision"),
        path("path_002", "Owner cockpit setup for AI-agent companies", "solo founders and owner-operators", "Need one place to see agents, blocks, approvals, and money path.", "Private owner cockpit setup and weekly command brief", ["asset_owner_cockpit", "asset_parallel_orchestrator", "asset_approval_workflow"], "opp_company_runtime_setup", "setup service", "14-30 days", 4, 3, 4, 4, ["cockpit template pack", "onboarding checklist"], ["approved outreach"], "Clear pain for busy owners.", "May look like custom ops consulting until productized.", {"speed_to_first_cash": 4, "existing_capability_fit": 5, "low_trust_barrier": 4, "clear_buyer": 4, "clear_pain": 4, "minimal_new_tooling": 4, "low_owner_burden": 4, "repeatability_after_first_sale": 4, "strategic_compounding_value": 5}, "$750-$2500", "owner-operator already using Codex/Claude/OpenClaw"),
        path("path_003", "Coding-agent governance audit", "engineering teams using coding agents", "Need proof that agents will not leak secrets or perform unsafe actions.", "Policy/test audit with contextual secret scanner and staged action policy report", ["asset_secret_context_policy", "asset_policy_registry", "asset_tests_validation"], "opp_coding_agent_governance", "paid audit report", "14-30 days", 3, 3, 4, 4, ["audit intake checklist", "sample report template"], ["approved outreach"], "Concrete technical pain and differentiated artifacts.", "Needs credibility and examples.", {"speed_to_first_cash": 4, "existing_capability_fit": 5, "low_trust_barrier": 4, "clear_buyer": 4, "clear_pain": 5, "minimal_new_tooling": 4, "low_owner_burden": 3, "repeatability_after_first_sale": 4, "strategic_compounding_value": 5}, "$1000-$3000", "CTO or engineering manager using AI coding agents"),
        path("path_004", "Governed AI workflow setup consulting", "SMB/founder teams", "Need safe AI workflows and approval gates.", "Done-for-you setup of staged policies, approval gates, and no-action receipts", ["asset_policy_registry", "asset_approval_workflow", "asset_owner_cockpit"], "opp_governed_workflow_consulting", "implementation sprint", "21-45 days", 3, 4, 4, 3, ["service delivery checklist", "approval workflow UI"], ["approved sales call"], "Service-before-product can start quickly.", "Delivery may become bespoke.", {"speed_to_first_cash": 3, "existing_capability_fit": 4, "low_trust_barrier": 3, "clear_buyer": 4, "clear_pain": 4, "minimal_new_tooling": 3, "low_owner_burden": 3, "repeatability_after_first_sale": 4, "strategic_compounding_value": 4}, "$1500-$5000", "founder running AI workflows internally"),
        path("path_005", "Compliance evidence packet delivery", "AI governance consultants and internal audit teams", "Need structured proof packets and claim boundaries.", "Evidence packet generation and review pack service", ["asset_evidence_pipeline", "asset_conflict_matrix", "asset_human_review_packet"], "opp_evidence_packet_generation", "paid evidence pack", "14-30 days", 3, 3, 4, 4, ["buyer-specific template", "source quality upgrade"], ["approved outreach"], "Clear artifact and repeatable process.", "Market education required.", {"speed_to_first_cash": 4, "existing_capability_fit": 4, "low_trust_barrier": 3, "clear_buyer": 3, "clear_pain": 4, "minimal_new_tooling": 4, "low_owner_burden": 3, "repeatability_after_first_sale": 4, "strategic_compounding_value": 4}, "$750-$2500", "AI governance consultant needing repeatable evidence packs"),
        path("path_006", "Grant/RFP watch and proposal support", "AI governance builders", "Need funding/RFP discovery and draft support.", "Read-only watch plus proposal outline generation", ["asset_real_web_observation", "asset_ceo_command_brief", "asset_cross_language"], "opp_grant_rfp_support", "proposal support fee", "30-90 days", 2, 3, 3, 3, ["funding/RFP tracker", "proposal generator"], ["form submission only after approval"], "Non-dilutive funding has obvious value.", "Cash cycle can be slow.", {"speed_to_first_cash": 2, "existing_capability_fit": 4, "low_trust_barrier": 3, "clear_buyer": 3, "clear_pain": 4, "minimal_new_tooling": 3, "low_owner_burden": 3, "repeatability_after_first_sale": 3, "strategic_compounding_value": 4}, "$500-$2000", "AI governance startup seeking grants/RFPs"),
        path("path_007", "Cross-border AI/business bridge", "Chinese-English founders", "Need translation between AI tooling, US market norms, and execution workflow.", "Bilingual governed market brief and AI workflow setup", ["asset_cross_language", "asset_owner_mu_speaker", "asset_ceo_command_brief"], "opp_cross_border_bridge", "paid bridge brief", "14-30 days", 4, 3, 3, 3, ["bilingual brief template", "customer discovery script"], ["approved outreach"], "Owner has natural differentiation.", "Needs careful positioning and trust.", {"speed_to_first_cash": 4, "existing_capability_fit": 4, "low_trust_barrier": 4, "clear_buyer": 3, "clear_pain": 4, "minimal_new_tooling": 4, "low_owner_burden": 3, "repeatability_after_first_sale": 3, "strategic_compounding_value": 4}, "$500-$2000", "Chinese-speaking founder building AI product for US market"),
        path("path_008", "Open-source plus paid support for agent governance templates", "AI-native developers", "Need reusable policies and lane runners.", "Open templates with paid setup/support", ["asset_policy_registry", "asset_parallel_orchestrator", "asset_tests_validation"], "opp_devtool_openclaw_codex", "paid support or setup", "30-60 days", 3, 3, 5, 4, ["public docs", "support packaging"], ["publication approval"], "Can compound through ecosystem.", "Open-source attention may not convert quickly.", {"speed_to_first_cash": 3, "existing_capability_fit": 5, "low_trust_barrier": 3, "clear_buyer": 3, "clear_pain": 4, "minimal_new_tooling": 4, "low_owner_burden": 3, "repeatability_after_first_sale": 5, "strategic_compounding_value": 5}, "$300-$1500", "AI-native developer/founder wanting setup help"),
        path("path_009", "Agent-team orchestration template kit", "small technical teams", "Need role/lane/task coordination for agents.", "Template kit plus installation sprint", ["asset_agent_team_runtime", "asset_parallel_orchestrator", "asset_owner_cockpit"], "opp_agent_team_orchestration", "template kit setup", "21-45 days", 3, 3, 4, 3, ["installer", "docs"], ["approved outreach"], "Current L7.0P is strong proof.", "May be perceived as internal-only until packaged.", {"speed_to_first_cash": 3, "existing_capability_fit": 5, "low_trust_barrier": 3, "clear_buyer": 3, "clear_pain": 4, "minimal_new_tooling": 3, "low_owner_burden": 4, "repeatability_after_first_sale": 4, "strategic_compounding_value": 5}, "$500-$2500", "small AI team needing multi-agent ops"),
        path("path_010", "Regulated workflow audit trail consulting", "regulated-market operators", "Need audit trail before AI automation.", "Audit-trail design and evidence receipt setup", ["asset_deterministic_governance", "asset_evidence_pipeline", "asset_policy_registry"], "opp_regulated_audit_trails", "consulting sprint", "60-120 days", 2, 5, 4, 3, ["domain policy", "legal review partner"], ["approved sales process"], "High value if trusted.", "Long sales cycle and trust barrier.", {"speed_to_first_cash": 1, "existing_capability_fit": 4, "low_trust_barrier": 2, "clear_buyer": 3, "clear_pain": 5, "minimal_new_tooling": 2, "low_owner_burden": 2, "repeatability_after_first_sale": 4, "strategic_compounding_value": 5}, "$5000-$15000", "regulated operator piloting AI workflows"),
        path("path_011", "Approval gate implementation for AI teams", "teams worried about agent side effects", "Need draft/request/approve/execute state machine.", "Approval workflow package and integration plan", ["asset_approval_workflow", "asset_policy_registry", "asset_tests_validation"], "opp_startup_ai_governance", "implementation sprint", "21-45 days", 3, 3, 4, 4, ["approval UI", "receipt generator"], ["approved outreach"], "Narrow and sellable wedge.", "Needs integration with buyer tools.", {"speed_to_first_cash": 3, "existing_capability_fit": 4, "low_trust_barrier": 3, "clear_buyer": 4, "clear_pain": 4, "minimal_new_tooling": 3, "low_owner_burden": 3, "repeatability_after_first_sale": 4, "strategic_compounding_value": 4}, "$1000-$4000", "AI team lead needing approval gates"),
        path("path_012", "AI company runtime platform", "ambitious founders and future enterprise teams", "Need an operating system for self-governed agent companies.", "Long-term platform based on Y*Bridge Labs runtime", ["asset_y_star_cieu", "asset_agent_team_runtime", "asset_owner_cockpit", "asset_policy_registry"], "opp_company_runtime_setup", "pilot then platform subscription", "90-180 days", 2, 5, 5, 4, ["product UI", "multi-tenant security", "billing", "support"], ["publication", "sales", "payment after approval"], "Big strategic compounding value.", "Too slow for first cash if overbuilt now.", {"speed_to_first_cash": 1, "existing_capability_fit": 4, "low_trust_barrier": 2, "clear_buyer": 3, "clear_pain": 4, "minimal_new_tooling": 1, "low_owner_burden": 2, "repeatability_after_first_sale": 5, "strategic_compounding_value": 5}, "$1000 pilot then subscription", "founder willing to be design partner"),
        path("path_013", "Trust/proof package generator for AI services", "AI service providers", "Need proof package to win cautious customers.", "Evidence-backed trust packet generator and review", ["asset_evidence_pipeline", "asset_human_review_packet", "asset_ceo_command_brief"], "opp_audit_evidence_compliance", "paid proof package", "14-30 days", 3, 3, 4, 4, ["case-study template", "proof package layout"], ["approved outreach"], "Directly helps others sell AI safely.", "Needs examples of accepted proof packets.", {"speed_to_first_cash": 4, "existing_capability_fit": 4, "low_trust_barrier": 3, "clear_buyer": 4, "clear_pain": 4, "minimal_new_tooling": 4, "low_owner_burden": 3, "repeatability_after_first_sale": 4, "strategic_compounding_value": 4}, "$750-$2500", "AI consultant/service provider"),
        path("path_014", "Lightweight customer discovery tracker for AI agents", "founders validating offers", "Need safe learning from approved outreach without memory chaos.", "CRM-lite plus approval and learning receipts", ["asset_writeback_dry_run", "asset_approval_workflow", "asset_owner_cockpit"], "opp_internal_automation_service", "tooling setup", "30-60 days", 3, 4, 4, 3, ["CRM-lite", "feedback schema"], ["approved outreach"], "Connects cash experiments to learning.", "Requires external interaction to prove value.", {"speed_to_first_cash": 3, "existing_capability_fit": 3, "low_trust_barrier": 3, "clear_buyer": 4, "clear_pain": 4, "minimal_new_tooling": 2, "low_owner_burden": 4, "repeatability_after_first_sale": 4, "strategic_compounding_value": 5}, "$500-$2000", "founder doing customer discovery"),
    ]


def ranking(paths: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return sorted(paths, key=lambda item: item[key], reverse=True)


def scorecard(paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in paths:
        scores = item["score_inputs"]
        strategic = round((item["scalability"] + scores["strategic_compounding_value"] + item["evidence_strength"] + scores["repeatability_after_first_sale"]) / 4, 2)
        total = round((item["cash_path_score"] + strategic) / 2, 2)
        rows.append(
            {
                "path_id": item["path_id"],
                "path_name": item["path_name"],
                "external_demand": scores["clear_pain"],
                "internal_advantage_fit": scores["existing_capability_fit"],
                "uniqueness": scores["strategic_compounding_value"],
                "trustability": scores["low_trust_barrier"],
                "speed_to_first_revenue": scores["speed_to_first_cash"],
                "shortest_cash_realization_score": item["cash_path_score"],
                "owner_burden": scores["low_owner_burden"],
                "delivery_feasibility": scores["low_delivery_complexity"] if "low_delivery_complexity" in scores else max(1, 6 - item["delivery_complexity"]),
                "margin_potential": scores["minimal_new_tooling"],
                "scalability": item["scalability"],
                "evidence_strength": item["evidence_strength"],
                "toolmaking_leverage": scores["strategic_compounding_value"],
                "ability_to_improve_agent_company_system": scores["strategic_compounding_value"],
                "alignment_with_long_term_y_star_vision": scores["strategic_compounding_value"],
                "total_score": total,
                "strategic_score": strategic,
                "cash_path_score": item["cash_path_score"],
                "confidence_level": "medium",
                "caveats": item["why_this_path_might_fail"],
            }
        )
    return rows


def build_tool_gaps(top_paths: list[dict[str, Any]]) -> dict[str, Any]:
    blocking = [
        {
            "gap_id": "gap_cash_001",
            "linked_path_id": top_paths[0]["path_id"],
            "missing_capability": "approval-ready outreach draft and owner review flow",
            "current_workaround": "manual review of internal offer hypothesis",
            "can_codex_build": True,
            "requires_real_world_action": False,
            "priority": "P0",
            "revenue_impact": "high",
            "cash_path_impact": "directly enables first paid validation request after human approval",
            "suggested_sprint": "L7.3",
            "can_parallelize": True,
            "risk_if_not_built": "cash path remains internal-only",
            "should_build_this_week": True,
        },
        {
            "gap_id": "gap_cash_002",
            "linked_path_id": top_paths[0]["path_id"],
            "missing_capability": "service delivery workflow generator",
            "current_workaround": "custom Markdown brief per sprint",
            "can_codex_build": True,
            "requires_real_world_action": False,
            "priority": "P0",
            "revenue_impact": "high",
            "cash_path_impact": "turns one-off brief into repeatable paid deliverable",
            "suggested_sprint": "L7.3",
            "can_parallelize": True,
            "risk_if_not_built": "delivery remains bespoke",
            "should_build_this_week": True,
        },
    ]
    accelerators = [
        ("gap_accel_001", "customer segment database", "speeds buyer targeting"),
        ("gap_accel_002", "trust/proof package generator", "reduces trust barrier"),
        ("gap_accel_003", "offer validation tracker", "captures paid-intent signals"),
        ("gap_accel_004", "revenue experiment dashboard", "keeps owner focused on cash path"),
    ]
    strategic = [
        ("gap_strategic_001", "memory writeback approval UI", "connects reviewed learning to future strategy"),
        ("gap_strategic_002", "agent task scheduler", "scales parallel execution"),
        ("gap_strategic_003", "source quality classifier upgrade", "strengthens evidence trust"),
        ("gap_strategic_004", "PDF reader", "expands evidence sources"),
    ]
    deferred = [
        ("gap_defer_001", "multi-tenant product UI", "important later but overbuilds before cash validation"),
        ("gap_defer_002", "billing automation", "wait until approved offer validation"),
        ("gap_defer_003", "autonomous outreach executor", "blocked until approval workflow is exercised"),
    ]

    def gap(gid: str, capability: str, impact: str, priority: str, should: bool) -> dict[str, Any]:
        return {
            "gap_id": gid,
            "linked_path_id": top_paths[0]["path_id"],
            "missing_capability": capability,
            "current_workaround": "human-reviewed internal artifact",
            "can_codex_build": True,
            "requires_real_world_action": False,
            "priority": priority,
            "revenue_impact": "medium",
            "cash_path_impact": impact,
            "suggested_sprint": "L7.3" if should else "later",
            "can_parallelize": True,
            "risk_if_not_built": "slower validation or weaker repeatability",
            "should_build_this_week": should,
        }

    return {
        "cash_path_blocking_tools": blocking,
        "cash_path_accelerators": [gap(gid, cap, impact, "P1", True) for gid, cap, impact in accelerators],
        "strategic_long_term_tools": [gap(gid, cap, impact, "P2", False) for gid, cap, impact in strategic],
        "defer_tools": [gap(gid, cap, impact, "P3", False) for gid, cap, impact in deferred],
    }


def build_all() -> None:
    real_status = real_observation_status()
    opportunities = build_external_opportunities()
    assets = build_internal_assets()
    matches = opportunity_asset_matches(opportunities, assets)
    paths = commercial_paths()
    cash_ranked = ranking(paths, "cash_path_score")
    strategic_ranked = sorted(paths, key=lambda item: (item["score_inputs"]["strategic_compounding_value"], item["scalability"], item["cash_path_score"]), reverse=True)
    score_rows = scorecard(paths)
    top_cash = cash_ranked[0]
    top_long = strategic_ranked[0]
    bridge = "path_009" if top_long["path_id"] == "path_012" else top_cash["path_id"]
    bridge_path = next(item for item in paths if item["path_id"] == bridge)

    write_json("external_world_opportunity_map/external_world_opportunity_map.json", {**packet("external_world_opportunity_map"), "real_external_observation": real_status, "opportunity_categories": opportunities})
    write_text("external_world_opportunity_map/external_world_opportunity_map.md", simple_md("External World Opportunity Map", [("Scope", "Broad opportunity map generated from existing evidence and L7 commercial artifacts."), ("Categories", md_table(opportunities, ["category_id", "opportunity_description", "customer_or_funder_segment", "time_to_cash_estimate"]))]))

    write_json("internal_asset_and_advantage_map/internal_asset_and_advantage_map.json", {**packet("internal_asset_and_advantage_map"), "assets": assets})
    write_text("internal_asset_and_advantage_map/internal_asset_and_advantage_map.md", simple_md("Internal Asset and Advantage Map", [("Assets", md_table(assets, ["asset_id", "description", "maturity", "commercial_relevance"]))]))

    write_json("opportunity_asset_match_matrix/opportunity_asset_match_matrix.json", {**packet("opportunity_asset_match_matrix"), "match_rows": matches})
    write_text("opportunity_asset_match_matrix/opportunity_asset_match_matrix.md", simple_md("Opportunity x Asset Match Matrix", [("Core Matrix", md_table(matches, ["opportunity_id", "fit_score", "cash_realization_potential", "recommended_path_candidate"]))]))

    write_json("commercial_path_generation/commercial_path_portfolio.json", {**packet("commercial_path_portfolio"), "candidate_paths": paths})
    write_text("commercial_path_generation/commercial_path_portfolio.md", simple_md("Commercial Path Portfolio", [("Candidate Money Paths", md_table(paths, ["path_id", "path_name", "first_possible_buyer", "time_to_first_revenue", "cash_path_score"]))]))

    cash_model = {
        **packet("shortest_cash_path_model"),
        "definition": "Fewest new tools, lowest external dependency, lowest owner burden, lowest trust barrier, shortest delivery cycle, and fewest approval steps toward first paid/strong-intent signal.",
        "weights": WEIGHTS,
        "distinctions": {
            "fastest_to_cash": top_cash["path_id"],
            "fastest_to_paid_validation": top_cash["path_id"],
            "fastest_to_customer_commitment": "path_003",
            "fastest_to_grant_or_funding_submission_ready": "path_006",
            "fastest_to_service_delivery": top_cash["path_id"],
            "fastest_to_repeatable_offer": "path_002",
        },
    }
    write_json("shortest_cash_realization_path/shortest_cash_path_model.json", cash_model)
    write_text("shortest_cash_realization_path/shortest_cash_path_model.md", simple_md("Shortest Cash Path Model", [("Definition", cash_model["definition"]), ("Weights", json.dumps(WEIGHTS, indent=2))]))
    write_json("shortest_cash_realization_path/cash_path_scorecard.json", {**packet("cash_path_scorecard"), "scorecard": [{"path_id": item["path_id"], "path_name": item["path_name"], "cash_path_score": item["cash_path_score"], "score_inputs": item["score_inputs"]} for item in paths]})
    write_text("shortest_cash_realization_path/cash_path_ranking.md", simple_md("Cash Path Ranking", [("Shortest Cash Ranking", md_table(cash_ranked, ["path_id", "path_name", "cash_path_score", "time_to_first_revenue", "first_possible_buyer"]))]))
    first_decision = {
        **packet("first_cash_step_decision"),
        "primary_shortest_cash_path": top_cash["path_id"],
        "primary_shortest_cash_path_name": top_cash["path_name"],
        "why_faster_than_others": "It can start as a service using current controlled observation, evidence, command brief, and owner review artifacts without waiting for a full product.",
        "where_first_money_likely_comes_from": top_cash["first_possible_buyer"],
        "first_chargeable_deliverable": top_cash["first_possible_paid_offer"],
        "first_possible_buyer": top_cash["first_possible_buyer"],
        "why_would_they_pay": "They need a fast, trusted internal decision deliverable and do not want accidental outreach, publication, or unsafe agent behavior.",
        "current_capabilities_enough_to_deliver": True,
        "minimum_missing_tool": "approval-ready outreach draft and service delivery workflow generator",
        "can_start_as_service_before_product": True,
        "requires_outreach": True,
        "outreach_requires_human_approval": True,
        "minimum_commercial_experiment": "human-reviewed offer one-pager plus approved outreach to 3-5 warm or highly targeted prospects",
        "estimated_time_to_paid_signal": "7-14 days for strong-intent signal, 14-30 days for first paid pilot if approved outreach occurs",
        "biggest_blocker": "trust and approved buyer contact, not product functionality",
        "what_codex_should_build_next": "approval-ready outreach draft generator plus service delivery workflow generator",
    }
    write_json("shortest_cash_realization_path/first_cash_step_decision.json", first_decision)
    write_text("shortest_cash_realization_path/first_cash_step_decision.md", simple_md("First Cash Step Decision", [("Decision", f"{top_cash['path_id']}: {top_cash['path_name']}"), ("Why", first_decision["why_faster_than_others"]), ("Next Build", first_decision["what_codex_should_build_next"])]))

    leverage = {
        **packet("strategic_leverage_scorecard"),
        "shortest_cash_ranking": [{"path_id": item["path_id"], "path_name": item["path_name"], "cash_path_score": item["cash_path_score"]} for item in cash_ranked],
        "strategic_compounding_ranking": [{"path_id": item["path_id"], "path_name": item["path_name"], "strategic_compounding_value": item["score_inputs"]["strategic_compounding_value"], "cash_path_score": item["cash_path_score"]} for item in strategic_ranked],
        "primary_shortest_cash_path": top_cash["path_id"],
        "primary_long_term_strategic_path": top_long["path_id"],
        "bridge_path_between_cash_and_strategy": bridge_path["path_id"],
        "why_they_differ": "The fastest cash path is a service wedge; the long-term path is a platform/runtime and would be overbuilt before validation.",
        "which_should_be_done_first": top_cash["path_id"],
        "how_cash_funds_strategy": "Paid service delivery produces case studies, trust artifacts, buyer language, and tool requirements for the future platform.",
        "what_must_not_be_overbuilt": "Do not build autonomous outreach, billing, multi-tenant UI, or permanent writeback before paid validation.",
        "scorecard": score_rows,
    }
    write_json("strategic_leverage_scorecard/strategic_leverage_scorecard.json", leverage)
    write_text("strategic_leverage_scorecard/strategic_leverage_scorecard.md", simple_md("Strategic Leverage Scorecard", [("Shortest Cash", top_cash["path_name"]), ("Long-Term Strategic", top_long["path_name"]), ("Bridge", bridge_path["path_name"])]))

    counterfactuals = []
    for item in cash_ranked[:5]:
        counterfactuals.append(
            {
                "path_id": item["path_id"],
                "best_case": "paid pilot or strong-intent signal within the estimated window",
                "base_case": "useful internal deliverable plus approval-ready outreach draft",
                "failure_case": "buyer trust insufficient or pain not urgent",
                "fastest_path_to_cash": item["shortest_cash_step"],
                "slow_but_strategic_path": "build full platform before selling",
                "if_goal_is_cash_in_30_days": "focus on service delivery and approved outreach, not product UI",
                "if_goal_is_paid_validation_in_14_days": "use warm/targeted approval-gated outreach and offer one-pager",
                "if_owner_time_is_under_5_hours_per_week": "Codex prepares all drafts; owner only approves and records responses",
                "if_no_external_trust_exists_yet": "sell small scoped audit/brief first",
                "if_no_product_is_ready": "service-first still works",
                "if_service_can_be_sold_before_product": True,
                "if_customer_only_buys_done_for_you": "position as done-for-you governed workflow/brief sprint",
                "if_grant_path_is_too_slow": "defer grant path behind service wedge",
                "if_enterprise_sales_cycle_is_too_long": "sell founder/SMB wedge first",
                "if_owner_english_friction_limits_direct_sales": "build bilingual approval-ready scripts and use narrow written outreach",
                "if_codex_can_build_required_tools_in_parallel": "build outreach draft generator, service workflow, and experiment tracker concurrently",
                "assumptions": ["human approval before external contact", "internal deliverable can be produced with current tools"],
                "likely_outcome": "internal validation now; external validation after approval",
                "risk": item["why_this_path_might_fail"],
                "evidence_needed": "buyer pain and willingness-to-pay response",
                "tool_needed": item["minimum_new_capabilities_required"],
                "approval_needed": item["required_external_actions"],
                "cash_path_adjustment": "reduce scope until buyer can say yes quickly",
                "minimum_next_action": "owner review and approve or reject one experiment",
                "does_this_path_still_work": item["can_start_as_service"],
            }
        )
    write_json("money_path_counterfactuals/money_path_counterfactuals.json", {**packet("money_path_counterfactuals"), "counterfactuals": counterfactuals})
    write_text("money_path_counterfactuals/money_path_counterfactuals.md", simple_md("Money Path Counterfactuals", [("Top Candidate Counterfactuals", md_table(counterfactuals, ["path_id", "best_case", "failure_case", "if_goal_is_cash_in_30_days"]))]))

    gaps = build_tool_gaps(cash_ranked[:3])
    write_json("tool_gap_backpropagation/tool_gap_backpropagation.json", {**packet("tool_gap_backpropagation"), **gaps})
    write_text("tool_gap_backpropagation/tool_gap_backpropagation.md", simple_md("Tool Gap Backpropagation", [("Cash Path Blocking Tools", md_table(gaps["cash_path_blocking_tools"], ["gap_id", "missing_capability", "priority", "should_build_this_week"])), ("Defer", md_table(gaps["defer_tools"], ["gap_id", "missing_capability", "cash_path_impact"]))]))

    routes = []
    for idx, item in enumerate(cash_ranked[:5], start=1):
        routes.append(
            {
                "route_id": f"route_{idx:03d}",
                "linked_path_id": item["path_id"],
                "agent_assignments": {
                    "CEO": "choose path and approve or reject external steps",
                    "Revenue Scout": "maintain opportunity and buyer pain map",
                    "Researcher": "run read-only evidence observation",
                    "Operator/COO": "turn path into delivery workflow",
                    "Engineer/CTO": "build required tools",
                    "Secretary": "archive artifacts and prepare approval packets",
                    "Auditor": "verify no side effects and policy compliance",
                },
                "handoff_sequence": ["Revenue Scout", "Researcher", "Operator/COO", "Engineer/CTO", "Secretary", "Auditor", "CEO"],
                "required_artifacts": ["opportunity packet", "offer hypothesis", "approval request", "no-action receipt"],
                "approval_points": item["required_external_actions"],
                "no-go_boundaries": ["no unapproved outreach", "no payment", "no publication", "no actual writeback"],
                "expected_output": "owner-ready experiment packet",
                "next_command": "bash scripts/run_l7_2_money_path_engine.sh --mode build",
                "cash_path_role": "primary" if item["path_id"] == top_cash["path_id"] else "secondary",
            }
        )
    write_json("agent_team_execution_routes/agent_team_execution_routes.json", {**packet("agent_team_execution_routes"), "routes": routes})
    write_text("agent_team_execution_routes/agent_team_execution_routes.md", simple_md("Agent Team Execution Routes", [("Routes", md_table(routes, ["route_id", "linked_path_id", "cash_path_role", "expected_output"]))]))

    experiments = []
    experiment_types = [
        "read-only market validation",
        "internal offer prototype",
        "mock proposal",
        "human-reviewed outreach draft",
        "landing page draft for review only",
        "grant/RFP watch",
        "customer interview script for future approval",
        "service delivery dry-run",
        "pricing sensitivity hypothesis",
        "trust/proof package review",
        "first paid validation simulation",
    ]
    for idx, exp_type in enumerate(experiment_types, start=1):
        linked = cash_ranked[(idx - 1) % 5]
        experiments.append(
            {
                "experiment_id": f"experiment_{idx:03d}",
                "linked_path_id": linked["path_id"],
                "goal": f"Test {exp_type} for {linked['path_name']}",
                "method": exp_type,
                "evidence_needed": "buyer pain, trust response, or deliverable usefulness",
                "expected_learning": "whether the path can produce a paid or strong-intent signal",
                "owner_effort": "low" if idx <= 4 else "medium",
                "external_action_required": exp_type in {"human-reviewed outreach draft", "customer interview script for future approval"},
                "human_approval_required": exp_type in {"human-reviewed outreach draft", "customer interview script for future approval"},
                "success_criteria": "clear yes/no paid validation signal or stronger evidence gap",
                "cash_signal_tested": "paid validation, customer commitment, or pricing reaction",
                "next_step_if_success": "prepare approval-gated external action or delivery sprint",
                "next_step_if_failure": "revise segment, pain, or offer scope",
            }
        )
    write_json("commercial_experiment_portfolio/commercial_experiment_portfolio.json", {**packet("commercial_experiment_portfolio"), "experiments": experiments})
    write_text("commercial_experiment_portfolio/commercial_experiment_portfolio.md", simple_md("Commercial Experiment Portfolio", [("Experiments", md_table(experiments, ["experiment_id", "linked_path_id", "method", "human_approval_required", "cash_signal_tested"]))]))

    decision = {
        **packet("meta_development_decision_packet"),
        "best_current_money_path": top_cash["path_id"],
        "shortest_cash_realization_path": top_cash["path_id"],
        "best_long_term_strategic_path": top_long["path_id"],
        "bridge_between_short_term_cash_and_long_term_strategy": bridge_path["path_id"],
        "second_best_path": cash_ranked[1]["path_id"],
        "paths_to_explore_not_pursue_yet": ["path_006", "path_010", "path_012"],
        "paths_to_avoid_now": ["autonomous outreach product", "multi-tenant platform before paid validation", "enterprise compliance sale before trust proof"],
        "internal_advantage_driving_recommendation": "current system can already produce governed observation, evidence packets, command briefs, and approval gates.",
        "external_evidence_support": [artifact_ref("l7_revenue_opportunity_radar_l7_1/real_read_only_revenue_scan_report.json")],
        "weak_or_uncertain": "Direct buyer willingness-to-pay is unvalidated.",
        "tool_to_build_next": first_decision["what_codex_should_build_next"],
        "experiment_to_run_next": "first paid validation simulation plus approval-ready outreach draft",
        "requires_human_approval": ["any outreach", "publication", "payment", "actual writeback"],
        "remains_forbidden": ["unapproved outreach", "form submission", "payment", "publication", "actual core writeback"],
        "how_this_improves_agent_company": "Backpropagates cash-path tool gaps into the agent team roadmap.",
    }
    write_json("meta_development_decision_packet/meta_development_decision_packet.json", decision)
    write_text("meta_development_decision_packet/meta_development_decision_packet.md", simple_md("Meta-Development Decision Packet", [("Best Current Money Path", top_cash["path_name"]), ("Shortest Cash Path", top_cash["path_name"]), ("Next Tool", decision["tool_to_build_next"])]))

    owner_md = simple_md(
        "L7.2 Money Path Owner Review Packet",
        [
            ("What the agent team analyzed", "External opportunity categories, internal advantages, opportunity-asset fit, 14 candidate money paths, shortest cash score, counterfactuals, tool gaps, agent execution routes, and commercial experiments."),
            ("Top 3 money paths", md_table(cash_ranked[:3], ["path_id", "path_name", "cash_path_score", "first_possible_buyer", "first_possible_price_range"])),
            ("Recommended first", f"{top_cash['path_name']} because it can start as a service with current tools before a full product exists."),
            ("Long-term strategy", f"{top_long['path_name']} remains the compounding platform path, but should be funded and clarified by service wedge learning."),
            ("# 最短兑现路径 / Shortest Cash Realization Path", "\n".join([
                f"现在最短的赚钱路径是什么？{top_cash['path_name']}。",
                "为什么不是其它看起来更大的路径？因为大平台、企业合规、grant/RFP 都更慢、更重、更需要信任。",
                f"第一笔钱可能从哪里来？{top_cash['first_possible_buyer']}。",
                f"第一个可收费交付物是什么？{top_cash['first_possible_paid_offer']}。",
                f"谁最可能付钱？{top_cash['first_possible_buyer']}。",
                "我需要批准什么？任何对外 outreach、发布、付款、提交表单、真实写回都需要你批准。",
                f"Codex 下一步应该构建什么？{first_decision['what_codex_should_build_next']}。",
                "agent team 下一步应该观察什么？目标买家的痛点、已有替代方案、愿意为内部 brief 付费的信号。",
                "什么事情暂时不要做？不要先做多租户平台、自动发邮件、收款自动化、公开营销或永久记忆写回。",
                "最快 7 天能验证：offer one-pager 和交付模板；14 天能验证：批准后的买家兴趣；30 天能验证：付费 pilot 或强意向信号。",
            ])),
            ("Next one-command action", "bash scripts/run_l7_2_money_path_engine.sh --mode build"),
        ],
    )
    owner_packet = {
        **packet("owner_review_packet"),
        "top_3_money_paths": [{"path_id": item["path_id"], "path_name": item["path_name"], "cash_path_score": item["cash_path_score"]} for item in cash_ranked[:3]],
        "primary_shortest_cash_path": top_cash["path_id"],
        "primary_long_term_strategic_path": top_long["path_id"],
        "bridge_path_between_cash_and_strategy": bridge_path["path_id"],
        "next_tool_to_build": first_decision["what_codex_should_build_next"],
        "next_one_command_action": "bash scripts/run_l7_2_money_path_engine.sh --mode build",
    }
    write_json("owner_review_packet/l7_2_money_path_owner_review_packet.json", owner_packet)
    write_text("owner_review_packet/l7_2_money_path_owner_review_packet.md", owner_md)

    receipt = {**packet("no_action_receipt")}
    for flag in NO_ACTION_FLAGS:
        receipt[f"{flag}_occurred"] = False
    write_json("l7_2_no_action_receipt/l7_2_no_action_receipt.json", receipt)

    summary = {
        **packet("l7_2_summary"),
        "real_external_observation_used": real_status["real_external_observation_used"],
        "external_opportunity_categories_analyzed": len(opportunities),
        "internal_assets_mapped": len(assets),
        "candidate_money_paths_generated": len(paths),
        "top_3_money_paths": [{"path_id": item["path_id"], "path_name": item["path_name"], "cash_path_score": item["cash_path_score"]} for item in cash_ranked[:3]],
        "primary_shortest_cash_path": top_cash["path_id"],
        "primary_shortest_cash_path_name": top_cash["path_name"],
        "primary_long_term_strategic_path": top_long["path_id"],
        "primary_long_term_strategic_path_name": top_long["path_name"],
        "bridge_path_between_cash_and_strategy": bridge_path["path_id"],
        "first_cash_step": top_cash["shortest_cash_step"],
        "first_possible_buyer": top_cash["first_possible_buyer"],
        "first_possible_paid_offer": top_cash["first_possible_paid_offer"],
        "estimated_time_to_paid_signal": first_decision["estimated_time_to_paid_signal"],
        "minimum_tool_needed_for_cash_path": first_decision["minimum_missing_tool"],
        "next_codex_build_for_cash_path": first_decision["what_codex_should_build_next"],
        "next_agent_observation_for_cash_path": "read-only buyer pain scan and approved customer discovery script",
        "paths_deferred": decision["paths_to_explore_not_pursue_yet"],
        "paths_avoided": decision["paths_to_avoid_now"],
        "counterfactuals_generated": len(counterfactuals),
        "tool_gaps_identified": sum(len(value) for value in gaps.values()),
        "next_tool_to_build": first_decision["what_codex_should_build_next"],
        "next_recommended_sprint": "L7.3 Approval-Ready Offer Validation and Service Delivery Workflow",
        "next_one_command_action": "bash scripts/run_l7_2_money_path_engine.sh --mode build",
        "ask_user_url_occurred": False,
        "external_side_effects_occurred": False,
        "customer_contacted": False,
        "email_sent": False,
        "form_submitted": False,
        "payment_occurred": False,
        "publication_occurred": False,
        "core_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }
    write_json("l7_meta_development_money_path_engine/l7_2_summary.json", summary)
    write_text("l7_meta_development_money_path_engine/l7_2_summary.md", simple_md("L7.2 Money Path Intelligence Engine", [("Primary Shortest Cash Path", top_cash["path_name"]), ("Long-Term Strategic Path", top_long["path_name"]), ("Bridge", bridge_path["path_name"]), ("Next Tool", summary["next_tool_to_build"])]))


if __name__ == "__main__":
    build_all()
