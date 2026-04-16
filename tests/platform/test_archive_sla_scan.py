#!/usr/bin/env python3
"""
test_archive_sla_scan.py — Integration test for Secretary archival SLA enforcer

Tests archive_sla_scan.py (cron-runnable script):
- Fresh file (mtime <30 min) + no ARCHIVE_INDEX entry → breach emitted
- Fresh file + ARCHIVE_INDEX entry → no breach
- Old file (mtime >30 min) → no breach
- Empty dir → no breach
- ARCHIVE_INDEX missing → graceful error exit 2

Invokes real script via subprocess to verify cron behavior.
"""
import pytest
import subprocess
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCAN_SCRIPT = REPO_ROOT / "scripts" / "archive_sla_scan.py"


def test_fresh_file_no_archive_entry_emits_breach(tmp_path, monkeypatch):
    """Fresh file (mtime <30 min) with no ARCHIVE_INDEX entry → exit 1, breach emitted."""
    # Create temporary directory structure
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    fresh_file = reports_dir / "new_report.md"
    fresh_file.write_text("Fresh artifact")

    # Create minimal ARCHIVE_INDEX (without new_report.md)
    archive_index = tmp_path / "knowledge" / "ARCHIVE_INDEX.md"
    archive_index.parent.mkdir(parents=True)
    archive_index.write_text("# Archive Index\n## Reports\n- [Old Report](reports/old.md)\n")

    # Monkeypatch REPO_ROOT in scan script (run from tmp_path)
    monkeypatch.chdir(tmp_path)

    # Run scan in dry-run mode
    result = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    # Assertions
    assert result.returncode == 1, "Expected exit 1 (breach found)"
    assert "new_report.md" in result.stdout, "Breach should mention missing file"
    assert "[DRY-RUN]" in result.stdout, "Dry-run mode should prefix output"


def test_fresh_file_with_archive_entry_no_breach(tmp_path, monkeypatch):
    """Fresh file (mtime <30 min) with ARCHIVE_INDEX entry → exit 0, no breach."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    fresh_file = reports_dir / "indexed_report.md"
    fresh_file.write_text("Indexed artifact")

    # Create ARCHIVE_INDEX with this file
    archive_index = tmp_path / "knowledge" / "ARCHIVE_INDEX.md"
    archive_index.parent.mkdir(parents=True)
    archive_index.write_text("# Archive Index\n## Reports\n- [Indexed](reports/indexed_report.md)\n")

    monkeypatch.chdir(tmp_path)

    result = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Expected exit 0 (no breach)"
    assert "No SLA breaches" in result.stdout


def test_old_file_no_breach(tmp_path, monkeypatch):
    """Old file (mtime >30 min) not in ARCHIVE_INDEX → exit 0, no breach."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    old_file = reports_dir / "old_report.md"
    old_file.write_text("Old artifact")

    # Set mtime to 60 minutes ago
    import os
    old_time = time.time() - (60 * 60)
    os.utime(old_file, (old_time, old_time))

    # ARCHIVE_INDEX exists but doesn't include this file
    archive_index = tmp_path / "knowledge" / "ARCHIVE_INDEX.md"
    archive_index.parent.mkdir(parents=True)
    archive_index.write_text("# Archive Index\n## Reports\n")

    monkeypatch.chdir(tmp_path)

    result = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Expected exit 0 (old file outside SLA window)"
    assert "No SLA breaches" in result.stdout


def test_empty_dir_no_breach(tmp_path, monkeypatch):
    """Empty scan directories → exit 0, no breach."""
    # Create directories but leave them empty
    (tmp_path / "reports").mkdir()
    (tmp_path / "knowledge").mkdir()

    # ARCHIVE_INDEX exists
    archive_index = tmp_path / "knowledge" / "ARCHIVE_INDEX.md"
    archive_index.write_text("# Archive Index\n")

    monkeypatch.chdir(tmp_path)

    result = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Expected exit 0 (no files to scan)"
    assert "0 fresh artifacts" in result.stdout or "No SLA breaches" in result.stdout


def test_archive_index_missing_graceful_error(tmp_path):
    """ARCHIVE_INDEX.md missing + fresh artifacts → exit 2 (error), graceful error message."""
    # Create temp repo without ARCHIVE_INDEX but with fresh file
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    fresh_file = reports_dir / "new_report.md"
    fresh_file.write_text("Fresh artifact")

    # Do NOT create ARCHIVE_INDEX
    # Do NOT create knowledge/ dir at all (triggers error path)

    # Invoke script with REPO_ROOT override via subprocess (inject REPO_ROOT via env)
    # Since script uses get_repo_root() that checks cwd/knowledge/, run from tmp_path
    result = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**subprocess.os.environ, "PWD": str(tmp_path)},
    )

    # Expect exit 2 if fresh artifacts exist but ARCHIVE_INDEX missing
    # Current script logic: if no fresh artifacts, exit 0 gracefully
    # If fresh artifacts exist, should error
    # Fix: script detects repo has no ARCHIVE_INDEX but has fresh files
    assert result.returncode == 2, f"Expected exit 2 (error), got {result.returncode}. stdout={result.stdout}, stderr={result.stderr}"
    assert "ARCHIVE_INDEX not found" in result.stderr or "ERROR" in result.stderr


def test_custom_sla_window(tmp_path, monkeypatch):
    """Test --max-age-minutes flag extends SLA window."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    # Create file 45 minutes old
    import os
    mid_age_file = reports_dir / "mid_age.md"
    mid_age_file.write_text("Mid-age artifact")
    old_time = time.time() - (45 * 60)
    os.utime(mid_age_file, (old_time, old_time))

    archive_index = tmp_path / "knowledge" / "ARCHIVE_INDEX.md"
    archive_index.parent.mkdir(parents=True)
    archive_index.write_text("# Archive Index\n")

    monkeypatch.chdir(tmp_path)

    # Default SLA (30 min) → no breach (file is 45 min old)
    result_default = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result_default.returncode == 0, "Default SLA should not catch 45-min-old file"

    # Extended SLA (60 min) → breach (file is 45 min old, within 60 min window)
    result_extended = subprocess.run(
        ["python3", str(SCAN_SCRIPT), "--dry-run", "--max-age-minutes", "60"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result_extended.returncode == 1, "Extended SLA should catch 45-min-old file"
    assert "mid_age.md" in result_extended.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
