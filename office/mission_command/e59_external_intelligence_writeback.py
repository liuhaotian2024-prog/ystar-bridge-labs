from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, write_learning_writeback


def write_external_intelligence_writeback(output_root: Path | None = None) -> dict:
    return write_learning_writeback(output_root or BRIDGE_ROOT)

