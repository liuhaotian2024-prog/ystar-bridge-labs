from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, run_completion_gate, write_json, write_md


def run_e61_completion_gate(root: Path | None = None) -> dict:
    return run_completion_gate(root or BRIDGE_ROOT)


def write_e61_completion_gate(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_e61_completion_gate(root)
    write_json(root, "operations/external_validation/e61_completion_gate_result.json", data)
    write_md(root, "reports/integration/e61_completion_gate_result.md", "E61 Completion Gate", [
        f"Gate passed: `{data['gate_passed']}`",
        f"Final status: `{data['final_status']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
    ])
    return data
