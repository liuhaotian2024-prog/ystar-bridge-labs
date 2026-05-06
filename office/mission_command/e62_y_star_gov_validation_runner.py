from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_y_star_gov_validation(root: Path | None = None) -> dict:
    return core.run_y_star_gov_validation(root or core.BRIDGE_ROOT)


def write_y_star_gov_validation(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_y_star_gov_validation(root)
    core.write_json(root, "operations/external_validation/e62_y_star_gov_validation_result.json", data)
    return data
