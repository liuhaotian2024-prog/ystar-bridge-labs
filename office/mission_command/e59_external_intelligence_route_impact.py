from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_route_impact, write_json, write_md


def run_external_intelligence_route_impact() -> dict:
    return build_route_impact()


def write_external_intelligence_route_impact(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_intelligence_route_impact()
    write_json(root, "operations/external_validation/e59_external_intelligence_route_impact.json", data)
    write_md(root, "reports/integration/e59_external_intelligence_route_impact.md", "E59 External Intelligence Route Impact", [
        f"Routes evaluated: `{data['routes_evaluated']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
        "No route becomes customer-validated or paid-validated from public-read-only evidence.",
    ])
    return data

