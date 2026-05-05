from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import get_artifact

def build_future_frontier_mvp_policy() -> dict[str, Any]:
    return get_artifact('e32_future_frontier_mvp_policy')
