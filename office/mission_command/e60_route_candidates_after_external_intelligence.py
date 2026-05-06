from __future__ import annotations

from pathlib import Path

from . import e60_market_readiness_core as core

BRIDGE_ROOT = core.BRIDGE_ROOT
write_json = core.write_json
write_md = core.write_md


def run_route_candidates_after_external_intelligence(root: Path | None = None) -> dict:
    return core.build_route_candidates_after_external_intelligence(root or BRIDGE_ROOT)


def write_route_candidates_after_external_intelligence(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_route_candidates_after_external_intelligence(root)
    write_json(root, "operations/external_validation/e60_route_candidates_after_external_intelligence.json", data)
    write_md(root, "reports/integration/e60_route_candidates_after_external_intelligence.md", "E60 Route Candidates After External Intelligence", [
        f"Artifact: `{data.get('artifact_id')}`",
        f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
        f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', 'n/a'))}`",
        f"External action allowed: `{data.get('external_action_allowed', False)}`",
    ])
    return data
