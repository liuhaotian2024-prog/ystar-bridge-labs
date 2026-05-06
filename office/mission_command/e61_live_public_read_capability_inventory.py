from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, build_capability_inventory, write_json, write_md


def run_live_public_read_capability_inventory(root: Path | None = None) -> dict:
    return build_capability_inventory(root or BRIDGE_ROOT)


def write_live_public_read_capability_inventory(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_live_public_read_capability_inventory(root)
    write_json(root, "operations/external_validation/e61_live_public_read_capability_inventory.json", data)
    write_md(root, "reports/integration/e61_live_public_read_capability_inventory.md", "E61 Live Public-Read Capability Inventory", [
        f"Discovered components: `{len(data['discovered_components'])}`",
        f"Failure appears to be: `{', '.join(data['failure_appears_to_be'])}`",
    ])
    return data
