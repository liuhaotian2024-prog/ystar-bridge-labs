from __future__ import annotations

from pathlib import Path

from . import e64_dual_axis_revenue_core as core


def run_e64_dual_axis_revenue_route_universe(root: Path | None = None) -> dict:
    return core.build_dual_axis_revenue_route_universe(root or core.BRIDGE_ROOT)


def write_e64_dual_axis_revenue_route_universe(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_e64_dual_axis_revenue_route_universe(root)
    core.write_json(root, "operations/external_validation/e64_dual_axis_revenue_route_universe.json", data)
    return data
