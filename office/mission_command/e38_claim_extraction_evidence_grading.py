from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_claim_extraction_evidence_grading() -> dict[str, Any]:
    return get_artifact("e38_claim_extraction_evidence_grading")
