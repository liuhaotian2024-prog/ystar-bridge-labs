from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_revenue_path_candidate_matrix(root: Path | None = None) -> dict:
    return core.build_revenue_path_candidate_matrix(root or core.BRIDGE_ROOT)


def write_revenue_path_candidate_matrix(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_revenue_path_candidate_matrix(root)
    core.write_json(root, "operations/external_validation/e62_revenue_path_candidate_matrix.json", data)
    return data
