from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_source_quality_evidence_burden_evaluator() -> dict[str, Any]:
    return get_artifact("e39_source_quality_evidence_burden_evaluator")
