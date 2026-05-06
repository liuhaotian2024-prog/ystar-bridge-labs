from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_reuse_first_growth_audit(root: Path | None = None) -> dict:
    return core.build_reuse_first_growth_audit(root or core.BRIDGE_ROOT)


def write_reuse_first_growth_audit(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_reuse_first_growth_audit(root)
    core.write_json(root, "operations/external_validation/e63_reuse_first_growth_audit.json", data)
    return data
