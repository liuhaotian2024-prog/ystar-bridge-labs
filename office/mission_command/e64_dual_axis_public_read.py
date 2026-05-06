from __future__ import annotations

from pathlib import Path

from . import e64_dual_axis_revenue_core as core


def run_e64_dual_axis_public_read_plan(root: Path | None = None) -> dict:
    return core.build_dual_axis_public_read_plan(root or core.BRIDGE_ROOT)


def run_e64_dual_axis_public_read_receipts(root: Path | None = None) -> dict:
    return core.build_dual_axis_public_read_receipts(root or core.BRIDGE_ROOT)


def run_e64_dual_axis_public_read_evidence_atoms(root: Path | None = None) -> dict:
    return core.build_dual_axis_public_read_evidence_atoms(root or core.BRIDGE_ROOT)


def write_e64_dual_axis_public_read(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    plan = run_e64_dual_axis_public_read_plan(root)
    core.write_json(root, "operations/external_validation/e64_dual_axis_public_read_plan.json", plan)
    receipts = run_e64_dual_axis_public_read_receipts(root)
    core.write_json(root, "operations/external_validation/e64_dual_axis_public_read_receipts.json", receipts)
    atoms = run_e64_dual_axis_public_read_evidence_atoms(root)
    core.write_json(root, "operations/external_validation/e64_dual_axis_public_read_evidence_atoms.json", atoms)
    return {"plan": plan, "receipts": receipts, "atoms": atoms}
