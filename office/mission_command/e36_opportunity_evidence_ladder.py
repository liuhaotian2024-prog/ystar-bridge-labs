from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_opportunity_evidence_ladder() -> dict[str, Any]:
    return get_artifact("e36_opportunity_evidence_ladder")
