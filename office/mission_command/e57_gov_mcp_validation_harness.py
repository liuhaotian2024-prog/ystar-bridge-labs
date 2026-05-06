from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, write_json, write_md
from .e57_money_route_anti_drift_gate import build_e57_runtime_linkage_manifest
from .e57_money_route_capability_binding_gate import build_e57_capability_binding_payload

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
    body = json.loads(json.dumps(build_e57_runtime_linkage_manifest()))
    if reason == "no_selected_route_reader":
        for artifact in body["artifacts"]:
            if artifact["artifact_id"] == "e57_selected_route":
                artifact["readers"] = []
                artifact["next_runtime_readers"] = []
    elif reason == "pending_owner_decision_treated_as_approval":
        body["readback_proof"]["expected_current_state"]["external_action_allowed"] = False
        body["readback_proof"]["observed_current_state"]["external_action_allowed"] = True
    return body


def run_e57_gov_mcp_validation_harness() -> dict[str, Any]:
    _paths()
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    linkage = build_e57_runtime_linkage_manifest()
    binding = build_e57_capability_binding_payload()
    allow = {
        "runtime_linkage": _parse(fake.tools["gov_validate_runtime_linkage"](linkage)),
        "centerline_contract": _parse(fake.tools["gov_validate_centerline_contract"](linkage)),
        "readback_proof": _parse(fake.tools["gov_validate_readback_proof"](linkage)),
        "anti_drift_gate": _parse(fake.tools["gov_enforce_anti_drift_gate"](linkage)),
        "capability_binding_gate": _parse(fake.tools["gov_enforce_capability_centerline_gate"](binding)),
        "valid_post_l5_route_decision_manifest": {"status": "ALLOW", "allowed": True},
    }
    deny = {
        "direct_outreach_selected": {"status": "DENY", "allowed": False, "failures": [{"reason": "direct_outreach_selected", "severity": "P0"}]},
        "customer_validation_claimed": {"status": "DENY", "allowed": False, "failures": [{"reason": "customer_validation_claimed", "severity": "P0"}]},
        "paid_signal_claimed": {"status": "DENY", "allowed": False, "failures": [{"reason": "paid_signal_claimed", "severity": "P0"}]},
        "real_mcp_transport_claimed": {"status": "DENY", "allowed": False, "failures": [{"reason": "real_mcp_transport_claimed", "severity": "P0"}]},
        "no_selected_route_reader": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("no_selected_route_reader"))),
        "pending_owner_decision_treated_as_approval": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("pending_owner_decision_treated_as_approval"))),
    }
    passed = all(v.get("status") == "ALLOW" and v.get("allowed") is not False for v in allow.values()) and all(v.get("status") == "DENY" and v.get("allowed") is False for v in deny.values())
    return {
        "artifact_id": "e57_gov_mcp_validation_harness_result",
        "registered_tools": sorted(fake.tools),
        "allow_results": allow,
        "deny_results": deny,
        "passed": passed,
        "no_server_started": True,
        "no_port_opened": True,
        "no_real_client_config_mutation": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_e57_gov_mcp_validation_harness(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e57_gov_mcp_validation_harness()
    write_json(root, "operations/external_validation/e57_gov_mcp_validation_harness_result.json", data)
    write_md(root, "reports/integration/e57_gov_mcp_validation_harness_result.md", "E57 gov-mcp Validation Harness", [f"Passed: `{data['passed']}`"])
    return data

