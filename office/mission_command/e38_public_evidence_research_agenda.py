from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_public_evidence_research_agenda() -> dict[str, Any]:
    return get_artifact("e38_public_evidence_research_agenda")
