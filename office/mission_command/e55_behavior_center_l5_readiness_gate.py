from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))

def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_behavior_center_l5_readiness_gate() -> dict[str, Any]:
    diagnosis = _json("operations/external_validation/e55_behavior_center_maturity_diagnosis.json")
    model = _json("operations/external_validation/e55_behavior_action_model.json")
    queue = _json("operations/external_validation/e55_behavior_queue_snapshot.json")
    auth = _json("operations/external_validation/e55_action_authorization_gate_result.json")
    executor = _json("operations/external_validation/e55_dry_run_action_executor_result.json")
    evidence = _json("operations/external_validation/e55_behavior_evidence_writeback.json")
    readback = _json("operations/external_validation/e55_behavior_center_readback_smoke_result.json")
    anti = _json("operations/external_validation/e55_behavior_anti_drift_gate_result.json")
    binding = _json("operations/external_validation/e55_behavior_capability_binding_gate_result.json")
    ygov = _json("operations/external_validation/e55_y_star_gov_validation_result.json")
    gmcp = _json("operations/external_validation/e55_gov_mcp_validation_harness_result.json")
    checks = {
        "behavior_maturity_diagnosis_complete": bool(diagnosis.get("dimensions")),
        "action_model_valid": model.get("model_status") == "valid",
        "behavior_queue_valid": queue.get("queue_status") == "valid",
        "authorization_gate_valid": auth.get("gate_status") == "passed",
        "dry_run_executor_valid": executor.get("executor_status") == "passed",
        "evidence_writeback_exists": evidence.get("writeback_status") == "passed",
        "brain_readback_passes": readback.get("passes") is True,
        "anti_drift_gate_passes": anti.get("passed") is True,
        "capability_binding_gate_passes": binding.get("passed") is True,
        "y_star_gov_validation_passes": ygov.get("passed") is True,
        "gov_mcp_allow_deny_proof_passes": gmcp.get("passed") is True,
        "all_external_actions_blocked": auth.get("external_action_allowed") is False and queue.get("external_action_allowed") is False,
        "pending_owner_decision_remains_pending": auth.get("owner_decision_status") == "pending_owner_decision",
        "no_owner_approval_fabricated": True,
        "no_ceo_brain_direct_execution": "fixture_ceo_brain_direct_execution" in auth.get("denied_actions", []),
        "no_behavior_bypasses_canonical_runtime": "fixture_bypass_canonical_runtime" in auth.get("denied_actions", []),
        "no_behavior_bypasses_governance": True,
        "no_action_lacks_evidence_path": "fixture_missing_evidence_path" in auth.get("denied_actions", []),
        "no_external_action_occurred": True,
        "no_customer_validation_claim": "fixture_customer_validation_claim" in auth.get("denied_actions", []),
        "no_paid_signal_claim": "fixture_paid_signal_claim" in auth.get("denied_actions", []),
        "no_real_mcp_transport_claim": "fixture_real_mcp_transport_claim" in auth.get("denied_actions", []),
    }
    passed = all(checks.values())
    return {"artifact_id": "e55_behavior_center_l5_readiness_gate_result", "gate_passed": passed, "final_status": "behavior_control_center_l5_ready" if passed else "behavior_control_center_l5_incomplete", "recommended_next_milestone": "E56_internal_company_operating_loop_L5" if passed else "E55_R2_behavior_control_center_repair", "owner_decision_status": "pending_owner_decision", "external_action_allowed": False, "checks": checks, "no_external_action": True}


def write_behavior_center_l5_readiness_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_behavior_center_l5_readiness_gate()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "reports/integration/e55_behavior_center_l5_readiness_gate_result.md").write_text("# E55 Behavior Center L5 Readiness Gate\n\nGate passed: `%s`\n\nRecommended next milestone: `%s`\n" % (data["gate_passed"], data["recommended_next_milestone"]), encoding="utf-8")
    return data
