from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_architecture, write_json, write_md


def run_external_intelligence_architecture() -> dict:
    return build_architecture()


def write_external_intelligence_architecture(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_intelligence_architecture()
    write_json(root, "operations/external_validation/e59_external_intelligence_architecture.json", data)
    write_md(root, "reports/integration/e59_external_intelligence_architecture.md", "E59 External Intelligence Architecture", [
        "External knowledge observation is allowed when public-read-only and safe.",
        "External human interaction remains forbidden.",
        "Boundaries are safety, relevance, evidence quality, and governance; not fixed categories.",
    ])
    return data

