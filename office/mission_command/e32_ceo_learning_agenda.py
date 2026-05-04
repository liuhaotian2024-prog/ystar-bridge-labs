from __future__ import annotations

from typing import Any

from .e32_existing_learning_strategy_wheel_inventory import get_artifact

def build_ceo_learning_agenda() -> dict[str, Any]:
    return get_artifact("e32_ceo_learning_agenda")
