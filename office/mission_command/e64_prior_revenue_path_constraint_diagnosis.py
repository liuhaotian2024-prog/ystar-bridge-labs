from __future__ import annotations

from pathlib import Path

from . import e64_dual_axis_revenue_core as core


def run_e64_prior_revenue_path_constraint_diagnosis(root: Path | None = None) -> dict:
    return core.build_prior_revenue_path_constraint_diagnosis(root or core.BRIDGE_ROOT)


def write_e64_prior_revenue_path_constraint_diagnosis(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_e64_prior_revenue_path_constraint_diagnosis(root)
    core.write_json(root, "operations/external_validation/e64_prior_revenue_path_constraint_diagnosis.json", data)
    return data
