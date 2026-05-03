#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from office.mission_command.e13_tier1_evidence_mission import build_default_e13_request


DEFAULT_PUBLIC_SOURCE_URLS = [
    {
        "url": "https://automationtransformationconsulting.com/resources/ai-automation-cost-guide",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["AI Ops Operating Room Implementation Support", "Runtime Setup Advisory"],
        "query_or_locator": "AI automation consulting cost guide with pricing ranges",
    },
    {
        "url": "https://www.orionintelligenceagency.com/advisory",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Agent Workflow Bottleneck Diagnosis", "AI Ops Operating Room Implementation Support"],
        "query_or_locator": "implementation advisory workflow blueprint guardrails pricing",
    },
    {
        "url": "https://humansai.io/blog/ai-automation-agency-pricing-2026",
        "source_type": "public_blog_post",
        "opportunity_paths": ["Partner Enablement Package for AI Consultants", "AI Ops Operating Room Implementation Support"],
        "query_or_locator": "AI automation agency pricing 2026",
    },
    {
        "url": "https://www.smeautomate.com/pricing",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Agent Workflow Bottleneck Diagnosis", "Runtime Setup Advisory"],
        "query_or_locator": "AI workflow automation pricing by workflow",
    },
    {
        "url": "https://www.jonomor.com/pricing",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Coding-Agent Governance Audit", "Founder AI Workflow Audit / CEO Command Brief"],
        "query_or_locator": "AI visibility audit governance stack pricing",
    },
    {
        "url": "https://dynode.ai/pricing",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["AI Ops Operating Room Implementation Support", "Runtime Setup Advisory"],
        "query_or_locator": "AI implementation pricing and retainers",
    },
    {
        "url": "https://flowevolve.com/services/",
        "source_type": "public_marketplace_or_agency_page",
        "opportunity_paths": ["AI Ops Operating Room Implementation Support", "Partner Enablement Package for AI Consultants"],
        "query_or_locator": "AI automation consulting implementation roadmap pricing",
    },
    {
        "url": "https://ethicalveracity.ai/",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Coding-Agent Governance Audit", "Founder AI Workflow Audit / CEO Command Brief"],
        "query_or_locator": "AI governance audit consulting pricing",
    },
    {
        "url": "https://www.johsolutions.com/pricing",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Agent Workflow Bottleneck Diagnosis", "Runtime Setup Advisory"],
        "query_or_locator": "AI workflow discovery audit pricing",
    },
    {
        "url": "https://coverge.ai/blog/llmops-tools-pricing-comparison",
        "source_type": "public_blog_post",
        "opportunity_paths": ["Coding-Agent Governance Audit", "AI Agent Incident Postmortem Service"],
        "query_or_locator": "LLMOps pricing comparison governance observability evaluation",
    },
    {
        "url": "https://audit-loop.com/",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Coding-Agent Governance Audit", "AI Agent Incident Postmortem Service"],
        "query_or_locator": "AI agent governance approval routing audit trail pricing",
    },
    {
        "url": "https://www.byteintelligence.com/pricing",
        "source_type": "public_pricing_page",
        "opportunity_paths": ["Agent Workflow Bottleneck Diagnosis", "AI Ops Operating Room Implementation Support"],
        "query_or_locator": "automation sprint bottleneck pricing",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the default E13 Tier-1 evidence mission request.")
    parser.add_argument("--repo-root", default="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    output = Path(args.output) if args.output else repo_root / "operations/external_validation/e13_tier1_evidence_request.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    request = build_default_e13_request(DEFAULT_PUBLIC_SOURCE_URLS).to_dict()
    output.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
