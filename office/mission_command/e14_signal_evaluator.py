from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .evidence_signal_router import EvidenceClaimType, EvidenceSignalType, evidence_supports_claim


@dataclass(frozen=True)
class E14ValidationSignalReport:
    classification: str
    approval_present: bool
    action_ledger_exists: bool
    feedback_events_exist: bool
    paid_signal_candidate: bool
    e15_entry_allowed: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_e14_validation_signal(
    *,
    approval_present: bool = False,
    action_ledger_events: List[Dict[str, Any]] | None = None,
    feedback_events: List[Dict[str, Any]] | None = None,
) -> E14ValidationSignalReport:
    action_ledger_events = action_ledger_events or []
    feedback_events = feedback_events or []
    if not approval_present:
        return E14ValidationSignalReport("no_approval", False, bool(action_ledger_events), bool(feedback_events), False, False, "Owner approval packet is request-only; no approval has been granted.")
    if not action_ledger_events:
        return E14ValidationSignalReport("approved_but_not_executed", True, False, bool(feedback_events), False, False, "Owner approval exists but no valid manual action ledger exists.")
    if not feedback_events:
        return E14ValidationSignalReport("executed_but_no_response_yet", True, True, False, False, False, "Manual action exists but no owner-entered feedback event has been captured.")
    paid_candidate = any(bool(event.get("paid_signal_candidate")) for event in feedback_events)
    feedback_types = {str(event.get("feedback_type")) for event in feedback_events}
    if paid_candidate:
        classification = "paid_signal_candidate"
    elif "strong_positive" in feedback_types:
        classification = "strong_positive"
    elif "weak_positive" in feedback_types:
        classification = "weak_positive"
    elif "negative" in feedback_types:
        classification = "negative"
    elif "no_response_after_valid_action" in feedback_types:
        classification = "no_response_after_valid_action"
    elif "objection_only" in feedback_types:
        classification = "objection_only"
    else:
        classification = "neutral"
    return E14ValidationSignalReport(
        classification=classification,
        approval_present=True,
        action_ledger_exists=True,
        feedback_events_exist=True,
        paid_signal_candidate=paid_candidate,
        e15_entry_allowed=classification in {"strong_positive", "paid_signal_candidate"},
        reason="E15 requires valid owner approval, action ledger, and owner-entered feedback; public evidence alone is insufficient.",
    )


def public_evidence_is_e14_validation_feedback() -> bool:
    return evidence_supports_claim(EvidenceSignalType.PUBLIC_MARKET_EVIDENCE, EvidenceClaimType.VALIDATION_RESULT)


def write_e14_validation_signal_report(repo_root: Path) -> Path:
    report = evaluate_e14_validation_signal()
    path = repo_root / "operations" / "external_validation" / "e14_validation_signal_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
