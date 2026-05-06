from __future__ import annotations

from pathlib import Path

from . import e60_market_readiness_core as core

BRIDGE_ROOT = core.BRIDGE_ROOT
write_json = core.write_json
write_md = core.write_md


def run_market_readiness_anti_drift_gate(root: Path | None = None) -> dict:
    return core.run_market_readiness_anti_drift_gate()


def write_market_readiness_anti_drift_gate(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_market_readiness_anti_drift_gate(root)
    write_json(root, "operations/external_validation/e60_market_readiness_anti_drift_gate_result.json", data)
    write_md(root, "reports/integration/e60_market_readiness_anti_drift_gate_result.md", "E60 Market Readiness Anti-Drift Gate", [
        f"Artifact: `{data.get('artifact_id')}`",
        f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
        f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', 'n/a'))}`",
        f"External action allowed: `{data.get('external_action_allowed', False)}`",
    ])
    return data
