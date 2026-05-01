from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from pathlib import Path
from typing import Any, Dict, List


EVIDENCE_ROLES = {
    "buyer_pain",
    "pricing_budget",
    "competitor",
    "substitute",
    "buying_process",
    "trust_gap",
    "market_category",
    "weak_context_only",
}

CLAIM_TYPES = {
    "directly_supported",
    "inferred_from_source",
    "internal_hypothesis",
    "requires_validation",
}


@dataclass(frozen=True)
class EvidenceQualityAssessment:
    source_id: str
    domain: str
    opportunity_ids: List[str]
    raw_summary_excerpt: str
    cleaned_summary: str
    buyer_pain_signal: str
    pricing_budget_signal: str
    competitor_substitute_signal: str
    buying_process_signal: str
    trust_gap_signal: str
    evidence_role: str
    claim_type: str
    readability_score: int
    signal_strength_score: int
    noise_flags: List[str]
    usable_for_customer_facing_packet: bool
    limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def detect_noise_flags(raw_text: str) -> List[str]:
    lower = raw_text.lower()
    flags: List[str] = []
    if any(token in lower for token in ["function(", "window.", "document.", "gtag(", "datalayer", "localstorage"]):
        flags.append("javascript_noise")
    if any(token in lower for token in ["@font-face", "{", "}", "--", "visibility:", "display:"]):
        flags.append("css_or_style_noise")
    if any(token in lower for token in ['"@context"', '"featureflags"', '{"', '":']):
        flags.append("json_or_schema_noise")
    if any(token in lower for token in ["tracking", "analytics", "nonce", "gtm", "intellimize"]):
        flags.append("tracking_noise")
    if len(raw_text) > 700:
        flags.append("long_raw_excerpt")
    return list(dict.fromkeys(flags))


def clean_source_summary(raw_text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw_text)
    text = re.sub(r"\{[^{}]{0,500}\}", " ", text)
    text = re.sub(r"!function\([^)]*\).*?(?=\s[A-Z][a-z]|\Z)", " ", text)
    text = re.sub(r"@font-face[^.]{0,400}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    useful_phrases = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        lower = sentence.lower()
        if any(token in lower for token in ["pricing", "enterprise", "plan", "support", "security", "workflow", "automation", "evaluation", "incident", "partner", "billing", "ai"]):
            useful_phrases.append(sentence.strip())
    cleaned = " ".join(useful_phrases[:3]) or text[:220]
    return cleaned[:420].strip()


def _score_readability(raw_text: str, flags: List[str]) -> int:
    score = 5
    score -= min(3, len(flags))
    if len(raw_text.split()) < 12:
        score -= 1
    return max(1, score)


def _score_signal(source: Dict[str, Any]) -> int:
    fields = [
        "buyer_pain_signal",
        "pricing_signal",
        "competitor_signal",
        "substitute_signal",
        "budget_signal",
    ]
    return max(1, min(5, sum(1 for field in fields if str(source.get(field, "")).strip())))


def _role_and_claim(source: Dict[str, Any], noise_flags: List[str]) -> tuple[str, str]:
    pricing = bool(str(source.get("pricing_signal", "")).strip() or str(source.get("budget_signal", "")).strip())
    competition = bool(str(source.get("competitor_signal", "")).strip() or str(source.get("substitute_signal", "")).strip())
    buyer = bool(str(source.get("buyer_pain_signal", "")).strip())
    category = str(source.get("source_category", "")).lower()
    if pricing:
        role = "pricing_budget"
    elif "docs" in category:
        role = "trust_gap"
    elif competition:
        role = "competitor"
    elif buyer:
        role = "buyer_pain"
    else:
        role = "weak_context_only"
    if noise_flags:
        claim_type = "inferred_from_source"
    elif role in {"pricing_budget", "competitor", "substitute", "trust_gap"}:
        claim_type = "directly_supported"
    elif buyer:
        claim_type = "requires_validation"
    else:
        claim_type = "internal_hypothesis"
    return role, claim_type


def evidence_is_customer_facing_usable(assessment: EvidenceQualityAssessment) -> bool:
    return (
        assessment.readability_score >= 4
        and assessment.signal_strength_score >= 3
        and not assessment.noise_flags
        and assessment.claim_type in {"directly_supported", "inferred_from_source"}
    )


def assess_source_quality(source: Dict[str, Any]) -> EvidenceQualityAssessment:
    raw_parts = [
        str(source.get("summary", "")),
        str(source.get("buyer_pain_signal", "")),
        str(source.get("pricing_signal", "")),
        str(source.get("competitor_signal", "")),
        str(source.get("substitute_signal", "")),
        str(source.get("budget_signal", "")),
    ]
    raw_text = " ".join(part for part in raw_parts if part).strip()
    noise_flags = detect_noise_flags(raw_text)
    cleaned = clean_source_summary(raw_text)
    role, claim_type = _role_and_claim(source, noise_flags)
    readability = _score_readability(raw_text, noise_flags)
    signal = _score_signal(source)
    limitations = list(source.get("limitations", [])) or ["Source requires owner review before external use."]
    if "pricing_budget" == role:
        limitations.append("Vendor pricing pages are budget proxies, not proof of buyer willingness to pay Y*Bridge.")
    if noise_flags:
        limitations.append("Raw excerpt contains page boilerplate/noise; use cleaned evidence only.")
    assessment = EvidenceQualityAssessment(
        source_id=str(source.get("source_id", "")),
        domain=str(source.get("domain", "")),
        opportunity_ids=list(source.get("relevant_opportunity_ids", [])),
        raw_summary_excerpt=raw_text[:500],
        cleaned_summary=cleaned,
        buyer_pain_signal=clean_source_summary(str(source.get("buyer_pain_signal", ""))),
        pricing_budget_signal=clean_source_summary(" ".join([str(source.get("pricing_signal", "")), str(source.get("budget_signal", ""))])),
        competitor_substitute_signal=clean_source_summary(" ".join([str(source.get("competitor_signal", "")), str(source.get("substitute_signal", ""))])),
        buying_process_signal=clean_source_summary(str(source.get("budget_signal", ""))),
        trust_gap_signal="Evidence supports a trust/category gap, not customer validation.",
        evidence_role=role if role in EVIDENCE_ROLES else "weak_context_only",
        claim_type=claim_type,
        readability_score=readability,
        signal_strength_score=signal,
        noise_flags=noise_flags,
        usable_for_customer_facing_packet=False,
        limitations=limitations,
    )
    usable = evidence_is_customer_facing_usable(assessment)
    return EvidenceQualityAssessment(**{**assessment.to_dict(), "usable_for_customer_facing_packet": usable})


def parse_e6_external_source_summaries(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    sources: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None
    body_lines: List[str] = []
    list_fields = {"relevant_opportunity_ids", "limitations"}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## e6_"):
            if current is not None:
                current["summary"] = current.get("summary") or " ".join(body_lines).strip()
                sources.append(current)
            current = {"source_id": line.replace("##", "").strip()}
            body_lines = []
            continue
        if current is None:
            continue
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "public_identifier":
                current["url_or_public_identifier"] = value
            elif key in list_fields:
                current[key] = [item.strip() for item in value.split(",") if item.strip()]
            else:
                current[key] = value
        elif line.strip():
            body_lines.append(line.strip())
    if current is not None:
        current["summary"] = current.get("summary") or " ".join(body_lines).strip()
        sources.append(current)
    return sources


def build_e7_evidence_quality_table(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [assess_source_quality(source).to_dict() for source in sources]


def render_e7_evidence_quality_calibration(rows: List[Dict[str, Any]]) -> str:
    usable_count = sum(1 for row in rows if row["usable_for_customer_facing_packet"])
    noisy_count = sum(1 for row in rows if row["noise_flags"])
    lines = [
        "# E7 Evidence Quality Calibration",
        "",
        f"- source_count: {len(rows)}",
        f"- customer_facing_usable_count: {usable_count}",
        f"- noisy_source_count: {noisy_count}",
        "- calibration_rule: raw noisy snippets may remain internal evidence but must not be used as polished commercial proof.",
        "- pricing_rule: vendor pricing pages provide budget proxy, not buyer willingness-to-pay for Y*Bridge.",
        "- validation_rule: public-source evidence is not customer validation.",
        "",
        "## Source Assessments",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['source_id']}",
                f"- domain: {row['domain']}",
                f"- role: {row['evidence_role']}",
                f"- claim_type: {row['claim_type']}",
                f"- readability_score: {row['readability_score']}",
                f"- signal_strength_score: {row['signal_strength_score']}",
                f"- noise_flags: {', '.join(row['noise_flags']) or 'none'}",
                f"- usable_for_customer_facing_packet: {row['usable_for_customer_facing_packet']}",
                f"- cleaned_summary: {row['cleaned_summary']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_e7_cleaned_evidence_table(rows: List[Dict[str, Any]]) -> str:
    lines = [
        "# E7 Cleaned Evidence Table",
        "",
        "| Source ID | Domain | Opportunity IDs | Role | Claim Type | Customer-Facing Usable | Limitations |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        limitations = "; ".join(row["limitations"])[:240]
        lines.append(
            f"| {row['source_id']} | {row['domain']} | {', '.join(row['opportunity_ids'])} | {row['evidence_role']} | {row['claim_type']} | {row['usable_for_customer_facing_packet']} | {limitations} |"
        )
    lines.extend(["", "## Cleaned Signals"])
    for row in rows:
        lines.extend(
            [
                f"### {row['source_id']}",
                f"- cleaned_buyer_pain_signal: {row['buyer_pain_signal'] or 'none'}",
                f"- cleaned_pricing_budget_signal: {row['pricing_budget_signal'] or 'none'}",
                f"- cleaned_competitor_substitute_signal: {row['competitor_substitute_signal'] or 'none'}",
                f"- cleaned_buying_process_signal: {row['buying_process_signal'] or 'none'}",
                f"- trust_gap_signal: {row['trust_gap_signal']}",
            ]
        )
    return "\n".join(lines)
