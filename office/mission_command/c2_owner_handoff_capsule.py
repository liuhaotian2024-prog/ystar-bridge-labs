from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class C2OwnerHandoffCapsule:
    capsule_id: str
    recommended_execution_order: List[str]
    owner_minimal_operations: List[str]
    action_capsules: List[Dict[str, Any]]
    action_ledger_backfill: str
    feedback_recording: str
    next_step_triggers: Dict[str, str]
    long_term_direction: str
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c2_owner_handoff_capsule(queue: Mapping[str, Any]) -> C2OwnerHandoffCapsule:
    candidates = [item for item in queue.get("candidates", []) if item.get("priority") == "primary"]
    action_capsules: List[Dict[str, Any]] = []
    for item in candidates:
        decision = item.get("ygov_decision", {})
        action_capsules.append(
            {
                "action_id": item["action_id"],
                "decision_id": decision.get("decision_id"),
                "ledger_id": f"ledger_{item['action_id']}",
                "feedback_event_id": f"feedback_{item['action_id']}",
                "target_id": item["target_id"],
                "target_human_explanation": f"{item['target_profile'].get('name')} appears relevant to AI-agent implementation readiness; no contact is approved by C2 itself.",
                "send_purpose": "Ask whether the 48h AI Agent Implementation Readiness Review is useful enough to justify a paid diagnostic or pilot-prep conversation.",
                "message_draft": item["action_copy_or_message_capsule"]["message_text"],
                "gov_mcp_execution_mode": item["gov_mcp_execution_mode"],
                "owner_boundary_status": item["owner_boundary_status"],
            }
        )
    return C2OwnerHandoffCapsule(
        capsule_id="c2_owner_handoff_execution_capsule",
        recommended_execution_order=[item["action_id"] for item in candidates],
        owner_minimal_operations=[
            "Review and activate or reject the constitutional envelope.",
            "If owner chooses manual execution, send only the bound message capsule for each approved action.",
            "Record one action ledger row after any actual send.",
            "Record one feedback event for any reply, opt-out, negative response, or eligible no-response window.",
        ],
        action_capsules=action_capsules,
        action_ledger_backfill="Use action_id + decision_id + draft_hash from this capsule; no ledger row means no_response cannot be counted.",
        feedback_recording="Use c2_feedback_ingestion_template.json; public evidence is not validation feedback.",
        next_step_triggers={
            "positive_interest": "record feedback and evaluate paid_signal_candidate or E15 entry readiness",
            "price_question": "record paid_signal_candidate and request governed next-step decision",
            "negative_not_relevant": "suppress target and consider offer/segment revision",
            "unsubscribe_or_do_not_contact": "suppress target immediately and stop",
            "no_response": "only valid after a real action ledger and waiting window",
        },
        long_term_direction="Owner is not the operating executor; this capsule is a temporary handoff while gov-mcp live adapters remain unactivated.",
        external_action_executed=False,
    )


def render_c2_owner_handoff_capsule(capsule: Mapping[str, Any] | C2OwnerHandoffCapsule) -> str:
    data = capsule.to_dict() if isinstance(capsule, C2OwnerHandoffCapsule) else dict(capsule)
    lines = [
        "# C2 Owner-Handoff Execution Capsule",
        "",
        "## 人话摘要",
        "",
        "C2 没有发送任何消息。这个 capsule 只是把未来第一轮低风险动作绑定到 action_id / decision_id / ledger_id / feedback_event_id，方便 owner 或未来 gov-mcp adapter 在授权后执行并回填。",
        "",
        "## Recommended Order",
    ]
    for action_id in data.get("recommended_execution_order", []):
        lines.append(f"- {action_id}")
    lines.extend(["", "## Minimal Owner Operations"])
    for item in data.get("owner_minimal_operations", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Action Capsules"])
    for item in data.get("action_capsules", []):
        lines.extend(
            [
                f"### {item['action_id']}",
                f"- decision_id: {item['decision_id']}",
                f"- ledger_id: {item['ledger_id']}",
                f"- feedback_event_id: {item['feedback_event_id']}",
                f"- target_id: {item['target_id']}",
                f"- purpose: {item['send_purpose']}",
                f"- execution_mode: {item['gov_mcp_execution_mode']}",
                "",
                "```text",
                item["message_draft"].rstrip(),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Feedback Recording",
            data.get("feedback_recording", ""),
            "",
            "## What C2 Does Not Authorize",
            "- customer contact by Aiden/Codex",
            "- email/message sending",
            "- publication",
            "- payment",
            "- account creation",
            "- form submission",
            "- login",
            "- core brain/CIEU/memory writeback",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def validate_c2_owner_handoff_capsule(capsule: Mapping[str, Any] | C2OwnerHandoffCapsule) -> List[str]:
    data = capsule.to_dict() if isinstance(capsule, C2OwnerHandoffCapsule) else dict(capsule)
    errors: List[str] = []
    if data.get("external_action_executed") is not False:
        errors.append("capsule_must_not_execute_external_action")
    if len(data.get("action_capsules", [])) < 3:
        errors.append("capsule_requires_three_primary_actions")
    for item in data.get("action_capsules", []):
        for key in ["action_id", "decision_id", "ledger_id", "feedback_event_id", "message_draft"]:
            if not item.get(key):
                errors.append(f"{item.get('action_id', 'unknown')}:missing_{key}")
    if "not the operating executor" not in data.get("long_term_direction", ""):
        errors.append("capsule_must_state_owner_not_operator")
    return list(dict.fromkeys(errors))
