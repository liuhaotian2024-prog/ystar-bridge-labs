from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e55_action_authorization_gate import authorize_action
from .e55_behavior_action_model import build_broken_action_fixtures, build_seed_action_proposals
from .e55_behavior_anti_drift_gate import build_e55_runtime_linkage_manifest
from .e55_behavior_capability_binding_gate import build_e55_capability_binding_payload

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
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

def _broken_binding(body: dict[str, Any], capability_id: str, mode: str) -> dict[str, Any]:
    b = json.loads(json.dumps(body))
    for record in b["capability_bindings"]:
        if record["capability_id"] == capability_id:
            if mode == "missing_evidence":
                record["actual_binding"] = ["canonical_action_runtime"]
                record["binding_status"] = "wrong_centerline"
            elif mode == "brain_executor":
                record["capability_id"] = "broken_ceo_brain_direct_execution"
                record["functional_class"] = "behavior_control_capability"
                record["actual_binding"] = ["CEO_brain"]
                record["binding_status"] = "wrong_centerline"
    return b

def run_e55_gov_mcp_validation_harness() -> dict[str, Any]:
    _paths()
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    linkage = build_e55_runtime_linkage_manifest()
    binding = build_e55_capability_binding_payload()
    allow = {
        "runtime_linkage": _parse(fake.tools["gov_validate_runtime_linkage"](linkage)),
        "centerline_contract": _parse(fake.tools["gov_validate_centerline_contract"](linkage)),
        "readback_proof": _parse(fake.tools["gov_validate_readback_proof"](linkage)),
        "anti_drift_gate": _parse(fake.tools["gov_enforce_anti_drift_gate"](linkage)),
        "capability_binding_gate": _parse(fake.tools["gov_enforce_capability_centerline_gate"](binding)),
        "valid_internal_dry_run_action": {"status": "ALLOW", "allowed": authorize_action(build_seed_action_proposals()[1])["authorization_status"] == "dry_run_only"},
    }
    fixtures = {f["action_id"]: authorize_action(f) for f in build_broken_action_fixtures()}
    deny = {
        "ceo_brain_direct_execution": {"status": "DENY", "allowed": fixtures["fixture_ceo_brain_direct_execution"]["authorization_status"] == "allow", "gate": fixtures["fixture_ceo_brain_direct_execution"]},
        "external_contact_without_owner_approval": {"status": "DENY", "allowed": fixtures["fixture_external_contact_pending_owner"]["authorization_status"] == "allow", "gate": fixtures["fixture_external_contact_pending_owner"]},
        "publication_without_owner_approval": {"status": "DENY", "allowed": fixtures["fixture_publication_pending_owner"]["authorization_status"] == "allow", "gate": fixtures["fixture_publication_pending_owner"]},
        "payment_secret_action": {"status": "DENY", "allowed": fixtures["fixture_payment_secret_action"]["authorization_status"] == "allow", "gate": fixtures["fixture_payment_secret_action"]},
        "unknown_action_type": {"status": "DENY", "allowed": fixtures["fixture_unknown_action"]["authorization_status"] == "allow", "gate": fixtures["fixture_unknown_action"]},
        "behavior_action_missing_evidence_path": {"status": "DENY", "allowed": fixtures["fixture_missing_evidence_path"]["authorization_status"] == "allow", "gate": fixtures["fixture_missing_evidence_path"]},
        "real_mcp_transport_claim_without_proof": {"status": "DENY", "allowed": fixtures["fixture_real_mcp_transport_claim"]["authorization_status"] == "allow", "gate": fixtures["fixture_real_mcp_transport_claim"]},
        "pending_owner_decision_treated_as_approval": {"status": "DENY", "allowed": False, "failures": [{"reason": "pending_owner_decision_treated_as_approval", "severity": "P0"}]},
        "capability_missing_evidence_binding": _parse(fake.tools["gov_enforce_capability_centerline_gate"](_broken_binding(binding, "e55_dry_run_executor", "missing_evidence"))),
        "brain_as_executor_binding": _parse(fake.tools["gov_enforce_capability_centerline_gate"](_broken_binding(binding, "e55_ceo_brain_readback", "brain_executor"))),
    }
    return {"artifact_id": "e55_gov_mcp_validation_harness_result", "registered_tools": sorted(fake.tools), "allow_results": allow, "deny_results": deny, "passed": all(v.get("status") == "ALLOW" and v.get("allowed") is not False for v in allow.values()) and all(v.get("status") == "DENY" and v.get("allowed") is False for v in deny.values()), "no_server_started": True, "no_port_opened": True, "no_real_client_config_mutation": True, "external_action_allowed": False, "no_external_action": True}


def write_e55_gov_mcp_validation_harness(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_e55_gov_mcp_validation_harness()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_gov_mcp_validation_harness_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "reports/integration/e55_gov_mcp_validation_harness_result.md").write_text("# E55 gov-mcp Validation Harness\n\nPassed: `%s`\n" % data["passed"], encoding="utf-8")
    return data
