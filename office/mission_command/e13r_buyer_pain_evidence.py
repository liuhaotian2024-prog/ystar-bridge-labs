from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .action_authorization_router import ActionAuthorizationRequest, action_authorization_blocks_without_governance
from .e13r_offer_revision import E13R_REVISED_OFFER_IDS, generate_revised_offer_candidates
from .evidence_signal_router import EvidenceClaimType, EvidenceSignalType, evidence_supports_claim


E13R_FORBIDDEN_ACTIONS = [
    "customer_contact",
    "email_or_message",
    "publication",
    "payment",
    "account_creation",
    "form_submission",
    "login",
    "private_data_collection",
    "personal_contact_scraping",
    "high_volume_crawling",
    "secret_reading",
    "core_brain_cieu_memory_writeback",
    "obligation_auto_registration",
]

E13R_ALLOWED_SOURCE_CLASSES = [
    "public_buyer_pain_article",
    "public_governance_article",
    "public_production_failure_article",
    "public_pricing_page",
    "public_substitute_or_competitor_page",
    "public_docs_or_vendor_claim",
]

E13R_BUYER_PAIN_QUERIES = [
    "AI agents broke production workflow",
    "coding agent generated unsafe code",
    "AI workflow bottleneck consulting",
    "AI implementation audit",
    "AI agent governance consulting",
    "AI development workflow audit",
    "Cursor coding agent governance",
    "AI coding assistant risk management",
    "agentic AI implementation challenges",
    "AI operations consulting pricing",
]

E13R_DEFAULT_SOURCE_URLS = [
    {
        "url": "https://www.techtarget.com/searchdatamanagement/feature/How-agentic-AI-governance-tackles-data-security-challenges",
        "source_type": "public_buyer_pain_article",
        "offer_ids": ["ai_agent_implementation_readiness_review", "ai_ops_operating_room_implementation_support"],
        "query_or_locator": "agentic AI governance data security operational risk pain",
    },
    {
        "url": "https://latitude.so/blog/why-ai-agents-break-in-production",
        "source_type": "public_production_failure_article",
        "offer_ids": ["ai_agent_workflow_recovery_room", "ai_ops_bottleneck_risk_map"],
        "query_or_locator": "AI agents break production workflow failure patterns",
    },
    {
        "url": "https://nodejam.com/blog/why-ai-agents-break-in-production",
        "source_type": "public_production_failure_article",
        "offer_ids": ["ai_agent_workflow_recovery_room", "ai_ops_bottleneck_risk_map"],
        "query_or_locator": "agent workflows break in production enterprise workflows",
    },
    {
        "url": "https://www.n-ix.com/agentic-ai-governance/",
        "source_type": "public_governance_article",
        "offer_ids": ["coding_agent_governance_audit", "ai_agent_implementation_readiness_review"],
        "query_or_locator": "agentic AI governance implementation challenges behavior hard to explain",
    },
    {
        "url": "https://www.ibm.com/think/insights/agentic-ai-governance-playbook",
        "source_type": "public_governance_article",
        "offer_ids": ["ai_agent_implementation_readiness_review", "ai_ops_operating_room_implementation_support"],
        "query_or_locator": "agentic AI execution gap unclear value weak risk controls",
    },
    {
        "url": "https://www.ibm.com/think/insights/ethics-governance-agentic-ai",
        "source_type": "public_governance_article",
        "offer_ids": ["coding_agent_governance_audit", "ai_agent_implementation_readiness_review"],
        "query_or_locator": "agentic AI risks code actions guardrails governance",
    },
    {
        "url": "https://www.primefirms.co/trends-articles/agentic-ai-architecture",
        "source_type": "public_buyer_pain_article",
        "offer_ids": ["ai_ops_bottleneck_risk_map", "ai_agent_implementation_readiness_review"],
        "query_or_locator": "agentic AI implementation challenges reliability hallucination integration",
    },
    {
        "url": "https://www.computerweekly.com/feature/Work-is-broken-Can-agentic-AI-fix-it",
        "source_type": "public_buyer_pain_article",
        "offer_ids": ["ai_ops_bottleneck_risk_map", "ai_ops_operating_room_implementation_support"],
        "query_or_locator": "work is broken agentic AI workflow fragmentation",
    },
    {
        "url": "https://audit-loop.com/",
        "source_type": "public_substitute_or_competitor_page",
        "offer_ids": ["coding_agent_governance_audit"],
        "query_or_locator": "AI coding audit substitute comparable service",
    },
    {
        "url": "https://ethicalveracity.ai/",
        "source_type": "public_substitute_or_competitor_page",
        "offer_ids": ["coding_agent_governance_audit", "ai_agent_implementation_readiness_review"],
        "query_or_locator": "AI governance audit substitute comparable service",
    },
    {
        "url": "https://www.johsolutions.com/pricing",
        "source_type": "public_pricing_page",
        "offer_ids": ["ai_ops_operating_room_implementation_support", "ai_agent_implementation_readiness_review"],
        "query_or_locator": "AI consulting pricing reference",
    },
    {
        "url": "https://automationtransformationconsulting.com/resources/ai-automation-cost-guide",
        "source_type": "public_pricing_page",
        "offer_ids": ["ai_ops_operating_room_implementation_support", "ai_ops_bottleneck_risk_map"],
        "query_or_locator": "AI automation consulting cost guide pricing",
    },
]


@dataclass(frozen=True)
class E13RBuyerPainEvidenceRequest:
    request_id: str
    milestone_id: str
    entry_repository_delivery_rt1: int
    revised_offer_ids: List[str]
    queries: List[str]
    allowed_source_classes: List[str]
    source_urls: List[Dict[str, Any]]
    budget: Dict[str, int]
    forbidden_actions: List[str]
    run_public_collection_if_sources_available: bool = True
    public_evidence_is_validation_feedback: bool = False
    readiness_is_revenue: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E13RBuyerPainEvidenceRecord:
    evidence_id: str
    offer_id: str
    offer_name: str
    source_url_or_ref: str
    source_type: str
    access_mode: str
    collected_at: str
    collector: str
    query_or_locator: str
    claim_supported: str
    buyer_segment: str
    pain_language: str
    urgency_signal: str
    pricing_signal: str
    substitute_signal: str
    trust_gap_signal: str
    delivery_burden_signal: str
    owner_burden_signal: str
    evidence_quality: str
    allowed_use: str
    limitations: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def receipt_hash(source: str, content: str) -> str:
    return hashlib.sha256(f"{source}\n{content}".encode("utf-8")).hexdigest()[:24]


def build_default_e13r_request() -> E13RBuyerPainEvidenceRequest:
    return E13RBuyerPainEvidenceRequest(
        request_id="e13r_offer_revision_buyer_pain_evidence",
        milestone_id="E13R_offer_revision_buyer_pain_evidence_rerun",
        entry_repository_delivery_rt1=0,
        revised_offer_ids=E13R_REVISED_OFFER_IDS,
        queries=E13R_BUYER_PAIN_QUERIES,
        allowed_source_classes=E13R_ALLOWED_SOURCE_CLASSES,
        source_urls=E13R_DEFAULT_SOURCE_URLS,
        budget={"max_sources": 12, "max_bytes_per_source": 140000, "max_runtime_seconds": 180},
        forbidden_actions=E13R_FORBIDDEN_ACTIONS,
    )


def validate_e13r_request(request: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if request.get("entry_repository_delivery_rt1") != 0:
        errors.append("e13r_requires_e13_repository_delivery_rt1_zero")
    if not request.get("revised_offer_ids"):
        errors.append("revised_offer_ids_required")
    if len(request.get("revised_offer_ids", [])) < 5:
        errors.append("at_least_five_revised_offers_required")
    if not request.get("queries"):
        errors.append("buyer_pain_queries_required")
    pricing_only = [query for query in request.get("queries", []) if "pricing" in query.lower() or "price" in query.lower()]
    if len(pricing_only) == len(request.get("queries", [])):
        errors.append("queries_must_target_buyer_pain_not_only_pricing")
    forbidden = set(request.get("forbidden_actions", []))
    missing_forbidden = [item for item in E13R_FORBIDDEN_ACTIONS if item not in forbidden]
    errors.extend(f"missing_forbidden_action_{item}" for item in missing_forbidden)
    source_classes = set(request.get("allowed_source_classes", []))
    for item in request.get("source_urls", []):
        if not str(item.get("url", "")).startswith(("https://", "http://")):
            errors.append("source_url_must_be_public_http_or_https")
        if item.get("source_type") not in source_classes:
            errors.append("source_type_not_allowlisted")
        for offer_id in item.get("offer_ids", []):
            if offer_id not in E13R_REVISED_OFFER_IDS:
                errors.append("unknown_offer_id_in_source")
    return list(dict.fromkeys(errors))


def e13r_blocks_external_side_effects() -> bool:
    request = ActionAuthorizationRequest(
        action_id="e13r_forbidden_contact_probe",
        action_type="external_validation_contact",
        risk_tier="Tier 2",
        target_lifecycle_state="proposed_target_seed",
        owner_approval_present=False,
        manifest_valid=False,
        channel_approved=False,
        draft_hash_valid=False,
        y_star_gov_decision="owner_approval_required",
        gov_mcp_gateway_available=True,
        gov_mcp_preflight_passed=False,
        execution_provider_available=False,
        no_forbidden_side_effects=False,
    )
    return action_authorization_blocks_without_governance(request)


def public_evidence_can_be_validation_feedback() -> bool:
    return evidence_supports_claim(EvidenceSignalType.PUBLIC_MARKET_EVIDENCE, EvidenceClaimType.VALIDATION_RESULT)


def public_readiness_can_be_revenue() -> bool:
    return evidence_supports_claim(EvidenceSignalType.PUBLIC_MARKET_EVIDENCE, EvidenceClaimType.PAID_SIGNAL_CLAIM)


def extract_terms(text: str, terms: List[str]) -> str:
    lowered = text.lower()
    return ", ".join(term for term in terms if term in lowered)[:180]


def classify_e13r_quality(source_type: str, content: str) -> str:
    lowered = f"{source_type} {content}".lower()
    if not content.strip():
        return "invalid_evidence"
    if source_type == "public_pricing_page" or any(term in lowered for term in ["pricing", "price", "$", "cost guide", "package"]):
        return "pricing_or_budget"
    if source_type == "public_substitute_or_competitor_page" or any(term in lowered for term in ["competitor", "substitute", "audit service", "governance service"]):
        return "substitute_or_comparable"
    pain_terms = [
        "broke",
        "break",
        "failure",
        "unsafe",
        "risk",
        "bottleneck",
        "hard to operate",
        "production",
        "governance gap",
        "workflow",
        "implementation challenge",
        "manual",
        "fragmented",
        "lack",
        "unprepared",
    ]
    if any(term in lowered for term in pain_terms):
        return "direct_buyer_pain"
    return "indirect_market_evidence"


def build_e13r_evidence_record(
    evidence_id: str,
    offer_id: str,
    source_url_or_ref: str,
    source_type: str,
    content: str,
    query_or_locator: str,
    collector: str = "host_e13r_evidence_runner",
) -> E13RBuyerPainEvidenceRecord:
    offer_by_id = {item.offer_id: item for item in generate_revised_offer_candidates()}
    offer = offer_by_id[offer_id]
    quality = classify_e13r_quality(source_type, content)
    claim = content.strip().replace("\n", " ")[:260]
    return E13RBuyerPainEvidenceRecord(
        evidence_id=evidence_id,
        offer_id=offer_id,
        offer_name=offer.offer_name,
        source_url_or_ref=source_url_or_ref,
        source_type=source_type,
        access_mode="public_read_only_no_login",
        collected_at=utc_now(),
        collector=collector,
        query_or_locator=query_or_locator,
        claim_supported=claim,
        buyer_segment=offer.buyer_segment,
        pain_language=extract_terms(content, ["broke", "break", "failure", "unsafe", "risk", "bottleneck", "production", "workflow", "governance", "implementation"]),
        urgency_signal=extract_terms(content, ["urgent", "production", "risk", "security", "failure", "breach", "deadline", "scale"]),
        pricing_signal=extract_terms(content, ["pricing", "price", "$", "cost", "package", "budget", "spend"]),
        substitute_signal=extract_terms(content, ["audit", "consulting", "service", "platform", "tool", "assessment", "review"]),
        trust_gap_signal=extract_terms(content, ["trust", "governance", "security", "risk", "compliance", "accountability", "visibility"]),
        delivery_burden_signal=extract_terms(content, ["implementation", "integration", "setup", "operate", "production", "workflow", "architecture"]),
        owner_burden_signal=offer.owner_burden,
        evidence_quality=quality,
        allowed_use="paid_signal_readiness_only_not_validation_feedback",
        limitations="Public read-only evidence; not buyer feedback, not paid signal, not outreach approval.",
        receipt_hash=receipt_hash(source_url_or_ref, content),
    )


def validate_e13r_evidence_record(record: E13RBuyerPainEvidenceRecord | Dict[str, Any]) -> List[str]:
    data = record.to_dict() if isinstance(record, E13RBuyerPainEvidenceRecord) else dict(record)
    required = ["evidence_id", "offer_id", "source_url_or_ref", "claim_supported", "evidence_quality", "limitations", "receipt_hash"]
    errors = [f"missing_{key}" for key in required if not data.get(key)]
    if data.get("offer_id") not in E13R_REVISED_OFFER_IDS:
        errors.append("unknown_offer_id")
    if str(data.get("source_url_or_ref", "")).lower().startswith(("fake:", "invented:")):
        errors.append("fake_evidence_source_rejected")
    if str(data.get("claim_supported", "")).strip().lower() in {"", "fake", "owner_to_fill", "tbd"}:
        errors.append("unsupported_or_fake_claim_rejected")
    if data.get("evidence_quality") == "invalid_evidence":
        errors.append("invalid_evidence_cannot_support_readiness")
    return list(dict.fromkeys(errors))


def write_e13r_request(repo_root: Path) -> Path:
    request = build_default_e13r_request().to_dict()
    path = repo_root / "operations" / "external_validation" / "e13r_buyer_pain_evidence_request.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def render_buyer_pain_evidence_report(request: Dict[str, Any], evidence_count: int, classification: str, blocked_reason: str) -> str:
    lines = [
        "# E13R Buyer-Pain Evidence Rerun",
        "",
        f"- request_id: {request.get('request_id')}",
        f"- evidence_count: {evidence_count}",
        f"- readiness_classification: {classification}",
        f"- blocked_reason: {blocked_reason or 'none'}",
        f"- public_evidence_is_validation_feedback: {str(public_evidence_can_be_validation_feedback()).lower()}",
        f"- readiness_is_revenue: {str(public_readiness_can_be_revenue()).lower()}",
        "",
        "## Buyer-Pain Queries",
    ]
    lines.extend(f"- {query}" for query in request.get("queries", []))
    lines.extend(["", "## Source Seeds"])
    lines.extend(f"- {item.get('source_type')}: {item.get('url')}" for item in request.get("source_urls", []))
    lines.extend(["", "## Forbidden Actions"])
    lines.extend(f"- {item}" for item in E13R_FORBIDDEN_ACTIONS)
    return "\n".join(lines)
