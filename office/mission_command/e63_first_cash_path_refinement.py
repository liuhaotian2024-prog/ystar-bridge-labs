from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_first_cash_path_refinement(root: Path | None = None) -> dict:
    return core.build_first_cash_path_refinement(root or core.BRIDGE_ROOT)


def write_first_cash_path_refinement(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_first_cash_path_refinement(root)
    core.write_json(root, "operations/external_validation/e63_first_cash_path_refinement.json", data)
    return data
