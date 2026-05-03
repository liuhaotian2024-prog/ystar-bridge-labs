from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .e14_target_candidates import E14TargetCandidate, validate_e14_target_candidate


@dataclass(frozen=True)
class E14TargetScore:
    target_id: str
    score: int
    fit_with_offer: int
    evidence_backed_pain_relevance: int
    likely_buyer_role: int
    channel_suitability: int
    trust_gap: int
    owner_burden: int
    risk: int
    public_noninvasive_path: int
    organization_facing: int
    inclusion_decision: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def score_e14_target(candidate: E14TargetCandidate) -> E14TargetScore:
    errors = validate_e14_target_candidate(candidate)
    if errors:
        return E14TargetScore(
            target_id=candidate.target_id,
            score=0,
            fit_with_offer=0,
            evidence_backed_pain_relevance=0,
            likely_buyer_role=0,
            channel_suitability=0,
            trust_gap=0,
            owner_burden=0,
            risk=0,
            public_noninvasive_path=0,
            organization_facing=0,
            inclusion_decision="exclude",
            reason="; ".join(errors),
        )
    text = f"{candidate.segment} {candidate.why_this_target} {candidate.relevance_to_offer}".lower()
    fit = 2 if any(term in text for term in ["implementation", "readiness", "governance", "agent", "workflow"]) else 1
    pain = 2 if candidate.evidence_refs else 0
    buyer = 2 if any(term in text for term in ["agency", "consult", "team", "cto", "operator", "project"]) else 1
    channel = 1 if "public" in candidate.contact_channel_candidate.lower() else 0
    trust_gap = 1 if "governance" in text or "risk" in text else 0
    owner_burden = 2 if "owner" in candidate.contact_channel_candidate.lower() or "public" in candidate.contact_channel_candidate.lower() else 1
    risk = 2 if candidate.risk_level.lower().startswith("tier 2") else 1
    public_path = 2 if candidate.public_url_or_ref.startswith("http") else 1
    org_facing = 2 if "organization-level" in candidate.privacy_notes.lower() or "business context" in candidate.privacy_notes.lower() else 1
    total = fit + pain + buyer + channel + trust_gap + owner_burden + risk + public_path + org_facing
    decision = "include_in_owner_review_batch" if total >= 11 else "hold_for_revision"
    return E14TargetScore(
        target_id=candidate.target_id,
        score=total,
        fit_with_offer=fit,
        evidence_backed_pain_relevance=pain,
        likely_buyer_role=buyer,
        channel_suitability=channel,
        trust_gap=trust_gap,
        owner_burden=owner_burden,
        risk=risk,
        public_noninvasive_path=public_path,
        organization_facing=org_facing,
        inclusion_decision=decision,
        reason="Organization-facing, public, owner-approval-only candidate for manual validation." if decision.startswith("include") else "Candidate needs target revision before owner approval.",
    )


def build_e14_target_batch(candidates: List[E14TargetCandidate], batch_id: str = "e14_owner_operated_readiness_review_batch") -> Dict[str, Any]:
    scored = sorted([score_e14_target(item) for item in candidates], key=lambda item: (-item.score, item.target_id))
    selected_ids = [item.target_id for item in scored if item.inclusion_decision == "include_in_owner_review_batch"][:3]
    return {
        "batch_id": batch_id,
        "proposal_only": True,
        "owner_approved": False,
        "offer": "48h AI Agent Implementation Readiness Review",
        "max_sends": len(selected_ids),
        "selected_target_ids": selected_ids,
        "scores": [item.to_dict() for item in scored],
        "contact_executed": False,
        "approval_required_before_any_contact": True,
    }


def write_e14_target_batch(repo_root: Path, candidates: List[E14TargetCandidate]) -> Path:
    batch = build_e14_target_batch(candidates)
    path = repo_root / "operations" / "external_validation" / "e14_target_batch.proposed.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
