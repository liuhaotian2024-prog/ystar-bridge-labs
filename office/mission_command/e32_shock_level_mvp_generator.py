from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import get_artifact

def build_shock_level_mvp_candidates() -> dict[str, Any]:
    return get_artifact('e32_shock_level_mvp_candidates')
