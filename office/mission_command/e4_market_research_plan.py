from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .tier1_public_research import Tier1ResearchBudget, Tier1ResearchRequest, FORBIDDEN_ACTIONS


E4_OPPORTUNITY_FAMILIES = [
    "Agent Workflow Bottleneck Diagnosis",
    "Founder AI Workflow Audit / CEO Command Brief",
    "Coding-Agent Governance Audit",
    "MCP / Tool-Use Boundary Review",
    "AI Agent Incident Postmortem Service",
    "Open-Source-to-Paid-Support Governance Pack",
    "Partner Enablement Package for AI Consultants",
    "AI Ops Operating Room / Implementation Support",
]


ALLOWED_SOURCE_CATEGORIES = [
    "public product/service pages",
    "public pricing pages",
    "public GitHub repos/issues/discussions",
    "public docs",
    "public engineering/security blogs",
    "public community discussions",
    "public job postings/hiring pages",
    "public vendor/consultant pages",
    "public app marketplace pages",
    "public no-login articles",
]


def build_e4_market_research_request() -> Tier1ResearchRequest:
    queries = [
        "AI agent workflow bottleneck diagnosis service pricing",
        "founder AI workflow audit consultant pricing",
        "coding agent governance audit AI engineering teams",
        "MCP tool use security boundary review consulting",
        "AI agent incident postmortem service",
        "open source governance paid support AI agents",
        "AI consultants partner enablement governance kit",
        "AI operations room implementation support startup",
        "AI coding assistant governance policy enterprise",
        "agentic AI risk management consulting",
        "AI workflow automation agency pricing",
        "AI agent observability incident response",
    ]
    # Page targets are deliberately empty until a safe search provider supplies public URLs.
    return Tier1ResearchRequest(
        mission_id="e4_market_backed_first_revenue",
        allowed_source_categories=ALLOWED_SOURCE_CATEGORIES,
        query_plan=queries,
        page_read_plan=[],
        budget=Tier1ResearchBudget(
            max_search_queries=25,
            max_pages_read=40,
            max_domains=20,
            max_runtime_seconds=300,
        ),
        stop_conditions=[
            "budget exhausted",
            "login required",
            "contact/form/payment/publication requested",
            "private or paywalled page encountered",
            "provider unavailable",
            "enough evidence to rank top two paths",
        ],
        forbidden_actions=list(FORBIDDEN_ACTIONS),
    )


def render_e4_market_research_plan(request: Tier1ResearchRequest) -> str:
    lines = [
        "# E4 Market Research Plan",
        "",
        f"- mission_id: {request.mission_id}",
        f"- max_search_queries: {request.budget.max_search_queries}",
        f"- max_pages_read: {request.budget.max_pages_read}",
        f"- max_domains: {request.budget.max_domains}",
        f"- max_runtime_seconds: {request.budget.max_runtime_seconds}",
        "",
        "## Opportunity Families",
    ]
    lines.extend(f"- {item}" for item in E4_OPPORTUNITY_FAMILIES)
    lines.extend(["", "## Evidence Sought"])
    lines.extend(
        f"- {item}"
        for item in [
            "buyer pain language",
            "competitors",
            "substitutes",
            "no-action / DIY patterns",
            "pricing or budget proxy",
            "buying trigger",
            "buying process",
            "trust gap",
            "why buyer might not choose us",
            "fastest disconfirming signal",
        ]
    )
    lines.extend(["", "## Query Plan"])
    lines.extend(f"- {query}" for query in request.query_plan)
    lines.extend(["", "## Allowed Source Categories"])
    lines.extend(f"- {category}" for category in request.allowed_source_categories)
    lines.extend(["", "## Stop Conditions"])
    lines.extend(f"- {condition}" for condition in request.stop_conditions)
    lines.extend(["", "## Forbidden"])
    lines.extend(f"- {item}" for item in request.forbidden_actions)
    lines.extend(
        [
            "",
            "No live research may be treated as evidence-backed unless a receipt and source summaries are written.",
        ]
    )
    return "\n".join(lines)


def write_e4_market_research_plan(repo_root: Path) -> Path:
    path = repo_root / "reports" / "integration" / "e4_market_research_plan.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_e4_market_research_plan(build_e4_market_research_request()) + "\n", encoding="utf-8")
    return path
