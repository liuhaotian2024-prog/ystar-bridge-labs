from __future__ import annotations

from typing import Any, Dict, List, Mapping


def build_c3_owner_handoff_batch(batch: Mapping[str, Any]) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for action in batch.get("actions", []):
        if action.get("role") not in {"primary", "fallback"}:
            continue
        incomplete = bool(action.get("missing_fields"))
        target = action.get("target_name") or action.get("target_id")
        message = (
            f"Subject: Quick question on AI-agent implementation readiness\n\n"
            f"Hi {target},\n\n"
            "I am Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs, working with Haotian. "
            "I am not pretending to be a human teammate, and this is a small owner-operated validation note before we ask anyone to buy anything.\n\n"
            "We are testing a 48h AI Agent Implementation Readiness Review for teams or agencies trying to deploy AI agents/coding agents safely. "
            "The review maps implementation readiness, workflow bottlenecks, governance risks, and the safest next operational step.\n\n"
            "Would this kind of 48h readiness review be useful enough to justify a paid diagnostic or pilot-prep conversation?\n\n"
            "No pressure, no automated follow-up, and it is completely fine to ignore this. If this is not relevant, please disregard.\n"
        )
        items.append(
            {
                "action_id": action["action_id"],
                "target_id": action["target_id"],
                "target": target,
                "context_summary": f"{target} is queued for {action['offer_thesis']} validation.",
                "why_this_target": action["selection_reason"],
                "exact_message_draft": message,
                "channel_suggestion": "owner-selected public/general channel only; no scraped personal contact",
                "do_not_send_warning": "DO NOT SEND: target data incomplete" if incomplete else "Do not send until owner chooses to execute this handoff.",
                "copy_paste_block": message,
                "ledger_id_to_mark_as_sent": action["ledger_id"],
                "feedback_event_id_to_use_after_reply": action["feedback_event_id"],
                "what_owner_does_now": "If owner later chooses E15A, send this exact block manually and then record the ledger id shown above.",
                "external_action_executed": False,
            }
        )
    return {
        "batch_id": "c3_owner_handoff_validation_batch",
        "source_batch_id": batch.get("batch_id"),
        "owner_minimal_step": "Review one page; if choosing E15A later, manually send the three primary copy/paste blocks and record ledger rows.",
        "handoff_items": items,
        "external_action_executed": False,
    }


def render_c3_owner_handoff_batch(packet: Mapping[str, Any]) -> str:
    lines = [
        "# C3 Owner-Handoff Validation Batch",
        "",
        "## 人话摘要",
        "",
        "C3 没有发送任何消息。这个页面把第一轮 validation batch 压缩成 owner 后续可执行的一页：每个 action 都绑定 ledger_id 和 feedback_event_id。",
        "",
        f"- owner_minimal_step: {packet.get('owner_minimal_step')}",
        "",
    ]
    for item in packet.get("handoff_items", []):
        lines.extend(
            [
                f"## {item['action_id']}",
                f"- target: {item['target']}",
                f"- ledger_id: {item['ledger_id_to_mark_as_sent']}",
                f"- feedback_event_id: {item['feedback_event_id_to_use_after_reply']}",
                f"- warning: {item['do_not_send_warning']}",
                "",
                "```text",
                item["copy_paste_block"].rstrip(),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Not Authorized",
            "- Aiden/Codex sending",
            "- publication",
            "- payment",
            "- account creation",
            "- form submission",
            "- login",
            "- core brain/CIEU/memory writeback",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def validate_c3_owner_handoff_batch(packet: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if packet.get("external_action_executed") is not False:
        errors.append("handoff_batch_must_not_execute_external_action")
    if len(packet.get("handoff_items", [])) < 5:
        errors.append("handoff_batch_requires_primary_and_fallback_items")
    for item in packet.get("handoff_items", []):
        for key in ["action_id", "target", "exact_message_draft", "copy_paste_block", "ledger_id_to_mark_as_sent", "feedback_event_id_to_use_after_reply", "what_owner_does_now"]:
            if not item.get(key):
                errors.append(f"{item.get('action_id', 'unknown')}:missing_{key}")
        if item.get("external_action_executed") is not False:
            errors.append(f"{item.get('action_id')}:external_action_executed")
    return list(dict.fromkeys(errors))
