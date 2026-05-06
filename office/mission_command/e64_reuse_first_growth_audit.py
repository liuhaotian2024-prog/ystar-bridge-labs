from __future__ import annotations

from pathlib import Path

from . import e64_dual_axis_revenue_core as core


def run_e64_reuse_first_growth_audit(root: Path | None = None) -> dict:
    return core.build_reuse_first_growth_audit(root or core.BRIDGE_ROOT)


def write_e64_reuse_first_growth_audit(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_e64_reuse_first_growth_audit(root)
    core.write_json(root, "operations/external_validation/e64_reuse_first_growth_audit.json", data)
    return data
