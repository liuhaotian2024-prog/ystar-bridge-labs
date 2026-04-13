#!/usr/bin/env python3
"""
E2E test for governance watcher — verifies <5s latency from file change to daemon cache invalidation.
"""
import os
import sys
import time
import json
import tempfile
import shutil
from pathlib import Path

# Add scripts to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from governance_watcher import create_watcher


def test_watcher_basic():
    """Test basic watcher functionality with all three files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create test files
        active_agent = repo / ".ystar_active_agent"
        agents_md = repo / "AGENTS.md"
        session_json = repo / ".ystar_session.json"

        active_agent.write_text("ceo\n")
        agents_md.write_text("# AGENTS\n- RULE: test rule\n")
        session_json.write_text('{"policies": []}\n')

        # Track invalidations
        invalidations = []

        def track_invalidation(changed_files):
            invalidations.append((time.time(), changed_files))

        # Start watcher
        watcher = create_watcher(str(repo), log_fn=print)
        watcher.set_invalidation_callback(track_invalidation)
        watcher.start()

        # Wait for initial hash capture
        time.sleep(0.5)

        # Test 1: Change .ystar_active_agent
        print("\n[TEST] Changing .ystar_active_agent...")
        start = time.time()
        active_agent.write_text("cto\n")
        time.sleep(5)  # Max latency target
        latency = time.time() - start

        assert len(invalidations) > 0, "No invalidation triggered"
        assert ".ystar_active_agent" in invalidations[-1][1], f"Wrong file: {invalidations[-1]}"
        print(f"✓ Active agent change detected in {latency:.1f}s")

        # Test 2: Change AGENTS.md
        print("\n[TEST] Changing AGENTS.md...")
        invalidations.clear()
        start = time.time()
        agents_md.write_text("# AGENTS\n- RULE: new rule\n- POLICY: new policy\n")
        time.sleep(5)
        latency = time.time() - start

        assert len(invalidations) > 0, "No invalidation triggered"
        assert "AGENTS.md" in invalidations[-1][1], f"Wrong file: {invalidations[-1]}"
        print(f"✓ AGENTS.md change detected in {latency:.1f}s")

        # Test 3: Change .ystar_session.json
        print("\n[TEST] Changing .ystar_session.json...")
        invalidations.clear()
        start = time.time()
        session_json.write_text('{"policies": ["new policy"]}\n')
        time.sleep(5)
        latency = time.time() - start

        assert len(invalidations) > 0, "No invalidation triggered"
        assert ".ystar_session.json" in invalidations[-1][1], f"Wrong file: {invalidations[-1]}"
        print(f"✓ Session config change detected in {latency:.1f}s")

        # Stop watcher
        watcher.stop()

    print("\n✅ All tests passed")


def test_watcher_latency():
    """Verify <5s latency target."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        active_agent = repo / ".ystar_active_agent"
        active_agent.write_text("ceo\n")

        invalidations = []

        def track_invalidation(changed_files):
            invalidations.append(time.time())

        watcher = create_watcher(str(repo), log_fn=lambda x: None)
        watcher.set_invalidation_callback(track_invalidation)
        watcher.start()

        # Wait for initial hash
        time.sleep(0.5)

        # Make change and measure latency
        start = time.time()
        active_agent.write_text("cto\n")

        # Wait for invalidation (max 5s)
        timeout = 5
        while not invalidations and (time.time() - start) < timeout:
            time.sleep(0.1)

        assert invalidations, f"No invalidation within {timeout}s"

        latency = invalidations[0] - start
        print(f"\n✓ Latency: {latency:.2f}s (target: <5s)")
        assert latency < 5, f"Latency {latency:.2f}s exceeds 5s target"

        watcher.stop()

    print("✅ Latency test passed")


def test_watcher_fail_open():
    """Verify watcher failure doesn't crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Don't create files — watcher should handle missing files gracefully
        watcher = create_watcher(str(repo), log_fn=lambda x: None)

        def crash_callback(changed_files):
            raise RuntimeError("Simulated callback crash")

        watcher.set_invalidation_callback(crash_callback)
        watcher.start()

        # Should not crash
        time.sleep(1)

        watcher.stop()

    print("✅ Fail-open test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Governance Watcher E2E Test")
    print("=" * 60)

    test_watcher_basic()
    test_watcher_latency()
    test_watcher_fail_open()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
