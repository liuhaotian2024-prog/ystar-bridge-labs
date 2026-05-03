from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping


E15A_CONSOLE_ID = "e15a_owner_execution_console"


def load_c3_owner_handoff_batch(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / "operations" / "external_validation" / "c3_owner_handoff_validation_batch.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_c3_validation_batch(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / "operations" / "external_validation" / "c3_validation_batch.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _batch_action_by_id(c3_batch: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(action.get("action_id")): dict(action) for action in c3_batch.get("actions", [])}


def build_e15a_owner_execution_console(repo_root: Path) -> Dict[str, Any]:
    handoff = load_c3_owner_handoff_batch(repo_root)
    c3_batch = load_c3_validation_batch(repo_root)
    batch_by_id = _batch_action_by_id(c3_batch)
    actions: List[Dict[str, Any]] = []
    for item in handoff.get("handoff_items", []):
        action = batch_by_id.get(str(item.get("action_id")), {})
        role = str(action.get("role", "unknown"))
        actions.append(
            {
                "action_id": item["action_id"],
                "decision_id": action.get("ygov_decision_id", ""),
                "ledger_id": item["ledger_id_to_mark_as_sent"],
                "feedback_event_id": item["feedback_event_id_to_use_after_reply"],
                "target_id": item["target_id"],
                "target_name": item["target"],
                "role": role,
                "one_line_target_explanation": item["context_summary"],
                "why_now": "C3 selected this target for the first owner-handoff validation batch; E15A only makes the owner send/record loop easy to execute.",
                "message_to_send": item["copy_paste_block"],
                "channel_suggestion": item["channel_suggestion"],
                "do_not_send_warning": item["do_not_send_warning"],
                "owner_minimal_fill_after_action": {
                    "send_status": "sent_confirmed_by_owner|skipped_by_owner|blocked_by_missing_target_info|replaced_by_fallback|suppressed_by_owner",
                    "sent_at": "OWNER_TO_FILL_IF_SENT",
                    "channel_used": "OWNER_TO_FILL_IF_SENT",
                    "not_sent_reason": "OWNER_TO_FILL_IF_NOT_SENT",
                    "feedback_event_id_to_use_after_reply": item["feedback_event_id_to_use_after_reply"],
                },
                "external_action_executed_by_agent": False,
            }
        )
    primary_actions = [action for action in actions if action["role"] == "primary"]
    fallback_actions = [action for action in actions if action["role"] == "fallback"]
    return {
        "console_id": E15A_CONSOLE_ID,
        "source_c3_batch_id": c3_batch.get("batch_id"),
        "source_c3_owner_handoff_batch_id": handoff.get("batch_id"),
        "recommended_action": "E15A_send_now_owner_operated",
        "human_summary": "Owner can manually send the three primary copy/paste messages, then fill one ledger row per sent/skipped target. Aiden/Codex does not send.",
        "primary_action_count": len(primary_actions),
        "fallback_action_count": len(fallback_actions),
        "primary_actions": primary_actions,
        "fallback_actions": fallback_actions,
        "not_approved": [
            "Aiden autonomous send",
            "agent email/message sending",
            "publication",
            "payment",
            "account creation",
            "form submission",
            "login",
            "external validation submission by agent",
            "customer system access",
            "legal or financial commitment",
            "credential disclosure",
            "core brain/CIEU/memory writeback",
        ],
        "owner_if_not_sending": "Set send_status to skipped_by_owner, blocked_by_missing_target_info, replaced_by_fallback, or suppressed_by_owner with not_sent_reason.",
        "external_action_executed_by_agent": False,
    }


def validate_e15a_owner_execution_console(console: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if console.get("primary_action_count") != 3:
        errors.append("console_must_include_three_primary_actions")
    if console.get("fallback_action_count") != 2:
        errors.append("console_must_include_two_fallback_actions")
    if console.get("external_action_executed_by_agent") is not False:
        errors.append("console_must_not_execute_agent_external_action")
    for action in list(console.get("primary_actions", [])) + list(console.get("fallback_actions", [])):
        for key in ["action_id", "decision_id", "ledger_id", "feedback_event_id", "message_to_send"]:
            if not action.get(key):
                errors.append(f"{action.get('action_id', 'unknown')}:missing_{key}")
        if action.get("external_action_executed_by_agent") is not False:
            errors.append(f"{action.get('action_id')}:agent_external_action_executed")
    not_approved = set(console.get("not_approved", []))
    for item in ["Aiden autonomous send", "payment", "login", "core brain/CIEU/memory writeback"]:
        if item not in not_approved:
            errors.append(f"missing_not_approved_{item}")
    return list(dict.fromkeys(errors))


def render_e15a_owner_execution_console(console: Mapping[str, Any]) -> str:
    lines = [
        "# E15A Owner Execution Console",
        "",
        "## 人话摘要",
        "",
        str(console["human_summary"]),
        "",
        "## Owner 最小动作",
        "",
        "1. 只看下面 3 个 primary actions。",
        "2. 如果决定执行，把对应 copy/paste block 手动发送。",
        "3. 发送后只回填 action_id / ledger_id / sent_at / channel_used。",
        "4. 收到回复后使用 feedback_event_id 填 E15A feedback form。",
        "5. 如果暂时不发，填 not_sent_reason，不要伪造 sent。",
        "",
        "## Primary Actions",
    ]
    for action in console.get("primary_actions", []):
        lines.extend(
            [
                "",
                f"### {action['target_name']}",
                f"- action_id: `{action['action_id']}`",
                f"- decision_id: `{action['decision_id']}`",
                f"- ledger_id: `{action['ledger_id']}`",
                f"- feedback_event_id: `{action['feedback_event_id']}`",
                f"- 为什么现在发: {action['why_now']}",
                f"- channel: {action['channel_suggestion']}",
                "",
                "```text",
                action["message_to_send"].rstrip(),
                "```",
            ]
        )
    lines.extend(["", "## Fallback Actions"])
    for action in console.get("fallback_actions", []):
        lines.extend(
            [
                f"- {action['target_name']}: use only if a primary is skipped/replaced. action_id `{action['action_id']}`",
            ]
        )
    lines.extend(["", "## 不被批准的事"])
    lines.extend(f"- {item}" for item in console.get("not_approved", []))
    return "\n".join(lines).rstrip() + "\n"
