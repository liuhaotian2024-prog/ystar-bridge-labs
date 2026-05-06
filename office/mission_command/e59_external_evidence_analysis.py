from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_external_evidence_analysis, write_json, write_md


def run_external_evidence_analysis() -> dict:
    return build_external_evidence_analysis()


def write_external_evidence_analysis(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_evidence_analysis()
    write_json(root, "operations/external_validation/e59_external_evidence_analysis.json", data)
    write_md(root, "reports/integration/e59_external_evidence_analysis.md", "E59 External Evidence Analysis", [
        "Credibility, freshness, and contradiction/gap labels are present.",
        "Public-read-only evidence remains hypothesis support, not validation.",
    ])
    return data

