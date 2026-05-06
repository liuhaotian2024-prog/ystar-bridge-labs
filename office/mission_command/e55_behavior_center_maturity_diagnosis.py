from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))

DIMENSIONS = [
    "canonical runtime action flow", "action proposal representation", "action authorization model", "owner approval boundary", "gov-mcp/Y-star-gov validation path", "dry-run execution support", "external action blocking", "dispatch / task routing", "behavior queue / scheduling", "evidence capture", "CIEU/CZL/KG writeback", "CEO brain readback after action", "anti-drift linkage", "capability centerline binding", "process/port cleanup", "no-overclaim boundary", "multi-agent dispatch readiness",
]

def run_behavior_center_maturity_diagnosis() -> dict[str, Any]:
    dimensions = []
    for name in DIMENSIONS:
        future = "multi-agent" in name or "dispatch" in name
        dimensions.append({
            "dimension": name,
            "current_level": "L3" if name in {"action proposal representation", "action authorization model", "behavior queue / scheduling", "dry-run execution support"} else "L4",
            "evidence_path": "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json",
            "code_symbol": "canonical runtime / E55 behavior center",
            "gap_to_L5": "needs explicit E55 behavior model/gate/evidence/readback" if not future else "future internal-company-loop dispatch depth remains after E55",
            "remediation_needed": True,
            "whether_E55_will_repair": not future,
            "whether_future_internal_company_loop_milestone_must_repair": future,
        })
    return {
        "artifact_id": "e55_behavior_center_maturity_diagnosis",
        "current_overall_behavior_level": "L3_plus",
        "target_level": "L5 behavior control center",
        "dimensions": dimensions,
        "L5_blockers": ["missing action queue", "missing deterministic authorization gate", "missing dry-run execution envelope", "missing behavior evidence/readback loop"],
        "expected_after_E55": "behavior_control_center_l5_ready",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_behavior_center_maturity_diagnosis(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_behavior_center_maturity_diagnosis()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_center_maturity_diagnosis.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = "# E55 Behavior Center Maturity Diagnosis\n\nCurrent level: `%s`\n\nTarget: `%s`\n" % (data["current_overall_behavior_level"], data["target_level"])
    (root / "reports/integration/e55_behavior_center_maturity_diagnosis.md").write_text(md, encoding="utf-8")
    return data
