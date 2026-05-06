from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_evidence_pipeline, write_json, write_jsonl


def build_source_receipts() -> list[dict]:
    return build_evidence_pipeline()["source_receipts"]


def write_source_receipt_artifacts(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    pipeline = build_evidence_pipeline()
    write_json(root, "operations/external_validation/e59_source_receipt_schema.json", {
        "artifact_id": "e59_source_receipt_schema",
        "receipt_count": pipeline["receipt_count"],
        "schema": pipeline["source_receipt_schema"],
        "no_external_action": True,
    })
    write_jsonl(root, "operations/external_validation/e59_source_receipts.jsonl", pipeline["source_receipts"])
    return {"artifact_id": "e59_source_receipt_builder_result", "receipt_count": pipeline["receipt_count"], "no_external_action": True}

