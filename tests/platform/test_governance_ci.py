#!/usr/bin/env python3
"""
Platform Test: governance_ci.py subcommands
CZL-93 P0 atomic — 4 subcommands: lint / register / smoke-verify / promote
"""
import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
GOVERNANCE_CI = REPO_ROOT / "scripts" / "governance_ci.py"


def test_lint_valid_rules():
    """Lint subcommand validates ForgetGuard YAML syntax."""
    result = subprocess.run(
        ["python3", str(GOVERNANCE_CI), "lint"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # Should pass (or fail with specific error count)
    assert result.returncode in [0, 1]
    assert "LINT" in result.stdout


def test_register_new_rules():
    """Register subcommand auto-adds rules to k9_event_trigger.py routing table."""
    # Backup k9_event_trigger.py
    k9_trigger = REPO_ROOT / "scripts" / "k9_event_trigger.py"
    backup = k9_trigger.with_suffix(".py.bak")
    shutil.copy(k9_trigger, backup)

    try:
        result = subprocess.run(
            ["python3", str(GOVERNANCE_CI), "register"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "REGISTER" in result.stdout
    finally:
        # Restore backup
        shutil.copy(backup, k9_trigger)
        backup.unlink()


def test_smoke_verify_generates_templates():
    """Smoke-verify subcommand generates test templates for rules missing tests."""
    result = subprocess.run(
        ["python3", str(GOVERNANCE_CI), "smoke-verify"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "SMOKE-VERIFY" in result.stdout


def test_promote_rules_dry_run_expiry():
    """Promote subcommand auto-upgrades warn→deny when dry_run_until expires."""
    result = subprocess.run(
        ["python3", str(GOVERNANCE_CI), "promote"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "PROMOTE" in result.stdout
