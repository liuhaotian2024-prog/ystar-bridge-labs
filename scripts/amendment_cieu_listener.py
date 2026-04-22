#!/usr/bin/env python3
"""AMENDMENT CIEU Listener — poll proposals jsonl for SELF_MOD_PROPOSAL events.

When AmendmentDraftGenerator writes a draft + emits CIEU event SELF_MOD_PROPOSAL,
this listener picks it up, registers a tracked_entity in OmissionEngine (fallback
to simple deadline jsonl if import fails), and writes Board inbox markdown.

Runs once per invocation (launchd StartInterval). Idempotent via sentinel.

M-tag: M-2b (prevent proposals rotting without Board review) + M-3 (complete
self-modification infrastructure).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
PROPOSALS_LOG = WORKSPACE / "scripts" / ".logs" / "amendment_proposals.jsonl"
SENTINEL = WORKSPACE / "scripts" / ".amendment_listener_sentinel.json"
INBOX = WORKSPACE / "reports" / "cto" / "amendment_proposals_inbox.md"

TIER_DEADLINES_HOURS = {"low": 24, "medium": 72, "high": 48}


def _read_sentinel() -> dict:
    if SENTINEL.exists():
        try:
            return json.loads(SENTINEL.read_text())
        except Exception:
            pass
    return {"last_line_num": 0, "last_run_at": 0}


def _write_sentinel(state: dict) -> None:
    SENTINEL.write_text(json.dumps(state, indent=2))


def _register_omission_tracked(event: dict) -> bool:
    deadline_h = TIER_DEADLINES_HOURS.get(event.get("tier", "medium"), 72)
    deadline_ts = event["timestamp"] + deadline_h * 3600

    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        from register_obligation import register_obligation_programmatic
        register_obligation_programmatic(
            rule_name=f"amendment_review_{event['amendment_id']}",
            subject="board",
            description=f"Review AMENDMENT draft {event['amendment_id']} "
                        f"(tier={event['tier']}, title={event.get('title','')})",
            deadline_unix=deadline_ts,
        )
        return True
    except Exception as e:
        tracker = WORKSPACE / "scripts" / ".logs" / "amendment_deadlines.jsonl"
        tracker.parent.mkdir(parents=True, exist_ok=True)
        with tracker.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "amendment_id": event["amendment_id"],
                "tier": event["tier"],
                "title": event.get("title", ""),
                "posted_at": event["timestamp"],
                "deadline_at": deadline_ts,
                "draft_path": event.get("draft_path", ""),
                "omission_register_error": str(e),
            }) + "\n")
        return False


def _update_inbox(new_events: list) -> None:
    if not new_events:
        return
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    header_exists = INBOX.exists()
    with INBOX.open("a", encoding="utf-8") as f:
        if not header_exists:
            f.write("# AMENDMENT Proposals Inbox\n\n")
            f.write("Audience: Board (Haotian Liu) review queue\n")
            f.write("Research basis: AmendmentDraftGenerator + CIEU listener pipeline\n")
            f.write("Synthesis: Agent-generated AMENDMENT proposals awaiting Board decision\n")
            f.write("Purpose: Single Board review inbox for pending self-modification requests\n\n")
            f.write("---\n\n")
        for ev in new_events:
            posted_at = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(ev['timestamp']))
            deadline_h = TIER_DEADLINES_HOURS.get(ev.get("tier", "medium"), 72)
            f.write(f"## {ev['amendment_id']} — {ev.get('title','')}\n\n")
            f.write(f"- **Tier**: {ev.get('tier','medium')}\n")
            f.write(f"- **Posted**: {posted_at}\n")
            f.write(f"- **Review deadline**: {deadline_h}h from posted\n")
            f.write(f"- **Draft path**: {ev.get('draft_path','')}\n\n")


def main() -> int:
    state = _read_sentinel()
    last_line = state.get("last_line_num", 0)

    if not PROPOSALS_LOG.exists():
        _write_sentinel({"last_line_num": last_line, "last_run_at": time.time()})
        print("[listener] no proposals log yet, exit 0")
        return 0

    new_events = []
    with PROPOSALS_LOG.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if i < last_line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("event_type") != "SELF_MOD_PROPOSAL":
            continue
        new_events.append(ev)
        _register_omission_tracked(ev)

    _update_inbox(new_events)
    _write_sentinel({
        "last_line_num": len(lines),
        "last_run_at": time.time(),
        "processed_this_run": len(new_events),
    })

    print(f"[listener] processed {len(new_events)} new AMENDMENT proposals "
          f"(total lines scanned: {len(lines) - last_line})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
