from __future__ import annotations

from pathlib import Path

from . import e60_market_readiness_core as core

BRIDGE_ROOT = core.BRIDGE_ROOT
write_json = core.write_json
write_md = core.write_md


def run_prior_gate_preflight(root: Path | None = None) -> dict:
    return core.build_prior_gate_preflight(root or BRIDGE_ROOT)


def write_prior_gate_preflight(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_prior_gate_preflight(root)
    write_json(root, "operations/external_validation/e60_prior_gate_preflight_result.json", data)
    write_md(root, "reports/integration/e60_prior_gate_preflight_result.md", "E60 Prior Gate Preflight", [
        f"Artifact: `{data.get('artifact_id')}`",
        f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
        f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', 'n/a'))}`",
        f"External action allowed: `{data.get('external_action_allowed', False)}`",
    ])
    return data
