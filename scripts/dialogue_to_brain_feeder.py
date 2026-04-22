#!/usr/bin/env python3
"""
Dialogue → Brain Feeder (M-1 Survivability + M-2b 补脑 pipeline).

Milestone 7 (2026-04-21): 把 scripts/.logs/dialogue_contract.log 的
Board/Aiden 对话内容增量 ingest 到 6D brain, 让 dialogue 节点与现有
brain nodes 建立 co-activation edges. 这是补脑 pipeline 最后一条通道.

老大 2026-04-21 问 "补脑机制是随时都通吗" — 本 feeder + launchd 每
60s schedule 把 dialogue 通道 从 ❌ 不通 → ✅ 随时通.

Format (3 lines per entry):
    {ISO timestamp} | method=regex confidence={float}
      msg: {dialogue text or JSON}
      contract: {json}

Sentinel: scripts/.dialogue_to_brain_sentinel.json tracks last byte offset.

Usage:
    python3.11 scripts/dialogue_to_brain_feeder.py           # incremental
    python3.11 scripts/dialogue_to_brain_feeder.py --full    # re-ingest all
    python3.11 scripts/dialogue_to_brain_feeder.py --dry-run # parse no write
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
DIALOGUE_LOG = WORKSPACE_ROOT / "scripts/.logs/dialogue_contract.log"
BRAIN_DB = WORKSPACE_ROOT / "aiden_brain.db"
SENTINEL = WORKSPACE_ROOT / "scripts/.dialogue_to_brain_sentinel.json"

sys.path.insert(0, str(WORKSPACE_ROOT / "scripts"))

ENTRY_HEADER = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.]+)\s*\|\s*method=(?P<method>\S+)\s*confidence=(?P<conf>[\d.]+)"
)


def _read_sentinel() -> dict:
    if not SENTINEL.exists():
        return {"byte_offset": 0, "entries_ingested": 0}
    try:
        return json.loads(SENTINEL.read_text())
    except Exception:
        return {"byte_offset": 0, "entries_ingested": 0}


def _write_sentinel(data: dict):
    SENTINEL.write_text(json.dumps(data, indent=2))


def parse_entries(log_text: str) -> list:
    """Parse raw log text into [{ts, method, confidence, msg, contract}, ...]."""
    lines = log_text.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        m = ENTRY_HEADER.match(lines[i])
        if not m:
            i += 1
            continue
        ts = m.group("ts")
        method = m.group("method")
        try:
            confidence = float(m.group("conf"))
        except ValueError:
            confidence = 0.0
        msg = ""
        contract = "{}"
        if i + 1 < len(lines) and lines[i + 1].lstrip().startswith("msg:"):
            msg = lines[i + 1].split("msg:", 1)[1].strip()
        if i + 2 < len(lines) and lines[i + 2].lstrip().startswith("contract:"):
            contract = lines[i + 2].split("contract:", 1)[1].strip()
        entries.append({
            "ts": ts,
            "method": method,
            "confidence": confidence,
            "msg": msg,
            "contract": contract,
        })
        i += 3
    return entries


def _entry_to_node(entry: dict) -> tuple:
    """Return (node_id, name, content) for brain ingest."""
    ts = entry["ts"]
    node_id = f"dialogue/{ts}"
    # Name = first 50 chars of msg for quick read
    msg = entry["msg"]
    name = msg[:80] + ("..." if len(msg) > 80 else "")
    return node_id, name, msg


def feed_entries(entries: list, brain_db_path: str, dry_run: bool = False) -> dict:
    """Create dialogue/* nodes in brain.db, link to 'board' anchor."""
    if dry_run:
        return {"would_ingest": len(entries), "dry_run": True}

    try:
        from aiden_brain import add_node, add_edge  # noqa: F401
    except ImportError:
        # Fallback: direct sqlite
        add_node = None
        add_edge = None

    if add_node is None:
        # minimal direct-sqlite fallback
        import sqlite3
        conn = sqlite3.connect(brain_db_path)
        conn.execute("PRAGMA busy_timeout=5000")
        ingested = 0
        errors = 0
        BOARD_ANCHOR = "board"
        # ensure board anchor exists
        try:
            conn.execute("""INSERT OR IGNORE INTO nodes
                (node_id, name, file_path, created_at, updated_at, access_count)
                VALUES (?, ?, '', ?, ?, 0)""",
                (BOARD_ANCHOR, "Board (Haotian Liu)", time.time(), time.time()))
        except Exception:
            pass
        for e in entries:
            node_id, name, content = _entry_to_node(e)
            try:
                conn.execute("""INSERT OR IGNORE INTO nodes
                    (node_id, name, file_path, created_at, updated_at, access_count)
                    VALUES (?, ?, '', ?, ?, 0)""",
                    (node_id, name, time.time(), time.time()))
                # edge dialogue → board (co-activation anchor)
                conn.execute("""INSERT INTO edges
                    (source_id, target_id, edge_type, weight,
                     created_at, updated_at, co_activations)
                    VALUES (?, ?, 'dialogue_anchor', ?, ?, ?, 1)
                    ON CONFLICT(source_id, target_id) DO UPDATE SET
                        co_activations = co_activations + 1,
                        updated_at = excluded.updated_at""",
                    (node_id, BOARD_ANCHOR, e["confidence"], time.time(), time.time()))
                ingested += 1
            except Exception:
                errors += 1
        conn.commit()
        conn.close()
        return {"ingested": ingested, "errors": errors, "dry_run": False}

    # preferred path (add_node + add_edge API)
    ingested, errors = 0, 0
    for e in entries:
        node_id, name, content = _entry_to_node(e)
        try:
            add_node(node_id, name, file_path="")
            add_edge(node_id, "board", weight=e["confidence"])
            ingested += 1
        except Exception:
            errors += 1
    return {"ingested": ingested, "errors": errors, "dry_run": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true",
                    help="re-ingest all entries (ignore sentinel)")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and count, do not write brain")
    ap.add_argument("--log-path", default=str(DIALOGUE_LOG))
    ap.add_argument("--brain-db", default=str(BRAIN_DB))
    args = ap.parse_args()

    log_path = Path(args.log_path)
    if not log_path.exists():
        print(f"[feeder] log not found: {log_path}")
        return 0

    sentinel = _read_sentinel() if not args.full else {"byte_offset": 0, "entries_ingested": 0}
    file_size = log_path.stat().st_size
    if sentinel["byte_offset"] >= file_size and not args.full:
        print(f"[feeder] up to date (offset={sentinel['byte_offset']}, size={file_size})")
        return 0

    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(sentinel["byte_offset"])
        new_text = f.read()

    entries = parse_entries(new_text)
    result = feed_entries(entries, args.brain_db, dry_run=args.dry_run)

    if not args.dry_run:
        _write_sentinel({
            "byte_offset": file_size,
            "entries_ingested": sentinel["entries_ingested"] + result.get("ingested", 0),
            "last_run": time.time(),
        })

    print(f"[feeder] scanned={len(entries)} result={result} "
          f"sentinel→{file_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
