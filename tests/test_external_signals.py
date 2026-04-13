#!/usr/bin/env python3
"""Tests for external_signals.py"""

import json
import subprocess
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from external_signals import gh_api, fetch_repo_activity, generate_report


def test_gh_api_success():
    """Test gh api call succeeds and returns non-empty data."""
    result = gh_api("repos/liuhaotian2024-prog/ystar-bridge-labs")
    assert result is not None, "gh api should return data"
    assert isinstance(result, dict), "repo query should return dict"
    assert "stargazers_count" in result, "should have stars count"
    print("✓ gh_api returns valid data")


def test_fetch_repo_activity_parses_correctly():
    """Test repo activity parsing extracts correct fields."""
    activity = fetch_repo_activity("liuhaotian2024-prog", "ystar-bridge-labs")

    assert "name" in activity
    assert activity["name"] == "liuhaotian2024-prog/ystar-bridge-labs"

    assert "stars" in activity
    assert isinstance(activity["stars"], int)
    assert activity["stars"] >= 0

    assert "open_issues" in activity
    assert isinstance(activity["open_issues"], int)

    assert "commits_last_7d" in activity
    assert isinstance(activity["commits_last_7d"], int)

    print(f"✓ Parsed activity: {activity['stars']} stars, {activity['commits_last_7d']} commits/7d")


def test_report_generation():
    """Test report generation produces valid markdown."""
    mock_repos = [
        {
            "name": "test/repo1",
            "stars": 10,
            "open_issues": 2,
            "open_prs": 1,
            "latest_release": "v1.0.0",
            "commits_last_7d": 5,
            "last_push": "2026-04-13T00:00:00Z"
        }
    ]

    mock_trending = [
        {
            "name": "trending/repo",
            "stars": 1000,
            "description": "Test repo",
            "url": "https://github.com/trending/repo"
        }
    ]

    report = generate_report(mock_repos, mock_trending)

    assert "# External Signals Report" in report
    assert "test/repo1" in report
    assert "trending/repo" in report
    assert "10" in report  # stars count
    assert "1000" in report  # trending stars

    print("✓ Report generation produces valid markdown")


def test_script_end_to_end():
    """Test full script execution."""
    result = subprocess.run(
        ["python3", str(Path(__file__).parent.parent / "scripts" / "external_signals.py")],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "Report written to" in result.stdout

    # Check files exist
    reports_dir = Path(__file__).parent.parent / "reports"
    assert any(reports_dir.glob("external_signals_*.md")), "Report file should exist"
    assert any(reports_dir.glob("external_signals_*_trending.json")), "Trending JSON should exist"

    print("✓ End-to-end script execution successful")


if __name__ == "__main__":
    test_gh_api_success()
    test_fetch_repo_activity_parses_correctly()
    test_report_generation()
    test_script_end_to_end()

    print("\n✅ All tests passed")
