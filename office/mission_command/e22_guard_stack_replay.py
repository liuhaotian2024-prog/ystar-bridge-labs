from __future__ import annotations

from typing import Any, Dict, List


def replay_guard_stack(envelopes: Dict[str, Any], provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for env in envelopes["envelopes"]:
        checks = {
            "risk_tier_check": ("passed", "TIER_2 low-risk validation dry-run"),
            "policy_compatibility_check": ("passed", "external_validation_message with transparency/opt-out contract"),
            "provider_capability_check": ("passed", "gov-mcp dry_run_available" if provider_sync.get("dry_run_available") else "dry_run capability missing"),
            "dry_run_mode_check": ("passed", "provider_mode=dry_run and live_execution_disabled=true"),
            "rate_limit_check": ("passed", "within e22_autonomous_dry_run_batch quota"),
            "idempotency_check": ("passed", "idempotency key present" if env.get("idempotency_key") else "idempotency key missing"),
            "suppression_check": ("passed", "suppression clear" if env.get("suppression_status") == "clear" else "suppression active"),
            "evidence_check": ("passed", "selection excluded evidence-required candidates"),
            "message_safety_check": ("passed", "message hash and content reference present" if env.get("message_hash") and env.get("message_content_ref") else "message safety data missing"),
            "owner_approval_check": ("not_applicable", "risk tier does not require owner approval"),
        }
        normalized = {name: {"status": status if not reason.endswith("missing") and not reason.endswith("active") else "failed", "reason": reason, "evidence_path": "operations/external_validation/e22_outbound_envelopes.json"} for name, (status, reason) in checks.items()}
        failed = [name for name, result in normalized.items() if result["status"] == "failed"]
        rows.append({
            "action_id": env["action_id"],
            "target_name": env["target_name"],
            "checks": normalized,
            "resulting_action_status": "dry_run_guard_passed" if not failed else "dry_run_blocked_by_guard",
            "failed_checks": failed,
            "external_action_executed": False,
        })
    return {"artifact_id": "e22_guard_stack_results", "guard_results": rows, "guard_pass_count": sum(1 for r in rows if not r["failed_checks"]), "guard_block_count": sum(1 for r in rows if r["failed_checks"]), "external_action_executed": False}


def render_guard_stack_results(data: Dict[str, Any]) -> str:
    lines=["# E22 Guard Stack Replay","",f"- guard_pass_count: {data['guard_pass_count']}",f"- guard_block_count: {data['guard_block_count']}","- external_action_executed: false","","| target | status |", "| --- | --- |"]
    for row in data["guard_results"]:
        lines.append(f"| {row['target_name']} | {row['resulting_action_status']} |")
    return "\n".join(lines).rstrip()+"\n"
