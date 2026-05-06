from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_public_read_source_receipts(root: Path | None = None) -> dict:
    return core.build_public_read_source_receipts(root or core.BRIDGE_ROOT)


def write_public_read_source_receipts(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_public_read_source_receipts(root)
    core.write_json(root, "operations/external_validation/e63_public_read_source_receipts.json", data)
    core.write_jsonl(root, "operations/external_validation/e63_public_read_source_receipts.jsonl", data["receipts"])
    return data
