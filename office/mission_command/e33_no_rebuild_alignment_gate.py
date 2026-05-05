from __future__ import annotations

from typing import Any

from .e33_agent_action_black_box_builder import get_artifact


def build_no_rebuild_alignment_gate() -> dict[str, Any]:
    return get_artifact("e33_no_rebuild_alignment_gate")
