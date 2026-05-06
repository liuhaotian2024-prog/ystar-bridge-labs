from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_frontier_capture, write_json, write_md


def run_frontier_technology_capture() -> dict:
    return build_frontier_capture()


def write_frontier_technology_capture(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_frontier_technology_capture()
    write_json(root, "operations/external_validation/e59_frontier_technology_capture.json", data)
    write_md(root, "reports/integration/e59_frontier_technology_capture.md", "E59 Frontier Technology Capture", [
        f"Captured ideas: `{data['idea_count']}`",
        "No author contact, no expert feedback claim, no customer validation claim.",
    ])
    return data

