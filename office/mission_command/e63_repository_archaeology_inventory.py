from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_repository_archaeology_inventory(root: Path | None = None) -> dict:
    return core.build_repository_archaeology_inventory(root or core.BRIDGE_ROOT)


def write_repository_archaeology_inventory(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_repository_archaeology_inventory(root)
    core.write_json(root, "operations/external_validation/e63_repository_archaeology_inventory.json", data)
    return data
