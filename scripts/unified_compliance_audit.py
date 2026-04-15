import sqlite3
import os
from pathlib import Path
from typing import Any

def query_cieu_5tuple(agent_ids: list[str], start: float, end: float) -> dict[str, Any]:
    """Dimension 1: Check CIEU events with complete 5-tuple fields.

    Graded scoring (relaxed because result_json not yet implemented in hook):
    - Full 5-tuple (params + result + decision + violations + drift) → 100
    - 4-tuple (params + decision + violations + event_type) → 75
    - 3-tuple (params + decision + event_type) → 50
    - Basic (decision + event_type) → 25
    """
    if not CIEU_DB.exists():
        return {"score": None, "reason": "CIEU DB not found"}

    try:
        db = sqlite3.connect(str(CIEU_DB))
        placeholders = ",".join("?" * len(agent_ids))

        total = db.execute(
            f"SELECT COUNT(*) FROM cieu_events WHERE agent_id IN ({placeholders}) "
            f"AND created_at >= ? AND created_at < ?",
            (*agent_ids, start, end)
        ).fetchone()[0]

        if total == 0:
            return {"score": None, "reason": "no CIEU events in date range"}

        # Full 5-tuple (all fields populated)
        full = db.execute(
            f"SELECT COUNT(*) FROM cieu_events WHERE agent_id IN ({placeholders}) "
            f"AND created_at >= ? AND created_at < ? "
            f"AND params_json IS NOT NULL AND params_json != '' "
            f"AND result_json IS NOT NULL AND result_json != '' "
            f"AND decision IS NOT NULL AND decision != '' "
            f"AND violations IS NOT NULL "
            f"AND drift_details IS NOT NULL",
            (*agent_ids, start, end)
        ).fetchone()[0]

        # 4-tuple (params + decision + violations + event_type)
        quad = db.execute(
            f"SELECT COUNT(*) FROM cieu_events WHERE agent_id IN ({placeholders}) "
            f"AND created_at >= ? AND created_at < ? "
            f"AND params_json IS NOT NULL AND params_json != '' "
            f"AND decision IS NOT NULL AND decision != '' "
            f"AND violations IS NOT NULL "
            f"AND event_type IS NOT NULL AND event_type != ''",
            (*agent_ids, start, end)
        ).fetchone()[0]

        # 3-tuple (params + decision + event_type)
        triple = db.execute(
            f"SELECT COUNT(*) FROM cieu_events WHERE agent_id IN ({placeholders}) "
            f"AND created_at >= ? AND created_at < ? "
            f"AND params_json IS NOT NULL AND params_json != '' "
            f"AND decision IS NOT NULL AND decision != '' "
            f"AND event_type IS NOT NULL AND event_type != ''",
            (*agent_ids, start, end)
        ).fetchone()[0]

        # Basic (decision + event_type)
        basic = db.execute(
            f"SELECT COUNT(*) FROM cieu_events WHERE agent_id IN ({placeholders}) "
            f"AND created_at >= ? AND created_at < ? "
            f"AND decision IS NOT NULL AND decision != '' "
            f"AND event_type IS NOT NULL AND event_type != ''",
            (*agent_ids, start, end)
        ).fetchone()[0]

        db.close()

        # Weighted score
        score = (
            (full * 100 + (quad - full) * 75 + (triple - quad) * 50 + (basic - triple) * 25)
            / total
        ) if total > 0 else 0

        return {
            "score": round(score, 1),
            "total": total,
            "full_5tuple": full,
            "quad_4tuple": quad,
            "triple_3tuple": triple,
            "basic_2tuple": basic,
        }

    except Exception as e:
        return {"score": None, "reason": f"query error: {e}"}