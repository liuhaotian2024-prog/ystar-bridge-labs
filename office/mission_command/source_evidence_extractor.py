from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Dict, List


@dataclass(frozen=True)
class SourceEvidenceSignals:
    buyer_pain_signal: str
    pricing_signal: str
    competitor_signal: str
    substitute_signal: str
    budget_signal: str
    buying_process_signal: str
    trust_gap_signal: str
    market_category_signal: str
    limitation_notes: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _snippet(text: str, tokens: List[str], max_len: int = 180) -> str:
    clean = " ".join(text.split())
    lower = clean.lower()
    for token in tokens:
        index = lower.find(token.lower())
        if index >= 0:
            start = max(0, index - 60)
            end = min(len(clean), index + max_len)
            return clean[start:end].strip()
    return clean[:max_len].strip()


def _has_any(text: str, tokens: List[str]) -> bool:
    lower = text.lower()
    return any(token.lower() in lower for token in tokens)


def extract_source_evidence_signals(
    *,
    text_excerpt: str,
    title: str,
    domain: str,
    source_category: str,
    evidence_sought: List[str],
) -> SourceEvidenceSignals:
    text = " ".join([title, domain, source_category, text_excerpt])
    lower = text.lower()
    pricing_tokens = ["pricing", "price", "$", "plan", "subscription", "enterprise", "contact sales", "free", "paid", "billing", "sponsor"]
    buyer_tokens = [
        "security",
        "risk",
        "evaluation",
        "observability",
        "workflow",
        "automation",
        "incident",
        "enterprise",
        "governance",
        "support",
        "partner",
        "billing",
    ]
    process_tokens = ["contact sales", "enterprise", "billing", "sponsor", "marketplace", "partner", "subscription", "plans", "pricing"]
    trust_tokens = ["security", "privacy", "governance", "enterprise", "compliance", "audit", "trusted", "permission", "authorization"]
    category_tokens = ["agent", "copilot", "workflow", "automation", "incident", "mcp", "ai", "observability", "consulting", "sponsors"]

    pricing_signal = ""
    if _has_any(lower, pricing_tokens):
        pricing_signal = _snippet(text, pricing_tokens)

    buyer_pain_signal = ""
    if _has_any(lower, buyer_tokens):
        buyer_pain_signal = _snippet(text, buyer_tokens)
    elif evidence_sought:
        buyer_pain_signal = f"Seed sought {', '.join(evidence_sought)}; excerpt requires human review."

    competitor_signal = ""
    vendorish = ["pricing", "vendor", "consultant", "product", "service", "docs", "ecosystem", "marketplace"]
    if _has_any(source_category, vendorish) or _has_any(domain, ["github", "cursor", "langchain", "crewai", "zapier", "humanloop", "vellum", "incident", "rootly", "aws", "bcg", "retool", "make"]):
        competitor_signal = f"{domain} is a public incumbent/source in category `{source_category}`."

    substitute_signal = ""
    if _has_any(lower, ["template", "guide", "checklist", "docs", "platform", "automation", "internal tools", "sponsors"]):
        substitute_signal = _snippet(text, ["template", "guide", "checklist", "docs", "platform", "automation", "internal tools", "sponsors"])

    budget_signal = ""
    if pricing_signal:
        budget_signal = "Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use."

    buying_process_signal = ""
    if _has_any(lower, process_tokens):
        buying_process_signal = _snippet(text, process_tokens)

    trust_gap_signal = ""
    if _has_any(lower, trust_tokens):
        trust_gap_signal = _snippet(text, trust_tokens)

    market_category_signal = ""
    if _has_any(lower, category_tokens):
        matched = [token for token in category_tokens if token in lower][:4]
        market_category_signal = " / ".join(matched)

    limitation_notes = [
        "Signals are deterministic excerpts from public page text only.",
        "No customer contact, login, form submission, payment, or publication occurred.",
        "Source interpretation requires owner review before any external use.",
    ]
    if not pricing_signal:
        limitation_notes.append("No explicit pricing/billing signal found in excerpt.")
    if not buyer_pain_signal:
        limitation_notes.append("No strong buyer-pain language found in excerpt.")
    if not buying_process_signal:
        limitation_notes.append("No clear buying-process signal found in excerpt.")
    if not trust_gap_signal:
        limitation_notes.append("No explicit trust/governance signal found in excerpt.")

    return SourceEvidenceSignals(
        buyer_pain_signal=buyer_pain_signal,
        pricing_signal=pricing_signal,
        competitor_signal=competitor_signal,
        substitute_signal=substitute_signal,
        budget_signal=budget_signal,
        buying_process_signal=buying_process_signal,
        trust_gap_signal=trust_gap_signal,
        market_category_signal=market_category_signal,
        limitation_notes=limitation_notes,
    )


def signal_strength(signals: SourceEvidenceSignals) -> int:
    fields = [
        signals.buyer_pain_signal,
        signals.pricing_signal,
        signals.competitor_signal,
        signals.substitute_signal,
        signals.budget_signal,
        signals.buying_process_signal,
        signals.trust_gap_signal,
        signals.market_category_signal,
    ]
    return sum(1 for field in fields if field)


def source_supports_market_backing(signals: SourceEvidenceSignals) -> bool:
    return bool(signals.buyer_pain_signal and (signals.pricing_signal or signals.competitor_signal or signals.substitute_signal))
