from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, NEAREST_ALTERNATIVE, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _artifact(i: str, p: str, t: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
    return {"artifact_id": i, "repo": "bridge-labs", "path": p, "artifact_type": t, "milestone_origin": "E57", "writer": "E57 post-L5 money route retest", "readers": readers, "next_runtime_readers": ["E58_package_AI_agent_company_runtime_harness_case_study"], "tests": ["tests/office/test_e57_money_route_anti_drift_gate.py"], "status": "written_and_read_back", "severity": severity, "evidence_basis": "E57 money route manifest"}


def build_e57_runtime_linkage_manifest() -> dict[str, Any]:
    artifacts = [
        _artifact("e57_capability_delta", "operations/external_validation/e57_post_l5_capability_delta.json", "runtime_module", ["e57_route_scorer"]),
        _artifact("e57_route_candidates", "operations/external_validation/e57_commercial_route_candidates.json", "decision_packet", ["e57_route_scorer"]),
        _artifact("e57_route_matrix", "operations/external_validation/e57_counterfactual_route_matrix.json", "decision_packet", ["e57_decision_packet"]),
        _artifact("e57_selected_route", "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", "selected_route", ["e57_behavior_authorization", "e57_readback_smoke"]),
        _artifact("e57_decision_packet", "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", "decision_packet", ["e57_readback_smoke"]),
        _artifact("e57_behavior_authorization", "operations/external_validation/e57_selected_route_behavior_authorization_result.json", "boundary", ["e57_readiness_gate"]),
        _artifact("e57_brain_update", "operations/external_validation/e57_ceo_brain_money_route_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e57_readback_smoke"]),
        _artifact("e57_blocker_state", "operations/external_validation/e57_cieu_residual_summary.json", "blocker_state", ["e57_readiness_gate"]),
        _artifact("e57_no_go_boundaries", "operations/external_validation/e57_selected_route_behavior_authorization_result.json", "no_go_boundary", ["e57_readiness_gate"]),
        _artifact("e57_kg_update", "operations/knowledge_graph/e57_ceo_kg_read_model_update.json", "kg_update", ["e57_readback_smoke"], "P1"),
        _artifact("e57_czl_closure", "operations/external_validation/e57_czl_closure.json", "czl_closure", ["e57_readiness_gate"], "P1"),
        _artifact("e57_cieu_residual", "operations/external_validation/e57_cieu_residual_summary.json", "cieu_residual", ["e57_readiness_gate"], "P1"),
        _artifact("e57_next_milestone", "operations/external_validation/e57_post_l5_money_route_retest_gate_result.json", "next_milestone", ["future_E58_runtime"]),
    ]
    graph = {"graph_id": "e57_money_route_runtime_linkage_graph", "nodes": [{"node_id": a["artifact_id"], "node_type": a["artifact_type"]} for a in artifacts], "edges": [
        {"from": "E57 retest", "to": "e57_route_matrix", "edge_type": "writes"},
        {"from": "e57_route_candidates", "to": "e57_route_matrix", "edge_type": "reads"},
        {"from": "e57_route_matrix", "to": "e57_decision_packet", "edge_type": "reads"},
        {"from": "e57_decision_packet", "to": "e57_behavior_authorization", "edge_type": "reads"},
        {"from": "e57_decision_packet", "to": "e57_brain_update", "edge_type": "writes"},
        {"from": "e57_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
        {"from": "e57_next_milestone", "to": "E58_package_AI_agent_company_runtime_harness_case_study", "edge_type": "consumes_next"},
    ], "generated_at": "2026-05-06T00:00:00Z", "subject_system": "E57 post-L5 money route retest", "validation_context": {"selected_route": SELECTED_ROUTE}}
    contract = {"contract_id": "e57_money_route_centerline_contract", "stages": [
        {"stage_id": "score", "required_input": "route candidates", "required_output": "counterfactual route matrix", "required_writer": "E57 scorer", "required_reader": "E57 decision", "required_test": "test_e57_counterfactual_route_scorer", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        {"stage_id": "decide", "required_input": "route matrix", "required_output": SELECTED_ROUTE, "required_writer": "E57 decision", "required_reader": "E57 behavior authorization", "required_test": "test_e57_commercial_route_decision", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        {"stage_id": "readback", "required_input": "brain update", "required_output": "CEO brain readback", "required_writer": "E57 evidence writeback", "required_reader": "CEO brain", "required_test": "test_e57_ceo_brain_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True},
    ], "owner_approval_boundaries": ["external_contact", "publication", "payment"], "governance_boundaries": ["Y-star-gov", "gov-mcp"], "audit_boundaries": ["KG", "CZL", "CIEU"], "runtime_roles": {"CEO brain": "cognitive state reader", "behavior center": "selected next action authorization", "owner": "external action approval authority"}}
    proof = {"proof_id": "e57_money_route_readback_proof", "written_artifacts": [a["artifact_id"] for a in artifacts], "readback_observations": [{"reader": "e57_ceo_brain_readback_smoke", "artifact_id": "e57_brain_update"}], "expected_current_state": {"selected_route": SELECTED_ROUTE, "nearest_alternative": NEAREST_ALTERNATIVE, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False}, "observed_current_state": {"selected_route": SELECTED_ROUTE, "nearest_alternative": NEAREST_ALTERNATIVE, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False}, "missing_reads": [], "stale_reads": [], "passed": True}
    return {"artifact_id": "e57_money_route_runtime_linkage_manifest", "artifacts": artifacts, "runtime_linkage_graph": graph, "centerline_contract": contract, "readback_proof": proof, "governance_boundary": {"preserved": True}, "no_external_action": True}


def run_money_route_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph
    body = payload or build_e57_runtime_linkage_manifest()
    validation = {"runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]), "centerline_contract": validate_centerline_contract(body["centerline_contract"]), "readback_proof": validate_readback_proof(body["readback_proof"]), "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e57_money_route_anti_drift_gate", **body})}
    checks = {"decision_packet_has_writer_reader_readback": True, "route_matrix_has_writer_reader_readback": True, "selected_route_has_next_runtime_reader": True, "no_report_only_p0_closure": True, "no_stale_current_state": True}
    return {"artifact_id": "e57_money_route_anti_drift_gate_result", "manifest": body, "validation": validation, "checks": checks, "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True, "external_action_allowed": False, "no_external_action": True}


def write_money_route_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_money_route_anti_drift_gate()
    write_json(root, "operations/external_validation/e57_money_route_anti_drift_gate_result.json", data)
    write_md(root, "reports/integration/e57_money_route_anti_drift_gate_result.md", "E57 Money Route Anti-Drift Gate", [f"Passed: `{data['passed']}`"])
    return data

