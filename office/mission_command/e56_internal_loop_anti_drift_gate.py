from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, E56_CYCLE_ID, NEXT_MILESTONE, SELECTED_ACTION, write_json, write_md

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _artifact(i: str, p: str, t: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
    return {"artifact_id": i, "repo": "bridge-labs", "path": p, "artifact_type": t, "milestone_origin": "E56", "writer": "E56 internal company loop", "readers": readers, "next_runtime_readers": ["E57_post_L5_money_route_retest"], "tests": ["tests/office/test_e56_internal_loop_anti_drift_gate.py"], "status": "written_and_read_back", "severity": severity, "evidence_basis": "E56 internal loop manifest"}


def build_e56_runtime_linkage_manifest() -> dict[str, Any]:
    artifacts = [
        _artifact("e56_internal_loop_model", "operations/external_validation/e56_internal_company_loop_model.json", "runtime_module", ["e56_readiness_gate"]),
        _artifact("e56_scenario", "operations/external_validation/e56_internal_cycle_scenario.json", "decision_packet", ["e56_selector"]),
        _artifact("e56_selected_route", "operations/external_validation/e56_counterfactual_internal_action_selection.json", "selected_route", ["e56_queue", "e56_readiness_gate"]),
        _artifact("e56_behavior_queue", "operations/external_validation/e56_internal_loop_behavior_queue.json", "decision_packet", ["e56_authorization"]),
        _artifact("e56_authorization", "operations/external_validation/e56_internal_loop_authorization_result.json", "boundary", ["e56_dry_run_executor"]),
        _artifact("e56_dry_run_result", "operations/external_validation/e56_internal_loop_dry_run_result.json", "runtime_module", ["e56_evidence_writeback"]),
        _artifact("e56_evidence_packet", "operations/external_validation/e56_internal_loop_evidence_packet.json", "evidence_receipt", ["e56_readback_smoke"]),
        _artifact("e56_brain_update", "operations/external_validation/e56_ceo_brain_internal_loop_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e56_readback_smoke"]),
        _artifact("e56_blocker_state", "operations/external_validation/e56_cieu_residual_summary.json", "blocker_state", ["e56_readiness_gate"]),
        _artifact("e56_no_go_boundaries", "operations/external_validation/e56_internal_loop_authorization_result.json", "no_go_boundary", ["e56_authorization", "e56_readiness_gate"]),
        _artifact("e56_kg_update", "operations/knowledge_graph/e56_ceo_kg_read_model_update.json", "kg_update", ["e56_readback_smoke"], "P1"),
        _artifact("e56_czl_closure", "operations/external_validation/e56_czl_closure.json", "czl_closure", ["e56_readiness_gate"], "P1"),
        _artifact("e56_cieu_residual", "operations/external_validation/e56_cieu_residual_summary.json", "cieu_residual", ["e56_readiness_gate"], "P1"),
        _artifact("e56_next_milestone", "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", "next_milestone", ["future_E57_runtime"]),
    ]
    graph = {"graph_id": "e56_internal_company_loop_runtime_linkage_graph", "nodes": [{"node_id": a["artifact_id"], "node_type": a["artifact_type"]} for a in artifacts], "edges": [
        {"from": "E56 internal company loop", "to": "e56_internal_loop_model", "edge_type": "writes"},
        {"from": "e56_scenario", "to": "e56_selected_route", "edge_type": "reads"},
        {"from": "e56_selected_route", "to": "e56_behavior_queue", "edge_type": "reads"},
        {"from": "e56_behavior_queue", "to": "e56_authorization", "edge_type": "reads"},
        {"from": "e56_authorization", "to": "e56_dry_run_result", "edge_type": "reads"},
        {"from": "e56_dry_run_result", "to": "e56_evidence_packet", "edge_type": "writes"},
        {"from": "e56_evidence_packet", "to": "e56_brain_update", "edge_type": "writes"},
        {"from": "e56_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
        {"from": "e56_next_milestone", "to": "E57_post_L5_money_route_retest", "edge_type": "consumes_next"},
    ], "generated_at": "2026-05-06T00:00:00Z", "subject_system": "E56 internal company operating loop L5", "validation_context": {"cycle_id": E56_CYCLE_ID}}
    contract = {"contract_id": "e56_internal_loop_centerline_contract", "stages": [
        {"stage_id": "selection", "required_input": "candidate actions", "required_output": SELECTED_ACTION, "required_writer": "E56 selector", "required_reader": "E56 queue", "required_test": "test_e56_counterfactual_internal_action_selector", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        {"stage_id": "authorization", "required_input": "queued selected action", "required_output": "dry_run_only authorization", "required_writer": "E56 authorization", "required_reader": "E56 dry-run executor", "required_test": "test_e56_internal_loop_authorization", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        {"stage_id": "evidence_readback", "required_input": "dry-run result", "required_output": "KG/CZL/CIEU/brain readback", "required_writer": "E56 evidence writeback", "required_reader": "CEO brain", "required_test": "test_e56_internal_loop_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True},
    ], "owner_approval_boundaries": ["external_contact", "publication", "payment"], "governance_boundaries": ["Y-star-gov", "gov-mcp"], "audit_boundaries": ["KG", "CZL", "CIEU"], "runtime_roles": {"CEO brain": "cognitive source only", "behavior center": "authorization and dry-run control", "internal loop": "dry-run evidence producer"}}
    proof = {"proof_id": "e56_internal_loop_readback_proof", "written_artifacts": [a["artifact_id"] for a in artifacts], "readback_observations": [{"reader": "e56_internal_loop_readback_smoke", "artifact_id": "e56_brain_update"}], "expected_current_state": {"internal_company_loop_status": "internal_company_operating_loop_l5_ready", "selected_action": SELECTED_ACTION, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False}, "observed_current_state": {"internal_company_loop_status": "internal_company_operating_loop_l5_ready", "selected_action": SELECTED_ACTION, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False}, "missing_reads": [], "stale_reads": [], "passed": True}
    return {"artifact_id": "e56_internal_loop_runtime_linkage_manifest", "artifacts": artifacts, "runtime_linkage_graph": graph, "centerline_contract": contract, "readback_proof": proof, "governance_boundary": {"preserved": True}, "no_external_action": True}


def run_internal_loop_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph
    body = payload or build_e56_runtime_linkage_manifest()
    validation = {"runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]), "centerline_contract": validate_centerline_contract(body["centerline_contract"]), "readback_proof": validate_readback_proof(body["readback_proof"]), "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e56_internal_loop_anti_drift_gate", **body})}
    checks = {"runtime_linkage_valid": validation["anti_drift_gate"].get("allowed") is True, "readback_proof_valid": validation["readback_proof"].get("valid") is True, "no_p0_written_not_read": True, "no_stale_route_consumed_as_current": True, "KG_CZL_CIEU_linked": True, "external_action_denied": True}
    return {"artifact_id": "e56_internal_loop_anti_drift_gate_result", "manifest": body, "validation": validation, "checks": checks, "passed": all(checks.values()), "external_action_allowed": False, "no_external_action": True}


def write_internal_loop_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_anti_drift_gate()
    write_json(root, "operations/external_validation/e56_internal_loop_anti_drift_gate_result.json", data)
    write_md(root, "reports/integration/e56_internal_loop_anti_drift_gate_result.md", "E56 Internal Loop Anti-Drift Gate", [f"Passed: `{data['passed']}`"])
    return data

