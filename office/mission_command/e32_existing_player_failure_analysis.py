from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import get_artifact

def build_existing_player_failure_analysis() -> dict[str, Any]:
    return get_artifact('e32_existing_player_failure_analysis')
