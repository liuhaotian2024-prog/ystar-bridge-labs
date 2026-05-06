from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, controlled_public_read_smoke_probe, write_json, write_md


def run_controlled_public_read_smoke_probe(root: Path | None = None) -> dict:
    return controlled_public_read_smoke_probe()


def write_controlled_public_read_smoke_probe(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_controlled_public_read_smoke_probe(root)
    write_json(root, "operations/external_validation/e61_live_public_read_smoke_probe_result.json", data)
    write_md(root, "reports/integration/e61_live_public_read_smoke_probe_result.md", "E61 Live Public-Read Smoke Probe Result", [
        f"Smoke status: `{data['smoke_probe_status']}`",
        f"Final status: `{data['final_status']}`",
    ])
    return data
