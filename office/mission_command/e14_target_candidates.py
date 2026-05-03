from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .target_lifecycle_router import target_contact_is_blocked


E14_PRIMARY_OFFER = "48h AI Agent Implementation Readiness Review"
E14_TARGET_SEGMENT = "AI consultants/agencies needing governance layer, plus AI-heavy teams adopting AI agents or coding-agent workflows."


@dataclass(frozen=True)
class E14TargetCandidate:
    target_id: str
    source: str
    organization_or_person_name: str
    public_url_or_ref: str
    segment: str
    why_this_target: str
    relevance_to_offer: str
    evidence_refs: List[str]
    risk_level: str
    contact_channel_candidate: str
    contact_channel_allowed: bool
    requires_owner_approval: bool
    no_contact_until_approved: bool
    privacy_notes: str
    exclusion_reason_if_any: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _top_e13r_evidence_refs(repo_root: Path, limit: int = 8) -> List[str]:
    data = _load_json(repo_root / "operations" / "external_validation" / "e13r_evidence_records.json")
    records = data.get("records", [])
    refs = []
    for record in records:
        if record.get("offer_id") == "ai_agent_implementation_readiness_review" and record.get("evidence_quality") in {
            "direct_buyer_pain",
            "pricing_or_budget",
            "substitute_or_comparable",
        }:
            refs.append(str(record.get("evidence_id")))
    return refs[:limit] or [str(item.get("evidence_id")) for item in records[:limit] if item.get("evidence_id")]


def _candidate_from_e10_seed(seed: Dict[str, Any], evidence_refs: List[str]) -> E14TargetCandidate:
    target_id = str(seed.get("target_id", "unknown_target"))
    target = {
        "target_id": target_id,
        "proposal_only": True,
        "owner_approved_for_contact": False,
        "contact_executed": False,
    }
    return E14TargetCandidate(
        target_id=target_id,
        source="E10_proposed_target_seed",
        organization_or_person_name=str(seed.get("name_or_label", target_id)),
        public_url_or_ref=str(seed.get("source_public_url", "")),
        segment=str(seed.get("segment", E14_TARGET_SEGMENT)),
        why_this_target=str(seed.get("why_relevant", "E10 discovered this organization-level candidate from public evidence.")),
        relevance_to_offer="Potential buyer/operator for AI-agent implementation readiness, governance, or client-risk reduction review.",
        evidence_refs=list(seed.get("source_ids", [])) + evidence_refs[:3],
        risk_level="Tier 2 owner-operated manual validation candidate",
        contact_channel_candidate=str(seed.get("channel", "owner_selected_public_general_channel_after_owner_review")),
        contact_channel_allowed=False,
        requires_owner_approval=True,
        no_contact_until_approved=target_contact_is_blocked(target),
        privacy_notes="Organization-level public business context only; no scraped personal contact, no inferred email, no private profile enrichment.",
    )


def _candidate_from_e10_registry(candidate: Dict[str, Any], evidence_refs: List[str]) -> E14TargetCandidate:
    candidate_id = str(candidate.get("candidate_id", "unknown_candidate"))
    target = {
        "target_id": candidate_id,
        "proposal_only": True,
        "owner_approved_for_contact": False,
        "contact_executed": False,
    }
    return E14TargetCandidate(
        target_id=candidate_id,
        source="E10_autonomous_target_candidate_registry",
        organization_or_person_name=str(candidate.get("target_name_or_label", candidate_id)),
        public_url_or_ref=str(candidate.get("public_url", "")),
        segment=str(candidate.get("segment", E14_TARGET_SEGMENT)),
        why_this_target="E10 registry suggests AI workflow/tooling/governance relevance; E14 keeps it as owner-review only.",
        relevance_to_offer="Potential fit if the organization needs implementation readiness, governance, evaluation, or agent workflow risk mapping.",
        evidence_refs=list(candidate.get("source_ids", [])) + evidence_refs[:2],
        risk_level=str(candidate.get("risk_tier", "Tier 2 owner-operated manual validation candidate")),
        contact_channel_candidate=str(candidate.get("contact_channel_status", "public_role_only_no_contact")),
        contact_channel_allowed=False,
        requires_owner_approval=True,
        no_contact_until_approved=target_contact_is_blocked(target),
        privacy_notes="Public organization/project context only; target is not approved for contact and contains no personal scraping.",
    )


def build_e14_target_candidates(repo_root: Path, max_candidates: int = 6) -> List[E14TargetCandidate]:
    evidence_refs = _top_e13r_evidence_refs(repo_root)
    proposed = _load_json(repo_root / "operations" / "external_validation" / "e10_target_seeds.proposed.json").get("targets", [])
    candidates: List[E14TargetCandidate] = [_candidate_from_e10_seed(item, evidence_refs) for item in proposed]
    registry = _load_json(repo_root / "operations" / "external_validation" / "e10_autonomous_target_candidates.json").get("candidates", [])
    preferred_segments = {"AI consultants/agencies needing governance layer", "teams using agent frameworks or AI workflow tooling"}
    for item in registry:
        if len(candidates) >= max_candidates:
            break
        if item.get("segment") in preferred_segments:
            new_candidate = _candidate_from_e10_registry(item, evidence_refs)
            if new_candidate.target_id not in {candidate.target_id for candidate in candidates}:
                candidates.append(new_candidate)
    return candidates[:max_candidates]


def validate_e14_target_candidate(candidate: E14TargetCandidate | Dict[str, Any]) -> List[str]:
    data = candidate.to_dict() if isinstance(candidate, E14TargetCandidate) else dict(candidate)
    errors: List[str] = []
    required = [
        "target_id",
        "organization_or_person_name",
        "public_url_or_ref",
        "segment",
        "why_this_target",
        "relevance_to_offer",
        "evidence_refs",
        "privacy_notes",
    ]
    errors.extend(f"missing_{key}" for key in required if not data.get(key))
    if data.get("contact_channel_allowed") is True:
        errors.append("contact_channel_must_not_be_allowed_before_owner_approval")
    if data.get("requires_owner_approval") is not True:
        errors.append("requires_owner_approval_must_be_true")
    if data.get("no_contact_until_approved") is not True:
        errors.append("no_contact_until_approved_must_be_true")
    lowered = " ".join(str(data.get(key, "")).lower() for key in ["public_url_or_ref", "contact_channel_candidate", "privacy_notes"])
    if "@" in lowered or "linkedin.com/in/" in lowered or "personal email" in lowered or "scraped_personal" in lowered:
        errors.append("private_or_personal_scraping_rejected")
    return list(dict.fromkeys(errors))


def write_e14_target_candidates(repo_root: Path) -> Path:
    candidates = build_e14_target_candidates(repo_root)
    path = repo_root / "operations" / "external_validation" / "e14_target_candidates.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"offer": E14_PRIMARY_OFFER, "candidate_count": len(candidates), "candidates": [item.to_dict() for item in candidates]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
