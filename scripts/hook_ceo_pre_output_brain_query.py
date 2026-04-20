#!/usr/bin/env python3
"""
CEO Pre-Output Brain Query — 6D wisdom injection for hook responses.

Authority: Board 2026-04-19 directive (Layer 3 root cause fix)
Purpose: Before CEO produces output, query the 6D brain for relevant
         wisdom nodes and inject them as context hints.

Pipeline:
  1. Extract context signals from the hook payload (tool, file paths, content)
  2. Build a synthetic event dict with those signals
  3. Project to 6D via cieu_brain_bridge.project_event_to_6d()
  4. Query top_k_nodes(k=3) from aiden_brain.db
  5. Read the first ~150 chars of each node's wisdom file (or summary)
  6. Return brain_context list suitable for injection into hook response

Does NOT write activations (read-only query path for latency).
"""

import json as _json
import os
import sqlite3
import sys
import time as _time
import uuid as _uuid
from typing import Any, Dict, List, Optional

# Resolve paths relative to this script's location
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_WISDOM_DIR = os.path.join(_REPO_ROOT, "knowledge", "ceo", "wisdom")
_DEFAULT_BRAIN_DB = os.path.join(_REPO_ROOT, "aiden_brain.db")
_L1_CACHE_PATH = os.path.join(_SCRIPT_DIR, ".brain_l1_cache.json")

# Import brain bridge (reuse Maya's Phase 1 module)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

from ystar.governance.cieu_brain_bridge import project_event_to_6d, top_k_nodes


def extract_context_signals(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract context signals from a hook payload into a synthetic event dict.

    The returned dict is compatible with project_event_to_6d() matchers.
    We enrich it with text signals from tool_input to help the 6D projection
    pick the right heuristic rule.
    """
    tool = payload.get("tool_name", "") or payload.get("tool", "") or ""
    tool_input = payload.get("tool_input", {}) or payload.get("input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    content = tool_input.get("content", "") or ""
    command = tool_input.get("command", "") or ""
    prompt = tool_input.get("prompt", "") or ""

    # Build synthetic event row for 6D projection
    event = {
        "event_type": tool,  # Write, Bash, Agent, etc.
        "decision": "",
        "agent_id": payload.get("agent_id", "ceo"),
        "drift_category": "",
    }

    # Enrich: detect decision-like content
    text_blob = (content + " " + command + " " + prompt).lower()
    if any(w in text_blob for w in ("deploy", "ship", "release", "launch", "publish")):
        event["decision"] = "escalate"  # triggers higher dim_z + dim_c
    if any(w in text_blob for w in ("strategy", "plan", "decision", "choose", "evaluate")):
        event["event_type"] = "ceo_learning"  # triggers higher dim_x
    if any(w in text_blob for w in ("identity", "who am i", "values", "purpose", "mission")):
        event["drift_category"] = "identity_violation"  # triggers higher dim_y

    # Keep raw signals for downstream use
    event["_file_path"] = file_path
    event["_tool"] = tool
    event["_text_snippet"] = text_blob[:200]

    return event


def _read_wisdom_file(file_path_relative: str, max_chars: int = 150) -> Optional[str]:
    """Read the first max_chars of a wisdom file. Returns None if not found."""
    full_path = os.path.join(_WISDOM_DIR, file_path_relative)
    if not os.path.isfile(full_path):
        # Try with .md extension
        if not full_path.endswith(".md"):
            alt = full_path + ".md"
            if os.path.isfile(alt):
                full_path = alt
        # Check if file_path_relative is actually an absolute path
        if not os.path.isfile(full_path) and os.path.isfile(file_path_relative):
            full_path = file_path_relative
        if not os.path.isfile(full_path):
            return None
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read(max_chars + 50)  # read extra to find word boundary
        # Trim to max_chars at word boundary
        if len(text) > max_chars:
            cut = text[:max_chars].rfind(" ")
            if cut > max_chars // 2:
                text = text[:cut] + "..."
            else:
                text = text[:max_chars] + "..."
        return text.strip()
    except Exception:
        return None


def query_brain_for_context(
    payload: Dict[str, Any],
    k: int = 3,
    brain_db_path: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Main entry point: extract context from payload, query 6D brain, return hints.

    Returns list of dicts:
      [{"node_name": "...", "hint": "...", "distance": "0.42"}, ...]

    Returns empty list on any failure (graceful degradation).
    """
    if brain_db_path is None:
        brain_db_path = _DEFAULT_BRAIN_DB

    if not os.path.isfile(brain_db_path):
        return []

    try:
        event = extract_context_signals(payload)
        coords = project_event_to_6d(event)

        conn = sqlite3.connect(brain_db_path)
        try:
            nearest = top_k_nodes(coords, k=k, conn=conn)
        finally:
            conn.close()

        results = []
        for node_id, node_name, dist in nearest:
            hint = None

            # Get file_path and summary from DB
            try:
                conn2 = sqlite3.connect(brain_db_path)
                row = conn2.execute(
                    "SELECT file_path, summary FROM nodes WHERE id = ?", (node_id,)
                ).fetchone()
                conn2.close()
                if row:
                    fp, summary = row
                    if fp:
                        hint = _read_wisdom_file(fp)
                    if not hint and summary:
                        hint = summary[:150]
            except Exception:
                pass

            if not hint:
                hint = f"(node: {node_name})"

            results.append({
                "node_id": node_id,
                "node_name": node_name,
                "hint": hint,
                "distance": f"{dist:.4f}",
            })

        # L1 cache write — persist top_k for L2 writeback consumption
        _write_l1_cache(results)

        return results

    except Exception:
        return []


def _write_l1_cache(top_k: List[Dict[str, str]]) -> None:
    """Write L1 query results to .brain_l1_cache.json for L2 writeback.

    Schema: {"query_id": uuid, "timestamp": unix, "top_k": [{node_id, distance, hint}]}
    Overwrites on every query (L2 reads the latest before drain).
    Fails silently — L1 cache is best-effort, must never block the hook.
    """
    try:
        cache_entry = {
            "query_id": str(_uuid.uuid4()),
            "timestamp": _time.time(),
            "top_k": [
                {
                    "node_id": item.get("node_id"),
                    "node_name": item.get("node_name", ""),
                    "distance": item.get("distance", ""),
                    "hint": item.get("hint", ""),
                }
                for item in top_k
            ],
        }
        with open(_L1_CACHE_PATH, "w", encoding="utf-8") as f:
            _json.dump(cache_entry, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # L1 cache write is non-critical; L2 handles missing cache gracefully


def format_brain_context_for_hook(brain_nodes: List[Dict[str, str]]) -> str:
    """Format brain query results as a human-readable context string."""
    if not brain_nodes:
        return ""
    lines = ["[6D Brain Wisdom Context]"]
    for i, node in enumerate(brain_nodes, 1):
        lines.append(f"  {i}. {node['node_name']} (dist={node['distance']}): {node['hint']}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: simulate a CEO reply scenario
    import json
    demo_payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "reports/phase2_deploy_decision.md",
            "content": "Decision: deploy Phase 2 of the brain pipeline to production."
        },
        "agent_id": "ceo",
    }
    results = query_brain_for_context(demo_payload)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print()
    print(format_brain_context_for_hook(results))
