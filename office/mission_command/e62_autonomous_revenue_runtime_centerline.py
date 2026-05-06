from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_autonomous_revenue_runtime_centerline(root: Path | None = None) -> dict:
    return core.build_autonomous_revenue_runtime_centerline(root or core.BRIDGE_ROOT)


def write_autonomous_revenue_runtime_centerline(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_autonomous_revenue_runtime_centerline(root)
    core.write_json(root, "operations/external_validation/e62_autonomous_revenue_runtime_centerline.json", data)
    return data
