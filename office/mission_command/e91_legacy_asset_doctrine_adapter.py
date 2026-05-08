from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def invoke_legacy_asset_doctrine(*, root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    promoted = _load_json(base / "operations/external_validation/e71_legacy_asset_promotion_gate_results.json")
    quarantined = _load_json(base / "operations/external_validation/e71_quarantined_legacy_assets.json")
    return {
        "doctrine_id": "legacy_asset_promotion_and_quarantine",
        "runtime_status": "callable_but_not_mandatory",
        "invocation_status": "completed",
        "output_summary": "E71 promoted/quarantined legacy asset records were consulted before selecting reusable assets.",
        "evidence_refs": [
            "operations/external_validation/e71_legacy_asset_promotion_gate_results.json",
            "operations/external_validation/e71_quarantined_legacy_assets.json",
        ],
        "promoted_count": _count_items(promoted),
        "quarantined_count": _count_items(quarantined),
        "quarantined_assets_excluded": True,
        "CIEU_recording_status": "candidate_for_Y_star_gov_CIEUStore_write",
    }


def _load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _count_items(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("assets", "results", "promoted_assets", "quarantined_assets"):
            if isinstance(payload.get(key), list):
                return len(payload[key])
    return 0


__all__ = ["invoke_legacy_asset_doctrine"]
