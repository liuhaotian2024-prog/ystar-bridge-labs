from __future__ import annotations

from typing import Any, Mapping

from office.mission_command.b2r_capability_domains import CapabilityDecision, evaluate_capability_action


def evaluate_form_draft(envelope: Mapping[str, Any]) -> CapabilityDecision:
    return evaluate_capability_action("form_fill_draft", envelope)


def evaluate_form_submission(envelope: Mapping[str, Any]) -> CapabilityDecision:
    return evaluate_capability_action("low_risk_form_submission", envelope)
