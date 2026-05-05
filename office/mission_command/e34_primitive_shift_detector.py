from __future__ import annotations

from typing import Any

from .e34_ceo_decision_failure_diagnosis import get_artifact


def build_primitive_shift_detector() -> dict[str, Any]:
    return get_artifact("e34_primitive_shift_detector")
