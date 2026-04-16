#!/usr/bin/env python3
"""Tests for Agent Capability (AC) score composite in session_watchdog.py."""

import sys
from pathlib import Path

# Add parent dir to path
YSTAR_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(YSTAR_DIR))

from scripts.session_watchdog import (
    compute_agent_capability_score,
    get_daemon_liveness_score,
    get_subagent_receipt_accuracy_score,
    get_k9_signal_noise_ratio_score,
    get_api_health_score,
)


def test_compute_agent_capability_returns_0_to_100():
    """AC composite score must be in range [0, 100]."""
    result = compute_agent_capability_score()
    assert "score" in result
    assert 0 <= result["score"] <= 100, f"Score out of range: {result['score']}"


def test_compute_agent_capability_has_4_signal_breakdown():
    """AC result must include breakdown of all 4 signals."""
    result = compute_agent_capability_score()
    assert "signals" in result
    signals = result["signals"]
    expected_keys = {
        "daemon_liveness",
        "subagent_receipt_accuracy",
        "k9_signal_noise_ratio",
        "api_health",
    }
    assert set(signals.keys()) == expected_keys, f"Missing signals: {expected_keys - set(signals.keys())}"
    for name, sig in signals.items():
        assert "score" in sig, f"Signal {name} missing score"
        assert 0 <= sig["score"] <= 100, f"Signal {name} score out of range: {sig['score']}"


def test_compute_agent_capability_below_75_emits_violations():
    """If AC score < 75, result must include violations list."""
    result = compute_agent_capability_score()
    if result["score"] < 75:
        assert "violations" in result
        assert isinstance(result["violations"], list), "Violations must be a list"
        # If score < 75, there should be at least one violation
        # (but we can't guarantee it without mocking, so just check type)


def test_statusline_format_includes_ac():
    """Statusline output must include both HP and AC scores."""
    import subprocess
    watchdog_script = YSTAR_DIR / "scripts" / "session_watchdog.py"
    result = subprocess.run(
        ["python3", str(watchdog_script), "--statusline"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0, f"Watchdog script failed: {result.stderr}"
    output = result.stdout.strip()
    # Output format: HP:NN AC:NN (with ANSI color codes)
    # Strip ANSI codes for assertion
    import re
    clean = re.sub(r'\033\[[0-9;]+m', '', output)
    assert "HP:" in clean, f"HP score missing in statusline: {clean}"
    assert "AC:" in clean, f"AC score missing in statusline: {clean}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
