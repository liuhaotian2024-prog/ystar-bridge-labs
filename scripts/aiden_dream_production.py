#!/usr/bin/env python3
"""
aiden_dream_production.py — Production sleep cycle for Aiden brain consolidation.

Promoted from dryrun mode per CZL-BRAIN-FRONTIER-1-AIDEN-DREAM-PROMOTE (2026-04-22).
Runs the full dream cycle: dry-run -> auto-approve -> commit.

Unlike the dryrun plist (which only generated diff proposals without committing),
this production wrapper completes the full consolidation pipeline:
  1. Generate fresh diff via aiden_dream.py --dry-run
  2. Auto-approve the diff (emit BRAIN_DREAM_DIFF_REVIEWED CIEU event)
  3. Apply changes via aiden_dream.py --commit

Safety: echo_chamber_score > 0.8 triggers skip (prevents runaway self-reinforcement).
Fail-open: Gemma endpoint not required (aiden_dream does not depend on Gemma).
"""

import os
import sys
import json
import time
import sqlite3
import uuid
from datetime import datetime

COMPANY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(COMPANY_ROOT, "scripts"))

CIEU_DB = os.path.join(COMPANY_ROOT, ".ystar_cieu.db")
DIFF_DIR = os.path.join(COMPANY_ROOT, "reports", "ceo", "brain_dream_diffs")
BRAIN_DB = os.path.join(COMPANY_ROOT, "aiden_brain.db")

ECHO_CHAMBER_THRESHOLD = 0.8  # Skip commit if echo score exceeds this


def _emit_cieu(event_type: str, data: dict):
    """Emit CIEU event. Fail-open."""
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, event_type, agent_id,
                decision, result_json, params_json, evidence_grade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            int(time.time() * 1_000_000),
            time.time(),
            event_type,
            "eng-platform",
            data.get("action", "dream_production"),
            json.dumps({"result": data.get("result", ""), "intent": data.get("intent", "")}),
            json.dumps(data.get("context", {})),
            "system",
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"  [WARN] CIEU emit failed: {e}", file=sys.stderr)
        return False


def _get_node_count() -> int:
    """Get current brain.db node count."""
    try:
        conn = sqlite3.connect(BRAIN_DB)
        count = conn.execute("SELECT count(*) FROM nodes").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return -1


def _get_edge_count() -> int:
    """Get current brain.db edge count."""
    try:
        conn = sqlite3.connect(BRAIN_DB)
        count = conn.execute("SELECT count(*) FROM edges").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return -1


def _extract_echo_score_from_diff(diff_path: str) -> float:
    """Extract echo chamber score from diff report. Returns 0.0 on parse failure."""
    try:
        with open(diff_path, "r") as f:
            for line in f:
                if "Echo chamber score:" in line:
                    # Format: "- Echo chamber score: 0.XXX (...)"
                    parts = line.split("Echo chamber score:")[1].strip()
                    return float(parts.split()[0])
    except Exception:
        pass
    return 0.0


def _auto_approve_latest():
    """Emit BRAIN_DREAM_DIFF_REVIEWED for the latest diff. Returns diff_path or None."""
    import glob as glob_mod
    if not os.path.isdir(DIFF_DIR):
        return None
    files = sorted(glob_mod.glob(os.path.join(DIFF_DIR, "dream_diff_*.md")))
    if not files:
        return None
    diff_path = max(files, key=os.path.getmtime)

    _emit_cieu("BRAIN_DREAM_DIFF_REVIEWED", {
        "action": "auto_approve_production",
        "intent": "Production auto-approve of brain dream diff (promoted from dryrun)",
        "context": {
            "diff_path": diff_path,
            "approved_at": datetime.now().isoformat(),
            "mode": "production_auto",
        },
        "result": f"auto_approved:{diff_path}",
    })
    return diff_path


def run_production_cycle():
    """Execute the full production dream cycle."""
    print("=" * 60)
    print("  AIDEN DREAM PRODUCTION CYCLE")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Mode: PRODUCTION (changes WILL be applied)")
    print("=" * 60)

    # Baseline
    nodes_before = _get_node_count()
    edges_before = _get_edge_count()
    print(f"\n  Baseline: {nodes_before} nodes, {edges_before} edges")

    # Step 1: Generate fresh diff
    print("\n--- Step 1: Generate diff (dry-run) ---")
    from aiden_dream import dry_run as dream_dry_run
    diff_path = dream_dry_run(pattern_filter="nrem")
    if not diff_path:
        print("  ERROR: dry_run returned no diff path. Aborting.")
        _emit_cieu("AIDEN_DREAM_PRODUCTION_FAILED", {
            "action": "production_cycle_failed",
            "intent": "Full production dream cycle",
            "context": {"step": "dry_run", "reason": "no diff generated"},
            "result": "failed:no_diff",
        })
        return False

    # Step 1b: Check echo chamber score
    echo_score = _extract_echo_score_from_diff(diff_path)
    print(f"\n  Echo chamber score: {echo_score}")
    if echo_score > ECHO_CHAMBER_THRESHOLD:
        print(f"  SKIP: Echo chamber score {echo_score} > threshold {ECHO_CHAMBER_THRESHOLD}")
        print("  Changes too self-reinforcing. Skipping commit to prevent echo chamber.")
        _emit_cieu("AIDEN_DREAM_PRODUCTION_SKIPPED", {
            "action": "echo_chamber_guard",
            "intent": "Prevent runaway self-reinforcement",
            "context": {"echo_score": echo_score, "threshold": ECHO_CHAMBER_THRESHOLD},
            "result": f"skipped:echo_score={echo_score}",
        })
        return False

    # Step 2: Auto-approve
    print("\n--- Step 2: Auto-approve ---")
    approved_path = _auto_approve_latest()
    if not approved_path:
        print("  ERROR: No diff to approve. Aborting.")
        return False
    print(f"  Auto-approved: {approved_path}")

    # Step 3: Commit changes
    print("\n--- Step 3: Commit changes ---")
    from aiden_dream import commit_dream
    success = commit_dream()

    # Results
    nodes_after = _get_node_count()
    edges_after = _get_edge_count()
    node_delta = nodes_after - nodes_before
    edge_delta = edges_after - edges_before

    print(f"\n  Result: {'COMMITTED' if success else 'FAILED'}")
    print(f"  Nodes: {nodes_before} -> {nodes_after} (delta: {node_delta:+d})")
    print(f"  Edges: {edges_before} -> {edges_after} (delta: {edge_delta:+d})")

    _emit_cieu("AIDEN_DREAM_PRODUCTION_COMPLETE", {
        "action": "production_cycle_complete",
        "intent": "Full production dream cycle completed",
        "context": {
            "diff_path": diff_path,
            "echo_score": echo_score,
            "nodes_before": nodes_before,
            "nodes_after": nodes_after,
            "edges_before": edges_before,
            "edges_after": edges_after,
            "committed": success,
        },
        "result": f"{'committed' if success else 'failed'}:nodes_delta={node_delta}:edges_delta={edge_delta}",
    })

    print("\n" + "=" * 60)
    print(f"  Production cycle {'COMPLETE' if success else 'FAILED'}")
    print("=" * 60)
    return success


if __name__ == "__main__":
    success = run_production_cycle()
    sys.exit(0 if success else 1)
