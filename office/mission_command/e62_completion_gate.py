from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_e62_completion_gate(root: Path | None = None) -> dict:
    return core.build_completion_gate(root or core.BRIDGE_ROOT)


def write_e62_completion_gate(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_e62_completion_gate(root)
    core.write_json(root, "operations/external_validation/e62_completion_gate_result.json", data)
    return data
