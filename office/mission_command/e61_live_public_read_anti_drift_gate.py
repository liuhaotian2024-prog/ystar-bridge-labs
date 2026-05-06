from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, run_anti_drift_gate, write_json, write_md


def run_live_public_read_anti_drift_gate(root: Path | None = None) -> dict:
    return run_anti_drift_gate()


def write_live_public_read_anti_drift_gate(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_live_public_read_anti_drift_gate(root)
    write_json(root, "operations/external_validation/e61_live_public_read_anti_drift_gate_result.json", data)
    write_md(root, "reports/integration/e61_live_public_read_anti_drift_gate_result.md", "E61 Live Public-Read Anti-Drift Gate", [f"Passed: `{data['passed']}`"])
    return data
