from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_public_readonly_evidence_sprint_design() -> dict[str, Any]:
    return get_artifact("e37_public_readonly_evidence_sprint_design")
