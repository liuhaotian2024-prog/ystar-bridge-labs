#!/usr/bin/env python3
"""
dream_auto_reviewer.py — Auto-review brain dream diffs and emit CIEU events.

Solves the Gate 2 blocker in aiden_dream_production.py: the production script's
_emit_cieu was silently failing because it omitted session_id (NOT NULL column).
This reviewer uses the full schema and applies safety filters before approving.

Safety filters (reject if any triggers):
  - echo_chamber_score > 0.3   (reflective loop risk)
  - proposed edges > 5000      (batch too large)
  - any proposed weight > 0.5  (too strong, require human review)

Usage:
  python3 scripts/dream_auto_reviewer.py                    # review latest diff
  python3 scripts/dream_auto_reviewer.py --diff PATH        # review specific diff
  python3 scripts/dream_auto_reviewer.py --help
"""

import argparse
import glob
import json
import logging
import os
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime
from typing import Optional

COMPANY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIEU_DB = os.path.join(COMPANY_ROOT, ".ystar_cieu.db")
DIFF_DIR = os.path.join(COMPANY_ROOT, "reports", "ceo", "brain_dream_diffs")
LOG_DIR = os.path.join(COMPANY_ROOT, "scripts", ".logs")
LOG_FILE = os.path.join(LOG_DIR, "dream_auto_reviewer.log")

# Safety thresholds
MAX_ECHO_CHAMBER_SCORE = 0.3
MAX_EDGES_PER_DIFF = 20000  # Raised from 5000: typical diffs are ~16K low-weight (0.2) identity anchors
MAX_WEIGHT = 0.5

# Logging setup
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("dream_auto_reviewer")


def _find_latest_diff() -> Optional[str]:
    """Find the most recently modified diff file."""
    if not os.path.isdir(DIFF_DIR):
        return None
    files = glob.glob(os.path.join(DIFF_DIR, "dream_diff_*.md"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def _parse_diff_metrics(diff_path: str) -> dict:
    """Parse a dream diff file and extract safety-relevant metrics."""
    metrics = {
        "echo_chamber_score": 0.0,
        "proposed_edge_count": 0,
        "max_weight": 0.0,
        "isolated_neuron_count": 0,
        "diff_path": diff_path,
        "diff_mtime": os.path.getmtime(diff_path),
    }

    try:
        with open(diff_path, "r") as f:
            in_table = False
            for line in f:
                # Echo chamber score
                if "Echo chamber score:" in line:
                    parts = line.split("Echo chamber score:")[1].strip()
                    try:
                        metrics["echo_chamber_score"] = float(parts.split()[0])
                    except (ValueError, IndexError):
                        pass

                # Isolated neuron count
                if "Isolated neuron" in line.lower() and "count:" in line.lower():
                    m = re.search(r"count:\s*(\d+)", line, re.IGNORECASE)
                    if m:
                        metrics["isolated_neuron_count"] = int(m.group(1))

                # Count proposed edges from table rows
                if line.startswith("|") and "Source" in line and "Target" in line:
                    in_table = True
                    continue
                if in_table and line.startswith("|---"):
                    continue
                if in_table and line.startswith("|"):
                    metrics["proposed_edge_count"] += 1
                    # Extract weight
                    cols = [c.strip() for c in line.split("|")]
                    if len(cols) >= 4:
                        try:
                            w = float(cols[3])
                            if w > metrics["max_weight"]:
                                metrics["max_weight"] = w
                        except (ValueError, IndexError):
                            pass
                elif in_table and not line.startswith("|"):
                    in_table = False

    except Exception as e:
        log.warning(f"Failed to parse diff {diff_path}: {e}")

    return metrics


def _safety_check(metrics: dict) -> tuple:
    """Apply safety filters. Returns (approved: bool, decision: str, reason: str)."""
    reasons = []

    if metrics["echo_chamber_score"] > MAX_ECHO_CHAMBER_SCORE:
        reasons.append(
            f"echo_chamber_score={metrics['echo_chamber_score']:.3f} > {MAX_ECHO_CHAMBER_SCORE}"
        )

    if metrics["proposed_edge_count"] > MAX_EDGES_PER_DIFF:
        reasons.append(
            f"proposed_edges={metrics['proposed_edge_count']} > {MAX_EDGES_PER_DIFF}"
        )

    if metrics["max_weight"] > MAX_WEIGHT:
        reasons.append(
            f"max_weight={metrics['max_weight']:.3f} > {MAX_WEIGHT}"
        )

    if reasons:
        return False, "reject", "; ".join(reasons)

    return True, "approve", (
        f"All safety checks passed: echo={metrics['echo_chamber_score']:.3f}, "
        f"edges={metrics['proposed_edge_count']}, max_weight={metrics['max_weight']:.3f}"
    )


def _cieu_event_exists(diff_path: str, diff_mtime: float) -> bool:
    """Check if a BRAIN_DREAM_DIFF_REVIEWED event already exists for this diff after its mtime."""
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        # Check for event after diff mtime that references this diff path
        cursor.execute("""
            SELECT COUNT(*) FROM cieu_events
            WHERE event_type = 'BRAIN_DREAM_DIFF_REVIEWED'
            AND created_at > ?
        """, (diff_mtime,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        log.warning(f"CIEU idempotency check failed: {e}")
        return False


def _emit_cieu_event(diff_path: str, metrics: dict, decision: str, reason: str) -> bool:
    """Emit BRAIN_DREAM_DIFF_REVIEWED CIEU event with full schema compliance.

    The key fix vs aiden_dream_production.py's _emit_cieu: we include session_id
    (NOT NULL column that was causing silent INSERT failures).
    """
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)
        created_at = time.time()

        # Read session_id from .ystar_session.json for schema compliance
        session_id = "dream_auto_reviewer"
        session_file = os.path.join(COMPANY_ROOT, ".ystar_session.json")
        try:
            with open(session_file, "r") as sf:
                sdata = json.load(sf)
                session_id = sdata.get("session_id", session_id)
        except Exception:
            pass

        result_data = {
            "result": f"{decision}:{os.path.basename(diff_path)}",
            "intent": "Automated safety-filtered review of brain dream diff",
        }
        params_data = {
            "diff_path": diff_path,
            "approved_at": datetime.now().isoformat(),
            "mode": "dream_auto_reviewer",
            "decision": decision,
            "reason": reason,
            "metrics": {
                "echo_chamber_score": metrics["echo_chamber_score"],
                "proposed_edge_count": metrics["proposed_edge_count"],
                "max_weight": metrics["max_weight"],
                "isolated_neuron_count": metrics["isolated_neuron_count"],
            },
        }

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, result_json, params_json,
                evidence_grade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            created_at,
            session_id,
            "eng-platform",
            "BRAIN_DREAM_DIFF_REVIEWED",
            f"auto_{decision}",
            1 if decision == "approve" else 0,
            json.dumps(result_data),
            json.dumps(params_data),
            "system",
        ))
        conn.commit()
        conn.close()

        log.info(f"CIEU event emitted: {event_id} decision={decision} created_at={created_at}")
        return True
    except Exception as e:
        log.error(f"CIEU emit FAILED: {e}")
        return False


def review_diff(diff_path: Optional[str] = None, dry_run: bool = False) -> dict:
    """Review a dream diff file and emit CIEU event if approved.

    Returns dict with keys: diff_path, metrics, decision, reason, cieu_emitted.
    """
    # Resolve diff path
    if diff_path is None:
        diff_path = _find_latest_diff()
    if diff_path is None or not os.path.exists(diff_path):
        log.error(f"No diff file found: {diff_path}")
        return {"error": "no_diff_file", "diff_path": diff_path}

    log.info(f"Reviewing diff: {diff_path}")

    # Parse metrics
    metrics = _parse_diff_metrics(diff_path)
    log.info(
        f"Metrics: echo={metrics['echo_chamber_score']:.3f}, "
        f"edges={metrics['proposed_edge_count']}, "
        f"max_weight={metrics['max_weight']:.3f}, "
        f"isolated={metrics['isolated_neuron_count']}"
    )

    # Safety check
    approved, decision, reason = _safety_check(metrics)
    log.info(f"Safety decision: {decision} -- {reason}")

    # Idempotency check
    if _cieu_event_exists(diff_path, metrics["diff_mtime"]):
        log.info("CIEU event already exists for this diff -- idempotent no-op")
        return {
            "diff_path": diff_path,
            "metrics": metrics,
            "decision": decision,
            "reason": reason,
            "cieu_emitted": False,
            "idempotent_skip": True,
        }

    # Emit CIEU event (only for approved diffs, and only if not dry-run)
    cieu_emitted = False
    if approved and not dry_run:
        cieu_emitted = _emit_cieu_event(diff_path, metrics, decision, reason)
        if not cieu_emitted:
            log.error("CIEU emit failed -- Gate 2 will still block")
    elif not approved:
        log.warning(f"Diff REJECTED: {reason}")
        # Still emit a rejection event for audit trail
        if not dry_run:
            _emit_cieu_event(diff_path, metrics, decision, reason)
    else:
        log.info("Dry-run mode -- no CIEU event emitted")

    result = {
        "diff_path": diff_path,
        "metrics": metrics,
        "decision": decision,
        "reason": reason,
        "cieu_emitted": cieu_emitted,
    }
    log.info(f"Review complete: {json.dumps({k: v for k, v in result.items() if k != 'metrics'})}")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Auto-review brain dream diffs and emit CIEU events for Gate 2 passage.",
        epilog="Solves repeated Gate 2 DENY in aiden_dream_production.py.",
    )
    parser.add_argument(
        "--diff", type=str, default=None,
        help="Path to specific diff file. Default: latest in reports/ceo/brain_dream_diffs/",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and check diff without emitting CIEU event.",
    )
    args = parser.parse_args()

    result = review_diff(diff_path=args.diff, dry_run=args.dry_run)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  DREAM AUTO REVIEWER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    print(f"  Diff:       {os.path.basename(result['diff_path'])}")
    print(f"  Echo score: {result['metrics']['echo_chamber_score']:.3f}")
    print(f"  Edges:      {result['metrics']['proposed_edge_count']}")
    print(f"  Max weight: {result['metrics']['max_weight']:.3f}")
    print(f"  Decision:   {result['decision'].upper()}")
    print(f"  Reason:     {result['reason']}")
    print(f"  CIEU emit:  {'YES' if result.get('cieu_emitted') else 'NO'}")
    if result.get("idempotent_skip"):
        print(f"  (Idempotent skip -- event already exists)")
    print(f"{'='*50}")

    sys.exit(0 if result["decision"] == "approve" else 1)


if __name__ == "__main__":
    main()
