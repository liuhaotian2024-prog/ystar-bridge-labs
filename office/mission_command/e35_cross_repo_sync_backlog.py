from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_cross_repo_sync_backlog() -> dict[str, Any]:
    return get_artifact("e35_cross_repo_sync_backlog")
