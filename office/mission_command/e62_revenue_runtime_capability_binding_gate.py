from __future__ import annotations

from pathlib import Path

from . import e62_revenue_runtime_core as core


def run_revenue_runtime_capability_binding_gate(root: Path | None = None) -> dict:
    return core.run_capability_binding_gate(root or core.BRIDGE_ROOT)


def write_revenue_runtime_capability_binding_gate(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_revenue_runtime_capability_binding_gate(root)
    core.write_json(root, "operations/external_validation/e62_revenue_runtime_capability_binding_gate_result.json", data)
    return data
