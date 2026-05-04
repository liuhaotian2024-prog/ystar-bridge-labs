from __future__ import annotations

from typing import Any

from .e31_existing_real_world_observation_wheel_inventory import get_artifact

def build_public_source_selection() -> dict[str, Any]:
    return get_artifact("e31_public_source_selection")
