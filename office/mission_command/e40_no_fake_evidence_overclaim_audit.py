from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_no_fake_evidence_overclaim_audit() -> dict[str, Any]:
    return get_artifact("e40_no_fake_evidence_overclaim_audit")
