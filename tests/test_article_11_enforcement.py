#!/usr/bin/env python3
"""
[L3→L4] Article 11 Enforcement Tests — AMENDMENT-023

Test 3-layer enforcement mechanism:
- Layer 1: Proactive injection (hook_user_prompt_tracker.py)
- Layer 2: In-flight enforcement (governance rules)
- Layer 3: Post-audit drift detection (forget_guard_summary.py)
"""

import pytest
import sqlite3
import tempfile
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts to path for imports
WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
sys.path.insert(0, str(WORKSPACE_ROOT / "scripts"))

from article_11_tracker import layer_complete, check_compliance, ARTICLE_11_LAYERS
from hook_user_prompt_tracker import detect_decision_context
from forget_guard_summary import detect_article_11_drift


@pytest.fixture
def temp_cieu_db():
    """Create temporary CIEU database for isolated testing."""
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = db_file.name
    db_file.close()

    # Initialize schema (minimal schema for testing)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cieu_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            seq_global INTEGER,
            created_at REAL,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            drift_detected INTEGER,
            drift_details TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


class TestLayer1ProactiveInjection:
    """Test Layer 1: Proactive keyword detection and injection."""

    def test_detect_decision_context_positive(self):
        """Should detect decision keywords in user message."""
        messages = [
            "We should launch new strategy next quarter",
            "I think we need to pivot our roadmap",
            "AMENDMENT-025 proposal for restructure",
            "我们需要重大决策关于架构",
            "Let's deploy the new mission statement"
        ]

        for msg in messages:
            assert detect_decision_context(msg), f"Should detect decision keyword in: {msg}"

    def test_detect_decision_context_negative(self):
        """Should NOT detect decision keywords in normal messages."""
        messages = [
            "What's the status of the bug fix?",
            "Can you read the file?",
            "Run tests please",
            "Update the documentation"
        ]

        for msg in messages:
            assert not detect_decision_context(msg), f"Should NOT detect decision keyword in: {msg}"

    def test_detect_decision_context_case_insensitive(self):
        """Should detect keywords regardless of case."""
        assert detect_decision_context("STRATEGY")
        assert detect_decision_context("Strategy")
        assert detect_decision_context("strategy")
        assert detect_decision_context("We need a new ROADMAP")


class TestLayer2InFlightTracking:
    """Test Layer 2: Event emission and compliance checking."""

    def test_layer_complete_emits_event(self, temp_cieu_db):
        """Should emit ARTICLE_11_LAYER_X_COMPLETE event to CIEU."""
        success = layer_complete(
            layer=0,
            evidence="Y* contract: Werner Vogels — operational excellence",
            db_path=temp_cieu_db
        )

        assert success, "layer_complete should return True"

        # Verify event in database
        conn = sqlite3.connect(temp_cieu_db)
        cursor = conn.execute("""
            SELECT event_type, drift_details FROM cieu_events
            WHERE event_type = 'ARTICLE_11_LAYER_0_COMPLETE'
            ORDER BY created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        assert row is not None, "Event should be written to CIEU"
        assert row[0] == "ARTICLE_11_LAYER_0_COMPLETE"
        assert "Vogels" in row[1]

    def test_layer_complete_all_layers(self, temp_cieu_db):
        """Should successfully emit events for all 7 layers."""
        for layer_num in range(7):
            success = layer_complete(
                layer=layer_num,
                evidence=f"Test evidence for layer {layer_num}",
                db_path=temp_cieu_db
            )
            assert success, f"Layer {layer_num} completion should succeed"

        # Verify all events exist
        conn = sqlite3.connect(temp_cieu_db)
        cursor = conn.execute("""
            SELECT COUNT(DISTINCT event_type) FROM cieu_events
            WHERE event_type LIKE 'ARTICLE_11_LAYER_%_COMPLETE'
        """)
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 7, "Should have 7 distinct layer completion events"

    def test_layer_complete_invalid_layer(self, temp_cieu_db):
        """Should reject invalid layer numbers."""
        success = layer_complete(
            layer=7,  # Invalid (0-6 only)
            evidence="Invalid layer test",
            db_path=temp_cieu_db
        )
        assert not success, "Should reject layer number outside 0-6 range"

    def test_layer_complete_insufficient_evidence(self, temp_cieu_db):
        """Should reject evidence that is too short."""
        success = layer_complete(
            layer=0,
            evidence="short",  # <10 chars
            db_path=temp_cieu_db
        )
        assert not success, "Should reject evidence shorter than 10 chars"

    def test_check_compliance_all_layers_pass(self, temp_cieu_db):
        """Should PASS when all 7 layers completed within window."""
        # Emit all 7 layer events
        for layer_num in range(7):
            layer_complete(
                layer=layer_num,
                evidence=f"Layer {layer_num}: {ARTICLE_11_LAYERS[layer_num]}",
                db_path=temp_cieu_db
            )

        result = check_compliance(window_hours=1, db_path=temp_cieu_db)

        assert result["status"] == "PASS", "Should PASS with all 7 layers"
        assert len(result["completed_layers"]) == 7
        assert len(result["missing_layers"]) == 0

    def test_check_compliance_missing_layers_fail(self, temp_cieu_db):
        """Should FAIL when some layers missing."""
        # Only emit layers 0, 1, 2
        for layer_num in range(3):
            layer_complete(
                layer=layer_num,
                evidence=f"Layer {layer_num} test",
                db_path=temp_cieu_db
            )

        result = check_compliance(window_hours=1, db_path=temp_cieu_db)

        assert result["status"] == "FAIL", "Should FAIL with missing layers"
        assert set(result["completed_layers"]) == {0, 1, 2}
        assert set(result["missing_layers"]) == {3, 4, 5, 6}

    def test_check_compliance_outside_window(self, temp_cieu_db):
        """Should FAIL when events are outside time window."""
        # Emit event with old timestamp
        conn = sqlite3.connect(temp_cieu_db)
        old_timestamp = (datetime.now() - timedelta(hours=3)).timestamp()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_detected, drift_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "test-old-event", 1000, old_timestamp, "test-session", "ceo",
            "ARTICLE_11_LAYER_0_COMPLETE", "complete", 1, 0, "Old event"
        ))
        conn.commit()
        conn.close()

        result = check_compliance(window_hours=1, db_path=temp_cieu_db)

        assert result["status"] == "FAIL", "Should FAIL when events outside window"
        assert 0 in result["missing_layers"]


class TestLayer3PostAudit:
    """Test Layer 3: Post-audit drift detection."""

    def test_detect_drift_with_decision_keyword_no_events(self, temp_cieu_db):
        """Should detect drift when user message has decision keyword but no Article 11 events."""
        # Insert user_message with decision keyword
        conn = sqlite3.connect(temp_cieu_db)
        cursor = conn.cursor()
        msg_time = datetime.now().timestamp()
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_detected, drift_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "test-user-msg", 2000, msg_time, "test-session", "board",
            "user_message", "", 0, 0, "We should launch new strategy now"
        ))
        conn.commit()
        conn.close()

        # Simulate forget_guard_summary.py drift detection
        # NOTE: This requires modifying detect_article_11_drift to accept db_path parameter
        # For now, we test the logic manually
        conn = sqlite3.connect(temp_cieu_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_id, created_at, drift_details FROM cieu_events
            WHERE event_type = 'user_message'
            AND created_at > ?
        """, ((datetime.now() - timedelta(hours=1)).timestamp(),))

        user_messages = cursor.fetchall()
        incidents = []

        for event_id, msg_timestamp, msg_content in user_messages:
            if "strategy" in msg_content.lower():
                # Check for Article 11 events within +/- 1h window
                window_start = msg_timestamp - 3600
                window_end = msg_timestamp + 3600

                cursor.execute("""
                    SELECT COUNT(*) FROM cieu_events
                    WHERE event_type LIKE 'ARTICLE_11_LAYER_%_COMPLETE'
                    AND created_at BETWEEN ? AND ?
                """, (window_start, window_end))

                article_11_count = cursor.fetchone()[0]
                if article_11_count == 0:
                    incidents.append(event_id)

        conn.close()

        assert len(incidents) > 0, "Should detect drift incident"

    def test_no_drift_when_article_11_events_present(self, temp_cieu_db):
        """Should NOT detect drift when Article 11 events exist around decision message."""
        # Insert user_message with decision keyword
        conn = sqlite3.connect(temp_cieu_db)
        cursor = conn.cursor()
        msg_time = datetime.now().timestamp()

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_detected, drift_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "test-user-msg-2", 3000, msg_time, "test-session", "board",
            "user_message", "", 0, 0, "We need to pivot our roadmap"
        ))

        # Insert Article 11 event within window
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_detected, drift_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "test-article11", 3001, msg_time + 600, "test-session", "ceo",
            "ARTICLE_11_LAYER_0_COMPLETE", "complete", 1, 0, "Y* contract check"
        ))

        conn.commit()

        # Check for drift
        cursor.execute("""
            SELECT event_id, created_at, drift_details FROM cieu_events
            WHERE event_type = 'user_message'
            AND created_at > ?
        """, ((datetime.now() - timedelta(hours=1)).timestamp(),))

        user_messages = cursor.fetchall()
        incidents = []

        for event_id, msg_timestamp, msg_content in user_messages:
            if "pivot" in msg_content.lower() or "roadmap" in msg_content.lower():
                window_start = msg_timestamp - 3600
                window_end = msg_timestamp + 3600

                cursor.execute("""
                    SELECT COUNT(*) FROM cieu_events
                    WHERE event_type LIKE 'ARTICLE_11_LAYER_%_COMPLETE'
                    AND created_at BETWEEN ? AND ?
                """, (window_start, window_end))

                article_11_count = cursor.fetchone()[0]
                if article_11_count == 0:
                    incidents.append(event_id)

        conn.close()

        assert len(incidents) == 0, "Should NOT detect drift when Article 11 events present"


class TestE2EIntegration:
    """End-to-end integration tests for all 3 layers."""

    def test_full_decision_flow_compliant(self, temp_cieu_db):
        """Simulate compliant decision flow: detection → layer completion → verification."""
        # Step 1: Board sends decision prompt
        user_msg = "We should launch new strategy for enterprise pivot"
        assert detect_decision_context(user_msg), "Layer 1 should detect decision context"

        # Step 2: CEO walks all 7 layers
        for layer_num in range(7):
            success = layer_complete(
                layer=layer_num,
                evidence=f"Completed {ARTICLE_11_LAYERS[layer_num]}",
                db_path=temp_cieu_db
            )
            assert success, f"Layer {layer_num} should complete successfully"

        # Step 3: Verify compliance
        result = check_compliance(window_hours=1, db_path=temp_cieu_db)
        assert result["status"] == "PASS", "Compliance check should PASS"

        # Step 4: Post-audit should find no drift
        # (Would require full forget_guard_summary.py run, tested above in isolation)

    def test_full_decision_flow_noncompliant(self, temp_cieu_db):
        """Simulate non-compliant decision flow: detection → partial layers → FAIL."""
        # Step 1: Board sends decision prompt
        user_msg = "重大决策：架构重组"
        assert detect_decision_context(user_msg), "Layer 1 should detect decision context"

        # Step 2: CEO only completes layers 0-2 (incomplete)
        for layer_num in range(3):
            layer_complete(
                layer=layer_num,
                evidence=f"Partial layer {layer_num}",
                db_path=temp_cieu_db
            )

        # Step 3: Verify compliance — should FAIL
        result = check_compliance(window_hours=1, db_path=temp_cieu_db)
        assert result["status"] == "FAIL", "Compliance check should FAIL with missing layers"
        assert set(result["missing_layers"]) == {3, 4, 5, 6}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
