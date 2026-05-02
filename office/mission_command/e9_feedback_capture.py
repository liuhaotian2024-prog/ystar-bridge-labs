from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List


E9_FEEDBACK_EVENTS_PATH = Path("operations/external_validation/e9_feedback_events.json")
E9_FEEDBACK_EVENTS_TEMPLATE_PATH = Path("operations/external_validation/e9_feedback_events.template.json")


@dataclass(frozen=True)
class E9FeedbackEvent:
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


def e9_feedback_event_from_dict(data: Dict[str, Any]) -> E9FeedbackEvent:
    return E9FeedbackEvent(
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


def load_e9_feedback_events(repo_root: Path) -> List[E9FeedbackEvent]:
    path = repo_root / E9_FEEDBACK_EVENTS_PATH
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("feedback_events", payload if isinstance(payload, list) else [])
    return [e9_feedback_event_from_dict(item) for item in raw]


def validate_e9_feedback_event(event: E9FeedbackEvent | Dict[str, Any]) -> List[str]:
    item = event if isinstance(event, E9FeedbackEvent) else e9_feedback_event_from_dict(event)
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


def render_e9_feedback_events_template() -> str:
    payload = {
        "feedback_events": [
            {
                "feedback_id": "feedback_001",
                "target_id": "target_001",
                "received_at": "YYYY-MM-DDTHH:MM:SSZ",
                "source_channel": "owner_selected_email",
                "response_type": "asks_price",
                "verbatim_or_summary": "Owner-entered summary of a real response.",
                "price_signal": "Asked whether the 48h blueprint has a fixed price.",
                "workflow_signal": "",
                "urgency_signal": "",
                "trust_gap_signal": "",
                "next_step_requested": "",
                "owner_entered": True,
                "external_action_reference": "owner_operated_handoff",
            }
        ]
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def write_e9_feedback_events_template(repo_root: Path) -> Path:
    path = repo_root / E9_FEEDBACK_EVENTS_TEMPLATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_e9_feedback_events_template() + "\n", encoding="utf-8")
    return path


def render_e9_feedback_capture_report(events: List[E9FeedbackEvent]) -> str:
    lines = ["# E9 Feedback Capture Report", "", f"- feedback_captured: {bool(events)}", f"- feedback_event_count: {len(events)}"]
    if not events:
        lines.extend(["- feedback_status: no feedback captured; do not infer validation success.", "- invented_feedback: false"])
    else:
        lines.extend(["", "## Events"])
        for event in events:
            lines.append(f"- {event.feedback_id}: {event.response_type} / target={event.target_id} / owner_entered={event.owner_entered}")
    return "\n".join(lines)
