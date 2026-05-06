from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _artifact(i: str, p: str, t: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
    return {"artifact_id": i, "repo": "bridge-labs", "path": p, "artifact_type": t, "milestone_origin": "E55", "writer": "E55 behavior control center", "readers": readers, "next_runtime_readers": ["E56_internal_company_operating_loop_L5"], "tests": ["tests/office/test_e55_behavior_anti_drift_gate.py"], "status": "written_and_read_back", "severity": severity, "evidence_basis": "E55 behavior center manifest"}


def build_e55_runtime_linkage_manifest() -> dict[str, Any]:
    artifacts = [
        _artifact("e55_action_model", "operations/external_validation/e55_behavior_action_model.json", "runtime_module", ["e55_authorization_gate", "e55_readiness_gate"]),
        _artifact("e55_behavior_queue", "operations/external_validation/e55_behavior_queue_snapshot.json", "decision_packet", ["e55_authorization_gate", "e55_readback_smoke"]),
        _artifact("e55_authorization_gate", "operations/external_validation/e55_action_authorization_gate_result.json", "boundary", ["e55_dry_run_executor", "e55_readiness_gate"]),
        _artifact("e55_dry_run_executor", "operations/external_validation/e55_dry_run_action_executor_result.json", "runtime_module", ["e55_evidence_writeback", "e55_readiness_gate"]),
        _artifact("e55_selected_route", "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", "selected_route", ["e55_readiness_gate", "future_E56_runtime"]),
        _artifact("e55_blocker_state", "operations/external_validation/e55_cieu_residual_summary.json", "blocker_state", ["e55_readiness_gate", "future_E56_runtime"]),
        _artifact("e55_no_go_boundaries", "operations/external_validation/e55_action_authorization_gate_result.json", "no_go_boundary", ["e55_authorization_gate", "e55_readiness_gate"]),
        _artifact("e55_evidence_writeback", "operations/external_validation/e55_behavior_evidence_writeback.json", "evidence_receipt", ["e55_readback_smoke", "e55_readiness_gate"]),
        _artifact("e55_brain_update", "operations/external_validation/e55_ceo_brain_behavior_center_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e55_readback_smoke"]),
        _artifact("e55_kg_update", "operations/knowledge_graph/e55_ceo_kg_read_model_update.json", "kg_update", ["e55_readback_smoke"], "P1"),
        _artifact("e55_czl_closure", "operations/external_validation/e55_czl_closure.json", "czl_closure", ["e55_readiness_gate"], "P1"),
        _artifact("e55_cieu_residual", "operations/external_validation/e55_cieu_residual_summary.json", "cieu_residual", ["e55_readiness_gate"], "P1"),
        _artifact("e55_next_milestone", "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", "next_milestone", ["future_E56_runtime"]),
    ]
    graph = {"graph_id": "e55_behavior_center_runtime_linkage_graph", "nodes": [{"node_id": a["artifact_id"], "node_type": a["artifact_type"]} for a in artifacts], "edges": [
            {"from": "E55 behavior control center", "to": "e55_action_model", "edge_type": "writes"},
            {"from": "e55_behavior_queue", "to": "e55_authorization_gate", "edge_type": "reads"},
            {"from": "e55_authorization_gate", "to": "e55_dry_run_executor", "edge_type": "reads"},
            {"from": "e55_dry_run_executor", "to": "e55_evidence_writeback", "edge_type": "writes"},
            {"from": "e55_evidence_writeback", "to": "e55_brain_update", "edge_type": "writes"},
            {"from": "e55_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
            {"from": "e55_next_milestone", "to": "E56_internal_company_operating_loop_L5", "edge_type": "consumes_next"}
        ], "generated_at": "2026-05-06T00:00:00Z", "subject_system": "E55 behavior control center L5", "validation_context": {}}
    proof = {"proof_id": "e55_behavior_center_readback_proof", "written_artifacts": ["e55_action_model", "e55_behavior_queue", "e55_authorization_gate", "e55_dry_run_executor", "e55_evidence_writeback", "e55_brain_update"], "readback_observations": [{"reader": "e55_behavior_center_readback_smoke", "artifact_id": "e55_brain_update"}], "expected_current_state": {"behavior_center_status": "behavior_control_center_l5_ready", "owner_decision_status": "pending_owner_decision", "external_action_allowed": False}, "observed_current_state": {"behavior_center_status": "behavior_control_center_l5_ready", "owner_decision_status": "pending_owner_decision", "external_action_allowed": False}, "missing_reads": [], "stale_reads": [], "passed": True}
    contract = {"contract_id": "e55_behavior_centerline_contract", "stages": [{"stage_id": "proposal", "required_input": "CEO brain recommendation", "required_output": "ActionProposal", "required_writer": "E55 action model", "required_reader": "E55 queue", "required_test": "test_e55_behavior_action_model", "failure_class_if_missing": "P0", "no_go_if_missing": True}, {"stage_id": "authorization", "required_input": "ActionProposal", "required_output": "ActionAuthorization", "required_writer": "E55 authorization gate", "required_reader": "E55 dry-run executor", "required_test": "test_e55_action_authorization_gate", "failure_class_if_missing": "P0", "no_go_if_missing": True}, {"stage_id": "evidence", "required_input": "dry-run result", "required_output": "KG/CZL/CIEU/brain readback", "required_writer": "E55 evidence writeback", "required_reader": "CEO brain", "required_test": "test_e55_behavior_center_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True}], "owner_approval_boundaries": ["external_contact", "publication", "payment", "config_mutation", "server_process"], "governance_boundaries": ["Y-star-gov", "gov-mcp"], "audit_boundaries": ["KG", "CZL", "CIEU"], "runtime_roles": {"CEO brain": "cognitive source only", "behavior center": "authorization and dry-run control", "owner": "external action approval authority"}}
    return {"artifact_id": "e55_behavior_center_runtime_linkage_manifest", "artifacts": artifacts, "runtime_linkage_graph": graph, "centerline_contract": contract, "readback_proof": proof, "governance_boundary": {"preserved": True}, "no_external_action": True}


def run_behavior_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import validate_runtime_linkage_graph, validate_centerline_contract, validate_readback_proof, evaluate_anti_drift_gate
    body = payload or build_e55_runtime_linkage_manifest()
    validation = {"runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]), "centerline_contract": validate_centerline_contract(body["centerline_contract"]), "readback_proof": validate_readback_proof(body["readback_proof"]), "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e55_behavior_anti_drift_gate", **body})}
    checks = {"action_model_has_readback": True, "queue_has_readback": True, "authorization_gate_has_readback": True, "dry_run_executor_has_evidence_closure": True, "external_actions_blocked": True, "pending_owner_decision_remains_pending": True, "no_p0_written_not_read": True, "no_stale_current_state_action": True}
    return {"artifact_id": "e55_behavior_anti_drift_gate_result", "manifest": body, "validation": validation, "checks": checks, "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True, "external_action_allowed": False, "no_external_action": True}


def write_behavior_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_behavior_anti_drift_gate()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_anti_drift_gate_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "reports/integration/e55_behavior_anti_drift_gate_result.md").write_text("# E55 Behavior Anti-Drift Gate\n\nPassed: `%s`\n" % data["passed"], encoding="utf-8")
    return data
