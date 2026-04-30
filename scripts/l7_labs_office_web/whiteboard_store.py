#!/usr/bin/env python3
"""Local JSON packet store for the Labs whiteboard runtime."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WEB_OUT = ROOT / "l7_real_labs_office_web_ui"
PACKET_ROOT = WEB_OUT / "runtime_packets"
L75_OUT = ROOT / "l7_labs_whiteboard_collaboration_runtime"
GENERATED_AT = "2026-04-30T00:00:00Z"

PACKET_DIRS = {
    "whiteboard_threads": PACKET_ROOT / "whiteboard_threads",
    "agent_replies": PACKET_ROOT / "agent_replies",
    "routing_decisions": PACKET_ROOT / "routing_decisions",
    "work_items": PACKET_ROOT / "work_items",
    "work_cycles": PACKET_ROOT / "work_cycles",
    "completion_reports": PACKET_ROOT / "completion_reports",
    "approval_requests": PACKET_ROOT / "approval_requests",
    "owner_messages": PACKET_ROOT / "owner_messages",
    "team_tasks": PACKET_ROOT / "team_tasks",
    "agent_inboxes": PACKET_ROOT / "agent_inboxes",
}

TIMELINE_PATH = PACKET_ROOT / "timeline_events.json"

FORBIDDEN_ACTIONS = [
    "external outreach",
    "email sending",
    "customer contact",
    "publication",
    "payment",
    "form submission",
    "account creation",
    "grant/RFP submission",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]

APPROVAL_REQUIRED_FOR = [
    "outreach",
    "publication",
    "payment",
    "account creation",
    "form submission",
    "grant/RFP submission",
    "customer contact",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]

ALLOWED_ACTIONS = [
    "internal analysis",
    "local artifact review",
    "draft-only artifact generation",
    "approval request preparation",
    "local packet creation",
]


def ensure_dirs(packet_root: Path = PACKET_ROOT) -> None:
    for relative in [
        "whiteboard_threads",
        "agent_replies",
        "routing_decisions",
        "work_items",
        "work_cycles",
        "completion_reports",
        "approval_requests",
        "owner_messages",
        "team_tasks",
        "agent_inboxes",
    ]:
        path = packet_root / relative
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("local runtime packet directory\n", encoding="utf-8")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def now_id() -> str:
    return f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{time.time_ns() % 1_000_000:06d}"


def safe_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.strip())[:90].strip("_")
    return cleaned or "packet"


def atomic_write_json(path: Path, data: Any) -> None:
    if not str(path.resolve()).startswith(str(PACKET_ROOT.resolve())) and not str(path.resolve()).startswith(str(L75_OUT.resolve())):
        raise ValueError(f"Refusing write outside Labs whiteboard packet/output roots: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def packet_base(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.5",
        "packet_type": packet_type,
        "created_at_utc": now_iso(),
        "allowed_actions": ALLOWED_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "approval_required_for": APPROVAL_REQUIRED_FOR,
        "external_side_effects": False,
        "core_writeback": False,
    }


def append_timeline(event_type: str, description: str, refs: dict[str, Any] | None = None, packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    path = packet_root / "timeline_events.json"
    events = read_json(path, [])
    event = {
        "event_id": f"timeline_{now_id()}_{len(events) + 1:04d}",
        "created_at_utc": now_iso(),
        "event_type": event_type,
        "description": description,
        "refs": refs or {},
    }
    events.append(event)
    atomic_write_json(path, events)
    return event


def load_timeline(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return read_json(packet_root / "timeline_events.json", [])


def create_whiteboard_message(
    text: str,
    target: str = "whole_team",
    objective: str = "",
    sender_type: str = "owner",
    sender_id: str = "owner",
    thread_id: str | None = None,
    packet_root: Path = PACKET_ROOT,
) -> dict[str, Any]:
    ensure_dirs(packet_root)
    thread_id = thread_id or f"thread_{now_id()}_{safe_id(target)}"
    message_id = f"message_{now_id()}_{safe_id(sender_id)}"
    message = {
        **packet_base("whiteboard_message"),
        "message_id": message_id,
        "thread_id": thread_id,
        "sender_type": sender_type,
        "sender_id": sender_id,
        "target": target,
        "text": text,
        "objective": objective,
        "linked_work_item": None,
        "status": "queued",
    }
    thread_path = packet_root / "whiteboard_threads" / f"{thread_id}.json"
    thread = read_json(
        thread_path,
        {
            "schema_version": "v0",
            "milestone_id": "L7.5",
            "packet_type": "whiteboard_thread",
            "thread_id": thread_id,
            "created_at_utc": now_iso(),
            "status": "open",
            "messages": [],
        },
    )
    thread["messages"].append(message)
    thread["updated_at_utc"] = now_iso()
    atomic_write_json(thread_path, thread)
    append_timeline("owner message created", f"{sender_id} posted to {target}", {"thread_id": thread_id, "message_id": message_id}, packet_root)
    return message


def load_threads(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    ensure_dirs(packet_root)
    return [read_json(path, {}) for path in sorted((packet_root / "whiteboard_threads").glob("*.json")) if path.name != ".gitkeep"]


def latest_message(packet_root: Path = PACKET_ROOT) -> dict[str, Any] | None:
    messages = []
    for thread in load_threads(packet_root):
        messages.extend(thread.get("messages", []))
    return messages[-1] if messages else None


def create_work_item(
    title: str,
    description: str,
    source_message_id: str | None,
    requested_by: str = "owner",
    assigned_agents: list[str] | None = None,
    status: str = "Inbox",
    packet_root: Path = PACKET_ROOT,
) -> dict[str, Any]:
    ensure_dirs(packet_root)
    work_item_id = f"work_item_{now_id()}_{safe_id(title)}"
    item = {
        **packet_base("work_item"),
        "work_item_id": work_item_id,
        "title": title,
        "description": description,
        "source_message_id": source_message_id,
        "requested_by": requested_by,
        "assigned_agents": assigned_agents or [],
        "status": status,
        "expected_outputs": ["agent replies", "work board update", "completion report"],
        "progress_notes": [],
        "blockers": [],
        "updated_at_utc": now_iso(),
    }
    atomic_write_json(packet_root / "work_items" / f"{work_item_id}.json", item)
    append_timeline("work item created", title, {"work_item_id": work_item_id}, packet_root)
    return item


def load_work_items(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    ensure_dirs(packet_root)
    return [read_json(path, {}) for path in sorted((packet_root / "work_items").glob("*.json")) if path.name != ".gitkeep"]


def save_work_item(item: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    item["updated_at_utc"] = now_iso()
    atomic_write_json(packet_root / "work_items" / f"{item['work_item_id']}.json", item)
    return item


def create_routing_decision(message: dict[str, Any], routing: dict[str, Any], work_item: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    decision_id = f"routing_{now_id()}_{safe_id(work_item['work_item_id'])}"
    decision = {
        **packet_base("routing_decision"),
        "routing_decision_id": decision_id,
        "source_message_id": message.get("message_id"),
        "work_item_id": work_item["work_item_id"],
        **routing,
    }
    atomic_write_json(packet_root / "routing_decisions" / f"{decision_id}.json", decision)
    append_timeline("routing decision created", f"Aiden routed {work_item['title']}", {"routing_decision_id": decision_id, "work_item_id": work_item["work_item_id"]}, packet_root)
    return decision


def create_agent_reply(reply: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    reply_id = f"reply_{now_id()}_{safe_id(reply['agent_id'])}_{safe_id(reply['work_item_id'])}"
    packet = {
        **packet_base("agent_reply"),
        "reply_id": reply_id,
        **reply,
    }
    atomic_write_json(packet_root / "agent_replies" / f"{reply_id}.json", packet)
    append_timeline("agent reply created", f"{reply['agent_id']} replied", {"reply_id": reply_id, "work_item_id": reply["work_item_id"]}, packet_root)
    return packet


def load_agent_replies(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    ensure_dirs(packet_root)
    return [read_json(path, {}) for path in sorted((packet_root / "agent_replies").glob("*.json")) if path.name != ".gitkeep"]


def create_approval_request(work_item: dict[str, Any], reason: str, packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    request_id = f"approval_{now_id()}_{safe_id(work_item['work_item_id'])}"
    request = {
        **packet_base("approval_request"),
        "approval_request_id": request_id,
        "work_item_id": work_item["work_item_id"],
        "reason": reason,
        "default_decision": "blocked_until_human_approved",
        "status": "waiting_for_owner",
    }
    atomic_write_json(packet_root / "approval_requests" / f"{request_id}.json", request)
    append_timeline("approval requested", reason, {"approval_request_id": request_id, "work_item_id": work_item["work_item_id"]}, packet_root)
    return request


def load_approval_requests(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    ensure_dirs(packet_root)
    return [read_json(path, {}) for path in sorted((packet_root / "approval_requests").glob("*.json")) if path.name != ".gitkeep"]


def create_work_cycle_packet(cycle: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    cycle_id = f"work_cycle_{now_id()}_{len(load_timeline(packet_root)) + 1:04d}"
    packet = {
        **packet_base("work_cycle"),
        "work_cycle_id": cycle_id,
        **cycle,
        "no_action_receipt": {
            "external_side_effects_occurred": False,
            "core_writeback_occurred": False,
            "db_log_wal_shm_active_agent_marker_content_read": False,
            "secret_printed_stored_in_repo": False,
        },
    }
    atomic_write_json(packet_root / "work_cycles" / f"{cycle_id}.json", packet)
    append_timeline("work cycle completed", f"Processed {len(cycle.get('work_items_processed', []))} work items", {"work_cycle_id": cycle_id}, packet_root)
    return packet


def create_completion_report(work_item: dict[str, Any], replies: list[dict[str, Any]], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    report_id = f"completion_{now_id()}_{safe_id(work_item['work_item_id'])}"
    report = {
        **packet_base("completion_report"),
        "completion_report_id": report_id,
        "work_item_id": work_item["work_item_id"],
        "summary": f"Completed local internal cycle for: {work_item['title']}",
        "assigned_agents": work_item.get("assigned_agents", []),
        "artifacts": [reply.get("reply_id") for reply in replies if reply.get("work_item_id") == work_item["work_item_id"]],
        "completion_status": work_item.get("status", "Done"),
        "remaining_risks": work_item.get("blockers", []),
        "approval_needed": work_item.get("status") == "Waiting for Approval",
        "next_owner_action": "Review approval request if present; otherwise review completion report.",
    }
    atomic_write_json(packet_root / "completion_reports" / f"{report_id}.json", report)
    append_timeline("completion report generated", report["summary"], {"completion_report_id": report_id, "work_item_id": work_item["work_item_id"]}, packet_root)
    return report


def load_completion_reports(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    ensure_dirs(packet_root)
    return [read_json(path, {}) for path in sorted((packet_root / "completion_reports").glob("*.json")) if path.name != ".gitkeep"]


def work_board(packet_root: Path = PACKET_ROOT) -> dict[str, list[dict[str, Any]]]:
    columns = {name: [] for name in ["Inbox", "Interpreting", "Assigned", "In Progress", "Waiting for Approval", "Blocked", "Done"]}
    for item in load_work_items(packet_root):
        columns.setdefault(item.get("status", "Inbox"), []).append(item)
    return columns


def whiteboard_snapshot(packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    return {
        "threads": load_threads(packet_root),
        "work_board": work_board(packet_root),
        "timeline": load_timeline(packet_root),
        "agent_replies": load_agent_replies(packet_root),
        "approval_requests": load_approval_requests(packet_root),
        "completion_reports": load_completion_reports(packet_root),
    }
