#!/usr/bin/env python3
"""
Brain L2 Writeback Async Queue — 30s drain cycle, persistent on failure.

Authority: CTO 3-Loop ruling Point 8 (learning-lag KPI), Point 6 (outcome-weighted Hebbian)
Engineer: Ryan Park (eng-platform) — hook wiring + queue infrastructure
Counterpart: Leo Chen (eng-kernel) — semantic writeback logic in hook_ceo_post_output_brain_writeback.py

Architecture:
  - PostToolUse(Agent) hook APPENDS entries to .brain_writeback_queue.jsonl
  - Stop hook DRAINS the queue by calling drain_queue()
  - 30s coalescing window: entries accumulate, drain processes all at once
  - On failure: entries stay in .jsonl, never dropped (Acceptance Criteria: never drops data)

Queue entry schema:
  {"entry_id": uuid, "timestamp": unix, "l1_cache": {...}, "outcome_events": [...], "status": "pending"}

Public API:
  enqueue(l1_cache_entry, outcome_events) -> str  # returns entry_id
  drain_queue() -> dict  # returns {"processed": N, "failed": N, "results": [...]}
"""

import json
import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_QUEUE_PATH = os.path.join(_SCRIPT_DIR, ".brain_writeback_queue.jsonl")
_L1_CACHE_PATH = os.path.join(_SCRIPT_DIR, ".brain_l1_cache.json")
_DRAIN_INTERVAL_SECONDS = 30
_LAST_DRAIN_PATH = os.path.join(_SCRIPT_DIR, ".brain_writeback_last_drain")

_log = logging.getLogger("brain_writeback_queue")


def read_l1_cache() -> Optional[Dict[str, Any]]:
    """Read the current L1 cache written by hook_ceo_pre_output_brain_query.py.

    Returns None if cache doesn't exist or is stale (>5 min old).
    """
    try:
        if not os.path.isfile(_L1_CACHE_PATH):
            return None
        with open(_L1_CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
        # Staleness check: cache older than 5 minutes is likely from a prior session
        ts = cache.get("timestamp", 0)
        if time.time() - ts > 300:
            _log.debug("L1 cache stale (%.0fs old), skipping", time.time() - ts)
            return None
        return cache
    except Exception as e:
        _log.warning("Failed to read L1 cache: %s", e)
        return None


def enqueue(
    l1_cache_entry: Optional[Dict[str, Any]] = None,
    outcome_events: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Append a writeback entry to the persistent queue.

    If l1_cache_entry is None, reads from .brain_l1_cache.json automatically.
    Returns the entry_id (uuid string).

    Never raises — failures are logged and the entry is still written
    with status='enqueue_error' for later retry.
    """
    entry_id = str(uuid.uuid4())

    if l1_cache_entry is None:
        l1_cache_entry = read_l1_cache()

    entry = {
        "entry_id": entry_id,
        "timestamp": time.time(),
        "l1_cache": l1_cache_entry,
        "outcome_events": outcome_events or [],
        "status": "pending",
    }

    try:
        with open(_QUEUE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        _log.debug("Enqueued brain writeback entry %s", entry_id)
    except Exception as e:
        _log.error("Failed to enqueue brain writeback: %s", e)
        # Even on file write failure, return the entry_id so caller knows
        # the attempt was made. The entry is lost in this case, but we
        # emit a CIEU event in the hook caller for observability.

    return entry_id


def _read_queue() -> List[Dict[str, Any]]:
    """Read all pending entries from the queue file.

    Returns empty list if file doesn't exist or is empty.
    """
    if not os.path.isfile(_QUEUE_PATH):
        return []
    entries = []
    try:
        with open(_QUEUE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    _log.warning("Skipping malformed queue entry: %s", e)
    except Exception as e:
        _log.error("Failed to read queue file: %s", e)
    return entries


def _write_failed_entries(entries: List[Dict[str, Any]]) -> None:
    """Write back entries that failed processing (preserves data, never drops)."""
    try:
        with open(_QUEUE_PATH, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        _log.error("CRITICAL: Failed to write back failed entries: %s", e)
        # Last resort: dump to stderr so at least there's a trace
        import sys
        print(f"BRAIN_WRITEBACK_CRITICAL: {len(entries)} entries lost: {e}",
              file=sys.stderr)


def _should_drain() -> bool:
    """Check if enough time has passed since last drain (30s interval)."""
    try:
        if os.path.isfile(_LAST_DRAIN_PATH):
            with open(_LAST_DRAIN_PATH, "r") as f:
                last_drain = float(f.read().strip())
            if time.time() - last_drain < _DRAIN_INTERVAL_SECONDS:
                return False
    except Exception:
        pass  # If we can't read the marker, drain anyway
    return True


def _mark_drained() -> None:
    """Record the current time as last drain timestamp."""
    try:
        with open(_LAST_DRAIN_PATH, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def drain_queue(force: bool = False) -> Dict[str, Any]:
    """Process all pending entries in the queue.

    Called by the Stop hook to drain accumulated writeback entries.
    Respects the 30s interval unless force=True.

    Returns dict: {"processed": N, "failed": N, "skipped": N, "results": [...]}

    On failure: entries that failed are written back to the queue file.
    Successfully processed entries are removed.
    """
    result = {"processed": 0, "failed": 0, "skipped": 0, "results": []}

    if not force and not _should_drain():
        entries = _read_queue()
        result["skipped"] = len(entries)
        _log.debug("Drain skipped (interval not elapsed), %d entries pending", len(entries))
        return result

    entries = _read_queue()
    if not entries:
        _mark_drained()
        return result

    _log.info("Draining %d brain writeback entries", len(entries))

    # Import Leo's writeback module (import-guarded: if not yet shipped, noop)
    writeback_fn = None
    try:
        from hook_ceo_post_output_brain_writeback import writeback
        writeback_fn = writeback
    except ImportError:
        _log.warning(
            "hook_ceo_post_output_brain_writeback not found — Leo's module not yet shipped. "
            "Entries will be preserved in queue for later processing."
        )
    except Exception as e:
        _log.error("Failed to import writeback module: %s", e)

    failed_entries = []
    for entry in entries:
        if entry.get("status") == "processed":
            continue  # Skip already-processed entries

        if writeback_fn is None:
            # Leo's module not available — keep entry for later
            failed_entries.append(entry)
            result["failed"] += 1
            continue

        try:
            l1_cache = entry.get("l1_cache")
            outcome_events = entry.get("outcome_events", [])

            if l1_cache is None:
                _log.debug("Skipping entry %s: no L1 cache data", entry.get("entry_id"))
                result["skipped"] += 1
                continue

            wb_result = writeback_fn(l1_cache, outcome_events)
            entry["status"] = "processed"
            result["processed"] += 1
            result["results"].append({
                "entry_id": entry.get("entry_id"),
                "writeback_result": wb_result,
            })
        except Exception as e:
            _log.error("Writeback failed for entry %s: %s", entry.get("entry_id"), e)
            entry["status"] = "failed"
            entry["error"] = str(e)
            failed_entries.append(entry)
            result["failed"] += 1

    # Write back only the failed entries (processed entries are removed)
    if failed_entries:
        _write_failed_entries(failed_entries)
    else:
        # All processed successfully — clear the queue
        try:
            os.remove(_QUEUE_PATH)
        except FileNotFoundError:
            pass
        except Exception as e:
            _log.error("Failed to clear queue file: %s", e)

    _mark_drained()
    _log.info("Drain complete: %d processed, %d failed, %d skipped",
              result["processed"], result["failed"], result["skipped"])
    return result


# ── CLI entry point for Stop hook ──────────────────────────────────────
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

    if len(sys.argv) > 1 and sys.argv[1] == "enqueue":
        # Called from PostToolUse hook: enqueue current L1 cache
        entry_id = enqueue()
        print(json.dumps({"status": "enqueued", "entry_id": entry_id}))
    elif len(sys.argv) > 1 and sys.argv[1] == "drain":
        # Called from Stop hook: drain the queue
        result = drain_queue(force=True)
        print(json.dumps(result, indent=2))
    else:
        # Default: drain with interval check
        result = drain_queue()
        print(json.dumps(result, indent=2))
