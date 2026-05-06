from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, write_json, write_md
from .e57_money_route_anti_drift_gate import run_money_route_anti_drift_gate
from .e57_money_route_capability_binding_gate import run_money_route_capability_binding_gate


def run_e57_y_star_gov_validation() -> dict[str, Any]:
    anti = run_money_route_anti_drift_gate()
    binding = run_money_route_capability_binding_gate()
    return {
        "artifact_id": "e57_y_star_gov_validation_result",
        "runtime_linkage_valid": anti["validation"]["runtime_linkage_graph"].get("valid") is True,
        "readback_proof_valid": anti["validation"]["readback_proof"].get("valid") is True,
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "passed": anti.get("passed") is True and binding.get("passed") is True,
        "read_only_validator": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_e57_y_star_gov_validation(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e57_y_star_gov_validation()
    write_json(root, "operations/external_validation/e57_y_star_gov_validation_result.json", data)
    write_md(root, "reports/integration/e57_y_star_gov_validation_result.md", "E57 Y-star-gov Validation Result", [f"Passed: `{data['passed']}`"])
    return data

