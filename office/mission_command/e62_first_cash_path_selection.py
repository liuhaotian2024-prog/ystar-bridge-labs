from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_first_cash_path_selection(root: Path | None = None) -> dict:
    return core.build_first_cash_path_selection(root or core.BRIDGE_ROOT)


def write_first_cash_path_selection(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_first_cash_path_selection(root)
    core.write_json(root, "operations/external_validation/e62_first_cash_path_selection.json", data)
    return data
