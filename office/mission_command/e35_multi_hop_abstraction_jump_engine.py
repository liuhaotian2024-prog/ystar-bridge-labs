from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_multi_hop_abstraction_jump_engine() -> dict[str, Any]:
    return get_artifact("e35_multi_hop_abstraction_jump_engine")
