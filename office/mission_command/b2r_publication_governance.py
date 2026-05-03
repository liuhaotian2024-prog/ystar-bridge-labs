from __future__ import annotations

from typing import Any, Mapping

from office.mission_command.b2r_capability_domains import CapabilityDecision, evaluate_capability_action


def evaluate_publication_draft(envelope: Mapping[str, Any]) -> CapabilityDecision:
    return evaluate_capability_action("publication_draft", envelope)


def evaluate_governed_publication(envelope: Mapping[str, Any]) -> CapabilityDecision:
    return evaluate_capability_action("governed_publication", envelope)
