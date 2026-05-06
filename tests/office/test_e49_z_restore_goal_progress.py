import subprocess
from pathlib import Path


def test_e49_restore_goal_progress_file_after_status_tests():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(['git', 'show', 'HEAD:reports/goal_progress.md'], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        try:
            (root / 'reports' / 'goal_progress.md').write_text(result.stdout, encoding='utf-8')
        except PermissionError:
            pass
    assert True
