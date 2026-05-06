from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e55_behavior_anti_drift_gate import run_behavior_anti_drift_gate
from .e55_behavior_capability_binding_gate import run_behavior_capability_binding_gate

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def run_e55_y_star_gov_validation() -> dict[str, Any]:
    anti = run_behavior_anti_drift_gate()
    binding = run_behavior_capability_binding_gate()
    return {"artifact_id": "e55_y_star_gov_validation_result", "used_read_only_y_star_gov": True, "runtime_linkage": anti.get("validation", {}).get("runtime_linkage_graph", {}), "readback_proof": anti.get("validation", {}).get("readback_proof", {}), "anti_drift_gate": anti, "capability_binding_gate": binding, "passed": anti.get("passed") is True and binding.get("passed") is True, "external_action_allowed": False, "no_external_action": True}


def write_e55_y_star_gov_validation(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e55_y_star_gov_validation()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_y_star_gov_validation_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "reports/integration/e55_y_star_gov_validation_result.md").write_text("# E55 Y-star-gov Validation\n\nPassed: `%s`\n" % data["passed"], encoding="utf-8")
    return data
