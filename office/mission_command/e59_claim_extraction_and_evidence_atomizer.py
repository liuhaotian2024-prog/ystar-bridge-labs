from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_evidence_pipeline, write_json, write_jsonl, write_md


def build_evidence_atoms() -> list[dict]:
    return build_evidence_pipeline()["evidence_atoms"]


def write_evidence_atom_artifacts(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    pipeline = build_evidence_pipeline()
    write_json(root, "operations/external_validation/e59_evidence_atom_schema.json", {
        "artifact_id": "e59_evidence_atom_schema",
        "evidence_atom_count": pipeline["evidence_atom_count"],
        "schema": pipeline["evidence_atom_schema"],
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_expert_feedback_claimed": True,
    })
    write_jsonl(root, "operations/external_validation/e59_evidence_atoms.jsonl", pipeline["evidence_atoms"])
    write_md(root, "reports/integration/e59_evidence_pipeline.md", "E59 Evidence Pipeline", [
        f"Source receipts: `{pipeline['receipt_count']}`",
        f"Evidence atoms: `{pipeline['evidence_atom_count']}`",
        "Atoms are learning evidence, not customer validation, paid signal, or expert feedback.",
    ])
    return pipeline

