from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, FINAL_STATUS, NEXT_MILESTONE, readiness_checks, write_json, write_md


def run_external_world_intelligence_l5_readiness_gate(root: Path | None = None) -> dict:
    checks = readiness_checks(root)
    passed = all(checks.values())
    return {
        "artifact_id": "e59_external_world_intelligence_l5_readiness_gate_result",
        "gate_passed": passed,
        "final_status": FINAL_STATUS if passed else "external_world_intelligence_L5_incomplete",
        "recommended_next_milestone": NEXT_MILESTONE if passed else "E59_R2_external_intelligence_repair",
        "live_public_read_status": "live_public_read_unavailable_nonfatal",
        "checks": checks,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "real_mcp_transport_claimed": False,
        "no_external_action": True,
    }


def write_external_world_intelligence_l5_readiness_gate(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_world_intelligence_l5_readiness_gate(root)
    write_json(root, "operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", data)
    write_md(root, "reports/integration/e59_external_world_intelligence_l5_readiness_gate_result.md", "E59 External World Intelligence L5 Readiness Gate", [
        f"Gate passed: `{data['gate_passed']}`",
        f"Final status: `{data['final_status']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
        "No live fresh market read occurred because live public reads are unavailable/nonfatal in this sandbox.",
    ])
    return data

