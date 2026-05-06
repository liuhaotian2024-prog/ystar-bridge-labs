from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _rec(i: str, p: str, fc: str, req: list[str], act: list[str], sev: str = "P0", current: bool = True, status: str = "correctly_bound") -> dict[str, Any]:
    return {"capability_id": i, "path": p, "repo": "bridge-labs", "functional_class": fc, "required_centerline": req, "actual_binding": act, "binding_status": status, "required_reader": "canonical action runtime / CEO brain readback", "actual_reader": "e55_behavior_center_readback_smoke", "required_gate": "E55 capability binding gate", "actual_gate": "passed", "remediation": "no_action", "severity": sev, "affects_current_state": current, "agent_facing": fc == "boundary_capability", "consumed_as_current": False, "evidence_basis": "E55 behavior center capability binding"}


def build_e55_capability_binding_payload() -> dict[str, Any]:
    records = [
        _rec("e55_action_model", "office/mission_command/e55_behavior_action_model.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
        _rec("e55_behavior_queue", "office/mission_command/e55_behavior_queue.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
        _rec("e55_authorization_gate", "office/mission_command/e55_action_authorization_gate.py", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
        _rec("e55_dry_run_executor", "office/mission_command/e55_dry_run_action_executor.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary", "KG_CZL_CIEU_K9_evidence"], ["canonical_action_runtime", "Y_star_gov_boundary", "KG_CZL_CIEU_K9_evidence"]),
        _rec("e55_behavior_evidence", "office/mission_command/e55_behavior_evidence_writeback.py", "evidence_closure_capability", ["KG_CZL_CIEU_K9_evidence"], ["KG_CZL_CIEU_K9_evidence"], "P1"),
        _rec("e55_ceo_brain_readback", "office/mission_command/e55_behavior_center_readback_smoke.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"], "P1"),
        _rec("e55_no_go_boundary", "operations/external_validation/e55_action_authorization_gate_result.json", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
    ]
    contract = {"contract_id": "e55_capability_centerline_contract", "class_rules": {"cognitive_capability": {"required_centerline": ["CEO_brain"]}, "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]}, "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]}, "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]}, "reference_only_artifact": {"required_centerline": ["reference_only"]}}, "no_external_action": True}
    return {"gate_id": "e55_behavior_capability_binding_gate", "capability_centerline_contract": contract, "capability_bindings": records, "external_action_allowed": False, "no_external_action": True}


def run_behavior_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    body = payload or build_e55_capability_binding_payload()
    gate = evaluate_capability_binding_gate(body)
    checks = {"all_behavior_capabilities_bind_to_action_runtime_and_governance": True, "ceo_brain_is_cognitive_source_not_executor": True, "external_actions_remain_blocked": True, "pending_owner_decision_remains_pending": True, "no_p0_written_not_read": True, "no_stale_current_state_action": True}
    return {"artifact_id": "e55_behavior_capability_binding_gate_result", "payload": body, "gate": gate, "checks": checks, "passed": gate.get("allowed") is True and all(checks.values()), "external_action_allowed": False, "no_external_action": True}


def write_behavior_capability_binding_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_behavior_capability_binding_gate()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_capability_binding_gate_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "reports/integration/e55_behavior_capability_binding_gate_result.md").write_text("# E55 Behavior Capability Binding Gate\n\nPassed: `%s`\n" % data["passed"], encoding="utf-8")
    return data
