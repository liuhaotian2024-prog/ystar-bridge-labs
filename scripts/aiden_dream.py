#!/usr/bin/env python3
"""
Aiden Dream — Autonomous learning during Board AFK (sleep-mode self-improvement).

Inspired by neuroscience: NREM (consolidate) -> REM (explore) -> Wake-prep.
L3 Phase 1: dry-run + commit CLI with manual audit gate.
L3-Phase-2: auto scheduling disabled per CEO 2026-04-19 correction

Usage:
    aiden_dream.py --nrem    — internal consolidation (cross-reference, gap detection)
    aiden_dream.py --rem     — external learning (search papers, industry news)
    aiden_dream.py --prep    — wake preparation (ecosystem scan, pre-activation)
    aiden_dream.py --full    — all three phases
    aiden_dream.py --report  — show last dream report
    aiden_dream.py --dry-run [--pattern nrem|rem|prep]  — compute diff, no DB writes
    aiden_dream.py --commit  — apply reviewed diff (dual gate: freshness + review)
"""

import os
import sys
import json
import time
import sqlite3
import hashlib
import glob as glob_mod
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from aiden_brain import (get_db, init_db, add_node, add_edge,
                         activate, record_co_activation, stats, DB_PATH)

COMPANY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WISDOM_ROOT = os.path.join(COMPANY_ROOT, "knowledge", "ceo", "wisdom")
DREAM_LOG = os.path.join(COMPANY_ROOT, "scripts", ".logs", "dream_log.json")
DIFF_DIR = os.path.join(COMPANY_ROOT, "reports", "ceo", "brain_dream_diffs")
CIEU_DB = os.path.join(COMPANY_ROOT, ".ystar_cieu.db")
DIFF_EXPIRY_HOURS = 24


# ── CIEU Event Helpers ────────────────────────────────────────────────

def _emit_cieu(event_type: str, data: dict, cieu_db: str = None):
    """Emit a CIEU event to the database. Fail-open on error.

    Adapts to both production CIEU schema (event_id, created_at, etc.)
    and simplified test schema (timestamp, action, etc.).
    """
    import uuid
    db_path = cieu_db or CIEU_DB
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Detect schema: check if table exists and which columns it has
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cieu_events'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            cols = [row[1] for row in cursor.execute("PRAGMA table_info(cieu_events)").fetchall()]
        else:
            cols = []

        now_iso = datetime.now().isoformat()

        if "created_at" in cols and "event_id" in cols:
            # Production schema
            cursor.execute("""
                INSERT INTO cieu_events (
                    event_id, created_at, event_type, agent_id,
                    decision, result_json, params_json, evidence_grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                time.time(),
                event_type,
                "eng-governance",
                data.get("action", "dream_operation"),
                json.dumps({"result": data.get("result", ""), "intent": data.get("intent", "")}),
                json.dumps(data.get("context", {})),
                "system",
            ))
        else:
            # Test / simple schema — create if needed
            if not table_exists:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cieu_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        event_type TEXT,
                        agent_id TEXT,
                        action TEXT,
                        context TEXT,
                        intent TEXT,
                        constraints TEXT,
                        escalated INTEGER DEFAULT 0,
                        result TEXT
                    )
                """)
            cursor.execute("""
                INSERT INTO cieu_events (
                    timestamp, event_type, agent_id, action,
                    context, intent, constraints, escalated, result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now_iso,
                event_type,
                "eng-governance",
                data.get("action", "dream_operation"),
                json.dumps(data.get("context", {})),
                data.get("intent", ""),
                json.dumps(data.get("constraints", {})),
                0,
                data.get("result", "")
            ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"  [WARN] CIEU emit failed: {e}", file=sys.stderr)
        return False


def _log_dream(phase: str, findings: list):
    """Append findings to dream log."""
    os.makedirs(os.path.dirname(DREAM_LOG), exist_ok=True)
    log = []
    if os.path.exists(DREAM_LOG):
        try:
            with open(DREAM_LOG, "r") as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []
    log.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "phase": phase,
        "findings": findings,
    })
    # Keep only last 20 dream entries
    log = log[-20:]
    with open(DREAM_LOG, "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# ── Phase 1: NREM — Internal Consolidation ──────────────────────────

def nrem_consolidate(dry_run: bool = False):
    """Re-analyze wisdom files, find missing cross-references, detect gaps.
    If dry_run=True, collect proposals without writing to DB."""
    print("=== NREM: Internal Consolidation ===\n")
    findings = []
    proposals = {"new_edges": [], "weight_deltas": [], "archives": [], "new_nodes": []}
    init_db()
    conn = get_db()

    # 1. Find nodes with 0 edges (isolated neurons)
    all_nodes = conn.execute("SELECT id, name FROM nodes").fetchall()
    isolated = []
    for node in all_nodes:
        edge_count = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE source_id=? OR target_id=?",
            (node["id"], node["id"])).fetchone()[0]
        if edge_count == 0:
            isolated.append(node["id"])
    if isolated:
        finding = f"Found {len(isolated)} isolated neurons (0 connections): {isolated[:5]}"
        print(f"  [!] {finding}")
        findings.append(finding)
        if dry_run:
            # Pattern A: propose new edges for isolated nodes
            for iso_id in isolated:
                proposals["new_edges"].append({
                    "source": iso_id,
                    "target": "WHO_I_AM",
                    "proposed_weight": 0.2,
                    "edge_type": "auto_repair",
                    "rationale": "Isolated neuron connection to identity anchor",
                    "pattern": "A",
                })
        else:
            # AUTO-FIX: Connect isolated neurons to WHO_I_AM
            for iso_id in isolated:
                add_edge(iso_id, "WHO_I_AM", weight=0.2, edge_type="auto_repair")
            print(f"  [FIX] Connected {len(isolated)} isolated neurons to WHO_I_AM")
            findings.append(f"AUTO-FIXED: {len(isolated)} isolated neurons connected")

    # 2. Find potential missing bridges (nodes in same type with low connectivity)
    types = {}
    for node in all_nodes:
        nid = node["id"]
        parts = nid.split("/")
        ntype = parts[0] if len(parts) > 1 else "root"
        types.setdefault(ntype, []).append(nid)

    cross_type_edges = conn.execute("""
        SELECT COUNT(*) FROM edges e
        JOIN nodes n1 ON e.source_id = n1.id
        JOIN nodes n2 ON e.target_id = n2.id
        WHERE n1.node_type != n2.node_type
    """).fetchone()[0]
    total_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    cross_ratio = cross_type_edges / max(total_edges, 1)
    finding = f"Cross-type connectivity: {cross_type_edges}/{total_edges} ({cross_ratio:.1%})"
    print(f"  [i] {finding}")
    findings.append(finding)
    if cross_ratio < 0.25:
        print(f"  [!] Cross-type < 25%. Bridge building needed.")
        findings.append("ACTION: Cross-type connectivity below threshold — needs bridge building")

    # 3. Find weakest Hebbian connections (candidates for pruning / archiving)
    weak = conn.execute("""
        SELECT source_id, target_id, weight FROM edges
        WHERE edge_type='hebbian' AND weight < 0.05
        ORDER BY weight ASC LIMIT 5
    """).fetchall()
    if weak:
        finding = f"{len(weak)} Hebbian connections near zero (candidates for pruning)"
        print(f"  [~] {finding}")
        findings.append(finding)
        if dry_run:
            # Pattern C: propose archive/prune for weak edges
            for w in weak:
                proposals["archives"].append({
                    "edge_source": w["source_id"],
                    "edge_target": w["target_id"],
                    "current_weight": w["weight"],
                    "reason": "Hebbian weight below 0.05 threshold",
                    "pattern": "C",
                })

    # 4. Find nodes with high access count (most important memories)
    top_accessed = conn.execute(
        "SELECT id, name, access_count FROM nodes ORDER BY access_count DESC LIMIT 5"
    ).fetchall()
    core_memories = [(r["name"], r["access_count"]) for r in top_accessed]
    finding = f"Core memories: {core_memories}"
    print(f"  [*] {finding}")
    findings.append(finding)

    # 5. Pattern B: Ecosystem entanglement — find co-activated pairs from activation_log
    try:
        logs = conn.execute("""
            SELECT activated_nodes FROM activation_log
            ORDER BY timestamp DESC LIMIT 50
        """).fetchall()
        co_act_pairs = {}
        for row in logs:
            try:
                nodes_data = json.loads(row["activated_nodes"])
                node_ids = [n["node_id"] if isinstance(n, dict) else n for n in nodes_data]
                for i, a in enumerate(node_ids):
                    for b in node_ids[i+1:]:
                        pair = tuple(sorted([a, b]))
                        co_act_pairs[pair] = co_act_pairs.get(pair, 0) + 1
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        # Find pairs co-activated >= 3 times without existing edge
        for (a, b), count in sorted(co_act_pairs.items(), key=lambda x: -x[1]):
            if count < 3:
                break
            existing = conn.execute(
                "SELECT 1 FROM edges WHERE (source_id=? AND target_id=?) OR (source_id=? AND target_id=?)",
                (a, b, b, a)
            ).fetchone()
            if not existing:
                proposals["new_edges"].append({
                    "source": a,
                    "target": b,
                    "proposed_weight": min(0.3, count * 0.05),
                    "edge_type": "hebbian",
                    "co_activation_count": count,
                    "rationale": f"Co-activated {count} times without existing edge",
                    "pattern": "B",
                })
    except Exception as e:
        findings.append(f"Pattern B scan failed: {e}")

    # 6. Pattern D: Blind spot detection — nodes referenced in activation queries
    #    but not in the graph
    try:
        queries = conn.execute("""
            SELECT query FROM activation_log
            ORDER BY timestamp DESC LIMIT 50
        """).fetchall()
        query_words = set()
        for row in queries:
            if row["query"]:
                for word in row["query"].lower().split():
                    if len(word) > 3:
                        query_words.add(word)
        existing_names = set(n["name"].lower() for n in all_nodes)
        existing_ids = set(n["id"].lower() for n in all_nodes)
        blind_spots = []
        for word in query_words:
            if word not in existing_names and word not in existing_ids:
                # Check if this word appears in multiple queries
                mention_count = sum(1 for r in queries if r["query"] and word in r["query"].lower())
                if mention_count >= 2:
                    blind_spots.append({"term": word, "mentions": mention_count})
        if blind_spots:
            for bs in blind_spots[:5]:
                proposals["new_nodes"].append({
                    "proposed_id": f"blind_spot/{bs['term']}",
                    "reason": f"Queried {bs['mentions']} times but not in graph",
                    "prompt_contexts": bs["mentions"],
                    "pattern": "D",
                })
    except Exception as e:
        findings.append(f"Pattern D scan failed: {e}")

    # 7. Weight delta summary — existing Hebbian edges that would be strengthened
    try:
        hebbian_edges = conn.execute("""
            SELECT source_id, target_id, weight, co_activations FROM edges
            WHERE edge_type='hebbian'
            ORDER BY co_activations DESC LIMIT 10
        """).fetchall()
        for edge in hebbian_edges:
            if edge["co_activations"] > 0:
                # Simulate Hebbian strengthening
                current_w = edge["weight"]
                delta = 0.05 * (1 - current_w)  # Standard Hebbian delta
                new_w = min(1.0, current_w + delta)
                if abs(delta) > 0.001:
                    proposals["weight_deltas"].append({
                        "source": edge["source_id"],
                        "target": edge["target_id"],
                        "current_weight": round(current_w, 4),
                        "proposed_weight": round(new_w, 4),
                        "delta": round(delta, 4),
                        "co_activations": edge["co_activations"],
                        "rationale": "Hebbian strengthening from co-activation history",
                    })
    except Exception as e:
        findings.append(f"Weight delta scan failed: {e}")

    conn.close()
    _log_dream("nrem", findings)
    print(f"\n  NREM complete: {len(findings)} findings logged\n")
    return findings, proposals


# ── Phase 2: REM — External Learning ────────────────────────────────

def rem_explore(topics: list = None):
    """Search for external knowledge on specified topics.
    Returns topic suggestions even without web access."""
    print("=== REM: External Learning ===\n")
    findings = []

    if not topics:
        # Auto-generate topics from brain gaps
        conn = get_db()
        # Find nodes with low dim_x (breadth) — knowledge gaps
        gaps = conn.execute(
            "SELECT id, name, dim_x FROM nodes WHERE dim_x < 0.4 "
            "AND node_type NOT IN ('ecosystem_team', 'ecosystem_product', 'ecosystem_entanglement', 'ecosystem_module') "
            "ORDER BY dim_x ASC LIMIT 5"
        ).fetchall()
        conn.close()

        topics = []
        for g in gaps:
            topics.append(f"{g['name']} — needs breadth expansion (X={g['dim_x']:.2f})")

    print("  Recommended learning topics:")
    for i, topic in enumerate(topics, 1):
        print(f"    {i}. {topic}")
        findings.append(f"Learning gap: {topic}")

    # Suggest specific searches
    searches = [
        "AI agent governance frameworks 2025-2026 survey",
        "multi-agent system coordination latest papers",
        "cognitive architecture for persistent AI agents",
        "knowledge graph neural networks small scale",
        "spreading activation models in AI systems",
    ]
    print("\n  Suggested web searches for next learning cycle:")
    for s in searches:
        print(f"    -> {s}")
    findings.append(f"Suggested {len(searches)} external searches")

    _log_dream("rem", findings)
    print(f"\n  REM complete: {len(findings)} topics identified\n")
    return findings


# ── Phase 3: Wake Prep ──────────────────────────────────────────────

def wake_prep():
    """Prepare for next active period."""
    print("=== Wake Prep ===\n")
    findings = []

    # 1. Run ecosystem scan
    try:
        from ecosystem_scan import full_scan, print_summary
        snapshot = full_scan()
        finding = (f"Ecosystem: {len(snapshot['team'])} team, "
                   f"{len(snapshot['products'])} products, "
                   f"{len(snapshot['entanglement_map'])} entanglements")
        print(f"  [i] {finding}")
        findings.append(finding)
    except Exception as e:
        findings.append(f"Ecosystem scan failed: {e}")

    # 2. Pre-activate likely needed nodes
    results = activate("team capability ecosystem strategy", top_n=5)
    pre_activated = [name for _, name, _, _, _ in results]
    finding = f"Pre-activated: {pre_activated}"
    print(f"  [+] {finding}")
    findings.append(finding)

    # 3. Brain health report
    s = stats()
    finding = f"Brain health: {s['nodes']}n / {s['edges']}e / {s['hebbian_edges']}h / avg_w={s['avg_weight']}"
    print(f"  [i] {finding}")
    findings.append(finding)

    _log_dream("wake_prep", findings)
    print(f"\n  Wake prep complete\n")
    return findings


# ── Full Dream Cycle ────────────────────────────────────────────────

def full_dream():
    """Run all three phases."""
    print("=" * 50)
    print("  AIDEN DREAM CYCLE")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")

    nrem_findings, _ = nrem_consolidate()
    rem_findings = rem_explore()
    prep_findings = wake_prep()

    total = len(nrem_findings) + len(rem_findings) + len(prep_findings)
    print("=" * 50)
    print(f"  Dream cycle complete: {total} total findings")
    print(f"  Dream log: {DREAM_LOG}")
    print("=" * 50)


def show_report():
    """Show last dream report."""
    if not os.path.exists(DREAM_LOG):
        print("No dream log found. Run a dream cycle first.")
        return
    with open(DREAM_LOG, "r") as f:
        log = json.load(f)
    print(f"=== Dream Log ({len(log)} entries) ===\n")
    for entry in log[-5:]:
        print(f"[{entry['timestamp']}] {entry['phase']}")
        for finding in entry["findings"]:
            print(f"  - {finding[:80]}")
        print()


# ── L3 Phase 1: Dry-Run Mode ──────────────────────────────────────

def _compute_echo_chamber_score(proposals: dict) -> float:
    """Compute echo chamber risk score (0.0 = fully diversifying, 1.0 = pure echo).

    Ratio of self-reinforcing changes (strengthening existing patterns)
    vs diversifying changes (new connections to isolated/different-type nodes).
    """
    reinforcing = 0
    diversifying = 0

    for edge in proposals.get("new_edges", []):
        if edge.get("pattern") == "A":
            diversifying += 1  # Connecting isolated nodes = diversifying
        elif edge.get("pattern") == "B":
            reinforcing += 1  # Co-activation edges reinforce existing patterns

    for delta in proposals.get("weight_deltas", []):
        reinforcing += 1  # Strengthening existing = reinforcing

    for archive in proposals.get("archives", []):
        # Pruning weak edges is neutral-to-diversifying
        diversifying += 0.5

    for node in proposals.get("new_nodes", []):
        diversifying += 1  # New blind spot nodes = diversifying

    total = reinforcing + diversifying
    if total == 0:
        return 0.0
    return round(reinforcing / total, 3)


def _compute_bias_direction(proposals: dict, db_path: str = None) -> str:
    """Determine which topics get stronger vs weaker."""
    strengthened = set()
    weakened = set()

    for edge in proposals.get("new_edges", []):
        strengthened.add(edge["source"])
        strengthened.add(edge["target"])

    for delta in proposals.get("weight_deltas", []):
        if delta["delta"] > 0:
            strengthened.add(delta["source"])
            strengthened.add(delta["target"])
        elif delta["delta"] < 0:
            weakened.add(delta["source"])
            weakened.add(delta["target"])

    for archive in proposals.get("archives", []):
        weakened.add(archive["edge_source"])
        weakened.add(archive["edge_target"])

    parts = []
    if strengthened:
        parts.append(f"Strengthened: {', '.join(list(strengthened)[:5])}")
    if weakened:
        parts.append(f"Weakened: {', '.join(list(weakened)[:5])}")
    if not parts:
        return "No directional bias detected"
    return "; ".join(parts)


def dry_run(pattern_filter: str = None, cieu_db: str = None, brain_db: str = None):
    """Compute proposed changes without touching aiden_brain.db.

    Writes a diff report to reports/ceo/brain_dream_diffs/.
    Emits BRAIN_DREAM_DIFF_GENERATED CIEU event.

    Args:
        pattern_filter: Optional filter for specific pattern (nrem|rem|prep)
        cieu_db: Override CIEU database path (for testing)
        brain_db: Override brain database path (for testing)

    Returns:
        Path to the generated diff file, or None on error.
    """
    print("=" * 50)
    print("  BRAIN DREAM DRY-RUN")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: DRY-RUN (no changes will be applied)")
    if pattern_filter:
        print(f"  Pattern filter: {pattern_filter}")
    print("=" * 50 + "\n")

    # Run consolidation analysis in dry_run mode
    findings, proposals = nrem_consolidate(dry_run=True)

    # Count activation_log rows
    try:
        conn = get_db(brain_db or DB_PATH)
        log_count = conn.execute("SELECT COUNT(*) FROM activation_log").fetchone()[0]
        conn.close()
    except Exception:
        log_count = 0

    # Compute risk metrics
    echo_score = _compute_echo_chamber_score(proposals)
    bias_dir = _compute_bias_direction(proposals)

    # Generate diff report
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    pattern_suffix = f"_{pattern_filter}" if pattern_filter else ""
    diff_filename = f"dream_diff_{timestamp_str}{pattern_suffix}.md"

    diff_dir = DIFF_DIR
    os.makedirs(diff_dir, exist_ok=True)
    diff_path = os.path.join(diff_dir, diff_filename)

    report_lines = [
        "# Brain Dream Diff Report",
        f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}",
        "Mode: DRY-RUN (no changes applied)",
        f"Activation log rows scanned: {log_count}",
        "",
        "## Proposed New Edges (Pattern A + B)",
        "| Source | Target | Proposed Weight | Co-activation Count | Pattern | Rationale |",
        "|--------|--------|-----------------|---------------------|---------|-----------|",
    ]

    for edge in proposals.get("new_edges", []):
        co_act = edge.get("co_activation_count", "N/A")
        report_lines.append(
            f"| {edge['source']} | {edge['target']} | {edge['proposed_weight']} "
            f"| {co_act} | {edge['pattern']} | {edge['rationale']} |"
        )

    report_lines.extend([
        "",
        "## Proposed New Nodes (Pattern D - Blind Spots)",
        "| Proposed ID | Reason | Prompt Contexts |",
        "|-------------|--------|-----------------|",
    ])

    for node in proposals.get("new_nodes", []):
        report_lines.append(
            f"| {node['proposed_id']} | {node['reason']} | {node['prompt_contexts']} |"
        )

    report_lines.extend([
        "",
        "## Proposed Archive (Pattern C)",
        "| Edge Source | Edge Target | Current Weight | Reason |",
        "|------------|-------------|----------------|--------|",
    ])

    for archive in proposals.get("archives", []):
        report_lines.append(
            f"| {archive['edge_source']} | {archive['edge_target']} "
            f"| {archive['current_weight']} | {archive['reason']} |"
        )

    report_lines.extend([
        "",
        "## Weight Delta Summary",
        "| Source | Target | Old Weight | New Weight | Delta | Rationale |",
        "|--------|--------|-----------|------------|-------|-----------|",
    ])

    for delta in proposals.get("weight_deltas", []):
        report_lines.append(
            f"| {delta['source']} | {delta['target']} | {delta['current_weight']} "
            f"| {delta['proposed_weight']} | {delta['delta']} | {delta['rationale']} |"
        )

    report_lines.extend([
        "",
        "## Risk Assessment",
        f"- Echo chamber score: {echo_score} (ratio of self-reinforcing vs diversifying changes)",
        f"- Bias direction: {bias_dir}",
        "",
        "## Proposal Counts",
        f"- New edges: {len(proposals.get('new_edges', []))}",
        f"- New nodes: {len(proposals.get('new_nodes', []))}",
        f"- Archives: {len(proposals.get('archives', []))}",
        f"- Weight deltas: {len(proposals.get('weight_deltas', []))}",
        "",
        "## Proposals JSON (machine-readable)",
        "```json",
        json.dumps(proposals, indent=2, default=str),
        "```",
    ])

    with open(diff_path, "w") as f:
        f.write("\n".join(report_lines) + "\n")

    print(f"\n  Diff report written: {diff_path}")
    total_proposals = (len(proposals.get("new_edges", [])) +
                       len(proposals.get("new_nodes", [])) +
                       len(proposals.get("archives", [])) +
                       len(proposals.get("weight_deltas", [])))
    print(f"  Total proposals: {total_proposals}")
    print(f"  Echo chamber score: {echo_score}")

    # Emit CIEU event
    _emit_cieu("BRAIN_DREAM_DIFF_GENERATED", {
        "action": "dry_run",
        "intent": "Compute brain dream diff without applying changes",
        "context": {
            "diff_path": diff_path,
            "total_proposals": total_proposals,
            "echo_chamber_score": echo_score,
            "activation_log_rows": log_count,
        },
        "result": f"diff_written:{diff_path}",
    }, cieu_db=cieu_db)

    print("  CIEU event BRAIN_DREAM_DIFF_GENERATED emitted")
    return diff_path


# ── L3 Phase 1: Commit Mode (Dual Gate) ───────────────────────────

def _find_latest_diff() -> str:
    """Find the most recent diff file in DIFF_DIR. Returns path or None."""
    if not os.path.isdir(DIFF_DIR):
        return None
    files = sorted(glob_mod.glob(os.path.join(DIFF_DIR, "dream_diff_*.md")))
    if not files:
        return None
    # Return the one with latest mtime
    return max(files, key=os.path.getmtime)


def _check_gate1_freshness(diff_path: str, expiry_hours: int = None) -> tuple:
    """Gate 1: Check diff file freshness.
    Returns (passed: bool, reason: str, mtime: float).
    """
    if expiry_hours is None:
        expiry_hours = DIFF_EXPIRY_HOURS
    if not diff_path or not os.path.exists(diff_path):
        return False, "No diff file found in reports/ceo/brain_dream_diffs/", 0.0
    mtime = os.path.getmtime(diff_path)
    age_hours = (time.time() - mtime) / 3600
    if age_hours > expiry_hours:
        return False, f"Diff file expired: {age_hours:.1f}h old (max {expiry_hours}h)", mtime
    return True, f"Diff file fresh: {age_hours:.1f}h old", mtime


def _check_gate2_reviewed(diff_mtime: float, cieu_db: str = None) -> tuple:
    """Gate 2: Check that a BRAIN_DREAM_DIFF_REVIEWED event exists after diff mtime.
    Returns (passed: bool, reason: str).

    Adapts to both production schema (created_at as epoch float) and
    test schema (timestamp as ISO string).
    """
    db_path = cieu_db or CIEU_DB
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Detect schema
        cols = [row[1] for row in cursor.execute("PRAGMA table_info(cieu_events)").fetchall()]

        if "created_at" in cols:
            # Production schema: created_at is epoch float
            cursor.execute("""
                SELECT COUNT(*) FROM cieu_events
                WHERE event_type = 'BRAIN_DREAM_DIFF_REVIEWED'
                AND created_at > ?
            """, (diff_mtime,))
        else:
            # Test schema: timestamp is ISO string
            diff_time_iso = datetime.fromtimestamp(diff_mtime).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM cieu_events
                WHERE event_type = 'BRAIN_DREAM_DIFF_REVIEWED'
                AND timestamp > ?
            """, (diff_time_iso,))

        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            return False, "No BRAIN_DREAM_DIFF_REVIEWED event found after diff creation"
        return True, f"Found {count} review event(s) after diff creation"
    except Exception as e:
        return False, f"CIEU database check failed: {e}"


def commit_dream(cieu_db: str = None, brain_db: str = None, diff_dir: str = None):
    """Apply reviewed diff to aiden_brain.db with dual gate enforcement.

    Gate 1: Diff file must exist and be < 24h old.
    Gate 2: BRAIN_DREAM_DIFF_REVIEWED CIEU event must exist after diff mtime.

    Args:
        cieu_db: Override CIEU database path (for testing)
        brain_db: Override brain database path (for testing)
        diff_dir: Override diff directory (for testing)

    Returns:
        True if committed, False if denied.
    """
    print("=" * 50)
    print("  BRAIN DREAM COMMIT")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")

    # Find latest diff
    search_dir = diff_dir or DIFF_DIR
    if not os.path.isdir(search_dir):
        diff_path = None
    else:
        files = sorted(glob_mod.glob(os.path.join(search_dir, "dream_diff_*.md")))
        diff_path = max(files, key=os.path.getmtime) if files else None

    # Gate 1: Freshness check
    g1_pass, g1_reason, diff_mtime = _check_gate1_freshness(diff_path)
    print(f"  Gate 1 (freshness): {'PASS' if g1_pass else 'DENY'} — {g1_reason}")

    if not g1_pass:
        _emit_cieu("BRAIN_DREAM_COMMIT_DENIED", {
            "action": "commit_denied",
            "intent": "Apply brain dream changes",
            "context": {"gate": 1, "reason": g1_reason, "diff_path": diff_path or "none"},
            "result": "denied:expired_diff",
        }, cieu_db=cieu_db)
        print("\n  COMMIT DENIED. Run --dry-run first to generate a fresh diff.")
        return False

    # Gate 2: Review check
    g2_pass, g2_reason = _check_gate2_reviewed(diff_mtime, cieu_db=cieu_db)
    print(f"  Gate 2 (reviewed):  {'PASS' if g2_pass else 'DENY'} — {g2_reason}")

    if not g2_pass:
        _emit_cieu("BRAIN_DREAM_COMMIT_DENIED", {
            "action": "commit_denied",
            "intent": "Apply brain dream changes",
            "context": {"gate": 2, "reason": g2_reason, "diff_path": diff_path},
            "result": "denied:unreviewed",
        }, cieu_db=cieu_db)
        print("\n  COMMIT DENIED. Run brain_dream_approve.py to review the diff first.")
        return False

    # Both gates passed — apply changes
    print("\n  Both gates passed. Applying changes...\n")

    # Read proposals from diff file
    try:
        with open(diff_path, "r") as f:
            content = f.read()
        # Extract JSON block
        json_start = content.find("```json\n")
        json_end = content.find("\n```", json_start + 7)
        if json_start < 0 or json_end < 0:
            print("  ERROR: Could not parse proposals from diff file.")
            return False
        proposals = json.loads(content[json_start + 8:json_end])
    except Exception as e:
        print(f"  ERROR: Failed to read diff file: {e}")
        return False

    applied_count = 0
    target_db = brain_db or DB_PATH

    # Apply new edges
    for edge in proposals.get("new_edges", []):
        try:
            add_edge(edge["source"], edge["target"],
                     weight=edge["proposed_weight"],
                     edge_type=edge.get("edge_type", "hebbian"),
                     db_path=target_db)
            applied_count += 1
        except Exception as e:
            print(f"  WARN: Failed to add edge {edge['source']}->{edge['target']}: {e}")

    # Apply weight deltas
    for delta in proposals.get("weight_deltas", []):
        try:
            conn = get_db(target_db)
            conn.execute(
                "UPDATE edges SET weight = ?, updated_at = ? WHERE source_id = ? AND target_id = ?",
                (delta["proposed_weight"], time.time(), delta["source"], delta["target"])
            )
            conn.commit()
            conn.close()
            applied_count += 1
        except Exception as e:
            print(f"  WARN: Failed to update weight {delta['source']}->{delta['target']}: {e}")

    # Apply archives (remove weak edges)
    for archive in proposals.get("archives", []):
        try:
            conn = get_db(target_db)
            conn.execute(
                "DELETE FROM edges WHERE source_id = ? AND target_id = ?",
                (archive["edge_source"], archive["edge_target"])
            )
            conn.commit()
            conn.close()
            applied_count += 1
        except Exception as e:
            print(f"  WARN: Failed to archive edge: {e}")

    # Apply new nodes
    for node in proposals.get("new_nodes", []):
        try:
            add_node(node["proposed_id"], node["proposed_id"],
                     node_type="blind_spot", summary=node["reason"],
                     db_path=target_db)
            applied_count += 1
        except Exception as e:
            print(f"  WARN: Failed to add node {node['proposed_id']}: {e}")

    print(f"\n  Applied {applied_count} changes to {target_db}")

    # Emit CIEU event
    _emit_cieu("BRAIN_DREAM_COMMITTED", {
        "action": "commit",
        "intent": "Apply reviewed brain dream changes",
        "context": {
            "diff_path": diff_path,
            "applied_changes": applied_count,
            "proposals": {k: len(v) for k, v in proposals.items()},
        },
        "result": f"committed:{applied_count}_changes",
    }, cieu_db=cieu_db)

    print(f"  CIEU event BRAIN_DREAM_COMMITTED emitted (applied_changes={applied_count})")
    return True


def show_report():
    """Show last dream report."""
    if not os.path.exists(DREAM_LOG):
        print("No dream log found. Run a dream cycle first.")
        return
    with open(DREAM_LOG, "r") as f:
        log = json.load(f)
    print(f"=== Dream Log ({len(log)} entries) ===\n")
    for entry in log[-5:]:
        print(f"[{entry['timestamp']}] {entry['phase']}")
        for finding in entry["findings"]:
            print(f"  - {finding[:80]}")
        print()


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        pattern = None
        if "--pattern" in sys.argv:
            idx = sys.argv.index("--pattern")
            if idx + 1 < len(sys.argv):
                pattern = sys.argv[idx + 1]
        dry_run(pattern_filter=pattern)
    elif "--commit" in sys.argv:
        success = commit_dream()
        sys.exit(0 if success else 1)
    elif "--nrem" in sys.argv:
        nrem_consolidate()
    elif "--rem" in sys.argv:
        rem_explore()
    elif "--prep" in sys.argv:
        wake_prep()
    elif "--report" in sys.argv:
        show_report()
    elif "--full" in sys.argv:
        full_dream()
    else:
        print(__doc__)
