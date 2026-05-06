from __future__ import annotations

from pathlib import Path

from . import e60_market_readiness_core as core

BRIDGE_ROOT = core.BRIDGE_ROOT
write_json = core.write_json
write_md = core.write_md


def run_counterfactual_market_readiness_matrix(root: Path | None = None) -> dict:
    return core.build_counterfactual_market_readiness_matrix(root or BRIDGE_ROOT)


def write_counterfactual_market_readiness_matrix(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_counterfactual_market_readiness_matrix(root)
    write_json(root, "operations/external_validation/e60_counterfactual_market_readiness_matrix.json", data)
    write_md(root, "reports/integration/e60_counterfactual_market_readiness_matrix.md", "E60 Counterfactual Market Readiness Matrix", [
        f"Artifact: `{data.get('artifact_id')}`",
        f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
        f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', 'n/a'))}`",
        f"External action allowed: `{data.get('external_action_allowed', False)}`",
    ])
    return data
