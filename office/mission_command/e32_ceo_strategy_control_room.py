from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import get_artifact

def build_ceo_strategy_control_room() -> dict[str, Any]:
    return get_artifact('e32_ceo_strategy_control_room')
