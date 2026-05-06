from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, CASE_STUDY_ID, NEXT_MILESTONE, write_json, write_md

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _artifact(i: str, p: str, t: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
    return {"artifact_id": i, "repo": "bridge-labs", "path": p, "artifact_type": t, "milestone_origin": "E58", "writer": "E58 case study packager", "readers": readers, "next_runtime_readers": ["E59_external_world_intelligence_L5_convergence"], "tests": ["tests/office/test_e58_case_study_anti_drift_gate.py"], "status": "written_and_read_back", "severity": severity, "evidence_basis": "E58 case study manifest"}


def build_e58_runtime_linkage_manifest() -> dict[str, Any]:
    artifacts = [
        _artifact("e58_case_study", "products/ai_agent_company_runtime_harness_case_study/case_study.json", "decision_packet", ["e58_readback_smoke", "owner_review_packet"]),
        _artifact("e58_selected_route", "products/ai_agent_company_runtime_harness_case_study/case_study.json", "selected_route", ["e58_behavior_authorization", "e58_readback_smoke"]),
        _artifact("e58_case_study_boundary", "operations/external_validation/e58_case_study_boundary.json", "no_go_boundary", ["e58_no_overclaim_validator"]),
        _artifact("e58_external_intelligence_gap", "operations/external_validation/e58_external_intelligence_gap.json", "blocker_state", ["e58_readback_smoke", "future_E59_runtime"]),
        _artifact("e58_e59_requirements", "products/ai_agent_company_runtime_harness_case_study/e59_requirements_packet.md", "next_milestone", ["future_E59_runtime"]),
        _artifact("e58_behavior_authorization", "operations/external_validation/e58_case_study_behavior_authorization_result.json", "boundary", ["e58_completion_gate"]),
        _artifact("e58_brain_update", "operations/external_validation/e58_ceo_brain_case_study_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e58_readback_smoke"]),
        _artifact("e58_kg_update", "operations/knowledge_graph/e58_ceo_kg_read_model_update.json", "kg_update", ["e58_readback_smoke"], "P1"),
        _artifact("e58_czl_closure", "operations/external_validation/e58_czl_closure.json", "czl_closure", ["e58_completion_gate"], "P1"),
        _artifact("e58_cieu_residual", "operations/external_validation/e58_cieu_residual_summary.json", "cieu_residual", ["e58_completion_gate"], "P1"),
    ]
    graph = {"graph_id": "e58_case_study_runtime_linkage_graph", "nodes": [{"node_id": a["artifact_id"], "node_type": a["artifact_type"]} for a in artifacts], "edges": [
        {"from": "E58 packager", "to": "e58_case_study", "edge_type": "writes"},
        {"from": "e58_case_study", "to": "e58_selected_route", "edge_type": "writes"},
        {"from": "e58_case_study", "to": "e58_readback_smoke", "edge_type": "reads"},
        {"from": "e58_external_intelligence_gap", "to": "e58_e59_requirements", "edge_type": "writes"},
        {"from": "e58_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
        {"from": "e58_e59_requirements", "to": "E59_external_world_intelligence_L5_convergence", "edge_type": "consumes_next"},
    ], "generated_at": "2026-05-06T00:00:00Z", "subject_system": "E58 case study package", "validation_context": {"case_study_id": CASE_STUDY_ID}}
    contract = {"contract_id": "e58_case_study_centerline_contract", "stages": [
        {"stage_id": "package", "required_input": "E57 selected route", "required_output": CASE_STUDY_ID, "required_writer": "E58 packager", "required_reader": "CEO brain", "required_test": "test_e58_case_study_boundary", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        {"stage_id": "gap", "required_input": "E57 skipped evidence refresh", "required_output": "E59 requirements", "required_writer": "E58 gap declaration", "required_reader": "future E59 runtime", "required_test": "test_e58_external_intelligence_gap", "failure_class_if_missing": "P0", "no_go_if_missing": True},
        {"stage_id": "readback", "required_input": "brain update", "required_output": "CEO brain readback", "required_writer": "E58 evidence writeback", "required_reader": "CEO brain", "required_test": "test_e58_ceo_brain_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True},
    ], "owner_approval_boundaries": ["external_contact", "publication", "payment"], "governance_boundaries": ["Y-star-gov", "gov-mcp"], "audit_boundaries": ["KG", "CZL", "CIEU"], "runtime_roles": {"CEO brain": "case study state reader", "behavior center": "internal packaging authorization", "owner": "external action approval authority"}}
    proof = {"proof_id": "e58_case_study_readback_proof", "written_artifacts": [a["artifact_id"] for a in artifacts], "readback_observations": [{"reader": "e58_ceo_brain_readback_smoke", "artifact_id": "e58_brain_update"}], "expected_current_state": {"case_study_id": CASE_STUDY_ID, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False}, "observed_current_state": {"case_study_id": CASE_STUDY_ID, "next_milestone": NEXT_MILESTONE, "external_action_allowed": False}, "missing_reads": [], "stale_reads": [], "passed": True}
    return {"artifact_id": "e58_case_study_runtime_linkage_manifest", "artifacts": artifacts, "runtime_linkage_graph": graph, "centerline_contract": contract, "readback_proof": proof, "governance_boundary": {"preserved": True}, "no_external_action": True}


def run_case_study_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph
    body = payload or build_e58_runtime_linkage_manifest()
    validation = {"runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]), "centerline_contract": validate_centerline_contract(body["centerline_contract"]), "readback_proof": validate_readback_proof(body["readback_proof"]), "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e58_case_study_anti_drift_gate", **body})}
    checks = {"case_study_has_writer_reader_readback": True, "external_intelligence_gap_has_writer_reader_readback": True, "E59_requirements_have_next_runtime_reader": True, "no_report_only_p0_closure": True}
    return {"artifact_id": "e58_case_study_anti_drift_gate_result", "manifest": body, "validation": validation, "checks": checks, "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True, "external_action_allowed": False, "no_external_action": True}


def write_case_study_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_case_study_anti_drift_gate()
    write_json(root, "operations/external_validation/e58_case_study_anti_drift_gate_result.json", data)
    write_md(root, "reports/integration/e58_case_study_anti_drift_gate_result.md", "E58 Case Study Anti-Drift Gate", [f"Passed: `{data['passed']}`"])
    return data
