"""
Regression tests for scripts/czl_boot_inject.py — CZL-BOOT-INJ-FIX.

Covers the AttributeError on line 49 when current_subgoal is a string
instead of a dict. Tests three cases:
  (a) dict input (happy path — structured subgoal)
  (b) string input (the bug — summary-style subgoal)
  (c) empty/None input (no current subgoal)
"""
import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent.parent / "scripts" / "czl_boot_inject.py"
AGENT_ID = "test-agent"


def _run_inject(data: dict) -> subprocess.CompletedProcess:
    """Write data to a temp .czl_subgoals.json and run czl_boot_inject.py against it."""
    # The script resolves .czl_subgoals.json relative to its own parent dir.
    # We create a temp directory structure: tmpdir/scripts/czl_boot_inject.py (symlink)
    # and tmpdir/.czl_subgoals.json, then run with the symlinked script.
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write subgoals JSON
        czl_path = os.path.join(tmpdir, ".czl_subgoals.json")
        with open(czl_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # Create scripts/ dir with a symlink to the real script
        scripts_dir = os.path.join(tmpdir, "scripts")
        os.makedirs(scripts_dir)
        link_path = os.path.join(scripts_dir, "czl_boot_inject.py")
        os.symlink(str(SCRIPT_PATH), link_path)

        result = subprocess.run(
            [sys.executable, link_path, AGENT_ID],
            capture_output=True,
            text=True,
            timeout=10,
        )
    return result


def _minimal_data(**overrides) -> dict:
    """Return minimal valid .czl_subgoals.json data with overrides."""
    base = {
        "y_star_ref": "test-ref",
        "campaign": "Test Campaign",
        "rt1_status": "0/1",
        "completed": [],
        "remaining": [],
    }
    base.update(overrides)
    return base


class TestCurrentSubgoalDict:
    """(a) Happy path: current_subgoal is a structured dict."""

    def test_dict_current_subgoal_prints_fields(self):
        data = _minimal_data(
            current_subgoal={
                "id": "W1",
                "goal": "Do the thing",
                "owner": "eng-platform",
                "started": "2026-04-19T10:00Z",
                "rt1_predicate": "thing is done",
            }
        )
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "CURRENT SUBGOAL: W1" in result.stdout
        assert "Do the thing" in result.stdout
        assert "eng-platform" in result.stdout

    def test_dict_current_subgoal_missing_optional_fields(self):
        data = _minimal_data(current_subgoal={"id": "W2"})
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "CURRENT SUBGOAL: W2" in result.stdout


class TestCurrentSubgoalString:
    """(b) The bug: current_subgoal is a plain string."""

    def test_string_current_subgoal_no_crash(self):
        data = _minimal_data(
            current_subgoal="W3 -- engineer activation steps (Ryan CZL-102 in flight)"
        )
        result = _run_inject(data)
        assert result.returncode == 0, f"Script crashed! stderr: {result.stderr}"
        assert "AttributeError" not in result.stderr

    def test_string_current_subgoal_prints_summary(self):
        summary = "W3 -- engineer activation steps"
        data = _minimal_data(current_subgoal=summary)
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "CURRENT SUBGOAL (summary):" in result.stdout
        assert summary in result.stdout
        assert "plain string" in result.stdout


class TestCurrentSubgoalEmpty:
    """(c) current_subgoal is None, missing, or empty."""

    def test_none_current_subgoal(self):
        data = _minimal_data(current_subgoal=None)
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "CURRENT SUBGOAL: None" in result.stdout

    def test_missing_current_subgoal_key(self):
        data = _minimal_data()
        # Ensure the key is absent
        data.pop("current_subgoal", None)
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "CURRENT SUBGOAL: None" in result.stdout

    def test_empty_string_current_subgoal(self):
        data = _minimal_data(current_subgoal="")
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Empty string is falsy, falls through to "None" branch
        assert "CURRENT SUBGOAL: None" in result.stdout


class TestCompletedItemsDefensive:
    """Completed items should handle non-dict entries gracefully."""

    def test_string_completed_item(self):
        data = _minimal_data(completed=["W1 done", {"id": "W2", "summary": "real entry"}])
        result = _run_inject(data)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "[?] W1 done" in result.stdout
        assert "[W2]" in result.stdout
