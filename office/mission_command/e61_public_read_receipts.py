from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, build_public_read_receipts, write_json


def run_public_read_receipts(root: Path | None = None) -> dict:
    return build_public_read_receipts(root or BRIDGE_ROOT)


def write_public_read_receipts(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_public_read_receipts(root)
    write_json(root, "operations/external_validation/e61_public_read_receipts.json", data)
    return data
