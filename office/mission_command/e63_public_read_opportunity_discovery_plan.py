from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_public_read_opportunity_discovery_plan(root: Path | None = None) -> dict:
    return core.build_public_read_opportunity_discovery_plan(root or core.BRIDGE_ROOT)


def write_public_read_opportunity_discovery_plan(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_public_read_opportunity_discovery_plan(root)
    core.write_json(root, "operations/external_validation/e63_public_read_opportunity_discovery_plan.json", data)
    return data
