from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .e10_autonomous_target_discovery import E10DiscoverySourceSummary
from .e10_buyer_signal_taxonomy import BuyerSignalType


E10_TARGET_CANDIDATES_PATH = Path("operations/external_validation/e10_autonomous_target_candidates.json")


class E10TargetType:
    COMPANY = "company"
    PROJECT = "project"
    OPEN_SOURCE_REPO = "open_source_repo"
    PUBLIC_ROLE_PERSONA = "public_role_persona"
    COMMUNITY = "community"
    AGENCY_PARTNER = "agency_partner"
    INTERNAL_BENCHMARK_PROXY = "internal_benchmark_proxy"


class E10ContactChannelStatus:
    PUBLIC_GENERAL_CHANNEL = "public_general_channel"
    PUBLIC_ROLE_ONLY_NO_CONTACT = "public_role_only_no_contact"
    OWNER_KNOWN_CONTACT_NEEDED = "owner_known_contact_needed"
    COMMUNITY_PUBLIC_POST_CANDIDATE = "community_public_post_candidate"
    NOT_CONTACTABLE_SAFELY = "not_contactable_safely"


@dataclass(frozen=True)
class E10TargetCandidate:
    candidate_id: str
    target_name_or_label: str
    target_type: str
    segment: str
    public_url: str
    source_ids: List[str]
    pain_signals: List[str]
    budget_signals: List[str]
    urgency_signals: List[str]
    tool_stack_complexity_signals: List[str]
    governance_safety_signals: List[str]
    implementation_burden_signals: List[str]
    existing_alternative_signals: List[str]
    contactability_signal: str
    contact_channel_status: str
    risk_tier: str
    owner_approved_for_contact: bool
    contact_executed: bool
    discovered_by_aiden: bool
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return cleaned[:54] or "candidate"


def _target_type_for_source(source: E10DiscoverySourceSummary) -> str:
    category = source.source_category.lower()
    if "agency" in category or "consultant" in category or "partner" in category:
        return E10TargetType.AGENCY_PARTNER
    if "job" in category:
        return E10TargetType.COMPANY
    if "github" in category or "open-source" in source.summary.lower():
        return E10TargetType.OPEN_SOURCE_REPO
    if "product" in category or "pricing" in category or "docs" in category:
        return E10TargetType.PROJECT
    return E10TargetType.COMPANY


def _contact_status_for_source(source: E10DiscoverySourceSummary) -> str:
    category = source.source_category.lower()
    summary = source.summary.lower()
    if "agency" in category or "consultant" in category or "partner" in category:
        return E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL
    if "job" in category:
        return E10ContactChannelStatus.OWNER_KNOWN_CONTACT_NEEDED
    if "open-source" in summary or "github" in category:
        return E10ContactChannelStatus.COMMUNITY_PUBLIC_POST_CANDIDATE
    if "pricing" in category or "docs" in category or "product" in category:
        return E10ContactChannelStatus.PUBLIC_ROLE_ONLY_NO_CONTACT
    return E10ContactChannelStatus.NOT_CONTACTABLE_SAFELY


def _signals_for_type(source: E10DiscoverySourceSummary, signal_type: str) -> List[str]:
    if signal_type in source.signal_types:
        return [source.summary]
    return []


def candidate_from_source(source: E10DiscoverySourceSummary) -> E10TargetCandidate:
    contact_status = _contact_status_for_source(source)
    risk_tier = "Tier 2 candidate" if contact_status != E10ContactChannelStatus.NOT_CONTACTABLE_SAFELY else "Tier 0 internal benchmark only"
    candidate_id = f"cand_{_slug(source.domain.split('.')[0])}_{_slug(source.source_id.replace('src_', ''))}"
    return E10TargetCandidate(
        candidate_id=candidate_id,
        target_name_or_label=source.title,
        target_type=_target_type_for_source(source),
        segment=source.segment_tags[0] if source.segment_tags else "unknown",
        public_url=source.url,
        source_ids=[source.source_id],
        pain_signals=_signals_for_type(source, BuyerSignalType.PAIN),
        budget_signals=_signals_for_type(source, BuyerSignalType.BUDGET),
        urgency_signals=_signals_for_type(source, BuyerSignalType.URGENCY) + _signals_for_type(source, BuyerSignalType.HIRING_JOB),
        tool_stack_complexity_signals=_signals_for_type(source, BuyerSignalType.TOOL_STACK_COMPLEXITY),
        governance_safety_signals=_signals_for_type(source, BuyerSignalType.GOVERNANCE_SAFETY),
        implementation_burden_signals=_signals_for_type(source, BuyerSignalType.IMPLEMENTATION_BURDEN),
        existing_alternative_signals=_signals_for_type(source, BuyerSignalType.EXISTING_ALTERNATIVE),
        contactability_signal=(
            "Public organization/project page only; owner must approve any contact route."
            if contact_status != E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL
            else "Public general channel appears available from organization/agency site; no contact executed."
        ),
        contact_channel_status=contact_status,
        risk_tier=risk_tier,
        owner_approved_for_contact=False,
        contact_executed=False,
        discovered_by_aiden=True,
        limitations=(
            "Autonomously discovered from public read-only evidence. Candidate is not approved for contact, "
            "contains no scraped personal contact, and does not prove willingness to pay."
        ),
    )


def validate_e10_target_candidate(candidate: E10TargetCandidate | Dict[str, Any]) -> List[str]:
    item = candidate if isinstance(candidate, E10TargetCandidate) else E10TargetCandidate(**candidate)
    errors: List[str] = []
    if not item.candidate_id:
        errors.append("missing_candidate_id")
    if not item.public_url:
        errors.append("missing_public_url")
    if not item.source_ids:
        errors.append("missing_public_evidence_source")
    if item.owner_approved_for_contact:
        errors.append("owner_approval_must_default_false")
    if item.contact_executed:
        errors.append("contact_executed_must_be_false_in_discovery")
    if item.contact_channel_status not in {
        E10ContactChannelStatus.PUBLIC_GENERAL_CHANNEL,
        E10ContactChannelStatus.PUBLIC_ROLE_ONLY_NO_CONTACT,
        E10ContactChannelStatus.OWNER_KNOWN_CONTACT_NEEDED,
        E10ContactChannelStatus.COMMUNITY_PUBLIC_POST_CANDIDATE,
        E10ContactChannelStatus.NOT_CONTACTABLE_SAFELY,
    }:
        errors.append("invalid_contact_channel_status")
    searchable = " ".join(
        [
            item.target_name_or_label,
            item.public_url,
            item.contactability_signal,
            item.limitations,
        ]
    )
    if re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", searchable):
        errors.append("scraped_personal_email_not_allowed")
    if "scraped" in searchable.lower() and "no scraped" not in searchable.lower():
        errors.append("scraped_contact_not_allowed")
    return list(dict.fromkeys(errors))


def build_e10_target_candidate_registry(sources: Iterable[E10DiscoverySourceSummary]) -> List[E10TargetCandidate]:
    candidates = [candidate_from_source(source) for source in sources]
    seen: set[str] = set()
    deduped: List[E10TargetCandidate] = []
    for candidate in candidates:
        if candidate.candidate_id in seen:
            continue
        seen.add(candidate.candidate_id)
        deduped.append(candidate)
    return deduped


def validate_e10_target_registry(candidates: List[E10TargetCandidate], research_ran: bool = True) -> List[str]:
    errors: List[str] = []
    if research_ran and len(candidates) < 20:
        errors.append("target_registry_requires_at_least_20_candidates_when_research_runs")
    if research_ran and len({candidate.segment for candidate in candidates}) < 5:
        errors.append("target_registry_requires_at_least_5_segments_when_research_runs")
    for candidate in candidates:
        errors.extend(f"{candidate.candidate_id}:{error}" for error in validate_e10_target_candidate(candidate))
    return list(dict.fromkeys(errors))


def write_e10_target_candidates_json(repo_root: Path, candidates: List[E10TargetCandidate]) -> Path:
    path = repo_root / E10_TARGET_CANDIDATES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "proposal_only": True,
        "contact_authorized": False,
        "contact_executed": False,
        "candidate_count": len(candidates),
        "segment_count": len({candidate.segment for candidate in candidates}),
        "candidates": [candidate.to_dict() for candidate in candidates],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def render_e10_target_candidate_registry(candidates: List[E10TargetCandidate]) -> str:
    errors = validate_e10_target_registry(candidates, research_ran=True)
    lines = [
        "# E10 Target Candidate Registry",
        "",
        f"- candidate_count: {len(candidates)}",
        f"- segment_count: {len({candidate.segment for candidate in candidates})}",
        f"- validation_errors: {', '.join(errors) or 'none'}",
        "- owner_approved_for_contact_default: false",
        "- contact_executed_default: false",
        "- personal_data_policy: no scraped personal emails, no private profile enrichment, no inferred personal contact details",
        "",
        "## Candidates",
    ]
    for candidate in candidates:
        lines.extend(
            [
                f"### {candidate.candidate_id}: {candidate.target_name_or_label}",
                f"- target_type: {candidate.target_type}",
                f"- segment: {candidate.segment}",
                f"- public_url: {candidate.public_url}",
                f"- source_ids: {', '.join(candidate.source_ids)}",
                f"- contact_channel_status: {candidate.contact_channel_status}",
                f"- risk_tier: {candidate.risk_tier}",
                f"- owner_approved_for_contact: {str(candidate.owner_approved_for_contact).lower()}",
                f"- contact_executed: {str(candidate.contact_executed).lower()}",
                f"- public_signals: pain={len(candidate.pain_signals)}, budget={len(candidate.budget_signals)}, urgency={len(candidate.urgency_signals)}, tool_stack={len(candidate.tool_stack_complexity_signals)}, governance={len(candidate.governance_safety_signals)}, implementation={len(candidate.implementation_burden_signals)}, alternatives={len(candidate.existing_alternative_signals)}",
                f"- contactability_signal: {candidate.contactability_signal}",
                f"- limitations: {candidate.limitations}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
