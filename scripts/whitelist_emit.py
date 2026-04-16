#!/usr/bin/env python3
"""
Whitelist Event Emitter — A018 Sync A (FAST PATH)
Reads hook event JSON from stdin, matches against whitelist, emits CIEU event.
Author: Ryan Park (eng-platform)
Date: 2026-04-13

Usage (from hook_client_labs.sh):
  echo "$PAYLOAD" | python3 scripts/whitelist_emit.py 2>/dev/null &

Fail-open: All errors are silent to avoid blocking the hook flow.
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Import whitelist matcher
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from whitelist_match import WhitelistMatcher
    from _cieu_helpers import _get_current_agent
except ImportError:
    # Silent fail-open: if matcher not available, exit cleanly
    sys.exit(0)


def emit_cieu_event(db_path: Path, event_type: str, data: dict):
    """Emit CIEU event to database. Fail-open on error."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cieu_events (
                timestamp,
                event_type,
                agent_id,
                action,
                context,
                intent,
                constraints,
                escalated,
                result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            event_type,
            _get_current_agent(),
            data.get("action", "whitelist_match"),
            json.dumps(data.get("context", {})),
            data.get("intent", ""),
            json.dumps(data.get("constraints", {})),
            0,  # not escalated
            data.get("result", "")
        ))

        conn.commit()
        conn.close()
    except Exception:
        # Silent fail-open
        pass


def main():
    """Main entry point."""
    try:
        # Read event payload from stdin
        payload = json.load(sys.stdin)

        # Initialize matcher
        whitelist_dir = Path(__file__).parent.parent / "governance" / "whitelist"
        if not whitelist_dir.exists():
            # No whitelist configured, silent exit
            sys.exit(0)

        matcher = WhitelistMatcher(whitelist_dir)

        # Try to match
        result = matcher.match_event(payload)

        # Determine CIEU database path
        company_root = Path(__file__).parent.parent
        cieu_db = company_root / ".ystar_cieu.db"

        if result:
            # WHITELIST_MATCH: Emit event with score and matched fields
            emit_cieu_event(
                db_path=cieu_db,
                event_type="WHITELIST_MATCH",
                data={
                    "action": "whitelist_match",
                    "context": {
                        "entry_id": result.entry_id,
                        "score": result.score,
                        "matched_fields": result.matched_fields,
                        "source_file": result.entry.source_file,
                        "who": result.entry.who,
                        "what": result.entry.what,
                        "task_type": result.entry.task_type,
                    },
                    "intent": f"Matched {result.entry_id} (score {result.score:.1f})",
                    "result": "match",
                }
            )
        else:
            # WHITELIST_DRIFT: Emit top-3 near-miss
            top_k = matcher.get_top_k_similar(payload, k=3)
            if top_k:
                emit_cieu_event(
                    db_path=cieu_db,
                    event_type="WHITELIST_DRIFT",
                    data={
                        "action": "whitelist_drift",
                        "context": {
                            "top_3": [
                                {
                                    "entry_id": m.entry_id,
                                    "score": m.score,
                                    "who": m.entry.who,
                                    "what": m.entry.what,
                                }
                                for m in top_k
                            ],
                            "threshold": matcher.THRESHOLD,
                        },
                        "intent": f"No match (top score {top_k[0].score:.1f} < {matcher.THRESHOLD})",
                        "result": "drift",
                    }
                )

    except Exception:
        # Silent fail-open: any error exits cleanly without blocking
        pass


if __name__ == "__main__":
    main()
