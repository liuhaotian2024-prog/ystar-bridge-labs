from __future__ import annotations

from pathlib import Path

from . import e60_market_readiness_core as core

BRIDGE_ROOT = core.BRIDGE_ROOT
write_json = core.write_json
write_md = core.write_md


def run_market_readiness_writeback(root: Path | None = None) -> dict:
    return core.write_market_readiness_writeback(root or BRIDGE_ROOT)


def write_market_readiness_writeback_artifacts(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_market_readiness_writeback(root)
    write_json(root, "operations/external_validation/e60_ceo_brain_market_readiness_update.json", data)
    write_md(root, "reports/integration/e60_cross_repo_evidence_packet.md", "E60 Market Readiness Writeback", [
        f"Artifact: `{data.get('artifact_id')}`",
        f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
        f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', 'n/a'))}`",
        f"External action allowed: `{data.get('external_action_allowed', False)}`",
    ])
    return data
