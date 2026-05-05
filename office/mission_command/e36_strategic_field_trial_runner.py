from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_strategic_field_trial_results() -> dict[str, Any]:
    return get_artifact("e36_strategic_field_trial_results")
