from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List


FEEDBACK_PATH = Path("operations/external_validation/e8_feedback_events.json")


@dataclass(frozen=True)
class E8FeedbackEvent:
    feedback_id: str
    target_id: str
    received_at: str
    source_channel: str
    response_type: str
    verbatim_or_summary: str
    price_signal: str
    workflow_signal: str
    urgency_signal: str
    trust_gap_signal: str
    next_step_requested: str
    owner_entered: bool
    external_action_reference: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def feedback_event_from_dict(data: Dict[str, Any]) -> E8FeedbackEvent:
    return E8FeedbackEvent(
        feedback_id=str(data.get("feedback_id", "")),
        target_id=str(data.get("target_id", "")),
        received_at=str(data.get("received_at", "")),
        source_channel=str(data.get("source_channel", "")),
        response_type=str(data.get("response_type", "")),
        verbatim_or_summary=str(data.get("verbatim_or_summary", "")),
        price_signal=str(data.get("price_signal", "")),
        workflow_signal=str(data.get("workflow_signal", "")),
        urgency_signal=str(data.get("urgency_signal", "")),
        trust_gap_signal=str(data.get("trust_gap_signal", "")),
        next_step_requested=str(data.get("next_step_requested", "")),
        owner_entered=bool(data.get("owner_entered", False)),
        external_action_reference=str(data.get("external_action_reference", "")),
    )


def load_e8_feedback_events(repo_root: Path) -> List[E8FeedbackEvent]:
    path = repo_root / FEEDBACK_PATH
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("feedback_events", payload if isinstance(payload, list) else [])
    return [feedback_event_from_dict(item) for item in raw]


def validate_feedback_event(event: E8FeedbackEvent | Dict[str, Any]) -> List[str]:
    item = event if isinstance(event, E8FeedbackEvent) else feedback_event_from_dict(event)
    errors: List[str] = []
    if not item.feedback_id:
        errors.append("missing_feedback_id")
    if not item.target_id:
        errors.append("missing_target_id")
    if not item.response_type:
        errors.append("missing_response_type")
    if item.response_type == "opt_out" and item.next_step_requested:
        errors.append("opt_out_must_not_have_next_step")
    return errors


def render_e8_feedback_capture_report(events: List[E8FeedbackEvent]) -> str:
    lines = ["# E8 Feedback Capture Report", "", f"- feedback_captured: {bool(events)}", f"- feedback_event_count: {len(events)}"]
    if not events:
        lines.extend(["- feedback_status: no feedback captured; do not infer validation success.", "- external_action_executed: false"])
    else:
        lines.extend(["", "## Events"])
        for event in events:
            lines.append(f"- {event.feedback_id}: {event.response_type} / target={event.target_id} / owner_entered={event.owner_entered}")
    return "\n".join(lines)
