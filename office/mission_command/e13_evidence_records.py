from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


class E13EvidenceQuality(str, Enum):
    DIRECT_BUYER_PAIN = "direct_buyer_pain"
    INDIRECT_MARKET_EVIDENCE = "indirect_market_evidence"
    COMPETITOR_OR_SUBSTITUTE = "competitor_or_substitute"
    PRICING_REFERENCE = "pricing_reference"
    PUBLIC_FORUM_ANECDOTE = "public_forum_anecdote"
    PUBLIC_DOCS_OR_VENDOR_CLAIM = "public_docs_or_vendor_claim"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    STALE_EVIDENCE = "stale_evidence"
    INVALID_EVIDENCE = "invalid_evidence"


E13_OPPORTUNITY_PATHS = [
    "Agent Workflow Bottleneck Diagnosis",
    "Founder AI Workflow Audit / CEO Command Brief",
    "AI Agent Incident Postmortem Service",
    "Coding-Agent Governance Audit",
    "AI Ops Operating Room Implementation Support",
    "Partner Enablement Package for AI Consultants",
    "Runtime Setup Advisory",
]


@dataclass(frozen=True)
class E13EvidenceRecord:
    evidence_id: str
    opportunity_path: str
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
    freshness: str
    allowed_use: str
    limitations: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def receipt_hash(source: str, content: str) -> str:
    return hashlib.sha256(f"{source}\n{content}".encode("utf-8")).hexdigest()[:24]


def classify_evidence_quality(source_type: str, text: str) -> E13EvidenceQuality:
    lowered = f"{source_type} {text}".lower()
    if not text.strip():
        return E13EvidenceQuality.INVALID_EVIDENCE
    if any(term in lowered for term in ["pricing", "price", "$", "plans", "package"]):
        return E13EvidenceQuality.PRICING_REFERENCE
    if any(term in lowered for term in ["pain", "bottleneck", "incident", "broken", "hard", "manual", "governance", "audit"]):
        return E13EvidenceQuality.DIRECT_BUYER_PAIN
    if any(term in lowered for term in ["alternative", "competitor", "substitute", "platform", "agency", "consulting"]):
        return E13EvidenceQuality.COMPETITOR_OR_SUBSTITUTE
    if any(term in lowered for term in ["forum", "hacker news", "hn", "reddit", "community", "issue", "discussion"]):
        return E13EvidenceQuality.PUBLIC_FORUM_ANECDOTE
    if any(term in lowered for term in ["docs", "guide", "vendor", "product", "case study"]):
        return E13EvidenceQuality.PUBLIC_DOCS_OR_VENDOR_CLAIM
    return E13EvidenceQuality.INDIRECT_MARKET_EVIDENCE


def extract_signal(text: str, terms: List[str]) -> str:
    lowered = text.lower()
    hits = [term for term in terms if term in lowered]
    return ", ".join(hits[:5])


def build_evidence_record(
    evidence_id: str,
    opportunity_path: str,
    source_url_or_ref: str,
    source_type: str,
    content: str,
    query_or_locator: str = "",
    collector: str = "host_tier1_evidence_runner",
) -> E13EvidenceRecord:
    quality = classify_evidence_quality(source_type, content)
    claim = content.strip().replace("\n", " ")[:240]
    return E13EvidenceRecord(
        evidence_id=evidence_id,
        opportunity_path=opportunity_path,
        source_url_or_ref=source_url_or_ref,
        source_type=source_type,
        access_mode="public_read_only_no_login",
        collected_at=utc_now(),
        collector=collector,
        query_or_locator=query_or_locator or source_url_or_ref,
        claim_supported=claim,
        buyer_segment="AI consultants/agencies and AI-heavy small teams",
        pain_language=extract_signal(content, ["bottleneck", "pain", "manual", "incident", "governance", "audit", "workflow"]),
        urgency_signal=extract_signal(content, ["urgent", "now", "incident", "risk", "production", "deadline"]),
        pricing_signal=extract_signal(content, ["pricing", "price", "$", "plan", "package", "consulting"]),
        substitute_signal=extract_signal(content, ["alternative", "platform", "agency", "consulting", "service", "tool"]),
        trust_gap_signal=extract_signal(content, ["trust", "security", "governance", "risk", "compliance", "approval"]),
        delivery_burden_signal=extract_signal(content, ["implementation", "setup", "integrate", "migration", "configure"]),
        owner_burden_signal=extract_signal(content, ["manual", "48h", "workshop", "diagnostic", "audit"]),
        evidence_quality=quality.value,
        freshness="unknown_from_public_source" if quality != E13EvidenceQuality.INVALID_EVIDENCE else "invalid",
        allowed_use="paid_signal_readiness_only_not_validation_feedback",
        limitations="Public read-only evidence; not customer validation, not paid signal, not outreach approval.",
        receipt_hash=receipt_hash(source_url_or_ref, content),
    )


def validate_evidence_record(record: E13EvidenceRecord | Dict[str, Any]) -> List[str]:
    data = record.to_dict() if isinstance(record, E13EvidenceRecord) else dict(record)
    required = [
        "evidence_id",
        "opportunity_path",
        "source_url_or_ref",
        "claim_supported",
        "evidence_quality",
        "limitations",
        "receipt_hash",
    ]
    errors = [f"missing_{key}" for key in required if not data.get(key)]
    if data.get("opportunity_path") not in E13_OPPORTUNITY_PATHS:
        errors.append("unknown_opportunity_path")
    if str(data.get("source_url_or_ref", "")).lower().startswith(("fake:", "invented:")):
        errors.append("fake_evidence_source_rejected")
    if str(data.get("claim_supported", "")).strip().lower() in {"", "tbd", "owner_to_fill", "fake"}:
        errors.append("unsupported_or_fake_claim_rejected")
    try:
        E13EvidenceQuality(data.get("evidence_quality", ""))
    except ValueError:
        errors.append("invalid_evidence_quality")
    if data.get("evidence_quality") == E13EvidenceQuality.INVALID_EVIDENCE.value:
        errors.append("invalid_evidence_cannot_support_readiness")
    return list(dict.fromkeys(errors))
