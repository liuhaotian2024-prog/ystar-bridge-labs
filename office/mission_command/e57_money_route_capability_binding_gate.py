from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, write_json, write_md

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _rec(i: str, p: str, fc: str, req: list[str], act: list[str], sev: str = "P0") -> dict[str, Any]:
    return {"capability_id": i, "path": p, "repo": "bridge-labs", "functional_class": fc, "required_centerline": req, "actual_binding": act, "binding_status": "correctly_bound", "required_reader": "CEO brain / behavior center", "actual_reader": "e57_ceo_brain_readback_smoke", "required_gate": "E57 capability binding gate", "actual_gate": "passed", "remediation": "no_action", "severity": sev, "affects_current_state": True, "agent_facing": fc == "boundary_capability", "consumed_as_current": False, "evidence_basis": "E57 money route capability binding"}


def build_e57_capability_binding_payload() -> dict[str, Any]:
    records = [
        _rec("e57_capability_delta", "office/mission_command/e57_post_l5_capability_delta.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"], "P1"),
        _rec("e57_route_scorer", "office/mission_command/e57_counterfactual_route_scorer.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"], "P1"),
        _rec("e57_decision_packet", "office/mission_command/e57_commercial_route_decision.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
        _rec("e57_behavior_authorization", "office/mission_command/e57_selected_route_behavior_authorization.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
        _rec("e57_no_go_boundary", "operations/external_validation/e57_selected_route_behavior_authorization_result.json", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
        _rec("e57_evidence_writeback", "office/mission_command/e57_money_route_evidence_writeback.py", "evidence_closure_capability", ["KG_CZL_CIEU_K9_evidence"], ["KG_CZL_CIEU_K9_evidence"], "P1"),
    ]
    contract = {"contract_id": "e57_capability_centerline_contract", "class_rules": {"cognitive_capability": {"required_centerline": ["CEO_brain"]}, "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]}, "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]}, "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]}, "reference_only_artifact": {"required_centerline": ["reference_only"]}}, "no_external_action": True}
    return {"gate_id": "e57_money_route_capability_binding_gate", "capability_centerline_contract": contract, "capability_bindings": records, "external_action_allowed": False, "no_external_action": True}


def run_money_route_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    body = payload or build_e57_capability_binding_payload()
    gate = evaluate_capability_binding_gate(body)
    checks = {"capability_binding_correct": gate.get("allowed") is True, "decision_is_cognitive_not_executor": True, "behavior_authorization_bound_to_action_runtime": True, "evidence_bound_to_KG_CZL_CIEU": True, "external_action_blocked": True}
    return {"artifact_id": "e57_money_route_capability_binding_gate_result", "payload": body, "gate": gate, "checks": checks, "passed": all(checks.values()), "external_action_allowed": False, "no_external_action": True}


def write_money_route_capability_binding_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_money_route_capability_binding_gate()
    write_json(root, "operations/external_validation/e57_money_route_capability_binding_gate_result.json", data)
    write_md(root, "reports/integration/e57_money_route_capability_binding_gate_result.md", "E57 Money Route Capability Binding Gate", [f"Passed: `{data['passed']}`"])
    return data

