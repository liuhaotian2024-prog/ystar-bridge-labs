#!/usr/bin/env python3
"""Build L7.1 review-gated memory dry-run lane outputs."""

from __future__ import annotations

from common import artifact_ref, base_no_action_receipt, base_packet, lane_summary, write_json


LANE_ID = "L7.1E"
LANE_NAME = "Review-Gated Memory Dry-Run v1"
OUT = "l7_review_gated_memory_dry_run_v1"


def candidate(candidate_id: str, target_layer: str, proposed_update: str, source_artifact: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "source_artifact": artifact_ref(source_artifact),
        "proposed_update": proposed_update,
        "target_layer": target_layer,
        "evidence_basis": [artifact_ref("ceo_command_brief/l6_16_ceo_command_brief.json"), artifact_ref("l7_parallel_commercial_autonomy_sprint/l7_1_summary.json")],
        "reason": "Promote reviewed commercial autonomy learning only as a candidate.",
        "expected_value": "Improves future commercial planning after review.",
        "risk_if_wrong": "Could steer future priorities incorrectly if written without review.",
        "required_human_approval": True,
        "default_decision": "blocked_until_approved",
        "dry_run_only": True,
    }


def build() -> None:
    memory = {
        **base_packet("memory_update_candidates"),
        "candidates": [
            candidate("l7_1_memory_candidate_001", "agent working memory", "Remember that revenue discovery and offer drafting are allowed before external action approval.", "policy/revenue_action_policy.json")
        ],
    }
    write_json(f"{OUT}/memory_update_candidates.json", memory)

    brain = {
        **base_packet("brain_update_candidates"),
        "candidates": [
            candidate("l7_1_brain_candidate_001", "CEO brain/profile", "Prioritize owner-visible money path: opportunity radar, offer hypothesis, approval workflow, then approved execution.", "l7_owner_runtime_cockpit_v2/owner_cockpit_v2.json")
        ],
    }
    write_json(f"{OUT}/brain_update_candidates.json", brain)

    canonical = {
        **base_packet("canonical_strategy_update_candidates"),
        "candidates": [
            candidate("l7_1_canonical_candidate_001", "canonical strategy", "Commercial autonomy proceeds by staged read/draft/approval before execution.", "policy/action_capability_registry.json")
        ],
    }
    write_json(f"{OUT}/canonical_strategy_update_candidates.json", canonical)

    capability = {
        **base_packet("capability_registry_update_candidates"),
        "candidates": [
            candidate("l7_1_capability_candidate_001", "capability registry", "Add L7.1 one-command commercial autonomy sprint runner as owner-burden reduction capability.", "scripts/run_l7_1_parallel_sprint.sh")
        ],
    }
    write_json(f"{OUT}/capability_registry_update_candidates.json", capability)

    receipts = {
        **base_packet("writeback_dry_run_receipts"),
        "dry_run_receipts": [
            {"candidate_id": item["candidate_id"], "dry_run_only": True, "actual_writeback_occurred": False, "default_decision": "blocked_until_approved"}
            for payload in [memory, brain, canonical, capability]
            for item in payload["candidates"]
        ],
    }
    write_json(f"{OUT}/writeback_dry_run_receipts.json", receipts)

    approval_requests = {
        **base_packet("writeback_approval_requests"),
        "requests": [
            {"candidate_id": item["candidate_id"], "approval_required": True, "default_decision": "blocked_until_approved"}
            for payload in [memory, brain, canonical, capability]
            for item in payload["candidates"]
        ],
    }
    write_json(f"{OUT}/writeback_approval_requests.json", approval_requests)

    risk = {
        **base_packet("writeback_risk_register"),
        "risks": [
            {"risk_id": "writeback_risk_001", "risk": "premature strategy persistence", "mitigation": "human approval gate and dry-run receipts only"},
        ],
    }
    write_json(f"{OUT}/writeback_risk_register.json", risk)
    write_json(f"{OUT}/writeback_no_action_receipt.json", base_no_action_receipt(LANE_ID, LANE_NAME))
    summary = lane_summary(LANE_ID, LANE_NAME, OUT, "completed", {"dry_run_candidates": 4, "actual_writeback_occurred": False})
    write_json(f"{OUT}/l7_1_memory_dry_run_summary.json", summary)


if __name__ == "__main__":
    build()
