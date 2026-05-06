from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e55_behavior_action_model import build_seed_action_proposals

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def classify_action_type(proposal: dict[str, Any]) -> str:
    action_type = proposal.get("action_type", "unknown")
    if action_type in {"external_contact", "publication", "payment", "config_mutation", "server_process"}:
        return "blocked_or_owner_approval_required"
    if action_type in {"internal_analysis", "internal_packaging", "internal_validation", "internal_dispatch"}:
        return "internal_dry_run_candidate"
    if action_type == "public_readonly_observation":
        return "future_public_readonly_candidate"
    return "unknown_blocked"


def validate_queue_item(item: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if not item.get("action_id"):
        failures.append("missing_action_id")
    if item.get("source") == "CEO_brain" and item.get("queue_status") == "ready_to_execute":
        failures.append("ceo_brain_cannot_enqueue_direct_execution")
    if item.get("external_action_allowed") is True and item.get("owner_approval_status") != "approved_explicitly":
        failures.append("external_action_without_owner_approval")
    return {"valid": not failures, "failures": failures}


def enqueue_action_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    cls = classify_action_type(proposal)
    status = "queued_dry_run_only" if cls == "internal_dry_run_candidate" else "blocked_pending_owner_decision"
    if proposal.get("action_id") in {"e56_internal_company_operating_loop_l5", "e57_post_l5_money_route_retest"}:
        status = "future_not_executed"
    return {
        **proposal,
        "classification": cls,
        "queue_status": status,
        "owner_approval_status": "pending_owner_decision",
        "external_action_allowed": False,
        "canonical_runtime_required": proposal.get("canonical_runtime_required", True),
        "no_external_action": True,
    }


def prioritize_internal_safe_actions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {"queued_dry_run_only": 0, "future_not_executed": 1, "blocked_pending_owner_decision": 2}
    return sorted(items, key=lambda item: (order.get(item.get("queue_status"), 9), item.get("action_id", "")))


def block_external_actions_without_approval(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocked = []
    for item in items:
        if item.get("classification") == "blocked_or_owner_approval_required":
            item = {**item, "queue_status": "blocked_pending_owner_decision", "external_action_allowed": False}
        blocked.append(item)
    return blocked


def produce_queue_snapshot() -> dict[str, Any]:
    proposals = build_seed_action_proposals()
    base = proposals[0]
    future = [
        {**base, "action_id": "e56_internal_company_operating_loop_l5", "action_type": "internal_dispatch", "intent": "Future internal company operating loop L5 dry-run; not executed in E55.", "expected_outputs": ["future_e56_internal_loop"], "evidence_path": ["future_e56_evidence"]},
        {**base, "action_id": "e57_post_l5_money_route_retest", "action_type": "public_readonly_observation", "intent": "Future post-L5 money route retest; not executed in E55.", "expected_outputs": ["future_e57_money_route_retest"], "evidence_path": ["future_e57_evidence"]},
        {**base, "action_id": "e53_e54_external_review_track", "action_type": "external_contact", "intent": "Controlled first-user review track remains frozen pending owner decision.", "externality_level": "external_human", "owner_approval_required": True, "expected_outputs": [], "evidence_path": ["operations/external_validation/e53_first_user_review_risk_gate_result.json"]},
    ]
    items = block_external_actions_without_approval([enqueue_action_proposal(p) for p in proposals + future])
    items = prioritize_internal_safe_actions(items)
    validations = {item["action_id"]: validate_queue_item(item) for item in items}
    return {
        "artifact_id": "e55_behavior_queue_snapshot",
        "queue_status": "valid",
        "items": items,
        "validations": validations,
        "dry_run_only_actions": [i["action_id"] for i in items if i["queue_status"] == "queued_dry_run_only"],
        "blocked_actions": [i["action_id"] for i in items if i["queue_status"] == "blocked_pending_owner_decision"],
        "future_not_executed_actions": [i["action_id"] for i in items if i["queue_status"] == "future_not_executed"],
        "pending_owner_decision_not_approval": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_behavior_queue_snapshot(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = produce_queue_snapshot()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_queue_snapshot.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = "# E55 Behavior Queue Snapshot\n\nQueue status: `%s`\n\nDry-run-only actions: `%s`\n\nBlocked actions: `%s`\n" % (data["queue_status"], len(data["dry_run_only_actions"]), len(data["blocked_actions"]))
    (root / "reports/integration/e55_behavior_queue_snapshot.md").write_text(md, encoding="utf-8")
    return data
