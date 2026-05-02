from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


class BuyerSignalType:
    PAIN = "pain"
    BUDGET = "budget"
    URGENCY = "urgency"
    TOOL_STACK_COMPLEXITY = "tool_stack_complexity"
    GOVERNANCE_SAFETY = "governance_safety"
    HIRING_JOB = "hiring_job"
    IMPLEMENTATION_BURDEN = "implementation_burden"
    EXISTING_ALTERNATIVE = "existing_alternative"
    CONTACTABILITY = "contactability"
    TRUST_GAP = "trust_gap"
    DISCONFIRMING = "disconfirming"


REQUIRED_BUYER_SIGNAL_TYPES = [
    BuyerSignalType.PAIN,
    BuyerSignalType.BUDGET,
    BuyerSignalType.URGENCY,
    BuyerSignalType.TOOL_STACK_COMPLEXITY,
    BuyerSignalType.GOVERNANCE_SAFETY,
    BuyerSignalType.HIRING_JOB,
    BuyerSignalType.IMPLEMENTATION_BURDEN,
    BuyerSignalType.EXISTING_ALTERNATIVE,
    BuyerSignalType.CONTACTABILITY,
    BuyerSignalType.TRUST_GAP,
    BuyerSignalType.DISCONFIRMING,
]


@dataclass(frozen=True)
class BuyerSignal:
    signal_id: str
    signal_type: str
    source_id: str
    source_url: str
    source_domain: str
    excerpt_or_summary: str
    strength: str
    confidence: float
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def classify_buyer_signal(text: str, source_metadata: Dict[str, Any]) -> BuyerSignal:
    lower = text.lower()
    signal_type = BuyerSignalType.PAIN
    if any(token in lower for token in ["already solved", "no urgency", "not a priority", "too expensive"]):
        signal_type = BuyerSignalType.DISCONFIRMING
    elif any(token in lower for token in ["pricing", "$", "paid", "enterprise", "sales", "budget", "plan"]):
        signal_type = BuyerSignalType.BUDGET
    elif any(token in lower for token in ["hiring", "job", "engineer", "salary"]):
        signal_type = BuyerSignalType.HIRING_JOB
    elif any(token in lower for token in ["urgent", "deadline", "now", "production", "launch", "incident"]):
        signal_type = BuyerSignalType.URGENCY
    elif any(token in lower for token in ["governance", "security", "audit", "compliance", "approval", "guardrail"]):
        signal_type = BuyerSignalType.GOVERNANCE_SAFETY
    elif any(token in lower for token in ["implementation", "integration", "deployment", "onboarding", "support"]):
        signal_type = BuyerSignalType.IMPLEMENTATION_BURDEN
    elif any(token in lower for token in ["alternative", "competitor", "substitute", "vendor", "platform"]):
        signal_type = BuyerSignalType.EXISTING_ALTERNATIVE
    elif any(token in lower for token in ["trust", "evidence", "provenance", "trace", "traceability"]):
        signal_type = BuyerSignalType.TRUST_GAP
    elif any(token in lower for token in ["observability", "evaluation", "tracing", "workflow", "agent", "automation", "llmops"]):
        signal_type = BuyerSignalType.TOOL_STACK_COMPLEXITY
    elif any(token in lower for token in ["contact", "community", "github", "docs", "public"]):
        signal_type = BuyerSignalType.CONTACTABILITY
    strength = "strong" if len(text) > 180 else "medium" if len(text) > 80 else "weak"
    return BuyerSignal(
        signal_id=str(source_metadata.get("signal_id", f"signal_{source_metadata.get('source_id', 'unknown')}")),
        signal_type=signal_type,
        source_id=str(source_metadata.get("source_id", "")),
        source_url=str(source_metadata.get("source_url", "")),
        source_domain=str(source_metadata.get("source_domain", "")),
        excerpt_or_summary=text[:500],
        strength=strength,
        confidence={"weak": 0.35, "medium": 0.65, "strong": 0.85}[strength],
        limitations="Public-source signal only; not customer validation or permission to contact.",
    )


def score_signal_strength(signal: BuyerSignal | Dict[str, Any]) -> int:
    item = signal if isinstance(signal, BuyerSignal) else BuyerSignal(**signal)
    return {"weak": 1, "medium": 2, "strong": 3}.get(item.strength, 0)


def render_buyer_signal_taxonomy_report() -> str:
    lines = [
        "# E10 Buyer Signal Taxonomy",
        "",
        "E10 distinguishes public discovery signals from validation feedback. Signals can identify promising target candidates, but they do not approve contact or prove willingness to pay.",
        "",
        "## Required Signal Types",
    ]
    lines.extend(f"- {item}" for item in REQUIRED_BUYER_SIGNAL_TYPES)
    lines.extend(
        [
            "",
            "## Safety Rules",
            "- Public signals may support candidate discovery only.",
            "- No personal contact scraping.",
            "- No private profile enrichment.",
            "- No contact, email, DM, publication, form, account, payment, or core writeback.",
            "- Candidate contact remains owner-approval-gated.",
        ]
    )
    return "\n".join(lines)
