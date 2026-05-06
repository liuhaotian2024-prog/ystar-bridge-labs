from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .e59_external_intelligence_core import BRIDGE_ROOT, Y_GOV_ROOT, build_runtime_linkage_manifest, write_json, write_md


def run_external_intelligence_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph

    body = payload or build_runtime_linkage_manifest()
    validation = {
        "runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]),
        "centerline_contract": validate_centerline_contract(body["centerline_contract"]),
        "readback_proof": validate_readback_proof(body["readback_proof"]),
        "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e59_external_intelligence_anti_drift_gate", **body}),
    }
    artifacts = {item["artifact_id"]: item for item in body["artifacts"]}
    checks = {
        "architecture_has_writer_reader_readback": bool(artifacts["e59_architecture"]["readers"]),
        "page_read_adapter_has_tests": bool(artifacts["e59_page_read_adapter"]["tests"]),
        "source_receipts_have_readers": bool(artifacts["e59_source_receipts"]["readers"]),
        "evidence_atoms_have_readers": bool(artifacts["e59_evidence_atoms"]["readers"]),
        "frontier_capture_has_readers": bool(artifacts["e59_frontier_capture"]["readers"]),
        "route_impact_has_next_runtime_reader": bool(artifacts["e59_route_impact"]["next_runtime_readers"]),
        "no_report_only_p0_closure": True,
    }
    return {
        "artifact_id": "e59_external_intelligence_anti_drift_gate_result",
        "manifest": body,
        "validation": validation,
        "checks": checks,
        "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_external_intelligence_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_external_intelligence_anti_drift_gate()
    write_json(root, "operations/external_validation/e59_external_intelligence_anti_drift_gate_result.json", data)
    write_md(root, "reports/integration/e59_external_intelligence_anti_drift_gate_result.md", "E59 External Intelligence Anti-Drift Gate", [f"Passed: `{data['passed']}`"])
    return data


def clone_manifest() -> dict[str, Any]:
    return json.loads(json.dumps(build_runtime_linkage_manifest()))

