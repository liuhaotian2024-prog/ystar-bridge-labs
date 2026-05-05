from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import get_artifact

def build_frontier_research_run() -> dict[str, Any]:
    return get_artifact('e32_frontier_research_run')
