from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_contradiction_graph() -> dict[str, Any]:
    return get_artifact("e39_contradiction_graph")


def build_unsupported_claim_downgrade_register() -> dict[str, Any]:
    return get_artifact("e39_unsupported_claim_downgrade_register")
