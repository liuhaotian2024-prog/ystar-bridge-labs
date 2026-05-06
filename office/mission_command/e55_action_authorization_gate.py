from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e55_behavior_action_model import build_broken_action_fixtures, build_seed_action_proposals

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _base_gate(owner_status: str = "pending_owner_decision") -> dict[str, Any]:
    return {
        "Y_star_gov_gate_result": {"status": "ALLOW", "allowed": True, "read_only_validator": True},
        "gov_mcp_gate_result": {"status": "ALLOW", "allowed": True, "fake_fastmcp_harness": True},
        "owner_approval_status": owner_status,
        "no_go_boundary_result": {"external_action_allowed": False, "pending_owner_decision_not_approval": True},
        "capability_binding_result": {"status": "ALLOW", "allowed": True},
        "anti_drift_result": {"status": "ALLOW", "allowed": True},
        "external_action_allowed": False,
        "no_external_action": True,
    }


def authorize_action(proposal: dict[str, Any]) -> dict[str, Any]:
    owner_status = _json("operations/external_validation/e54_ceo_brain_current_state_resolution.json").get("owner_approval_status") or "pending_owner_decision"
    gate = _base_gate(owner_status)
    action_type = proposal.get("action_type", "unknown")
    side = proposal.get("side_effect_profile") or {}
    evidence = proposal.get("evidence_path") or []
    status = "dry_run_only"
    reason = "internal action may run only as dry-run with evidence capture"
    if action_type in {"external_contact", "publication"}:
        status = "deny"
        reason = f"{action_type} denied while owner decision is pending"
    elif action_type in {"payment", "config_mutation", "server_process"}:
        status = "deny"
        reason = f"{action_type} denied without explicit owner/governance approval"
    elif action_type == "unknown":
        status = "quarantine"
        reason = "unknown action type defaults to quarantine"
    elif proposal.get("source") == "CEO_brain" and proposal.get("canonical_runtime_required") is False:
        status = "deny"
        reason = "CEO brain may propose but cannot execute behavior directly"
    elif proposal.get("canonical_runtime_required") is False:
        status = "deny"
        reason = "behavior action bypasses canonical runtime"
    elif not evidence:
        status = "deny"
        reason = "behavior action missing evidence path"
    elif side.get("claim_real_mcp_transport_closed"):
        status = "deny"
        reason = "real MCP transport closure cannot be claimed without proof"
    elif side.get("claim_customer_validation"):
        status = "deny"
        reason = "customer validation claim denied"
    elif side.get("claim_paid_signal"):
        status = "deny"
        reason = "paid signal claim denied"
    elif action_type == "public_readonly_observation":
        status = "owner_approval_required"
        reason = "future public-read-only observation is not executed in E55"
    return {"action_id": proposal.get("action_id"), "authorization_status": status, "reason": reason, **gate}


def run_authorization_gate() -> dict[str, Any]:
    proposals = build_seed_action_proposals()
    fixtures = build_broken_action_fixtures()
    proposal_results = [authorize_action(p) for p in proposals]
    fixture_results = [authorize_action(f) for f in fixtures]
    allowed = [r["action_id"] for r in proposal_results if r["authorization_status"] in {"allow", "dry_run_only"}]
    denied = [r["action_id"] for r in fixture_results if r["authorization_status"] == "deny"]
    quarantined = [r["action_id"] for r in fixture_results if r["authorization_status"] == "quarantine"]
    owner_required = [r["action_id"] for r in proposal_results + fixture_results if r["authorization_status"] == "owner_approval_required"]
    dry_run = [r["action_id"] for r in proposal_results if r["authorization_status"] == "dry_run_only"]
    checks = {
        "internal_validation_dry_run_only": "e55_validate_behavior_action_model" in dry_run,
        "external_contact_denied": "fixture_external_contact_pending_owner" in denied,
        "publication_denied": "fixture_publication_pending_owner" in denied,
        "payment_secret_denied": "fixture_payment_secret_action" in denied,
        "real_mcp_transport_claim_denied": "fixture_real_mcp_transport_claim" in denied,
        "customer_validation_claim_denied": "fixture_customer_validation_claim" in denied,
        "paid_signal_claim_denied": "fixture_paid_signal_claim" in denied,
        "unknown_action_quarantined": "fixture_unknown_action" in quarantined,
        "ceo_brain_direct_execution_denied": "fixture_ceo_brain_direct_execution" in denied,
        "missing_evidence_denied": "fixture_missing_evidence_path" in denied,
        "canonical_runtime_bypass_denied": "fixture_bypass_canonical_runtime" in denied,
    }
    return {
        "artifact_id": "e55_action_authorization_gate_result",
        "gate_status": "passed" if all(checks.values()) else "failed",
        "proposal_results": proposal_results,
        "fixture_results": fixture_results,
        "allowed_actions": allowed,
        "denied_actions": denied,
        "quarantined_actions": quarantined,
        "owner_approval_required_actions": owner_required,
        "dry_run_only_actions": dry_run,
        "reasons": {r["action_id"]: r["reason"] for r in proposal_results + fixture_results},
        "checks": checks,
        "external_action_allowed": False,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def write_action_authorization_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_authorization_gate()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_action_authorization_gate_result.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = "# E55 Action Authorization Gate\n\nGate status: `%s`\n\nDry-run-only actions: `%s`\n\nDenied actions: `%s`\n" % (data["gate_status"], len(data["dry_run_only_actions"]), len(data["denied_actions"]))
    (root / "reports/integration/e55_action_authorization_gate_result.md").write_text(md, encoding="utf-8")
    return data
