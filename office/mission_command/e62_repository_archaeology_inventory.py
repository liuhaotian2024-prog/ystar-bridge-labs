from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_repository_archaeology_inventory(root: Path | None = None) -> dict:
    return core.build_repository_archaeology_inventory(root or core.BRIDGE_ROOT)


def write_repository_archaeology_inventory(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_repository_archaeology_inventory(root)
    core.write_json(root, "operations/external_validation/e62_repository_archaeology_inventory.json", data)
    core.write_md(root, "reports/integration/e62_repository_archaeology_inventory.md", "E62 Repository Archaeology Inventory", [
        f"Assets discovered: `{data.get('asset_count')}`.",
        f"Revenue-runtime supporting assets: `{data.get('revenue_runtime_supporting_assets_count')}`.",
        "Reuse-first inventory completed before adding E62 runtime recenter logic.",
    ])
    return data
