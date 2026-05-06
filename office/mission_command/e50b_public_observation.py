from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _read_text(path: Path, limit: int = 800000) -> str:
    try:
        data = path.read_text(encoding='utf-8', errors='ignore')
        return data[:limit]
    except Exception:
        return ''


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _contains(text: str, needles: list[str]) -> bool:
    low = text.lower()
    return any(needle.lower() in low for needle in needles)

DOMAINS = [
    'AI agent governance / guardrails buyer pain',
    'MCP adoption / MCP server tooling pain',
    'agentic workflow safety and approval gates',
    'AI audit / causal logging / compliance evidence',
    'enterprise AI governance procurement signals',
    'developer tool integration pain around local agent execution',
    'startup / SMB demand for governed agent execution',
    'security review / red-team / policy enforcement pain',
    'existing alternatives and competitors',
    'pricing / packaging signals',
    'first-user reachable segments without outreach',
    'urgency triggers around regulation, rollout, incidents, or MCP ecosystem growth',
]

PUBLIC_RECEIPTS = [
    ('mcp_tooling', 'Claude Desktop Extensions docs', 'https://claude.com/docs/connectors/custom/desktop-extensions', 'official_docs', 'Anthropic', 'Claude Desktop extensions package MCP servers as installable .mcpb bundles.', 'Strengthens plugin/MCPB packaging route but requires packaging polish.'),
    ('mcp_tooling', 'Building Desktop Extensions with MCPB', 'https://support.claude.com/en/articles/12922929-building-desktop-extensions-with-mcpb', 'official_docs', 'Anthropic', 'MCPB bundles are zip archives with manifest metadata and local server code.', 'Confirms distribution mechanics for later plugin packaging.'),
    ('mcp_tooling', 'Anthropic desktop extensions announcement', 'https://www.anthropic.com/engineering/desktop-extensions', 'official_blog', 'Anthropic', 'Extensions reduce MCP server setup friction for Claude Desktop users.', 'Shows install friction is a recognized buyer/developer pain.'),
    ('agent_governance', 'OpenAI Agents SDK Guardrails', 'https://openai.github.io/openai-agents-js/guides/guardrails/', 'official_docs', 'OpenAI', 'Agent guardrails are positioned as configurable checks around agent inputs and outputs.', 'Supports governance/guardrail pain but is not validation of Y*Bridge demand.'),
    ('agent_observability', 'OpenAI Agents SDK Tracing', 'https://openai.github.io/openai-agents-js/guides/tracing/', 'official_docs', 'OpenAI', 'Tracing is first-class for debugging, visualization, and monitoring of agent workflows.', 'Shows proof/evidence/trace language is legible in agent tooling.'),
    ('agent_observability', 'Arize Phoenix docs', 'https://arize.com/docs/phoenix/', 'official_docs', 'Arize', 'Phoenix provides open-source AI observability and tracing docs.', 'Competitor/adjacent category for proof and observability framing.'),
    ('pricing', 'Braintrust pricing', 'https://www.braintrust.dev/pricing', 'pricing_page', 'Braintrust', 'AI eval/observability products publish usage/team pricing pages.', 'Supports paid-tool packaging comparables, not a paid signal for Y*Bridge.'),
    ('enterprise_governance', 'AWS Bedrock Guardrails', 'https://aws.amazon.com/bedrock/guardrails/', 'official_product_page', 'AWS', 'AWS markets guardrails for generative AI applications.', 'Enterprise governance pain is externally visible.'),
    ('enterprise_governance', 'Azure AI Content Safety overview', 'https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview', 'official_docs', 'Microsoft', 'Azure documents content safety APIs for detecting harmful content.', 'Confirms large-platform investment in AI safety controls.'),
    ('enterprise_governance', 'Google Model Armor', 'https://cloud.google.com/security/products/model-armor', 'official_product_page', 'Google Cloud', 'Model Armor is positioned as model security and safety for generative AI.', 'Supports enterprise safety/governance framing.'),
    ('agent_governance', 'NVIDIA NeMo Guardrails', 'https://docs.nvidia.com/nemo-guardrails/index.html', 'official_docs', 'NVIDIA', 'NeMo Guardrails documents programmable guardrails for conversational AI.', 'Competitor/adjacent route; argues against overclaiming generic guardrails.'),
    ('security_redteam', 'HackerOne AI Red Teaming', 'https://www.hackerone.com/ai-red-teaming', 'product_page', 'HackerOne', 'HackerOne markets AI red teaming services.', 'Shows service wedge exists but Y*Bridge must avoid claiming validation.'),
    ('security_redteam', 'HackerOne AI Red Teaming product', 'https://www.hackerone.com/product/ai-red-teaming', 'product_page', 'HackerOne', 'AI red teaming is packaged as a product/service offer.', 'Supports service-first proof packet possibility.'),
    ('workflow_automation', 'n8n pricing', 'https://n8n.io/pricing/', 'pricing_page', 'n8n', 'Workflow automation platforms have visible tiered pricing.', 'Workflow resale route has pricing comparables but weak current proof.'),
    ('workflow_automation', 'Zapier pricing', 'https://zapier.com/pricing', 'pricing_page', 'Zapier', 'Automation platform pricing is visible for teams and businesses.', 'Workflow automation pricing is legible but not specific to governed agents.'),
    ('agent_ops', 'Vercel Agents docs', 'https://vercel.com/docs/agents', 'official_docs', 'Vercel', 'Vercel documents agent-building infrastructure.', 'Developer-led agent ops segment is externally visible.'),
    ('pricing', 'Dify pricing', 'https://dify.ai/pricing', 'pricing_page', 'Dify', 'AI app platform exposes public plan/pricing structure.', 'AI builder products use public pricing but Y*Bridge still needs proof packaging.'),
    ('audit_compliance', 'Arize Phoenix homepage', 'https://phoenix.arize.com/', 'product_page', 'Arize', 'Phoenix positions AI observability/tracing for developers.', 'Audit/proof positioning needs differentiated governed-action language.'),
]


def build_public_observation_plan() -> dict[str, Any]:
    return {
        'artifact_id': 'e50b_public_observation_plan',
        'observation_mode': 'bounded_public_read_only',
        'domains': [{'domain_id': f'domain_{idx:02d}', 'domain': domain, 'max_sources': 4, 'no_contact_boundary': True} for idx, domain in enumerate(DOMAINS, 1)],
        'hard_cap_public_pages': 40,
        'source_quality_criteria': ['official docs/product/pricing pages preferred', 'public pages only', 'no login/payment/private API', 'no personal contact data'],
        'claims_policy': {'not_customer_validation': True, 'not_paid_signal': True, 'claims_require_receipts': True},
    }


def build_public_source_receipts() -> list[dict[str, Any]]:
    receipts = []
    for idx, (domain, title, url, source_type, publisher, claim, relevance) in enumerate(PUBLIC_RECEIPTS, 1):
        receipts.append({
            'receipt_id': f'e50b_receipt_{idx:03d}',
            'domain': domain,
            'source_title': title,
            'source_url_or_public_identifier': url,
            'source_type': source_type,
            'publisher': publisher,
            'observed_claim': claim,
            'relevance': relevance,
            'support_level': 'public_readonly_observation',
            'limitation': 'Public source only; not customer validation, not expert feedback, not paid signal, and not proof of Y*Bridge demand.',
            'not_customer_validation': True,
            'not_paid_signal': True,
            'collected_without_contact': True,
            'collected_without_login': True,
        })
    return receipts


def build_commercial_evidence_atoms() -> list[dict[str, Any]]:
    atoms = []
    for receipt in build_public_source_receipts():
        if receipt['domain'] in {'mcp_tooling', 'agent_ops'}:
            implication = 'Strengthens MCP/plugin/developer proof route, but packaging friction remains.'
        elif receipt['domain'] in {'enterprise_governance', 'agent_governance'}:
            implication = 'Strengthens governed-agent proof packet language while warning against enterprise compliance overclaim.'
        elif receipt['domain'] in {'security_redteam'}:
            implication = 'Supports service-wedge framing if bounded as proof review, not certified red-team result.'
        elif receipt['domain'] in {'pricing', 'workflow_automation'}:
            implication = 'Shows public pricing comparables, but current Y*Bridge route needs a proof artifact before pricing.'
        else:
            implication = 'Useful adjacent evidence; keep as supporting, not decisive.'
        atoms.append({
            'evidence_id': receipt['receipt_id'].replace('receipt', 'evidence'),
            'domain': receipt['domain'],
            'source_url_or_local_source_ref': receipt['source_url_or_public_identifier'],
            'observed_claim': receipt['observed_claim'],
            'relevance_to_YBridge': receipt['relevance'],
            'freshness_date_if_available': 'observed_2026-05-06_public_page',
            'buyer_pain_signal': 'public_category_signal',
            'competitor_signal': 'adjacent_or_competing_tooling_visible',
            'route_implication': implication,
            'confidence_basis': 'direct_source',
            'not_customer_validation': True,
            'not_paid_signal': True,
        })
    return atoms


def build_observation_run() -> dict[str, Any]:
    receipts = build_public_source_receipts()
    return {
        'artifact_id': 'e50b_public_readonly_commercial_observation_run',
        'status': 'public_readonly_observation_executed',
        'provider': 'Codex web public search/open',
        'source_receipt_count': len(receipts),
        'domains_covered': sorted(set(receipt['domain'] for receipt in receipts)),
        'page_read_cap': 40,
        'contacts_identified': False,
        'personal_contact_data_collected': False,
        'login_used': False,
        'forms_submitted': False,
        'messages_sent': False,
        'published': False,
        'provider_private_api_used': False,
        'customer_validation_claimed': False,
        'paid_signal_claimed': False,
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(build_observation_run(), indent=2, ensure_ascii=False))
