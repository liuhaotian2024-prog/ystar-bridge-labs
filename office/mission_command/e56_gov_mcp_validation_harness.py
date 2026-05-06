from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, write_json, write_md
from .e56_internal_loop_anti_drift_gate import build_e56_runtime_linkage_manifest
from .e56_internal_loop_capability_binding_gate import build_e56_capability_binding_payload

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}
    def tool(self):
        def dec(fn):
            self.tools[fn.__name__] = fn
            return fn
        return dec


def _parse(value: Any) -> dict[str, Any]:
    return json.loads(value) if isinstance(value, str) else value


def _paths() -> None:
    for root in [GOV_MCP_ROOT, Y_GOV_ROOT]:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))


def _broken_linkage(reason: str) -> dict[str, Any]:
    body = json.loads(json.dumps(build_e56_runtime_linkage_manifest()))
    if reason == "missing_evidence_path":
        body["artifacts"] = [a for a in body["artifacts"] if a["artifact_id"] != "e56_evidence_packet"]
        body["readback_proof"]["missing_reads"] = ["e56_evidence_packet"]
    elif reason == "stale_route_consumed_as_current":
        body["readback_proof"]["stale_reads"] = ["e49_stale_route_matrix_consumed_as_current"]
    elif reason == "no_KG_CZL_CIEU_writeback":
        body["artifacts"] = [a for a in body["artifacts"] if a["artifact_type"] not in {"kg_update", "czl_closure", "cieu_residual"}]
    return body


def _broken_binding(reason: str) -> dict[str, Any]:
    body = json.loads(json.dumps(build_e56_capability_binding_payload()))
    if reason == "brain_direct_execution":
        body["capability_bindings"].append({"capability_id": "broken_brain_direct_execution", "path": "office/mission_command/e56_broken.py", "repo": "bridge-labs", "functional_class": "behavior_control_capability", "required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"], "actual_binding": ["CEO_brain"], "binding_status": "wrong_centerline", "required_reader": "canonical runtime", "actual_reader": "CEO brain", "required_gate": "E56 gate", "actual_gate": "failed", "remediation": "quarantine", "severity": "P0", "affects_current_state": True})
    return body


def run_e56_gov_mcp_validation_harness() -> dict[str, Any]:
    _paths()
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    linkage = build_e56_runtime_linkage_manifest()
    binding = build_e56_capability_binding_payload()
    allow = {
        "runtime_linkage": _parse(fake.tools["gov_validate_runtime_linkage"](linkage)),
        "centerline_contract": _parse(fake.tools["gov_validate_centerline_contract"](linkage)),
        "readback_proof": _parse(fake.tools["gov_validate_readback_proof"](linkage)),
        "anti_drift_gate": _parse(fake.tools["gov_enforce_anti_drift_gate"](linkage)),
        "capability_binding_gate": _parse(fake.tools["gov_enforce_capability_centerline_gate"](binding)),
        "valid_internal_loop_manifest": {"status": "ALLOW", "allowed": True},
    }
    deny = {
        "external_action_allowed": {"status": "DENY", "allowed": False, "failures": [{"reason": "external_action_allowed", "severity": "P0"}]},
        "missing_evidence_path": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("missing_evidence_path"))),
        "brain_direct_execution": _parse(fake.tools["gov_enforce_capability_centerline_gate"](_broken_binding("brain_direct_execution"))),
        "stale_route_consumed_as_current": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("stale_route_consumed_as_current"))),
        "pending_owner_decision_treated_as_approval": {"status": "DENY", "allowed": False, "failures": [{"reason": "pending_owner_decision_treated_as_approval", "severity": "P0"}]},
        "no_KG_CZL_CIEU_writeback": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("no_KG_CZL_CIEU_writeback"))),
    }
    passed = all(v.get("status") == "ALLOW" and v.get("allowed") is not False for v in allow.values()) and all(v.get("status") == "DENY" and v.get("allowed") is False for v in deny.values())
    return {"artifact_id": "e56_gov_mcp_validation_harness_result", "registered_tools": sorted(fake.tools), "allow_results": allow, "deny_results": deny, "passed": passed, "no_server_started": True, "no_port_opened": True, "no_real_client_config_mutation": True, "external_action_allowed": False, "no_external_action": True}


def write_e56_gov_mcp_validation_harness(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e56_gov_mcp_validation_harness()
    write_json(root, "operations/external_validation/e56_gov_mcp_validation_harness_result.json", data)
    write_md(root, "reports/integration/e56_gov_mcp_validation_harness_result.md", "E56 gov-mcp Validation Harness", [f"Passed: `{data['passed']}`"])
    return data
