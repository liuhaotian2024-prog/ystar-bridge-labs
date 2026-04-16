"""
Test ystar_wakeup.sh octal interpretation fix.

Regression test for line 22 octal bug where HOUR=09 caused
"value too great for base (error token is '09')" error.
"""

import subprocess
import pytest


def test_hour_09_decimal_interpretation():
    """HOUR=09 should parse as decimal 9, not fail as octal."""
    result = subprocess.run(
        ["bash", "-c", "HOUR=09; echo $((10#$HOUR / 3 % 6))"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Failed with: {result.stderr}"
    assert result.stdout.strip() == "3", f"Expected 3, got {result.stdout.strip()}"


def test_hour_08_decimal_interpretation():
    """HOUR=08 should parse as decimal 8, not fail as octal."""
    result = subprocess.run(
        ["bash", "-c", "HOUR=08; echo $((10#$HOUR / 3 % 6))"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Failed with: {result.stderr}"
    assert result.stdout.strip() == "2", f"Expected 2, got {result.stdout.strip()}"


def test_ystar_wakeup_learning_no_syntax_error():
    """ystar_wakeup.sh learning mode should execute without syntax errors."""
    result = subprocess.run(
        ["bash", "scripts/ystar_wakeup.sh", "learning"],
        capture_output=True,
        text=True,
        cwd="/Users/haotianliu/.openclaw/workspace/ystar-company",
    )
    # Should not contain bash syntax errors about octal
    assert "value too great for base" not in result.stderr
    assert "error token is" not in result.stderr
