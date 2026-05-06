from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, run_y_star_gov_validation, write_json, write_md


def run_e61_y_star_gov_validation(root: Path | None = None) -> dict:
    return run_y_star_gov_validation()


def write_e61_y_star_gov_validation(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_e61_y_star_gov_validation(root)
    write_json(root, "operations/external_validation/e61_y_star_gov_validation_result.json", data)
    write_md(root, "reports/integration/e61_y_star_gov_validation_result.md", "E61 Y-star-gov Validation", [f"Passed: `{data['passed']}`"])
    return data
