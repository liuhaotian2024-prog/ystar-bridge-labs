from __future__ import annotations

from pathlib import Path

from . import e60_market_readiness_core as core

BRIDGE_ROOT = core.BRIDGE_ROOT
write_json = core.write_json
write_md = core.write_md

load_e60_state_for_brain = core.load_e60_state_for_brain


def run_ceo_brain_readback_smoke(root: Path | None = None) -> dict:
    return core.run_ceo_brain_readback_smoke(root or BRIDGE_ROOT)


def write_ceo_brain_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_ceo_brain_readback_smoke(root)
    write_json(root, "operations/external_validation/e60_ceo_brain_readback_smoke_result.json", data)
    write_md(root, "reports/integration/e60_ceo_brain_readback_smoke_result.md", "E60 CEO Brain Readback Smoke", [
        f"Artifact: `{data.get('artifact_id')}`",
        f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
        f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', 'n/a'))}`",
        f"External action allowed: `{data.get('external_action_allowed', False)}`",
    ])
    return data
