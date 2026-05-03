from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping


C3_BATCH_ID = "c3_first_governed_validation_batch"
C3_OFFER = "48h AI Agent Implementation Readiness Review"


@dataclass(frozen=True)
class C3BatchAction:
    batch_id: str
    action_id: str
    role: str
    target_id: str
    target_name: str
    missing_fields: List[str]
    target_evidence_basis: List[str]
    offer_thesis: str
    buyer_pain_hypothesis: str
    selection_reason: str
    exclusion_or_suppression_reason: str
    capability_domain: str
    risk_tier: str
    owner_boundary_status: str
    ygov_decision_id: str
    gov_mcp_execution_mode: str
    message_capsule_id: str
    ledger_id: str
    feedback_event_id: str
    next_action_route: str
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_c2_queue(repo_root: Path) -> Dict[str, Any]:
    return _load_json(repo_root / "operations" / "external_validation" / "c2_governed_action_queue.json")


def _batch_action(candidate: Mapping[str, Any], role: str, index: int, reason: str = "") -> C3BatchAction:
    target_profile = dict(candidate.get("target_profile", {}))
    decision = dict(candidate.get("ygov_decision", {}))
    capsule = dict(candidate.get("action_copy_or_message_capsule", {}))
    target_id = str(candidate.get("target_id", f"placeholder_target_{index:03d}"))
    return C3BatchAction(
        batch_id=C3_BATCH_ID,
        action_id=str(candidate.get("action_id", f"c3_placeholder_action_{index:03d}")),
        role=role,
        target_id=target_id,
        target_name=str(target_profile.get("name") or f"DETERMINISTIC_PLACEHOLDER_{target_id}"),
        missing_fields=list(target_profile.get("missing_fields") or []),
        target_evidence_basis=list(decision.get("evidence_basis") or []),
        offer_thesis=C3_OFFER,
        buyer_pain_hypothesis=str(candidate.get("buyer_pain_hypothesis", "AI-agent implementation readiness and governance risk.")),
        selection_reason=str(candidate.get("reason_for_selection", "C2 queue candidate selected for governed validation batch.")),
        exclusion_or_suppression_reason=reason,
        capability_domain=str(candidate.get("action_domain", "external_validation_message")),
        risk_tier=str(candidate.get("risk_tier", "Tier 5 governed low-volume external validation")),
        owner_boundary_status=str(candidate.get("owner_boundary_status", "pending_owner_activation")),
        ygov_decision_id=str(decision.get("decision_id", "missing_decision_id")),
        gov_mcp_execution_mode=str(candidate.get("gov_mcp_execution_mode", "owner_handoff")),
        message_capsule_id=str(capsule.get("capsule_id", f"missing_capsule_{index:03d}")),
        ledger_id=f"ledger_{candidate.get('action_id', f'c3_placeholder_action_{index:03d}')}",
        feedback_event_id=f"feedback_{candidate.get('action_id', f'c3_placeholder_action_{index:03d}')}",
        next_action_route="owner_handoff_ready" if role in {"primary", "fallback"} else role,
        external_action_executed=False,
    )


def build_c3_validation_batch(repo_root: Path) -> Dict[str, Any]:
    queue = load_c2_queue(repo_root)
    candidates = list(queue.get("candidates", []))
    primary = [item for item in candidates if item.get("priority") == "primary"][:3]
    fallback = [item for item in candidates if item.get("priority") == "fallback"][:3]
    while len(primary) < 3:
        idx = len(primary) + 1
        primary.append({"action_id": f"c3_missing_primary_{idx}", "target_id": f"missing_primary_{idx}", "target_profile": {"missing_fields": ["target_profile"]}})
    while len(fallback) < 3:
        idx = len(fallback) + 1
        fallback.append({"action_id": f"c3_missing_fallback_{idx}", "target_id": f"missing_fallback_{idx}", "target_profile": {"missing_fields": ["target_profile"]}})
    actions: List[C3BatchAction] = []
    for idx, candidate in enumerate(primary, start=1):
        actions.append(_batch_action(candidate, "primary", idx))
    for idx, candidate in enumerate(fallback[:2], start=4):
        actions.append(_batch_action(candidate, "fallback", idx))
    actions.append(_batch_action(fallback[2], "suppression_candidate", 6, "Reserve/suppress unless primary/fallback fails or owner explicitly expands batch."))
    actions.append(
        C3BatchAction(
            batch_id=C3_BATCH_ID,
            action_id="c3_excluded_agent_direct_execution_without_activation",
            role="excluded",
            target_id="not_applicable_agent_direct_execution",
            target_name="Excluded direct agent execution path",
            missing_fields=["real_target_not_applicable"],
            target_evidence_basis=[],
            offer_thesis=C3_OFFER,
            buyer_pain_hypothesis="not_applicable",
            selection_reason="Explicitly excluded to prove C3 does not permit direct agent sending without owner activation.",
            exclusion_or_suppression_reason="No owner approval evidence; direct agent email/message sending is outside C3 envelope.",
            capability_domain="external_validation_message",
            risk_tier="Tier 5 governed low-volume external validation",
            owner_boundary_status="excluded_no_owner_activation",
            ygov_decision_id="excluded_no_decision_replay_required",
            gov_mcp_execution_mode="deny",
            message_capsule_id="none",
            ledger_id="none",
            feedback_event_id="none",
            next_action_route="blocked_agent_direct_execution",
            external_action_executed=False,
        )
    )
    return {
        "batch_id": C3_BATCH_ID,
        "source_queue_id": queue.get("queue_id", "c2_governed_first_action_queue"),
        "offer_thesis": C3_OFFER,
        "primary_count": 3,
        "fallback_count": 2,
        "suppression_candidate_count": 1,
        "excluded_count": 1,
        "external_action_executed": False,
        "actions": [action.to_dict() for action in actions],
    }


def validate_c3_validation_batch(batch: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    actions = list(batch.get("actions", []))
    counts = {role: sum(1 for action in actions if action.get("role") == role) for role in ["primary", "fallback", "suppression_candidate", "excluded"]}
    if counts["primary"] != 3:
        errors.append("requires_three_primary_actions")
    if counts["fallback"] != 2:
        errors.append("requires_two_fallback_actions")
    if counts["suppression_candidate"] != 1:
        errors.append("requires_one_suppression_candidate")
    if counts["excluded"] != 1:
        errors.append("requires_one_excluded_candidate")
    if batch.get("external_action_executed") is not False:
        errors.append("batch_must_not_execute_external_action")
    for action in actions:
        for key in ["action_id", "target_id", "offer_thesis", "capability_domain", "risk_tier", "ygov_decision_id", "gov_mcp_execution_mode", "ledger_id", "feedback_event_id", "next_action_route"]:
            if not action.get(key):
                errors.append(f"{action.get('action_id', 'unknown')}:missing_{key}")
        if action.get("offer_thesis") != C3_OFFER:
            errors.append(f"{action.get('action_id')}:wrong_offer")
        if action.get("external_action_executed") is not False:
            errors.append(f"{action.get('action_id')}:external_action_executed")
    return list(dict.fromkeys(errors))
