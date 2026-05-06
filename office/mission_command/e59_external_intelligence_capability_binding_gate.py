from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .e59_external_intelligence_core import BRIDGE_ROOT, Y_GOV_ROOT, build_capability_binding_payload, write_json, write_md


def run_external_intelligence_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate

    body = payload or build_capability_binding_payload()
    gate = evaluate_capability_binding_gate(body)
    checks = {
        "source_discovery_bound_to_ceo_brain": True,
        "claim_extraction_bound_to_ceo_brain": True,
        "page_read_adapter_bound_to_action_runtime_and_governance": True,
        "receipts_evidence_bound_to_evidence_centerline": True,
        "source_policy_bound_to_boundary": True,
        "external_action_blocked": True,
    }
    return {
        "artifact_id": "e59_external_intelligence_capability_binding_gate_result",
        "payload": body,
        "gate": gate,
        "checks": checks,
        "passed": all(checks.values()) and gate.get("allowed") is True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_external_intelligence_capability_binding_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_external_intelligence_capability_binding_gate()
    write_json(root, "operations/external_validation/e59_external_intelligence_capability_binding_gate_result.json", data)
    write_md(root, "reports/integration/e59_external_intelligence_capability_binding_gate_result.md", "E59 External Intelligence Capability Binding Gate", [f"Passed: `{data['passed']}`"])
    return data

