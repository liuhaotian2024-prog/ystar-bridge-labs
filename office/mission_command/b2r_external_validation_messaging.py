from __future__ import annotations

from typing import Any, Mapping

from office.mission_command.b2r_capability_domains import (
    CapabilityDecision,
    evaluate_capability_action,
    stop_required_for_event,
)


def evaluate_external_validation_message(envelope: Mapping[str, Any]) -> CapabilityDecision:
    return evaluate_capability_action("external_validation_message", envelope)


def should_stop_for_feedback_event(event_type: str) -> bool:
    return stop_required_for_event(event_type)
