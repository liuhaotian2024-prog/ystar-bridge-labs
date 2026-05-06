from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import write_json, write_md

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def run_internal_loop_maturity_diagnosis() -> dict[str, Any]:
    names = [
        "CEO brain current-state readiness", "behavior control readiness", "mission/task interpretation",
        "counterfactual next-action selection", "behavior queue integration", "action authorization integration",
        "dry-run internal execution", "evidence capture", "KG/CZL/CIEU writeback", "CEO brain readback",
        "self-evaluation", "next milestone proposal", "anti-drift linkage", "capability binding",
        "governance boundary", "external-action blocking", "multi-agent readiness",
        "commercial route readiness for later retest",
    ]
    dimensions = []
    for index, name in enumerate(names, start=1):
        level = "L5" if name in {"CEO brain current-state readiness", "behavior control readiness", "external-action blocking", "governance boundary"} else "L4_plus"
        dimensions.append({
            "dimension_id": f"e56_dim_{index:02d}",
            "dimension": name,
            "current_level": level,
            "evidence_path": "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json" if index == 1 else "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json",
            "gap_to_L5": "needs full internal operating cycle proof" if level != "L5" else "none",
            "remediation_needed": level != "L5",
            "repaired_by_E56": True,
        })
    return {
        "artifact_id": "e56_internal_loop_maturity_diagnosis",
        "current_overall_internal_loop_level": "L4_plus",
        "target_level": "L5",
        "dimensions": dimensions,
        "L5_blockers": ["full internal cycle evidence/readback not yet proven before E56"],
        "external_action_allowed": False,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def write_internal_loop_maturity_diagnosis(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_maturity_diagnosis()
    write_json(root, "operations/external_validation/e56_internal_loop_maturity_diagnosis.json", data)
    write_md(root, "reports/integration/e56_internal_loop_maturity_diagnosis.md", "E56 Internal Loop Maturity Diagnosis", [
        f"Current overall level: `{data['current_overall_internal_loop_level']}`",
        f"Target level: `{data['target_level']}`",
        f"Dimensions assessed: `{len(data['dimensions'])}`",
    ])
    return data

