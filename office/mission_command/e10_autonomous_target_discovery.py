from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class E10TargetDiscoveryRequest:
    mission_id: str
    top_offer: str
    target_segments_to_explore: List[str]
    search_queries: List[str]
    allowed_source_categories: List[str]
    budget: Dict[str, int]
    forbidden_actions: List[str]
    stop_conditions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E10DiscoverySourceSummary:
    source_id: str
    title: str
    url: str
    domain: str
    source_category: str
    segment_tags: List[str]
    summary: str
    signal_types: List[str]
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


TARGET_SEGMENTS = [
    "AI-heavy small teams",
    "technical founders building AI workflows",
    "teams hiring for AI ops / LLMOps / AI evaluation / automation",
    "teams using agent frameworks or AI workflow tooling",
    "open-source teams/projects needing governance/support",
    "incident-heavy teams or reliability teams adopting AI",
    "AI consultants/agencies needing governance layer",
    "startup ops teams using no-code/automation tools",
]


SEARCH_QUERIES = [
    "AI ops workflow implementation pain startup",
    "LLMOps evaluation workflow startup hiring",
    "AI automation operations founder pain",
    "agentic workflow production evaluation tools",
    "AI agent governance startup team",
    "AI team hiring LLMOps evaluation observability",
    "AI workflow automation agency pricing",
    "startup AI operations implementation consultant",
    "agent workflow bottleneck founder",
    "AI tool sprawl operations startup",
    "GitHub issue AI agent workflow governance",
    "AI incident postmortem agent workflow",
    "LangSmith pricing tracing evaluation agents",
    "Langfuse open source LLM engineering platform observability evaluation",
    "AI automation agency n8n workflow pricing",
    "agentic AI consulting governance implementation",
    "AI agent control plane governance open source",
    "LLMOps engineer job observability governance evaluation",
    "AI operations consulting implementation fixed price",
    "workflow automation agency n8n AI agents",
]


def build_e10_target_discovery_request() -> E10TargetDiscoveryRequest:
    return E10TargetDiscoveryRequest(
        mission_id="e10_autonomous_buyer_discovery",
        top_offer="48h AI Ops Operating Room Blueprint",
        target_segments_to_explore=TARGET_SEGMENTS,
        search_queries=SEARCH_QUERIES,
        allowed_source_categories=[
            "public company pages",
            "public job postings",
            "public product docs",
            "public pricing pages",
            "public GitHub repos/issues/discussions",
            "public blogs",
            "public community pages",
            "public partner/agency pages",
            "public conference/session pages",
            "public marketplace/app pages",
        ],
        budget={"max_search_queries": 50, "max_pages_read": 100, "max_domains": 50, "max_runtime_seconds": 900},
        forbidden_actions=[
            "customer_contact",
            "sending_messages",
            "email",
            "dm",
            "publication",
            "form_submission",
            "payment",
            "account_creation",
            "login",
            "scraping_private_data",
            "paywall_bypass",
            "reading_or_printing_secrets",
            "collecting_personal_sensitive_data",
            "core_db_writeback",
            "obligation_registration",
            "coo_invention",
        ],
        stop_conditions=[
            "budget exhausted",
            "login or paywall required",
            "source requires contact/form/account creation",
            "candidate would require private personal contact scraping",
            "at least 20 safe candidates across at least 5 segments identified",
        ],
    )


def _source(
    source_id: str,
    title: str,
    url: str,
    domain: str,
    category: str,
    segments: List[str],
    summary: str,
    signal_types: List[str],
) -> E10DiscoverySourceSummary:
    return E10DiscoverySourceSummary(
        source_id=source_id,
        title=title,
        url=url,
        domain=domain,
        source_category=category,
        segment_tags=segments,
        summary=summary,
        signal_types=signal_types,
        limitations="Public read-only evidence; not customer validation, not contact approval, and not private contact information.",
    )


def load_or_run_e10_target_discovery() -> Dict[str, Any]:
    sources = [
        _source("src_langsmith_pricing", "LangSmith Plans and Pricing", "https://www.langchain.com/pricing", "langchain.com", "public pricing pages", ["teams using agent frameworks or AI workflow tooling"], "LangSmith pricing describes tracing, online/offline evals, monitoring, alerting, human feedback queues, deployment, and startup pricing.", ["budget", "tool_stack_complexity", "governance_safety"]),
        _source("src_langfuse_docs", "Langfuse Overview", "https://langfuse.com/docs", "langfuse.com", "public product docs", ["teams using agent frameworks or AI workflow tooling", "open-source teams/projects needing governance/support"], "Langfuse positions observability, prompt management, evaluation, production health, and collaborative iteration as an integrated LLM engineering loop.", ["pain", "tool_stack_complexity", "governance_safety"]),
        _source("src_arize_phoenix", "Arize Phoenix / Arize LLM Observability", "https://arize.com/", "arize.com", "public product pages", ["teams using agent frameworks or AI workflow tooling"], "Arize emphasizes agent evaluation, tracing, open standards, debugging, and production observability.", ["tool_stack_complexity", "governance_safety", "existing_alternative"]),
        _source("src_braintrust", "Braintrust AI observability platform", "https://www.braintrust.dev/", "braintrust.dev", "public product pages", ["teams using agent frameworks or AI workflow tooling"], "Braintrust describes production traces, evals, prompt/model comparisons, quality monitoring, and blocking bad releases.", ["pain", "tool_stack_complexity", "governance_safety"]),
        _source("src_humanloop_pricing", "Humanloop Pricing", "https://humanloop.com/pricing", "humanloop.com", "public pricing pages", ["AI-heavy small teams"], "Humanloop highlights evaluation, observability, prompt management, human review, enterprise security, SSO, VPC, and support.", ["budget", "governance_safety", "existing_alternative"]),
        _source("src_vellum_pricing", "Vellum Pricing Docs", "https://www.vellum.ai/docs/pricing", "vellum.ai", "public pricing pages", ["AI-heavy small teams"], "Vellum pricing docs discuss transparent credits, usage, and AI workflow platform costs.", ["budget", "existing_alternative"]),
        _source("src_zapier_pricing", "Zapier AI orchestration pricing", "https://zapier.com/pricing", "zapier.com", "public pricing pages", ["startup ops teams using no-code/automation tools"], "Zapier pricing describes AI orchestration, workflows, tables, forms, MCP, team/enterprise plans, and admin permissions.", ["budget", "tool_stack_complexity", "existing_alternative"]),
        _source("src_retool_pricing", "Retool Pricing", "https://retool.com/pricing", "retool.com", "public pricing pages", ["startup ops teams using no-code/automation tools"], "Retool pricing includes workflows, agents, permissions, audit logging, observability, evaluations, SSO, and enterprise support.", ["budget", "tool_stack_complexity", "governance_safety"]),
        _source("src_crewai_pricing", "CrewAI Pricing", "https://www.crewai.com/pricing", "crewai.com", "public pricing pages", ["teams using agent frameworks or AI workflow tooling"], "CrewAI pricing includes agentic workflows, executions, enterprise support, deployment, onboarding, training, and dedicated support.", ["budget", "tool_stack_complexity", "implementation_burden"]),
        _source("src_trm_llmops_job", "TRM Labs Senior MLOps Engineer, LLMOps", "https://jobs.ashbyhq.com/trm-labs/32c97568-5212-48f5-9eb2-caab1c8dec2a", "ashbyhq.com", "public job postings", ["teams hiring for AI ops / LLMOps / AI evaluation / automation"], "TRM Labs job posting mentions observability, governance, approval workflows, compliance checks, LLM/agent tools, regression testing, cost monitoring, and HITL workflows.", ["hiring_job", "urgency", "governance_safety", "tool_stack_complexity"]),
        _source("src_sumologic_llmops_job", "Sumo Logic Senior MLOps/LLMOps Engineer", "https://job-boards.greenhouse.io/sumologic/jobs/7584291", "greenhouse.io", "public job postings", ["teams hiring for AI ops / LLMOps / AI evaluation / automation"], "Sumo Logic job posting describes production-grade MLOps/LLMOps infrastructure for lifecycle, evaluation, deployment, monitoring, reliability, observability, and efficiency.", ["hiring_job", "urgency", "budget", "tool_stack_complexity"]),
        _source("src_tensorzero_job", "TensorZero Backend Engineering", "https://jobs.ashbyhq.com/tensorzero/6cf3673e-5377-4c22-9f0c-ebf27c8567b1", "ashbyhq.com", "public job postings", ["open-source teams/projects needing governance/support"], "TensorZero describes an open-source LLMOps platform with gateway, observability, optimization, evaluation, experimentation, and customers from startups to enterprises.", ["hiring_job", "tool_stack_complexity", "budget"]),
        _source("src_wotai", "WotAI AI Automation", "https://wotai.co/", "wotai.co", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "WotAI offers validated n8n workflow generation, production workflow expertise, and pricing tiers including agency/team scale.", ["budget", "implementation_burden", "existing_alternative"]),
        _source("src_botsquash", "BotSquash AI Automation Agency", "https://botsquash.com/", "botsquash.com", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "BotSquash markets n8n-first automation and AI systems with documentation, secure auth, maintainability, proposal in 24h, and typical operational outcomes.", ["pain", "implementation_burden", "contactability"]),
        _source("src_hgray", "Hgray AI Automation Agency", "https://www.hgray.agency/", "hgray.agency", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "Hgray lists n8n workflow development, automation consulting, process analysis, ROI assessment, implementation planning, training, and support.", ["budget", "implementation_burden", "contactability"]),
        _source("src_workflowwizard", "WorkflowWizard AI Automation Agency", "https://www.workflowwizard.dev/", "workflowwizard.dev", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "WorkflowWizard offers AI agents, n8n workflows, Apify scrapers, pricing tiers, support channels, and active workflow/node constraints.", ["budget", "implementation_burden", "contactability"]),
        _source("src_byteflows", "Byteflows Agentic AI Consultancy", "https://www.byteflows.com/", "byteflows.com", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "Byteflows helps teams move from demos to deployed agentic systems and explicitly includes AI Ops, governance, monitoring, guardrails, evaluation loops, and HITL controls.", ["pain", "governance_safety", "contactability"]),
        _source("src_opoclaw", "OpoClaw AI Automation Agency", "https://opoclaw.com/", "opoclaw.com", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "OpoClaw offers custom AI automations for agencies and small businesses with delivery-time and pricing claims.", ["budget", "implementation_burden", "contactability"]),
        _source("src_n8nlab", "N8N Lab Automation Agency", "https://n8nlab.io/", "n8nlab.io", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "N8N Lab describes enterprise-grade n8n workflows and AI agentic systems, hours saved, agents deployed, uptime, and industry targets.", ["pain", "implementation_burden", "contactability"]),
        _source("src_alicelabs", "Alice Labs AI Operations Consulting", "https://alicelabs.ai/en/ai-operations-consulting", "alicelabs.ai", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "Alice Labs offers AI operations consulting with discovery, architecture, integration, training, 90-day support, fixed price, and EU AI Act-native positioning.", ["budget", "governance_safety", "implementation_burden"]),
        _source("src_opsbridge", "OpsBridge AI", "https://www.opsbridgeai.com/", "opsbridgeai.com", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "OpsBridge AI builds workflow automation, data platforms, and intelligent systems for operations leaders and founders with practical AI roadmaps.", ["pain", "implementation_burden", "contactability"]),
        _source("src_tqa", "TQA Agentic AI Consulting", "https://tqa.ai/technology/agentic-ai/", "tqa.ai", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "TQA emphasizes agentic AI systems with traceability, control, human oversight, use-case validation, production-ready design, and support after launch.", ["governance_safety", "implementation_burden", "contactability"]),
        _source("src_perelyn", "Perelyn LLMOps Services", "https://www.perelyn.com/en/services/ai-operations/llmops", "perelyn.com", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "Perelyn offers LLMOps strategy, best practices, evaluation/testing, deployment, monitoring, compliance, and workflow integration.", ["governance_safety", "implementation_burden", "contactability"]),
        _source("src_dashclaw", "DashClaw Decision Infrastructure", "https://www.dashclaw.io/", "dashclaw.io", "public product/project pages", ["open-source teams/projects needing governance/support"], "DashClaw positions itself as an open-source policy firewall for AI agents that intercepts actions, enforces policies, requires approval, and records evidence.", ["governance_safety", "existing_alternative", "tool_stack_complexity"]),
        _source("src_orloj", "Orloj Agent Infrastructure as Code", "https://www.orloj.dev/", "orloj.dev", "public product/project pages", ["open-source teams/projects needing governance/support"], "Orloj offers YAML-defined workflows, policies, isolated tools, fail-closed governance, observability, and community/cloud paths.", ["governance_safety", "tool_stack_complexity", "existing_alternative"]),
        _source("src_pact5", "PACT5 Agent Coordination and Trust", "https://pact5.io/", "pact5.io", "public product/project pages", ["open-source teams/projects needing governance/support"], "PACT5 frames scoped authority, structured coordination, and human oversight for multi-agent AI systems.", ["governance_safety", "existing_alternative", "trust_gap"]),
        _source("src_govagentic", "Govagentic AI Governance Consulting", "https://govagentic.ai/", "govagentic.ai", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "Govagentic argues mid-market companies are deploying AI agents faster than legal, ops, and risk teams can govern and need audit trail ownership.", ["pain", "governance_safety", "contactability"]),
        _source("src_inteq", "Inteq Agentic AI Consulting", "https://www.inteqgroup.com/agentic-ai-consulting/development-implementation-scale", "inteqgroup.com", "public partner/agency pages", ["AI consultants/agencies needing governance layer"], "Inteq focuses on implementing agents that perform in production, with governance and measurable performance.", ["governance_safety", "implementation_burden", "contactability"]),
    ]
    receipt = {
        "mission_id": "e10_autonomous_buyer_discovery",
        "public_target_discovery_ran": True,
        "provider_name": "codex_public_read_only_web_search",
        "queries_used": 20,
        "pages_read": len(sources),
        "domains_touched": sorted({source.domain for source in sources}),
        "external_action_executed": False,
        "customer_contact_occurred": False,
        "publication_occurred": False,
        "payment_or_form_or_account_action": False,
        "contact_info_scraped": False,
        "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "stop_reason": "safe candidate evidence exceeded 20 candidates across at least 5 segments",
    }
    return {"request": build_e10_target_discovery_request(), "sources": sources, "receipt": receipt}


def render_e10_target_discovery_research_plan(request: E10TargetDiscoveryRequest) -> str:
    lines = ["# E10 Target Discovery Research Plan", "", f"- mission_id: {request.mission_id}", f"- top_offer: {request.top_offer}", ""]
    lines.extend(["## Target Segments"])
    lines.extend(f"- {item}" for item in request.target_segments_to_explore)
    lines.extend(["", "## Search Queries"])
    lines.extend(f"- {item}" for item in request.search_queries)
    lines.extend(["", "## Budget"])
    lines.extend(f"- {key}: {value}" for key, value in request.budget.items())
    lines.extend(["", "## Forbidden Actions"])
    lines.extend(f"- {item}" for item in request.forbidden_actions)
    return "\n".join(lines)


def render_e10_target_discovery_receipt(research: Dict[str, Any]) -> str:
    lines = ["# E10 Target Discovery Receipt", ""]
    for key, value in research["receipt"].items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def render_e10_target_discovery_source_summaries(sources: List[E10DiscoverySourceSummary]) -> str:
    lines = ["# E10 Target Discovery Source Summaries", "", f"- source_count: {len(sources)}", ""]
    for source in sources:
        lines.extend(
            [
                f"## {source.source_id}: {source.title}",
                f"- url: {source.url}",
                f"- domain: {source.domain}",
                f"- category: {source.source_category}",
                f"- segments: {', '.join(source.segment_tags)}",
                f"- signals: {', '.join(source.signal_types)}",
                f"- summary: {source.summary}",
                f"- limitations: {source.limitations}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
