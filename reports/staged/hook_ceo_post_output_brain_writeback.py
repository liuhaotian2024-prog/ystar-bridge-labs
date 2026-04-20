# Audience: Ryan-Platform (hook wiring integration) + CTO Ethan (architectural review)
# Research basis: CTO ruling CZL-BRAIN-3LOOP-FINAL Point 6 (outcome-weighted Hebbian); CEO v2 Section 3.3 (asymmetric lr); Ethan Q6 provenance guard; aiden_brain.py hebbian_update() lines 187-210
# Synthesis: L2 write-back computes per-node relevance from L1 cache + outcome events, then applies signed Hebbian updates with asymmetric learning rates (pos=0.10, neg=0.15) and provenance tagging to prevent self-referential training
# Purpose: Enable Ryan to wire this module into PostToolUse/Stop hooks; close the L1->decision->L2 feedback loop in the 3-loop brain architecture
#!/usr/bin/env python3
"""
L2 Outcome-Weighted Hebbian Write-Back Module.

Authority: CTO ruling CZL-BRAIN-3LOOP-FINAL Point 6 (outcome-weighted Hebbian
is PRIMARY defense); CEO v2 consolidation Section 3.3; Ethan Q6 provenance guard.

Purpose: After a CEO decision (tool calls complete), evaluate whether the brain
nodes that fired during L1 pre-query contributed to a good or bad outcome.
Reinforce good-outcome co-activations (Hebbian strengthen), decay bad-outcome
co-activations (Hebbian weaken). Asymmetric learning rates: positive=0.10,
negative=0.15 (errors are rarer, higher-value signal).

Public API:
    writeback(l1_cache_entry, outcome_events) -> dict

Integration:
    Ryan wires this into PostToolUse (queue-append) and Stop (drain) hooks.
    This module contains only the semantic logic -- no hook plumbing.

Constraints:
    - Never raise to parent -- all errors caught, CIEU event emitted, return dict
    - provenance='system:brain' on all activation_log entries (Ethan Q6)
    - Warmup gate: skip Hebbian if activation_log < 5000 rows (CTO ruling Point 9)
    - Within-session scope only (CTO ruling Point 10)
"""

import os
import sqlite3
import time
import json
import re
from typing import Any, Dict, List, Optional

# ── Constants ──────────────────────────────────────────────────────────

OUTCOME_WINDOW_SECONDS = 900  # 15 minutes (CTO ruling Point 6 revision)
POSITIVE_LR = 0.10            # Positive learning rate
NEGATIVE_LR = 0.15            # Negative learning rate (asymmetric, CEO v2 spec)
WARMUP_THRESHOLD = 5000       # Minimum activation_log rows before Hebbian (CTO Point 9)
RELEVANCE_CITED = 1.0         # Node explicitly cited in outcome
RELEVANCE_KEYWORD = 0.6       # Node hint terms match outcome events
RELEVANCE_BACKGROUND = 0.3    # Node was in top-k but no direct match

# Negative outcome markers -- events containing these indicate bad outcome
NEGATIVE_MARKERS = frozenset({
    'CROBA', 'croba', 'violation', 'VIOLATION', 'DENY', 'deny',
    'BLOCKED', 'blocked', 'DRIFT', 'drift_detected',
    'BOUNDARY_VIOLATION', 'SCOPE_VIOLATION',
})

# ── Path Resolution ───────────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_DEFAULT_BRAIN_DB = os.path.join(_REPO_ROOT, "aiden_brain.db")
_DEFAULT_CIEU_DB = os.path.join(_REPO_ROOT, ".ystar_cieu.db")


# ── CIEU Event Emission ──────────────────────────────────────────────

def _emit_cieu(event_type: str, details: Dict[str, Any],
               cieu_db_path: Optional[str] = None) -> Optional[str]:
    """Emit a CIEU event with system:brain provenance. Returns event_id or None."""
    if cieu_db_path is None:
        cieu_db_path = _DEFAULT_CIEU_DB
    try:
        if not os.path.isfile(cieu_db_path):
            return None
        conn = sqlite3.connect(cieu_db_path)
        event_id = f"brain_wb_{int(time.time()*1000)}"
        conn.execute(
            """INSERT OR IGNORE INTO cieu_events
               (event_id, event_type, agent_id, decision, details, created_at, provenance)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (event_id, event_type, 'system:brain', 'allow',
             json.dumps(details), time.time(), 'system:brain')
        )
        conn.commit()
        conn.close()
        return event_id
    except Exception:
        return None


# ── Relevance Computation ────────────────────────────────────────────

def _compute_node_relevance(node: Dict[str, Any],
                            outcome_events: List[Dict[str, Any]]) -> float:
    """Compute relevance score for a single node given outcome events.

    Returns:
        1.0 if node_id appears explicitly in any outcome event tool_results
        0.6 if node hint terms appear in outcome event text
        0.3 otherwise (background -- node was in top-k but no match)
    """
    node_id = node.get("node_id", "")
    hint = node.get("hint", "")

    # Check for explicit citation (node_id in tool_results)
    for event in outcome_events:
        event_text = json.dumps(event) if isinstance(event, dict) else str(event)
        if node_id and node_id in event_text:
            return RELEVANCE_CITED

    # Check for keyword match (hint terms in event text)
    if hint:
        # Extract meaningful words from hint (>= 4 chars to avoid noise)
        hint_terms = [w.lower() for w in re.findall(r'\w+', hint) if len(w) >= 4]
        if hint_terms:
            for event in outcome_events:
                event_text = (json.dumps(event).lower() if isinstance(event, dict)
                              else str(event).lower())
                matches = sum(1 for term in hint_terms if term in event_text)
                if matches >= 1:
                    return RELEVANCE_KEYWORD

    return RELEVANCE_BACKGROUND


def _determine_outcome_sign(outcome_events: List[Dict[str, Any]]) -> int:
    """Determine whether the outcome is positive (+1) or negative (-1).

    If ANY outcome event contains CROBA/violation/DENY markers, the outcome
    is negative. Otherwise positive.

    Returns: +1 or -1
    """
    for event in outcome_events:
        event_text = json.dumps(event) if isinstance(event, dict) else str(event)
        for marker in NEGATIVE_MARKERS:
            if marker in event_text:
                return -1
    return 1


# ── Warmup Gate ──────────────────────────────────────────────────────

def _check_warmup(brain_db_path: str) -> bool:
    """Check if activation_log has >= WARMUP_THRESHOLD rows.

    Returns True if warmed up (Hebbian allowed), False if still warming up.
    """
    try:
        conn = sqlite3.connect(brain_db_path)
        row = conn.execute("SELECT count(*) FROM activation_log").fetchone()
        conn.close()
        return (row[0] if row else 0) >= WARMUP_THRESHOLD
    except Exception:
        return False


# ── Core Write-Back ──────────────────────────────────────────────────

def writeback(l1_cache_entry: Dict[str, Any],
              outcome_events: List[Dict[str, Any]],
              brain_db_path: Optional[str] = None,
              cieu_db_path: Optional[str] = None) -> Dict[str, Any]:
    """L2 outcome-weighted Hebbian write-back.

    Args:
        l1_cache_entry: {
            "query_id": str,
            "timestamp": float,
            "top_k": [{"node_id": str, "distance": float, "hint": str}, ...]
        }
        outcome_events: list of CIEU events within OUTCOME_WINDOW_SECONDS
                        after l1 query. Each is a dict with at least
                        event_type, decision, details, agent_id fields.

    Returns:
        {
            "applied_updates": [{"node_a", "node_b", "delta", "lr_used"}, ...],
            "cieu_event_ids": [str, ...],
            "error": str or None,
            "warmup_pending": bool,
            "outcome_sign": int,  # +1 or -1
            "nodes_accessed": [str, ...],
        }
    """
    if brain_db_path is None:
        brain_db_path = _DEFAULT_BRAIN_DB
    if cieu_db_path is None:
        cieu_db_path = _DEFAULT_CIEU_DB

    result = {
        "applied_updates": [],
        "cieu_event_ids": [],
        "error": None,
        "warmup_pending": False,
        "outcome_sign": 0,
        "nodes_accessed": [],
    }

    try:
        top_k = l1_cache_entry.get("top_k", [])
        if not top_k:
            return result

        # ── Step 1: Compute per-node relevance ──
        relevances = {}
        for node in top_k:
            node_id = node.get("node_id", "")
            if not node_id:
                continue
            relevances[node_id] = _compute_node_relevance(node, outcome_events)

        # ── Step 2: Determine outcome sign ──
        sign = _determine_outcome_sign(outcome_events)
        result["outcome_sign"] = sign
        lr = NEGATIVE_LR if sign < 0 else POSITIVE_LR

        # ── Step 3: Increment access_count for each fired node ──
        try:
            conn = sqlite3.connect(brain_db_path)
            now = time.time()
            for node_id in relevances:
                conn.execute(
                    "UPDATE nodes SET access_count = access_count + 1, "
                    "last_accessed = ? WHERE id = ?",
                    (now, node_id)
                )
                result["nodes_accessed"].append(node_id)
            conn.commit()
            conn.close()
        except Exception as e:
            eid = _emit_cieu("BRAIN_WRITEBACK_FAILED",
                             {"stage": "access_count", "error": str(e)},
                             cieu_db_path)
            if eid:
                result["cieu_event_ids"].append(eid)
            result["error"] = f"access_count update failed: {e}"
            return result

        # ── Step 4: Write activation_log with provenance='system:brain' ──
        try:
            conn = sqlite3.connect(brain_db_path)
            query_id = l1_cache_entry.get("query_id", f"wb_{int(time.time()*1000)}")
            for node_id, rel in relevances.items():
                conn.execute(
                    """INSERT INTO activation_log
                       (node_id, query_text, activation_score, timestamp, provenance)
                       VALUES (?, ?, ?, ?, ?)""",
                    (node_id, f"L2_writeback:{query_id}",
                     rel * sign, now, 'system:brain')
                )
            conn.commit()
            conn.close()
        except Exception as e:
            eid = _emit_cieu("BRAIN_WRITEBACK_FAILED",
                             {"stage": "activation_log", "error": str(e)},
                             cieu_db_path)
            if eid:
                result["cieu_event_ids"].append(eid)
            result["error"] = f"activation_log write failed: {e}"
            return result

        # ── Step 5: Check warmup gate ──
        if not _check_warmup(brain_db_path):
            result["warmup_pending"] = True
            eid = _emit_cieu("BRAIN_WARMUP_PENDING",
                             {"activation_log_count": "< threshold",
                              "threshold": WARMUP_THRESHOLD,
                              "query_id": l1_cache_entry.get("query_id", "")},
                             cieu_db_path)
            if eid:
                result["cieu_event_ids"].append(eid)
            # Skip Hebbian but activation_log was still written (bootstrap)
            return result

        # ── Step 6: Hebbian update for co-activated pairs ──
        # Only update pairs where both nodes have relevance > RELEVANCE_BACKGROUND
        fired_nodes = [nid for nid, rel in relevances.items()
                       if rel > RELEVANCE_BACKGROUND]

        if len(fired_nodes) < 2:
            # Need at least 2 nodes for co-activation
            event_type = ("BRAIN_HEBBIAN_UPDATE_POSITIVE" if sign > 0
                          else "BRAIN_HEBBIAN_DECAY")
            eid = _emit_cieu(event_type,
                             {"query_id": l1_cache_entry.get("query_id", ""),
                              "sign": sign, "lr": lr,
                              "fired_nodes": len(fired_nodes),
                              "skipped": "fewer_than_2_co_activated"},
                             cieu_db_path)
            if eid:
                result["cieu_event_ids"].append(eid)
            return result

        try:
            conn = sqlite3.connect(brain_db_path)
            conn.row_factory = sqlite3.Row
            for i, node_a in enumerate(fired_nodes):
                for node_b in fired_nodes[i + 1:]:
                    rel_a = relevances[node_a]
                    rel_b = relevances[node_b]

                    # Compute delta: sign * lr * rel_a * rel_b
                    delta = sign * lr * rel_a * rel_b

                    # Read current edge weight and update for both directions
                    for src, tgt in [(node_a, node_b), (node_b, node_a)]:
                        existing = conn.execute(
                            "SELECT weight, co_activations FROM edges "
                            "WHERE source_id=? AND target_id=?",
                            (src, tgt)
                        ).fetchone()

                        if existing:
                            old_w = existing["weight"]
                            if sign > 0:
                                new_w = min(1.0, old_w + lr * rel_a * rel_b)
                            else:
                                new_w = max(0.0, old_w - lr * rel_a * rel_b)
                            conn.execute(
                                "UPDATE edges SET weight=?, updated_at=?, "
                                "co_activations=co_activations+1 "
                                "WHERE source_id=? AND target_id=?",
                                (new_w, now, src, tgt)
                            )
                        else:
                            init_w = max(0.0, min(1.0, 0.5 + delta))
                            conn.execute(
                                "INSERT INTO edges "
                                "(source_id, target_id, edge_type, weight, "
                                "created_at, updated_at, co_activations) "
                                "VALUES (?, ?, 'hebbian', ?, ?, ?, 1)",
                                (src, tgt, init_w, now, now)
                            )

                    result["applied_updates"].append({
                        "node_a": node_a,
                        "node_b": node_b,
                        "delta": delta,
                        "lr_used": lr,
                    })

            conn.commit()
            conn.close()

            # Emit Hebbian event
            event_type = ("BRAIN_HEBBIAN_UPDATE_POSITIVE" if sign > 0
                          else "BRAIN_HEBBIAN_DECAY")
            eid = _emit_cieu(event_type,
                             {"query_id": l1_cache_entry.get("query_id", ""),
                              "sign": sign, "lr": lr,
                              "pairs_updated": len(result["applied_updates"]),
                              "fired_nodes": len(fired_nodes)},
                             cieu_db_path)
            if eid:
                result["cieu_event_ids"].append(eid)

        except Exception as e:
            eid = _emit_cieu("BRAIN_WRITEBACK_FAILED",
                             {"stage": "hebbian_update", "error": str(e),
                              "query_id": l1_cache_entry.get("query_id", "")},
                             cieu_db_path)
            if eid:
                result["cieu_event_ids"].append(eid)
            result["error"] = f"hebbian_update failed: {e}"
            return result

    except Exception as e:
        eid = _emit_cieu("BRAIN_WRITEBACK_FAILED",
                         {"stage": "top_level", "error": str(e)},
                         cieu_db_path)
        if eid:
            result["cieu_event_ids"].append(eid)
        result["error"] = str(e)

    return result
