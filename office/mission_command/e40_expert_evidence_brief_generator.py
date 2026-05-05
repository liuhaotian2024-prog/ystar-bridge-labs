from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_expert_evidence_briefs() -> dict[str, Any]:
    return get_artifact("e40_expert_evidence_briefs")
