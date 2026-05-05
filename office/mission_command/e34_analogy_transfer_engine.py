from __future__ import annotations

from typing import Any

from .e34_ceo_decision_failure_diagnosis import get_artifact


def build_analogy_transfer_engine() -> dict[str, Any]:
    return get_artifact("e34_analogy_transfer_engine")
