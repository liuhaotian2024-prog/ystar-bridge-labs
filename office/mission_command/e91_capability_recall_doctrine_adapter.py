from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def invoke_capability_recall_doctrine(*, root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    code_index = _load_json(base / "operations/baseline/e87r_full_repo_baseline/code_index.json")
    architecture = _load_json(base / "operations/baseline/e87r_full_repo_baseline/architecture_evidence_map.json")
    return {
        "doctrine_id": "full_repo_capability_recall_and_inventory",
        "runtime_status": "runtime_active",
        "invocation_status": "completed",
        "output_summary": "E87R code index and architecture map were consulted for full-repo capability recall.",
        "evidence_refs": [
            "operations/baseline/e87r_full_repo_baseline/code_index.json",
            "operations/baseline/e87r_full_repo_baseline/architecture_evidence_map.json",
        ],
        "capability_counts": code_index.get("counts", {}),
        "domain_count": len(architecture.get("domains", [])) if isinstance(architecture.get("domains"), list) else len(architecture.get("domains", {})),
        "recent_memory_only": False,
        "CIEU_recording_status": "candidate_for_Y_star_gov_CIEUStore_write",
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = ["invoke_capability_recall_doctrine"]
