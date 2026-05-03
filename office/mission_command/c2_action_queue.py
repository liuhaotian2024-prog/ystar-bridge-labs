from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping

from office.mission_command.c2_gov_mcp_execution_control import build_c2_gov_mcp_execution_control
from office.mission_command.c2_ygov_action_decision import evaluate_c2_ygov_action
from office.mission_command.e14_manual_validation_draft import build_e14_manual_validation_draft


C2_OFFER_THESIS = "48h AI Agent Implementation Readiness Review"


@dataclass(frozen=True)
class C2GovernedActionCandidate:
    action_id: str
    queue_position: int
    priority: str
    offer_thesis: str
    target_id: str
    target_profile: Dict[str, Any]
    buyer_pain_hypothesis: str
    reason_for_selection: str
    action_domain: str
    risk_tier: str
    owner_boundary_status: str
    ygov_decision: Dict[str, Any]
    gov_mcp_execution_mode: str
    action_copy_or_message_capsule: Dict[str, Any]
    ledger_placeholder: Dict[str, Any]
    feedback_wait_condition: str
    next_if_no_response: str
    next_if_positive_response: str
    next_if_negative_response: str
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_e14_selected_targets(repo_root: Path) -> List[Dict[str, Any]]:
    batch = _load_json(repo_root / "operations" / "external_validation" / "e14_target_batch.proposed.json")
    candidates = _load_json(repo_root / "operations" / "external_validation" / "e14_target_candidates.json").get("candidates", [])
    by_id = {candidate.get("target_id"): candidate for candidate in candidates}
    selected_ids = batch.get("selected_target_ids", [])
    selected: List[Dict[str, Any]] = []
    for target_id in selected_ids:
        candidate = dict(by_id.get(target_id, {}))
        if not candidate:
            candidate = {
                "target_id": target_id,
                "organization_or_person_name": "MISSING_TARGET_PROFILE",
                "segment": "missing_segment",
                "evidence_refs": [],
                "missing_fields": ["organization_or_person_name", "segment", "evidence_refs"],
            }
        selected.append(candidate)
    return selected


def _target_class_for(candidate: Mapping[str, Any]) -> str:
    segment = str(candidate.get("segment", "")).lower()
    if "consult" in segment or "agenc" in segment:
        return "ai_consultant_agency"
    return "ai_heavy_team_with_agent_workflow_bottleneck"


def _message_capsule(candidate: Mapping[str, Any], index: int) -> Dict[str, Any]:
    draft = build_e14_manual_validation_draft()
    target_name = str(candidate.get("organization_or_person_name", candidate.get("target_id", "target")))
    body = draft.draft_text.replace("Hi,\n", f"Hi {target_name},\n", 1)
    message_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()[:24]
    return {
        "capsule_id": f"c2_message_capsule_{index:03d}",
        "draft_family": "ai_transparent_validation",
        "draft_hash": message_hash,
        "message_text": body,
        "ai_transparency_required": True,
        "opt_out_required": True,
        "no_attachment": True,
        "no_tracking_link": True,
        "send_now": False,
    }


def _build_action_packet(candidate: Mapping[str, Any], index: int, *, priority: str) -> Dict[str, Any]:
    target_id = str(candidate.get("target_id", f"missing_target_{index:03d}"))
    action_id = f"c2_action_{priority}_{index:03d}_{target_id}"
    return {
        "action_id": action_id,
        "intent_id": action_id,
        "y_star": "first_governed_action_activation_loop_without_unapproved_external_side_effects",
        "x_t": "AB3/C1 contracts exist; owner constitutional activation is pending; no live external action executed.",
        "proposed_u": "Prepare one AI-transparent validation message for owner-handoff or future gov-mcp execution after activation.",
        "target_id": target_id,
        "target_class": _target_class_for(candidate),
        "channel": str(candidate.get("contact_channel_candidate", "owner_handoff_or_governed_messaging_adapter")),
        "risk_tier": "Tier 5 governed low-volume external validation",
        "capability_domain": "external_validation_message",
        "required_envelope": "c2_pending_constitutional_activation",
        "evidence_refs": list(candidate.get("evidence_refs") or []),
        "stop_conditions": ["opt_out", "negative_feedback", "complaint", "budget_exceeded", "target_class_mismatch"],
    }


def build_c2_action_queue(repo_root: Path, activation_packet: Mapping[str, Any]) -> Dict[str, Any]:
    selected_targets = load_e14_selected_targets(repo_root)
    if not selected_targets:
        selected_targets = [
            {"target_id": f"missing_e14_target_{idx}", "organization_or_person_name": "MISSING_TARGET_PROFILE", "segment": "missing", "evidence_refs": []}
            for idx in range(1, 4)
        ]
    primary_targets = selected_targets[:3]
    fallback_targets = (selected_targets[3:6] or selected_targets[:3])[:3]
    candidates: List[C2GovernedActionCandidate] = []
    for idx, candidate in enumerate(primary_targets + fallback_targets, start=1):
        priority = "primary" if idx <= len(primary_targets) else "fallback"
        action_packet = _build_action_packet(candidate, idx, priority=priority)
        decision = evaluate_c2_ygov_action(action_packet, activation_packet)
        control = build_c2_gov_mcp_execution_control(decision.to_dict())
        target_id = str(candidate.get("target_id", f"missing_target_{idx:03d}"))
        capsule = _message_capsule(candidate, idx)
        candidates.append(
            C2GovernedActionCandidate(
                action_id=action_packet["action_id"],
                queue_position=idx,
                priority=priority,
                offer_thesis=C2_OFFER_THESIS,
                target_id=target_id,
                target_profile={
                    "name": candidate.get("organization_or_person_name", "MISSING_TARGET_PROFILE"),
                    "segment": candidate.get("segment", "missing_segment"),
                    "public_url_or_ref": candidate.get("public_url_or_ref", ""),
                    "missing_fields": [key for key in ["organization_or_person_name", "segment", "evidence_refs"] if not candidate.get(key)],
                },
                buyer_pain_hypothesis="AI-agent implementation readiness, workflow bottlenecks, governance risk, and safe next operational step.",
                reason_for_selection=str(candidate.get("relevance_to_offer") or candidate.get("why_this_target") or "missing_target_rationale"),
                action_domain="external_validation_message",
                risk_tier=action_packet["risk_tier"],
                owner_boundary_status=str(activation_packet.get("activation_state", "pending_owner_activation")),
                ygov_decision=decision.to_dict(),
                gov_mcp_execution_mode=control.execution_mode,
                action_copy_or_message_capsule=capsule,
                ledger_placeholder={
                    "action_id": action_packet["action_id"],
                    "envelope_id": activation_packet.get("activation_id", "c2_pending_constitutional_activation"),
                    "y_gov_decision_id": decision.decision_id,
                    "gov_mcp_receipt_id": "PENDING_OWNER_ACTIVATION_OR_DRY_RUN",
                    "target_id": target_id,
                    "action_type": "external_validation_message",
                    "draft_hash": capsule["draft_hash"],
                    "executed": False,
                },
                feedback_wait_condition="Feedback event may be recorded only after valid owner/governed execution ledger exists.",
                next_if_no_response="wait_until_no_response_window_then_record_no_response_after_valid_action_only",
                next_if_positive_response="record_positive_feedback_event_and_evaluate_paid_signal_candidate",
                next_if_negative_response="record_negative_feedback_stop_suppress_target_and_evaluate_offer_revision_or_segment_mismatch",
            )
        )
    return {
        "queue_id": "c2_governed_first_action_queue",
        "offer_thesis": C2_OFFER_THESIS,
        "primary_candidate_count": len([item for item in candidates if item.priority == "primary"]),
        "fallback_candidate_count": len([item for item in candidates if item.priority == "fallback"]),
        "external_action_executed": False,
        "candidates": [item.to_dict() for item in candidates],
    }


def validate_c2_action_queue(queue: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    candidates = list(queue.get("candidates", []))
    if queue.get("primary_candidate_count", 0) < 3:
        errors.append("requires_three_primary_action_candidates")
    if queue.get("fallback_candidate_count", 0) < 3:
        errors.append("requires_three_fallback_action_candidates")
    if queue.get("external_action_executed") is not False:
        errors.append("c2_queue_must_not_execute_external_action")
    for item in candidates:
        for key in ["action_id", "target_id", "ygov_decision", "gov_mcp_execution_mode", "ledger_placeholder", "feedback_wait_condition"]:
            if not item.get(key):
                errors.append(f"{item.get('action_id', 'unknown')}:missing_{key}")
        if item.get("external_action_executed") is not False:
            errors.append(f"{item.get('action_id')}:external_action_must_be_false")
        if item.get("offer_thesis") != C2_OFFER_THESIS:
            errors.append(f"{item.get('action_id')}:wrong_offer_thesis")
    return list(dict.fromkeys(errors))
