from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, build_readiness_delta, write_json, write_md


def run_external_intelligence_readiness_delta(root: Path | None = None) -> dict:
    return build_readiness_delta(root or BRIDGE_ROOT)


def write_external_intelligence_readiness_delta(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_intelligence_readiness_delta(root)
    write_json(root, "operations/external_validation/e61_external_intelligence_readiness_delta.json", data)
    write_md(root, "reports/integration/e61_external_intelligence_readiness_delta.md", "E61 External Intelligence Readiness Delta", [
        f"Final status: `{data['final_status']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
    ])
    return data
