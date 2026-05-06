from __future__ import annotations

from pathlib import Path

from . import e64_dual_axis_revenue_core as core


def run_e64_dual_axis_cross_selection_matrix(root: Path | None = None) -> dict:
    return core.build_dual_axis_cross_selection_matrix(root or core.BRIDGE_ROOT)


def write_e64_dual_axis_cross_selection_matrix(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_e64_dual_axis_cross_selection_matrix(root)
    core.write_json(root, "operations/external_validation/e64_dual_axis_cross_selection_matrix.json", data)
    return data
