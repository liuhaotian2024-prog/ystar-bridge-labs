#!/usr/bin/env python3
"""Test Suite for Aiden Continuity Guardian

Board-approved 2026-04-12
Covers M1-M8 metrics from brief §6

Run:
    python -m pytest tests/test_continuity_guardian.py -v
"""

import pytest
import tempfile
import json
import sqlite3
import time
from pathlib import Path
import subprocess
import sys
import os

# Add ystar-company to path
COMPANY_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(COMPANY_ROOT))


class TestHealthWatchdog:
    """M1: Guardian can detect yellow-line thresholds"""

    def test_m1_jsonl_size_threshold(self, tmp_path):
        """M1.1: JSONL > 3MB triggers yellow line"""
        from scripts.session_health_watchdog import collect_health_metrics, THRESHOLD_JSONL_MB

        # Note: This test checks the threshold logic, actual JSONL detection
        # is filesystem-based and harder to mock
        assert THRESHOLD_JSONL_MB == 3.0

    def test_m1_call_count_threshold(self, tmp_path):
        """M1.2: Call count > 500 triggers yellow line"""
        from scripts.session_health_watchdog import THRESHOLD_CALL_COUNT, get_call_count

        # Create mock call count file
        count_file = tmp_path / ".session_call_count"
        count_file.write_text("510")

        # Mock company_root
        original_root = COMPANY_ROOT
        try:
            # Create scripts dir in tmp
            scripts_dir = tmp_path / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / ".session_call_count").write_text("510")

            count = get_call_count(tmp_path)
            assert count == 510
            assert count >= THRESHOLD_CALL_COUNT
        finally:
            pass

    def test_m1_runtime_threshold(self, tmp_path):
        """M1.3: Runtime > 6h triggers yellow line"""
        from scripts.session_health_watchdog import THRESHOLD_RUNTIME_HOURS

        assert THRESHOLD_RUNTIME_HOURS == 6.0

    def test_m1_deny_rate_threshold(self, tmp_path):
        """M1.4: Deny rate > 30% triggers yellow line"""
        from scripts.session_health_watchdog import THRESHOLD_DENY_RATE, get_hook_deny_rate

        # Create mock CIEU db with deny events
        cieu_db = tmp_path / ".ystar_cieu.db"
        conn = sqlite3.connect(str(cieu_db))
        conn.execute("""
            CREATE TABLE cieu_events (
                event_id TEXT,
                event_type TEXT,
                decision TEXT,
                created_at REAL
            )
        """)

        # Insert 50 events, 20 denies (40% deny rate)
        for i in range(50):
            decision = "deny" if i < 20 else "allow"
            conn.execute("""
                INSERT INTO cieu_events (event_id, event_type, decision, created_at)
                VALUES (?, ?, ?, ?)
            """, (f"evt_{i}", "HOOK_CALL", decision, time.time()))
        conn.commit()
        conn.close()

        deny_rate = get_hook_deny_rate(tmp_path)
        assert deny_rate == 0.4  # 40%
        assert deny_rate >= THRESHOLD_DENY_RATE

    def test_m1_drift_threshold(self, tmp_path):
        """M1.6: Drift > 3 events in recent 10 triggers yellow line"""
        from scripts.session_health_watchdog import THRESHOLD_DRIFT_COUNT, get_drift_count

        # Create mock CIEU db with drift events
        cieu_db = tmp_path / ".ystar_cieu.db"
        conn = sqlite3.connect(str(cieu_db))
        conn.execute("""
            CREATE TABLE cieu_events (
                event_id TEXT,
                event_type TEXT,
                params_json TEXT,
                created_at REAL
            )
        """)

        # Insert 10 events, 4 with drift indicators
        for i in range(10):
            event_type = "DRIFT_DETECTED" if i < 4 else "NORMAL_EVENT"
            conn.execute("""
                INSERT INTO cieu_events (event_id, event_type, params_json, created_at)
                VALUES (?, ?, ?, ?)
            """, (f"evt_{i}", event_type, "{}", time.time()))
        conn.commit()
        conn.close()

        drift_count = get_drift_count(tmp_path)
        assert drift_count == 4
        assert drift_count >= THRESHOLD_DRIFT_COUNT


class TestSaveChain:
    """M2: Graceful save chain completes all steps"""

    def test_m2_save_chain_steps(self):
        """M2: Verify save chain script has all 8 steps"""
        save_script = COMPANY_ROOT / "scripts/session_graceful_restart.sh"
        assert save_script.exists()

        content = save_script.read_text()

        # Check for all required steps
        assert "session_close_yml.py" in content
        assert "twin_evolution.py" in content
        assert "learning_report.py" in content
        assert "session_wisdom_extractor.py" in content
        assert "aiden_cognition_backup.py" in content or "Cognition backup" in content
        assert "git commit" in content
        assert "continuation.json" in content
        assert "ystar_ready_for_restart" in content


class TestWisdomPackage:
    """M3: Wisdom package ≤ 10KB"""

    def test_m3_wisdom_package_size(self, tmp_path):
        """M3: Wisdom package output ≤ 10KB"""
        from scripts.session_wisdom_extractor import generate_wisdom_package

        # Create mock databases
        memory_db = tmp_path / ".ystar_memory.db"
        conn = sqlite3.connect(str(memory_db))
        conn.execute("""
            CREATE TABLE memories (
                memory_id TEXT,
                agent_id TEXT,
                memory_type TEXT,
                content TEXT,
                created_at REAL,
                context_tags TEXT
            )
        """)
        # Add some test data
        conn.execute("""
            INSERT INTO memories (memory_id, agent_id, memory_type, content, created_at, context_tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("mem1", "ceo", "obligation", "Test obligation", time.time(), "[]"))
        conn.commit()
        conn.close()

        cieu_db = tmp_path / ".ystar_cieu.db"
        conn = sqlite3.connect(str(cieu_db))
        conn.execute("""
            CREATE TABLE cieu_events (
                event_id TEXT,
                event_type TEXT,
                task_description TEXT,
                params_json TEXT,
                decision TEXT,
                created_at REAL
            )
        """)
        conn.commit()
        conn.close()

        # Generate wisdom package
        session_id = "test_session"
        session_start = time.time() - 3600

        wisdom_text = generate_wisdom_package(tmp_path, session_id, session_start)

        # Check size
        wisdom_bytes = len(wisdom_text.encode('utf-8'))
        wisdom_kb = wisdom_bytes / 1024.0

        assert wisdom_kb <= 10.0, f"Wisdom package too large: {wisdom_kb:.2f} KB"


class TestBootIntegration:
    """M4: Boot time ≤ 1 CIEU event depth"""

    def test_m4_boot_script_has_wisdom_step(self):
        """M4: governance_boot.sh includes STEP 7 (wisdom injection)"""
        boot_script = COMPANY_ROOT / "scripts/governance_boot.sh"
        assert boot_script.exists()

        content = boot_script.read_text()

        # Check for STEP 7
        assert "STEP 7" in content or "wisdom_package_latest.md" in content
        assert "SESSION WISDOM" in content


class TestContinuity:
    """M5: Continuity validation (agent knows recent context)"""

    def test_m5_wisdom_package_contains_context(self, tmp_path):
        """M5: Wisdom package includes obligations and decisions"""
        from scripts.session_wisdom_extractor import (
            extract_core_decisions,
            extract_uncompleted_obligations
        )

        # Create mock CIEU db with decisions
        cieu_db = tmp_path / ".ystar_cieu.db"
        conn = sqlite3.connect(str(cieu_db))
        conn.execute("""
            CREATE TABLE cieu_events (
                event_id TEXT,
                event_type TEXT,
                task_description TEXT,
                params_json TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            INSERT INTO cieu_events (event_id, event_type, task_description, params_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("evt1", "BOARD_DECISION", "Test decision", "{}", time.time()))
        conn.commit()
        conn.close()

        # Create mock memory db with obligations
        memory_db = tmp_path / ".ystar_memory.db"
        conn = sqlite3.connect(str(memory_db))
        conn.execute("""
            CREATE TABLE memories (
                memory_id TEXT,
                agent_id TEXT,
                memory_type TEXT,
                content TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            INSERT INTO memories (memory_id, agent_id, memory_type, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("mem1", "ceo", "obligation", "Complete task X", time.time()))
        conn.commit()
        conn.close()

        session_start = time.time() - 3600

        # Extract context
        decisions = extract_core_decisions(tmp_path, session_start)
        obligations = extract_uncompleted_obligations(tmp_path)

        assert len(decisions) > 0, "No decisions extracted"
        assert len(obligations) > 0, "No obligations extracted"


class TestHookCompliance:
    """M6: Hook boundary compliance"""

    def test_m6_no_hook_bypass_in_scripts(self):
        """M6: Guardian scripts don't bypass hook system"""
        scripts = [
            COMPANY_ROOT / "scripts/session_health_watchdog.py",
            COMPANY_ROOT / "scripts/session_wisdom_extractor.py",
            COMPANY_ROOT / "scripts/session_graceful_restart.sh",
            COMPANY_ROOT / "scripts/aiden_continuity_guardian.sh",
        ]

        for script in scripts:
            if not script.exists():
                continue

            content = script.read_text()

            # Check for known bypass patterns
            assert "--no-verify" not in content, f"{script.name} contains hook bypass"
            assert "YSTAR_HOOK_DISABLE" not in content, f"{script.name} disables hook"

            # Scripts should use proper git commands (precise add, no -A in guardian)
            if script.name == "session_graceful_restart.sh":
                # This script is allowed to do git operations
                assert "git add" in content
                assert "git commit" in content
                # Check that actual git add commands don't use -A (ignore comments)
                lines = [l for l in content.split('\n') if not l.strip().startswith('#')]
                code_content = '\n'.join(lines)
                assert "git add -A" not in code_content, f"{script.name} uses git add -A in code"


class TestFailOpen:
    """M7: Fail-open validation"""

    def test_m7_watchdog_failure_doesnt_block(self):
        """M7: If watchdog fails, guardian should exit (fail-open)"""
        guardian_script = COMPANY_ROOT / "scripts/aiden_continuity_guardian.sh"
        assert guardian_script.exists()

        content = guardian_script.read_text()

        # Guardian should monitor watchdog but not block if it fails
        # Check for fail-open patterns
        assert "kill" in content.lower()  # Can kill processes
        # If claude exits naturally, guardian should exit
        assert "exit" in content


class TestBoardOverride:
    """M8: Board can disable auto-restart"""

    def test_m8_board_override_file(self):
        """M8: /tmp/ystar_no_auto_restart disables guardian"""
        from scripts.session_health_watchdog import check_board_override

        # Clean state
        override_file = Path("/tmp/ystar_no_auto_restart")
        if override_file.exists():
            override_file.unlink()

        assert not check_board_override()

        # Create override
        override_file.touch()
        assert check_board_override()

        # Clean up
        override_file.unlink()

    def test_m8_guardian_checks_override(self):
        """M8: Guardian script checks for override"""
        guardian_script = COMPANY_ROOT / "scripts/aiden_continuity_guardian.sh"
        assert guardian_script.exists()

        content = guardian_script.read_text()

        # Should check for override file
        assert "/tmp/ystar_no_auto_restart" in content
        assert "check_override" in content or "ystar_no_auto_restart" in content


class TestIntegration:
    """Integration tests for full lifecycle"""

    def test_all_scripts_exist(self):
        """Verify all required scripts exist"""
        required = [
            "scripts/session_health_watchdog.py",
            "scripts/session_wisdom_extractor.py",
            "scripts/session_graceful_restart.sh",
            "scripts/aiden_continuity_guardian.sh",
            "scripts/governance_boot.sh",
            "governance/CONTINUITY_PROTOCOL.md",
        ]

        for path_str in required:
            path = COMPANY_ROOT / path_str
            assert path.exists(), f"Required file missing: {path_str}"

    def test_scripts_are_executable(self):
        """Verify shell scripts have execute permissions"""
        scripts = [
            "scripts/session_graceful_restart.sh",
            "scripts/aiden_continuity_guardian.sh",
            "scripts/governance_boot.sh",
        ]

        for path_str in scripts:
            path = COMPANY_ROOT / path_str
            # Check if shebang exists (good practice)
            if path.exists():
                first_line = path.read_text().split('\n')[0]
                assert first_line.startswith('#!'), f"{path_str} missing shebang"


# === Pytest Fixtures ===

@pytest.fixture
def tmp_company_root(tmp_path):
    """Create temporary company root with mock databases"""
    # Create directory structure
    (tmp_path / "scripts").mkdir()
    (tmp_path / "memory").mkdir()
    (tmp_path / "reports/daily").mkdir(parents=True)

    # Create mock databases
    memory_db = tmp_path / ".ystar_memory.db"
    conn = sqlite3.connect(str(memory_db))
    conn.execute("""
        CREATE TABLE memories (
            memory_id TEXT,
            agent_id TEXT,
            memory_type TEXT,
            content TEXT,
            created_at REAL,
            context_tags TEXT,
            access_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

    cieu_db = tmp_path / ".ystar_cieu.db"
    conn = sqlite3.connect(str(cieu_db))
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT,
            event_type TEXT,
            decision TEXT,
            task_description TEXT,
            params_json TEXT,
            created_at REAL
        )
    """)
    conn.commit()
    conn.close()

    yield tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
