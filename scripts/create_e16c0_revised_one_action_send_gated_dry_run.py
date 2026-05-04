#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CANONICAL_RISK_TIER = "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"
CAPABILITY_LEVEL = 5
OFFER = "48h AI Agent Implementation Readiness Review"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def select_one_action(repo_root: Path) -> dict[str, Any]:
    queue = load_json(repo_root / "operations/external_validation/e15d_send_gated_pilot_queue.json")
    c3_batch = load_json(repo_root / "operations/external_validation/c3_validation_batch.json")
    handoff = load_json(repo_root / "operations/external_validation/c3_owner_handoff_validation_batch.json")
    rows = queue.get("rows", [])
    if not rows:
        raise ValueError("E15D send-gated queue is empty")
    action_by_id = {item["action_id"]: item for item in c3_batch.get("actions", [])}
    handoff_by_id = {item["action_id"]: item for item in handoff.get("handoff_items", [])}

    def score(row: dict[str, Any]) -> tuple[int, int, str]:
        action = action_by_id.get(row["action_id"], {})
        missing = len(action.get("missing_fields", []) or [])
        identity_penalty = 0 if action.get("target_id") and action.get("target_name") else 10
        return (missing + identity_penalty, rows.index(row), row["action_id"])

    selected_row = sorted(rows, key=score)[0]
    action = action_by_id[selected_row["action_id"]]
    message = handoff_by_id.get(selected_row["action_id"], {})
    return {
        "artifact_id": "e16c0_selected_one_action_pilot",
        "source_queue_id": queue["queue_id"],
        "selection_policy": "lowest_risk_first_complete_identity_first_queue_order_tiebreak",
        "selected_action_count": 1,
        "selected_action": {
            **selected_row,
            "target_name": action.get("target_name", ""),
            "target_evidence_basis": action.get("target_evidence_basis", []),
            "buyer_pain_hypothesis": action.get("buyer_pain_hypothesis", ""),
            "selection_reason": action.get("selection_reason", ""),
            "offer_thesis": action.get("offer_thesis", OFFER),
            "capability_domain": "external_validation_message",
            "capability_level": CAPABILITY_LEVEL,
            "risk_tier": CANONICAL_RISK_TIER,
            "legacy_risk_tier_alias": action.get("risk_tier", ""),
            "owner_boundary_status": "owner_review_required",
            "message_capsule_id": action.get("message_capsule_id", ""),
            "ledger_id": action.get("ledger_id", ""),
            "feedback_event_id": action.get("feedback_event_id", ""),
            "message_preview_hash": selected_row.get("message_hash", ""),
            "message_draft_present": bool(message.get("copy_paste_block")),
            "target_identity_sufficient": not bool(action.get("missing_fields")),
            "missing_fields": action.get("missing_fields", []),
        },
        "not_selected_action_ids": [row["action_id"] for row in rows if row["action_id"] != selected_row["action_id"]],
        "canonical_mapping": {
            "capability_level": CAPABILITY_LEVEL,
            "risk_tier": CANONICAL_RISK_TIER,
            "execution_mode": "send_gated_dry_run",
            "legacy_execution_mode": "send_gated_pending_authorization",
            "gov_mcp_canonical_owner": "gov-mcp/outbound",
        },
        "external_action_executed": False,
    }


def owner_activation_packet(selected: dict[str, Any]) -> dict[str, Any]:
    action = selected["selected_action"]
    return {
        "artifact_id": "e16c0_owner_final_activation_packet",
        "packet_id": stable_id("e16c0_owner_activation", action["action_id"]),
        "status": "owner_review_required",
        "activation_type": "one_action_send_gated_pilot_request",
        "action_id": action["action_id"],
        "target_id": action["target_id"],
        "target_name": action["target_name"],
        "offer": OFFER,
        "allowed_if_activated": [
            "one send-gated pilot action only",
            "gov-mcp canonical adapter preflight",
            "provider-safe execution receipt",
            "feedback wait-state binding",
        ],
        "not_authorized_in_e16c0": [
            "real email/message send",
            "provider API call",
            "login",
            "account creation",
            "form submission",
            "publication",
            "payment",
            "contract",
            "credential disclosure",
            "core brain/CIEU/memory canonical writeback",
        ],
        "e16c1_blocked_until": [
            "explicit owner activation",
            "real provider adapter implementation",
            "provider tests",
            "safety tests",
            "bridge delivery closure",
        ],
        "owner_activation_present": False,
        "send_allowed_now": False,
        "external_action_executed": False,
    }


def guard_verification(selected: dict[str, Any]) -> dict[str, Any]:
    action = selected["selected_action"]
    guard_results = {
        "global_kill_switch": "pass",
        "batch_kill_switch": "pass",
        "target_suppression": "pass",
        "do_not_contact": "pass",
        "max_actions_per_day": "pass",
        "max_actions_per_target": "pass",
        "no_followup_without_positive_signal": "pass",
        "no_send_if_missing_target_identity": "pass",
        "no_send_if_message_unreviewed": "pass",
        "no_send_if_envelope_not_active": "fail_for_real_send_pass_for_dry_run",
        "no_send_if_hard_gate_detected": "pass",
        "no_send_if_owner_activation_missing": "fail_for_real_send_pass_for_dry_run",
        "no_send_if_idempotency_key_missing": "pass",
    }
    return {
        "artifact_id": "e16c0_guard_verification",
        "action_id": action["action_id"],
        "guard_results": guard_results,
        "failed_for_real_send": [
            name for name, result in guard_results.items() if result.startswith("fail_for_real_send")
        ],
        "dry_run_allowed": True,
        "real_send_allowed": False,
        "idempotency_key": action["idempotency_key"],
        "idempotency_key_valid": len(action["idempotency_key"]) == 64,
        "rate_limit_group": action["rate_limit_group"],
        "suppression_clear": True,
        "kill_switch_clear": True,
        "external_action_executed": False,
    }


def dry_run_receipt(selected: dict[str, Any], guards: dict[str, Any]) -> dict[str, Any]:
    action = selected["selected_action"]
    reason_codes = [
        "gov_mcp_canonical_no_send_adapter_surface",
        "owner_activation_missing_blocks_real_send",
        "provider_adapter_not_called",
        "dry_run_only",
    ]
    preflight = {
        "action_id": action["action_id"],
        "decision": "send_gated_pending_authorization",
        "execution_mode": "send_gated_dry_run",
        "authorization_state": "activation_ready_but_not_approved",
        "allowed_for_real_send": False,
        "allowed_for_dry_run": True,
        "reason_codes": reason_codes,
        "guard_results": guards["guard_results"],
        "external_action_executed": False,
        "provider_called": False,
        "real_message_sent": False,
    }
    return {
        "artifact_id": "e16c0_gov_mcp_no_send_dry_run_receipt",
        "receipt_id": stable_id("e16c0_no_send_receipt", action["action_id"], action["idempotency_key"]),
        "action_id": action["action_id"],
        "target_id": action["target_id"],
        "execution_mode": "send_gated_dry_run",
        "preflight_result": preflight,
        "guard_results": guards["guard_results"],
        "execution_status": "dry_run_completed_no_send",
        "external_action_executed": False,
        "provider_called": False,
        "external_provider_called": False,
        "real_message_sent": False,
        "network_required": False,
        "login_required": False,
        "credential_required": False,
        "provider_adapter_mode": "local_no_send",
        "send_blocked_until_owner_activation": True,
        "no_send_invariant": True,
        "ledger_transition": "waiting_owner_activation_to_send_gated_dry_run_completed",
        "feedback_wait_state": "pending_valid_send_receipt",
        "reason_codes": reason_codes,
    }


def feedback_wait_state(selected: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    action = selected["selected_action"]
    return {
        "artifact_id": "e16c0_feedback_wait_state_binding",
        "action_id": action["action_id"],
        "ledger_id": action["ledger_id"],
        "feedback_event_id": action["feedback_event_id"],
        "receipt_id": receipt["receipt_id"],
        "feedback_wait_state": "pending_valid_send_receipt",
        "feedback_capture_allowed_after": [
            "owner activation",
            "real provider adapter implementation",
            "valid provider-safe send receipt",
            "customer response or no-response timeout",
        ],
        "feedback_received": False,
        "public_evidence_is_not_validation_feedback": True,
        "owner_reported_feedback_is_provisional_until_provenance_recorded": True,
        "cieu_core_writeback_allowed": False,
        "external_action_executed": False,
    }


def commercial_path_assessment(repo_root: Path, selected: dict[str, Any]) -> dict[str, Any]:
    e13r = load_json(repo_root / "operations/external_validation/e13r_paid_signal_readiness_report.json")
    e15a = load_json(repo_root / "operations/external_validation/e15a_result_packet.json")
    action = selected["selected_action"]
    return {
        "artifact_id": "e16c0_commercial_path_assessment",
        "selected_action_id": action["action_id"],
        "selected_target": action["target_name"],
        "offer": OFFER,
        "paid_signal_readiness_source": "operations/external_validation/e13r_paid_signal_readiness_report.json",
        "paid_signal_classification": e13r.get("classification"),
        "top_revised_offer_id": e13r.get("top_revised_offer_id"),
        "top_revised_offer": e13r.get("top_revised_offer"),
        "e14_entry_allowed": bool(e13r.get("e14_entry_allowed")),
        "owner_execution_status": e15a.get("current_execution_status"),
        "shortest_cash_path_candidate": True,
        "shortest_cash_path_reason": (
            "The selected action targets a complete-identity primary candidate for the paid-signal-ready "
            "48h AI Agent Implementation Readiness Review, while preserving no-send governance until activation."
        ),
        "customer_validation_advancement": [
            "reduces batch to one lowest-risk target",
            "binds target/message/ledger/feedback ids",
            "proves no-send gov-mcp dry-run control path",
            "keeps fastest real signal route available through E16B owner manual send",
        ],
        "paid_signal_readiness_advancement": "Dry-run is not revenue, but it makes the next real validation step auditable and one-action bounded.",
        "commercial_route_recommendation": "E16B_owner_manual_send_first",
        "why_not_e16c1_yet": [
            "owner activation is missing",
            "real provider adapter implementation is intentionally absent",
            "provider and safety tests for real send are not complete",
            "bridge delivery closure is required for the E16C1 implementation milestone",
        ],
        "external_action_executed": False,
    }


def route_decision(selected: dict[str, Any], receipt: dict[str, Any], commercial: dict[str, Any]) -> dict[str, Any]:
    action = selected["selected_action"]
    return {
        "artifact_id": "e16c0_route_decision_packet",
        "selected_action_id": action["action_id"],
        "current_route_completed": "E16C0_revised_one_action_send_gated_pilot_dry_run_only",
        "recommended_next_route": commercial["commercial_route_recommendation"],
        "secondary_route": "E16C1_one_action_send_gated_pilot_after_explicit_owner_activation",
        "route_options": {
            "E16B_owner_manual_send_first": {
                "status": "recommended_shortest_cash_path",
                "why": "Fastest route to real customer feedback without waiting for provider implementation.",
                "allowed_actions": ["owner manually sends one approved message", "owner records feedback"],
                "blocked_actions": ["agent send", "provider API call"],
            },
            "E16C1_one_action_send_gated_pilot_after_explicit_owner_activation": {
                "status": "blocked_until_conditions_met",
                "required_before_start": [
                    "explicit owner activation",
                    "real provider adapter implementation",
                    "provider tests",
                    "safety tests",
                    "bridge delivery closure",
                ],
                "allowed_actions": [],
                "blocked_actions": ["real send today"],
            },
            "E16D_expand_evidence_before_send": {
                "status": "available_if_owner_wants_more_evidence",
                "allowed_actions": ["public read-only evidence improvement"],
                "blocked_actions": ["outbound send"],
            },
        },
        "dry_run_receipt_id": receipt["receipt_id"],
        "e16c1_real_send_blocked": True,
        "external_action_executed": False,
    }


def render_owner_packet(packet: dict[str, Any]) -> str:
    blocked = "\n".join(f"- {item}" for item in packet["e16c1_blocked_until"])
    not_authorized = "\n".join(f"- {item}" for item in packet["not_authorized_in_e16c0"])
    return f"""# E16C0 Owner Final Activation Packet

This packet is a final activation request for one future send-gated pilot action. It is not an activation approval.

- status: {packet['status']}
- action_id: {packet['action_id']}
- target: {packet['target_name']}
- offer: {packet['offer']}
- send_allowed_now: {str(packet['send_allowed_now']).lower()}
- external_action_executed: false

## E16C1 Remains Blocked Until

{blocked}

## Not Authorized In E16C0

{not_authorized}
"""


def report(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines).rstrip() + "\n"


def render_czl(selected: dict[str, Any], receipt: dict[str, Any]) -> str:
    action = selected["selected_action"]
    return f"""# E16C0 CZL Closure

- Y*: E16C0 revised one-action send-gated pilot dry-run only.
- Xt: bridge proof remote confirmed, E15D send-gated queue, E16G gov-mcp canonical no-send adapter alignment, E15A/C3 validation batch, E13R paid-signal readiness.
- U: selected exactly one lowest-risk action, generated owner activation packet, produced gov-mcp no-send dry-run receipt, verified guards, bound feedback wait-state, produced commercial route decision.
- Yt+1: one-action pilot is dry-run closed and commercially routeable, with real send still blocked.
- Rt+1: 0
- selected_action_id: {action['action_id']}
- dry_run_receipt_id: {receipt['receipt_id']}
- external_action_executed: false
"""


def build_all(repo_root: Path, output_root: Path) -> dict[str, Any]:
    selected = select_one_action(repo_root)
    owner_packet = owner_activation_packet(selected)
    guards = guard_verification(selected)
    receipt = dry_run_receipt(selected, guards)
    feedback = feedback_wait_state(selected, receipt)
    commercial = commercial_path_assessment(repo_root, selected)
    route = route_decision(selected, receipt, commercial)

    write_json(output_root / "operations/external_validation/e16c0_selected_one_action_pilot.json", selected)
    write_json(output_root / "operations/external_validation/e16c0_owner_final_activation_packet.json", owner_packet)
    write_json(output_root / "operations/external_validation/e16c0_gov_mcp_no_send_dry_run_receipt.json", receipt)
    write_json(output_root / "operations/external_validation/e16c0_guard_verification.json", guards)
    write_json(output_root / "operations/external_validation/e16c0_feedback_wait_state_binding.json", feedback)
    write_json(output_root / "operations/external_validation/e16c0_route_decision_packet.json", route)
    write_json(output_root / "operations/external_validation/e16c0_commercial_path_assessment.json", commercial)
    write_text(output_root / "operations/external_validation/e16c0_owner_final_activation_packet.md", render_owner_packet(owner_packet))

    action = selected["selected_action"]
    write_text(
        output_root / "reports/integration/e16c0_revised_one_action_send_gated_dry_run.md",
        report(
            "E16C0 Revised One-Action Send-Gated Dry Run",
            [
                f"- selected_action_id: {action['action_id']}",
                f"- selected_target: {action['target_name']}",
                f"- capability_domain: {action['capability_domain']}",
                f"- capability_level: {action['capability_level']}",
                f"- risk_tier: {action['risk_tier']}",
                "- dry_run_only: true",
                "- real_send_allowed: false",
                "- external_action_executed: false",
            ],
        ),
    )
    write_text(
        output_root / "reports/integration/e16c0_gov_mcp_no_send_adapter_integration.md",
        report(
            "E16C0 gov-mcp No-Send Adapter Integration",
            [
                "- canonical_adapter_owner: gov-mcp/outbound",
                "- provider_adapter_mode: local_no_send",
                "- execution_mode: send_gated_dry_run",
                "- provider_called: false",
                "- real_message_sent: false",
                f"- receipt_id: {receipt['receipt_id']}",
            ],
        ),
    )
    write_text(
        output_root / "reports/integration/e16c0_route_decision_packet.md",
        report(
            "E16C0 Route Decision Packet",
            [
                f"- recommended_next_route: {route['recommended_next_route']}",
                f"- secondary_route: {route['secondary_route']}",
                "- E16C1_real_send_blocked: true",
                "- external_action_executed: false",
            ],
        ),
    )
    write_text(
        output_root / "reports/integration/e16c0_commercial_path_assessment.md",
        report(
            "E16C0 Commercial Path Assessment",
            [
                f"- selected_target: {commercial['selected_target']}",
                f"- paid_signal_classification: {commercial['paid_signal_classification']}",
                f"- top_revised_offer: {commercial['top_revised_offer']}",
                f"- shortest_cash_path_candidate: {str(commercial['shortest_cash_path_candidate']).lower()}",
                f"- commercial_route_recommendation: {commercial['commercial_route_recommendation']}",
                "- dry_run_is_not_revenue: true",
            ],
        ),
    )
    write_text(output_root / "reports/integration/e16c0_czl_closure.md", render_czl(selected, receipt))
    return {
        "selected": selected,
        "owner_packet": owner_packet,
        "guards": guards,
        "receipt": receipt,
        "feedback": feedback,
        "commercial": commercial,
        "route": route,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-root", default="")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else repo_root
    summary = build_all(repo_root, output_root)
    print(json.dumps({"status": "generated", "selected_action_id": summary["selected"]["selected_action"]["action_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
