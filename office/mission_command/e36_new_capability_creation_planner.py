from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_new_capability_creation_planner() -> dict[str, Any]:
    return get_artifact("e36_new_capability_creation_planner")
