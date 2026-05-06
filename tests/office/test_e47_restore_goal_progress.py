from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def test_restore_goal_progress_dashboard_after_delivery_tests():
    result = subprocess.run(["git", "show", "HEAD:reports/goal_progress.md"], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0
    (ROOT / "reports/goal_progress.md").write_text(result.stdout, encoding="utf-8")
    assert (ROOT / "reports/goal_progress.md").read_text(encoding="utf-8") == result.stdout
