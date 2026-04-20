#!/usr/bin/env python3
"""
Aiden Action Queue — Persistent "nagging" mechanism.

Every identified-but-not-acted-on item goes here.
Every response MUST check this queue before ending.
Items accumulate urgency over time — the longer they sit, the louder they nag.

This is NOT a todo list. This is a cognitive pressure mechanism.
Like the human feeling of "I forgot to turn off the stove" — it doesn't
go away just because you're in a conversation.

Usage:
    aiden_action_queue.py add "description" --source "where discovered"
    aiden_action_queue.py check           — show all pending items with urgency
    aiden_action_queue.py resolve ID      — mark item as acted on
    aiden_action_queue.py nag             — one-line summary for mid-conversation check
"""

import os
import sys
import json
import time

QUEUE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", ".logs", "action_queue.json"
)


def _load() -> list:
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save(queue: list):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def add_item(description: str, source: str = ""):
    queue = _load()
    item = {
        "id": len(queue) + 1,
        "description": description,
        "source": source,
        "created_at": time.time(),
        "created_at_human": time.strftime("%Y-%m-%d %H:%M"),
        "status": "pending",
        "urgency": 1.0,
    }
    queue.append(item)
    _save(queue)
    print(f"  + Action #{item['id']}: {description[:60]}")


def check_queue():
    queue = _load()
    pending = [i for i in queue if i["status"] == "pending"]
    if not pending:
        print("  Action queue empty. All clear.")
        return

    now = time.time()
    print(f"  === ACTION QUEUE: {len(pending)} pending ===")
    for item in pending:
        age_min = (now - item["created_at"]) / 60
        urgency = min(10.0, item["urgency"] + age_min / 30)
        marker = "🔴" if urgency > 5 else ("🟡" if urgency > 2 else "⚪")
        print(f"  {marker} #{item['id']} [{urgency:.1f}] {item['description'][:55]}")
        if item.get("source"):
            print(f"       source: {item['source'][:50]}")


def resolve_item(item_id: int):
    queue = _load()
    for item in queue:
        if item["id"] == item_id:
            item["status"] = "resolved"
            item["resolved_at"] = time.time()
            _save(queue)
            print(f"  ✅ Resolved #{item_id}: {item['description'][:50]}")
            return
    print(f"  Item #{item_id} not found")


def nag():
    """One-line nag for mid-conversation insertion."""
    queue = _load()
    pending = [i for i in queue if i["status"] == "pending"]
    if not pending:
        return ""
    now = time.time()
    urgent = []
    for item in pending:
        age_min = (now - item["created_at"]) / 60
        urgency = min(10.0, item["urgency"] + age_min / 30)
        if urgency > 3:
            urgent.append(f"#{item['id']}")
    if urgent:
        return f"⚠ {len(pending)} actions pending ({len(urgent)} urgent: {', '.join(urgent[:3])})"
    return f"📋 {len(pending)} actions pending (none urgent yet)"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "add":
        desc = " ".join(sys.argv[2:])
        source_flag = ""
        if "--source" in sys.argv:
            idx = sys.argv.index("--source")
            source_flag = " ".join(sys.argv[idx + 1:])
            desc = " ".join(sys.argv[2:idx])
        add_item(desc, source_flag)
    elif cmd == "check":
        check_queue()
    elif cmd == "resolve":
        resolve_item(int(sys.argv[2]))
    elif cmd == "nag":
        msg = nag()
        if msg:
            print(msg)
    else:
        print(f"Unknown command: {cmd}")
