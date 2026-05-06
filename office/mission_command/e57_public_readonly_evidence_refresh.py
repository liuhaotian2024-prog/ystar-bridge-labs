from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, write_json, write_md
from .e57_public_readonly_evidence_preflight import run_public_readonly_evidence_preflight


def run_public_readonly_evidence_refresh() -> dict[str, Any]:
    preflight = run_public_readonly_evidence_preflight()
    return {
        "artifact_id": "e57_public_readonly_evidence_refresh",
        "refresh_status": "skipped",
        "skip_reason": preflight["blocker"],
        "pages_read": 0,
        "hard_cap_pages": 24,
        "source_receipts_path": "operations/external_validation/e57_public_source_receipts.jsonl",
        "evidence_atoms_path": "operations/external_validation/e57_commercial_evidence_atoms.jsonl",
        "claims": [],
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_public_readonly_evidence_refresh(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_public_readonly_evidence_refresh()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e57_public_source_receipts.jsonl").write_text("", encoding="utf-8")
    (root / "operations/external_validation/e57_commercial_evidence_atoms.jsonl").write_text("", encoding="utf-8")
    write_json(root, "operations/external_validation/e57_public_readonly_evidence_refresh.json", data)
    write_md(root, "reports/integration/e57_public_readonly_evidence_refresh.md", "E57 Public Read-Only Evidence Refresh", [
        "Refresh status: `skipped`",
        f"Blocker: `{data['skip_reason']}`",
        "No public pages were read in E57.",
    ])
    return data

