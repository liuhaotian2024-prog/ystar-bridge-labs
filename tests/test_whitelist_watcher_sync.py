#!/usr/bin/env python3
"""
E2E test: governance_watcher.py whitelist sync mechanism (A018 Phase 1).

Test scenario:
1. Start watcher monitoring governance/whitelist/*.yaml
2. Hand-edit constitutional.yaml (or create new test.yaml)
3. Verify daemon loads new version within 5s
4. Verify WHITELIST_UPDATE CIEU event emitted

Author: eng-kernel (Leo Chen)
Date: 2026-04-13
"""
import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add scripts/ to path for governance_watcher import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from governance_watcher import create_watcher


def test_whitelist_file_change_triggers_reload_and_event():
    """
    E2E: Edit governance/whitelist/constitutional.yaml → watcher detects → emits event.
    """
    # Setup: temp repo structure
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        whitelist_dir = repo_root / "governance" / "whitelist"
        whitelist_dir.mkdir(parents=True, exist_ok=True)

        # Create initial YAML file
        test_yaml = whitelist_dir / "constitutional.yaml"
        test_yaml.write_text("version: 1.0.0\nrules: []\n")

        # Track events
        events_emitted = []
        cache_invalidations = []

        def mock_cieu_emit(event_type, data, severity="info"):
            events_emitted.append({
                "type": event_type,
                "data": data,
                "severity": severity
            })

        def mock_cache_invalidate(changed_files):
            cache_invalidations.append(changed_files)

        # Start watcher
        watcher = create_watcher(
            str(repo_root),
            log_fn=lambda msg: print(f"[test-log] {msg}"),
            cieu_emit_fn=mock_cieu_emit
        )
        watcher.set_invalidation_callback(mock_cache_invalidate)
        watcher.start()

        # Wait for initial poll
        time.sleep(2.5)

        # Modify YAML file
        print("\n[TEST] Modifying constitutional.yaml...")
        test_yaml.write_text("version: 2.0.0\nrules: [new_rule]\n")

        # Wait for watcher to detect change (target: <5s, actual: ~2s poll)
        time.sleep(5)

        # Verify cache invalidation
        assert len(cache_invalidations) > 0, "Cache invalidation callback not triggered"
        assert any("constitutional.yaml" in str(files) for files in cache_invalidations), \
            "constitutional.yaml not in invalidation list"

        # Verify CIEU event emission
        assert len(events_emitted) > 0, "No CIEU events emitted"
        whitelist_events = [e for e in events_emitted if e["type"] == "WHITELIST_UPDATE"]
        assert len(whitelist_events) > 0, "No WHITELIST_UPDATE event emitted"

        # Verify event data
        event = whitelist_events[0]
        assert "governance/whitelist/constitutional.yaml" in event["data"]["changed_files"], \
            "constitutional.yaml not in WHITELIST_UPDATE event"

        # Cleanup
        watcher.stop()

        print("\n[TEST PASS] ✅ Whitelist watcher sync mechanism working:")
        print(f"  - Cache invalidations: {len(cache_invalidations)}")
        print(f"  - CIEU events emitted: {len(whitelist_events)}")
        print(f"  - Latency: <5s (target met)")


def test_whitelist_file_deletion_detected():
    """
    E2E: Delete whitelist YAML → watcher detects → emits event with [DELETED] marker.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        whitelist_dir = repo_root / "governance" / "whitelist"
        whitelist_dir.mkdir(parents=True, exist_ok=True)

        # Create file
        test_yaml = whitelist_dir / "temp_rule.yaml"
        test_yaml.write_text("version: 1.0.0\n")

        events_emitted = []

        def mock_cieu_emit(event_type, data, severity="info"):
            events_emitted.append({"type": event_type, "data": data})

        watcher = create_watcher(
            str(repo_root),
            log_fn=lambda msg: print(f"[test-log] {msg}"),
            cieu_emit_fn=mock_cieu_emit
        )
        watcher.start()
        time.sleep(2.5)  # Initial poll

        # Delete file
        print("\n[TEST] Deleting temp_rule.yaml...")
        test_yaml.unlink()
        time.sleep(5)  # Wait for detection

        # Verify deletion detected
        whitelist_events = [e for e in events_emitted if e["type"] == "WHITELIST_UPDATE"]
        assert len(whitelist_events) > 0, "No WHITELIST_UPDATE event for deletion"

        deleted_files = [f for f in whitelist_events[0]["data"]["changed_files"] if "[DELETED]" in f]
        assert len(deleted_files) > 0, "Deletion not marked in event"
        assert "temp_rule.yaml" in deleted_files[0], "Wrong file marked as deleted"

        watcher.stop()
        print("\n[TEST PASS] ✅ Whitelist file deletion detected correctly")


def test_new_whitelist_file_creation():
    """
    E2E: Create new YAML file in whitelist/ → watcher detects → triggers reload.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        whitelist_dir = repo_root / "governance" / "whitelist"
        whitelist_dir.mkdir(parents=True, exist_ok=True)

        cache_invalidations = []

        def mock_cache_invalidate(changed_files):
            cache_invalidations.append(changed_files)

        watcher = create_watcher(str(repo_root), log_fn=lambda msg: None)
        watcher.set_invalidation_callback(mock_cache_invalidate)
        watcher.start()
        time.sleep(2.5)  # Initial poll

        # Create new file
        new_yaml = whitelist_dir / "new_procedure.yaml"
        new_yaml.write_text("id: test_procedure\ntitle: Test\n")
        time.sleep(5)

        # Verify detection
        assert len(cache_invalidations) > 0, "New file creation not detected"
        assert any("new_procedure.yaml" in str(files) for files in cache_invalidations), \
            "new_procedure.yaml not in invalidation"

        watcher.stop()
        print("\n[TEST PASS] ✅ New whitelist file creation detected")


if __name__ == "__main__":
    print("=== Whitelist Watcher E2E Test Suite ===\n")

    try:
        test_whitelist_file_change_triggers_reload_and_event()
        test_whitelist_file_deletion_detected()
        test_new_whitelist_file_creation()

        print("\n=== ALL TESTS PASSED ===")
        print("✅ Watcher detects YAML changes within 5s")
        print("✅ WHITELIST_UPDATE events emitted correctly")
        print("✅ Cache invalidation callback triggered")
        print("✅ File creation/deletion handled")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
