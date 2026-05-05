from __future__ import annotations

from typing import Any

from .e33_agent_action_black_box_builder import get_artifact


def build_owner_validation_route() -> dict[str, Any]:
    return get_artifact("e33_owner_validation_route")
