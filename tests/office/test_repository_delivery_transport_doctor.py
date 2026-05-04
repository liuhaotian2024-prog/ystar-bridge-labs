from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.repository_delivery_transport import (
    inspect_repo_transport,
    parse_status_porcelain,
    safe_git_add_allowlisted,
)


def test_parse_status_porcelain_expands_file_paths() -> None:
    output = "?? reports/cross_repo/a.md\n M scripts/tool.py\nR  old.py -> new.py\n"
    assert parse_status_porcelain(output) == [
        "reports/cross_repo/a.md",
        "scripts/tool.py",
        "new.py",
    ]


def test_transport_doctor_classifies_dirty_temp_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("x\n")
    result = inspect_repo_transport(tmp_path)
    assert result["transport_classification"] == "direct_push_blocked_by_dirty_state"
    assert "README.md" in result["dirty_set"]


def test_safe_force_add_only_allows_exact_allowlisted_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitignore").write_text("test_*.py\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    outbound = tests / "test_outbound_models.py"
    outbound.write_text("def test_x(): assert True\n")
    secret = tests / "test_secret.py"
    secret.write_text("SECRET='nope'\n")

    result = safe_git_add_allowlisted(
        tmp_path,
        ["tests/test_outbound_models.py"],
        ["tests/test_outbound_models.py"],
    )
    assert result["status"] == "ok"
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=tmp_path, text=True, capture_output=True, check=True)
    assert staged.stdout.splitlines() == ["tests/test_outbound_models.py"]
    assert "tests/test_secret.py" not in staged.stdout
