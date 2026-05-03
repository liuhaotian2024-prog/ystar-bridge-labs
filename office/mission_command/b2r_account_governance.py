from __future__ import annotations

from typing import Any, Mapping

from office.mission_command.b2r_capability_domains import CapabilityDecision, evaluate_capability_action


def evaluate_account_creation(envelope: Mapping[str, Any]) -> CapabilityDecision:
    return evaluate_capability_action("low_risk_account_creation", envelope)
