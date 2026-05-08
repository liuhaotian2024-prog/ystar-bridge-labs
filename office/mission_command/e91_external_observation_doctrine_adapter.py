from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


HISTORICAL_PUBLIC_READ_ARTIFACTS = (
    "operations/external_validation/e67_external_validation_evidence_atoms.json",
    "operations/external_validation/e78_owner_approved_l3_read_only_external_research_pilot_R1_post_E73_20260507T000001Z.report.json",
    "operations/external_validation/e90_market_grounded_strategy_run_report.json",
)


def invoke_external_observation_doctrine(*, root: Path | None = None, live_required: bool = False) -> dict[str, Any]:
    """Bind existing public-read assets without pretending they are live observation."""

    base = root or BRIDGE_ROOT
    evidence = []
    for rel in HISTORICAL_PUBLIC_READ_ARTIFACTS:
        path = base / rel
        if path.exists():
            evidence.append({"path": rel, "summary": _summary(path)})
    return {
        "doctrine_id": "external_observation_public_read_evidence",
        "runtime_status": "callable_but_not_live",
        "invocation_status": "historical_public_read_wrapper_invoked",
        "live_observation_runtime_active": False,
        "live_required": live_required,
        "satisfies_live_requirement": False if live_required else True,
        "output_summary": "Historical public-read artifacts were bound; no live external observation was executed.",
        "evidence_refs": [item["path"] for item in evidence],
        "gaps": ["live_public_read_runtime_not_invoked"] if live_required else [],
        "CIEU_recording_status": "candidate_for_Y_star_gov_CIEUStore_write",
        "no_external_action": True,
        "no_customer_validation_claim": True,
    }


def _summary(path: Path) -> str:
    try:
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            return str(payload.get("artifact_id") or payload.get("job_id") or path.name)
        return path.read_text(encoding="utf-8", errors="ignore")[:240]
    except Exception:
        return path.name


__all__ = ["invoke_external_observation_doctrine"]
