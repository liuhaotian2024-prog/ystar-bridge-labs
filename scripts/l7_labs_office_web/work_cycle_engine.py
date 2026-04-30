#!/usr/bin/env python3
"""Bounded local work-cycle engine for the Labs whiteboard runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_worker_runtime import auditor_boundary_reply, generate_agent_reply
from team_router import route_owner_goal
from whiteboard_store import (
    PACKET_ROOT,
    append_timeline,
    create_agent_reply,
    create_approval_request,
    create_completion_report as store_completion_report,
    create_routing_decision,
    create_whiteboard_message,
    create_work_cycle_packet,
    create_work_item,
    latest_message,
    load_agent_replies,
    load_work_items,
    save_work_item,
    whiteboard_snapshot,
)


def route_latest_or_payload(payload: dict[str, Any] | None = None, packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    message = payload.get("message") if payload and payload.get("message") else latest_message(packet_root)
    if not message:
        text = (payload or {}).get("text", "Owner asked the team to prepare the next safe internal work item.")
        message = create_whiteboard_message(text=text, target=(payload or {}).get("target", "whole_team"), objective=(payload or {}).get("objective", ""), packet_root=packet_root)
    text = message.get("text", "")
    routing = route_owner_goal(text, message.get("target", "whole_team"))
    title = text[:72] or "Untitled owner whiteboard task"
    assigned = [routing["primary_agent"], *routing.get("supporting_agents", [])]
    item = create_work_item(
        title=title,
        description=text,
        source_message_id=message.get("message_id"),
        assigned_agents=assigned,
        status="Assigned",
        packet_root=packet_root,
    )
    decision = create_routing_decision(message, routing, item, packet_root)
    append_timeline("Aiden interpreted", routing["reason"], {"work_item_id": item["work_item_id"]}, packet_root)
    return {"ok": True, "message": message, "routing_decision": decision, "work_item": item}


def active_items(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return [
        item
        for item in load_work_items(packet_root)
        if item.get("status") in {"Inbox", "Interpreting", "Assigned", "In Progress"}
    ]


def run_work_cycle(
    work_item_id: str | None = None,
    max_agent_replies: int = 8,
    packet_root: Path = PACKET_ROOT,
) -> dict[str, Any]:
    items = active_items(packet_root)
    if work_item_id:
        items = [item for item in load_work_items(packet_root) if item.get("work_item_id") == work_item_id]
    if not items:
        routed = route_latest_or_payload(packet_root=packet_root)
        items = [routed["work_item"]]
    item = items[0]
    if item.get("status") == "Inbox":
        item["status"] = "Assigned"
    item["status"] = "In Progress"
    item.setdefault("progress_notes", []).append("Safe local work cycle started.")
    save_work_item(item, packet_root)
    append_timeline("work cycle started", item["title"], {"work_item_id": item["work_item_id"]}, packet_root)

    replies = []
    assigned_agents = item.get("assigned_agents") or ["aiden_ceo"]
    for agent_id in assigned_agents[:max_agent_replies]:
        replies.append(create_agent_reply(generate_agent_reply(agent_id, item), packet_root))
    replies.append(create_agent_reply(auditor_boundary_reply(item), packet_root))

    approval_needed = any(reply.get("approval_needed") for reply in replies)
    if approval_needed:
        item["status"] = "Waiting for Approval"
        item.setdefault("blockers", []).append("Owner approval required before external action.")
        approval_request = create_approval_request(item, "Task implies approval-gated action.", packet_root)
    else:
        item["status"] = "Done"
        approval_request = None
    item.setdefault("progress_notes", []).append(f"Generated {len(replies)} role-specific local replies.")
    save_work_item(item, packet_root)
    cycle = create_work_cycle_packet(
        {
            "work_items_processed": [item["work_item_id"]],
            "agents_involved": [reply["agent_id"] for reply in replies],
            "actions_taken": ["generated local agent replies", "updated local work item status"],
            "artifacts_created": [reply["reply_id"] for reply in replies],
            "blocked_items": [item["work_item_id"]] if item["status"] == "Waiting for Approval" else [],
            "approval_requests_created": [approval_request["approval_request_id"]] if approval_request else [],
        },
        packet_root,
    )
    return {"ok": True, "work_item": item, "agent_replies": replies, "approval_request": approval_request, "work_cycle": cycle}


def run_team_work_cycle(
    max_work_items_per_cycle: int = 3,
    max_agent_replies_per_cycle: int = 8,
    packet_root: Path = PACKET_ROOT,
) -> dict[str, Any]:
    items = active_items(packet_root)[:max_work_items_per_cycle]
    if not items:
        routed = route_latest_or_payload(packet_root=packet_root)
        items = [routed["work_item"]]
    results = []
    for item in items:
        results.append(run_work_cycle(item["work_item_id"], max_agent_replies_per_cycle, packet_root))
    return {"ok": True, "items_processed": [result["work_item"]["work_item_id"] for result in results], "results": results}


def create_completion_report(work_item_id: str | None = None, packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    items = load_work_items(packet_root)
    if work_item_id:
        items = [item for item in items if item.get("work_item_id") == work_item_id]
    if not items:
        routed = route_latest_or_payload(packet_root=packet_root)
        run_work_cycle(routed["work_item"]["work_item_id"], packet_root=packet_root)
        items = [routed["work_item"]]
    item = items[-1]
    if item.get("status") not in {"Done", "Waiting for Approval", "Blocked"}:
        item["status"] = "Done"
        save_work_item(item, packet_root)
    replies = load_agent_replies(packet_root)
    report = store_completion_report(item, replies, packet_root)
    return {"ok": True, "completion_report": report}


def create_demo_scenario() -> dict[str, Any]:
    text = "团队请一起分析：我们下一步怎么最快拿到第一笔钱，同时不牺牲长期战略？"
    routing = route_owner_goal(text, "whole_team")
    assigned = [routing["primary_agent"], *routing["supporting_agents"]]
    work_item = {
        "work_item_id": "demo_work_item_first_cash_path",
        "title": "Fastest first-cash path without sacrificing long-term strategy",
        "description": text,
        "assigned_agents": assigned,
        "status": "Done",
    }
    replies = [generate_agent_reply(agent_id, work_item) for agent_id in assigned[:7]]
    replies.append(auditor_boundary_reply(work_item))
    return {
        "schema_version": "v0",
        "milestone_id": "L7.5",
        "demo_id": "demo_first_cash_path_team_discussion",
        "owner_message": text,
        "flow": [
            "Aiden interprets and delegates",
            "Zara analyzes commercialization path",
            "Marco checks pricing/cash assumptions",
            "Sofia drafts positioning",
            "Jinjin proposes read-only research",
            "Ethan identifies missing tools",
            "Samantha indexes outputs",
            "Auditor function reviews boundaries",
        ],
        "routing_decision": routing,
        "work_item": work_item,
        "agent_replies": replies,
        "no_action_receipt": {
            "external_side_effects_occurred": False,
            "core_writeback_occurred": False,
            "customer_contacted": False,
            "email_sent": False,
            "payment_occurred": False,
        },
    }


def snapshot(packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    return whiteboard_snapshot(packet_root)
