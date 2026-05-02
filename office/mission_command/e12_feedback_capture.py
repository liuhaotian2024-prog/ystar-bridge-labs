from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


E12_FEEDBACK_EVENTS_PATH = Path("operations/external_validation/e12_feedback_events.json")
E12_FEEDBACK_TEMPLATE_PATH = Path("operations/external_validation/e12_feedback_events.template.json")

POSITIVE_TYPES = {"interested", "asks_price", "asks_example", "offers_workflow", "says_would_pay", "asks_followup", "referral"}
NEGATIVE_TYPES = {"rejects_no_urgency", "rejects_price", "says_tools_solve_it", "wants_implementation_not_blueprint", "opt_out"}
VALID_RESPONSE_TYPES = POSITIVE_TYPES | NEGATIVE_TYPES | {"no_response", "neutral"}


@dataclass(frozen=True)
class E12FeedbackEvent:
    feedback_id: str
    target_id: str
    received_at: str
    source_channel: str
    response_type: str
    verbatim_or_summary: str
    price_signal: str = ""
    workflow_signal: str = ""
    urgency_signal: str = ""
    trust_gap_signal: str = ""
    next_step_requested: str = ""
    owner_entered: bool = False
    external_action_reference: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E12FeedbackCapture:
    feedback_file_present: bool
    feedback_captured: bool
    feedback_valid: bool
    events: List[E12FeedbackEvent] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["events"] = [event.to_dict() for event in self.events]
        return data


def write_e12_feedback_template(repo_root: Path) -> Path:
    path = repo_root / E12_FEEDBACK_TEMPLATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "template_only": True,
        "events": [
            {
                "feedback_id": "OWNER_TO_FILL",
                "target_id": "cand_alicelabs_alicelabs",
                "received_at": "OWNER_TO_FILL_ISO8601",
                "source_channel": "owner_operated_handoff",
                "response_type": "interested | asks_price | asks_example | offers_workflow | says_would_pay | asks_followup | referral | rejects_no_urgency | rejects_price | says_tools_solve_it | wants_implementation_not_blueprint | opt_out | no_response",
                "verbatim_or_summary": "OWNER_ENTERED_SUMMARY",
                "price_signal": "",
                "workflow_signal": "",
                "urgency_signal": "",
                "trust_gap_signal": "",
                "next_step_requested": "",
                "owner_entered": True,
                "external_action_reference": "owner_operated_handoff_or_e12_action_ledger_reference",
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_e12_feedback_event(event: Dict[str, Any], *, action_ledger_exists: bool) -> List[str]:
    errors: List[str] = []
    response_type = event.get("response_type")
    if response_type not in VALID_RESPONSE_TYPES:
        errors.append("invalid_response_type")
    if not event.get("feedback_id") or "OWNER_TO_FILL" in str(event.get("feedback_id")):
        errors.append("feedback_id_required")
    if not event.get("target_id"):
        errors.append("target_id_required")
    if not event.get("verbatim_or_summary") or "OWNER_ENTERED" in str(event.get("verbatim_or_summary")):
        errors.append("verbatim_or_summary_required")
    owner_entered = event.get("owner_entered") is True
    has_action_ref = bool(event.get("external_action_reference")) and "OWNER_TO_FILL" not in str(event.get("external_action_reference"))
    if not owner_entered and not (action_ledger_exists and has_action_ref):
        errors.append("feedback_must_be_owner_entered_or_reference_action_ledger")
    if response_type == "no_response" and not (owner_entered or action_ledger_exists):
        errors.append("no_response_requires_action_ledger_or_owner_entered_event")
    return errors


def load_e12_feedback_capture(repo_root: Path, *, action_ledger_exists: bool = False) -> E12FeedbackCapture:
    write_e12_feedback_template(repo_root)
    path = repo_root / E12_FEEDBACK_EVENTS_PATH
    if not path.exists():
        return E12FeedbackCapture(False, False, False, [], ["missing_e12_feedback_events"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("template_only"):
        return E12FeedbackCapture(True, False, False, [], ["feedback_template_is_not_feedback"])
    events: List[E12FeedbackEvent] = []
    errors: List[str] = []
    for item in payload.get("events", []):
        event_errors = validate_e12_feedback_event(item, action_ledger_exists=action_ledger_exists)
        errors.extend(f"{item.get('feedback_id', 'unknown')}: {error}" for error in event_errors)
        if not event_errors:
            events.append(E12FeedbackEvent(**item))
    return E12FeedbackCapture(True, bool(events), not errors and bool(events), events, list(dict.fromkeys(errors)))


def render_e12_feedback_capture_report(capture: E12FeedbackCapture) -> str:
    lines = [
        "# E12 Feedback Capture Report",
        "",
        f"- feedback_file_present: {str(capture.feedback_file_present).lower()}",
        f"- feedback_captured: {str(capture.feedback_captured).lower()}",
        f"- feedback_valid: {str(capture.feedback_valid).lower()}",
        f"- feedback_event_count: {len(capture.events)}",
        f"- errors: {', '.join(capture.errors) or 'none'}",
        "",
        "## Events",
    ]
    for event in capture.events:
        lines.extend(
            [
                f"### {event.feedback_id}",
                f"- target_id: {event.target_id}",
                f"- response_type: {event.response_type}",
                f"- owner_entered: {str(event.owner_entered).lower()}",
                f"- summary: {event.verbatim_or_summary}",
                "",
            ]
        )
    if not capture.events:
        lines.append("- none")
    return "\n".join(lines).rstrip()

