from __future__ import annotations

from typing import Any

from .e33_agent_action_black_box_builder import get_artifact


def build_ceo_brain_black_box_update() -> dict[str, Any]:
    return get_artifact("e33_ceo_brain_black_box_update")
