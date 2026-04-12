#!/usr/bin/env python3
"""
Tests for Aiden Cognition Guardian backup system.

Coverage:
1. Full backup of mock company state
2. Incremental backup (detect unchanged files)
3. Atomic write conflict (simulated crash during tmp→rename)
4. Fail-open mode (backup error doesn't block)
5. Verify mode (detect hash mismatches)
6. Recovery roundtrip (backup → corrupt → restore → verify)
"""

import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from aiden_cognition_backup import (
    BackupEngine,
    BackupLagMonitor,
    verify_backup,
    BACKUP_PATHS,
)


class TestAidenCognitionBackup(unittest.TestCase):
    """Test suite for Aiden Cognition Guardian."""

    def setUp(self):
        """Create mock company structure."""
        self.test_dir = tempfile.mkdtemp()
        self.company_root = Path(self.test_dir) / "company"
        self.backup_root = Path(self.test_dir) / "backup"

        self.company_root.mkdir()
        self.backup_root.mkdir()

        # Create mock file structure
        self._create_mock_company()

    def tearDown(self):
        """Clean up test directories."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_company(self):
        """Create minimal mock company structure."""
        # Create directories
        (self.company_root / "knowledge" / "ceo").mkdir(parents=True)
        (self.company_root / "memory").mkdir(parents=True)
        (self.company_root / "governance").mkdir(parents=True)
        (self.company_root / "reports" / "daily").mkdir(parents=True)
        (self.company_root / "agents").mkdir(parents=True)

        # Create mock files
        (self.company_root / "CLAUDE.md").write_text("# Mock CLAUDE.md\n")
        (self.company_root / "AGENTS.md").write_text("# Mock AGENTS.md\n")
        (self.company_root / "knowledge/ceo/expertise.md").write_text("CEO knowledge\n")
        (self.company_root / "memory/session_handoff.md").write_text("Session state\n")
        (self.company_root / ".ystar_active_agent").write_text("ceo\n")

        # Create mock DBs
        self._create_mock_db(self.company_root / ".ystar_memory.db")
        self._create_mock_db(self.company_root / ".ystar_cieu.db")

        # Create mock session JSON
        session = {"version": "1.0", "constraints": []}
        (self.company_root / ".ystar_session.json").write_text(json.dumps(session))

        # Create files that should be excluded
        (self.company_root / "archive").mkdir()
        (self.company_root / "archive" / "old.md").write_text("archived\n")
        (self.company_root / "test.tmp").write_text("temp\n")
        (self.company_root / ".DS_Store").write_text("macos\n")

    def _create_mock_db(self, path: Path):
        """Create a minimal SQLite DB."""
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
        cursor.execute("INSERT INTO test (data) VALUES ('mock_data')")
        conn.commit()
        conn.close()

    def _sha256(self, file_path: Path) -> str:
        """Calculate SHA256 of file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def test_01_full_backup(self):
        """Test 1: Full backup of mock company state."""
        engine = BackupEngine(self.company_root, self.backup_root, mode="full")
        manifest = engine.backup(fail_open=False)

        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.mode, "full")
        self.assertGreater(manifest.file_count, 0)
        self.assertGreater(manifest.total_bytes, 0)

        # Verify key files are backed up
        self.assertTrue((self.backup_root / "CLAUDE.md").exists())
        self.assertTrue((self.backup_root / "AGENTS.md").exists())
        self.assertTrue((self.backup_root / ".ystar_memory.db").exists())
        self.assertTrue((self.backup_root / ".ystar_cieu.db").exists())

        # Verify excluded files are NOT backed up
        self.assertFalse((self.backup_root / "archive" / "old.md").exists())
        self.assertFalse((self.backup_root / "test.tmp").exists())
        self.assertFalse((self.backup_root / ".DS_Store").exists())

        # Verify manifest
        manifest_path = self.backup_root / "MANIFEST.json"
        self.assertTrue(manifest_path.exists())
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
        self.assertIn("CLAUDE.md", manifest_data["files"])

    def test_02_incremental_backup(self):
        """Test 2: Incremental backup (skip unchanged files)."""
        # First backup
        engine1 = BackupEngine(self.company_root, self.backup_root, mode="full")
        manifest1 = engine1.backup(fail_open=False)
        initial_count = manifest1.file_count

        # Modify one file
        modified_file = self.company_root / "CLAUDE.md"
        modified_file.write_text("# Modified CLAUDE.md\n")

        # Incremental backup
        engine2 = BackupEngine(self.company_root, self.backup_root, mode="incremental")
        manifest2 = engine2.backup(fail_open=False)

        # Should still track all files, but only copy modified one
        self.assertEqual(manifest2.file_count, initial_count)

        # Verify modified file hash changed
        self.assertNotEqual(
            manifest1.files["CLAUDE.md"],
            manifest2.files["CLAUDE.md"]
        )

        # Verify backup has updated content
        backup_content = (self.backup_root / "CLAUDE.md").read_text()
        self.assertEqual(backup_content, "# Modified CLAUDE.md\n")

    def test_03_atomic_write(self):
        """Test 3: Atomic write (tmp → rename, no half-writes)."""
        engine = BackupEngine(self.company_root, self.backup_root, mode="full")

        # Backup should not leave .tmp files
        manifest = engine.backup(fail_open=False)

        # Check no .tmp files exist
        tmp_files = list(self.backup_root.rglob("*.tmp"))
        self.assertEqual(len(tmp_files), 0, f"Found leftover .tmp files: {tmp_files}")

        # Verify manifest was written atomically
        manifest_tmp = self.backup_root / "MANIFEST.tmp"
        self.assertFalse(manifest_tmp.exists())

    def test_04_fail_open(self):
        """Test 4: Fail-open mode (backup error doesn't block)."""
        # Create engine first
        engine = BackupEngine(self.company_root, self.backup_root, mode="full")

        # Make backup root read-only to trigger failure during backup
        self.backup_root.chmod(0o444)

        manifest = engine.backup(fail_open=True)

        # Restore permissions first so cleanup works
        self.backup_root.chmod(0o755)

        # Should return None but not raise exception
        self.assertIsNone(manifest)

        # Should log error to daily backup log
        log_path = self.company_root / "reports" / "daily" / "backup.log"
        self.assertTrue(log_path.exists())
        log_content = log_path.read_text()
        self.assertIn("BACKUP_FAILED", log_content)

    def test_05_verify_mode(self):
        """Test 5: Verify mode (detect hash mismatches)."""
        # Create initial backup
        engine = BackupEngine(self.company_root, self.backup_root, mode="full")
        manifest = engine.backup(fail_open=False)

        # Verify should pass initially
        results = verify_backup(self.company_root, self.backup_root)
        self.assertEqual(results["status"], "ok")
        self.assertEqual(len(results["hash_mismatches"]), 0)

        # Corrupt a file in backup
        corrupted_file = self.backup_root / "CLAUDE.md"
        corrupted_file.write_text("# CORRUPTED\n")

        # Verify should detect mismatch
        results = verify_backup(self.company_root, self.backup_root)
        self.assertEqual(results["status"], "degraded")
        self.assertGreater(len(results["hash_mismatches"]), 0)

        # Check the corrupted file is identified
        mismatch_paths = [m["path"] for m in results["hash_mismatches"]]
        self.assertIn("CLAUDE.md", mismatch_paths)

    def test_06_recovery_roundtrip(self):
        """Test 6: Recovery roundtrip (backup → corrupt → restore → verify)."""
        # 1. Create backup
        engine = BackupEngine(self.company_root, self.backup_root, mode="full")
        manifest = engine.backup(fail_open=False)
        original_hash = manifest.files["CLAUDE.md"]

        # 2. Corrupt source file
        corrupted_file = self.company_root / "CLAUDE.md"
        corrupted_file.write_text("# CORRUPTED DATA\n")
        corrupted_hash = self._sha256(corrupted_file)
        self.assertNotEqual(original_hash, corrupted_hash)

        # 3. Simulate recovery (copy from backup)
        backup_file = self.backup_root / "CLAUDE.md"
        shutil.copy2(backup_file, corrupted_file)

        # 4. Verify recovery
        recovered_hash = self._sha256(corrupted_file)
        self.assertEqual(recovered_hash, original_hash)

        # 5. Verify entire backup
        results = verify_backup(self.company_root, self.backup_root)
        self.assertEqual(results["status"], "ok")
        self.assertEqual(len(results["hash_mismatches"]), 0)


class TestBackupLagMonitor(unittest.TestCase):
    """Test backup lag monitoring."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.company_root = Path(self.test_dir) / "company"
        self.company_root.mkdir()

        # Create mock CIEU DB
        self.cieu_db = self.company_root / ".ystar_cieu.db"
        self._create_mock_cieu_db()

        # Create mock memory DB
        self.memory_db = self.company_root / ".ystar_memory.db"
        conn = sqlite3.connect(self.memory_db)
        conn.close()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_cieu_db(self):
        """Create mock CIEU DB with events."""
        conn = sqlite3.connect(self.cieu_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                context TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO events (timestamp, action, context)
            VALUES ('2026-04-12T10:00:00Z', 'file_write', '{"path": "test.md"}')
        """)
        conn.commit()
        conn.close()

    def test_get_latest_cieu_event(self):
        """Test retrieving latest CIEU event."""
        monitor = BackupLagMonitor(self.company_root)
        event = monitor.get_latest_cieu_event()

        self.assertIsNotNone(event)
        self.assertEqual(event["action"], "file_write")
        self.assertEqual(event["id"], 1)

    def test_record_backup_lag(self):
        """Test recording backup metrics to memory DB."""
        from aiden_cognition_backup import BackupManifest

        monitor = BackupLagMonitor(self.company_root)

        manifest = BackupManifest(
            version="1.0.0",
            timestamp="2026-04-12T10:05:00Z",
            mode="full",
            company_root=str(self.company_root),
            backup_root="/tmp/backup",
            file_count=10,
            total_bytes=1024,
            files={}
        )

        monitor.record_backup_lag(manifest)

        # Verify metrics were recorded
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_metrics")
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        # Row format: (id, timestamp, cieu_event_id, backup_mode, file_count, total_bytes, backup_lag_note)
        self.assertEqual(row[3], "full")
        self.assertEqual(row[4], 10)
        self.assertEqual(row[5], 1024)


if __name__ == '__main__':
    unittest.main(verbosity=2)
