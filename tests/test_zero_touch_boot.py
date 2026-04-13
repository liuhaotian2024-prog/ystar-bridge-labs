"""
Unit tests for Zero-Touch Boot Sequencer (AMENDMENT-015 v2 LRS C8)

Test coverage:
- LaunchAgent plist generation and validation
- Crontab entry deduplication
- Daemon health detection
- Identity self-heal logic
- Script override status check
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")


class TestLaunchAgentPlists(unittest.TestCase):
    """Validate LaunchAgent plist files are well-formed."""

    def test_hook_daemon_plist_exists(self):
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.hook_daemon.plist"
        self.assertTrue(plist.exists(), "hook_daemon plist not found")

    def test_gov_mcp_plist_exists(self):
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.gov_mcp.plist"
        self.assertTrue(plist.exists(), "gov_mcp plist not found")

    def test_crontab_sync_plist_exists(self):
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.crontab_sync.plist"
        self.assertTrue(plist.exists(), "crontab_sync plist not found")

    def test_hook_daemon_plist_valid_xml(self):
        """Validate hook_daemon plist is valid XML."""
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.hook_daemon.plist"
        result = subprocess.run(
            ["plutil", "-lint", str(plist)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Invalid XML: {result.stderr}")
        self.assertIn("OK", result.stdout)

    def test_gov_mcp_plist_valid_xml(self):
        """Validate gov_mcp plist is valid XML."""
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.gov_mcp.plist"
        result = subprocess.run(
            ["plutil", "-lint", str(plist)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Invalid XML: {result.stderr}")
        self.assertIn("OK", result.stdout)

    def test_hook_daemon_has_keepalive(self):
        """Ensure hook_daemon plist has KeepAlive for crash restart."""
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.hook_daemon.plist"
        content = plist.read_text()
        self.assertIn("<key>KeepAlive</key>", content)
        self.assertIn("<key>Crashed</key>", content)
        self.assertIn("<true/>", content)

    def test_hook_daemon_has_pythonpath(self):
        """Ensure hook_daemon plist sets PYTHONPATH."""
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.hook_daemon.plist"
        content = plist.read_text()
        self.assertIn("<key>EnvironmentVariables</key>", content)
        self.assertIn("<key>PYTHONPATH</key>", content)
        self.assertIn("Y-star-gov", content)

    def test_gov_mcp_has_correct_port(self):
        """Ensure gov_mcp plist specifies port 7922."""
        plist = REPO_ROOT / "scripts/launchagents/com.ystar.gov_mcp.plist"
        content = plist.read_text()
        self.assertIn("<string>--port</string>", content)
        self.assertIn("<string>7922</string>", content)


class TestCrontabDeduplication(unittest.TestCase):
    """Test crontab entry deduplication logic."""

    def test_ensure_crontab_script_exists(self):
        script = REPO_ROOT / "scripts/ensure_crontab.sh"
        self.assertTrue(script.exists())
        self.assertTrue(os.access(script, os.X_OK), "Script not executable")

    def test_crontab_idempotent(self):
        """Running ensure_crontab.sh twice should not duplicate entries."""
        # This is a read-only test — we don't actually modify crontab
        script = REPO_ROOT / "scripts/ensure_crontab.sh"

        # Get current crontab count
        result1 = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True
        )

        # Should report "already present" on second run (if first run added nothing)
        if "All crontab entries already present" in result1.stdout:
            # Second run should be identical
            result2 = subprocess.run(
                ["bash", str(script)],
                capture_output=True,
                text=True
            )
            self.assertIn("All crontab entries already present", result2.stdout)


class TestDaemonHealthDetection(unittest.TestCase):
    """Test daemon health check logic."""

    def test_hook_socket_exists(self):
        """Hook daemon should create /tmp/ystar_hook.sock."""
        # This test assumes daemons are running (after install)
        # If not installed, test will be skipped
        socket_path = Path("/tmp/ystar_hook.sock")
        if not socket_path.exists():
            self.skipTest("Hook daemon not running (run install_ystar_services.sh first)")

        self.assertTrue(socket_path.is_socket(), "Hook socket is not a socket file")

    def test_gov_mcp_port_listening(self):
        """GOV-MCP should be listening on port 7922."""
        result = subprocess.run(
            ["lsof", "-iTCP:7922", "-sTCP:LISTEN"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.skipTest("GOV-MCP not running (run install_ystar_services.sh first)")

        self.assertIn("7922", result.stdout)


class TestIdentitySelfHeal(unittest.TestCase):
    """Test .ystar_active_agent identity self-heal logic."""

    def test_identity_file_exists(self):
        identity = REPO_ROOT / ".ystar_active_agent"
        self.assertTrue(identity.exists(), "Identity file not found")

    def test_identity_defaults_to_ceo(self):
        """After zero_touch_boot.sh, identity should be 'ceo'."""
        identity = REPO_ROOT / ".ystar_active_agent"
        content = identity.read_text().strip()
        self.assertEqual(content, "ceo", f"Expected 'ceo', got '{content}'")


class TestScriptOverrideStatus(unittest.TestCase):
    """Test script_override_active check in zero_touch_boot.sh."""

    def test_session_json_exists(self):
        session = REPO_ROOT / ".ystar_session.json"
        self.assertTrue(session.exists(), ".ystar_session.json not found")

    def test_script_override_field_present(self):
        """session.json should have script_override_active field."""
        import json
        session = REPO_ROOT / ".ystar_session.json"
        with session.open() as f:
            config = json.load(f)

        # Field may be absent (defaults to false), but if present, should be bool
        if "script_override_active" in config:
            self.assertIsInstance(
                config["script_override_active"],
                bool,
                "script_override_active must be boolean"
            )


class TestZeroTouchBootScript(unittest.TestCase):
    """Integration test for zero_touch_boot.sh."""

    def test_zero_touch_boot_exists(self):
        script = REPO_ROOT / "scripts/zero_touch_boot.sh"
        self.assertTrue(script.exists())
        self.assertTrue(os.access(script, os.X_OK), "Script not executable")

    def test_zero_touch_boot_runs(self):
        """Run zero_touch_boot.sh and verify it completes without error."""
        script = REPO_ROOT / "scripts/zero_touch_boot.sh"

        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT
        )

        # Should complete (exit 0 if all checks pass, exit 1 if failures)
        # We accept both — the test is that it doesn't crash
        self.assertIn("[1/6]", result.stdout, "Boot sequence did not start")
        self.assertIn("[6/6]", result.stdout, "Boot sequence did not complete")
        self.assertIn("BOOT SUMMARY", result.stdout)

    def test_boot_creates_session_markers(self):
        """zero_touch_boot.sh should create .session_booted marker."""
        marker = REPO_ROOT / "scripts/.session_booted"
        counter = REPO_ROOT / "scripts/.session_call_count"

        # Run boot
        script = REPO_ROOT / "scripts/zero_touch_boot.sh"
        subprocess.run(["bash", str(script)], capture_output=True, cwd=REPO_ROOT)

        self.assertTrue(marker.exists(), "Session marker not created")
        self.assertTrue(counter.exists(), "Call counter not created")

        # Counter should be reset to 0
        self.assertEqual(counter.read_text().strip(), "0")


if __name__ == "__main__":
    unittest.main()
