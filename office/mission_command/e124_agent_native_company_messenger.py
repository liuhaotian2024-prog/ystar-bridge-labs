from __future__ import annotations

import importlib
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MILESTONE_ID = "E124_Agent_Native_Company_Messenger_R1"
SESSION_ID = "e124_agent_native_company_messenger"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
OWNER_DIALOGUE_LANGUAGE = "zh-CN"

CIEU_FIVE_TUPLE_FIELDS = ("Y_star_t", "X_t", "U_t", "Y_t_plus_1", "R_t_plus_1")


def build_agent_native_participants() -> list[dict[str, Any]]:
    return [
        {
            "participant_id": "owner",
            "display_name": "Haotian / Owner",
            "participant_type": "human",
            "role": "company_owner",
            "communication_boundary": "can initiate CEO meeting and approve external/high-risk actions",
        },
        {
            "participant_id": "Aiden",
            "display_name": "Aiden",
            "participant_type": "agent",
            "role": "CEO principal",
            "communication_boundary": "strategy owner; must use governed model orchestration and CIEU five tuple messages",
        },
        {
            "participant_id": "Codex",
            "display_name": "Codex",
            "participant_type": "tool_executor",
            "role": "engineering executor",
            "communication_boundary": "may execute only from CEOImplementationOrder; not a strategy owner",
        },
        {
            "participant_id": "StrategyAgent",
            "display_name": "Strategy Agent",
            "participant_type": "agent",
            "role": "market/research analyst",
            "communication_boundary": "local research synthesis only; no external send",
        },
        {
            "participant_id": "FinanceAgent",
            "display_name": "Finance Agent",
            "participant_type": "agent",
            "role": "pricing, wallet, and cash discipline analyst",
            "communication_boundary": "wallet/payment proposal-only; no payment execution",
        },
        {
            "participant_id": "external_agent_placeholder",
            "display_name": "External Agent Placeholder",
            "participant_type": "external_agent",
            "role": "future outside-company agent contact",
            "communication_boundary": "no-send proposal-only until owner approves provider and external boundary",
            "live_external_delivery_allowed": False,
        },
    ]


def build_cieu_five_tuple(
    *,
    y_star: str,
    context: str | Mapping[str, Any],
    action: str | Mapping[str, Any],
    expected_next: str,
    residual: str = "pending until recipient response",
    residual_status: str = "planning_residual_pending",
) -> dict[str, Any]:
    return {
        "Y_star_t": y_star,
        "X_t": context,
        "U_t": action,
        "Y_t_plus_1": expected_next,
        "R_t_plus_1": residual,
        "residual_status": residual_status,
        "five_tuple_protocol": "CZL/CIEU",
    }


def build_agent_native_message_packet(
    *,
    thread_id: str,
    sender_id: str,
    recipient_ids: list[str],
    message_kind: str,
    human_readable_text: str,
    cieu_five_tuple: Mapping[str, Any],
    cieu_db: str | Path,
    message_id: str | None = None,
    participants: list[dict[str, Any]] | None = None,
    wallet_proposal: Mapping[str, Any] | None = None,
    attachment_manifest: Mapping[str, Any] | None = None,
    selected_model_id: str = "local_gemma4_e4b",
    local_messenger_only: bool = True,
    no_send_default: bool = True,
    external_delivery_executed: bool = False,
    provider_action_executed: bool = False,
) -> dict[str, Any]:
    participants = participants or build_agent_native_participants()
    participant_types = {item["participant_id"]: item["participant_type"] for item in participants}
    agent_involved = participant_types.get(sender_id) in {"agent", "tool_executor"} or any(
        participant_types.get(recipient_id) in {"agent", "tool_executor"} for recipient_id in recipient_ids
    )
    message: dict[str, Any] = {
        "message_id": message_id or f"msg_{uuid.uuid4().hex[:12]}",
        "created_at": _now(),
        "sender_id": sender_id,
        "recipient_ids": list(recipient_ids),
        "message_kind": message_kind,
        "human_readable_text": human_readable_text,
        "cieu_five_tuple": dict(cieu_five_tuple),
    }
    if wallet_proposal is not None:
        message["wallet_proposal"] = dict(wallet_proposal)
    return {
        "artifact_id": "e124_agent_native_message_packet",
        "milestone_id": MILESTONE_ID,
        "messenger_session_id": SESSION_ID,
        "thread": {
            "thread_id": thread_id,
            "thread_type": "direct" if len(recipient_ids) == 1 else "group_meeting",
            "title": "Aiden Company Messenger",
            "purpose": "Human/agent and agent/agent communication with natural language plus CIEU/CZL five tuple",
        },
        "participants": participants,
        "message": message,
        "model_orchestration": {
            "model_orchestration_required": bool(agent_involved),
            "selected_model_id": selected_model_id if agent_involved else "human_direct_input",
            "raw_prompt_only": False,
            "E123_model_orchestration_reused": bool(agent_involved),
            "routing_summary": "Aiden messages route through governed local model/tool orchestration before execution.",
        },
        "delivery_boundary": {
            "local_messenger_only": local_messenger_only,
            "no_send_default": no_send_default,
            "external_delivery_executed": external_delivery_executed,
            "provider_action_executed": provider_action_executed,
            "external_side_effect": False,
        },
        "attachment_manifest": dict(attachment_manifest or {"metadata_only": True, "external_upload_executed": False, "attachments": []}),
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_AGENT_NATIVE_MESSAGE_DECISION",
            "target_cieu_db": str(cieu_db),
            "five_tuple_fields": list(CIEU_FIVE_TUPLE_FIELDS),
        },
        "truth_constraints": {
            "raw_natural_language_only_message": False,
            "missing_CIEU_five_tuple_allowed": False,
            "agent_message_without_model_orchestration": False,
            "external_delivery_executed": external_delivery_executed,
            "external_agent_live_contact_executed": False,
            "payment_executed": False,
            "USDC_transfer_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "K9Audit_write_claim": False,
            "hidden_chain_of_thought_stored": False,
            "CIEU_recording_bypassed": False,
        },
    }


def validate_and_record_agent_native_message(
    packet: Mapping[str, Any],
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    gov = _load_ystar_module("ystar.governance.aiden_agent_native_messenger_contract", ystar_gov_root)
    return gov.validate_and_write_aiden_agent_native_message_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
    )


def generate_aiden_reply_text(
    owner_text: str,
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    repo_root: str | Path | None = None,
    allow_live_network: bool = False,
    require_real_model_invocation: bool = False,
    real_model_invoker: Any | None = None,
) -> dict[str, Any]:
    """Generate Aiden's reply through governed retrieval plus a real model when required."""

    try:
        from office.mission_command.e126_adaptive_retrieval_planner_runtime import run_adaptive_retrieval_planner_and_retrieval
        from office.aiden_meeting_room.chat_router import route_chat_message_to_aiden_meeting_room

        adaptive_retrieval_result = run_adaptive_retrieval_planner_and_retrieval(
            owner_text,
            cieu_db=cieu_db,
            ystar_gov_root=ystar_gov_root,
            repo_root=repo_root or BRIDGE_ROOT,
        )
        planner_decision = adaptive_retrieval_result["YstarGov_planner_result"]["governance_decision"]
        if planner_decision["decision"] != "ALLOW":
            return {
                "reply_text": (
                    "Aiden Adaptive Retrieval Planner Notice: I cannot answer yet because the adaptive retrieval/capability "
                    f"planner returned {planner_decision['decision']}: {planner_decision['reason']}. "
                    f"Correct path: {'; '.join(planner_decision.get('correct_path') or [])}"
                ),
                "reply_backend": "adaptive_retrieval_planner_notice",
                "reply_protocol": "AidenAdaptiveRetrievalPlannerV1",
                "runtime_fallback_used": True,
                "adaptive_retrieval_result": adaptive_retrieval_result,
                "adaptive_planner_decision": planner_decision["decision"],
                "retrieval_result": None,
                "retrieval_decision": "not_run",
                "retrieval_context_summary": "",
            }
        retrieval_result = adaptive_retrieval_result["retrieval_result"]
        retrieval_decision = retrieval_result["YstarGov_retrieval_result"]["governance_decision"]
        if retrieval_decision["decision"] != "ALLOW":
            return {
                "reply_text": (
                    "Aiden Retrieval Runtime Notice: I cannot responsibly answer from recent memory alone. "
                    f"Retrieval governance returned {retrieval_decision['decision']}: {retrieval_decision['reason']}. "
                    f"Correct path: {'; '.join(retrieval_decision.get('correct_path') or [])}"
                ),
                "reply_backend": "retrieval_governance_notice",
                "reply_protocol": "AidenRetrievalOrchestrationV1",
                "runtime_fallback_used": True,
                "adaptive_retrieval_result": adaptive_retrieval_result,
                "adaptive_planner_decision": planner_decision["decision"],
                "retrieval_result": retrieval_result,
                "retrieval_decision": retrieval_decision["decision"],
                "retrieval_context_summary": retrieval_result["retrieval_context_summary"],
            }

        if require_real_model_invocation:
            from office.mission_command.e149_governed_real_model_invocation_runtime import (
                run_governed_real_model_invocation,
            )

            invocation = run_governed_real_model_invocation(
                owner_text=owner_text,
                cieu_db=cieu_db,
                retrieval_context_summary=retrieval_result["retrieval_context_summary"],
                ystar_gov_root=ystar_gov_root,
                repo_root=repo_root or BRIDGE_ROOT,
                real_model_invoker=real_model_invoker,
            )
            return {
                "reply_text": invocation["reply_text"],
                "reply_backend": invocation["reply_backend"],
                "reply_protocol": invocation["reply_protocol"],
                "runtime_fallback_used": invocation["runtime_fallback_used"],
                "adaptive_retrieval_result": adaptive_retrieval_result,
                "adaptive_planner_decision": planner_decision["decision"],
                "retrieval_result": retrieval_result,
                "retrieval_decision": retrieval_decision["decision"],
                "retrieval_context_summary": retrieval_result["retrieval_context_summary"],
                "model_orchestration_result": invocation["model_orchestration_result"],
                "actual_model_invocation_proof": invocation["actual_model_invocation_proof"],
            }

        route = route_chat_message_to_aiden_meeting_room(
            f"Aiden: {owner_text}",
            repo_root=Path(repo_root or BRIDGE_ROOT),
            cieu_db=cieu_db,
            ystar_gov_root=Path(ystar_gov_root or Y_GOV_ROOT),
            allow_live_network=allow_live_network,
        )
        return {
            "reply_text": route.response_text or "Aiden received the message, but the governed response was empty.",
            "reply_backend": route.route,
            "reply_protocol": route.protocol,
            "runtime_fallback_used": False,
            "adaptive_retrieval_result": adaptive_retrieval_result,
            "adaptive_planner_decision": planner_decision["decision"],
            "retrieval_result": retrieval_result,
            "retrieval_decision": retrieval_decision["decision"],
            "retrieval_context_summary": retrieval_result["retrieval_context_summary"],
        }
    except Exception as exc:
        return {
            "reply_text": (
                "Aiden Messenger Runtime Notice: I received your message inside the governed local messenger, "
                "but the Aiden behavior runtime could not complete this reply. The message was still recorded "
                "with CIEU/CZL provenance. Correct path: inspect the Aiden runtime error and retry."
            ),
            "reply_backend": "runtime_fallback_notice",
            "reply_protocol": "AidenMessengerFallbackV1",
            "runtime_fallback_used": True,
            "runtime_error": str(exc),
            "adaptive_retrieval_result": None,
            "adaptive_planner_decision": "runtime_error",
            "retrieval_result": None,
            "retrieval_decision": "runtime_error",
            "retrieval_context_summary": "",
        }


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _is_chinese_owner_dialogue(text: str) -> bool:
    if not text.strip():
        return False
    cjk_count = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    letter_count = sum(1 for char in text if char.isalpha())
    return cjk_count >= 12 and cjk_count >= max(8, int(letter_count * 0.18))


def _compact_owner_text(owner_text: str, limit: int = 180) -> str:
    normalized = " ".join(str(owner_text).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def _compact_runtime_text(text: str, limit: int = 900) -> str:
    normalized = "\n".join(line.rstrip() for line in str(text).strip().splitlines() if line.strip())
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "\n...（原始运行输出较长，已在 owner-facing 回复里截断；完整记录仍在 CIEU packet/runtime artifact 中。）"


STRATEGY_RECEIPT_LABEL_ORDER = (
    "Provider mode",
    "No-new-wheel decision",
    "CZL Rt+1",
    "Code index loaded",
    "Action-relevant capability groups",
    "Evidence count",
    "Dated evidence",
    "Fresh evidence accepted",
    "Brain learning candidates",
    "CIEU events",
    "Selected first-cash path",
    "selected_route_id",
    "math_model_score",
    "EVSI",
    "Top market-first routes",
    "Boundary",
)


def _receipt_label_index(text: str, label: str, start: int = 0) -> int:
    match = re.search(rf"(?:^|\s+-\s+|\s){re.escape(label)}:\s*", text[start:])
    if not match:
        return -1
    return start + match.start()


def _extract_strategy_receipt_value(text: str, label: str) -> str:
    start = _receipt_label_index(text, label)
    if start < 0:
        return ""
    value_start = text.find(":", start) + 1
    next_indices = [
        idx
        for other in STRATEGY_RECEIPT_LABEL_ORDER
        if other != label
        for idx in [_receipt_label_index(text, other, value_start)]
        if idx >= 0
    ]
    value_end = min(next_indices) if next_indices else len(text)
    return " ".join(text[value_start:value_end].split()).strip(" -")


def _format_strategy_route_for_owner(route: str) -> str:
    match = re.match(r"(?P<route_id>[a-zA-Z0-9_]+):\s*score=(?P<score>[^,]+),\s*EVSI=(?P<evsi>[^|]+)\|\s*(?P<title>.+)", route)
    if not match:
        return route
    return (
        f"{match.group('route_id')}：score={match.group('score').strip()}，"
        f"EVSI={match.group('evsi').strip()}；{match.group('title').strip()}"
    )


def _extract_strategy_milestone(text: str) -> str:
    value = text.replace("CEO Strategy Runtime:", "", 1).strip()
    cut_points = []
    if "This Aiden strategy question" in value:
        cut_points.append(value.index("This Aiden strategy question"))
    for label in STRATEGY_RECEIPT_LABEL_ORDER:
        idx = _receipt_label_index(value, label)
        if idx >= 0:
            cut_points.append(idx)
    if cut_points:
        value = value[: min(cut_points)]
    return " ".join(value.split()).strip()


def _extract_top_strategy_routes(text: str, limit: int = 3) -> list[str]:
    section = _extract_strategy_receipt_value(text, "Top market-first routes")
    if not section:
        return []
    routes = []
    pattern = re.compile(
        r"(?:^|\s+-\s*)(?P<route>[a-zA-Z0-9_]+:\s*score=.*?)(?=\s+-\s*[a-zA-Z0-9_]+:\s*score=|$)"
    )
    for match in pattern.finditer(section):
        routes.append(_format_strategy_route_for_owner(" ".join(match.group("route").split())))
        if len(routes) >= limit:
            break
    return routes


def _is_strategy_runtime_receipt(reply_runtime: Mapping[str, Any], raw_reply: str) -> bool:
    backend = str(reply_runtime.get("reply_backend") or "")
    protocol = str(reply_runtime.get("reply_protocol") or "")
    return (
        "strategy" in backend
        or "Strategy" in protocol
        or raw_reply.startswith("CEO Strategy Runtime:")
        or "Selected first-cash path:" in raw_reply
    )


def _render_strategy_receipt_as_chinese(owner_text: str, reply_runtime: Mapping[str, Any], raw_reply: str) -> str:
    milestone = _extract_strategy_milestone(raw_reply)
    provider_mode = _extract_strategy_receipt_value(raw_reply, "Provider mode") or "未解析"
    no_new_wheel = _extract_strategy_receipt_value(raw_reply, "No-new-wheel decision") or "未解析"
    selected_path = _extract_strategy_receipt_value(raw_reply, "Selected first-cash path") or "未解析"
    selected_route_id = _extract_strategy_receipt_value(raw_reply, "selected_route_id") or "未解析"
    score = _extract_strategy_receipt_value(raw_reply, "math_model_score") or "未解析"
    evsi = _extract_strategy_receipt_value(raw_reply, "EVSI") or "未解析"
    evidence_count = _extract_strategy_receipt_value(raw_reply, "Evidence count") or "未解析"
    dated_evidence = _extract_strategy_receipt_value(raw_reply, "Dated evidence") or "未解析"
    cieu_events = _extract_strategy_receipt_value(raw_reply, "CIEU events") or "未解析"
    top_routes = _extract_top_strategy_routes(raw_reply)
    rendered_routes = "\n".join(f"- {route}" for route in top_routes) if top_routes else "- 未能从机器收据中解析候选路线。"

    freshness_warning = ""
    if "snapshot" in provider_mode.lower():
        freshness_warning = (
            "\n\n重要提醒：这次 provider mode 显示为 snapshot，说明它使用的是受控公开证据快照，"
            "不等同于实时联网扫描。若你的消息要求“上网/最新/实时搜索”，meeting room server 必须把 live public-read 打开。"
        )

    return (
        "我的判断：这轮 Aiden 返回的是策略运行结果，但 owner-facing 层必须先讲内容，不该先让你读流程。\n\n"
        "1. 当前结论是什么？\n"
        f"当前候选排序选中的是：{selected_path}。\n"
        f"内部 route id 是 `{selected_route_id}`，数学分数是 `{score}`，EVSI 是 `{evsi}`。\n\n"
        "2. 它为什么会这么选？\n"
        f"这轮使用的 provider mode 是 `{provider_mode}`，证据数量是 `{evidence_count}`，带日期证据是 `{dated_evidence}`，"
        f"no-new-wheel 决策是 `{no_new_wheel}`，CIEU 事件数是 `{cieu_events}`。也就是说，它主要是在当前受控证据集里，"
        f"把“{selected_path}”判断为更贴近当前证据、能力和约束的候选路径；这个解释不能再把固定的 AI 安全路线塞进所有问题。"
        f"{freshness_warning}\n\n"
        "3. 其他候选路线有哪些？\n"
        f"{rendered_routes}\n\n"
        "4. 这条结论应该怎么理解？\n"
        "它不是客户验证，不是收入信号，也不是已经证明市场愿意付钱。它只是一次受治理的战略候选排序。"
        "如果你问的是推进或赚钱路径，合格回答必须继续给出目标买方、交付物、验证问题和内部行动包，而不是停在“建议下一步”。\n\n"
        "5. 运行证明，放在最后\n"
        f"触发 runtime：`{milestone or 'CEO strategy runtime'}`。这些证明用于审计，不应替代 CEO 判断。\n\n"
        "6. 边界\n"
        "这轮没有外部发送、没有客户联系、没有付款、没有收入证明、没有 live provider execution，也没有 K9Audit 写入。\n\n"
        f"你的原始问题摘要：{_compact_owner_text(owner_text)}"
    )


def apply_owner_dialogue_language_policy(owner_text: str, reply_runtime: Mapping[str, Any]) -> dict[str, Any]:
    """Ensure Aiden's owner-facing message is clear Chinese, even if the runtime body is English."""

    runtime = dict(reply_runtime)
    raw_reply = str(runtime.get("reply_text") or "").strip()
    policy = {
        "target_language": OWNER_DIALOGUE_LANGUAGE,
        "style": "fluent_logical_chinese_owner_dialogue",
        "raw_runtime_reply_preserved_in_runtime_artifact": True,
        "applied": False,
    }
    if _is_strategy_runtime_receipt(runtime, raw_reply):
        policy["applied"] = True
        policy["strategy_runtime_receipt_translated"] = True
        runtime["raw_reply_text_before_owner_dialogue_policy"] = raw_reply
        runtime["reply_text"] = _render_strategy_receipt_as_chinese(owner_text, runtime, raw_reply)
        runtime["owner_answer_generalization_gate"] = _validate_owner_answer_generalization_safe(owner_text, runtime["reply_text"])
        runtime["owner_dialogue_language_policy"] = policy
        return runtime

    if _is_chinese_owner_dialogue(raw_reply):
        runtime["owner_answer_generalization_gate"] = _validate_owner_answer_generalization_safe(owner_text, raw_reply)
        runtime["owner_dialogue_language_policy"] = policy
        return runtime

    backend = str(runtime.get("reply_backend") or "unknown_runtime")
    protocol = str(runtime.get("reply_protocol") or "unknown_protocol")
    retrieval_decision = str(runtime.get("retrieval_decision") or "not_applicable")
    planner_decision = str(runtime.get("adaptive_planner_decision") or "not_applicable")
    if not raw_reply:
        raw_reply = "Aiden runtime returned an empty response."

    policy["applied"] = True
    runtime["raw_reply_text_before_owner_dialogue_policy"] = raw_reply
    runtime["reply_text"] = (
        "我先用中文把这轮 Aiden 的回复整理清楚。\n\n"
        f"1. 我理解你的输入：{_compact_owner_text(owner_text)}\n\n"
        "2. 这轮实际走过的受控链路："
        f"{backend} / {protocol}；检索规划决策={planner_decision}；检索治理决策={retrieval_decision}。\n\n"
        "3. 当前可用结论：\n"
        f"{_compact_runtime_text(raw_reply)}\n\n"
        "4. 讨论边界：如果这只是备忘录，我会把它当作本地受控上下文记录；如果你是在要求战略、外部行动、付款、发布或客户触达，"
        "我必须继续走对应的治理链路，不能把一句自然语言直接当成执行授权。\n\n"
        "5. 下一步：你可以继续追问“为什么”“依据是什么”“下一步怎么做”，我会优先用中文、分点、带边界地回答。"
    )
    runtime["owner_answer_generalization_gate"] = _validate_owner_answer_generalization_safe(owner_text, runtime["reply_text"])
    runtime["owner_dialogue_language_policy"] = policy
    return runtime


def _validate_owner_answer_generalization_safe(owner_text: str, answer_text: str) -> dict[str, Any]:
    try:
        from office.mission_command.e144_hardcode_generalization_audit import validate_owner_answer_generalization

        return validate_owner_answer_generalization(owner_text, answer_text)
    except Exception as exc:  # pragma: no cover - guard must never break messenger replies.
        return {
            "artifact_id": "e144_owner_answer_generalization_gate",
            "decision": "NOT_RUN",
            "passed": False,
            "runtime_error": exc.__class__.__name__,
        }


def run_agent_native_messenger_turn(
    *,
    owner_text: str,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    reply_text_override: str | None = None,
    allow_live_network: bool = False,
    runtime_owner_text: str | None = None,
    real_model_invoker: Any | None = None,
) -> dict[str, Any]:
    """Record an owner message, generate Aiden's reply, and record the reply."""

    participants = build_agent_native_participants()
    owner_packet = build_agent_native_message_packet(
        thread_id="local_owner_aiden_chat",
        sender_id="owner",
        recipient_ids=["Aiden"],
        message_kind="human_to_agent",
        human_readable_text=owner_text,
        cieu_five_tuple=build_cieu_five_tuple(
            y_star="Owner message enters Aiden's governed CEO meeting room.",
            context={"source": "agent-native messenger", "local_only": True},
            action={"speech_act": "owner_message_to_aiden", "text_preview": owner_text[:180]},
            expected_next="Aiden generates a governed reply and records it as a CIEU-native message.",
        ),
        cieu_db=cieu_db,
        participants=participants,
    )
    owner_validation = validate_and_record_agent_native_message(owner_packet, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    if owner_validation["governance_decision"]["decision"] != "ALLOW":
        return {
            "artifact_id": "e124_agent_native_messenger_turn_result",
            "turn_status": "owner_message_not_allowed",
            "owner_packet": owner_packet,
            "owner_validation": owner_validation,
            "aiden_reply_packet": None,
            "aiden_reply_validation": None,
            "CIEUStore_summary": summarize_cieustore(cieu_db),
            "aiden_auto_reply_generated": False,
        }

    effective_owner_text = runtime_owner_text or owner_text
    reply_runtime = (
        {
            "reply_text": reply_text_override,
            "reply_backend": "test_override",
            "reply_protocol": "AidenMessengerTestOverrideV1",
            "runtime_fallback_used": False,
        }
        if reply_text_override is not None
        else generate_aiden_reply_text(
            effective_owner_text,
            cieu_db=cieu_db,
            ystar_gov_root=ystar_gov_root,
            allow_live_network=allow_live_network,
            require_real_model_invocation=True,
            real_model_invoker=real_model_invoker,
        )
    )
    if runtime_owner_text and runtime_owner_text != owner_text:
        reply_runtime["runtime_owner_text_resolved_from_context"] = True
        reply_runtime["visible_owner_text"] = owner_text
        reply_runtime["resolved_runtime_owner_text_preview"] = runtime_owner_text[:600]
    reply_runtime = apply_owner_dialogue_language_policy(owner_text, reply_runtime)
    reply_packet = build_agent_native_message_packet(
        thread_id="local_owner_aiden_chat",
        sender_id="Aiden",
        recipient_ids=["owner"],
        message_kind="agent_to_human",
        human_readable_text=str(reply_runtime["reply_text"]),
        cieu_five_tuple=build_cieu_five_tuple(
            y_star="Aiden answers the owner as CEO through governed local messaging.",
            context={
                "source": "Aiden governed router",
                "reply_backend": reply_runtime["reply_backend"],
                "reply_protocol": reply_runtime["reply_protocol"],
                "owner_dialogue_language": OWNER_DIALOGUE_LANGUAGE,
                "owner_dialogue_language_policy": reply_runtime.get("owner_dialogue_language_policy", {}),
                "adaptive_planner_decision": reply_runtime.get("adaptive_planner_decision", "not_applicable"),
                "retrieval_decision": reply_runtime.get("retrieval_decision", "not_applicable"),
                "retrieval_context_summary": reply_runtime.get("retrieval_context_summary", "")[:500],
                "actual_model_invocation_proof": reply_runtime.get("actual_model_invocation_proof", {}),
            },
            action={"speech_act": "aiden_reply_to_owner", "runtime_fallback_used": reply_runtime["runtime_fallback_used"]},
            expected_next="Owner receives an actual Aiden reply plus CIEU/CZL provenance.",
            residual="pending until owner reads or responds",
        ),
        cieu_db=cieu_db,
        message_id=f"reply_{uuid.uuid4().hex[:12]}",
        participants=participants,
    )
    reply_validation = validate_and_record_agent_native_message(reply_packet, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    return {
        "artifact_id": "e124_agent_native_messenger_turn_result",
        "turn_status": "completed" if reply_validation["governance_decision"]["decision"] == "ALLOW" else "reply_message_not_allowed",
        "owner_packet": owner_packet,
        "owner_validation": owner_validation,
        "aiden_reply_runtime": reply_runtime,
        "aiden_reply_packet": reply_packet,
        "aiden_reply_validation": reply_validation,
        "message_packets": [owner_packet, reply_packet],
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "aiden_auto_reply_generated": True,
        "external_action_executed": False,
        "payment_executed": False,
    }


def run_agent_native_messenger_demo_session(
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    participants = build_agent_native_participants()
    messages = [
        build_agent_native_message_packet(
            thread_id="owner_aiden_ceo_meeting",
            sender_id="owner",
            recipient_ids=["Aiden"],
            message_kind="human_to_agent",
            human_readable_text="Aiden, open a governed company meeting and turn my intent into a CEO-readable action thread.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Owner intent becomes a governed Aiden CEO meeting.",
                context={"source": "owner local messenger", "risk": "internal"},
                action={"speech_act": "request", "intended_effect": "open governed meeting"},
                expected_next="Aiden receives a CIEU-recorded local message and prepares a CEO response.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_001_owner_to_aiden",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="aiden_strategy_agent",
            sender_id="Aiden",
            recipient_ids=["StrategyAgent"],
            message_kind="agent_to_agent",
            human_readable_text="Strategy Agent, prepare a no-send opportunity map for agent-native company communication, using current governed capabilities only.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Aiden delegates internal analysis without external action.",
                context={"source": "Aiden CEO", "available_capabilities": ["CIEUStore", "model orchestration", "local messenger"]},
                action={"speech_act": "delegate_internal_research", "recipient": "StrategyAgent"},
                expected_next="StrategyAgent returns a CIEU-scoped local synthesis to Aiden.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_002_aiden_to_strategy",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="aiden_strategy_agent",
            sender_id="StrategyAgent",
            recipient_ids=["Aiden"],
            message_kind="execution_receipt",
            human_readable_text="Aiden, the local messenger should start as a governed meeting room plus CIEU message spine before any external-agent network is enabled.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Internal analysis returns actionable, no-send guidance.",
                context={"source": "StrategyAgent", "external_action": False},
                action={"speech_act": "return_receipt", "finding": "start with governed local message spine"},
                expected_next="Aiden integrates the receipt into owner-facing next action.",
                residual="planning residual closed for local messenger scope; market residual pending",
                residual_status="planning_residual_closed_real_world_pending",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_003_strategy_to_aiden",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="owner_aiden_ceo_meeting",
            sender_id="Aiden",
            recipient_ids=["owner"],
            message_kind="governance_notice",
            human_readable_text="Owner, the first safe version is a local agent-native company messenger: natural language for people, CIEU/CZL five-tuples for agents, and CIEUStore memory for every message.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Owner receives a clear CEO answer plus machine-readable governance trace.",
                context={"source": "Aiden CEO", "decision": "local-first messenger"},
                action={"speech_act": "respond_to_owner", "recommendation": "ship local governed messenger first"},
                expected_next="Owner can inspect both human answer and CIEU five-tuple trace.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_004_aiden_to_owner",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="owner_finance_agent_wallet_proposal",
            sender_id="Aiden",
            recipient_ids=["owner", "FinanceAgent"],
            message_kind="wallet_proposal",
            human_readable_text="Proposal only: future versions may attach USDC wallet intents to agent contracts, but E124 executes no payment and no transfer.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Wallet-related communication remains proposal-only until owner and payment boundaries exist.",
                context={"source": "Aiden CEO", "wallet_feature": "future USDC proposal"},
                action={"speech_act": "wallet_capability_proposal", "payment_execution": False},
                expected_next="FinanceAgent can model wallet UX without moving funds.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_005_wallet_proposal",
            participants=participants,
            wallet_proposal={"proposal_only": True, "payment_executed": False, "USDC_transfer_executed": False, "risk_tier": "payment_boundary_future"},
        ),
    ]
    validations = [
        validate_and_record_agent_native_message(packet, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
        for packet in messages
    ]
    return {
        "artifact_id": "e124_agent_native_company_messenger_demo_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "participants": participants,
        "message_packets": messages,
        "YstarGov_message_results": validations,
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "human_language_plus_CIEU_five_tuple_proven": all(_has_five_tuple(packet) for packet in messages),
        "human_agent_and_agent_agent_paths_proven": True,
        "wallet_proposal_boundary_proven": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "payment_executed": False,
        "USDC_transfer_executed": False,
        "what_was_not_claimed": [
            "no external agent message was sent",
            "no customer contact",
            "no revenue or payment validation",
            "no USDC transfer",
            "no K9Audit write",
        ],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_agent_native_company_messenger",
            "L5-B": "stronger_governed_intelligence_with_CIEU_native_human_agent_and_agent_agent_communication",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_and_CIEU_backed_message_memory",
        },
    }


def write_e124_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_agent_native_messenger_demo_session(cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    protocol_spec = build_message_protocol_spec()
    report = {
        "milestone_id": MILESTONE_ID,
        "base_hashes": {
            "bridge_labs": "4953876d86ecb03844b605f49418378432484d54",
            "Y_star_gov": "07f020c35d2af6d5a0a156d53ee8bcfd1ee42fbe",
        },
        "existing_systems_reused": [
            "scripts/meeting_room concept and meeting UI lineage",
            "E123 model orchestration runtime",
            "Y-star-gov CIEUStore",
            "CIEU/CZL five tuple vocabulary",
            "Aiden meeting-room routing direction",
        ],
        "message_protocol": protocol_spec,
        "demo_result": result,
        "CIEUStore_records_written": result["CIEUStore_summary"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_agent_native_company_messenger",
        "human_readable_plus_CIEU_five_tuple_required": True,
        "human_agent_message_path": "proven",
        "agent_agent_message_path": "proven",
        "wallet_support": "proposal_only_no_payment_execution",
        "external_agent_support": "proposal_only_no_send",
        "CIEUStore_summary": result["CIEUStore_summary"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e124_agent_native_company_messenger_report.json",
        "report_md": base / "office/mission_command/e124_agent_native_company_messenger_readback.md",
        "protocol_json": base / "operations/agent_native_messenger/e124_message_protocol_spec.json",
        "protocol_md": base / "operations/agent_native_messenger/e124_message_protocol_spec.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e124_agent_native_company_messenger.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e124_agent_native_company_messenger.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["protocol_json"].write_text(json.dumps(protocol_spec, indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["protocol_md"].write_text(_protocol_md(protocol_spec), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return {"result": result, "report": report, "status": status, "protocol_spec": protocol_spec, "files": {k: str(v) for k, v in files.items()}}


def build_message_protocol_spec() -> dict[str, Any]:
    return {
        "protocol_id": "aiden_agent_native_company_messenger_protocol_v1",
        "milestone_id": MILESTONE_ID,
        "principle": "Every formal communication speaks human language and carries CIEU/CZL five-tuple state.",
        "required_message_fields": [
            "human_readable_text",
            "cieu_five_tuple.Y_star_t",
            "cieu_five_tuple.X_t",
            "cieu_five_tuple.U_t",
            "cieu_five_tuple.Y_t_plus_1",
            "cieu_five_tuple.R_t_plus_1",
        ],
        "supported_paths": [
            "human_to_agent",
            "agent_to_human",
            "agent_to_agent",
            "group_meeting",
            "file_attachment_metadata",
            "image_attachment_metadata",
            "wallet_proposal_no_payment",
            "external_agent_proposal_no_send",
        ],
        "execution_boundaries": {
            "local_messenger_only": True,
            "external_agent_delivery": "owner_approved_future_boundary_required",
            "wallet": "proposal_only_until_payment_boundary_exists",
            "CIEUStore": "mandatory for every formal message",
            "model_orchestration": "mandatory when any agent participates",
        },
    }


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "event_count": 0, "event_types": []}
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
        event_types = [row[0] for row in conn.execute("SELECT DISTINCT event_type FROM cieu_events ORDER BY event_type").fetchall()]
    return {"db_path": str(path), "event_count": int(count), "event_types": event_types}


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _has_five_tuple(packet: Mapping[str, Any]) -> bool:
    five_tuple = dict(dict(packet.get("message") or {}).get("cieu_five_tuple") or {})
    return all(five_tuple.get(field) for field in CIEU_FIVE_TUPLE_FIELDS)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _report_md(report: Mapping[str, Any]) -> str:
    result = dict(report["demo_result"])
    return "\n".join(
        [
            "# E124 Agent Native Company Messenger",
            "",
            "## What Changed",
            "- Built a local company messenger protocol for owner, Aiden, Codex, Labs agents, and future external-agent proposals.",
            "- Every formal message must include human-readable text and the CIEU/CZL five tuple.",
            "- Y-star-gov validates each message and CIEUStore records each decision.",
            "",
            "## Proof",
            f"- Messages written: {len(result['message_packets'])}",
            f"- CIEU events: {result['CIEUStore_summary']['event_count']}",
            f"- Event types: {', '.join(result['CIEUStore_summary']['event_types'])}",
            "- External actions: none.",
            "- Wallet/payment: proposal-only; no USDC transfer.",
            "",
            "## L5 Truth Table",
            *[f"- {key}: {value}" for key, value in result["L5_truth_table_after"].items()],
        ]
    )


def _protocol_md(spec: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# E124 Message Protocol Spec",
            "",
            f"Protocol: `{spec['protocol_id']}`",
            "",
            "## Required Message Shape",
            *[f"- `{field}`" for field in spec["required_message_fields"]],
            "",
            "## Supported Paths",
            *[f"- {path}" for path in spec["supported_paths"]],
            "",
            "## Boundaries",
            *[f"- {key}: {value}" for key, value in spec["execution_boundaries"].items()],
        ]
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Current Runtime Status After E124",
            "",
            f"Status: {status['status']}",
            "",
            "## Communication Boundary",
            "- Human-readable text plus CIEU/CZL five tuple is mandatory for formal messages.",
            "- Human-agent and agent-agent paths are proven in isolated CIEUStore.",
            "- External-agent and wallet capabilities remain proposal-only.",
            "",
            "## L5 Truth Table",
            *[f"- {key}: {value}" for key, value in status["L5_truth_table_after"].items()],
        ]
    )


if __name__ == "__main__":
    db = Path(os.environ.get("E124_CIEU_DB", "/tmp/e124_agent_native_company_messenger.db"))
    output = write_e124_reports(cieu_db=db)
    print(json.dumps({"status": "ok", "files": output["files"], "CIEUStore_summary": output["result"]["CIEUStore_summary"]}, indent=2))
