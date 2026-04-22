#!/usr/bin/env python3
"""Reflexion OmissionEngine Poller — external callback for tracked_entity overdue.

Rather than modify Y-star-gov omission_engine.py core (product scope),
this poller reads CIEU events for OMISSION_OVERDUE or similar tracked_entity
failure events, feeds each into ReflexionGenerator, writes reflection brain nodes.

Runs periodically via launchd StartInterval. Idempotent via sentinel.

M-tag: M-2b (OmissionEngine failures become learning signal, not silent drops)
     + M-3 (self-improvement infrastructure end-to-end LIVE).
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE / ".ystar_cieu_omission.db"  # omission-specific DB
CIEU_MAIN_DB = WORKSPACE / ".ystar_cieu.db"      # main CIEU DB (fallback)
SENTINEL = WORKSPACE / "scripts" / ".reflexion_poller_sentinel.json"

sys.path.insert(0, str(WORKSPACE / "scripts"))


OVERDUE_EVENT_TYPES = (
    "OMISSION_OVERDUE", "TRACKED_ENTITY_OVERDUE", "OBLIGATION_BREACH",
    "RT_NONZERO", "DISPATCH_OVERDUE",
)


def _read_sentinel() -> dict:
    if SENTINEL.exists():
        try:
            return json.loads(SENTINEL.read_text())
        except Exception:
            pass
    return {"last_event_id": "", "last_run_at": 0, "processed_total": 0}


def _write_sentinel(state: dict) -> None:
    SENTINEL.write_text(json.dumps(state, indent=2))


def _query_overdue_events(db_path: Path, since_event_id: str = "") -> list[dict]:
    """Query CIEU table for overdue events since last sentinel."""
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        # Defensive schema: table name may vary. Try common names.
        table_name = None
        for candidate in ("cieu_events", "events", "cieu"):
            try:
                conn.execute(f"SELECT 1 FROM {candidate} LIMIT 1").fetchone()
                table_name = candidate
                break
            except sqlite3.OperationalError:
                continue
        if not table_name:
            conn.close()
            return []

        # Detect columns
        cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")}
        event_type_col = "event_type" if "event_type" in cols else ("type" if "type" in cols else None)
        id_col = "event_id" if "event_id" in cols else "id"
        if not event_type_col:
            conn.close()
            return []

        placeholders = ",".join("?" * len(OVERDUE_EVENT_TYPES))
        query = (
            f"SELECT {id_col}, {event_type_col}, * FROM {table_name} "
            f"WHERE {event_type_col} IN ({placeholders})"
        )
        params = list(OVERDUE_EVENT_TYPES)
        if since_event_id:
            query += f" AND {id_col} > ?"
            params.append(since_event_id)
        query += f" ORDER BY {id_col} ASC LIMIT 50"

        rows = conn.execute(query, params).fetchall()
        col_names = [d[0] for d in conn.execute(f"SELECT * FROM {table_name} LIMIT 1").description]
        conn.close()

        result = []
        for row in rows:
            d = dict(zip(col_names, row[2:]))  # skip duplicate id/type from SELECT
            d["event_id"] = row[0]
            d["event_type"] = row[1]
            result.append(d)
        return result
    except Exception as e:
        print(f"[poller] query error ({db_path}): {e}")
        return []


def _generate_reflection_for_event(event: dict) -> bool:
    """Feed event into ReflexionGenerator, write brain node, return success."""
    try:
        from reflexion_generator import ReflexionGenerator, _llm_via_cluster_daemon
        gen = ReflexionGenerator(llm_call_fn=_llm_via_cluster_daemon)
        failure_context = json.dumps(event, default=str)[:2000]
        rt_value = event.get("rt_value") or event.get("rt") or 1
        r = gen.generate_reflection(
            cieu_event_id=str(event["event_id"]),
            rt_value=int(rt_value) if isinstance(rt_value, (int, str)) and str(rt_value).isdigit() else 1,
            failure_context=failure_context,
        )
        return r.reflection_id > 0
    except Exception as e:
        print(f"[poller] reflection generation failed for event {event.get('event_id','?')}: {e}")
        return False


def main() -> int:
    state = _read_sentinel()
    last_id = state.get("last_event_id", "")

    all_events = []
    for db in (CIEU_DB, CIEU_MAIN_DB):
        all_events.extend(_query_overdue_events(db, last_id))

    # Dedup by event_id
    seen = set()
    unique_events = []
    for ev in all_events:
        eid = str(ev.get("event_id", ""))
        if eid and eid not in seen:
            seen.add(eid)
            unique_events.append(ev)

    processed = 0
    new_last_id = last_id
    for ev in unique_events:
        if _generate_reflection_for_event(ev):
            processed += 1
            new_last_id = max(new_last_id, str(ev.get("event_id", "")))

    _write_sentinel({
        "last_event_id": new_last_id,
        "last_run_at": time.time(),
        "processed_total": state.get("processed_total", 0) + processed,
        "processed_this_run": processed,
    })

    print(f"[poller] processed {processed}/{len(unique_events)} overdue events into reflections "
          f"(total lifetime: {state.get('processed_total', 0) + processed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
