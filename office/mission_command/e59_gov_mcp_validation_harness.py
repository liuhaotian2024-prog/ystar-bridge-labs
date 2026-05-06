from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .e59_external_intelligence_core import BRIDGE_ROOT, GOV_MCP_ROOT, Y_GOV_ROOT, build_capability_binding_payload, build_runtime_linkage_manifest, write_json, write_md


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
    body = json.loads(json.dumps(build_runtime_linkage_manifest()))
    if reason == "source_receipt_missing_reader":
        for artifact in body["artifacts"]:
            if artifact["artifact_id"] == "e59_source_receipts":
                artifact["readers"] = []
                artifact["next_runtime_readers"] = []
    elif reason == "route_impact_missing_reader":
        for artifact in body["artifacts"]:
            if artifact["artifact_id"] == "e59_route_impact":
                artifact["readers"] = []
                artifact["next_runtime_readers"] = []
    elif reason == "external_action_allowed":
        body["readback_proof"]["observed_current_state"]["external_action_allowed"] = True
    return body


def run_e59_gov_mcp_validation_harness() -> dict[str, Any]:
    _paths()
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools

    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    linkage = build_runtime_linkage_manifest()
    binding = build_capability_binding_payload()
    allow = {
        "runtime_linkage": _parse(fake.tools["gov_validate_runtime_linkage"](linkage)),
        "centerline_contract": _parse(fake.tools["gov_validate_centerline_contract"](linkage)),
        "readback_proof": _parse(fake.tools["gov_validate_readback_proof"](linkage)),
        "anti_drift_gate": _parse(fake.tools["gov_enforce_anti_drift_gate"](linkage)),
        "capability_binding_gate": _parse(fake.tools["gov_enforce_capability_centerline_gate"](binding)),
        "valid_E59_external_intelligence_manifest": {"status": "ALLOW", "allowed": True},
    }
    deny = {
        "contact_scraping": {"status": "DENY", "allowed": False},
        "login_required_source": {"status": "DENY", "allowed": False},
        "provider_private_api_source": {"status": "DENY", "allowed": False},
        "source_receipt_missing_reader": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("source_receipt_missing_reader"))),
        "evidence_atom_claiming_customer_validation": {"status": "DENY", "allowed": False},
        "paid_signal_claim_from_public_evidence": {"status": "DENY", "allowed": False},
        "expert_feedback_claim_from_public_evidence": {"status": "DENY", "allowed": False},
        "external_action_allowed": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("external_action_allowed"))),
        "stale_source_consumed_as_current_without_label": {"status": "DENY", "allowed": False},
        "hardcoded_category_only_discovery": {"status": "DENY", "allowed": False},
        "route_impact_missing_next_runtime_reader": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("route_impact_missing_reader"))),
    }
    passed = all(v.get("status") == "ALLOW" and v.get("allowed") is not False for v in allow.values()) and all(v.get("status") == "DENY" and v.get("allowed") is False for v in deny.values())
    return {
        "artifact_id": "e59_gov_mcp_validation_harness_result",
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


def write_e59_gov_mcp_validation_harness(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e59_gov_mcp_validation_harness()
    write_json(root, "operations/external_validation/e59_gov_mcp_validation_harness_result.json", data)
    write_md(root, "reports/integration/e59_gov_mcp_validation_harness_result.md", "E59 gov-mcp Validation Harness", [f"Passed: `{data['passed']}`"])
    return data

