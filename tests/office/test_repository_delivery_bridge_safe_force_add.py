from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_worker import safe_git_add


def test_exact_ignored_allowlisted_file_can_be_force_added(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitignore").write_text("tests/test_outbound_*.py\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_outbound_models.py").write_text("def test_x(): assert True\n")
    job = {
        "allowed_files": ["tests/test_outbound_models.py"],
        "force_add_allowlisted_files": ["tests/test_outbound_models.py"],
        "forbidden_patterns": ["**/__pycache__/**", "**/*.pyc", "**/*.log", "**/*.db"],
    }
    result = safe_git_add(tmp_path, job)
    assert result["ok"] is True
    assert result["forced_add_allowlisted_files"] == ["tests/test_outbound_models.py"]


def test_ignored_non_force_file_is_rejected(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitignore").write_text("tests/test_outbound_*.py\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_outbound_models.py").write_text("def test_x(): assert True\n")
    job = {
        "allowed_files": ["tests/test_outbound_models.py"],
        "force_add_allowlisted_files": [],
        "forbidden_patterns": ["**/__pycache__/**", "**/*.pyc", "**/*.log", "**/*.db"],
    }
    result = safe_git_add(tmp_path, job)
    assert result["ok"] is False
    assert result["failure_code"] == "IGNORED_ALLOWED_FILE_NOT_FORCE_ALLOWLISTED"

