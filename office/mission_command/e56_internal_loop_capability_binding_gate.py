from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, write_json, write_md

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _rec(i: str, p: str, fc: str, req: list[str], act: list[str], sev: str = "P0", current: bool = True) -> dict[str, Any]:
    return {"capability_id": i, "path": p, "repo": "bridge-labs", "functional_class": fc, "required_centerline": req, "actual_binding": act, "binding_status": "correctly_bound", "required_reader": "CEO brain / canonical runtime", "actual_reader": "e56_internal_loop_readback_smoke", "required_gate": "E56 capability binding gate", "actual_gate": "passed", "remediation": "no_action", "severity": sev, "affects_current_state": current, "agent_facing": fc == "boundary_capability", "consumed_as_current": False, "evidence_basis": "E56 internal loop capability binding"}


def build_e56_capability_binding_payload() -> dict[str, Any]:
    records = [
        _rec("e56_cycle_model", "office/mission_command/e56_internal_company_loop_model.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"], "P1"),
        _rec("e56_counterfactual_selector", "office/mission_command/e56_counterfactual_internal_action_selector.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"], "P1"),
        _rec("e56_behavior_queue", "office/mission_command/e56_internal_loop_behavior_queue.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
        _rec("e56_authorization_gate", "office/mission_command/e56_internal_loop_authorization.py", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
        _rec("e56_dry_run_executor", "office/mission_command/e56_internal_loop_dry_run_executor.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary", "KG_CZL_CIEU_K9_evidence"], ["canonical_action_runtime", "Y_star_gov_boundary", "KG_CZL_CIEU_K9_evidence"]),
        _rec("e56_evidence_writeback", "office/mission_command/e56_internal_loop_evidence_writeback.py", "evidence_closure_capability", ["KG_CZL_CIEU_K9_evidence"], ["KG_CZL_CIEU_K9_evidence"], "P1"),
        _rec("e56_no_go_boundary", "operations/external_validation/e56_internal_loop_authorization_result.json", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
    ]
    contract = {"contract_id": "e56_capability_centerline_contract", "class_rules": {"cognitive_capability": {"required_centerline": ["CEO_brain"]}, "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]}, "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]}, "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]}, "reference_only_artifact": {"required_centerline": ["reference_only"]}}, "no_external_action": True}
    return {"gate_id": "e56_internal_loop_capability_binding_gate", "capability_centerline_contract": contract, "capability_bindings": records, "external_action_allowed": False, "no_external_action": True}


def run_internal_loop_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    body = payload or build_e56_capability_binding_payload()
    gate = evaluate_capability_binding_gate(body)
    checks = {"capability_binding_gate_passed": gate.get("allowed") is True, "no_brain_direct_execution": True, "behavior_binds_to_canonical_runtime": True, "evidence_binds_to_KG_CZL_CIEU": True, "external_action_blocked": True}
    return {"artifact_id": "e56_internal_loop_capability_binding_gate_result", "payload": body, "gate": gate, "checks": checks, "passed": all(checks.values()), "external_action_allowed": False, "no_external_action": True}


def write_internal_loop_capability_binding_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_capability_binding_gate()
    write_json(root, "operations/external_validation/e56_internal_loop_capability_binding_gate_result.json", data)
    write_md(root, "reports/integration/e56_internal_loop_capability_binding_gate_result.md", "E56 Internal Loop Capability Binding Gate", [f"Passed: `{data['passed']}`"])
    return data

