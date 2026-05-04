from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


E18_TARGET_STATUSES = [
    "ready_for_owner_review",
    "needs_more_evidence",
    "weak_fit",
    "suppress_or_do_not_contact",
    "blocked_missing_source",
]


@dataclass(frozen=True)
class E18BatchCandidate:
    action_id: str
    target_id: str
    target_name: str
    role: str
    status: str
    evidence_basis: List[str]
    offer: str
    buyer_pain_hypothesis: str
    selection_reason: str
    risk_tier: str
    capability_domain: str
    ledger_id: str
    feedback_event_id: str
    missing_fields: List[str]
    suppression_reason: str
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _canonical_risk_tier(value: str) -> str:
    if "tier 5" in value.lower() or "external validation" in value.lower():
        return "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"
    return value or "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"


def classify_candidate(action: Dict[str, Any]) -> str:
    role = str(action.get("role", "candidate"))
    missing = list(action.get("missing_fields", []))
    evidence = list(action.get("target_evidence_basis", []))
    reason = str(action.get("exclusion_or_suppression_reason", ""))
    text = " ".join(
        [
            str(action.get("target_name", "")),
            str(action.get("selection_reason", "")),
            str(action.get("buyer_pain_hypothesis", "")),
            str(action.get("offer_thesis", "")),
            role,
            reason,
        ]
    ).lower()
    if role in {"suppression_candidate", "suppressed"} or "suppress" in text or "do not contact" in text:
        return "suppress_or_do_not_contact"
    if missing:
        return "needs_more_evidence"
    if not evidence:
        return "blocked_missing_source"
    fit_terms = ["implementation", "readiness", "governance", "agent", "workflow", "automation", "consult"]
    if role in {"primary", "fallback"} and any(term in text for term in fit_terms):
        return "ready_for_owner_review"
    return "weak_fit"


def build_revenue_validation_batch(c3_batch: Dict[str, Any], e17_queue: Dict[str, Any]) -> Dict[str, Any]:
    e17_status_by_action = {item.get("action_id"): item.get("status") for item in e17_queue.get("entries", [])}
    candidates: List[E18BatchCandidate] = []
    for action in c3_batch.get("actions", []):
        status = classify_candidate(action)
        if e17_status_by_action.get(action.get("action_id")) == "current_selected_action":
            status = "ready_for_owner_review"
        candidates.append(
            E18BatchCandidate(
                action_id=str(action.get("action_id", "")),
                target_id=str(action.get("target_id", "")),
                target_name=str(action.get("target_name", "")),
                role=str(action.get("role", "candidate")),
                status=status,
                evidence_basis=list(action.get("target_evidence_basis", [])),
                offer=str(action.get("offer_thesis", "48h AI Agent Implementation Readiness Review")),
                buyer_pain_hypothesis=str(action.get("buyer_pain_hypothesis", "")),
                selection_reason=str(action.get("selection_reason", "")),
                risk_tier=_canonical_risk_tier(str(action.get("risk_tier", ""))),
                capability_domain=str(action.get("capability_domain", "external_validation_message")),
                ledger_id=str(action.get("ledger_id", "")),
                feedback_event_id=str(action.get("feedback_event_id", "")),
                missing_fields=list(action.get("missing_fields", [])),
                suppression_reason=str(action.get("exclusion_or_suppression_reason", "")),
            )
        )
    ready = [item for item in candidates if item.status == "ready_for_owner_review"]
    blocked = [item for item in candidates if item.status != "ready_for_owner_review"]
    return {
        "artifact_id": "e18_revenue_validation_batch",
        "batch_id": "e18_first_revenue_validation_batch",
        "source_batch_id": c3_batch.get("batch_id"),
        "selection_policy": "existing_repo_evidence_only_no_scraping_no_fake_targets",
        "lead_offer": "48h AI Agent Implementation Readiness Review",
        "candidate_count": len(candidates),
        "ready_for_owner_review_count": len(ready),
        "blocked_or_not_ready_count": len(blocked),
        "max_owner_manual_sends": min(3, len(ready)),
        "owner_approved": False,
        "external_action_executed": False,
        "candidates": [item.to_dict() for item in candidates],
    }


def render_revenue_validation_batch(batch: Dict[str, Any]) -> str:
    lines = [
        "# E18 Revenue Validation Batch Runtime",
        "",
        "E18 builds a small owner-approval-gated revenue validation batch from existing repo evidence only.",
        "",
        f"- batch_id: {batch['batch_id']}",
        f"- lead_offer: {batch['lead_offer']}",
        f"- candidate_count: {batch['candidate_count']}",
        f"- ready_for_owner_review_count: {batch['ready_for_owner_review_count']}",
        f"- max_owner_manual_sends: {batch['max_owner_manual_sends']}",
        "- external_action_executed: false",
        "",
        "## Candidates",
    ]
    for item in batch["candidates"]:
        lines.extend(
            [
                f"### {item['target_name']}",
                f"- action_id: {item['action_id']}",
                f"- status: {item['status']}",
                f"- role: {item['role']}",
                f"- evidence_basis: {', '.join(item['evidence_basis']) if item['evidence_basis'] else 'missing'}",
                f"- selection_reason: {item['selection_reason']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
