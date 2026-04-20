"""
Tests for L3 Phase 1 — Brain Dream Manual CLI + Dual Gate.

Covers:
1. dry-run produces diff file but does NOT modify brain DB
2. commit with no diff -> DENY
3. commit with diff but no reviewed event -> DENY
4. commit with diff + reviewed event but diff > 24h -> DENY
5. commit with diff + reviewed event + mtime fresh -> apply + DB changes
6. CIEU events emitted correctly for each path
"""

import os
import sys
import json
import time
import sqlite3
import tempfile
import shutil
import pytest
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts to path
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "scripts")
sys.path.insert(0, SCRIPTS_DIR)


@pytest.fixture
def temp_env(tmp_path):
    """Create isolated temp environment with brain DB, CIEU DB, and diff dir."""
    brain_db = str(tmp_path / "test_brain.db")
    cieu_db = str(tmp_path / "test_cieu.db")
    diff_dir = str(tmp_path / "brain_dream_diffs")
    os.makedirs(diff_dir, exist_ok=True)

    # Initialize brain DB
    from aiden_brain import init_db, add_node, add_edge
    init_db(brain_db)
    # Add some test nodes
    add_node("WHO_I_AM", "Who I Am", node_type="self_knowledge", db_path=brain_db)
    add_node("test/node_a", "Node A", node_type="ceo_learning", db_path=brain_db)
    add_node("test/node_b", "Node B", node_type="strategic", db_path=brain_db)
    add_node("test/isolated", "Isolated Node", node_type="meta", db_path=brain_db)
    # Add an edge between A and B but leave isolated node without edges
    add_edge("test/node_a", "test/node_b", weight=0.5, edge_type="explicit", db_path=brain_db)
    # Add a weak Hebbian edge for pruning test
    add_edge("test/node_a", "WHO_I_AM", weight=0.02, edge_type="hebbian", db_path=brain_db)

    # Initialize CIEU DB
    conn = sqlite3.connect(cieu_db)
    conn.execute("""
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
    conn.commit()
    conn.close()

    return {
        "brain_db": brain_db,
        "cieu_db": cieu_db,
        "diff_dir": diff_dir,
        "tmp_path": tmp_path,
    }


def _count_edges(db_path):
    """Count total edges in brain DB."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    conn.close()
    return count


def _count_nodes(db_path):
    """Count total nodes in brain DB."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    conn.close()
    return count


def _count_cieu_events(db_path, event_type=None):
    """Count CIEU events, optionally filtered by type."""
    conn = sqlite3.connect(db_path)
    if event_type:
        count = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = ?",
            (event_type,)
        ).fetchone()[0]
    else:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
    conn.close()
    return count


def _create_diff_file(diff_dir, proposals=None, age_hours=0):
    """Create a diff file with given proposals and age."""
    if proposals is None:
        proposals = {
            "new_edges": [
                {
                    "source": "test/isolated",
                    "target": "WHO_I_AM",
                    "proposed_weight": 0.2,
                    "edge_type": "auto_repair",
                    "rationale": "Test edge",
                    "pattern": "A",
                }
            ],
            "weight_deltas": [],
            "archives": [],
            "new_nodes": [],
        }

    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    diff_path = os.path.join(diff_dir, f"dream_diff_{timestamp_str}.md")

    content = f"""# Brain Dream Diff Report
Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}
Mode: DRY-RUN (no changes applied)
Activation log rows scanned: 0

## Proposed New Edges (Pattern A + B)
| Source | Target | Proposed Weight | Co-activation Count | Pattern | Rationale |
|--------|--------|-----------------|---------------------|---------|-----------|

## Proposed New Nodes (Pattern D - Blind Spots)
| Proposed ID | Reason | Prompt Contexts |
|-------------|--------|-----------------|

## Proposed Archive (Pattern C)
| Edge Source | Edge Target | Current Weight | Reason |
|------------|-------------|----------------|--------|

## Weight Delta Summary
| Source | Target | Old Weight | New Weight | Delta | Rationale |
|--------|--------|-----------|------------|-------|-----------|

## Risk Assessment
- Echo chamber score: 0.0 (ratio of self-reinforcing vs diversifying changes)
- Bias direction: No directional bias detected

## Proposal Counts
- New edges: {len(proposals.get('new_edges', []))}
- New nodes: {len(proposals.get('new_nodes', []))}
- Archives: {len(proposals.get('archives', []))}
- Weight deltas: {len(proposals.get('weight_deltas', []))}

## Proposals JSON (machine-readable)
```json
{json.dumps(proposals, indent=2)}
```
"""
    with open(diff_path, "w") as f:
        f.write(content)

    # Backdate the file if needed
    if age_hours > 0:
        old_time = time.time() - (age_hours * 3600)
        os.utime(diff_path, (old_time, old_time))

    return diff_path


def _insert_review_event(cieu_db, timestamp_iso=None):
    """Insert a BRAIN_DREAM_DIFF_REVIEWED event."""
    if timestamp_iso is None:
        timestamp_iso = datetime.now().isoformat()
    conn = sqlite3.connect(cieu_db)
    conn.execute("""
        INSERT INTO cieu_events (timestamp, event_type, agent_id, action, context, intent, constraints, escalated, result)
        VALUES (?, 'BRAIN_DREAM_DIFF_REVIEWED', 'board', 'review_approved', '{}', 'test', '{}', 0, 'approved')
    """, (timestamp_iso,))
    conn.commit()
    conn.close()


# ── Test 1: dry-run produces diff file but does NOT modify brain DB ──

class TestDryRun:
    def test_dry_run_produces_diff_no_db_change(self, temp_env):
        """dry-run must produce a diff file without changing brain DB."""
        import aiden_dream

        # Record initial state
        initial_edges = _count_edges(temp_env["brain_db"])
        initial_nodes = _count_nodes(temp_env["brain_db"])

        # Monkey-patch DB_PATH and DIFF_DIR for isolation
        orig_db = aiden_dream.DB_PATH
        orig_diff_dir = aiden_dream.DIFF_DIR
        orig_cieu_db = aiden_dream.CIEU_DB
        try:
            aiden_dream.DB_PATH = temp_env["brain_db"]
            aiden_dream.DIFF_DIR = temp_env["diff_dir"]
            aiden_dream.CIEU_DB = temp_env["cieu_db"]

            # Also patch aiden_brain.DB_PATH for the import
            import aiden_brain
            orig_brain_db = aiden_brain.DB_PATH
            aiden_brain.DB_PATH = temp_env["brain_db"]

            diff_path = aiden_dream.dry_run(cieu_db=temp_env["cieu_db"],
                                             brain_db=temp_env["brain_db"])
        finally:
            aiden_dream.DB_PATH = orig_db
            aiden_dream.DIFF_DIR = orig_diff_dir
            aiden_dream.CIEU_DB = orig_cieu_db
            aiden_brain.DB_PATH = orig_brain_db

        # Verify diff file was created
        assert diff_path is not None
        assert os.path.exists(diff_path)
        assert diff_path.startswith(temp_env["diff_dir"])

        # Verify DB was NOT modified
        assert _count_edges(temp_env["brain_db"]) == initial_edges
        assert _count_nodes(temp_env["brain_db"]) == initial_nodes

        # Verify CIEU event was emitted
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_DIFF_GENERATED") == 1

        # Verify diff file content has required sections
        with open(diff_path) as f:
            content = f.read()
        assert "Brain Dream Diff Report" in content
        assert "DRY-RUN" in content
        assert "Echo chamber score" in content
        assert "Proposals JSON" in content


# ── Test 2: commit with no diff -> DENY ──

class TestCommitNoDiff:
    def test_commit_no_diff_denied(self, temp_env):
        """commit with no diff file must be denied."""
        import aiden_dream

        result = aiden_dream.commit_dream(
            cieu_db=temp_env["cieu_db"],
            brain_db=temp_env["brain_db"],
            diff_dir=temp_env["diff_dir"],  # empty dir
        )

        assert result is False
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_COMMIT_DENIED") == 1


# ── Test 3: commit with diff but no reviewed event -> DENY ──

class TestCommitUnreviewed:
    def test_commit_unreviewed_denied(self, temp_env):
        """commit with diff but no BRAIN_DREAM_DIFF_REVIEWED event must be denied."""
        import aiden_dream

        # Create a fresh diff file
        _create_diff_file(temp_env["diff_dir"])

        result = aiden_dream.commit_dream(
            cieu_db=temp_env["cieu_db"],
            brain_db=temp_env["brain_db"],
            diff_dir=temp_env["diff_dir"],
        )

        assert result is False
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_COMMIT_DENIED") >= 1

        # Check the denied event context mentions unreviewed
        conn = sqlite3.connect(temp_env["cieu_db"])
        row = conn.execute(
            "SELECT result FROM cieu_events WHERE event_type='BRAIN_DREAM_COMMIT_DENIED' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        assert "unreviewed" in row[0]


# ── Test 4: commit with diff + reviewed event but diff > 24h -> DENY ──

class TestCommitExpired:
    def test_commit_expired_diff_denied(self, temp_env):
        """commit with old diff (> 24h) must be denied even with review event."""
        import aiden_dream

        # Create a diff that's 25 hours old
        diff_path = _create_diff_file(temp_env["diff_dir"], age_hours=25)

        # Insert a review event AFTER the diff creation
        # but the diff itself is expired
        _insert_review_event(temp_env["cieu_db"])

        result = aiden_dream.commit_dream(
            cieu_db=temp_env["cieu_db"],
            brain_db=temp_env["brain_db"],
            diff_dir=temp_env["diff_dir"],
        )

        assert result is False
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_COMMIT_DENIED") >= 1

        # Check reason mentions expiry
        conn = sqlite3.connect(temp_env["cieu_db"])
        row = conn.execute(
            "SELECT result FROM cieu_events WHERE event_type='BRAIN_DREAM_COMMIT_DENIED' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        assert "expired" in row[0]


# ── Test 5: commit with diff + reviewed event + mtime fresh -> apply ──

class TestCommitSuccess:
    def test_commit_success_applies_changes(self, temp_env):
        """commit with valid diff + review event must apply changes to DB."""
        import aiden_dream

        proposals = {
            "new_edges": [
                {
                    "source": "test/isolated",
                    "target": "WHO_I_AM",
                    "proposed_weight": 0.2,
                    "edge_type": "auto_repair",
                    "rationale": "Isolated neuron fix",
                    "pattern": "A",
                }
            ],
            "weight_deltas": [],
            "archives": [],
            "new_nodes": [],
        }

        # Record initial state
        initial_edges = _count_edges(temp_env["brain_db"])

        # Create a fresh diff file
        diff_path = _create_diff_file(temp_env["diff_dir"], proposals=proposals)

        # Wait a tiny bit so the review timestamp is after diff mtime
        time.sleep(0.1)

        # Insert review event
        _insert_review_event(temp_env["cieu_db"])

        result = aiden_dream.commit_dream(
            cieu_db=temp_env["cieu_db"],
            brain_db=temp_env["brain_db"],
            diff_dir=temp_env["diff_dir"],
        )

        assert result is True

        # Verify DB was modified: new edge added (bidirectional = +2 rows)
        final_edges = _count_edges(temp_env["brain_db"])
        assert final_edges > initial_edges

        # Verify CIEU committed event
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_COMMITTED") == 1

        # Verify the specific edge was created
        conn = sqlite3.connect(temp_env["brain_db"])
        conn.row_factory = sqlite3.Row
        edge = conn.execute(
            "SELECT * FROM edges WHERE source_id='test/isolated' AND target_id='WHO_I_AM'"
        ).fetchone()
        conn.close()
        assert edge is not None
        assert abs(edge["weight"] - 0.2) < 0.01


# ── Test 6: CIEU events emitted for all paths ──

class TestCIEUEvents:
    def test_cieu_events_registered(self, temp_env):
        """Verify all 4 CIEU event types can be emitted."""
        import aiden_dream

        # BRAIN_DREAM_DIFF_GENERATED — emitted by dry_run
        aiden_dream._emit_cieu("BRAIN_DREAM_DIFF_GENERATED", {
            "action": "test", "result": "test_diff"
        }, cieu_db=temp_env["cieu_db"])

        # BRAIN_DREAM_COMMIT_DENIED
        aiden_dream._emit_cieu("BRAIN_DREAM_COMMIT_DENIED", {
            "action": "test", "result": "test_deny"
        }, cieu_db=temp_env["cieu_db"])

        # BRAIN_DREAM_COMMITTED
        aiden_dream._emit_cieu("BRAIN_DREAM_COMMITTED", {
            "action": "test", "result": "test_commit"
        }, cieu_db=temp_env["cieu_db"])

        # BRAIN_DREAM_DIFF_REVIEWED (normally emitted by brain_dream_approve.py)
        aiden_dream._emit_cieu("BRAIN_DREAM_DIFF_REVIEWED", {
            "action": "test", "result": "test_review"
        }, cieu_db=temp_env["cieu_db"])

        # Verify all 4 types exist
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_DIFF_GENERATED") == 1
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_COMMIT_DENIED") == 1
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_COMMITTED") == 1
        assert _count_cieu_events(temp_env["cieu_db"], "BRAIN_DREAM_DIFF_REVIEWED") == 1


# ── Test 7: Gate functions work independently ──

class TestGateFunctions:
    def test_gate1_no_file(self, temp_env):
        """Gate 1 denies when no diff file exists."""
        import aiden_dream
        passed, reason, mtime = aiden_dream._check_gate1_freshness(None)
        assert passed is False
        assert "No diff file" in reason

    def test_gate1_expired(self, temp_env):
        """Gate 1 denies when diff is > 24h old."""
        import aiden_dream
        diff_path = _create_diff_file(temp_env["diff_dir"], age_hours=25)
        passed, reason, mtime = aiden_dream._check_gate1_freshness(diff_path)
        assert passed is False
        assert "expired" in reason.lower()

    def test_gate1_fresh(self, temp_env):
        """Gate 1 passes when diff is fresh."""
        import aiden_dream
        diff_path = _create_diff_file(temp_env["diff_dir"])
        passed, reason, mtime = aiden_dream._check_gate1_freshness(diff_path)
        assert passed is True
        assert mtime > 0

    def test_gate2_no_review(self, temp_env):
        """Gate 2 denies when no review event exists."""
        import aiden_dream
        passed, reason = aiden_dream._check_gate2_reviewed(
            time.time(), cieu_db=temp_env["cieu_db"]
        )
        assert passed is False
        assert "No BRAIN_DREAM_DIFF_REVIEWED" in reason

    def test_gate2_with_review(self, temp_env):
        """Gate 2 passes when review event exists after diff mtime."""
        import aiden_dream
        diff_mtime = time.time() - 60  # 1 minute ago
        _insert_review_event(temp_env["cieu_db"])  # now
        passed, reason = aiden_dream._check_gate2_reviewed(
            diff_mtime, cieu_db=temp_env["cieu_db"]
        )
        assert passed is True
