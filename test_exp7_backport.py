#!/usr/bin/env python3
"""
E2E test for exp7 watcher backport
Verifies daemon picks up .ystar_active_agent changes within 5s
"""
import os
import sys
import time
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent
ACTIVE_AGENT_FILE = REPO_ROOT / ".ystar_active_agent"
TEST_FILE = REPO_ROOT / "test_exp7_sentinel.txt"


def read_active_agent():
    """Read current active agent."""
    if ACTIVE_AGENT_FILE.exists():
        return ACTIVE_AGENT_FILE.read_text().strip()
    return None


def write_active_agent(agent_id):
    """Write active agent (simulates sub-agent writing it)."""
    ACTIVE_AGENT_FILE.write_text(f"{agent_id}\n")
    print(f"[test] Wrote .ystar_active_agent = {agent_id}")


def test_git_commit(agent_id):
    """Try to commit as given agent. Returns True if successful."""
    os.chdir(REPO_ROOT)
    try:
        # Create a test file change
        TEST_FILE.write_text(f"Test commit from {agent_id} at {time.time()}\n")
        subprocess.run(["git", "add", str(TEST_FILE)], check=True, capture_output=True)

        result = subprocess.run(
            ["git", "commit", "-m", f"test: exp7 watcher backport e2e ({agent_id})"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"[test] ✅ Commit succeeded as {agent_id}")
            return True
        else:
            print(f"[test] ❌ Commit failed as {agent_id}: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"[test] ❌ Commit error: {e}")
        return False


def cleanup_test_commit():
    """Reset the test commit."""
    os.chdir(REPO_ROOT)
    try:
        subprocess.run(["git", "reset", "--soft", "HEAD~1"], capture_output=True)
        TEST_FILE.unlink(missing_ok=True)
        subprocess.run(["git", "restore", "--staged", str(TEST_FILE)], capture_output=True)
        print("[test] Cleaned up test commit")
    except Exception:
        pass


def main():
    print("=== exp7 Watcher Backport E2E Test ===\n")

    # Save original agent
    original_agent = read_active_agent()
    print(f"[test] Original agent: {original_agent}")

    # Step 1: Simulate sub-agent drift (write different agent ID)
    print("\n[1] Simulating sub-agent drift...")
    write_active_agent("eng-kernel")
    time.sleep(0.5)  # Give filesystem time

    # Step 2: Wait for watcher (max 5s, check every 0.5s)
    print("[2] Waiting up to 5s for daemon watcher to pick up change...")
    max_wait = 5.0
    start = time.time()

    while time.time() - start < max_wait:
        # Simulate sub-agent exiting (restore original agent)
        write_active_agent(original_agent or "cto")
        time.sleep(0.5)

        # Check if daemon picked up the change by trying a commit
        if test_git_commit(original_agent or "cto"):
            elapsed = time.time() - start
            print(f"\n✅ SUCCESS: Daemon picked up change in {elapsed:.1f}s")
            print("   Watcher eliminated cache lock — no manual daemon restart needed")

            cleanup_test_commit()

            # Restore state
            write_active_agent(original_agent or "cto")
            return 0

        time.sleep(0.5)

    # Test failed
    print(f"\n❌ FAIL: Daemon did not pick up change within {max_wait}s")
    print("   Expected: commit succeeds after .ystar_active_agent write")
    print("   Actual: still getting 'current agent is X' error")

    cleanup_test_commit()
    write_active_agent(original_agent or "cto")
    return 1


if __name__ == "__main__":
    sys.exit(main())
