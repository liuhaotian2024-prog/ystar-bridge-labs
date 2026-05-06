from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_revenue_opportunity_evidence_atoms(root: Path | None = None) -> dict:
    return core.build_revenue_opportunity_evidence_atoms(root or core.BRIDGE_ROOT)


def write_revenue_opportunity_evidence_atoms(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_revenue_opportunity_evidence_atoms(root)
    core.write_json(root, "operations/external_validation/e63_revenue_opportunity_evidence_atoms.json", data)
    return data
