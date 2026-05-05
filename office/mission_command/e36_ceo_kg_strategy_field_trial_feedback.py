from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_ceo_kg_strategy_field_trial_feedback() -> dict[str, Any]:
    return get_artifact("e36_ceo_kg_strategy_field_trial_feedback")
