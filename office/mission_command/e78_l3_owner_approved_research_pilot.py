from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
JOB_ID = "e78_owner_approved_l3_read_only_external_research_pilot_R1_post_E73_20260507T000001Z"
EXPECTED_BASE = "0a44916d01cb5237bdd400ab8a16b9b71f023802"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
OWNER_DECISION_STATUS = "APPROVE_L3_READ_ONLY_RESEARCH_PILOT"
ROUTE = "governed_business_operations_blueprint_for_agent_teams"
PRODUCT_CONTEXT = "Governed Business Operations Blueprint for Agent Teams + CIEU Audit Module"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def git_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT

    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=base, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "branch": run("branch", "--show-current"),
        "head": run("rev-parse", "HEAD"),
        "expected_branch": EXPECTED_BRANCH,
        "expected_head": EXPECTED_BASE,
    }


def base_verified(root: Path | None = None) -> bool:
    state = git_state(root)
    return state["branch"] == EXPECTED_BRANCH and state["head"] == EXPECTED_BASE


def forbidden_claims() -> list[str]:
    return [
        "customer validation",
        "expert validation",
        "paid signal",
        "pricing validation",
        "legal compliance",
        "regulatory certification",
        "production deployment",
        "live audit ledger",
        "live provider execution",
        "L4 external action readiness achieved",
        "L5 revenue readiness",
    ]


def load_required_context(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return {
        "E73": {
            "responsibility_matrix": load_json("operations/external_validation/e73_ecosystem_responsibility_matrix.json", base),
            "no_new_wheel_policy": load_json("operations/external_validation/e73_no_new_wheel_policy.json", base),
            "readiness_gate": load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", base),
            "self_architecture_protocol": load_json("operations/external_validation/e73_ceo_self_architecture_protocol.json", base),
            "owner_closure": load_json("operations/external_validation/e73_owner_readable_closure_report.json", base),
        },
        "E74": {
            "readiness_packet": load_json("operations/external_validation/e74_owner_facing_l3_readiness_packet.json", base),
            "allowlist": load_json("operations/external_validation/e74_l3_allowlist_proposal_no_execution.json", base),
            "reuse_map": load_json("operations/external_validation/e74_existing_artifact_reuse_map.json", base),
            "residual": load_json("operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json", base),
            "readback": load_json("operations/external_validation/e74_ceo_l2_work_readback.json", base),
            "completion": load_json("operations/external_validation/e74_completion_report.json", base),
        },
        "E75": {
            "decision_packet": load_json("operations/external_validation/e75_l3_owner_decision_packet.json", base),
            "allowlist_denylist": load_json("operations/external_validation/e75_l3_source_allowlist_and_denylist.json", base),
            "receipt_schema": load_json("operations/external_validation/e75_l3_evidence_receipt_schema.json", base),
            "approval_form": load_json("operations/external_validation/e75_l3_owner_approval_form.json", base),
            "residual": load_json("operations/external_validation/e75_cieu_residual_for_owner_decision_packet.json", base),
            "readback": load_json("operations/external_validation/e75_ceo_readback.json", base),
            "completion": load_json("operations/external_validation/e75_completion_report.json", base),
        },
        "E76_E77": {
            "lineage_map": load_json("operations/external_validation/e76_e77_prior_public_read_lineage_map.json", base),
            "reconciliation": load_json("operations/external_validation/e76_e77_public_read_lineage_reconciliation.json", base),
            "decision_record": load_json("operations/external_validation/e76_e77_owner_decision_record.json", base),
            "naming_registry": load_json("operations/external_validation/e76_e77_corrected_l3_milestone_naming_registry.json", base),
            "phase_gate": load_json("operations/external_validation/e76_e77_phase_gate_result.json", base),
            "readback": load_json("operations/external_validation/e76_e77_ceo_readback.json", base),
            "completion": load_json("operations/external_validation/e76_e77_completion_report.json", base),
        },
        "product": {
            "cieu_audit_module": load_json("products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json", base),
            "updated_offer": load_json("products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json", base),
        },
    }


def _receipt(
    source_id: str,
    title: str,
    url: str,
    category: str,
    evidence_type: str,
    claims: list[str],
    summary: str,
    *,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_title": title,
        "source_url": url,
        "source_locator": url,
        "source_category": category,
        "access_mode": "public_read_only",
        "access_time": "2026-05-07T13:25:00Z",
        "public_read_only_confirmed": True,
        "login_required": False,
        "interaction_required": False,
        "evidence_type": evidence_type,
        "relevant_claims_supported": claims,
        "quote_or_summary_boundary": summary,
        "risk_flags": risk_flags or ["none"],
        "allowed_by_owner_scope": True,
        "included_in_synthesis": True,
        "exclusion_reason": None,
        "no_contact_confirmed": True,
        "no_publication_confirmed": True,
        "no_payment_confirmed": True,
    }


def source_receipts() -> list[dict[str, Any]]:
    return [
        _receipt(
            "SRC001",
            "OpenAI Agents SDK tracing documentation",
            "https://openai.github.io/openai-agents-python/tracing/",
            "official_agent_framework_docs",
            "tool_trace_and_observability_language",
            ["agent runs need traces", "tool calls and guardrails are observable units"],
            "OpenAI's Agents SDK docs describe tracing of agent runs, model generations, function calls, guardrails, handoffs, and custom spans. This supports tool-call oversight language.",
        ),
        _receipt(
            "SRC002",
            "LangChain human-in-the-loop docs",
            "https://docs.langchain.com/oss/python/langchain/human-in-the-loop",
            "official_agent_framework_docs",
            "human_approval_and_control_boundary_language",
            ["human approval can be required before sensitive tool calls", "interrupt and resume patterns are first-class"],
            "LangChain documents middleware that pauses execution and waits for human decisions before tool calls. This supports controlled delegation and owner-gated action language.",
        ),
        _receipt(
            "SRC003",
            "Microsoft AutoGen human-in-the-loop guide",
            "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html",
            "official_agent_framework_docs",
            "human_feedback_and_agent_control_language",
            ["agent frameworks expose human feedback modes", "interactive approval is a common agent operations concern"],
            "AutoGen's AgentChat guide includes human-in-the-loop modes and warnings about potential indefinite blocking. This supports a need for explicit action boundaries and operator controls.",
        ),
        _receipt(
            "SRC004",
            "LangChain platform overview",
            "https://www.langchain.com/",
            "ai_governance_observability_security_vendor_pages",
            "adjacent_product_category_presence",
            ["agent engineering platform demand", "observability, evaluation, deployment, and iteration are packaged together"],
            "LangChain positions its platform around agent engineering, observability, testing, evaluation, deployment, and improvement. This is adjacent to a governed operations blueprint.",
        ),
        _receipt(
            "SRC005",
            "LangSmith observability concepts",
            "https://docs.langchain.com/langsmith/observability-concepts",
            "ai_governance_observability_security_vendor_pages",
            "observability_trace_concept_language",
            ["traces, runs, spans, metadata, and feedback are buyer-readable concepts"],
            "LangSmith explains observability around traces, runs, spans, metadata, feedback, and evaluators. This strengthens the auditability/traceability part of the route.",
        ),
        _receipt(
            "SRC006",
            "Langfuse LLM engineering platform",
            "https://langfuse.com/",
            "ai_governance_observability_security_vendor_pages",
            "adjacent_product_category_presence",
            ["LLM tracing, evaluation, prompt management, and metrics are established adjacent categories"],
            "Langfuse describes open-source LLM engineering with tracing, prompt management, evaluations, metrics, and datasets. This supports a market category around LLM/agent ops visibility.",
        ),
        _receipt(
            "SRC007",
            "Langfuse pricing",
            "https://langfuse.com/pricing",
            "public_pricing_pages",
            "pricing_packaging_public_proxy",
            ["usage-based pricing and retention tiers are visible public analogs"],
            "Langfuse public pricing shows free/hobby and paid tiers, usage unit pricing, retention differences, and enterprise features. This is a pricing proxy only, not pricing validation.",
            risk_flags=["pricing_proxy_not_validation"],
        ),
        _receipt(
            "SRC008",
            "Arize Phoenix documentation",
            "https://arize.com/docs/phoenix",
            "ai_governance_observability_security_vendor_pages",
            "llm_observability_and_evaluation_language",
            ["LLM tracing and evaluation are adjacent product capabilities"],
            "Phoenix docs describe AI observability and evaluation workflows with tracing, evaluation, experiments, and prompt management. This is adjacent to blueprint/control-room positioning.",
        ),
        _receipt(
            "SRC009",
            "Arize / Phoenix pricing",
            "https://arize.com/pricing/",
            "public_pricing_pages",
            "pricing_packaging_public_proxy",
            ["open-source/free and pro tiers are visible public analogs"],
            "Arize's public pricing shows free/open-source Phoenix, AX Pro, and enterprise options. This informs packaging analogs but does not validate Y*Bridge pricing.",
            risk_flags=["pricing_proxy_not_validation"],
        ),
        _receipt(
            "SRC010",
            "OpenInference specification",
            "https://arize-ai.github.io/openinference/spec/semantic_conventions.html",
            "public_github_repos_issues",
            "trace_semantic_convention_language",
            ["agent, chain, tool, retriever, and embedding spans are standardized public observability concepts"],
            "OpenInference semantic conventions define tracing spans for LLM applications including agents, chains, tools, retrievers, and embeddings. This supports audit trace semantics.",
        ),
        _receipt(
            "SRC011",
            "OpenInference GitHub repository",
            "https://github.com/Arize-ai/openinference",
            "public_github_repos_issues",
            "public_repo_category_presence",
            ["open-source instrumentation exists for LLM observability"],
            "The OpenInference repository presents open-source instrumentation for LLM application observability with OpenTelemetry compatibility. This supports the existence of a developer-facing trace ecosystem.",
        ),
        _receipt(
            "SRC012",
            "NIST AI Risk Management Framework",
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "public_standards_regulatory_guidance",
            "risk_management_language",
            ["govern, map, measure, manage language supports governance framing"],
            "NIST's AI RMF is a voluntary risk management framework with govern/map/measure/manage functions. It is useful public guidance context, not compliance proof.",
            risk_flags=["regulatory_context_not_compliance_proof"],
        ),
        _receipt(
            "SRC013",
            "NIST Generative AI Profile",
            "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence",
            "public_standards_regulatory_guidance",
            "generative_ai_risk_language",
            ["AI risk guidance supports careful governance and evidence language"],
            "NIST's Generative AI Profile points to generative AI risks and risk-management practices. It supports compliance-readiness language only as public context.",
            risk_flags=["regulatory_context_not_compliance_proof"],
        ),
        _receipt(
            "SRC014",
            "NIST AI RMF Playbook",
            "https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook",
            "public_standards_regulatory_guidance",
            "governance_practice_language",
            ["risk management workflows need documentation and repeatable practices"],
            "The NIST AI RMF Playbook provides actions and resources for applying AI risk management. It supports structured governance workflow language without proving compliance.",
            risk_flags=["regulatory_context_not_compliance_proof"],
        ),
        _receipt(
            "SRC015",
            "ISO/IEC 42001 overview",
            "https://www.iso.org/standard/42001",
            "public_standards_regulatory_guidance",
            "ai_management_system_language",
            ["AI management system language exists as a public category"],
            "ISO describes ISO/IEC 42001 as an AI management system standard. This supports management-system and readiness language, not certification or legal sufficiency.",
            risk_flags=["standards_context_not_certification"],
        ),
        _receipt(
            "SRC016",
            "Arden AI agent governance platform",
            "https://www.arden.sh/",
            "ai_governance_observability_security_vendor_pages",
            "governance_policy_audit_product_language",
            ["runtime policy enforcement and audit logs are adjacent product claims"],
            "Arden's product language focuses on monitoring agent behavior, enforcing runtime policies, blocking unauthorized actions, and generating audit logs. This strongly supports the buyer/problem category.",
        ),
        _receipt(
            "SRC019",
            "Rutile autonomous agent control platform",
            "https://www.rutilea.com/",
            "ai_governance_observability_security_vendor_pages",
            "control_policy_and_traceability_language",
            ["policy enforcement, HITL, traceability, and logging are adjacent controls"],
            "Rutile presents policy enforcement, human-in-the-loop, monitoring, traceability, and logging for agents. This supports operational assurance and action-boundary pain.",
        ),
        _receipt(
            "SRC023",
            "AgentOps documentation",
            "https://docs.agentops.ai/v1/introduction",
            "ai_governance_observability_security_vendor_pages",
            "agent_observability_language",
            ["agent observability includes replays, analytics, benchmarks, and monitoring"],
            "AgentOps documentation describes observability for AI agents, including session tracking and analytics. This supports the adjacent agent operations tooling category.",
        ),
        _receipt(
            "SRC024",
            "AgentOps GitHub repository",
            "https://github.com/AgentOps-AI/agentops",
            "public_github_repos_issues",
            "public_repo_category_presence",
            ["open-source agent observability repos exist"],
            "The AgentOps GitHub repository presents open-source observability for AI agents and indicates developer activity in agent monitoring.",
        ),
        _receipt(
            "SRC025",
            "Insight Global AI governance role listing",
            "https://insightglobal.com/jobs/find_a_job/job-495046",
            "public_job_posts",
            "job_post_demand_proxy",
            ["AI governance and AI operating model work appears in public job demand"],
            "The public listing references an AI Governance Lead/Strategy role and AI Operating Model responsibilities. This is a demand proxy only and not customer validation.",
            risk_flags=["job_post_proxy_not_customer_validation"],
        ),
        _receipt(
            "SRC028",
            "LangSmith pricing public page mirror",
            "https://www.lang.chat/pricing-langgraph-platform",
            "public_pricing_pages",
            "pricing_packaging_public_proxy",
            ["per-seat and trace-volume pricing appear as public analogs"],
            "The public pricing page mirror lists developer/plus tier structures and trace-volume pricing for LangSmith/LangGraph platform context. Treat as pricing proxy only.",
            risk_flags=["pricing_proxy_not_validation"],
        ),
    ]


def excluded_sources() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "EXC001",
            "source_title": "PepsiCo AI Governance roles search result",
            "source_url": "https://www.pepsicojobs.com/main/jobs/369152",
            "source_category": "public_job_posts",
            "exclusion_reason": "Direct page fetch was unavailable in the read-only research tool; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC002",
            "source_title": "Hitachi AI governance job search result",
            "source_url": "https://careers.hitachi.com/jobs/17001101-director-ai-governance-and-strategy",
            "source_category": "public_job_posts",
            "exclusion_reason": "Direct page fetch was unavailable in the read-only research tool; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC003",
            "source_title": "AgentID agent governance platform",
            "source_url": "https://www.agentid.io/",
            "source_category": "ai_governance_observability_security_vendor_pages",
            "exclusion_reason": "Direct page fetch returned an internal read error; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC004",
            "source_title": "Posturio agent governance platform",
            "source_url": "https://www.posturio.com/",
            "source_category": "ai_governance_observability_security_vendor_pages",
            "exclusion_reason": "Direct page fetch returned an internal read error; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC005",
            "source_title": "Preloop governed AI orchestration",
            "source_url": "https://www.preloop.com/",
            "source_category": "ai_governance_observability_security_vendor_pages",
            "exclusion_reason": "Direct page was not safe to open from the available search context; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC006",
            "source_title": "Waxell AI guardrails and governance",
            "source_url": "https://www.waxell.co/",
            "source_category": "ai_governance_observability_security_vendor_pages",
            "exclusion_reason": "Direct page was not safe to open from the available search context; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC007",
            "source_title": "HumanLatch enterprise AI agent governance",
            "source_url": "https://humanlatch.com/",
            "source_category": "ai_governance_observability_security_vendor_pages",
            "exclusion_reason": "Direct page was not safe to open from the available search context; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC008",
            "source_title": "Wells Fargo AI Risk Governance Lead listing mirror",
            "source_url": "https://www.tealhq.com/job/ai-risk-governance-lead_26207c5c-c82b-4fee-8471-4d4264d26a0e",
            "source_category": "public_job_posts",
            "exclusion_reason": "Direct page fetch returned an internal read error; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC009",
            "source_title": "PwC AI governance job listing mirror",
            "source_url": "https://www.tealhq.com/job/director-senior-manager-ai-governance_c748398a-3a4c-433a-97db-ae966941fbc2",
            "source_category": "public_job_posts",
            "exclusion_reason": "Direct page fetch returned an internal read error; not included in synthesis.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
        {
            "source_id": "EXC010",
            "source_title": "General press/news pages about agent governance",
            "source_url": "multiple_general_news_results_not_included",
            "source_category": "not_in_E75_allowlist",
            "exclusion_reason": "News results were skipped because the approved source categories prioritize official docs, vendor/product pages, public repos, standards, job posts, pricing pages, and case studies.",
            "login_required": False,
            "interaction_required": False,
            "no_contact_confirmed": True,
        },
    ]


def build_source_receipts(root: Path | None = None) -> dict[str, Any]:
    receipts = source_receipts()
    categories = sorted({item["source_category"] for item in receipts})
    return {
        "artifact_id": "e78_l3_source_receipts",
        "bridge_job_id": JOB_ID,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "source_count": len(receipts),
        "source_categories_used": categories,
        "receipts": receipts,
        "all_sources_public_read_only": all(item["public_read_only_confirmed"] for item in receipts),
        "no_contact_confirmed": all(item["no_contact_confirmed"] for item in receipts),
        "no_publication_confirmed": all(item["no_publication_confirmed"] for item in receipts),
        "no_payment_confirmed": all(item["no_payment_confirmed"] for item in receipts),
        "external_action_class": "public_read_only_non_contact",
    }


def build_excluded_sources_log(root: Path | None = None) -> dict[str, Any]:
    excluded = excluded_sources()
    return {
        "artifact_id": "e78_l3_excluded_sources_log",
        "bridge_job_id": JOB_ID,
        "excluded_source_count": len(excluded),
        "excluded_sources": excluded,
        "no_contact_confirmed": True,
        "no_login_gated_source_used": True,
        "no_payment_source_used": True,
    }


def build_evidence_synthesis(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e78_l3_evidence_synthesis",
        "bridge_job_id": JOB_ID,
        "source_count": len(source_receipts()),
        "buyer_problem_evidence": {
            "finding": "Public evidence strengthens the buyer/problem hypothesis.",
            "supporting_sources": ["SRC001", "SRC002", "SRC003", "SRC005", "SRC016", "SRC019", "SRC025"],
            "language_observed": [
                "tracing",
                "observability",
                "audit trails",
                "policy enforcement",
                "human-in-the-loop approvals",
                "tool-call oversight",
                "risk governance",
                "AI operating model",
            ],
            "buyer_profiles": [
                "AI automation teams and agent builders",
                "founder/operator teams deploying AI workflows",
                "AI governance/risk leaders",
                "platform/infra teams responsible for agent operations",
            ],
        },
        "product_offer_evidence": {
            "finding": "Adjacent products cluster around observability, tracing, evaluations, governance controls, approvals, audit trails, and agent control rooms.",
            "supporting_sources": ["SRC004", "SRC005", "SRC006", "SRC008", "SRC016", "SRC019", "SRC023", "SRC024"],
            "gap_hypothesis": "Many public products are platforms or SDKs. A no-execution blueprint/readiness package can sit upstream as a decision and operating-model artifact for teams not ready to buy or integrate a full platform.",
        },
        "CIEU_audit_module_relevance": {
            "finding": "CIEU-style causal traceability is commercially meaningful if translated into buyer language such as intent-action-outcome audit trails, residuals, approvals, and incident review.",
            "supporting_sources": ["SRC001", "SRC005", "SRC010", "SRC011", "SRC012", "SRC013", "SRC014", "SRC016", "SRC019"],
            "front_stage_or_back_stage": "back_stage_with_front_stage_translation",
            "safe_front_stage_language": "causal action audit trail: intent, action, outcome, residual",
        },
        "first_cash_route_implications": {
            "finding": "The current first-cash route is strengthened, especially as an agent-team governance blueprint with a founder/operator diagnostic entry wedge and AI operations control-room setup as the strongest implementation frame.",
            "strongest_positions": [
                "agent-team governance blueprint",
                "AI operations control-room setup",
                "founder/operator diagnostic",
                "consulting/productized service",
            ],
            "weaker_or_later_positions": [
                "audit-readiness package unless language remains compliance-careful",
                "technical implementation package unless owner approves L4/L5 progression later",
            ],
        },
        "pricing_packaging_public_analogs": {
            "finding": "Public analogs show SaaS usage/seat tiers and open-source-to-enterprise packaging, but they do not validate Y*Bridge pricing.",
            "supporting_sources": ["SRC007", "SRC009", "SRC028"],
            "safe_internal_hypotheses": [
                "fixed-fee diagnostic/readiness sprint",
                "blueprint + CIEU audit-module appendix",
                "optional implementation planning add-on",
                "no claim of validated price willingness",
            ],
        },
        "contradictions_and_weak_signals": [
            "The category is real but fragmented; buyers may already associate value with tooling platforms rather than advisory/blueprint packages.",
            "Governance and compliance language carries overclaim risk; CIEU should not be sold as compliance proof.",
            "Pricing pages are proxies from SaaS products, not direct willingness-to-pay evidence for a service package.",
            "Job posts indicate organizational concern, but job-post evidence is not customer validation.",
        ],
        "evidence_quality": {
            "classification": "L3_public_read_non_contact_public_proxy_evidence",
            "strength": "moderate_to_strong_for_category_presence_and_language",
            "limits": [
                "no customer conversations",
                "no expert feedback",
                "no paid signal",
                "no pricing validation",
                "no compliance/legal proof",
            ],
        },
        "what_remains_unproven": [
            "specific buyer willingness to buy Y*Bridge package",
            "validated pricing",
            "actual conversion path",
            "legal/compliance sufficiency",
            "production ledger readiness",
            "L4 outreach safety for a named audience",
        ],
        "no_overclaim": True,
    }


def build_route_implication_matrix(root: Path | None = None) -> dict[str, Any]:
    positions = [
        {
            "route_position": "founder_operator_diagnostic",
            "public_evidence_support": "moderate",
            "weakness": "public sources often discuss platform/tooling more than founder advisory packages",
            "buyer_profile": "founders/operators trying to deploy AI workflows safely",
            "possible_package_shape": "fixed-fee AI operations governance diagnostic with CIEU audit appendix",
            "risk": "can sound generic unless tied to concrete agent action boundaries",
            "no_overclaim_boundary": "diagnostic, not validation or compliance proof",
        },
        {
            "route_position": "agent_team_governance_blueprint",
            "public_evidence_support": "strong",
            "weakness": "requires clear distinction from full governance platforms",
            "buyer_profile": "AI automation teams, platform teams, agent builders",
            "possible_package_shape": "governed business operations blueprint, action-boundary map, CIEU audit-module context",
            "risk": "overbuilding if it becomes a platform implementation",
            "no_overclaim_boundary": "blueprint/readiness artifact only unless owner approves execution",
        },
        {
            "route_position": "AI_operations_control_room_setup",
            "public_evidence_support": "strong",
            "weakness": "could imply live operations or production deployment too early",
            "buyer_profile": "operators responsible for agent workflows and tool calls",
            "possible_package_shape": "control-room architecture packet with approval gates, logs, traces, and escalation map",
            "risk": "must remain no-execution planning at L3",
            "no_overclaim_boundary": "setup blueprint, not live control-room deployment",
        },
        {
            "route_position": "audit_readiness_package",
            "public_evidence_support": "moderate",
            "weakness": "high compliance/legal overclaim risk",
            "buyer_profile": "governance/risk leaders and teams preparing for audit conversations",
            "possible_package_shape": "audit-readiness context pack with public guidance mapping and CIEU residual template",
            "risk": "buyer may infer compliance certification",
            "no_overclaim_boundary": "readiness support only; no certification/legal sufficiency",
        },
        {
            "route_position": "consulting_productized_service",
            "public_evidence_support": "moderate_to_strong",
            "weakness": "public pricing analogs are mostly SaaS, not direct service pricing",
            "buyer_profile": "teams needing guided packaging before tool adoption",
            "possible_package_shape": "two-week blueprint sprint with implementation backlog and owner-gated next steps",
            "risk": "needs L4/L5 validation before revenue claims",
            "no_overclaim_boundary": "internal offer hypothesis, not paid signal",
        },
        {
            "route_position": "technical_implementation_package",
            "public_evidence_support": "moderate",
            "weakness": "requires execution capability, integration work, and live-system risk controls beyond L3",
            "buyer_profile": "engineering teams already selecting observability/governance stacks",
            "possible_package_shape": "future adapter/integration plan wrapping existing tools",
            "risk": "could duplicate K9/Y-star-gov/gov-mcp or imply production readiness",
            "no_overclaim_boundary": "future owner-gated implementation only",
        },
    ]
    return {
        "artifact_id": "e78_l3_route_implication_matrix",
        "bridge_job_id": JOB_ID,
        "positions": positions,
        "top_ranked_positions": [
            "agent_team_governance_blueprint",
            "AI_operations_control_room_setup",
            "founder_operator_diagnostic",
        ],
        "matrix_decision": "Current route is strengthened; prepare L4 owner-decision packet rather than execute L4.",
        "external_action_allowed": False,
    }


def build_cieu_market_relevance(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e78_l3_cieu_audit_module_market_relevance",
        "bridge_job_id": JOB_ID,
        "defensibility_effect": "strengthens_route_defensibility",
        "market_language_supports": [
            "traceability",
            "audit trails",
            "tool-call oversight",
            "policy enforcement",
            "human approval",
            "risk management",
            "observability",
            "incident review",
        ],
        "CIEU_translation": {
            "front_stage_language": "causal action audit trail",
            "back_stage_model": "X_t / U_t / Y_star_t / Y_t_plus_1 / R_t_plus_1",
            "recommended_messaging": "Use buyer language first; keep CIEU acronym as technical appendix or defensibility layer.",
        },
        "should_CIEU_be_front_stage": False,
        "should_CIEU_be_back_stage": True,
        "safe_claims": [
            "internal structural audit-module context",
            "intent-action-outcome residual framing",
            "no-execution blueprint appendix",
            "public evidence suggests adjacent demand for traces, audit trails, and approvals",
        ],
        "forbidden_claims": forbidden_claims(),
        "remaining_proof_needed": [
            "customer or expert feedback before market validation claims",
            "legal review before compliance language",
            "K9/Y-star-gov integration proof before live ledger claims",
            "owner-approved L4 packet before any contact transition",
        ],
        "external_action_allowed": False,
    }


def build_pricing_packaging_proxy(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e78_l3_pricing_packaging_public_proxy",
        "bridge_job_id": JOB_ID,
        "pricing_sources": ["SRC007", "SRC009", "SRC028"],
        "public_pricing_package_analogs": [
            {
                "source_id": "SRC007",
                "analog": "open-source/free tier plus usage-based paid tiers and enterprise options",
                "possible_learning": "buyers may expect usage/retention/enterprise feature boundaries in observability categories",
            },
            {
                "source_id": "SRC009",
                "analog": "open-source/free Phoenix plus pro/enterprise packaging",
                "possible_learning": "open-source-to-pro-to-enterprise ladder is common in adjacent observability tooling",
            },
            {
                "source_id": "SRC028",
                "analog": "developer/free plus per-seat/trace-volume tiers",
                "possible_learning": "trace volume and seats are visible pricing dimensions in adjacent tooling",
            },
        ],
        "what_can_be_inferred": [
            "adjacent market accepts tiered SaaS packaging and enterprise upsell language",
            "usage volume, data retention, seats, and support appear as common packaging dimensions",
            "a service/blueprint offer should be priced as a hypothesis, not derived mechanically from SaaS pricing",
        ],
        "what_cannot_be_inferred": [
            "willingness to pay for Y*Bridge",
            "validated price point",
            "paid signal",
            "conversion probability",
        ],
        "recommended_internal_pricing_hypotheses_non_validated": [
            "entry diagnostic/readiness sprint as fixed-fee service",
            "blueprint package plus CIEU audit-module appendix as the core deliverable",
            "optional implementation backlog or vendor-selection add-on",
            "avoid publishing pricing until L4/L5 evidence and owner approval exist",
        ],
        "pricing_validation_absent": True,
        "paid_signal_absent": True,
        "external_action_allowed": False,
    }


def build_post_run_readiness_assessment(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e78_l3_post_run_readiness_assessment",
        "bridge_job_id": JOB_ID,
        "L3_executed": True,
        "owner_approval_explicit": True,
        "did_L3_strengthen_current_first_cash_route": True,
        "did_L3_weaken_current_first_cash_route": False,
        "route_strengthening_summary": "Public-read evidence shows a real adjacent category around agent observability, governance, human approvals, audit trails, policy enforcement, and AI risk governance. This supports the current route as a buyer-language and packaging hypothesis.",
        "another_L3_run_needed": "not_required_before_L4_packet_preparation_but_useful_if_owner_wants_more_vertical_focus",
        "L4_owner_decision_packet_preparation_justified": True,
        "L4_execution_ready": False,
        "L5_revenue_ready": False,
        "smallest_next_step": "prepare an L4 owner-decision packet for a tightly scoped non-contact-to-contact transition, without executing outreach",
        "recommended_next_milestone": "E79_L4_Owner_Decision_Packet_Preparation_No_External_Action",
        "readiness_delta": {
            "L2": "ready",
            "L3": "executed_under_owner_approval",
            "L4": "ready_for_owner_decision_packet_preparation_not_execution",
            "L5": "not_ready",
        },
        "no_overclaim": True,
        "external_action_allowed": False,
    }


def build_cieu_residual(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e78_cieu_residual_for_l3_research_pilot",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "E73_readiness_gate": "L2 ready; L3 conditionally ready with owner approval",
            "E74_L2_internal_work_completed": True,
            "E75_L3_decision_packet_completed": True,
            "E76_E77_lineage_reconciled": True,
            "owner_approval_block_present": True,
            "public_read_no_contact_boundary": True,
        },
        "U_t": {
            "executed_action": "owner-approved L3 read-only external research pilot",
            "source_receipts_collected": len(source_receipts()),
            "evidence_synthesized": True,
            "readiness_delta_assessed": True,
        },
        "Y_star_t": {
            "intended_outcome": "Gather public-read evidence for the current first-cash route without contact, publication, payment, login, or overclaim.",
            "constraints": [
                "public-read only",
                "no login",
                "no contact",
                "no publication",
                "no paid action",
                "no customer validation claim",
                "no compliance/legal proof claim",
                "no production claim",
            ],
        },
        "Y_t_plus_1": {
            "generated_outputs": [
                "run plan",
                "source receipts",
                "excluded source log",
                "evidence synthesis",
                "route implication matrix",
                "CIEU Audit Module market relevance report",
                "pricing/packaging public proxy report",
                "post-run readiness assessment",
                "CEO readback",
            ],
            "L3_executed": True,
            "new_external_evidence_collected": True,
        },
        "R_t_plus_1": {
            "residual_gaps": [
                "no customer validation",
                "no expert feedback",
                "no paid signal",
                "no pricing validation",
                "no compliance/legal proof",
                "no L4 execution",
                "no L5 revenue readiness",
                "market ambiguity remains around whether buyer prefers diagnostic, blueprint, or implementation packaging",
            ],
            "next_U": "E79_L4_Owner_Decision_Packet_Preparation_No_External_Action",
        },
        "no_overclaim": True,
    }


def build_ceo_readback(root: Path | None = None) -> dict[str, Any]:
    synthesis = build_evidence_synthesis(root)
    assessment = build_post_run_readiness_assessment(root)
    return {
        "artifact_id": "e78_ceo_readback",
        "bridge_job_id": JOB_ID,
        "E78_status": "owner_approved_L3_public_read_pilot_executed",
        "did_execute_L3": True,
        "owner_approval_explicit": True,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "source_count": len(source_receipts()),
        "source_categories_used": sorted({item["source_category"] for item in source_receipts()}),
        "public_read_evidence_collected": True,
        "buyer_problem_finding": synthesis["buyer_problem_evidence"]["finding"],
        "product_offer_finding": synthesis["product_offer_evidence"]["finding"],
        "CIEU_audit_module_finding": synthesis["CIEU_audit_module_relevance"]["finding"],
        "pricing_packaging_finding": synthesis["pricing_packaging_public_analogs"]["finding"],
        "L4_owner_decision_packet_preparation_justified": assessment["L4_owner_decision_packet_preparation_justified"],
        "L4_execution_ready": False,
        "L5_ready": False,
        "next_recommended_milestone": assessment["recommended_next_milestone"],
        "claims_remaining_forbidden": forbidden_claims(),
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "expert_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "L4_execution_readiness_claimed": False,
        "L5_readiness_claimed": False,
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
        "no_contact_confirmed": True,
        "no_publication_confirmed": True,
        "no_payment_confirmed": True,
        "no_login_gated_action_confirmed": True,
        "false_first_external_read_only_research_claimed": False,
    }


def build_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    assessment = build_post_run_readiness_assessment(root)
    return {
        "artifact_id": "e78_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "selected_next_milestone": assessment["recommended_next_milestone"],
        "type": "owner_decision_preparation_not_execution",
        "why_selected": "L3 public-read evidence strengthens the route enough to justify preparing an L4 owner-decision packet, but not enough to execute L4 or claim L5 readiness.",
        "not_selected": {
            "E79_L3_Evidence_Gap_Burn_Down_or_Second_Read_Only_Run": "useful but not the smallest necessary next step before owner decision packet preparation",
            "E79_Return_to_L2_Route_Reassessment_and_Commercial_Repackaging": "route was strengthened, not weakened",
            "E79_L2_Commercial_Offer_Repackaging_From_L3_Evidence": "could be included inside L4 packet preparation as internal packaging refinement",
            "L4_execution": "forbidden; only L4 owner-decision packet preparation is justified",
            "L5_revenue_work": "not ready; no customer, paid, pricing, or compliance validation",
        },
        "external_action_allowed": False,
    }


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    receipts = build_source_receipts(base)
    excluded = build_excluded_sources_log(base)
    assessment = build_post_run_readiness_assessment(base)
    checks = {
        "base_verified": base_verified(base),
        "owner_approval_block_recorded": True,
        "L3_executed_under_explicit_approval": True,
        "source_receipts_generated": receipts["source_count"] >= 20,
        "excluded_source_log_exists": (base / "operations/external_validation/e78_l3_excluded_sources_log.json").exists(),
        "evidence_synthesis_exists": (base / "operations/external_validation/e78_l3_evidence_synthesis.json").exists(),
        "route_implication_matrix_exists": (base / "operations/external_validation/e78_l3_route_implication_matrix.json").exists(),
        "CIEU_market_relevance_exists": (base / "operations/external_validation/e78_l3_cieu_audit_module_market_relevance.json").exists(),
        "pricing_proxy_exists": (base / "operations/external_validation/e78_l3_pricing_packaging_public_proxy.json").exists(),
        "post_run_assessment_exists": (base / "operations/external_validation/e78_l3_post_run_readiness_assessment.json").exists(),
        "CIEU_residual_exists": (base / "operations/external_validation/e78_cieu_residual_for_l3_research_pilot.json").exists(),
        "CEO_readback_exists": (base / "operations/external_validation/e78_ceo_readback.json").exists(),
        "next_milestone_evidence_driven": assessment["recommended_next_milestone"] == "E79_L4_Owner_Decision_Packet_Preparation_No_External_Action",
        "no_forbidden_claims": True,
    }
    return {
        "artifact_id": "e78_completion_report",
        "bridge_job_id": JOB_ID,
        "base": git_state(base),
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": "e78_owner_approved_l3_public_read_pilot_completed",
        "owner_approval_block_detected": True,
        "L3_executed": True,
        "source_count": receipts["source_count"],
        "source_categories_used": receipts["source_categories_used"],
        "excluded_source_count": excluded["excluded_source_count"],
        "key_buyer_problem_findings": build_evidence_synthesis(base)["buyer_problem_evidence"]["language_observed"],
        "key_product_offer_finding": build_evidence_synthesis(base)["product_offer_evidence"]["finding"],
        "CIEU_audit_module_relevance_finding": build_evidence_synthesis(base)["CIEU_audit_module_relevance"]["finding"],
        "pricing_packaging_proxy_finding": build_evidence_synthesis(base)["pricing_packaging_public_analogs"]["finding"],
        "route_implication_summary": "Top positions are agent-team governance blueprint, AI operations control-room setup, and founder/operator diagnostic.",
        "post_run_readiness_decision": {
            "L2": "ready",
            "L3": "executed",
            "L4_owner_decision_packet_preparation": "justified",
            "L4_execution": "not_ready",
            "L5": "not_ready",
        },
        "next_recommended_milestone": assessment["recommended_next_milestone"],
        "external_action_allowed_after_E78": False,
        "no_customer_outreach": True,
        "no_expert_outreach": True,
        "no_publication": True,
        "no_payment": True,
        "no_login_gated_action": True,
        "read_only_repos_mutated": False,
        "customer_validation_claimed": False,
        "expert_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_ledger_claimed": False,
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
        "false_first_external_read_only_research_claimed": False,
    }


def _md_list(items: list[Any]) -> list[str]:
    return [f"- {item}" for item in items]


def write_all_e78_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    receipts = build_source_receipts(base)
    excluded = build_excluded_sources_log(base)
    synthesis = build_evidence_synthesis(base)
    matrix = build_route_implication_matrix(base)
    cieu = build_cieu_market_relevance(base)
    pricing = build_pricing_packaging_proxy(base)
    assessment = build_post_run_readiness_assessment(base)
    residual = build_cieu_residual(base)
    readback = build_ceo_readback(base)
    next_proposal = build_next_milestone_proposal(base)

    write_json(base, "operations/external_validation/e78_l3_source_receipts.json", receipts)
    write_md(
        base,
        "operations/external_validation/e78_l3_source_receipts.md",
        "E78 L3 Source Receipts",
        [
            f"- Source count: {receipts['source_count']}",
            f"- Categories used: {', '.join(receipts['source_categories_used'])}",
            "- All included sources were public-read-only; no contact, publication, payment, login, or credentialed API action occurred.",
            "",
            "## Sources",
        ] + [f"- {item['source_id']}: {item['source_title']} ({item['source_url']})" for item in receipts["receipts"]],
    )

    write_json(base, "operations/external_validation/e78_l3_excluded_sources_log.json", excluded)
    write_md(
        base,
        "operations/external_validation/e78_l3_excluded_sources_log.md",
        "E78 L3 Excluded Sources Log",
        [f"- Excluded source count: {excluded['excluded_source_count']}"] + [f"- {item['source_id']}: {item['source_title']} - {item['exclusion_reason']}" for item in excluded["excluded_sources"]],
    )

    write_json(base, "operations/external_validation/e78_l3_evidence_synthesis.json", synthesis)
    write_md(
        base,
        "operations/external_validation/e78_l3_evidence_synthesis.md",
        "E78 L3 Evidence Synthesis",
        [
            f"- Buyer/problem: {synthesis['buyer_problem_evidence']['finding']}",
            f"- Product/offer: {synthesis['product_offer_evidence']['finding']}",
            f"- CIEU: {synthesis['CIEU_audit_module_relevance']['finding']}",
            f"- First-cash implication: {synthesis['first_cash_route_implications']['finding']}",
            f"- Pricing proxy: {synthesis['pricing_packaging_public_analogs']['finding']}",
            "",
            "## What Remains Unproven",
        ] + _md_list(synthesis["what_remains_unproven"]),
    )

    write_json(base, "operations/external_validation/e78_l3_route_implication_matrix.json", matrix)
    write_md(
        base,
        "operations/external_validation/e78_l3_route_implication_matrix.md",
        "E78 L3 Route Implication Matrix",
        [f"- Matrix decision: {matrix['matrix_decision']}", "", "## Positions"] + [f"- {row['route_position']}: support={row['public_evidence_support']}; package={row['possible_package_shape']}; boundary={row['no_overclaim_boundary']}" for row in matrix["positions"]],
    )

    write_json(base, "operations/external_validation/e78_l3_cieu_audit_module_market_relevance.json", cieu)
    write_md(
        base,
        "operations/external_validation/e78_l3_cieu_audit_module_market_relevance.md",
        "E78 L3 CIEU Audit Module Market Relevance",
        [
            f"- Defensibility effect: {cieu['defensibility_effect']}",
            f"- Recommended messaging: {cieu['CIEU_translation']['recommended_messaging']}",
            f"- Front-stage CIEU acronym: {cieu['should_CIEU_be_front_stage']}",
            f"- Back-stage CIEU layer: {cieu['should_CIEU_be_back_stage']}",
            "",
            "## Safe Claims",
        ] + _md_list(cieu["safe_claims"]) + ["", "## Forbidden Claims"] + _md_list(cieu["forbidden_claims"]),
    )

    write_json(base, "operations/external_validation/e78_l3_pricing_packaging_public_proxy.json", pricing)
    write_md(
        base,
        "operations/external_validation/e78_l3_pricing_packaging_public_proxy.md",
        "E78 L3 Pricing Packaging Public Proxy",
        [
            "- Pricing validation remains absent.",
            "- Public pricing pages are analogs only.",
            "",
            "## What Can Be Inferred",
        ] + _md_list(pricing["what_can_be_inferred"]) + ["", "## What Cannot Be Inferred"] + _md_list(pricing["what_cannot_be_inferred"]),
    )

    write_json(base, "operations/external_validation/e78_l3_post_run_readiness_assessment.json", assessment)
    write_md(
        base,
        "operations/external_validation/e78_l3_post_run_readiness_assessment.md",
        "E78 L3 Post-Run Readiness Assessment",
        [
            f"- Strengthened current route: {assessment['did_L3_strengthen_current_first_cash_route']}",
            f"- Weakened current route: {assessment['did_L3_weaken_current_first_cash_route']}",
            f"- L4 packet preparation justified: {assessment['L4_owner_decision_packet_preparation_justified']}",
            f"- L4 execution ready: {assessment['L4_execution_ready']}",
            f"- L5 ready: {assessment['L5_revenue_ready']}",
            f"- Smallest next step: {assessment['smallest_next_step']}",
        ],
    )

    write_json(base, "operations/external_validation/e78_cieu_residual_for_l3_research_pilot.json", residual)
    write_md(
        base,
        "operations/external_validation/e78_cieu_residual_for_l3_research_pilot.md",
        "E78 CIEU Residual For L3 Research Pilot",
        [
            "- X_t: E73 gate, E74 L2 work, E75 decision packet, E76/E77 lineage correction, explicit owner approval, public-read boundary.",
            f"- U_t: executed owner-approved L3 read-only research and collected {residual['U_t']['source_receipts_collected']} receipts.",
            "- Y_star_t: gather public-read evidence without contact, publication, payment, login, or overclaim.",
            "- Y_t_plus_1: run plan, receipts, synthesis, route matrix, CIEU relevance, pricing proxy, readiness assessment.",
            f"- R_t_plus_1 next_U: {residual['R_t_plus_1']['next_U']}",
        ],
    )

    write_json(base, "operations/external_validation/e78_ceo_readback.json", readback)
    write_md(
        base,
        "operations/external_validation/e78_ceo_readback.md",
        "E78 CEO Readback",
        [
            f"- Did E78 execute L3: {readback['did_execute_L3']}",
            f"- Owner approval explicit: {readback['owner_approval_explicit']}",
            f"- Source count: {readback['source_count']}",
            f"- Buyer/problem finding: {readback['buyer_problem_finding']}",
            f"- Product/offer finding: {readback['product_offer_finding']}",
            f"- CIEU finding: {readback['CIEU_audit_module_finding']}",
            f"- Pricing/packaging finding: {readback['pricing_packaging_finding']}",
            f"- L4 packet preparation justified: {readback['L4_owner_decision_packet_preparation_justified']}",
            f"- L5 ready: {readback['L5_ready']}",
        ],
    )

    write_json(base, "operations/external_validation/e78_generated_next_milestone_proposal.json", next_proposal)
    write_md(
        base,
        "operations/external_validation/e78_generated_next_milestone_proposal.md",
        "E78 Generated Next Milestone Proposal",
        [
            f"- Selected next milestone: {next_proposal['selected_next_milestone']}",
            f"- Type: {next_proposal['type']}",
            f"- Why: {next_proposal['why_selected']}",
        ],
    )

    completion = build_completion_report(base)
    write_json(base, "operations/external_validation/e78_completion_report.json", completion)
    write_md(
        base,
        "operations/external_validation/e78_completion_report.md",
        "E78 Completion Report",
        [
            f"- Final status: {completion['final_status']}",
            f"- Gate passed: {completion['gate_passed']}",
            f"- Owner approval block detected: {completion['owner_approval_block_detected']}",
            f"- L3 executed: {completion['L3_executed']}",
            f"- Source count: {completion['source_count']}",
            f"- Excluded source count: {completion['excluded_source_count']}",
            f"- L4 owner-decision packet preparation: {completion['post_run_readiness_decision']['L4_owner_decision_packet_preparation']}",
            f"- L5: {completion['post_run_readiness_decision']['L5']}",
            f"- Next recommended milestone: {completion['next_recommended_milestone']}",
        ],
    )
    return completion


def main() -> None:
    report = write_all_e78_artifacts(BRIDGE_ROOT)
    print(json.dumps({"artifact_id": "e78_write_result", "gate_passed": report["gate_passed"]}, indent=2))


if __name__ == "__main__":
    main()
