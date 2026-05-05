from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import get_artifact

def build_world_fracture_map() -> dict[str, Any]:
    return get_artifact('e32_world_fracture_institutional_void_map')
