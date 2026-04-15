"""
gov_mcp.health — Session Health Score computation

Computes governance health score based on CIEU database records.
Used by dashboard P0-A health check.
"""

from typing import Dict, Any, Optional
import sqlite3
from pathlib import Path


def compute_health_score(
    db_path: Optional[str] = None,
    lookback_hours: int = 24
) -> Dict[str, Any]:
    """
    Compute session health score from CIEU database.

    Health score is computed as:
    (allow_count / total_records) * 100

    Where:
    - allow_count: number of records with decision='allow' or event_type in allowed set
    - total_records: all CIEU records in lookback window

    Args:
        db_path: Path to CIEU database (defaults to .ystar_cieu.db in current dir)
        lookback_hours: Hours of history to analyze (default 24)

    Returns:
        Dict with keys:
        - score: int (0-100) health score
        - total_records: int, total CIEU records analyzed
        - allow_count: int, records that passed governance
        - block_count: int, records that were blocked
        - lookback_hours: int, time window analyzed
    """
    if db_path is None:
        db_path = str(Path.cwd() / ".ystar_cieu.db")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query CIEU records from last N hours
        query = """
        SELECT event_type, decision, passed
        FROM cieu_events
        WHERE created_at >= unixepoch('now', '-{} hours')
        ORDER BY created_at DESC
        """.format(lookback_hours)

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        total_records = len(rows)

        # If no records, return default healthy score
        if total_records == 0:
            return {
                "score": 100,
                "total_records": 0,
                "allow_count": 0,
                "block_count": 0,
                "lookback_hours": lookback_hours,
                "status": "no_data"
            }

        # Count allows vs blocks
        # decision='allow' OR passed=1 counts as healthy
        # decision='deny' OR passed=0 counts as unhealthy

        allow_count = 0
        for event_type, decision, passed in rows:
            if decision == 'allow' or passed == 1:
                allow_count += 1

        block_count = total_records - allow_count

        # Compute score
        score = int((allow_count / total_records) * 100)

        # Determine status
        if score >= 90:
            status = "healthy"
        elif score >= 70:
            status = "stable"
        elif score >= 50:
            status = "degraded"
        else:
            status = "critical"

        return {
            "score": score,
            "total_records": total_records,
            "allow_count": allow_count,
            "block_count": block_count,
            "lookback_hours": lookback_hours,
            "status": status
        }

    except sqlite3.OperationalError as e:
        # Database doesn't exist or table doesn't exist
        return {
            "score": 0,
            "total_records": 0,
            "allow_count": 0,
            "block_count": 0,
            "lookback_hours": lookback_hours,
            "status": "no_database",
            "error": str(e)
        }
    except Exception as e:
        # Other errors
        return {
            "score": 0,
            "total_records": 0,
            "allow_count": 0,
            "block_count": 0,
            "lookback_hours": lookback_hours,
            "status": "error",
            "error": str(e)
        }
